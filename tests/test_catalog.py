"""Tests for plugins/team-procedures/scripts/catalog.py — the header parser, the trigger
matching and the hook itself. Standard library only: `python -m unittest discover -s tests`.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "team-procedures"
sys.path.insert(0, str(PLUGIN / "scripts"))
import catalog  # noqa: E402

TODAY = date(2026, 9, 12)

SKILL_TEMPLATE = """---
name: {name}
description: {description}
metadata:
  owner: {owner}
  version: "{version}"
  verified: {verified}
  triggers: [{triggers}]{extra}
---

## When to use
Situation.

## Steps
1. Read.

## Decisions behind this
- Because.

## Gotchas
- Bites here.

## Output
Shape.
"""


def write_skill(root: Path, name: str, triggers: str, owner="Mikołaj", verified="2026-09-01",
                version="1.0", archived=False, description="Does a thing.", extra="", text=None) -> Path:
    sub = catalog.ARCHIVE_DIR if archived else catalog.SKILLS_DIR
    path = root / sub / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if text is None:
        text = SKILL_TEMPLATE.format(name=name, description=description, owner=owner, version=version,
                                     verified=verified, triggers=triggers, extra=extra)
    path.write_text(text, encoding="utf-8")
    return path


def procedures(*specs):
    """Build Procedure objects without touching disk: specs are (name, [triggers])."""
    return [catalog.Procedure(path=Path(n), name=n, triggers=list(t)) for n, t in specs]


# ------------------------------------------------------------------------------- parser


class ParserTests(unittest.TestCase):
    def test_scalars_nested_block_and_inline_list(self):
        fm = catalog.parse_frontmatter(
            "---\nname: x\ndescription: Two words\nmetadata:\n  owner: Ala\n  triggers: [a, b, c]\n---\nbody"
        )
        self.assertEqual(fm["name"], "x")
        self.assertEqual(fm["description"], "Two words")
        self.assertEqual(fm["metadata"], {"owner": "Ala", "triggers": ["a", "b", "c"]})

    def test_quoted_values_are_unquoted_and_lists_keep_phrases(self):
        fm = catalog.parse_frontmatter('---\nmetadata:\n  version: "1.2"\n  triggers: ["user story", \'PR\', plain]\n---')
        self.assertEqual(fm["metadata"]["version"], "1.2")
        self.assertEqual(fm["metadata"]["triggers"], ["user story", "PR", "plain"])

    def test_empty_list_and_blank_lines(self):
        fm = catalog.parse_frontmatter("---\nname: x\n\nmetadata:\n\n  triggers: []\n---")
        self.assertEqual(fm["metadata"]["triggers"], [])

    def test_key_without_children_is_an_empty_value_not_a_block(self):
        fm = catalog.parse_frontmatter("---\ndescription: \nname:\nmetadata:\n  owner: x\n---")
        self.assertEqual(fm["description"], "")
        self.assertEqual(fm["name"], "")
        self.assertEqual(fm["metadata"], {"owner": "x"})

    def test_value_containing_colon_is_kept_whole(self):
        fm = catalog.parse_frontmatter("---\ndescription: Use when: something happens\n---")
        self.assertEqual(fm["description"], "Use when: something happens")

    def test_missing_opening_dashes(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "line 1"):
            catalog.parse_frontmatter("name: x\n---")

    def test_missing_closing_dashes(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "never closed"):
            catalog.parse_frontmatter("---\nname: x\n")

    def test_tab_indentation_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "line 3: tabs"):
            catalog.parse_frontmatter("---\nmetadata:\n\towner: x\n---")

    def test_block_list_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "block lists"):
            catalog.parse_frontmatter("---\nmetadata:\n  triggers: - a\n---")

    def test_indented_line_without_parent_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "line 2: indented line without a parent"):
            catalog.parse_frontmatter("---\n  owner: x\n---")

    def test_key_without_space_after_colon_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "line 2: expected 'key: value'"):
            catalog.parse_frontmatter("---\nname:x\n---")

    def test_unbalanced_quote_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "unbalanced quote"):
            catalog.parse_frontmatter('---\nname: "x\n---')

    def test_unclosed_list_rejected(self):
        with self.assertRaisesRegex(catalog.FrontmatterError, "same line"):
            catalog.parse_frontmatter("---\nmetadata:\n  triggers: [a, b\n---")

    def test_body_sections_skip_header_and_split_on_h2(self):
        text = SKILL_TEMPLATE.format(name="n", description="d", owner="o", version="1", verified="2026-01-01",
                                     triggers="a, b, c", extra="")
        sections = catalog.body_sections(text)
        self.assertEqual(set(sections), set(catalog.REQUIRED_SECTIONS))
        self.assertEqual(sections["Gotchas"], "- Bites here.")


# ------------------------------------------------------------------------------ matching


class MatchingTests(unittest.TestCase):
    P = procedures(("pm-meeting-decisions", ["transcript", "meeting", "decisions", "follow-up"]))

    def hits(self, prompt, procs=None, **kw):
        return catalog.find_hits(prompt, procs or self.P, **kw)

    def test_two_distinct_triggers_fire(self):
        self.assertEqual(len(self.hits("pull the decisions from this meeting")), 1)

    def test_one_trigger_is_silent(self):
        self.assertEqual(self.hits("what was decided about the status page"), [])

    def test_case_insensitive(self):
        self.assertEqual(len(self.hits("DECISIONS from the MEETING")), 1)

    def test_optional_plural_s_and_es(self):
        p = procedures(("x", ["note", "branch"]))
        self.assertEqual(len(self.hits("the notes on those branches", p)), 1)

    def test_hyphen_is_part_of_the_word(self):
        p = procedures(("x", ["up", "meeting"]))
        self.assertEqual(self.hits("follow-up after the meeting", p), [])

    def test_phrase_trigger_matches(self):
        p = procedures(("x", ["user story", "criteria"]))
        self.assertEqual(len(self.hits("acceptance criteria for this user story", p)), 1)

    def test_punctuation_next_to_word_is_fine(self):
        self.assertEqual(len(self.hits("decisions, meeting.")), 1)

    def test_duplicate_trigger_counts_once(self):
        p = procedures(("x", ["meeting", "Meeting", "call"]))
        self.assertEqual(self.hits("about the meeting", p), [])

    def test_two_procedures_sorted_strongest_first(self):
        p = procedures(("weak", ["meeting", "call", "zzz"]), ("strong", ["meeting", "call", "decisions"]))
        names = [proc.name for proc, _ in self.hits("decisions of the meeting call", p)]
        self.assertEqual(names, ["strong", "weak"])

    def test_cap_at_max_hints(self):
        p = procedures(*[(f"p{i}", ["alpha", "beta"]) for i in range(catalog.MAX_HINTS + 2)])
        self.assertEqual(len(self.hits("alpha beta", p)), catalog.MAX_HINTS)

    def test_threshold_is_a_parameter(self):
        self.assertEqual(len(self.hits("just the meeting", threshold=1)), 1)

    def test_matched_triggers_returns_in_list_order(self):
        self.assertEqual(catalog.matched_triggers("meeting then transcript", ["transcript", "meeting"]),
                         ["transcript", "meeting"])


# ---------------------------------------------------------------------------------- hook


class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude-plugin").mkdir()
        (self.root / ".claude-plugin" / "plugin.json").write_text('{"name": "tp"}', encoding="utf-8")
        write_skill(self.root, "pm-weekly-status", "weekly, status, update", owner="Mikołaj", verified="2026-09-01")
        write_skill(self.root, "old-thing", "persona, segment, archetype", archived=True,
                    extra='\n  retired: 2026-08-01\n  retired_reason: "Superseded by something better."')

    def tearDown(self):
        self.tmp.cleanup()

    def run_hint(self, payload, data_dir=None, today=TODAY):
        text = payload if isinstance(payload, str) else json.dumps(payload)
        return catalog.run_hint(text, self.root, data_dir, today)

    def test_fires_with_name_owner_age_and_skill_reference(self):
        out = json.loads(self.run_hint({"prompt": "write the weekly status update"}))
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("pm-weekly-status v1.0", ctx)
        self.assertIn("owner: Mikołaj", ctx)
        self.assertIn("verified 11 days ago", ctx)
        self.assertIn("skill tp:pm-weekly-status", ctx)
        self.assertNotIn("NOT VERIFIED", ctx)

    def test_hint_is_shown_to_the_human_not_only_to_the_model(self):
        # The whole point of the hook is that the person sees the procedure exists. Claude Code
        # renders `systemMessage` ("UserPromptSubmit says: ...") and does NOT render
        # `additionalContext` — that one only reaches the model. Checked in the TUI on 2.1.270,
        # both ways. Drop systemMessage and the hook goes silent on screen while still working.
        out = json.loads(self.run_hint({"prompt": "write the weekly status update"}))
        self.assertEqual(out["systemMessage"], out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("pm-weekly-status v1.0", out["systemMessage"])

    def test_user_input_field_is_accepted_too(self):
        self.assertIn("pm-weekly-status", self.run_hint({"user_input": "weekly status please"}))

    def test_slash_command_empty_prompt_bad_json_and_non_object_are_silent(self):
        for payload in ({"prompt": "/plugin update"}, {"prompt": "   "}, "not json", "[1, 2]", {"prompt": 42}):
            self.assertEqual(self.run_hint(payload), "", payload)

    def test_one_trigger_is_silent(self):
        self.assertEqual(self.run_hint({"prompt": "the weekly report"}), "")

    def test_archive_entry_reports_retirement_without_double_period(self):
        ctx = json.loads(self.run_hint({"prompt": "draft a persona for this segment"}))["hookSpecificOutput"]["additionalContext"]
        self.assertIn('"old-thing" was RETIRED on 2026-08-01: Superseded by something better. Check', ctx)
        self.assertNotIn("..", ctx)

    def test_stale_verified_gets_a_months_note(self):
        write_skill(self.root, "stale-one", "alpha, beta, gamma", verified="2026-01-01")
        ctx = json.loads(self.run_hint({"prompt": "alpha and beta"}))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("verified 254 days ago · NOT VERIFIED IN 8+ MONTHS", ctx)

    def test_logs_one_line_per_hit_only_when_data_dir_given(self):
        data = self.root / "data"
        self.run_hint({"prompt": "weekly status"}, data_dir=data)
        lines = (data / "hits.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("\tpm-weekly-status\tweekly,status", lines[0])
        self.run_hint({"prompt": "weekly status"}, data_dir=None)
        self.assertEqual(len((data / "hits.log").read_text(encoding="utf-8").splitlines()), 1)

    def test_unparseable_skill_is_skipped_not_fatal(self):
        write_skill(self.root, "broken", "", text="name: no dashes\n")
        self.assertIn("pm-weekly-status", self.run_hint({"prompt": "weekly status"}))

    def test_multiple_hits_are_joined_with_newlines(self):
        write_skill(self.root, "also-weekly", "weekly, status, digest")
        ctx = json.loads(self.run_hint({"prompt": "weekly status"}))["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(ctx.count("Team procedure exists"), 2)
        self.assertIn("\n", ctx)


class CliTests(unittest.TestCase):
    """The shim and the script as Claude Code runs them: stdin in, stdout out, exit 0 always."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_skill(self.root, "pm-weekly-status", "weekly, status, update")
        self.env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(self.root)}
        self.env.pop("CLAUDE_PLUGIN_DATA", None)
        self.shim = PLUGIN / "scripts" / "hint.sh"

    def tearDown(self):
        self.tmp.cleanup()

    def run_shim(self, stdin):
        return subprocess.run(["bash", str(self.shim)], input=stdin, capture_output=True, text=True, env=self.env)

    def test_shim_prints_hint_json_and_exits_zero(self):
        res = self.run_shim(json.dumps({"prompt": "weekly status update"}))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("pm-weekly-status", json.loads(res.stdout)["hookSpecificOutput"]["additionalContext"])

    def test_shim_is_silent_and_exits_zero_on_garbage(self):
        res = self.run_shim("garbage")
        self.assertEqual((res.returncode, res.stdout), (0, ""))

    def test_parse_subcommand_prints_json(self):
        path = self.root / catalog.SKILLS_DIR / "pm-weekly-status" / "SKILL.md"
        res = subprocess.run([sys.executable, str(PLUGIN / "scripts" / "catalog.py"), "parse", str(path)],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["metadata"]["owner"], "Mikołaj")


if __name__ == "__main__":
    unittest.main()

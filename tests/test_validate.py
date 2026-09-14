"""Tests for tools/validate.py — one fixture per rule, so every message the CI can print is
pinned by a test that proves the rule catches the mistake it exists for."""
import contextlib
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate  # noqa: E402

TODAY = date(2026, 9, 12)

HEADER = {
    "name": "pm-thing",
    "description": "Does a thing when asked.",
    "owner": "Mikołaj",
    "version": '"1.0"',
    "verified": "2026-09-01",
    "triggers": "[alpha, beta, gamma]",
}
SECTIONS = {
    "When to use": "Situation.",
    "Steps": "1. Read.",
    "Decisions behind this": "- Because.",
    "Gotchas": "- Bites here.",
    "Output": "Shape.",
}


def render(header=None, sections=None, archived_meta=None):
    h = {**HEADER, **(header or {})}
    lines = ["---", f"name: {h['name']}", f"description: {h['description']}", "metadata:"]
    for key in ("owner", "version", "verified", "triggers"):
        if h.get(key) is not None:
            lines.append(f"  {key}: {h[key]}")
    for key, value in (archived_meta or {}).items():
        lines.append(f"  {key}: {value}")
    lines.append("---")
    for title, body in {**SECTIONS, **(sections or {})}.items():
        lines += ["", f"## {title}", body]
    return "\n".join(lines) + "\n"


class Repo:
    def __init__(self, roster=("Mikołaj", "Agnieszka")):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "team.yml").write_text(
            "# roster\nmembers:\n" + "".join(f"  - {n}\n" for n in roster), encoding="utf-8"
        )
        (self.root / validate.PLUGIN_REL / "skills").mkdir(parents=True)
        (self.root / validate.PLUGIN_REL / "archive").mkdir(parents=True)

    def add(self, dirname="pm-thing", text=None, archived=False, **render_kwargs):
        sub = "archive" if archived else "skills"
        path = self.root / validate.PLUGIN_REL / sub / dirname / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text is not None else render(**render_kwargs), encoding="utf-8")
        return path

    def run(self, today=TODAY):
        errors, warnings, _ = validate.run(self.root, today)
        return errors, warnings

    def cleanup(self):
        self.tmp.cleanup()


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def only(self, items, prefix):
        found = [i for i in items if i.startswith(prefix)]
        self.assertEqual(len(found), 1, items)
        return found[0]

    def test_valid_procedure_is_clean(self):
        self.repo.add()
        self.assertEqual(self.repo.run(), ([], []))

    def test_owner_team_is_rejected_with_the_message_from_the_talk(self):
        self.repo.add(header={"owner": "team"})
        errors, _ = self.repo.run()
        msg = self.only(errors, "E020")
        self.assertIn('owner "team" is not on the roster (team.yml). Owner must be a person.', msg)
        self.assertIn("plugins/team-procedures/skills/pm-thing/SKILL.md", msg)

    def test_owner_missing(self):
        self.repo.add(header={"owner": None})
        self.assertIn("owner is missing", self.only(self.repo.run()[0], "E020"))

    def test_version_missing(self):
        self.repo.add(header={"version": None})
        self.only(self.repo.run()[0], "E030")

    def test_verified_missing_and_not_a_date(self):
        self.repo.add(header={"verified": None})
        self.assertIn("missing", self.only(self.repo.run()[0], "E040"))
        self.repo.add(header={"verified": "soon"})
        self.assertIn('"soon" is not a date', self.only(self.repo.run()[0], "E040"))

    def test_stale_verified_is_a_warning_not_an_error(self):
        self.repo.add(header={"verified": "2026-01-01"})
        errors, warnings = self.repo.run()
        self.assertEqual(errors, [])
        self.assertIn("254 days old (> 90)", self.only(warnings, "W010"))

    def test_verified_in_the_future_is_an_error(self):
        self.repo.add(header={"verified": "2027-01-01"})
        self.assertIn("is in the future", self.only(self.repo.run()[0], "E041"))

    def test_retired_fields_on_a_live_procedure(self):
        self.repo.add(archived_meta={"retired": "2026-08-01", "retired_reason": '"why"'})
        self.assertIn("Move it to archive/", self.only(self.repo.run()[0], "E062"))

    def test_github_annotations_when_running_in_actions(self):
        self.repo.add(header={"owner": "team", "verified": "2026-01-01"})
        out = io.StringIO()
        env = dict(os.environ, GITHUB_ACTIONS="true")
        with unittest.mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            validate.main(["--root", str(self.repo.root), "--today", "2026-09-12"])
        text = out.getvalue()
        self.assertIn("::error file=plugins/team-procedures/skills/pm-thing/SKILL.md::E020", text)
        self.assertIn("::warning file=plugins/team-procedures/skills/pm-thing/SKILL.md::W010", text)

    def test_bom_at_file_start_is_tolerated(self):
        self.repo.add(text="﻿" + render())
        self.assertEqual(self.repo.run(), ([], []))

    def test_name_must_match_directory(self):
        self.repo.add(dirname="other-name")
        self.assertIn('name "pm-thing" does not match the directory "other-name"', self.only(self.repo.run()[0], "E010"))

    def test_fewer_than_three_triggers(self):
        self.repo.add(header={"triggers": "[alpha, beta]"})
        self.assertIn("has 2 entries", self.only(self.repo.run()[0], "E050"))

    def test_description_missing(self):
        self.repo.add(header={"description": ""})
        self.only(self.repo.run()[0], "E070")

    def test_empty_required_section_is_a_warning(self):
        self.repo.add(sections={"Gotchas": ""})
        errors, warnings = self.repo.run()
        self.assertEqual(errors, [])
        self.assertIn('section "## Gotchas" is missing or empty', self.only(warnings, "W020"))

    def test_unparseable_header(self):
        self.repo.add(text="---\nmetadata:\n\towner: x\n---\n")
        self.assertIn("tabs are not allowed", self.only(self.repo.run()[0], "E001"))

    def test_archive_needs_date_and_reason(self):
        self.repo.add(dirname="pm-thing", archived=True)
        errors, _ = self.repo.run()
        self.only(errors, "E060")
        self.assertIn("has no retired_reason", self.only(errors, "E061"))

    def test_archive_with_bad_date(self):
        self.repo.add(archived=True, archived_meta={"retired": "someday", "retired_reason": '"why"'})
        self.assertIn('got "someday"', self.only(self.repo.run()[0], "E060"))

    def test_valid_archive_is_clean_and_exempt_from_section_check(self):
        self.repo.add(archived=True, archived_meta={"retired": "2026-08-01", "retired_reason": '"why"'},
                      sections={"Gotchas": ""})
        self.assertEqual(self.repo.run(), ([], []))

    def test_empty_roster_is_an_error(self):
        repo = Repo(roster=())
        self.addCleanup(repo.cleanup)
        repo.add()
        self.assertTrue(any(e.startswith("E000") for e in repo.run()[0]))

    def test_main_exit_codes_and_summary_line(self):
        self.repo.add(header={"owner": "team"})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = validate.main(["--root", str(self.repo.root), "--today", "2026-09-12"])
        self.assertEqual(code, 1)
        self.assertIn("FAILED: 1 procedures, 0 archived, 1 errors, 0 warnings", out.getvalue())
        self.repo.add(header={"owner": "Agnieszka"})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate.main(["--root", str(self.repo.root), "--today", "2026-09-12"]), 0)


class RealCatalogTests(unittest.TestCase):
    def test_the_real_catalog_has_no_errors(self):
        # The real catalog is checked against the real today, not the pinned fixture date:
        # a `verified` date in the future has to fail on the day somebody writes it, and a
        # pinned TODAY would let every entry added after it through unseen.
        errors, warnings, counts = validate.run(ROOT, date.today())
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts["skills"], 4)
        self.assertGreaterEqual(counts["archived"], 1)


if __name__ == "__main__":
    unittest.main()

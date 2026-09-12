"""Pins the exact prompts typed on stage during the WaysConf block B demo against the real
catalog, so a trigger-list edit cannot silently break the choreography:

- §0 teaser must fire exactly one hint, for pm-weekly-status.
- §1 ("do it by hand") and §2 ("turn it into a procedure") must be silent on main, where
  pm-meeting-decisions does not exist yet.
- §4 must fire exactly one hint, for pm-meeting-decisions, once that procedure is installed.
- The retired persona entry must not answer any of them.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "team-procedures"
sys.path.insert(0, str(PLUGIN / "scripts"))
import catalog  # noqa: E402

STAGE = {
    "s0_teaser": "draft the weekly status update for Meridian",
    "s1_by_hand": "Read this transcript and pull out the decisions that were made.",
    "s2_make_procedure": "Turn what we just did into a team procedure. Use the template from the repo.",
    "s4_second_laptop": "get the decisions out of the follow-up call transcript meridian/2026-09-10-followup-transcript.md and write the decisions file next to it",
}
# The first version of the §4 prompt was "get the decisions out of meridian/2026-09-10-followup-
# transcript.md …" and it was SILENT: the only "transcript" sat inside the filename, where the
# hyphen makes it part of a longer word. Trigger words have to be typed as words.
S4_FILENAME_ONLY = "get the decisions out of meridian/2026-09-10-followup-transcript.md and write the decisions file next to it"

# Mirror of the fifth procedure's trigger list (it lives on the add-pm-meeting-decisions
# branch until the on-stage merge). If you change the SKILL.md header, change this too.
FIFTH = catalog.Procedure(
    path=Path("pm-meeting-decisions"), name="pm-meeting-decisions",
    triggers=["transcript", "meeting", "call", "decisions", "minutes", "notes", "agreed", "follow-up"],
)


class StagePromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = [p for p in catalog.load_catalog(PLUGIN) if p.name != "pm-meeting-decisions"]
        cls.names = {p.name for p in cls.main}
        cls.with_fifth = cls.main + [FIFTH]

    def names_hit(self, prompt, procedures):
        return [p.name for p, _ in catalog.find_hits(prompt, procedures)]

    def test_catalog_has_the_four_seeds_and_the_archive_entry(self):
        self.assertTrue({"pm-weekly-status", "ux-interview-synthesis", "qa-acceptance-criteria",
                         "eng-pr-description", "ux-persona-draft"} <= self.names)

    def test_s0_teaser_fires_exactly_pm_weekly_status(self):
        self.assertEqual(self.names_hit(STAGE["s0_teaser"], self.with_fifth), ["pm-weekly-status"])

    def test_s1_and_s2_are_silent_on_main(self):
        for key in ("s1_by_hand", "s2_make_procedure"):
            self.assertEqual(self.names_hit(STAGE[key], self.main), [], key)

    def test_s1_would_fire_once_the_fifth_procedure_exists(self):
        # This is why pm-meeting-decisions must NOT be installed on laptop 1 before §2.
        self.assertEqual(self.names_hit(STAGE["s1_by_hand"], self.with_fifth), ["pm-meeting-decisions"])

    def test_s4_fires_exactly_pm_meeting_decisions(self):
        self.assertEqual(self.names_hit(STAGE["s4_second_laptop"], self.with_fifth), ["pm-meeting-decisions"])

    def test_a_trigger_word_inside_a_filename_does_not_count(self):
        self.assertEqual(self.names_hit(S4_FILENAME_ONLY, self.with_fifth), [])

    def test_no_seed_shares_the_fifth_procedures_key_words(self):
        for p in self.main:
            if p.archived:
                continue
            overlap = {t.lower() for t in p.triggers} & {"transcript", "decisions", "meeting"}
            self.assertEqual(overlap, set(), f"{p.name} would steal the §1/§4 prompts: {overlap}")


if __name__ == "__main__":
    unittest.main()

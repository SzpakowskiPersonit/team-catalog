"""Pins the curator procedures against the prompts typed on stage in part 2 of block B.

The curator entries are the first ones whose own trigger words describe working ON the
catalog rather than in a project, so they are the likeliest to start answering ordinary
prompts. These tests fail if that happens:

- the two part-2 prompts each fire exactly one hint, the right one;
- adding the curator entries leaves the part-1 prompts exactly as silent as before;
- no curator trigger word is already owned by a project procedure.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "team-procedures"
sys.path.insert(0, str(PLUGIN / "scripts"))
import catalog  # noqa: E402

from test_demo_prompts import FIFTH, STAGE  # noqa: E402  (one source for the part-1 prompts)

STAGE_PART2 = {
    "s6_intake": "as curator, do the intake on the new procedure proposal before we merge it",
    "s7_rot": "as curator, do the monthly rot sweep over the catalog",
}
CURATOR = {"curator-intake", "curator-rot"}


class CuratorPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = list(catalog.load_catalog(PLUGIN)) + [FIFTH]
        cls.project = [p for p in cls.all if p.name not in CURATOR]

    def names_hit(self, prompt, procedures):
        return [p.name for p, _ in catalog.find_hits(prompt, procedures)]

    def test_both_curator_procedures_are_in_the_catalog(self):
        self.assertTrue(CURATOR <= {p.name for p in self.all})

    def test_intake_prompt_fires_exactly_curator_intake(self):
        self.assertEqual(self.names_hit(STAGE_PART2["s6_intake"], self.all), ["curator-intake"])

    def test_rot_prompt_fires_exactly_curator_rot(self):
        self.assertEqual(self.names_hit(STAGE_PART2["s7_rot"], self.all), ["curator-rot"])

    def test_curator_entries_do_not_change_what_the_part_one_prompts_hear(self):
        # "Turn what we just did into a team procedure" contains `procedure`, `review`-adjacent
        # words and `merge` in earlier drafts: one more shared trigger and §2 stops being silent.
        for key, prompt in STAGE.items():
            self.assertEqual(self.names_hit(prompt, self.all),
                             self.names_hit(prompt, self.project), key)

    def test_no_curator_trigger_is_owned_by_a_project_procedure(self):
        project_words = {t for p in self.project for t in p.triggers}
        for p in self.all:
            if p.name in CURATOR:
                self.assertEqual(set(p.triggers) & project_words, set(), p.name)


if __name__ == "__main__":
    unittest.main()

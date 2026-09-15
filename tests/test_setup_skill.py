"""Pins `setup/SKILL.md` — the adoption path promised to the workshop room — in two ways.

It is a skill file, so it has to parse like one. But it lives at the repository root and
NOT under `plugins/team-procedures/skills/`, because you run it before you have a catalog
to install it from. Two things break if it drifts:

- moved under `skills/`, it becomes a seventh procedure. Block B says "we have six
  procedures" out loud in §2.2, and `curator-intake` counts them on stage;
- installed anyway (somebody copies it into their own skills directory, which the file
  invites), its trigger words start competing with the real procedures.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "team-procedures"
SETUP = ROOT / "setup" / "SKILL.md"
sys.path.insert(0, str(PLUGIN / "scripts"))
import catalog  # noqa: E402


class SetupSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = catalog.load_procedure(SETUP)
        # load_catalog also returns archive/ entries; the stage line counts live ones.
        cls.all = list(catalog.load_catalog(PLUGIN))
        cls.live = [p for p in cls.all if not p.archived]

    def test_it_parses_as_a_procedure(self):
        self.assertEqual(self.setup.name, "catalog-setup")
        self.assertTrue(self.setup.owner)
        self.assertGreaterEqual(len(self.setup.triggers), 3)

    def test_it_is_not_one_of_the_catalog_entries(self):
        self.assertNotIn("catalog-setup", {p.name for p in self.live})
        self.assertEqual(len(self.live), 6)

    def test_its_triggers_collide_with_nothing_in_the_catalog(self):
        owned = {t for p in self.all for t in p.triggers}
        self.assertEqual(set(self.setup.triggers) & owned, set())

    def test_it_does_not_fire_on_the_part_two_stage_prompts(self):
        # If it ever is installed, it must stay silent while the curator sections run.
        for prompt in ("as curator, do the intake on the new procedure proposal before we merge it",
                       "as curator, do the monthly review over the catalog"):
            hits = [p.name for p, _ in catalog.find_hits(prompt, self.all + [self.setup])]
            self.assertNotIn("catalog-setup", hits, prompt)


if __name__ == "__main__":
    unittest.main()

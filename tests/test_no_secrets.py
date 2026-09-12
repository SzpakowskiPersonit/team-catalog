"""The repository is public and its author works in private repositories all week. This test
fails the build if anything that looks like a credential lands in the tree."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "results", "__pycache__"}
SELF = Path(__file__).resolve()

# Built from parts so this file does not trip its own check.
PATTERNS = [re.compile(p) for p in (
    "ph" + "at_[A-Za-z0-9]{8,}",          # Personit Hub personal access tokens
    "ey" + "JhbGci",                      # JWT header
    "sb_" + "(publishable|secret)_",      # Supabase keys
    "sk-" + "ant-",                       # Anthropic API keys
    "gh" + "[pousr]_[A-Za-z0-9]{20,}",    # GitHub tokens
    "PERSONIT_HUB_ACCESS_TOKEN" + "=",
    "HUB_ANON_KEY" + "=",
)]


def tracked_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path == SELF:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


class NoSecretsTests(unittest.TestCase):
    def test_no_credential_shaped_strings(self):
        hits = []
        for path in tracked_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for rx in PATTERNS:
                if rx.search(text):
                    hits.append(f"{path.relative_to(ROOT)}: {rx.pattern}")
        self.assertEqual(hits, [])

    def test_the_check_itself_catches_a_token(self):
        self.assertTrue(any(rx.search("token=ph" + "at_ABCDEFGH12") for rx in PATTERNS))


if __name__ == "__main__":
    unittest.main()

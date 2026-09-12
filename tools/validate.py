#!/usr/bin/env python3
"""Validate every procedure header in the catalog. CI runs this on every push and PR.

    python tools/validate.py [--root REPO_ROOT] [--today YYYY-MM-DD]

Exit 0 = no errors (warnings allowed), exit 1 = at least one error.
One line per finding, prefixed E### (error) or W### (warning), so it reads the same in a
terminal and in a CI log.

Rules (the header is parsed by plugins/team-procedures/scripts/catalog.py — one parser):
  E001 header does not parse            E010 name != directory name
  E020 owner missing / not on roster    E030 version missing
  E040 verified missing / not a date    E041 verified is in the future
  E050 fewer than 3 triggers            E070 description missing
  E060/E061 archive: retired date / retired_reason   E062 retired fields on a live procedure
  W010 verified older than 90 days      W020 required section missing or empty

Under GitHub Actions the same findings are also printed as ::error/::warning annotations,
so the pull request shows them inline.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_REL = Path("plugins") / "team-procedures"
sys.path.insert(0, str(REPO_ROOT / PLUGIN_REL / "scripts"))
import catalog  # noqa: E402  (imported after sys.path so the one parser is reused)

_ROSTER_LINE = re.compile(r"^\s*-\s+(.+?)\s*$")


def load_roster(root: Path) -> list:
    """Names from team.yml: every `- Name` line. Comments and other lines are ignored."""
    path = root / "team.yml"
    if not path.is_file():
        return []
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ROSTER_LINE.match(line)
        if m and not line.lstrip().startswith("#"):
            names.append(m.group(1))
    return names


def _path_of(finding: str) -> str:
    """'E020 plugins/x/SKILL.md: text' -> 'plugins/x/SKILL.md' (for GitHub annotations)."""
    rest = finding.split(" ", 1)[1] if " " in finding else finding
    return rest.split(":", 1)[0]


def _is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value.strip())
        return True
    except (ValueError, AttributeError):
        return False


def check_procedure(path: Path, roster: list, today: date, archived: bool, root: Path = None) -> tuple:
    """Return (errors, warnings) for one SKILL.md. Messages start with the path relative to root."""
    errors, warnings = [], []
    rel = path.relative_to(root).as_posix() if root and path.is_relative_to(root) else path.as_posix()
    text = path.read_text(encoding="utf-8")
    try:
        proc = catalog.load_procedure(path, archived)
    except catalog.FrontmatterError as exc:
        return [f"E001 {rel}: header does not parse: {exc}"], []

    if proc.name != path.parent.name:
        errors.append(f'E010 {rel}: name "{proc.name}" does not match the directory "{path.parent.name}"')
    if not proc.description.strip():
        errors.append(f"E070 {rel}: description is missing (the model needs it to pick the procedure)")
    if not proc.owner.strip():
        errors.append(f"E020 {rel}: owner is missing. Owner must be a person from team.yml")
    elif proc.owner not in roster:
        errors.append(f'E020 {rel}: owner "{proc.owner}" is not on the roster (team.yml). Owner must be a person.')
    if not proc.version.strip():
        errors.append(f"E030 {rel}: version is missing")
    if not proc.verified.strip():
        errors.append(f"E040 {rel}: verified date is missing (YYYY-MM-DD)")
    elif not _is_iso_date(proc.verified):
        errors.append(f'E040 {rel}: verified "{proc.verified}" is not a date (YYYY-MM-DD)')
    else:
        age = catalog.days_since(proc.verified, today)
        if age is not None and age < 0:
            errors.append(f"E041 {rel}: verified {proc.verified} is in the future")
        elif age is not None and age > catalog.STALE_DAYS:
            warnings.append(
                f"W010 {rel}: verified {proc.verified} is {age} days old (> {catalog.STALE_DAYS}). Re-verify or retire."
            )
    if len(proc.triggers) < 3:
        errors.append(f"E050 {rel}: triggers has {len(proc.triggers)} entries; at least 3 are needed for the hook")

    if archived:
        if not proc.retired.strip() or not _is_iso_date(proc.retired):
            errors.append(f'E060 {rel}: archived procedure needs retired: YYYY-MM-DD (got "{proc.retired}")')
        if not proc.retired_reason.strip():
            errors.append(f"E061 {rel}: archived procedure has no retired_reason. Say why it was retired.")
    else:
        if proc.retired.strip() or proc.retired_reason.strip():
            errors.append(f'E062 {rel}: has "retired" fields but lives in skills/. Move it to archive/.')
        sections = catalog.body_sections(text)
        for name in catalog.REQUIRED_SECTIONS:
            if not sections.get(name, "").strip():
                warnings.append(f'W020 {rel}: section "## {name}" is missing or empty')
    return errors, warnings


def run(root: Path, today: date) -> tuple:
    """Validate the whole catalog under root. Returns (errors, warnings, counts)."""
    plugin = root / PLUGIN_REL
    roster = load_roster(root)
    errors, warnings = [], []
    if not roster:
        errors.append("E000 team.yml: roster is empty or missing — nobody can own anything")
    counts = {"skills": 0, "archived": 0}
    for sub, archived, key in ((catalog.SKILLS_DIR, False, "skills"), (catalog.ARCHIVE_DIR, True, "archived")):
        folder = plugin / sub
        if not folder.is_dir():
            continue
        for skill in sorted(folder.glob("*/SKILL.md")):
            counts[key] += 1
            e, w = check_procedure(skill, roster, today, archived, root)
            errors.extend(e)
            warnings.extend(w)
    return errors, warnings, counts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root (default: this repo)")
    ap.add_argument("--today", type=date.fromisoformat, default=date.today(), help="reference date for staleness")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles vs "Mikołaj"
    errors, warnings, counts = run(args.root.resolve(), args.today)
    for line in warnings:
        print(line)
    for line in errors:
        print(line)
    if os.environ.get("GITHUB_ACTIONS"):
        for level, lines in (("warning", warnings), ("error", errors)):
            for line in lines:
                print(f"::{level} file={_path_of(line)}::{line}")
    status = "FAILED" if errors else "OK"
    print(
        f"{status}: {counts['skills']} procedures, {counts['archived']} archived, "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

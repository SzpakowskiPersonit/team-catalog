#!/usr/bin/env python3
"""team-catalog: the one module that reads a procedure header.

    catalog.py hint          UserPromptSubmit hook: stdin JSON in, hint JSON out. Never blocks.
    catalog.py parse FILE    debug: print the parsed frontmatter of one SKILL.md

Python 3 standard library only. Used by the hook and by tools/validate.py, so the header
format is defined in exactly one place.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

THRESHOLD = 2        # distinct trigger words of ONE procedure needed before the hook speaks
STALE_DAYS = 90      # `verified` older than this: warning in CI, note in the hint
MAX_HINTS = 3        # never more than this many lines per prompt
SKILLS_DIR = "skills"
ARCHIVE_DIR = "archive"
REQUIRED_SECTIONS = ("When to use", "Steps", "Decisions behind this", "Gotchas", "Output")


class FrontmatterError(ValueError):
    """The header uses syntax the minimal parser does not accept. The message names the line."""


# ----------------------------------------------------------------------------- parser

_KEY = r"[A-Za-z_][A-Za-z0-9_-]*"
_TOP = re.compile(rf"^({_KEY}):(?:\s+(.*))?$")
_NESTED = re.compile(rf"^  ({_KEY}):\s+(.*)$")


def _unquote(raw: str, lineno: int) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s and s[0] in "\"'":
        raise FrontmatterError(f"line {lineno}: unbalanced quote: {s}")
    return s


def _scalar(raw: str, lineno: int):
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_unquote(x, lineno) for x in inner.split(",")] if inner else []
    if s.startswith("["):
        raise FrontmatterError(f"line {lineno}: a list must open and close on the same line: {s}")
    if s.startswith("-"):
        raise FrontmatterError(f"line {lineno}: block lists ('- item') are not supported, use [a, b]")
    return _unquote(s, lineno)


def parse_frontmatter(text: str) -> dict:
    """Parse the YAML *subset* used by procedure headers.

    Accepted: `key: value`, `key: "quoted"`, `key: [a, b]`, and one nested block — a bare
    `key:` followed by lines indented with exactly two spaces. Everything else raises
    FrontmatterError naming the line. On purpose: a header nobody can parse by eye is a
    header nobody will maintain.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("line 1: file must start with '---'")
    data: dict = {}
    block: str | None = None

    def close_block() -> None:
        # `key:` with no indented children is an empty value, not an empty block.
        if block is not None and data.get(block) == {}:
            data[block] = ""

    for lineno, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            close_block()
            return data
        if not line.strip():
            continue
        indent = line[: len(line) - len(line.lstrip())]
        if "\t" in indent:
            raise FrontmatterError(f"line {lineno}: tabs are not allowed in the header")
        if indent:
            if block is None:
                raise FrontmatterError(f"line {lineno}: indented line without a parent key")
            m = _NESTED.match(line)
            if not m:
                raise FrontmatterError(f"line {lineno}: expected '  key: value' under '{block}:'")
            data[block][m.group(1)] = _scalar(m.group(2), lineno)
            continue
        close_block()
        m = _TOP.match(line)
        if not m:
            raise FrontmatterError(f"line {lineno}: expected 'key: value', got: {line.strip()}")
        key, raw = m.group(1), m.group(2)
        if raw is None or not raw.strip():
            data[key] = {}
            block = key
        else:
            data[key] = _scalar(raw, lineno)
            block = None
    raise FrontmatterError("header never closed: the second '---' is missing")


def _text(value) -> str:
    """Scalar fields as text; a block or a list where a scalar was expected reads as empty."""
    return value.strip() if isinstance(value, str) else ""


def body_sections(text: str) -> dict:
    """Map '## Heading' -> its text (stripped), for everything after the frontmatter."""
    lines = text.splitlines()
    closes = [i for i, ln in enumerate(lines) if ln.strip() == "---"]
    body = lines[closes[1] + 1 :] if len(closes) >= 2 else lines
    sections: dict = {}
    current = None
    for ln in body:
        if ln.startswith("## "):
            current = ln[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(ln)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


# ----------------------------------------------------------------------------- catalog


@dataclass
class Procedure:
    path: Path
    name: str
    description: str = ""
    owner: str = ""
    version: str = ""
    verified: str = ""
    triggers: list = field(default_factory=list)
    archived: bool = False
    retired: str = ""
    retired_reason: str = ""
    raw: dict = field(default_factory=dict)


def load_procedure(path: Path, archived: bool = False) -> Procedure:
    # utf-8-sig: a Windows editor may prepend a BOM, which would otherwise hide the first '---'
    fm = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
    meta = fm.get("metadata")
    meta = meta if isinstance(meta, dict) else {}
    triggers = meta.get("triggers", [])
    if isinstance(triggers, str):
        triggers = [triggers]
    return Procedure(
        path=path,
        name=_text(fm.get("name")) or path.parent.name,
        description=_text(fm.get("description")),
        owner=_text(meta.get("owner")),
        version=_text(meta.get("version")),
        verified=_text(meta.get("verified")),
        triggers=[str(t).strip() for t in triggers if str(t).strip()],
        archived=archived,
        retired=_text(meta.get("retired")),
        retired_reason=_text(meta.get("retired_reason")),
        raw=fm,
    )


def load_catalog(plugin_root: Path) -> list:
    """Every parseable SKILL.md under skills/ and archive/. Unparseable files are skipped
    here (the hook must never die on one bad file); tools/validate.py reports them."""
    procedures = []
    for sub, archived in ((SKILLS_DIR, False), (ARCHIVE_DIR, True)):
        folder = plugin_root / sub
        if not folder.is_dir():
            continue
        for skill in sorted(folder.glob("*/SKILL.md")):
            try:
                procedures.append(load_procedure(skill, archived))
            except (FrontmatterError, OSError):
                continue
    return procedures


def plugin_name(plugin_root: Path) -> str:
    try:
        manifest = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        return str(manifest.get("name") or plugin_root.name)
    except (OSError, ValueError):
        return plugin_root.name


# ----------------------------------------------------------------------------- matching


def _pattern(trigger: str) -> re.Pattern:
    # Whole word (or phrase), case-insensitive. A hyphen counts as part of the word, so the
    # trigger "up" does not fire on "follow-up". Optional -s / -es so "note" also matches
    # "notes". That is the whole matching rule: if it did not fire, the word is not on the list.
    return re.compile(r"(?<![\w-])" + re.escape(trigger.strip()) + r"(?:e?s)?(?![\w-])", re.IGNORECASE)


def matched_triggers(prompt: str, triggers) -> list:
    seen, out = set(), []
    for t in triggers:
        key = t.strip().lower()
        if key and key not in seen and _pattern(t).search(prompt):
            seen.add(key)
            out.append(t.strip())
    return out


def find_hits(prompt: str, procedures, threshold: int = THRESHOLD) -> list:
    """[(procedure, matched_triggers)] for procedures with >= threshold distinct hits,
    strongest first, capped at MAX_HINTS."""
    hits = []
    for p in procedures:
        m = matched_triggers(prompt, p.triggers)
        if len(m) >= threshold:
            hits.append((p, m))
    hits.sort(key=lambda h: (-len(h[1]), h[0].name))
    return hits[:MAX_HINTS]


# ----------------------------------------------------------------------------- hint text


def days_since(iso: str, today: date):
    try:
        return (today - date.fromisoformat(iso.strip())).days
    except (ValueError, AttributeError):
        return None


def hint_line(p: Procedure, today: date, plugin: str = "team-procedures") -> str:
    if p.archived:
        when = p.retired or "an unknown date"
        why = (p.retired_reason or "no reason recorded").rstrip(". ")
        return f'Team procedure "{p.name}" was RETIRED on {when}: {why}. Check the archive before rebuilding it.'
    n = days_since(p.verified, today)
    age = f"verified {n} days ago" if n is not None else "verification date unknown"
    stale = f" · NOT VERIFIED IN {n // 30}+ MONTHS" if n is not None and n > STALE_DAYS else ""
    return (
        f"Team procedure exists: {p.name} v{p.version or '?'} · owner: {p.owner or 'nobody'} · {age}{stale}. "
        f"Use it unless the user says otherwise (skill {plugin}:{p.name})."
    )


# ----------------------------------------------------------------------------- hook


def run_hint(stdin_text: str, plugin_root: Path, data_dir, today: date) -> str:
    """The hook, as a pure function: returns the JSON to print, or '' for silence."""
    try:
        data = json.loads(stdin_text or "{}")
    except json.JSONDecodeError:
        return ""
    if not isinstance(data, dict):
        return ""
    prompt = data.get("prompt") or data.get("user_input") or ""
    if not isinstance(prompt, str) or not prompt.strip() or prompt.lstrip().startswith("/"):
        return ""
    hits = find_hits(prompt, load_catalog(plugin_root))
    if not hits:
        return ""
    name = plugin_name(plugin_root)
    lines = [hint_line(p, today, name) for p, _ in hits]
    _log_hits(data_dir, hits)
    return json.dumps(
        {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "\n".join(lines)}},
        ensure_ascii=False,
    )


def _log_hits(data_dir, hits) -> None:
    # One line per fired procedure. Nothing reads this file yet; it exists so that one day
    # something can. Missing data_dir (e.g. `claude --plugin-dir`) means no log, not an error.
    if not data_dir:
        return
    try:
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with (data_dir / "hits.log").open("a", encoding="utf-8") as fh:
            for p, m in hits:
                fh.write(f"{stamp}\t{p.name}\t{','.join(m)}\n")
    except OSError:
        pass


def plugin_root_from_env() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    return Path(env) if env else Path(__file__).resolve().parent.parent


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "hint"
    if cmd == "hint":
        try:
            out = run_hint(
                sys.stdin.read(),
                plugin_root_from_env(),
                os.environ.get("CLAUDE_PLUGIN_DATA"),
                date.today(),
            )
            if out:
                print(out)
        except Exception:  # noqa: BLE001 — a hook that blocks the prompt is worse than a missed hint
            pass
        return 0
    if cmd == "parse" and len(argv) > 2:
        fm = parse_frontmatter(Path(argv[2]).read_text(encoding="utf-8-sig"))
        print(json.dumps(fm, indent=2, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

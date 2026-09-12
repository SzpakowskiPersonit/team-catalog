# team-catalog — notes for anyone (or any agent) changing this repo

This is a Claude Code plugin marketplace with one plugin, `team-procedures`: procedures as
skills, a UserPromptSubmit hook that announces them, a CI validator and golden cases. It is
handed to workshop participants, so it must stay small, readable by product people, and
runnable with nothing installed beyond Claude Code and Python 3.

## Hard rules

- **Python 3 standard library only.** No `pip install`, no PyYAML, no `jq`. The header parser
  in `plugins/team-procedures/scripts/catalog.py` is the one parser; `tools/validate.py`
  imports it. Do not add a second one.
- **Every logic change ships with a test in the same PR** (`tests/`, `unittest`). The test
  must catch the failure it prevents: run it before the fix or break the code after.
- **The hook never blocks.** Any exception, bad input or missing file → silence and exit 0.
  Keep it under the 10 s timeout; it runs on every prompt.
- **Procedure headers follow the format in `TEMPLATE.md`.** Custom fields go under
  `metadata:`. `owner` is a name from `team.yml`. CI enforces the rest; do not weaken CI to
  merge a file — fix the file.
- **No secrets, no company-internal systems.** Nothing here may depend on a tool only one
  team has. A procedure names *what* it reads ("the previous decisions file"), never a
  proprietary API.
- **Change behavior → bump `version`.** Ran it and it was still right → bump `verified`.
- **Retire, do not delete.** Move to `archive/` with `retired` and `retired_reason`.

## Layout

```
.claude-plugin/marketplace.json          the marketplace: one JSON list
plugins/team-procedures/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md                 procedures (Claude Code loads these as skills)
  archive/<name>/SKILL.md                retired procedures (hook reads, Claude Code does not load)
  hooks/hooks.json                       UserPromptSubmit → scripts/hint.sh
  scripts/hint.sh, scripts/catalog.py    the hook (python selector shim + logic)
  evals/                                 claude plugin eval cases, 3 per procedure
tools/validate.py                        CI validator (E### errors, W### warnings)
tests/                                   unittest: parser, matching, hook CLI, validator rules
team.yml                                 roster
demo/meridian/                           fictional project for the demo and the evals
```

## Commands

```
python -m unittest discover -s tests -v
python tools/validate.py [--today YYYY-MM-DD]
claude --plugin-dir plugins/team-procedures
claude plugin eval plugins/team-procedures --no-publish --ablation none
```

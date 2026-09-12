# team-catalog

A shared catalog of team procedures for Claude Code. Every procedure is a text file with an
owner, a version, a last-verified date and the two sections no model writes for you: the
decisions behind it and the gotchas. Installed with two commands. Announces itself before
the model answers. Checked by CI. Tested against model changes.

## Install

```
/plugin marketplace add SzpakowskiPersonit/team-catalog
/plugin install team-procedures@team-catalog
```

Same in a terminal: `claude plugin marketplace add SzpakowskiPersonit/team-catalog` and
`claude plugin install team-procedures@team-catalog --scope user`. Under two minutes.
Updates: `/plugin marketplace update team-catalog`, then `/plugin update team-procedures`.

Then type what you want, in your own words. If the team already has a procedure for it, a
line like this appears before the model answers:

```
Team procedure exists: pm-weekly-status v1.0 · owner: Mikołaj · verified 5 days ago.
Use it unless the user says otherwise (skill team-procedures:pm-weekly-status).
```

You did not search. You did not remember. That is the point.

## What is in the box

| Path | What |
|---|---|
| `plugins/team-procedures/skills/<name>/SKILL.md` | The procedures. One folder each. |
| `plugins/team-procedures/archive/<name>/SKILL.md` | Retired procedures, with the date and the reason. The hook reads these too. |
| `plugins/team-procedures/hooks/hooks.json` → `scripts/hint.sh` → `scripts/catalog.py` | The hook. Two trigger words of one procedure in your prompt → one line of context. |
| `tools/validate.py` + `.github/workflows/validate.yml` | CI. Rejects a header without a real owner, a version or a verified date. |
| `plugins/team-procedures/evals/` | Golden cases for `claude plugin eval`. Re-run when the model changes. |
| `team.yml` | The roster. `owner` must be one of these names. |
| `TEMPLATE.md` | Copy this to start a procedure. |
| `demo/meridian/` | Fictional project used by the workshop demo and by the evals. |
| `GUIDE.md` | From zero to the first hint on a clean machine — including what bites. |

## The procedure file

```
---
name: pm-meeting-decisions
description: One sentence, for the model: when to reach for this and what it produces.
metadata:
  owner: Agnieszka
  version: "1.2"
  verified: 2026-09-12
  triggers: [transcript, meeting, call, decisions, minutes, notes, agreed, follow-up]
---
## When to use
## Steps                    ← the model writes this
## Decisions behind this    ← you write this
## Gotchas                  ← you write this
## Output
```

Four header lines matter. **owner** is a person from `team.yml`, never "team" — when a
golden case fails after a model change, the failure goes to a name. **version** bumps when
behavior changes. **verified** is the day somebody last ran it and it was still right; older
than 90 days gets a warning. **triggers** are the words people type, six to ten of them.

The custom fields live under `metadata:`, which Claude Code ignores, so nothing else ever
complains about them. The parser accepts `key: value`, `key: "quoted"`, `key: [a, b]` and one
indented block. Nothing else, on purpose.

## The rules, and what enforces them

| Rule | Enforced by |
|---|---|
| `owner` is a name from `team.yml` | CI, error E020. `owner: team` does not merge. |
| `version` present, `verified` is a real date | CI, errors E030 / E040 |
| `verified` newer than 90 days | CI, warning W010; the hint says "NOT VERIFIED IN N+ MONTHS" |
| at least 3 triggers, `name` equals the folder | CI, errors E050 / E010 |
| every section present and non-empty | CI, warning W020 |
| retired procedures carry `retired` + `retired_reason` | CI, errors E060 / E061 |
| still works on the current model | you: `claude plugin eval`, three cases per procedure |

## The hook, in numbers

- Fires on **2** distinct trigger words of the same procedure. Not 1 ("meeting" alone fires
  on half of what a PM types), not 3 (nobody types three of your words).
- Whole words, case-insensitive, optional plural `-s`/`-es`. A hyphen is part of the word,
  so `up` does not fire on `follow-up`. Multi-word triggers (`user story`) work.
- Tuned for 5–10 procedures. At 30 it will start shouting: `notes` and `decisions` will sit
  in four lists. Then **narrow the trigger lists**, do not raise the threshold.
- At most 3 lines per prompt. Prompts starting with `/` are ignored.
- Never blocks: any error means silence and exit 0. Timeout 10 s.
- Logs each fire to `hits.log` in the plugin's data directory. Nothing reads that file yet.
- It is context, not a command: the model can still ignore the line. What the script
  guarantees is that the line appears.

Check it by hand:

```
echo '{"prompt":"write the weekly status update for Meridian"}' \
  | CLAUDE_PLUGIN_ROOT=plugins/team-procedures bash plugins/team-procedures/scripts/hint.sh
```

## Golden cases

Each procedure ships three cases under `plugins/team-procedures/evals/`, run by Claude
Code's built-in eval runner. They check the shape of the output — "exactly three decision
lines", "the reversal is marked CHANGED" — not the wording, because two runs of the same
model never produce identical text. Details and the case layout: `plugins/team-procedures/evals/README.md`.

```
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish --model sonnet   # "the model changed"
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish --case 'pm-meeting-decisions-02*'
```

`--scaffold` seeds the fixture files, `--allow-tools Write` lets procedures write their dated
output file. Fifteen cases, one run each, is fifteen model sessions on your account.

The runner tells you the output changed. It does not tell you it got worse. The owner reads
the diff. That is why the owner is a person.

## Add a procedure

1. Copy `TEMPLATE.md` to `plugins/team-procedures/skills/<name>/SKILL.md`. Or do what the
   workshop does: finish the task once by hand, then ask the agent to turn what you just did
   into a procedure using the template.
2. Let the model fill **Steps**. You fill **Decisions behind this** and **Gotchas**. If
   Gotchas is empty, it is not done.
3. Add three cases under `evals/`.
4. Pull request. CI runs `python -m unittest` and `python tools/validate.py`. One reviewer.
5. Everyone gets it on the next `/plugin update`.

Retire one: move the folder to `archive/`, add `retired: YYYY-MM-DD` and `retired_reason:`
to the header. The hook keeps announcing it, with the reason, so nobody rebuilds it blind.

## Run everything locally

```
python -m unittest discover -s tests -v
python tools/validate.py                                  # our header rules
claude plugin validate plugins/team-procedures --strict   # Claude Code's own manifest and skill checks
claude --plugin-dir plugins/team-procedures               # try the plugin without installing it
```

Python 3.9 or newer, standard library only. No `pip install`, no `jq`. On Windows use Git
Bash; `hint.sh` picks `python3`, `python` or `py -3`, whichever works.

## What bites

Read `GUIDE.md`. It was written from a real install on a clean machine, and every item in
it is there because it happened.

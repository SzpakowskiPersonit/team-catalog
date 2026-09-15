# Catalog rot pass — 2026-09-15
Curator: Mikołaj · model: claude-opus-5[1m] · 6 live, 1 archived

| Procedure | Owner | Verified | Days | Cases | Proposal |
|---|---|---|---|---|---|
| eng-pr-description | Mikołaj | 2026-09-12 | 3 | 3/3 | re-verify |
| pm-weekly-status | Mikołaj | 2026-09-12 | 3 | 3/3 | re-verify |
| qa-acceptance-criteria | Mikołaj | 2026-09-12 | 3 | 3/3 | re-verify |
| ux-interview-synthesis | Agnieszka | 2026-09-12 | 3 | 3/3 | re-verify |
| curator-intake | Mikołaj | 2026-09-14 | 1 | 1/1 | re-verify |
| curator-rot | Mikołaj | 2026-09-14 | 1 | 1/1 | re-verify |

Nothing is stale: `validate.py` reports 0 errors and 0 warnings, and the oldest `verified`
is 3 days old. Both red golden cases turned out to be harness artifacts, not rot — details
below.

## Retire
- Nothing. The catalog is 3 days old and every entry still does what its header claims.

## Needs its owner

- **curator-intake (Mikołaj)** — the golden case only passes when the run gets `--scaffold`.
  Without it the fixture never writes `proposal/ux-workshop-notes/SKILL.md`, the procedure
  reviews an empty workspace, and `names-the-duplicate` and `verdict-is-changes` go red —
  which is what the recorded 2026-09-14 run shows. Re-run scaffolded today: 3/3 runs, score
  1.00. The command in `CLAUDE.md` omitted `--scaffold` while `evals/README.md` has it; this
  pass fixes `CLAUDE.md`. Decide whether CI pins the scaffolded form too.
- **qa-acceptance-criteria (Mikołaj)** — the case runs at `runs: 1` and has now failed on
  two different graders in three attempts: `at-least-five` on 2026-09-14, then
  `given-when-then-lines` this morning, then clean 5/5 an hour later. Same procedure text
  each time, so this is a one-run case reporting noise as a verdict. Decide: raise `runs`
  to 3 like curator-intake, or pin the line format in the procedure's `Output` section
  (it shows AC1–AC3 and never shows the `- AC5: Given …, When …, Then …` shape the grader
  requires).
- **Catalog-wide (Mikołaj)** — no procedure fires on a Polish prompt. "napisz opis PR-a dla
  tej gałęzi", "napisz status tygodniowy dla projektu Meridian" and "napisz kryteria
  akceptacji dla tej historyjki" all produce no hint; their English equivalents all do.
  Every `triggers` list is English-only while `CLAUDE.md` says Polish is normal here.
  Decide whether Polish trigger words get added.
- **Coverage (Mikołaj)** — `curator-intake` and `curator-rot` have one golden case each;
  every other procedure has three, and both `CLAUDE.md` and `evals/README.md` say three per
  procedure. Also `evals/README.md` still shows `--case 'pm-meeting-decisions-*'`, which is
  not a procedure in this plugin.

## Usage

Merged from both hit logs on this machine (`~/.claude` and `~/.claude-demo`, 22 lines):
pm-weekly-status 16, curator-rot 4, curator-intake 2, eng-pr-description 0,
qa-acceptance-criteria 0, ux-interview-synthesis 0.

The three zeros are no data, not disuse. Typing the prompt a person would actually type
("write the PR description for this branch", "write acceptance criteria for the
cancel-appointment story", "synthesize these five interviews into themes") fires each of
their hints correctly. Nobody has done that work on these two machines yet.

## What this pass changed

`verified` moved to 2026-09-15 on the three procedures whose cases were actually run and
read today: `curator-intake`, `qa-acceptance-criteria`, `curator-rot` (this sweep is its
run). `eng-pr-description`, `pm-weekly-status` and `ux-interview-synthesis` keep their
2026-09-12 date — the full-suite run of 2026-09-14 is green and one day old, and bumping a
date against a run this pass did not make is the thing the header exists to prevent.

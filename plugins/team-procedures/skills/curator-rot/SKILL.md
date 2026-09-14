---
name: curator-rot
description: Find the procedures in the catalog that have gone stale, unused or wrong since the last model change, and propose for each one to re-verify, rewrite or retire. Use when someone acts as this month's curator and does the periodic pass over the whole catalog.
metadata:
  owner: Mikołaj
  version: "1.2"
  verified: 2026-09-14
  triggers: [rot, stale, decay, retire, unused, archive, curator, sweep]
---

## When to use

Once a month, and always after the model behind the team's tooling changes. Input is the
repository. Output is one report with a proposal per entry, and the pull requests that
carry out whatever the curator agrees with.

## Steps

0. This is a sweep, not an investigation. One pass over the catalog, one proposal per entry,
   report written at the end. When something looks wrong, write down what you saw and whose
   entry it is — do not go and find out why. The owner investigates; the sweep notices.
1. Run `python3 tools/validate.py`. Its `W010` warnings are the shortlist: everything
   verified more than ninety days ago.
2. For every live procedure compute the days since `verified`. Sort the catalog by it,
   oldest first. That order is the agenda for the rest of this pass.
3. Golden cases: read the most recent run under `evals/results/` and record which cases
   failed and on which model. Only run `claude plugin eval` yourself if there is no recorded
   run, or the recorded one predates the current model. A case that fails is evidence; a
   procedure nobody ran is not.
4. Usage, if there is any to read: `plugins/data/*/hits.log` holds one line per time the
   hook spoke. It exists only on machines where somebody ran the hook, so treat an absent
   log as no data, never as no use.
5. For each entry on the agenda pick exactly one of:
   - **re-verify** — it still does what it says: run its cases, set `verified` to today,
     nothing else changes.
   - **rewrite** — the steps are right, the output drifted. Bump the version, fix the
     `Output` section first, then the cases that assert against it.
   - **retire** — move to `archive/<name>/`, add `retired` and `retired_reason` to the
     header, and name the procedure that replaces it. CI enforces both fields.
6. Write the report in the Output format **in the reply itself**, in full, and save the same
   text as `catalog-rot-<YYYY-MM-DD>.md`. Then open one pull request per retire, and one for
   all the re-verifies together — a date bump does not need its own review.

## Decisions behind this

- The date is a claim someone makes, not a timestamp a tool writes. `verified` moves only
  when a person ran the procedure and read the result; automating it would turn the one
  honest field in the header into noise.
- Ninety days is the warning, not the deadline. It is long enough that a quarterly pass
  catches everything and short enough that a procedure written around a model that no
  longer exists gets noticed.
- Retiring is the normal outcome, not the failure case. A catalog that only grows stops
  being read at around thirty entries, and then all of it is dead, not just the stale part.
- The reason for retiring is stored in the archive, not in the commit message. Six months
  later somebody proposes the same procedure again, and the reason is the answer.
- Nothing is deleted. The archive is what makes it safe to retire quickly.
- The sweep is bounded on purpose: headers, the last recorded run, the archive, and stop. An
  unbounded sweep turns into one person debugging one entry for an hour, and the other
  fourteen never get looked at — which is the failure this job exists to prevent.

## Gotchas

- Zero hits in the log usually means the trigger words are wrong, not that the procedure is
  unused. Check by typing the prompt you would actually type before proposing a retire.
- A failing golden case after a model change is an assertion problem about as often as it
  is a procedure problem. Read the run output before rewriting anything.
- The oldest `verified` date is rarely the worst entry. The worst one is the procedure that
  reaches into a system whose API changed — and that one can have last week's date.
- Bumping `verified` while re-running the cases in the same session is the easy way to
  certify a procedure against a run you never read. Read the output, then set the date.
- A sweep that only lands in a file is a sweep nobody reads. The report goes in the reply,
   where the person who asked for it already is; the file is the copy for next month. Our
   golden cases assert against the reply for exactly this reason — the first version of this
   procedure wrote the file and answered with one sentence, and three checks went red.
- Retiring an entry does not stop it answering: the hook reads `archive/` too, on purpose,
  so it can say "this was retired and here is what replaced it".

## Output

```
# Catalog rot pass — <YYYY-MM-DD>
Curator: <person> · model: <model id> · <N> live, <M> archived

| Procedure | Owner | Verified | Days | Cases | Proposal |
|---|---|---|---|---|---|
| <name> | <person> | <YYYY-MM-DD> | <n> | <k>/<k> | re-verify \| rewrite \| retire |

## Retire
- <name> — <one sentence: why, and what replaces it>

## Needs its owner
- <name> (<person>) — <what failed and what has to be decided>
```

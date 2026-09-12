---
name: pm-weekly-status
description: Write the weekly status update for a project so that stakeholders who were not in any meeting understand what moved, what is next, what is blocked and what they must decide. Use when asked for a weekly, a status update, a progress report or "what happened this week".
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [weekly, status, update, progress, stakeholders, week, report, blockers]
---

## When to use

Once a week per project, or whenever a stakeholder asks "where are we". Input is whatever
exists in the project folder for that week: dated decision files, transcripts, task lists,
a changelog. Output is one short document they read in ninety seconds.

## Steps

1. Read the project folder. Take everything with this week's dates in the filename
   (`YYYY-MM-DD-*`). If nothing is dated this week, say so and stop — do not summarize the
   whole project as if it happened this week.
2. Collect what was done, what is planned, what is blocked, and what needs a decision from
   the reader. Every item gets a person.
3. Write the four sections in the Output format. Lead with the item the reader most needs
   to act on.
4. Save as `YYYY-MM-DD-weekly-status.md` in the project folder, dated with the last day of
   the reported week. Show the content in the reply too.

## Decisions behind this

- Four fixed sections, always in the same order, even when one is empty ("nothing this
  week"). Readers learn where to look; an empty section is information.
- Every line names a person. "The team" is not a person.
- "Decisions needed" comes first in the reader's attention but last in the file, so the
  reader has the context before the ask.
- No adjectives about pace ("good progress"). Say what happened.
- The file is dated and lives next to the other dated artifacts, so next week's status can
  read this week's without anyone pasting.

## Gotchas

- Stakeholders read the first three lines. If the blocker is on line twelve, it does not
  exist.
- A blocker without a named unblocker is a complaint, not a blocker.
- Transcripts from a week with a cancelled meeting still exist as empty files in some tools.
  An empty file is not "nothing happened" — check the task list before writing "no progress".

## Output

```
# Weekly status — <project> — week ending <YYYY-MM-DD>

## Done
- <what shipped or was finished> (<person>)

## Next
- <what happens next week> (<person>)

## Blockers
- <what is blocked> — unblocked by <person> by <YYYY-MM-DD>

## Decisions needed
- <question> — decide by <YYYY-MM-DD> (<who decides>)
```

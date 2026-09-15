---
name: curator-intake
description: Review a proposed procedure before it is merged into the catalog and return one verdict with the changes it needs. Use when someone acts as this month's curator and a branch or pull request adds or edits a SKILL.md under plugins/team-procedures/skills/.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-15
  triggers: [curator, intake, proposal, duplicate, overlap, curate, gatekeeping, shortlist]
---

## When to use

Somebody proposes a new procedure, or a new version of one. One person on rotation is the
curator that month and reviews it. Input is a branch or a pull request. Output is one
comment with a verdict, posted on the pull request.

## Steps

1. Read every added or changed `SKILL.md` in the diff (`git diff --name-only main...HEAD`).
   If the diff touches no `SKILL.md`, say so and stop — this is not an intake.
2. Run `python3 tools/validate.py`. Do not repeat anything it already says: its errors are
   the author's to fix before review, not the curator's to transcribe.
3. Duplication: for every existing procedure in `skills/` and `archive/`, compare the
   proposal's `description` and `When to use`. If one already covers this situation, the
   verdict is a new version of that procedure, not a new entry.
4. Trigger overlap: collect the `triggers` of every live procedure. Any word the proposal
   shares with another entry is a finding — two entries answering the same prompt is how a
   catalog starts being ignored.
5. Read `Decisions behind this` and `Gotchas`. Every line must be a thing that happened
   here: a choice with what it rules out, or a place someone tripped. A line that would be
   true in any company is not a decision — it is filler, and it is the finding.
6. Golden cases: the proposal needs at least one folder in `evals/` named after it.
   Without one, nobody can tell after the next model change whether it still works.
7. Write the verdict in the Output format. At most three findings, most important first.
   More than three means the answer is CHANGES with one sentence about the shape, not a
   list nobody will work through.

## Decisions behind this

- The curator is one named person on rotation, never a committee. Two reviewers means each
  waits for the other; the catalog then grows a queue instead of entries.
- Intake checks only what CI cannot see. CI reads the header; the curator reads whether the
  procedure is the same as one we already have and whether a human actually wrote the two
  human sections. Splitting it this way keeps the review under fifteen minutes.
- Three findings maximum, and the verdict is ACCEPT or CHANGES — never a score. A score
  invites negotiation; a named change gets made.
- A rejected proposal is never closed silently. It goes back with the one thing to fix, so
  the next version comes from the same author rather than from nobody.
- Trigger overlap is a blocker, not a note. Header mistakes are cheap to fix later; an
  overlapping trigger list quietly degrades every prompt from then on.

## Gotchas

- Decisions written by a model read beautifully and say nothing. "Keep it consistent",
  "ensure clarity" — both are filler. Ask what the line rules out; if nothing, delete it.
- The overlap that bites is not two identical trigger words, it is two entries that both
  fire on the same real prompt. Type the prompt the author would type and see what answers.
- An author who is also the owner of a similar procedure will argue for a new entry. It is
  usually a version bump; the version history is what makes the catalog worth reading.
- The archive counts as existing procedures. A proposal that revives something retired six
  weeks ago has to say what changed since the reason for retiring it.
- A proposal with the `Gotchas` section still empty is not early, it is not started. That
  section is the only part nobody can get from documentation.

## Output

```
# Intake: <name> v<version> — <ACCEPT|CHANGES>
Curator: <person> · <YYYY-MM-DD>

## Findings
1. <what is wrong> — <what to change>
2. …

## Checked
- validate.py: <clean | N errors, author's to fix>
- duplicates: <none | overlaps with <name>>
- triggers: <no shared words | shares <word> with <name>>
- golden cases: <N in evals/<name>-* | none>
```

---
name: qa-acceptance-criteria
description: Write acceptance criteria for a user story or feature as numbered Given/When/Then scenarios that a tester can execute without asking the author anything. Use when asked for acceptance criteria, test scenarios, a definition of done or "how do we know this is done".
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [acceptance, criteria, user story, scenario, gherkin, edge cases, definition of done, testable]
---

## When to use

Before a story goes to development. Input is the story or feature description, plus
whatever the project folder knows about the existing behavior. Output is a numbered list
a tester can run top to bottom.

## Steps

1. Read the story. If it has no actor or no outcome ("as a user I want the button to work"),
   stop and ask for those two things — criteria for a vague story are vague criteria.
2. Write the happy path first as AC1.
3. Add one scenario per edge case you can name: empty input, maximum size, no permission,
   offline, repeated action, concurrent action. Skip the ones that do not apply; do not
   pad.
4. Add the negative scenario: what must NOT happen.
5. Every scenario is checkable by a person who has never spoken to the author. If a step
   says "works correctly", rewrite it with the observable result.
6. Save as `YYYY-MM-DD-<story-slug>-acceptance.md` in the project folder and show it in the
   reply.

## Decisions behind this

- Given/When/Then, one scenario per line, numbered. Numbering lets a tester report "AC3
  fails" instead of a paragraph.
- Observable results only. "The user is notified" is not observable; "a toast with the
  text X appears within 2 s" is.
- Between five and twelve criteria. Fewer means the edge cases were skipped, more means the
  story is two stories.
- Non-functional limits (time, size, count) are written with numbers, never "fast" or
  "large".

## Gotchas

- Authors write criteria for the UI they imagine, not the one that exists. Read the current
  screen or API before writing "the existing button".
- "Then the data is saved" hides the real check. Saved where, visible to whom, after how
  long? If the tester cannot see it, it is not a criterion.
- Criteria written after development describe what was built, not what was needed. Date
  the file so this is visible.

## Output

```
# Acceptance criteria — <story title> — <YYYY-MM-DD>
Story: <one line, actor + outcome>

- AC1: Given <precondition>, When <action>, Then <observable result>
- AC2: Given <precondition>, When <action>, Then <observable result>
- AC3: …
```

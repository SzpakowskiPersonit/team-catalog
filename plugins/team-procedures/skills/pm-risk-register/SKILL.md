---
name: pm-risk-register
description: Keep the project risk register current after every status meeting. Use when asked to update the risks, log a new risk or review mitigation owners.
metadata:
  owner: team
  version: "0.1"
  verified: 2026-05-01
  triggers: [risk, risks, register, mitigation, likelihood, impact]
---

> This pull request exists to show what CI rejects. Two things are wrong with the header on
> purpose: the owner is not a person, and nobody has verified this in four months. Both
> dates and names here are an example, not history.

## When to use

After every status meeting, when a risk was mentioned and nobody wrote it down.

## Steps

1. Read the current register (`*-risks.md`, latest by filename). If none, say so and stop.
2. Add, update or close risks mentioned in the meeting notes.
3. Every open risk has an owner and a review date.
4. Save as `YYYY-MM-DD-risks.md` and show it in the reply.

## Decisions behind this

- One line per risk, with likelihood and impact as numbers 1–3, never words.
- A risk without a mitigation owner is a worry, not a risk. It goes to "Unowned" at the end.

## Gotchas

- Risks that were "handled" in a meeting are closed only when the owner says so in writing.

## Output

```
# Risks — <project> — <YYYY-MM-DD>
- [R1] <risk> — L<1-3> I<1-3> — mitigation: <what> — owner: <person> — review by <YYYY-MM-DD>
## Unowned
- <worry> — needs an owner
```

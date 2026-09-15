---
name: ux-workshop-notes
description: Turn the notes from a discovery workshop into themes the team can act on, with the quotes that support each one. Use after a workshop, a group session or a set of user conversations.
metadata:
  owner: Agnieszka
  version: "0.1"
  verified: 2026-09-14
  triggers: [workshop, notes, themes, interview, session, research, quotes, participants]
---

## When to use

After a discovery workshop or a round of user sessions, when the raw notes need to become
something the team can decide from.

## Steps

1. Read every note file from the session.
2. Group what participants said into themes.
3. Attach at least one quote to each theme.
4. Write the result to `YYYY-MM-DD-workshop-themes.md`.

## Decisions behind this

- Keep the output consistent so everyone knows what to expect.
- Make sure the themes are clear and well structured.
- Always ground the analysis in what participants actually said.

## Gotchas

- Workshops produce a lot of notes, so the file can get long.

## Output

```
# Workshop themes — <session> — <YYYY-MM-DD>

## <theme>
- <finding>
- "<quote>" (<participant>)
```

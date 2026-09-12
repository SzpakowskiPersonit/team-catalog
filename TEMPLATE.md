---
name: role-what-it-does
description: One sentence, written for the model, saying when to reach for this procedure and what it produces.
metadata:
  owner: A person from team.yml
  version: "0.1"
  verified: YYYY-MM-DD
  triggers: [six, to, ten, words, people, actually, type, when, they, need, this]
---

<!--
HOW TO USE THIS TEMPLATE
- Copy this file to plugins/team-procedures/skills/<name>/SKILL.md. <name> == the `name` field.
- Name: role prefix + what it does. pm-, ux-, qa-, eng-. A PM should know it is theirs before opening it.
- Header rules (CI enforces them): owner is a name from team.yml, version is present,
  verified is a real date. verified older than 90 days gets a warning. triggers: at least 3.
- The hook fires when a prompt contains 2 of the trigger words. Keep the list to what
  people type, not what the procedure is about. Narrow the list if it fires too often.
- The model writes Steps. You write Decisions behind this and Gotchas. If Gotchas is empty,
  the file is not done.
- Delete this comment block when you are done.
-->

## When to use

One or two lines. The situation, not the mechanics.

## Steps

1. The first step of anything that reads history or a system is the read itself — and if
   the read fails, stop and say so. Do not improvise from what is at hand.
2. …
3. …

## Decisions behind this

Why it is done this way and what was deliberately left out. These are the rules a model
cannot infer, because they are not in the input and not on the internet. One line each.

- …

## Gotchas

Where it bites. Each line exists because someone tripped over it. Grows for the whole life
of the procedure.

- …

## Output

The exact shape of the result: file name, headings, line format. Make it checkable — the
golden cases in evals/ assert against this section.

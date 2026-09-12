---
name: pm-meeting-decisions
description: Extract the decisions from a meeting transcript into a dated decisions file, compared against the previous meeting's decisions so reversals are marked. Use when asked to get the decisions, action points or agreements out of a call, meeting, transcript or notes.
metadata:
  owner: Agnieszka
  version: "1.2"
  verified: 2026-09-12
  triggers: [transcript, meeting, call, decisions, minutes, notes, agreed, follow-up]
---

## When to use

After any meeting that has a transcript file in the project folder. Works for one meeting
and for a series: the history of earlier meetings is read from the folder, never pasted.

## Steps

1. **Read the history first.** In the folder of the transcript, list `*-decisions.md`, sort
   by filename, take the latest. If there is none: stop and say "No previous decisions file
   found in <folder>." Continue only if the user confirms this is the first meeting — then
   write `Previous: none`. Never improvise history from the transcript alone.
2. Take the meeting date from the transcript filename (`YYYY-MM-DD-…`). No date in the
   name: ask for it before doing anything else.
3. Read the transcript. Extract decisions using the rules in "Decisions behind this".
4. Compare with the previous decisions. A decision that changes an earlier one is written
   as `[CHANGED]` with the old value, the new value and the date of the file it came from.
   It is never silently replaced.
5. Write `<meeting-date>-decisions.md` next to the transcript, in the Output format. If a
   file for that date already exists, do not overwrite it — ask. Show the full content in
   the reply as well.

## Decisions behind this

- A decision is **who does what by when**. Missing owner or missing date makes it an
  `[OPEN]` item, not a decision.
- "We'll look into it", "let's think about it", "we should probably" are not decisions.
- Relative dates ("by Friday", "next sprint") are resolved against the meeting date. If they
  cannot be resolved, the item is `[OPEN]`.
- One file per meeting, dated, next to the transcript. History becomes context by itself;
  nobody has to remember or paste last week's notes.
- Reversals are marked, not merged. The reader who was not in the room must see what
  changed, not only the current state.
- Written for a reader who was not there: no "as discussed", no "the usual".

## Gotchas

- Transcription tools merge speakers on calls with six or more participants. A decision the
  transcript attributes to one person may have been made by another. Attribute to the role
  that owns the topic, and add "(speaker unclear)" when the transcript is the only evidence.
- The client PM signs emails "Anna K."; the transcript tool writes "Ania". Same person.
  Match people by role, not by the spelling of the name.
- A meeting that ends with "let's continue on Slack" can produce zero decisions. Zero is a
  valid output. Do not invent one to fill the file.
- A transcript file without a date prefix breaks step 1 and step 2 quietly. Rename first.

## Output

```
# Decisions — <project> — <YYYY-MM-DD>
Source: <transcript filename>
Previous: <previous decisions filename, or "none">

- [D1] <who> — <what> — by <YYYY-MM-DD>
- [D2] <who> — <what> — by <YYYY-MM-DD>
- [CHANGED] <what> — was: <old value> (<YYYY-MM-DD>) — now: <new value> — by <YYYY-MM-DD>
- [OPEN] <question> — to decide: <who>
```

Rules for the lines: every `[D]` line has exactly three parts separated by ` — ` and ends
with a real date. `[CHANGED]` lines carry the date of the file the old value came from.
`[OPEN]` lines name who decides.

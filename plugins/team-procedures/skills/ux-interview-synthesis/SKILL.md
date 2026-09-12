---
name: ux-interview-synthesis
description: Turn a set of user interview transcripts or notes into themes with evidence, each theme backed by counted participants and verbatim quotes. Use when asked to synthesize interviews, find insights, cluster research findings or summarize what users said.
metadata:
  owner: Agnieszka
  version: "1.0"
  verified: 2026-09-12
  triggers: [interview, synthesis, insights, research, participants, findings, themes, quotes]
---

## When to use

After a round of user interviews (three or more), when the notes exist as files and someone
needs to know what the users actually said, not what we hoped they would say.

## Steps

1. Read every interview file in the folder. Count them. If fewer than three, say so and
   stop — two interviews are anecdotes, not a synthesis.
2. For each participant, list the statements that describe a problem, a workaround or a
   need. Keep the participant id attached to every statement.
3. Cluster statements into themes. A theme needs at least two participants. Statements from
   one participant only go to "Singles" at the end, not into a theme.
4. For each theme, pick one verbatim quote per participant that supports it.
5. Write the Output. Save as `YYYY-MM-DD-synthesis.md` in the research folder, dated with
   the day of the synthesis.

## Decisions behind this

- A theme is counted (n=participants), not felt. "Many users" is not allowed; "4 of 6" is.
- Quotes are verbatim and attributed to a participant id. Paraphrase is where research
  becomes fiction.
- Singles are kept, not dropped. One person's edge case is next quarter's theme.
- We synthesize problems and behaviors, not feature requests. "I want a button" is recorded
  as the problem behind it.
- Dated file next to the interviews, so the next round can read what the previous one found.

## Gotchas

- Interviewers finish participants' sentences. A quote that starts with the interviewer's
  words is not the participant's opinion — check who is speaking before you count it.
- Participants agree with the last thing said. Late-interview "yes, exactly" statements are
  weak evidence; prefer what they said unprompted.
- The same person interviewed twice (follow-up) is one participant, not two.

## Output

```
# Synthesis — <study> — <YYYY-MM-DD>
Participants: <n> (<ids>)

## Themes
- T1 (n=<k>/<n>): <theme in one sentence>
  - "<verbatim quote>" (<participant id>)
  - "<verbatim quote>" (<participant id>)
- T2 (n=<k>/<n>): …

## Singles
- <participant id>: <statement>
```

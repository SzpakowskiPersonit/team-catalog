#!/usr/bin/env bash
# Seeds a catalog of two live procedures plus a proposal that duplicates one of them:
# same job, five shared trigger words, Decisions that would be true at any company.
set -euo pipefail
mkdir -p catalog/ux-interview-synthesis catalog/qa-acceptance-criteria proposal/ux-workshop-notes

cat > catalog/ux-interview-synthesis/SKILL.md <<'SKILL'
---
name: ux-interview-synthesis
description: Turn a set of user interviews into themes with the quotes that support them.
metadata:
  owner: Agnieszka
  version: "1.1"
  verified: 2026-09-12
  triggers: [interview, synthesis, insights, research, participants, findings, themes, quotes]
---
## When to use
After a round of user interviews, when the notes have to become themes the team can decide from.
## Steps
1. Read every interview note.
2. Group what participants said into themes; a theme needs two independent participants.
3. Attach at least one quote per theme.
## Decisions behind this
- A theme needs two participants, because one person's strong opinion is not a pattern.
- Quotes carry participant ids, so anyone can go back to the source without asking the researcher.
## Gotchas
- Interviews run by two people drift in wording; match by what was asked, not how it was phrased.
## Output
`YYYY-MM-DD-synthesis.md` with one section per theme.
SKILL

cat > catalog/qa-acceptance-criteria/SKILL.md <<'SKILL'
---
name: qa-acceptance-criteria
description: Turn a user story into testable acceptance criteria.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [acceptance, criteria, user story, scenario, gherkin, edge cases, testable]
---
## When to use
When a story is ready for refinement.
## Steps
1. Read the story.
2. Write Given/When/Then per rule.
## Decisions behind this
- Every criterion has to fail for a reason somebody can name.
## Gotchas
- A story with no failure mode is a task, not a story.
## Output
A list of Given/When/Then blocks.
SKILL

cat > proposal/ux-workshop-notes/SKILL.md <<'SKILL'
---
name: ux-workshop-notes
description: Turn the notes from a discovery workshop into themes the team can act on, with the quotes that support each one.
metadata:
  owner: Agnieszka
  version: "0.1"
  verified: 2026-09-14
  triggers: [workshop, notes, themes, interview, session, research, quotes, participants]
---
## When to use
After a discovery workshop, when the raw notes need to become something the team can decide from.
## Steps
1. Read every note file from the session.
2. Group what participants said into themes.
3. Attach at least one quote to each theme.
## Decisions behind this
- Keep the output consistent so everyone knows what to expect.
- Make sure the themes are clear and well structured.
- Always ground the analysis in what participants actually said.
## Gotchas
- Workshops produce a lot of notes, so the file can get long.
## Output
`YYYY-MM-DD-workshop-themes.md` with one section per theme.
SKILL

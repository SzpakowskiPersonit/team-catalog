#!/usr/bin/env bash
# Three live procedures — one verified in April, two last week — and one archived entry.
# The April one also points at a tool that no longer exists, so the sweep has something to
# say beyond the date.
set -euo pipefail
mkdir -p catalog/skills/pm-weekly-status catalog/skills/pm-sprint-report catalog/skills/qa-acceptance-criteria catalog/archive/ux-persona-draft

write() { mkdir -p "$(dirname "$1")"; cat > "$1"; }

write catalog/skills/pm-weekly-status/SKILL.md <<'SKILL'
---
name: pm-weekly-status
description: Write the weekly status update for a project from the dated files in its folder.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [weekly, status, update, progress, stakeholders, report]
---
## When to use
Once a week per project.
## Steps
1. Read the project folder.
## Decisions behind this
- Every line names a person; "the team" is not a person.
## Gotchas
- Stakeholders read the first three lines.
## Output
`YYYY-MM-DD-weekly-status.md`
SKILL

write catalog/skills/pm-sprint-report/SKILL.md <<'SKILL'
---
name: pm-sprint-report
description: Build the end-of-sprint report from the tracker export.
metadata:
  owner: Marta
  version: "0.4"
  verified: 2026-04-02
  triggers: [sprint, report, velocity, burndown, tracker]
---
## When to use
At the end of every sprint.
## Steps
1. Export the sprint from the tracker as `sprint.csv` using the Reports tab.
2. Summarize the columns.
## Decisions behind this
- The report counts finished stories, not points, because points drift between teams.
## Gotchas
- The tracker's Reports tab was removed in the June release; the export now lives under Insights.
## Output
`sprint-<n>-report.md`
SKILL

write catalog/skills/qa-acceptance-criteria/SKILL.md <<'SKILL'
---
name: qa-acceptance-criteria
description: Turn a user story into testable acceptance criteria.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [acceptance, criteria, user story, scenario, testable]
---
## When to use
When a story is ready for refinement.
## Steps
1. Read the story.
## Decisions behind this
- Every criterion has to fail for a reason somebody can name.
## Gotchas
- A story with no failure mode is a task, not a story.
## Output
Given/When/Then blocks.
SKILL

write catalog/archive/ux-persona-draft/SKILL.md <<'SKILL'
---
name: ux-persona-draft
description: RETIRED. Draft a user persona from interview notes.
metadata:
  owner: Agnieszka
  version: "0.3"
  verified: 2026-09-12
  retired: 2026-09-12
  retired_reason: "Superseded by ux-interview-synthesis."
  triggers: [persona, archetype, segment]
---
## When to use
Do not. Use ux-interview-synthesis.
## Steps
1. (retired)
## Decisions behind this
- Kept for its Gotchas.
## Gotchas
- Personas drifted from the evidence.
## Output
(retired)
SKILL

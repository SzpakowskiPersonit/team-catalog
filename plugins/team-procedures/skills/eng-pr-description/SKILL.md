---
name: eng-pr-description
description: Write a pull request description from the branch diff so a reviewer knows what changed, why, how to test it and what could break, without opening every file. Use when asked to describe a PR, write a changelog entry for a branch or prepare a change for review.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-12
  triggers: [pull request, PR, description, changelog, diff, commit, review, branch]
---

## When to use

When a branch is ready for review. Input is the diff against the base branch and the
commit messages; the task or ticket if the folder or branch name points to one.

## Steps

1. Read the diff (`git diff <base>...HEAD`) and the commit messages. If the diff is empty,
   say so and stop.
2. Find the task the branch belongs to (branch name, commit trailers, project folder). If
   none, write "No linked task" — do not guess one.
3. Write the four sections in the Output format. "How to test" must be runnable by the
   reviewer, step by step, with the expected result of each step.
4. List every file that changes behavior under "Risk", with one line on what breaks if the
   change is wrong. Pure refactors and tests are not listed.
5. Show the description in the reply. Do not open the PR yourself unless asked.

## Decisions behind this

- Four sections, fixed order: What, Why, How to test, Risk. Reviewers read Risk first, so
  it is written last and best.
- "Why" cites the task or the observed problem, never "as discussed".
- "How to test" is imperative and numbered. A reviewer who has to guess the command will
  approve without running it.
- Test-only and formatting-only changes get a one-line description; the template is for
  behavior changes.

## Gotchas

- Commit messages lie after a rebase. Describe the diff, not the commits.
- Generated files (lockfiles, snapshots) inflate the diff; mention them in one line and
  exclude them from Risk.
- A PR that touches a migration always has a Risk entry, even when the migration looks
  trivial. Migrations are where "trivial" goes to die.

## Output

```
## What
<two to five lines, the change in plain words>

## Why
<the task or the problem, with a link or id>

## How to test
1. <command or click> → expected: <result>
2. …

## Risk
- <file or area> — <what breaks if this is wrong>
```

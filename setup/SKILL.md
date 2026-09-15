---
name: catalog-setup
description: Set this catalog up for a new team from a fork or clone — write the roster, replace the example procedures, wire the hook, and print what the humans still have to do on GitHub. Use when somebody has just cloned team-catalog and wants it to be theirs rather than ours.
metadata:
  owner: Mikołaj
  version: "1.0"
  verified: 2026-09-15
  triggers: [setup, onboard, roster, teammate, adopt, fork, bootstrap]
---

## When to use

Somebody cloned or forked this repository after the workshop and wants it to hold their
team's procedures instead of ours. Run once, by one person, on their own clone.

This file lives outside `plugins/`, on purpose: you run it **before** you have a catalog, so
it is not something you install from one. Point your agent at it —
`read setup/SKILL.md and set this repository up for my team` — or copy the folder into your
own skills directory if you would rather have it announce itself.

## Steps

1. Ask four questions, one at a time, and wait for each answer. Do not guess any of them
   and do not offer defaults for the first two:
   - **Who is on the team?** First names or handles, as they will appear as procedure
     owners. This becomes `team.yml`. One name per person; never a group name.
   - **Who is the curator this month?** One of those names.
   - **What is the repository going to be called, and under which GitHub org or account?**
   - **Which one procedure do they want in it first?** Ask for the task, not the prompt:
     "what does your team keep redoing by hand and getting slightly differently each time".
2. Write `team.yml` from the first answer, keeping the comment block that explains why an
   owner is a person. Verify with `python3 tools/validate.py` that the roster parses.
3. Replace the demo content. Ours is fictional and keeping it is how a catalog becomes
   somebody else's furniture:
   - delete `demo/meridian/` and the evals that depend on it (`*/fixture.sh` referencing it);
   - delete every folder under `plugins/team-procedures/skills/` **except** `curator-intake`
     and `curator-rot`, and re-own those two to the curator from step 1 with today's date;
   - empty `plugins/team-procedures/archive/`.
   Say out loud which files you are deleting before you delete them.
4. Rewrite the two identifiers that carry our name: `name` and `owner` in
   `.claude-plugin/marketplace.json`, and the `marketplace add` line in `README.md`, to the
   org and repository from step 1. Nothing else in the repository hardcodes them — check
   with `grep -rn SzpakowskiPersonit .` and fix whatever that finds.
5. Build the first procedure from step 1's answer, using `TEMPLATE.md`. Write **Steps**
   yourself. Then stop and ask the person for **Decisions behind this** and **Gotchas** —
   two or three rules their team keeps re-deciding, and one thing that has bitten them. Do
   not write these two sections for them and do not accept "you can fill that in later": a
   procedure whose Gotchas section is empty is not started.
6. Add one golden case for it under `evals/`, modelled on the nearest existing one.
7. Run `python3 -m unittest discover -s tests` and `python3 tools/validate.py`. Both clean
   before you hand back.
8. Print the handover checklist — the part no agent can do, because it needs somebody with
   an account:

   ```
   Still yours to do, in this order:

   1. Create the repository under <org> and push.  gh repo create <org>/<repo> --public --source=. --push
   2. Add your teammates:  Settings → Collaborators and teams → Add people
      (or: gh api -X PUT repos/<org>/<repo>/collaborators/<github-username> -f permission=push)
      A name in team.yml is who owns a procedure. A collaborator on GitHub is who can
      merge one. They are two different lists and both have to be right.
   3. Turn on branch protection on main: require the "validate" check.
   4. Tell each person, in whatever you use to talk:
        /plugin marketplace add <org>/<repo>
        /plugin install team-procedures@<org>/<repo>
      They will not discover the repository on their own. This is not a
      communication system.
   5. Put the curator rotation somewhere people see it — one name, one month.
   ```

## Decisions behind this

- The four questions are asked one at a time and none of them is optional. A setup that
  guesses the roster produces a catalog nobody's name is on, which is the failure this whole
  repository exists to prevent.
- The demo content is deleted rather than left as examples. A fork that keeps `Meridian`
  teaches the team that this catalog is about somebody else's project.
- `curator-intake` and `curator-rot` survive the wipe. They are the only two entries that are
  about the catalog rather than about our work, and a catalog with no curator procedure gets
  curated by whoever happens to care that week — which is nobody, by month three.
- Step 8 prints a checklist instead of doing it. Creating repositories and adding people are
  the two operations where getting it wrong is expensive and silent, and they need the
  person's own credentials anyway.
- Roster and collaborators are named as two separate lists on purpose. Conflating them is the
  first thing that goes wrong in an adopted catalog: somebody owns a procedure they cannot
  merge a fix to.

## Gotchas

- `python3` may be `python` or `py -3`. The hook handles all three; this skill should check
  which one works before it promises a green test run.
- Deleting `demo/meridian/` breaks every eval with a `fixture.sh` that seeds from it. Delete
  those cases in the same step or the first test run is red for a reason that has nothing to
  do with the team's own work.
- A fork keeps our `marketplace.json` name until step 4. Two catalogs with the same
  marketplace name cannot be installed side by side, and the error does not say why.
- People will want to skip step 5's second half and let the model write the Decisions
  section. It will produce something that reads well and settles no argument. Ask what the
  line rules out; if the answer is nothing, it is filler.

## Output

A clone that passes `python3 tools/validate.py` and `python3 -m unittest discover -s tests`,
holds one real procedure owned by a named person, and the printed handover checklist from
step 8 with `<org>`, `<repo>` and the usernames filled in.

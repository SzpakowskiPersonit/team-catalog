# Golden cases

Three cases per procedure, run by Claude Code's built-in `claude plugin eval`. Each case is a
directory: `prompt.md` (what a person would type), `graders/*.md` (pass/fail checks) and,
where the task needs files, `case.yaml` + `fixture.sh` that seed the run's empty workspace
with the fictional project from `demo/meridian/`.

| Suffix | What it checks |
|---|---|
| `01-…` | the happy path: the skill fires and the output has the shape the procedure's **Output** section promises |
| `02-…` | the edge the procedure's **Steps** say to refuse: no history, too few interviews, an empty diff, a vague story |
| `03-…` | a look-alike request that must **not** invoke the procedure |

Graders are deterministic (`regex`, `tool_used`, `file_exists`) so two runs of the same model
score the same. They check shape, not wording: "exactly three `[D]` lines, each ending in a
date", not "the summary is good". No judge models, no extra cost per grader.

## Run

From the repository root:

```
# everything, one run per case, no baseline arm, fixtures seeded, files may be written
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish

# one procedure
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish --case 'pm-meeting-decisions-*'

# "the model changed": same suite, different model
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish --model sonnet
```

`--scaffold` is required for the cases with a `fixture.sh`; without it they start empty and
fail on purpose. `--allow-tools Write` lets the procedures write their dated output file;
without it `file_exists` graders fail. Every run is a real model call on your account —
fifteen cases at one run each is fifteen `claude -p` sessions. The report lands in
`evals/results/<timestamp>/report.html` (git-ignored).

The runner tells you the output **changed**. It does not tell you it got **worse**. Somebody
reads the failing grader's explanation and decides. That somebody is the procedure's owner.

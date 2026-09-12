# From zero to the first hint

This is the walkthrough for someone who has never seen this repository. It was written by
doing exactly these steps on a clean Claude Code configuration on 2026-09-12, and every
item under **What bites** is there because it happened during that run or while building
the repository. Times are from that machine.

## You need

- Claude Code **2.1.269 or newer** (`claude --version`). Older versions install the plugin
  and run the hook fine but have no `claude plugin eval`.
- **Python 3.9 or newer** on the PATH as `python3`, `python` or `py -3`. Nothing to `pip
  install`. On Windows use Git Bash, and install Python from python.org, not the Microsoft
  Store (see What bites, 9).
- Git credentials only if the repository is private. For the workshop it is public.

## 1. Install — two commands, about three seconds

In a Claude Code session:

```
/plugin marketplace add SzpakowskiPersonit/team-catalog
/plugin install team-procedures@team-catalog
```

Or in a terminal, which is what the numbers below come from:

```
claude plugin marketplace add SzpakowskiPersonit/team-catalog      # local path: 0.8 s
claude plugin install team-procedures@team-catalog --scope user    # 2.5 s
claude plugin list                                                 # shows team-procedures@team-catalog, enabled
```

You now have the procedures as skills (`/team-procedures:pm-weekly-status` and friends), the
hook, and nothing else. No server, no account, no configuration.

## 2. See the hint — one prompt

Open a Claude Code session in any folder and type, in your own words:

```
write the weekly status update for Meridian
```

Before the model answers, this line appears in the transcript:

```
Team procedure exists: pm-weekly-status v1.0 · owner: Mikołaj · verified 0 days ago.
Use it unless the user says otherwise (skill team-procedures:pm-weekly-status).
```

Three of the procedure's eight trigger words were in your sentence (weekly, status, update).
Two would have been enough. One would have been silence.

The same works non-interactively, which is how the run above was checked:

```
claude -p "Write the weekly status update for Meridian. Before doing anything else, tell me
in one line which team procedure applies and who owns it, then stop." < /dev/null
# → "The team-procedures:pm-weekly-status procedure (v1.0) applies — owned by Mikołaj …"   4.4 s, $0.08
```

Every fire is one line in `hits.log` inside the plugin's data directory. For an installed
plugin that is `<config>/plugins/data/team-procedures-team-catalog/hits.log`, where
`<config>` is `~/.claude` unless you changed it:

```
2026-09-12T21:22:21Z	pm-weekly-status	weekly,status,update
```

Nothing reads this file yet. It exists so that one day something can.

## 3. Check the hook without a model

The hook is a script; you can feed it a prompt directly and see what it would say. From the
repository root:

```
echo '{"prompt":"get the decisions out of this call transcript"}' \
  | CLAUDE_PLUGIN_ROOT=plugins/team-procedures bash plugins/team-procedures/scripts/hint.sh
```

Silence with exit code 0 means "no procedure matched", or "the hook could not run and chose
not to block you". The tests in `tests/test_catalog.py` pin every case: two hits fire, one
does not, `/commands` are ignored, garbage on stdin is ignored, archived procedures announce
their retirement, a `verified` date older than 90 days adds a note.

## 4. Add a procedure

1. Copy `TEMPLATE.md` to `plugins/team-procedures/skills/<name>/SKILL.md`. `<name>` is
   role prefix + what it does: `pm-`, `ux-`, `qa-`, `eng-`. The `name` field must equal the
   folder name.
2. Fill the header: `owner` is a name from `team.yml`, `version: "0.1"`, `verified` today,
   six to ten `triggers` — the words people type, not the words the procedure is about.
3. Let the model write **Steps**. You write **Decisions behind this** and **Gotchas**.
4. Run the checks (next section). Open a pull request. CI runs the same checks.
5. Everyone else gets it on their next `/plugin marketplace update team-catalog`.

The workshop does step 1–3 differently: finish the task once by hand, then ask the agent to
turn what you just did into a procedure using the template. Under five minutes.

## 5. Run the checks

```
python -m unittest discover -s tests -v                    # 55 tests, under a second
python tools/validate.py                                   # "OK: 4 procedures, 1 archived, 0 errors, 0 warnings"
claude plugin validate plugins/team-procedures --strict    # Claude Code's own manifest + skill checks
```

Make the validator fail on purpose once, so you know what it looks like: change an `owner`
to `team` and run it. You get one line, `E020 …: owner "team" is not on the roster (team.yml).
Owner must be a person.`, and exit code 1. That line is what the pull request shows.

## 6. Run the golden cases

```
claude plugin eval plugins/team-procedures --ablation none --scaffold --allow-tools Write --no-publish
```

First run in a directory asks `Trust this plugin directory?` — answer `y`, or pass
`--trust-plugin` in scripts. One case is one `claude -p` session on your account: the cheap
negative cases cost about $0.08 and take 10 s, the scaffolded ones about $0.30 and a minute.
The report is `plugins/team-procedures/evals/results/<timestamp>/report.html`.

To see what "the model changed" looks like, run the same suite with `--model sonnet` (or
`haiku`, or a full model id) and compare the two reports.

## 7. Update, retire, move on

- Get the latest: `/plugin marketplace update team-catalog`.
- Retire a procedure: move its folder from `skills/` to `archive/`, add `retired:` and
  `retired_reason:` under `metadata:`. The hook keeps announcing it, with the reason.
- Try a change before installing it: `claude --plugin-dir plugins/team-procedures` loads the
  working copy for one session. Its hint log goes to `plugins/data/team-procedures-inline/`.

## What bites

Each of these happened. In the order you are likely to meet them.

1. **`--case` globs are `*` only.** `--case 'pm-weekly-status-0[12]*'` matched nothing
   ("No eval cases found matching"). Use `--case 'pm-weekly-status-0*'` or run twice.
2. **Scaffolded cases need `--scaffold`.** Without it the run starts in an empty workspace,
   the procedure finds no files, and the case fails on purpose. The flag exists because the
   scaffold script runs as you, outside the sandbox — only pass it for suites you trust.
3. **Writing files needs `--allow-tools Write`.** A case's own `allowed_tools` cannot grant
   it. Without the grant the procedure explains it cannot write, and every `file_exists`
   grader fails.
4. **`--json` eats the next argument.** `claude plugin eval --json .` treats `.` as the
   output path and fails. Put the target first: `claude plugin eval . --json out.json`.
5. **The hook's log is not where you exported it.** Claude Code sets `CLAUDE_PLUGIN_DATA`
   itself: `plugins/data/<plugin>-<marketplace>/` for an installed plugin,
   `plugins/data/<plugin>-inline/` under `--plugin-dir`. Your own `export CLAUDE_PLUGIN_DATA=…`
   is overwritten. Look in the config directory, not in your variable.
6. **`claude -p` waits three seconds for stdin.** In a script, it prints "no stdin data
   received in 3s, proceeding without it" and wastes the time. Add `< /dev/null`.
7. **The prompt arrives in the `prompt` field.** A UserPromptSubmit hook gets `cwd`,
   `hook_event_name`, `permission_mode`, `prompt`, `prompt_id`, `session_id`,
   `transcript_path` on stdin. Some documentation shows `user_input`; the hook reads both,
   `prompt` first.
8. **The hint is context, not a command.** The script guarantees the line appears. What the
   model does with it is the model's call. In every run so far it followed the line; that is
   an observation, not a guarantee, and the golden cases are how you keep observing it.
9. **Windows: `python3` may be a stub that exits silently.** The Microsoft Store puts a
   `python3` on the PATH that fails in non-interactive use. `hint.sh` probes `python3`,
   `python`, `py -3` in that order and uses the first one that answers; if none does, the
   hook stays silent — which looks exactly like "no procedure matched". Test with the echo
   command from section 3 before concluding the catalog is empty.
10. **A private repository installs only for people with git access.** `marketplace add`
    clones with your git credentials. During development this repository was private and
    that was fine for its author; it is public now because the participants have no
    credentials for it. If `marketplace add` fails with an authentication error, that is why.
11. **Two procedures sharing trigger words fire together.** The hook prints both, strongest
    first, at most three. That is a signal the lists overlap; narrow them in the headers.
    Do not raise the threshold — that hides every procedure a little.
12. **Plurals match, synonyms do not.** `note` matches `notes`; `criteria` does not match
    `criterion`; `minutes` does not match `summary`. If it did not fire, the word is not on
    the list — open the header and see. Everybody's first idea is embeddings; a list of
    eight words you can read is why this stays debuggable.
13. **`claude plugin eval` is a real model call, every run.** Fifteen cases at one run each
    is fifteen sessions. The default is three runs per case and a second no-plugin arm —
    six sessions per case. `--ablation none` and `runs: 1` in each case are what keep the
    suite under a few dollars.

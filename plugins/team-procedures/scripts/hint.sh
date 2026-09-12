#!/usr/bin/env bash
# UserPromptSubmit hook entry point. Finds a working Python 3 and runs `catalog.py hint`
# on the prompt Claude Code passes on stdin.
#
# Why a shim: on Windows + Git Bash `python3` is often the Microsoft Store stub, which
# exits silently; `python` or `py -3` is the real interpreter. Pattern borrowed from
# Anthropic's security-guidance plugin (hooks/sg-python.sh).
#
# Never blocks the prompt: if no interpreter works, exit 0 and stay silent.
here="$(cd "$(dirname "$0")" && pwd)"
for cmd in python3 python "py -3"; do
  # shellcheck disable=SC2086  # intentional word-splitting so `py -3` works
  v=$($cmd -c 'import sys; print(sys.version_info[0])' 2>/dev/null) || continue
  # shellcheck disable=SC2086
  [ "$v" = "3" ] && exec $cmd "$here/catalog.py" hint
done
exit 0

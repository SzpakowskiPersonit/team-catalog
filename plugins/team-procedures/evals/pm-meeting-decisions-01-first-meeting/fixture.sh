#!/usr/bin/env bash
# Seeds the run's empty workspace with the fictional Meridian project (demo/meridian in the
# repo). Runs only when `claude plugin eval` is called with --scaffold.
set -euo pipefail
src="$(cd "$(dirname "$0")/../../../../demo/meridian" && pwd)"
mkdir -p meridian
for f in 2026-09-03-kickoff-transcript.md; do
  cp "$src/$f" meridian/
done

#!/usr/bin/env bash
#
# Scaffold a new coding problem with the strict 01/02/03/04 layout.
# Usage:
#   bash scripts/new_problem.sh examples/<problem_name>_{bug_fix|completion} "Problem Title"
#
# Examples:
#   bash scripts/new_problem.sh examples/config_processor_bug_fix "Configuration Processor — Bug Fix"
#   bash scripts/new_problem.sh examples/data_dashboard_completion "Data Analysis Dashboard — Completion"
#
# What it does:
#   - Validates target folder pattern.
#   - Copies templates/01..04 into the target directory.
#   - Writes a small README with run instructions.
#   - Injects the human-readable title into 01-description.md (line 1).

set -euo pipefail

err() { echo "Error: $*" >&2; exit 1; }
note() { echo "[new_problem] $*"; }

if [ $# -lt 1 ]; then
  err "Usage: bash scripts/new_problem.sh examples/<name>_{bug_fix|completion} [\"Problem Title\"]"
fi

TARGET="$1"
TITLE="${2:-}"

# 1) Validate target pattern
[[ "$TARGET" =~ ^examples/[a-zA-Z0-9_]+_(bug_fix|completion)$ ]] || \
  err "Target must match: examples/<problem_name>_{bug_fix|completion}"

# 2) Ensure templates exist
[ -d "templates" ] || err "Missing templates/ directory (run from repo root)."
for f in 01-description.md 02-tests.py 03-base.py 04-solution.py; do
  [ -f "templates/$f" ] || err "Missing templates/$f"
done

# 3) Ensure target does not already exist
if [ -e "$TARGET" ] && [ "$(ls -A "$TARGET" 2>/dev/null | wc -l)" -gt 0 ]; then
  err "Target '$TARGET' already exists and is not empty."
fi

mkdir -p "$TARGET"

# 4) Copy templates
cp templates/01-description.md "$TARGET/01-description.md"
cp templates/02-tests.py       "$TARGET/02-tests.py"
cp templates/03-base.py        "$TARGET/03-base.py"
cp templates/04-solution.py    "$TARGET/04-solution.py"

# 5) Inject title (if provided): replace the first line with '# Title: <TITLE>'
if [ -n "$TITLE" ]; then
  tmpfile="$(mktemp)"
  awk -v t="$TITLE" 'NR==1{print "# Title: " t; next} {print}' \
      "$TARGET/01-description.md" > "$tmpfile" && mv "$tmpfile" "$TARGET/01-description.md"
  note "Injected title into $TARGET/01-description.md"
fi

# 6) Create a per-problem README
cat > "$TARGET/README.md" <<'EOF'
# Problem README

## How to run tests
```bash
cp 03-base.py solution.py  # for bug_fix (repair) or completion (implement)
pytest -q 02-tests.py

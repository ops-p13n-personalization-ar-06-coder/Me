#!/usr/bin/env bash
set -euo pipefail
passes=0
for i in {1..20}; do
  if pytest -q 02-tests.py; then passes=$((passes+1)); fi
done
echo "Passes: $passes / 20"

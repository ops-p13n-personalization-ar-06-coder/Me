# Project Aurora (2025-09-19) — Source of Truth

This repo contains the **single, up-to-date canon** for writing Aurora coding challenges. It encodes everything we learned from the final three reference problems:
- Configuration Processor (Bug Fix)
- Data Analysis Dashboard CLI (Completion; Pandas)
- Raft Log Validator (Bug Fix)

## What you must produce for every problem
Exactly **four artifacts** in this order (ASCII-only, deterministic):
1. **Description** (markdown)
2. **Unit Tests** — file named `solution_test.py`
3. **Base Code** — file named `solution.py` (buggy for Bug-Fix; stubs for Completion)
4. **Correct Solution Code** — contents for `solution.py` that pass the tests

No extra files or prose around the artifacts.

## Where the rules live
- Read **`aurora_canon_v2025-09-19.md`** for policy details (error wording, precedence, pipelines, rounding, persistence, etc.)
- Use **`aurora_workflow_checklist.md`** as your day-to-day gate before merging a problem.
- Author new problems from **`problem_authoring_template.md`**.

## Test hygiene
- Deterministic only (no network, sleeps, locale/time assertions).
- **No comments/docstrings** in `solution_test.py`.
- Assert **exact strings** (including punctuation, case, and CLI newline policy).
- Tests import only from `solution`.

## Fairness target
- Aim for **<30% pass rate** for unaided solvers; include ≥2 straight-forward success cases to avoid 0%.
- Do not claim “ran tests N times”; encode difficulty via spec & tests.

## Tools
- `tools/no_comments_check.py` helps verify tests contain no comments.

Happy authoring!

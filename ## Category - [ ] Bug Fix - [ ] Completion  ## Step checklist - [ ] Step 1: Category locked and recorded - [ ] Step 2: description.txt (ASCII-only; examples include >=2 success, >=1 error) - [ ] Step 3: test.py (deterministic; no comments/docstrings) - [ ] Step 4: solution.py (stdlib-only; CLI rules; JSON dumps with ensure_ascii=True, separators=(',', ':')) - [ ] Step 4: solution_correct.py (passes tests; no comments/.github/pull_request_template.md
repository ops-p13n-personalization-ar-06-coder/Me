## Category
- [ ] Bug Fix
- [ ] Completion

## Step checklist
- [ ] Step 1: Category locked and recorded
- [ ] Step 2: description.txt (ASCII-only; examples include >=2 success, >=1 error)
- [ ] Step 3: test.py (deterministic; no comments/docstrings)
- [ ] Step 4: solution.py (stdlib-only; CLI rules; JSON dumps with ensure_ascii=True, separators=(',', ':'))
- [ ] Step 4: solution_correct.py (passes tests; no comments/docstrings)
- [ ] Preflight: ascii_guard.py + no_comments_check.py pass

## Notes for reviewers
- Edge cases covered:
- Error messages exactly match spec:

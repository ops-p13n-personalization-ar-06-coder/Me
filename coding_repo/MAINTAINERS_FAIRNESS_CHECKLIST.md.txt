
---

### 3) `MAINTAINERS_FAIRNESS_CHECKLIST.md`  (optional, for repo maintainers)

```markdown
# Maintainers: Fairness Checklist

**Target:** <30% pass rate for first-time attempts. At least ~2/20 passes in quick loop for fairness (not impossible).

## Review Steps

1. **Spec completeness**
   - Inputs/outputs fully specified (exact keys, types, messages).
   - Edge cases enumerated (empty data, boundaries, invalid formats).
   - No hidden requirements outside 01-description.md.

2. **Tests (02-tests.py)**
   - Only assert public API and messages.
   - Stable ordering, no reliance on wall-clock timing or network.
   - Avoid calling private helpers or reading solution internals.

3. **Base (03-base.py)**
   - For *bug_fix*: include realistic bugs but runnable.
   - For *completion*: provide minimal skeleton and clear class/function stubs.

4. **Solution (04-solution.py)**
   - Mirrors description 1:1.
   - No extra deps beyond allowed list.
   - Readable and idiomatic.

5. **Fairness run (20x)**
   ```bash
   passes=0; for i in {1..20}; do
     if pytest -q 02-tests.py; then passes=$((passes+1)); fi
   done; echo "Passes: $passes / 20"

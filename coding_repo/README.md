
---

### `README.md` (root)
```markdown
# ChatGPT Coding Project — Starter Repository

This repo is a **turn-key scaffold** for building coding challenges that follow a strict, reproducible layout:
- Every problem lives in its own folder with **exactly four files**: `01-description.md`, `02-tests.py`, `03-base.py`, `04-solution.py`.
- Tests enforce the spec **verbatim** (messages, outputs, API).
- A fairness policy targets **< 30% pass rate** for first-time attempts.

---

## 📁 Repository Layout

coding_starter_repo/
├── README.md
├── REFERENCE_INDEX.md
├── project_coding_supreme_guidelines.md
├── project_coding_workflow_playbook.md
├── CUSTOM_INSTRUCTIONS_FOR_CHATGPT.md
├── HINTS_FOR_SOLVERS.md
├── MAINTAINERS_FAIRNESS_CHECKLIST.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── scripts/
│ ├── fairness_check.sh
│ └── new_problem.sh
├── templates/
│ ├── 01-description.md
│ ├── 02-tests.py
│ ├── 03-base.py
│ └── 04-solution.py
└── examples/
├── config_processor_bug_fix/
├── config_processor_completion/
├── data_dashboard_bug_fix/
├── data_dashboard_completion/
├── raft_log_validator_bug_fix/
└── raft_log_validator_completion/


**How these connect:**
- **Guidelines & Playbook** (policy):  
  `project_coding_supreme_guidelines.md` + `project_coding_workflow_playbook.md`  
  → Define rules, fairness, and the end-to-end creation process.
- **Custom Instructions for ChatGPT** (operational):  
  `CUSTOM_INSTRUCTIONS_FOR_CHATGPT.md`  
  → Paste into ChatGPT’s “How can ChatGPT best help you…” field to lock in behavior.
- **Templates** (scaffolding):  
  `templates/`  
  → Canonical four-file layout for new problems.
- **Scripts** (automation):  
  `scripts/new_problem.sh` to scaffold, `scripts/fairness_check.sh` to run tests 20×.
- **Examples** (references):  
  `examples/` houses your real problem packs (bug_fix & completion). Replace placeholders with your 01–04 files.

---

## 🚀 Quick Start

```bash
python -V              # Python 3.11+
pip install -r requirements.txt

Create a new problem folder:

bash scripts/new_problem.sh examples/my_feature_completion "My Feature — Completion"
# or
bash scripts/new_problem.sh examples/my_bug_fix "My Feature — Bug Fix"

Run tests inside any problem:

cd examples/<your_problem_dir>
cp 03-base.py solution.py   # completion or bug_fix flow
pytest -q 02-tests.py

Fairness & Difficulty (maintainers)

Target a < 30% pass rate for a first attempt. If pass rate drifts higher:

Add meaningful edge cases and stricter behavior.

Tighten error precedence or I/O formatting.

Enhance interactions among functions.

Run fairness loop (20×):

cd examples/<problem_dir>
bash ../../scripts/fairness_check.sh
# or:
passes=0; for i in {1..20}; do if pytest -q 02-tests.py; then passes=$((passes+1)); fi; done; echo "Passes: $passes / 20"


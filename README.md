# Budget and Spending Assistant

HKU COMP1110 Project - Group F01

### 1. Problem Statement and Project Scope

#### Problem Statement

Managing personal finances is a common challenge, especially for students and young adults whose spending is spread across categories such as meals, transportation, and subscriptions. Without a systematic way to record and review expenses, it becomes difficult to understand spending behavior and control overspending.

To address this, our project develops a lightweight, text-based Personal Budget and Spending Assistant. The tool helps users record transactions, view spending summaries, and receive rule-based alerts when they approach or exceed predefined budgets.

#### Project Scope

1. Design a clear data model for transactions (date, amount, category, description) and budget rules.
2. Implement file I/O using CSV and JSON to store and load data.
3. Provide a text menu interface for adding/viewing/filtering transactions, generating summaries, configuring budgets, and reloading data.
4. Compute summary statistics (totals by category/period, top categories, simple trends).
5. Implement 4-5 rule-based alerts (for example, daily category caps and percentage thresholds).
6. Include a test data generator and create 3-4 realistic case studies to demonstrate and evaluate the system.
7. Validate user inputs and handle common file errors gracefully.

### 2. Technology Stack and Implementation Approach

#### Programming Language

- Python 3.9+: simple syntax, rich standard library, and suitable for text-based interfaces and file processing.

#### Data Storage

- CSV for transactions: human-readable, easy to generate and edit.
- JSON for budget rules: supports nested structures and future extensions.

#### Core Data Structures

| Entity      | Fields                                                                                             |
| ----------- | -------------------------------------------------------------------------------------------------- |
| Transaction | date (YYYY-MM-DD), amount (float), category (str), description (str), notes (optional)             |
| BudgetRule  | category (str), period (day/week/month), threshold (float), alert_type (over_threshold/over_ratio) |

A predefined category list is provided (Catering, Transport, Shopping, Entertainment, Housing, Medical, Education, Others), with custom categories loaded from `data/category_config.json`.

#### Input Validation and Error Handling

- Validate date format, amount sign, and category existence with immediate re-prompts during input.
- Gracefully handle missing files, malformed headers/rows, malformed JSON, and empty inputs with clear error messages.
- Keep compatibility mapping only inside I/O and validator internals (legacy values map to unified values).

#### Modular Architecture

- `models.py`: data classes and category manager.
- `io.py`: file read/write and validation.
- `stats.py`: summaries and trends.
- `alert.py`: rule-based alerts.
- `menu.py`: text interface (including transaction filtering, data reload, and auto-alert display in report views).
- `test_data_generator.py`: realistic and edge-case test data generation.
- `case_runner.py`: reproducible case-study runner.

#### Quick Start

1. Install Python 3.9+.
2. Use one virtual environment (`.venv`) for this project.

- Create (first time): `python -m venv .venv`
- Activate in PowerShell: `.\.venv\Scripts\Activate.ps1`

3. This version uses only Python standard library (no third-party package required).
4. Run the CLI application:

- `python -m src.menu`

5. Run automated tests:

- `python -m unittest discover -s test -p "*.py"`

6. Generate random test transactions:

- `python -m src.test_data_generator`

7. Reproduce one case study:

- `python -m src.case_runner 1`

Current menu highlights:

- View/filter transactions (all, by category, by date range).
- Reload transactions and budget rules from files.
- Immediate budget alert check after adding a transaction.
- Consecutive overspend threshold can be configured per daily threshold rule.

#### Design Trade-Offs (Explicit)

1. Manual entry vs bank synchronization:

- Chosen: manual entry. Reason: no external API dependency and easier implementation/testing.

2. Fixed baseline categories vs unrestricted free-form categories:

- Chosen: fixed baseline with optional extension. Reason: improves validation quality and summary consistency.

3. CSV/JSON files vs database backend:

- Chosen: CSV/JSON. Reason: transparent for teaching context and simple for inspection/debugging.

4. Rule-based thresholds vs predictive forecasting:

- Chosen: threshold and ratio rules. Reason: deterministic behavior and explainable results for case studies.

5. Legacy value compatibility vs strict canonical schema only:

- Chosen: compatibility mapping (`meals`, `daily`, `exceed`, etc.) into canonical values. Reason: robust against mixed datasets.

6. Dynamic "today" anchor vs deterministic data-driven anchor:

- Chosen: deterministic anchor (`start_date` from rule, otherwise earliest transaction date). Reason: reproducible alerts across runs.

#### Case Study Evidence Chain

All four case studies include scenario, input files, expected outputs, limitations, and comparison notes:

1. `case_studies/case_1_daily_food_cap.md`
2. `case_studies/case_2_monthly_transport_tracking.md`
3. `case_studies/case_3_subscription_creep.md`
4. `case_studies/case_4_one_off_purchase_spike.md`

Input datasets are stored in `data/case_studies/` and validated by `test/test_case_studies.py`.

#### Testing Strategy

- Unit tests for core functions (validation, statistics, alerts).
- Integration tests use four predefined case studies with assertion-based expected outputs.
- Edge cases (empty files, missing categories, large amounts) to verify robustness.

#### Technical Coordination Emphasis (Updated)

- Unified transaction CSV header order is fixed: date, amount, category, description, notes.
- Unified budget rule JSON fields are fixed: category, period, threshold, alert_type.
- Standard initial categories are fixed to 8 items: Catering, Transport, Shopping, Entertainment, Housing, Medical, Education, Others.
- Legacy mappings (meals/transport/shopping, daily/weekly/monthly, exceed/percentage) must be normalized before business logic.
- Module interface contracts should remain stable across roles to reduce integration risk.

### 3. Task Breakdown and Role Assignment

#### Role 1 - Yan Zihan (3036482292), Project Lead

- Core responsibilities: project coordination, integration, quality control.
- Key tasks (ordered):
  1.  Run kickoff meeting.
  2.  Maintain Gantt and risk log.
  3.  Manage GitHub merges.
  4.  Compile final report.
  5.  Enforce cross-role interface freeze and technical standard compliance checks.
- Deliverables: kickoff minutes, Gantt, merged PRs, final report draft.
- Acceptance criteria: all milestones tracked, PRs reviewed within 48h, final report assembled on time, technical standards aligned.

#### Role 2 - Tang Yinqi (3036645820), Data Model Architect

- Core responsibilities: define data schemas and interfaces for other modules.
- Key tasks (ordered):
  1.  Produce Transaction/BudgetRule specification.
  2.  Provide sample objects.
  3.  Publish interface document.
  4.  Update on schema changes.
  5.  Ensure BudgetRule fields use period and threshold as canonical names.
- Deliverables: schema document, example CSV/JSON headers, interface README.
- Acceptance criteria: other roles can parse sample files, validation tests pass on schema, and canonical field names are preserved.

#### Role 3 - Zheng Weiqi (3036589234), File I/O and Validation

- Core responsibilities: file formats, load/save, input validation, error handling.
- Key tasks (ordered):
  1.  Define file formats.
  2.  Implement load/save functions.
  3.  Implement `validate_transaction` and `validate_rule`.
  4.  Provide sample files.
  5.  Normalize legacy values to unified enums in load functions.
- Deliverables: `load_transactions`, `save_transactions`, validation module, sample files.
- Acceptance criteria: functions handle missing/malformed files gracefully, include unit tests for edge cases, and return unified-format dictionaries.

#### Role 4 - Zou Jiachen (3036481016), Text Menu Interface

- Core responsibilities: CLI menu, user flows, integration with modules.
- Key tasks (ordered):
  1.  Create CLI skeleton.
  2.  Implement add/view flows.
  3.  Hook to I/O and stats modules.
  4.  Provide usage examples.
  5.  Follow input flow: assemble dict -> validate -> save.
- Deliverables: CLI script, usage README, example session logs.
- Acceptance criteria: menu supports add/view/summaries, handles invalid inputs with clear messages, and does not break module boundaries.

#### Role 5 - Li Aitong (3036588060), Statistics and Alerts

- Core responsibilities: summary computations, trend analysis, alert rules.
- Key tasks (ordered):
  1.  Implement totals and per-period summaries.
  2.  Implement Top N categories.
  3.  Implement trend generator.
  4.  Implement 4 alert rules.
  5.  Write unit tests.
  6.  Ensure weekly summary uses `isocalendar()` and alert enums use unified names.
- Deliverables: stats module, `check_budget_alerts`, test cases.
- Acceptance criteria: outputs match expected values on test datasets, alerts trigger per rules, and over_ratio default threshold behavior is validated.

#### Role 6 - Li Ryan Han (3036519344), Case Studies and Testing

- Core responsibilities: design scenarios, generate test data, run end-to-end tests, demo script.
- Key tasks (ordered):
  1.  Design 3-4 case studies.
  2.  Generate transaction files.
  3.  Run integrated tests.
  4.  Draft demo script and record checklist.
  5.  Provide both unified-format and legacy-format compatibility test data.
- Deliverables: case input files, test reports, demo script.
- Acceptance criteria: case runs reproduce expected summaries/alerts, demo script maps to test data, and compatibility tests are reproducible.

### 4. Timeline and Milestones

| Task / Milestone                                                                                     | W0 Mar 23 | W1 Mar 24-30 | W2 Mar 31-Apr 6 | W3 Apr 7-13 | W4 Apr 14-20 | W5 Apr 21-27 | W6 Apr 28-May 2 |
| ---------------------------------------------------------------------------------------------------- | --------- | ------------ | --------------- | ----------- | ------------ | ------------ | --------------- |
| Finalize Project Plan (Role 1 lead)                                                                  | X         |              |                 |             |              |              |                 |
| Role 2 publishes schema draft                                                                        |           | X            |                 |             |              |              |                 |
| Role 3 confirms file formats                                                                         |           | X            |                 |             |              |              |                 |
| Data model implementation (Role 2)                                                                   |           | X            | X               |             |              |              |                 |
| File I/O basic functions load/save (Role 3)                                                          |           | X            | X               |             |              |              |                 |
| CLI skeleton (Role 4)                                                                                |           |              | X               |             |              |              |                 |
| Statistics core totals, Top N (Role 5)                                                               |           |              | X               |             |              |              |                 |
| Validation integrated into I/O (Role 3)                                                              |           |              | X               | X           |              |              |                 |
| Technical standard lock: unified fields and enums across all modules                                 |           |              |                 | X           | X            |              |                 |
| Unit tests start (Role 5/3)                                                                          |           |              |                 | X           |              |              |                 |
| Module integration: CLI + I/O + stats (All)                                                          |           |              |                 | X           | X            |              |                 |
| Interface contract review checkpoint (Role 1 + Role 2 + Role 3 + Role 4 + Role 5)                    |           |              |                 |             | X            |              |                 |
| First end-to-end tests + bug log (Role 6)                                                            |           |              |                 |             | X            |              |                 |
| Case study execution (3-4 scenarios, Role 6)                                                         |           |              |                 |             | X            | X            |                 |
| Compatibility regression tests (legacy mapping + unified format)                                     |           |              |                 |             |              | X            |                 |
| Bug fixes and feature polish (All)                                                                   |           |              |                 |             |              | X            |                 |
| Demo recording and report drafting (Role 6 lead; Role 1 compiles)                                    |           |              |                 |             |              | X            | X               |
| Finalize unit and integration tests                                                                  |           |              |                 |             |              | X            | X               |
| Final polishing and submission (GitHub cleanup, final report PDF, individual reports, Moodle upload) |           |              |                 |             |              |              | X               |

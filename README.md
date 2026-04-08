# Budget and Spending Assistant

HKU COMP1110 Project -  Group  F01

### 1. Problem Statement and Project Scope

#### Problem Statement

Managing personal finances is a common challenge, especially for students and young adults whose spending is spread across categories such as meals, transportation, and subscriptions. Without a systematic way to record and review expenses, it becomes difficult to understand spending behavior and control overspending.

To address this, our project develops a lightweight, text-based Personal Budget and Spending Assistant. The tool helps users record transactions, view spending summaries, and receive rule-based alerts when they approach or exceed predefined budgets.

#### Project Scope

1. Design a clear data model for transactions (date, amount, category, description) and budget rules.
2. Implement file I/O using CSV and JSON to store and load data.
3. Provide a text menu interface for adding and viewing transactions, generating summaries, and configuring budgets.
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

| Entity      | Fields                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------ |
| Transaction | date (YYYY-MM-DD), amount (float), category (str), description (str), notes (optional)           |
| BudgetRule  | category (str), period (daily/weekly/monthly), threshold (float), alert_type (exceed/percentage) |

A predefined category list (for example, Food, Transport, Shopping) is provided, with support for user-defined categories via a configuration file.

#### Input Validation and Error Handling

- Validate date format, amount sign, and category existence.
- Gracefully handle missing files, malformed rows, and empty inputs with clear error messages.

#### Modular Architecture

- `models.py`: data classes and category manager.
- `io.py`: file read/write and validation.
- `stats.py`: summaries and trends.
- `alert.py`: rule-based alerts.
- `menu.py`: text interface.
- `test_data_generator.py`: random test data.

#### Testing Strategy

- Unit tests for core functions (validation, statistics, alerts).
- Integration tests using 3-4 predefined case studies.
- Edge cases (empty files, missing categories, large amounts) to verify robustness.

### 3. Task Breakdown and Role Assignment

#### Role 1 - Yan Zihan (3036482292), Project Lead

- Core responsibilities: project coordination, integration, quality control.
- Key tasks (ordered):
  1.  Run kickoff meeting.
  2.  Maintain Gantt and risk log.
  3.  Manage GitHub merges.
  4.  Compile final report.
- Deliverables: kickoff minutes, Gantt, merged PRs, final report draft.
- Acceptance criteria: all milestones tracked, PRs reviewed within 48h, final report assembled on time.

#### Role 2 - Tang Yinqi (3036645820), Data Model Architect

- Core responsibilities: define data schemas and interfaces for other modules.
- Key tasks (ordered):
  1.  Produce Transaction/BudgetRule specification.
  2.  Provide sample objects.
  3.  Publish interface document.
  4.  Update on schema changes.
- Deliverables: schema document, example CSV/JSON headers, interface README.
- Acceptance criteria: other roles can parse sample files and validation tests pass on schema.

#### Role 3 - Zheng Weiqi (3036589234), File I/O and Validation

- Core responsibilities: file formats, load/save, input validation, error handling.
- Key tasks (ordered):
  1.  Define file formats.
  2.  Implement load/save functions.
  3.  Implement `validate_transaction` and `validate_rule`.
  4.  Provide sample files.
- Deliverables: `load_transactions`, `save_transactions`, validation module, sample files.
- Acceptance criteria: functions handle missing/malformed files gracefully and include unit tests for edge cases.

#### Role 4 - Zou Jiachen (3036481016), Text Menu Interface

- Core responsibilities: CLI menu, user flows, integration with modules.
- Key tasks (ordered):
  1.  Create CLI skeleton.
  2.  Implement add/view flows.
  3.  Hook to I/O and stats modules.
  4.  Provide usage examples.
- Deliverables: CLI script, usage README, example session logs.
- Acceptance criteria: menu supports add/view/summaries and handles invalid inputs with clear messages.

#### Role 5 - Li Aitong (3036588060), Statistics and Alerts

- Core responsibilities: summary computations, trend analysis, alert rules.
- Key tasks (ordered):
  1.  Implement totals and per-period summaries.
  2.  Implement Top N categories.
  3.  Implement trend generator.
  4.  Implement 4 alert rules.
  5.  Write unit tests.
- Deliverables: stats module, `check_budget_alerts`, test cases.
- Acceptance criteria: outputs match expected values on test datasets and alerts trigger per rules.

#### Role 6 - Li Ryan Han (3036519344), Case Studies and Testing

- Core responsibilities: design scenarios, generate test data, run end-to-end tests, demo script.
- Key tasks (ordered):
  1.  Design 3-4 case studies.
  2.  Generate transaction files.
  3.  Run integrated tests.
  4.  Draft demo script and record checklist.
- Deliverables: case input files, test reports, demo script.
- Acceptance criteria: case runs reproduce expected summaries/alerts and demo script maps to test data.


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
| Unit tests start (Role 5/3)                                                                          |           |              |                 | X           |              |              |                 |
| Module integration: CLI + I/O + stats (All)                                                          |           |              |                 | X           | X            |              |                 |
| First end-to-end tests + bug log (Role 6)                                                            |           |              |                 |             | X            |              |                 |
| Case study execution (3-4 scenarios, Role 6)                                                         |           |              |                 |             | X            | X            |                 |
| Bug fixes and feature polish (All)                                                                   |           |              |                 |             |              | X            |                 |
| Demo recording and report drafting (Role 6 lead; Role 1 compiles)                                    |           |              |                 |             |              | X            | X               |
| Finalize unit and integration tests                                                                  |           |              |                 |             |              | X            | X               |
| Final polishing and submission (GitHub cleanup, final report PDF, individual reports, Moodle upload) |           |              |                 |             |              |              | X               |

---
name: write-branch-problem-solution-test-descriptions
description: Create a timestamped Better Battery CSV that explains the operator problem, solution, staging test path, and pass condition for each supplied Git branch. Use when a user provides a list of better-battery-m2 branches and wants branch problem/solution/test descriptions; do not use for implementation plans, code changes, or execution of the tests themselves.
metadata:
  layer: capability
---

# Write Branch Problem, Solution, and Test Descriptions

Create one new CSV row per supplied branch, based on the branch's current implementation and its supporting plans and review artefacts.

## Defaults and scope

- Use `/Users/liammccarroll/Documents/Projects/better-battery-m2` as the code repository and `/Users/liammccarroll/Documents/Projects/better-battery-m2-plans` as the plans repository when those paths exist. Otherwise locate the corresponding repositories from the current workspace or ask for their locations.
- Write the finished file under `<plans-repository>/branch_problem_solution_test_descriptions/` unless the user specifies another destination.
- Preserve the supplied branch names and order. Do not add parent, dependency, or related branches that were not requested.
- This task is read-only apart from creating the requested CSV and temporary drafting data. Do not check out branches, change code, run deployments, alter configuration, or execute operator tests.
- Never modify or replace an earlier CSV. Create exactly one new timestamped file.

## Evidence workflow

Read [references/writing-guide.md](references/writing-guide.md) before researching or drafting rows.

1. Record the exact branch list and reject duplicates. Resolve every branch to a local commit without changing the working tree. If a branch is missing, report it instead of silently substituting a similarly named ref.
2. Find plans and review artefacts that explicitly name each branch. Prefer an explicit branch declaration inside a plan over filename similarity.
3. Establish the branch's intended comparison parent. For a stacked branch, use the declared parent or review target rather than `master`; otherwise inherited changes will be misdescribed as part of the branch.
4. Inspect the branch-only diff, commits, tests, configuration changes, templates, and operational artefacts. Reconcile them with the plan and reviews. Current branch contents outrank stale proposed wording, while accepted scope and operational prerequisites still matter.
5. Draft all five fields from evidence. Include dependencies, manual configuration/profile activation, or developer-only verification where they affect whether an operator can test or pass the change. Do not invent fixtures, UI paths, receivers, numeric results, or supported scenarios.
6. Review the rows together for overlap, supersession, and shared prerequisites. Say when one requested branch changes another row's expected result.

Stop and ask for clarification only when a missing ref or genuinely ambiguous parent prevents an accurate branch-specific description. Do not hide uncertainty inside confident prose.

## Write and verify the CSV

Prepare a temporary JSON array using the exact keys documented in the writing guide, then run:

```bash
python3 scripts/write_branch_descriptions.py rows.json \
  --output-dir <plans-repository>/branch_problem_solution_test_descriptions
```

Use the copy of the script inside this skill, resolving `scripts/` relative to this `SKILL.md`. The script validates the schema and creates the timestamped CSV without overwriting an existing file.

After writing, parse the CSV with Python's `csv` module and confirm:

- the header is exact and in the required order;
- row count and branch order match the supplied list;
- each field is non-empty and each branch appears once;
- the file has a UTF-8 BOM, CRLF record endings, and a final record terminator;
- no earlier CSV was changed.

Report the output path and the number of branches represented. Briefly identify any evidence limitation that materially narrowed a row.

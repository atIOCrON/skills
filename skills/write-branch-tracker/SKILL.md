---
name: write-branch-tracker
description: Create a CSV or create/update a Google Sheet tracking supplied Better Battery Git branches, their dependencies, plan status, classifications, operator problems, solutions, and test descriptions. Use for branch tracking and operator handoff, not implementation, deployment, or test execution.
disable-model-invocation: true
metadata:
  layer: capability
---

# Write Branch Tracker

Write one row per requested branch. For current builds, use the strict JSON
contract in [references/operational-records.md](references/operational-records.md)
and [its schema](references/operational-records.schema.json). Operator fields
come only from the selected build/source/pin's `operator_handoff`; never redraft
them independently from a Sheet or Markdown. Report missing/draft/stale data to
the coordinator for reconciliation. Historical research below applies only to
explicitly requested records without canonical handoff data.

## Destination and scope

- If the destination is missing, ask **CSV file** or **Google Drive** before
  writing. Do not ask again when the user has already specified it.
- CSV: create one new timestamped file under
  `<plans-repository>/branch_tracker/`, unless the user provides another path.
  Never replace an earlier CSV.
- Google Drive: require a folder URL/path or spreadsheet URL. A folder means a
  new native Google Sheet; a spreadsheet means update that file. Resolve the
  folder and target tab; ask when either is ambiguous. Read
  [references/google-sheets.md](references/google-sheets.md) for this route.
- Default repositories are
  `/Users/liammccarroll/Documents/Projects/better-battery-m2` and
  `/Users/liammccarroll/Documents/Projects/better-battery-m2-plans` when present.
  Otherwise locate them from the workspace or ask for their locations.
- Preserve exact requested branch names; reject duplicates. Inspect related
  branches as evidence without adding unrequested rows.
- Only write the requested tracker and temporary drafting data. Do not check
  out branches, edit code or plans, deploy, change configuration, or run tests.

## Evidence and ordering

Read [references/writing-guide.md](references/writing-guide.md) before drafting.

1. Resolve each branch to a local commit without changing the working tree.
   Report missing refs rather than substituting similar names.
2. Find the canonical release manifest, matching slice plans, and reviews.
   Prefer explicit branch declarations over filename similarity. The manifest
   owns release order, targets, and dependencies; reconcile conflicts with Git
   and plan evidence instead of copying state from a spreadsheet.
3. Establish the intended parent and inspect the branch-only diff, commits,
   tests, configuration, templates, and operational artefacts. Describe current
   implementation rather than stale proposed wording; retain supported scope
   and operational prerequisites.
4. Group branches by demonstrated dependency relationships, including omitted
   ancestors where evidenced. Sharing only the base does not join stacks.
   Independent branches form separate stacks. Number stacks from 1 by their
   first appearance in the request. Keep each stack together, place parents
   before descendants, and retain supplied order among eligible siblings.
   Assign unique `Sort` values from 1 across all output rows.
5. Derive status from the current plan lifecycle and classify purpose, surfaces,
   and changed packages. Draft operator descriptions with evidenced scenarios,
   prerequisites, and limits; do not invent fixtures or pass claims.
6. Check overlap, supersession, and shared prerequisites. Each row describes its
   own contribution. State when another requested branch changes its expected
   result.

Ask when a missing ref or unresolved parent, plan status, or dependency conflict
prevents an accurate row. A missing plan alone may leave `Plan` blank if status
is independently supported; report that evidence limitation.

## Validate and deliver

For current builds, generate the exact 15-key rows from canonical JSON:

```bash
python3 scripts/export_operator_rows.py <project> <build-manifest> \
  --source <branch> --source <other-branch> > <temporary-rows.json>
```

The exporter validates the contract and selected pin and rejects missing, draft
or stale handoffs. It reads JSON only and preserves the four operator texts
apart from flattening whitespace for CSV cells. Then validate/deliver those rows
with the writer below. For explicit historical research, prepare the same exact
15-key array using the writing guide. Resolve scripts relative to `SKILL.md`:

```bash
python3 scripts/write_branch_tracker.py rows.json \
  --output-dir <plans-repository>/branch_tracker
```

For Google Sheets, validate the draft without creating a CSV:

```bash
python3 scripts/write_branch_tracker.py rows.json --validate-only
```

The script checks schema, classifications, blank operator fields, consecutive
sort/stack numbers, and parent ordering within the supplied rows. Confirm
evidenced dependency relationships separately, including omitted ancestors.

Read back the deliverable. Confirm the exact header, requested branch coverage,
dependency order, classifications, status evidence, and preserved operator data.
For CSV, also confirm UTF-8 BOM, CRLF records, and a final record terminator.
For an existing Sheet, apply the full-table reconciliation rules in its reference.

Report the file path or spreadsheet link, row count, and material evidence limits.

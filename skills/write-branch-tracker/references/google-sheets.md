# Google Sheets Destination

Use the available Google Drive/Sheets capability and its native-file workflows.
Read its skill and task-specific references before file or cell operations.
Do not use the example spreadsheet as a write destination unless requested.

## Resolve the destination

- Folder URL or unambiguous folder path: resolve the folder, verify access, and
  create one new timestamped native Google Sheet there. Use
  `YYYY-MM-DDTHH-MM-SS+ZZZZ-branch-tracker` in the user's timezone.
- Spreadsheet URL: inspect metadata and bounded header/row reads. Use an
  explicitly selected tab or linked `gid`; otherwise select the sole matching
  tracker tab and ask if ambiguous. Update that spreadsheet rather than making
  a new one.
- A folder name/path with multiple matches needs clarification. Do not choose
  an arbitrary folder or change sharing permissions.

For creation, follow the installed capability's native creation/import route.
Use the exact writing-guide schema, numeric Sort/Stack cells, a frozen header,
filtering, and allowed Status values. Add native type/surface choices when the
capability supports the intended multi-value behaviour; otherwise retain the
canonical semicolon-separated text. Avoid single-choice validation that
rejects legitimate multi-value cells.

## Update an existing tracker

1. Read headers, existing branch identities, operator cells, and relevant
   formulas/validation before writing. Refresh reads if the file changes.
2. Match by exact `Source Branch`, never row number or display order. Ask about
   duplicate identities or ambiguous header migrations. Map legacy `Branch`
   to `Source Branch` when unambiguous. Migrate `Complete` to `Done` only when
   current plan evidence supports it.
3. Update generated fields only for requested branches; append missing branches.
   Preserve unrequested rows, unrelated tabs/columns, and existing `To Do` and
   `Note` cells, including formulas, links, and formatting. New operator cells
   are empty. Do not clear a full row or sheet to refresh generated fields.
4. Reconcile Sort/Stack across the full tracker so numbers remain unique,
   consecutive, and consistent with dependency groups. Existing operator order
   may be retained where dependencies permit. Inspect unrequested branches only
   as needed to establish order; change their Sort/Stack only. If that context
   cannot be established, ask for scope/order clarification before writing.
   Draft validation covers the requested rows; verify full-table numbering
   separately after the merge. Do not renumber from 1 only within an appended
   subset or silently create collisions.
5. If physically moving rows, move complete records so operator entries and
   other row-owned cells stay attached to their source branch. Sorting via the
   Sort column is sufficient; physical reordering is optional.

## Verify

Read back headers, requested generated fields, preserved operator cells,
full-table Sort/Stack values, and final file metadata. Confirm the parent folder
for a new file and the unchanged spreadsheet identity for an update. Return
the verified spreadsheet link and requested branch count. Report limitations
without substituting a CSV when the requested Drive destination is unavailable.

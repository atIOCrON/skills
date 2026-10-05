# Change Request Description

Compose a forge-neutral change request title and description for a pushed branch.
Read-only: do not create change requests, push, commit, or edit files.

## Inputs

Require:

- pushed source branch;
- target branch, defaulting to the repository's remote default.

For a schema-v2 build, read the selected source/pin's `operator_handoff` under
the operational-records contract. Copy ready, matching-pin problem, solution,
test_path and pass_condition into their sections; link the canonical manifest.
Do not reconstruct missing JSON from a Sheet or Markdown, or silently copy
draft/stale wording. Report it for the build coordinator to reconcile.

For an explicitly supplied historical stack sheet without canonical handoff
data, use its matching source-branch row. Investigate branch contradictions and
report conflicts between canonical JSON and Sheet text; do not silently choose.
Suggested paths and conditions are not executed acceptance results.

## Workflow

1. Run `git fetch origin <target>`.
2. Inspect `git log --oneline --decorate origin/<target>...refs/heads/<source>`.
3. Inspect `git diff --stat origin/<target>...refs/heads/<source>`.
4. Inspect `git diff origin/<target>...refs/heads/<source>` when needed for
   accurate scope.
5. Stop with a clear message if the branch or target is missing.

## Composition

Title: short release-note-style headline.

Description template:

```markdown
## Problem

## Solution

## Scope

## Verification

## Suggested operator test path

## Pass condition

## Risk / Rollback
```

### Stack Sheet Text

Copy applicable fields verbatim, preserving wording, qualifications, pending
acceptance, and dependency context. Markdown formatting may change; do not
shorten or paraphrase the text for concision.

| Sheet field | Description section |
| --- | --- |
| Operator problem | Problem |
| Solution | Solution |
| Suggested operator test path | Suggested operator test path |
| Pass condition | Pass condition |

Link the source sheet row. If branch evidence contradicts a field, report the
discrepancy rather than silently rewriting it or copying inaccurate text.
Without applicable sheet text, write these sections from the branch and its
plan; omit test-path and pass-condition sections when irrelevant.

### Branch Evidence

- **Solution:** explain what this branch implements and its resulting behavior.
  Add necessary implementation detail separately from copied sheet text.
- **Scope:** identify boundaries and relevant dependencies; do not attribute
  predecessor changes or later integration behavior to this branch.
- **Verification:** state completed checks and results, the tested revision and
  environment, and pending validation. A commit SHA or review status alone is
  not testing evidence; a test path or pass condition is not a recorded pass.
- **Risk / Rollback:** describe material risks, how to revert, and consequences
  for persisted data, configuration, dependencies, or external effects.

Keep essential acceptance criteria self-contained; summarize and link any
criteria referenced only by identifier. Scale authored detail to the change.
Allow one brief, linked dependency or integration-merge instruction when it
affects review or merging. Exclude repeated workflow status, inflated diffs,
rebasing plans, and unrelated process mechanics.

## Output

Return only the title and description. Do not include commands or file edits.

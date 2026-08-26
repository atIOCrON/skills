---
name: gitlab-mr-description
description: Compose a GitLab merge request title and description for a pushed branch from its diff against the target branch, using the Problem/Solution/Scope/Verification/Risk-Rollback template. Use when asked to draft or write an MR title or description. Read-only; does not create the merge request; use gitlab-create-mr for that.
metadata:
  layer: capability
---

# GitLab MR Description

Compose a GitLab merge request title and description for a pushed branch.
Read-only: do not create merge requests, push, commit, or edit files.

## Inputs

Require:

- pushed branch;
- target branch, defaulting to `develop`.

## Workflow

1. Run `git fetch origin <target>`.
2. Inspect `git log --oneline --decorate origin/<target>...HEAD`.
3. Inspect `git diff --stat origin/<target>...HEAD`.
4. Inspect `git diff origin/<target>...HEAD` when needed for accurate scope.
5. Stop with a clear message if the branch or target is missing.

## Composition

Title: short release-note-style headline.

Description template:

```markdown
## Problem

## Solution

## Scope

## Verification

## Risk / Rollback
```

Describe only this branch's intended change. Do not include stacked-branch
status, inflated diffs, rebasing plans, or branch/process mechanics.

## Output

Return only the title and description. Do not include commands or file edits.

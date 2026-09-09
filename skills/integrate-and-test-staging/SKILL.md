---
name: integrate-and-test-staging
description: Combine requested changes, deploy to staging, and verify their behavior.
---

# Integrate and test staging

## Prepare

- Read repository and deployment instructions.
- Verify the target environment, current release and requested changes.
- Identify dependencies, conflicts and changes already deployed.
- Define acceptance checks for each change.

## Integrate

- Use an isolated worktree and integration branch based on current staging.
- Preserve source branches and include every requested change.
- Review the combined diff and run relevant checks.
- Create a PR or MR documenting scope, validation and required settings.

## Deploy

- Merge and deploy within the user’s authorization.
- Record the previous release and a rollback path.
- Apply only required code, configuration and database changes.
- If deployment fails, inspect its state before retrying or rolling back.
- Verify the active release and site availability.

## Validate

- Test each change on the live staging site.
- Check observable behavior, including relevant failure cases.
- Verify external results where applicable.
- Remove test fixtures and restore temporary settings.

## Report

State what was deployed, what passed, what remains unresolved and where the evidence is saved. Distinguish deployment status from test results.

Leave production unchanged.

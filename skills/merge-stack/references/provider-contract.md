# Provider Contract

`scripts/provider.sh` loads `scripts/providers/<name>.sh`, or the same filename
under `MERGE_STACK_PROVIDER_DIR`. Provider names use lowercase letters, digits,
and hyphens.

An adapter receives:

```text
<remote> <operation> [arguments...]
```

It must support these operations:

- `auth-check`
- `get-change <branch|url|id>`
- `list-by-target <branch>`
- `retarget <id> <branch>`
- `merge <id> <head-sha> <target-branch> <base-sha> [merge-commit|squash]`

Omitting the strategy means `merge-commit` on every provider. Squash requires
an explicit `squash` argument; disabled merge commits never trigger a fallback.
The Bitbucket adapter also supports publication's `create` operation through
the shared `scripts/bitbucket_cloud.py`.
Bitbucket also returns `draft`, `author_uuid`, `merge_commit_allowed`,
`source_branch_auto_delete`, `policy_status`, and raw `policy_checks`.
`policy_status` is `passed`, `blocked`, `queue-required`, or `unknown`.
`checks_status: not-required` is allowed only in release mode when no expected
build applies. Fields such as approval SHA or target protection stay null when
the provider cannot establish them; release mode uses applicable provider checks
and explicit user merge authorization rather than the squash-specific gate.

Each successful operation prints one JSON value. `get-change` returns:

```json
{
  "provider": "example",
  "id": "opaque-id",
  "url": "https://example.test/change/1",
  "state": "open",
  "source_branch": "feature",
  "target_branch": "develop",
  "head_sha": "...",
  "base_sha": "...",
  "target_protected": true,
  "target_policy_enforced": true,
  "review_status": "approved",
  "approval_head_sha": "...",
  "checks_status": "passed",
  "checks_head_sha": "...",
  "mergeability": "mergeable",
  "squash_allowed": true,
  "cross_repository": false,
  "landed_sha": null
}
```

Allowed normalized states:

- `state`: `open`, `merged`, `closed`, `unknown`
- `review_status`: `approved`, `blocked`, `pending`, `unknown`
- `checks_status`: `passed`, `failed`, `pending`, `missing`, `unknown`
- `mergeability`: `mergeable`, `stale`, `conflict`, `blocked`, `checking`,
  `unknown`

`list-by-target` returns an array of `{id, url, source_branch, target_branch}`.
`approval_head_sha` is non-null only when every effective approval applies to
`head_sha`. `checks_head_sha` identifies the tested commit. Missing freshness
data maps to `null`.

`merge` receives `<id> <head-sha> <target-branch> <base-sha>`.
Immediately before merging, it must recheck state, source and target SHAs,
approval freshness, mergeability, selected-strategy capability, remote checks,
and server-enforced up-to-date or merged-result policy for the standard workflow. Release
assembly instead uses the applicable Bitbucket policy checks, merge-commit
or explicit-squash availability, source retention, and pinned inputs described above.
It returns `{status, merge_method, landed_sha}` (`squash` or `merge-commit`) and must prove the source branch
will survive. Branch deletion is a separate opt-in action.

Map incomplete or unrecognized provider data to `unknown`; never infer success.
Use provider IDs as opaque strings. Exit non-zero on authentication, query,
mutation, validation, or unsupported-capability errors.

GitLab reports both `merge_commit_sha` and `squash_commit_sha`; confirmation
selects the field matching the journaled strategy. Require a merge-commit project
method and no mandatory squash for the default. Do not change repository settings.

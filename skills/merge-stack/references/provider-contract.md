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
- `merge <id> <head-sha> <target-branch> <base-sha>`

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
approval freshness, mergeability, squash, remote checks, and server-enforced
up-to-date or merged-result policy.
It returns `{status, merge_method, landed_sha}` and must prove the source branch
will survive. Branch deletion is a separate opt-in action.

Map incomplete or unrecognized provider data to `unknown`; never infer success.
Use provider IDs as opaque strings. Exit non-zero on authentication, query,
mutation, validation, or unsupported-capability errors.

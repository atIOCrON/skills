# Bitbucket Cloud Change Request Adapter

Implement `change-request-lifecycle.md` for Bitbucket Cloud pull requests (PRs)
on `bitbucket.org`. Bitbucket Data Center has a different API and is not covered
by this adapter. Use the Bitbucket Cloud REST API directly; `gh` and `glab` do
not operate this lifecycle.

## Provider Preflight

Require `curl`, `jq`, and an authenticated Bitbucket Cloud user token. Set
`BITBUCKET_TOKEN`; API tokens also need `BITBUCKET_EMAIL` and use Basic
authentication with that email and token. OAuth access tokens use Bearer
authentication without `BITBUCKET_EMAIL`. Never print the token, put it in a URL, or enable shell tracing
while making requests. For an API token, require `read:user:bitbucket`,
`read:repository:bitbucket`, `read:pullrequest:bitbucket`, and
`write:pullrequest:bitbucket` scopes. Confirm `GET /2.0/user` succeeds and retain
its `uuid` as the authenticated author. Stop if identity cannot be verified.

Derive `<workspace>/<repo_slug>` only from an unambiguous `bitbucket.org`
`origin` URL. Require the API repository's `full_name` to match it. This adapter
supports PRs whose source and destination are branches in that same repository.
Set `api` to
`https://api.bitbucket.org/2.0/repositories/<workspace>/<repo_slug>` and use
the selected authentication header for every request.

Apply the lifecycle's local branch, upstream, fetched target, diff, dirty-file,
verified-SHA, and pinned-parent checks, including its return-to-draft exception
for detected movement. Also fetch the target
branch from the API at `GET $api/refs/branches/<URL-encoded-target-branch>`.
Require its `target.hash` to equal `origin/<target-branch>`; for create,
refresh, and ready modes also require the pinned base SHA. Require its
`merge_strategies` array to contain `squash` or
`squash_fast_forward`; record the available option and
`default_merge_strategy`. Availability is the squash capability here. Do not
change repository settings or imply that the default strategy will be used.

The API returns `source.commit.hash` and `destination.commit.hash` in PR
responses. Outside the return-to-draft invalidation case, compare their full
values with the local, upstream, verified, and pinned target SHAs; do not
accept abbreviated hashes. A PR's `state` must be
`OPEN`, while its separate `draft` boolean controls readiness. Bitbucket Cloud
has no PR assignee field: record `assignee: unsupported` and the authenticated
`author.uuid`. If the user expressly requires an assignee, stop.

## Locate The PR

Before creation, enumerate **all pages** of `GET $api/pullrequests?state=OPEN`
by following `next`. Include drafts; do not rely on the web UI's default list,
which hides them. Filter returned PRs by exact `source.branch.name` and
`source.repository.full_name`. Stop if any open PR already uses that source.
For later modes, use the recorded numeric `id`, fetch
`GET $api/pullrequests/<id>`, and require the same source and destination
repository, source branch, target branch, and author identity. Do not silently
reuse or retarget a different PR.

## Create Draft

Compose title and description with `change-request-description.md`. Send
`POST $api/pullrequests` with `Content-Type: application/json` and a JSON body
formed with `jq`, not shell string interpolation:

```json
{
  "title": "<title>",
  "description": "<description>",
  "source": {"branch": {"name": "<branch-name>"}},
  "destination": {"branch": {"name": "<target-branch>"}},
  "draft": true,
  "close_source_branch": false
}
```

Require HTTP 201 and a numeric PR `id`. Fetch that PR again, then repeat the
open-source enumeration and require exactly this one PR. Require `OPEN`,
`draft == true`, the exact source and target branches and SHAs, author UUID,
`close_source_branch == false`, and a nonempty `links.html.href`.

## Refresh Draft

After an accepted and verified source change, require the recorded PR remains
draft. Regenerate metadata from the current branch diff. Send
`PUT $api/pullrequests/<id>` with only `title` and `description`. Fetch the PR
again and require the updated metadata, draft status, source and target
identity, and all lifecycle SHAs. Do not include branch, reviewer, or readiness
fields in this update.

## Return To Draft

Before reviewing a changed source or target, send
`PUT $api/pullrequests/<id>` with `{"draft":true}` for this PR and every ready
descendant. Fetch each PR after its update and require `OPEN` and
`draft == true`. Stop if any transition is not reflected by the API. If a
source change was unexpected, leave it draft and follow the lifecycle's user
confirmation rule before accepting the new SHA.

## Read Checks

List all pages of `GET $api/commit/<source-sha>/statuses` and compare the
statuses with configured Pipelines and merge checks for the target branch.
Wait for required statuses to pass. A pending, failed, or missing required
status blocks readiness. Record `none applicable` only when no status is
configured for this PR. Refetch the PR source SHA after checking.

## Mark Ready

Only after the publication skill confirms the reviewed SHA and applicable
forge checks, refetch the PR,
target branch API object, and target Git ref. Require exact source and target
SHA agreement, `OPEN`, `draft == true`, preserved source branch, and available
squash. Select a qualified independent reviewer allowed by repository policy;
the reviewer must have a Bitbucket UUID different from the PR author's UUID.
Inspect effective default reviewers at
`GET $api/effective-default-reviewers` when applicable.

Preserve the UUIDs of existing reviewers, append the selected reviewer if
absent, and send `PUT $api/pullrequests/<id>` with `draft: false` and that full
`reviewers` array (each entry `{"uuid":"<uuid>"}`). Bitbucket Cloud notifies
reviewers when a draft is marked ready. Fetch the PR again and require
`draft == false`, the reviewer UUID, unchanged branches and SHAs, and all
normalized evidence. Refetch the target branch and Git ref once more. If the
target moved or any ready check fails, immediately return this PR and ready
descendants to draft, then follow the invalidation and restack workflow.

## Output

After **every** mutation, fetch the PR and target branch anew. Report provider
`bitbucket-cloud`, PR `id` and `links.html.href`, `state`, `draft`, source and
target branches and full SHAs, authenticated author UUID, assignee
`unsupported`, requested reviewer UUID, squash strategy availability and
default, and `close_source_branch`. Never call the merge endpoint.

API references: [pull requests](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/),
[branches](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-refs/),
[current user](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-users/),
and [token authentication](https://support.atlassian.com/bitbucket-cloud/docs/using-api-tokens/).

## Release Publication And Assembly

For release modes, use the shared executable `scripts/bitbucket_cloud.py`
bundled into both publication and merge skills. Do not apply this reference's
draft, squash, or automated-review gates. Require Python 3.9+ and the same
authenticated user/repository identity. Bitbucket Data Center is unsupported.

Publication calls `create <source> <target> <head> <base> <metadata.json>`.
It creates a fresh non-draft PR, preserves its source, checks input SHAs,
enumerates every page for duplicates, and verifies the resulting PR. Explicit
reviewers are optional metadata; do not add notifications beyond the authorized
PR workflow. Record intent/results as defined by `release-preparation.md`.

Assembly uses the `merge-stack` provider interface: `auth-check`, `get-change`,
`list-by-target`, `retarget`, and `merge`. Default to destination branch strategy
`merge_commit`; use `squash` only with an explicit override. Require the selected
strategy to be available. Immediately before merging, read the PR, source and target
branches, and `/pullrequests/<id>/mergeability/checks`. Require complete state,
permission and Git checks, no blockers, and every required check passed. Stop
when a merge queue is required; this runner performs direct sequential merges.
Optional advisory checks are reported without inventing an approval requirement.
Repository-required approvals remain enforced by the provider.

Use required named CI statuses from `BITBUCKET_REQUIRED_STATUS_KEYS` when the
repository or release specifies them; these must pass on the exact source SHA.
Otherwise report whether configured build checks apply. Never infer passing CI
or approval freshness from an empty list. Bitbucket approval participants do
not prove which SHA was reviewed, so `approval_head_sha` remains null.

Send the selected `merge_strategy` and `close_source_branch: false` to the
merge endpoint. Handle immediate and asynchronous results; confirm Git parents
and tree using `confirm_merge.sh` before proceeding. The endpoint has no
caller-supplied expected source/base fields: fresh reads are preflight evidence,
not an atomic lease. Stop and report any landed-input mismatch, HTTP failure,
or unknown mutation outcome; reconcile before retrying. Never fall back to
manual pushes or change repository protection to bypass a blocked merge.

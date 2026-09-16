# Bitbucket Cloud Change Request Adapter

Implement `change-request-lifecycle.md` for Bitbucket Cloud pull requests (PRs)
on `bitbucket.org`. Bitbucket Data Center has a different API and is not covered
by this adapter. Use the Bitbucket Cloud REST API directly; `gh` and `glab` do
not operate this lifecycle.

## Provider Preflight

Require `curl`, `jq`, and an authenticated Bitbucket Cloud user token. An API
token or OAuth access token may be supplied as `BITBUCKET_TOKEN` for Bearer
authentication. Never print the token, put it in a URL, or enable shell tracing
while making requests. For an API token, require `read:user:bitbucket`,
`read:repository:bitbucket`, `read:pullrequest:bitbucket`, and
`write:pullrequest:bitbucket` scopes. Confirm `GET /2.0/user` succeeds and retain
its `uuid` as the authenticated author. Stop if identity cannot be verified.

Derive `<workspace>/<repo_slug>` only from an unambiguous `bitbucket.org`
`origin` URL. Require the API repository's `full_name` to match it. This adapter
supports PRs whose source and destination are branches in that same repository.
Set `api` to
`https://api.bitbucket.org/2.0/repositories/<workspace>/<repo_slug>` and use
the header `Authorization: Bearer $BITBUCKET_TOKEN` for every request.

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

## Mark Ready

Only after `code-review-loop.md` returns `Ready for CR review`, refetch the PR,
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

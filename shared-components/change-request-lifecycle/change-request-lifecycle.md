# Change Request Lifecycle

Publish one locally verified and clean-reviewed branch as a draft change
request (CR), then mark it ready after applicable forge checks pass. Do not
edit, commit, push, merge, or delete branches.

## Select The Provider

Identify the forge from `origin` only when its host is unambiguous. Use exactly
one adapter for the whole CR lifecycle:

- GitLab: `change-request-providers/gitlab.md`
- GitHub: `change-request-providers/github.md`
- Bitbucket Cloud (`bitbucket.org`): `change-request-providers/bitbucket-cloud.md`
- Another forge: `change-request-providers/<provider>.md`, satisfying the
  contract below

Do not translate commands from a different provider by guesswork. If no suitable
adapter or authenticated API is available, stop and report the missing support.

## Adapter Contract

An adapter must support `create draft`, `refresh draft`, `return to draft`,
`read checks`, and `mark ready`. It must query the provider after every mutation
and return normalized evidence for:

- provider, CR identifier, URL, state, and draft status;
- source and target branches plus their current commit SHAs;
- requested assignee where supported and independent reviewer; if the provider
  has no PR assignee, report that explicitly and identify the authenticated
  author instead;
- effective squash support: per-CR setting or repository capability; and
- source-branch deletion policy when the provider exposes it.

`read checks` is read-only. Match branch-push and CR pipelines or statuses to
the exact source SHA and distinguish passed, failed, pending, skipped, and
absent. Inspect repository CI and approval policy to identify expected checks;
an absent or skipped expected check blocks readiness. Record `none applicable`
only when no check is configured for that source and CR target.

Before every mode, require the local source branch, fetched target, authenticated
provider, and no dirty file overlapping the CR diff. Use
`origin/<target>...refs/heads/<source>` for log and diff inspection. For create,
refresh, and ready modes, require synchronized upstream; require the source
SHA to equal the local branch ref, upstream, and verified SHA. When ready, also
require the latest clean review SHA. Require the target SHA to equal the pinned
base and remain an ancestor.
For return to draft after detected movement, allow only the SHA or upstream
mismatch being invalidated; fetch and record the actual refs and preserve CR
identity before changing readiness. Do not accept the new source SHA as verified.

Create exactly one draft CR with an explicit source and target. Refresh its
title and description after every accepted source change. Return it and all
ready descendants to draft before a changed source or target is reviewed.
Mark it ready only when the stack manifest's final checks, verified and
clean-reviewed SHA, current source and target SHAs, and applicable forge checks
agree. Then request a qualified independent reviewer allowed by repository
policy. A skipped pipeline does not count as a pass; record when no CR checks
apply.

Compose metadata with `change-request-description.md`. Never merge the CR,
delete its branch, or change repository-wide settings. Stop for duplicate CRs,
identity drift, an unsupported draft transition, wrong target, unavailable
squash, or incomplete normalized evidence.

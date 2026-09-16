# Change Request Lifecycle

Publish and maintain one verified branch as a draft change request (CR), then
mark it ready only after commit-pinned review passes. Do not edit, commit, push,
merge, or delete branches.

## Select The Provider

Identify the forge from `origin` only when its host is unambiguous. Use exactly
one adapter for the whole CR lifecycle:

- GitLab: `change-request-providers/gitlab.md`
- GitHub: `change-request-providers/github.md`
- Another forge: `change-request-providers/<provider>.md`, satisfying the
  contract below

Do not translate commands from a different provider by guesswork. If no suitable
adapter or authenticated API is available, stop and report the missing support.

## Adapter Contract

An adapter must support four modes: `create draft`, `refresh draft`, `return
to draft`, and `mark ready`. It must query the provider after every mutation
and return normalized evidence for:

- provider, CR identifier, URL, state, and draft status;
- source and target branches plus their current commit SHAs;
- requested assignee and independent reviewer;
- effective squash support: per-CR setting or repository capability; and
- source-branch deletion policy when the provider exposes it.

Before every mode, require the expected branch, synchronized upstream, fetched
target, authenticated provider, and no dirty file overlapping the CR diff. Use
`origin/<target>...HEAD` for log and diff inspection. Require the source SHA to
equal local `HEAD`, upstream, the verified SHA, and—when ready—the latest clean
review SHA. Require the target SHA to equal the pinned base and remain an
ancestor.

Create exactly one draft CR with an explicit source and target. Refresh its
title and description after every accepted source change. Return it and all
ready descendants to draft before reviewing a changed source or target. Mark it
ready only after `code-review-loop.md` returns `Ready for CR review`, then
request a qualified independent reviewer allowed by repository policy.

Compose metadata with `change-request-description.md`. Never merge the CR,
delete its branch, or change repository-wide settings. Stop for duplicate CRs,
identity drift, an unsupported draft transition, wrong target, unavailable
squash, or incomplete normalized evidence.

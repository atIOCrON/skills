# Release Preparation Record

Use `plans/releases/<release-id>/preparation.json` for PR assembly state. This
operational record does not replace a build manifest or change its dependency
pins, review evidence, freeze digest, or feature stages. When a build manifest
exists, link this record under `integration.release_preparation` and retain its
original targets; release PR destinations belong here.

Record:

- `kind: "release-preparation"`, `schema_version: 1`, release ID, repository,
  remote, and provider;
- base branch and full SHA; integration branch and starting SHA;
- ordered changes: source, full head SHA, original parent branch and SHA,
  title, description-file path, verification references, and PR ID, URL,
  author UUID, current destination, state, and landed SHA;
- an append-only merge journal path outside the repository;
- candidate commit and tree SHA, staging receipt and acceptance evidence;
- final PR identity and current state.

Pin all inputs before publication. A source change invalidates its recorded
verification and merge authorization; stop for disposition without launching
reviewers or editing code. A target change requires refreshing its diff and
configured checks, not automatically rebasing the source.

Initially, each independent root targets integration; each stacked change
targets its nearest selected unmerged predecessor. Use the input dependency
map and Git ancestry together. Reject unlisted inherited work, cycles, and a
parent that is not an ancestor. Do not turn independent roots into a chain.
An ordering dependency already present in Git must be represented even when
the features are functionally independent. For mixed stacks, keep the user's
order when it puts every predecessor first; otherwise report the conflict.

Fresh runs create new non-draft PRs. Before each creation, record its source,
destination, both SHAs, author, and intended metadata. Immediately record the
returned ID and URL. After interruption, reconcile only a PR from this run:
require the same author, branches, full source SHA, and intended metadata.
An unrecorded but matching creation may be recovered only from its recorded
intent and a unique provider match. Stop for unrelated or duplicate PRs.
Never retry a mutation with an unknown outcome before reconciliation.

## Merge Authorization

Create all individual PRs and present their links, descriptions, pinned heads,
and merge order before merging. Pause for direct user confirmation unless the
user explicitly authorized this release's merges upfront. Creating PRs or
invoking preparation alone is not merge authorization. Do not invent a second
human approval gate; satisfy only checks and approvals required by the forge.

Record that confirmation with `merge-stack/scripts/journal_event.sh`:

```json
{
  "event": "merge-authorized",
  "authorized_by": "user",
  "merge_method": "merge-commit",
  "evidence": "<direct user instruction or confirmation>",
  "changes": [
    {
      "change_id": "<PR ID>",
      "head_sha": "<full source SHA>",
      "target_branch": "<integration branch>"
    }
  ]
}
```

The eventual integration destination is recorded even while a stacked PR
temporarily targets its predecessor. Authorization survives an unchanged run
resumption; it does not cover new changes, rewritten heads, another release,
or the final integration-to-base merge. Source changes need new authorization.
Squash requires an explicit override and authorization recorded with
`merge_method: "squash"`; omitted methods in existing authorization events mean
`merge-commit`.

## Completion

Merging into integration means assembled, not released. Do not move plans to
`plans/slices/done/` or specs to `plans/specs/fulfilled/`, delete sources, or
mark the build manifest released. Freeze the assembled candidate's commit and
tree, deploy that exact commit, and record acceptance separately from
deployment success.

The final PR contains the scope, individual PR links and merge order,
integration resolutions, candidate identity, test and staging evidence,
limitations, and rollback. Create it only after acceptance and current-base
checks pass. Leave it open for the final reviewer; preparation never merges
the final PR or deploys production.

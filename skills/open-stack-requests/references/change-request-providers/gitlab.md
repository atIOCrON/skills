# GitLab Change Request Adapter

Implement `change-request-lifecycle.md` for GitLab merge requests (MRs).

Target `<target-branch>` defaults to the repository default; chained mode must
pass the dependency parent. Use the authenticated user as assignee, preserve
dependency branches, and require squash-on-merge. Reviewers must be qualified,
independent, and allowed by repository approval policy; never request the author
or a committer merely because they are authenticated.

Before every `glab` command, load the bundled non-interactive PATH setup:

```bash
eval "$("$orchestration_skill_root/scripts/ensure_forge_cli.sh" gitlab)"
```

## Provider Preflight

Require authenticated `glab`, the expected local source branch, an upstream, and no
local/upstream divergence. Fetch and resolve the target, then inspect:

```bash
git log --oneline origin/<target-branch>..refs/heads/<branch-name>
git diff --stat origin/<target-branch>...refs/heads/<branch-name>
git diff --name-only origin/<target-branch>...refs/heads/<branch-name>
```

Stop if the target is unresolved, the source equals the target, or dirty files
overlap the branch diff. Unrelated dirty files may remain and must be reported.
Resolve and validate the authenticated username with `glab api user` and `jq`.

## Create Draft

Stop if any open MR already exists for the source branch.

Compose the title and description with `change-request-description.md`, then run:

```bash
glab mr create \
  --draft \
  --source-branch "<branch-name>" \
  --target-branch "<target-branch>" \
  --title "<title>" \
  --description "<description>" \
  --assignee "<gitlab-username>" \
  --squash-before-merge=true \
  --remove-source-branch=false \
  --yes
```

Refresh the MR. Require exactly one open MR with the requested source and target,
draft status, source SHA equal to the verified local and upstream SHA, and
effective `squash_on_merge == true`.

## Refresh Draft

After every accepted source change, including a fix or restack, regenerate the
title and description from the current verified branch diff, then run:

```bash
glab mr update <mr-iid> --title "<title>" --description "<description>"
```

Require the MR source SHA, upstream, local branch ref, and verified SHA to match
afterward.

## Return To Draft

If a ready MR's source or pinned target head changes, run
`glab mr update <mr-iid> --draft` before new verification or review. Refresh and
require draft status; also return every ready descendant to draft. Stop if any
transition fails.

## Read Checks

List branch pipelines through `GET /projects/:id/pipelines?ref=<source-branch>`
and MR pipelines through `GET /projects/:id/merge_requests/:iid/pipelines`.
For each pipeline on the exact source SHA, read its jobs and status. Compare
the result with the source branch's `.gitlab-ci.yml` rules and project merge
checks for this target. A skipped pipeline is expected only when no jobs
apply; record `none applicable` in that case. Stop for missing, pending, or
failed required jobs. Refetch the MR source SHA after checking.

## Mark Ready

Use this mode only after the publication skill confirms the reviewed SHA and
applicable forge checks.
Resolve the existing MR and require:

- it is still draft and targets `<target-branch>`;
- local branch ref, upstream, MR source, latest verified SHA, and latest clean-review
  SHA are identical;
- the fetched MR target head equals the pinned base SHA and remains an ancestor;
  and
- effective squash-on-merge is true.

Resolve the required reviewers or Code Owners from repository policy. Then run:

```bash
glab mr update <mr-iid> --ready --reviewer "<independent-reviewer>"
```

Refresh the MR and target ref again. Require non-draft status, the independent
reviewer or applicable Code Owner, the same source SHA, effective squash, and
target-head equality with the pinned base. If the target moved during readiness,
immediately return this MR and every ready descendant to draft, then require the
ordered invalidation and restack workflow.

## Output

Report the mode, source and target branches, MR URL and status, source SHA,
assignee, reviewer, effective squash setting, and preserved-source setting.

# GitLab Create MR

Create a draft GitLab merge request for the first verified commit, then mark it
ready only after commit-pinned review passes. Do not edit, commit, push, or merge.

Target `<target-branch>` defaults to `develop`; stack mode must pass the stack
parent. Use the authenticated user as assignee and reviewer, preserve stack
branches, and require squash-on-merge.

Before every `glab` command, load the bundled non-interactive PATH setup:

```bash
eval "$("$orchestration_skill_root/scripts/ensure_glab.sh")"
```

## Shared Preflight

Require authenticated `glab`, the expected current branch, an upstream, and no
local/upstream divergence. Fetch and resolve the target, then inspect:

```bash
git log --oneline origin/<target-branch>..HEAD
git diff --stat origin/<target-branch>...HEAD
git diff --name-only origin/<target-branch>...HEAD
```

Stop if the target is unresolved, the source equals the target, or dirty files
overlap the branch diff. Unrelated dirty files may remain and must be reported.
Resolve and validate the authenticated username with `glab api user` and `jq`.

## Create Draft

Use this mode immediately after the first candidate commit is verified and
pushed. Stop if any MR already exists for the source branch.

Compose the title and description with `gitlab-mr-description.md`, then run:

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

Require the MR source SHA, upstream, local `HEAD`, and verified SHA to match
afterward.

## Return To Draft

If a ready MR's source or pinned target head changes, run
`glab mr update <mr-iid> --draft` before new verification or review. Refresh and
require draft status; also return every ready descendant to draft. Stop if any
transition fails.

## Mark Ready

Use this mode only after `code-review-loop` returns `Ready for MR review`.
Resolve the existing MR and require:

- it is still draft and targets `<target-branch>`;
- local `HEAD`, upstream, MR source, latest verified SHA, and latest clean-review
  SHA are identical;
- the fetched MR target head equals the pinned base SHA and remains an ancestor;
  and
- effective squash-on-merge is true.

Then run:

```bash
glab mr update <mr-iid> --ready --reviewer "<gitlab-username>"
```

Refresh the MR and target ref again. Require non-draft status, the requested
reviewer and target, the same source SHA, effective squash-on-merge, and target
head equality with the pinned base. If the target moved during readiness,
immediately return this MR and every ready descendant to draft, then require the
ordered invalidation and restack workflow.

## Output

Report the mode, source and target branches, MR URL and status, source SHA,
assignee, reviewer, effective squash setting, and preserved-source setting.

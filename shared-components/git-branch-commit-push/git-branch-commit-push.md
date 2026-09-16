# Git Branch Commit Push

Create the plan branch before implementation, then commit and push verified
candidate revisions. Do not edit implementation files or create merge requests.

Base branch `<base-branch>` defaults to `develop`; stack mode must pass the
stack parent. Branch names describe the change and use the repository policy or
one of: `fix/` for incorrect behavior, `feature/` for new behavior, `docs/` for
documentation only, `refactor/` for structural changes without intended
behavior changes, or `chore/` for other maintenance. Never name tools, models,
assistants, or bots in a branch.

## Branch Start

Before implementation:

1. Run `git status --short` and `git branch --show-current`.
2. Fetch and prune `origin`.
3. Resolve `<base-branch>` locally and remotely. Stop if it cannot be fetched
   or fast-forwarded.
4. Stop if `<branch-name>` exists locally or on `origin`.
5. Switch to `<base-branch>`, fast-forward it, then create `<branch-name>`:

   ```bash
   git switch <base-branch>
   git pull --ff-only origin <base-branch>
   git switch -c <branch-name>
   ```

Unrelated dirty files are allowed only when these operations do not overwrite
or carry ambiguous implementation state. Record the pinned base SHA immediately
after branch creation. Do not start implementation on the stack parent.

## Candidate Commit

After `staged-diff-scope` approves a candidate tree:

1. Confirm the current branch is `<branch-name>`.
2. Run:

   ```bash
   git status --short
   git diff --cached --stat
   git diff --cached --name-only
   git diff --name-only
   git ls-files --others --exclude-standard
   git diff --cached
   ```

3. Stop if nothing is staged, a staged path is outside scope, or a staged path
   also has unstaged edits.
4. Assert `git write-tree` equals the approved candidate tree SHA.
5. Compose the message with `references/git-commit-message.md` and commit.
6. Assert `git rev-parse HEAD^{tree}` equals the approved candidate tree SHA.
7. Return the commit SHA. Verification must run on this exact commit before it
   is pushed.

Create a new commit for every accepted review-fix batch. Do not amend or
force-push a revision already published to the draft merge request.

## Push Verified Commit

Push only a commit that `verification-runner` verified in a clean detached
worktree:

```bash
git push -u origin <branch-name> # first push
git push                         # later commits
```

Stop if `HEAD` differs from the verified commit SHA. After the push, require
`@{u}...HEAD` to report `0 0`.

## Reviewed-Revision Gate

Before marking the merge request ready, require all of these SHAs to match:

- current `HEAD`;
- upstream branch head;
- latest clean review commit;
- latest verified commit.

Also require the fetched stack-parent head to equal the pinned base SHA and
remain an ancestor. A changed parent requires restacking, verification, and
review of the resulting commit.

## Restack A Published Draft

Use this only when the MR is draft and its stack parent advanced. Require a
clean implementation tree, no staged changes, and an exact old remote tip.

1. Record the old base, old local and remote tips, and new parent SHA. Create a
   recoverable backup ref for the old tip.
2. Rebase the plan commits with
   `git rebase --onto <new-base-sha> <old-base-sha> <branch-name>`. Abort and
   stop on conflicts; conflict resolution is an intentional behavior change.
3. Compare old and new commit ranges with `git range-diff` and deterministic
   patch, tree, and generated-output checks. Classify every delta as `verbatim`,
   `mechanical regeneration`, or `intentional behavior change`.
4. Verify the new tip in a clean detached worktree. Send intentional changes
   through normal implementation scope, verification, and review.
5. Push only with an explicit lease on the recorded remote tip:

   ```bash
   git push --force-with-lease=refs/heads/<branch-name>:<old-remote-sha> \
     origin <branch-name>
   ```

6. Update the pinned base SHA, refresh the draft MR and review pack, and run a
   fresh review of the new base-to-tip range.

Never use an unqualified force push. Stop if the MR is ready, the lease fails,
the source changed unexpectedly, or a delta cannot be classified.

## Stop Conditions

Stop if switching branches would overwrite work, a name already exists, staged
and unstaged changes overlap, the candidate tree changed, commit or push fails,
or any revision identity or restack check fails.

## Output

Report the base branch and SHA, plan branch, candidate tree SHA, commit SHA,
verification status, push status, and unrelated local files.

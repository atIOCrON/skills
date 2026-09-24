# Git Sync Branch

Push verified commits to the corresponding remote branch. Do not create or
change a merge or pull request.

Before creating a remote branch, require the local tip to equal the verified
SHA, the pinned parent to be unchanged, and the remote branch to be absent.
Then create the remote branch:

```bash
git push -u origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

For an adopted remote branch, require the local tip to equal the verified SHA,
the pinned parent to be unchanged, and the freshly fetched remote tip to equal
the tip recorded at adoption and be an ancestor of the verified local SHA. If
the tips already match, no push is needed. Otherwise fast-forward it with the
same explicit refspec. Set upstream if absent, even when no push is needed.
Never force an adopted branch merely to reconcile its starting state.

For a later verified fix, require the fetched remote tip to equal the recorded
tip and be an ancestor of the new local commit. Push with the same explicit
refspec without `-u`.

For a restack, require a recoverable backup ref, the recorded old remote tip,
the new pinned parent, and exact-tip verification. Push a verified tip with
pending reviews when it needs a fresh pass; preserve old review evidence and
keep the manifest review status pending until that pass is clean. A provisional
wave descendant stays in `in_progress/` and cannot be promoted or have a CR
published while its ancestors are unreviewed.
If a change request exists, the publication skill must return it and ready
descendants to draft before the restack. Push only with:

```bash
git push --force-with-lease=refs/heads/<branch-name>:<old-remote-sha> \
  origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

Never use an unqualified force push. After each push, fetch and require local,
upstream, remote, and verified SHAs to match. At final branch handoff, also
require all three clean reviews on the final SHA or their recorded
valid restack or test-only-closure mappings. Stop for a failed push, lease
mismatch, unexpected remote change, or revision drift.

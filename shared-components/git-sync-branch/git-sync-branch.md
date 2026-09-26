# Git Sync Branch

Push verified commits to the corresponding remote branch. Do not create or
change a merge or pull request.

Before creating a remote branch, require the local tip to equal the verified
SHA, the recorded pinned parent SHA to remain an ancestor, and the remote
branch to be absent. If the parent ref has advanced, use an explicit lease for
the expected absence when pushing provisionally. Otherwise create the branch:

```bash
git push -u origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

For the provisional first push, replace that command with:

```bash
git push -u --force-with-lease=refs/heads/<branch-name>: \
  origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

For an adopted remote branch, require the local tip to equal the verified SHA,
the recorded pinned parent SHA to remain an ancestor, and the freshly fetched
remote tip to equal the tip recorded at adoption and be an ancestor of the
verified local SHA. If the tips already match, no push is needed. Otherwise
fast-forward it with the same explicit refspec. Set upstream if absent, even
when no push is needed.
Never force an adopted branch merely to reconcile its starting state.
If its parent ref advanced after the pin, use an explicit lease for the fetched
remote tip on a provisional push.

For a later verified fix, require the fetched remote tip to equal the recorded
tip and be an ancestor of the new local commit. Push with the same explicit
refspec without `-u`; add an explicit lease for the fetched remote tip while
the parent ref has advanced beyond the pin.

For a restack, require a recoverable backup ref, the recorded old remote tip,
the new pinned parent, and exact-tip verification. Push a verified tip with
pending reviews when it needs a fresh pass; preserve old review evidence and
keep current-tip review evidence pending until mapped or freshly reviewed.
A capped slice retains its cap status. A provisional wave descendant stays in
`in_progress/` until its own review passes finish or
reach the cap. A routine restack leaves a completed slice in `review/` while
current-tip evidence is refreshed. Ancestor review status gates ready CRs and
release progression, not draft publication or the stage move.
If a change request exists, the publication skill must return it and ready
descendants to draft before the restack. Push only with:

```bash
git push --force-with-lease=refs/heads/<branch-name>:<old-remote-sha> \
  origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

Never use an unqualified force push. After each push, fetch and require local,
upstream, remote, and verified SHAs to match. For `review/` handoff, require
proportionate trim and clean reviews or the exhausted cap after fixes and
closure. Ready CRs and release progression additionally require clean
current-tip reviews or an accepted capped disposition on the final SHA,
directly or through a proven restack mapping. Stop for a failed push, lease
mismatch, unexpected remote change, or revision drift.

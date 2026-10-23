# Git Sync Branch

Push exact verified local tip to same remote branch; no CR changes. Require pinned
parent ancestry. Coordinator or explicit authoring lease owns publication. Stop on
failed push/lease, unexpected remote change or pin drift; never unqualified force.

| Case | Preconditions and push |
| --- | --- |
| New branch | Remote absent; explicit refspec, -u |
| Adopted branch | Fresh remote equals adoption pin and is ancestor of verified local; no push if equal, set upstream if absent; never force starting state |
| Later fix | Fresh remote equals recorded pin and is ancestor of new verified commit; same refspec without -u |
| Restack | Backup ref, recorded old remote/new parent and exact-tip checks; CR publisher drafts source/ready descendants first; explicit old-tip force lease |

Normal first push:

```bash
git push -u origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

Provisional push after parent ref moves still uses recorded ancestor SHA, but needs
explicit expected-remote lease (absence on first push):

```bash
git push -u --force-with-lease=refs/heads/<branch-name>: origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

Existing provisional/restacked branch uses exact fetched/recorded old remote:

```bash
git push --force-with-lease=refs/heads/<branch-name>:<old-remote-sha> origin refs/heads/<branch-name>:refs/heads/<branch-name>
```

Fetch after each push and require local/upstream/remote/verified equality. New
restacked tips may push pending review to enable fresh passes, preserving old proof
and cap state. Own trim/correctness completion or cap after fixes/closure gates
review-stage handoff, not ancestor review status. Routine restacks keep completed
slices review with coverage pending; unfinished owners remain in_progress.
Rewritten in_release sources invalidate membership under layout. Ready CR/release
requires qualified matched parent chain and current clean reviews or validly mapped
accepted capped disposition; provisional pushes/draft CRs grant none of that.

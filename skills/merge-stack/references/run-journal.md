# Run Journal

Create a JSON Lines journal outside the repository before mutation. Its first
event records the run ID, provider, remote, base branch, and base SHA. Append an
event before and after every rebase, force-push, merge, retarget, and remote
deletion with the relevant change ID, branch, expected and result SHAs.
`journal_event.sh` adds the event name and UTC time.

On resume, read the journal and reconcile each recorded change with provider and
Git state. For an unmatched `force-push-planned`, compare the remote branch with
both `lease_sha` and `rebased_head_sha`: the former means not applied, the latter
means applied, and any other SHA is a blocker. For an unmatched `merge-planned`
or `merge-submitted`, query the provider: an open request at the recorded head
means not confirmed; a merged request must be passed to
`confirm_squash_merge.sh`; any changed head, target, or unknown state is a
blocker. Apply the same planned/completed rule to retargeting and deletion.

Run `scripts/reconcile_run.sh <provider> <remote> <journal>` for this read-only
classification. It reports `not-applied`, `applied-unrecorded`,
`confirmation-required`, or `blocker`. Append the missing completion only after
independently verifying the reported postcondition; never edit prior lines.

Skip only an action whose postcondition is proven. Stop on an unrecorded merge,
changed SHA, target mismatch, or ambiguous partial action. Write cleanup
outcomes without making cleanup part of merge success.

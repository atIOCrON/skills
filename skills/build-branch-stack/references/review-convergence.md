# Review Convergence

An architecture epoch is a sequence of fixes under one design. Record its
number, mechanism, and state owner in the design checkpoint. Start a new epoch
when the mechanism, native owner, state model, dependency strategy, or slice
boundary materially changes; record the prior epoch's failure class and why the
new design removes it.

Within an epoch, group findings by invariant or ownership failure and fix one
root cause instead of adding one guard per example. Do not rerun unchanged
expensive checks or enlarge tests beyond candidate-owned behaviour.

Accept a runtime review finding only when it is reproduced on the pinned SHA
through an existing supported production-like flow or deductively proven from
committed code and a binding contract. Give each accepted finding a failure
family defined by its invariant, runtime owner, supported path, and observable
failure. Match that family across all passes, files, designs, and epochs. Static
plausibility is advisory and cannot trigger code, tests, ledger entries,
closure, or another pass.

Before adopting a broader design, record the demonstrated failure, whether
deletion or simplification resolves it, the existing native owner, whether the
work is one invariant or several outcomes, whether tests exceed production
machinery, and any dependency patch's removal condition. Reject a design when
fewer state owners, async boundaries, patches, or extensions satisfy the same
approved outcome.

Two discovery passes anywhere in the ledger that expose new failures from the
same family, design, or verification model require an autonomous architecture
reassessment before more edits. Changing implementation shape or epoch does
not reset this count. Compare removal, simplification, replacement, upgrade,
the native owner, a narrow dependency correction, and a prerequisite split by
production surface, state ownership, rollback, verification cost, and
maintenance. Select the smallest
viable design, amend the recorded architecture, and continue with a fresh
candidate.

If two epochs fail for the same underlying reason, do not try a third variation
of that mechanism. Remove it, use the native owner, upgrade or narrowly correct
the owning dependency, split a prerequisite, or use an already-supported
contract that still satisfies the approved outcome. Mark the affected chain
blocked only when every viable repository-local option conflicts with a hard
constraint or the approved outcome.

After two accepted fix cycles in one failure family, prohibit another local
variation and record an autonomous continuation decision. Continue only for a
confirmed defect with a viable, non-repeated disposition. Require a human only
when every viable option crosses the authority boundary above.

Run at most five completed fresh three-reviewer discovery passes for one plan.
A pass counts after all three validated outputs are triaged. Closure, output
repair, transport retry, review mapping, and incomplete launches do not count.
The count persists across resumptions, designs, and epochs. After pass 5,
finish accepted remediation, verification, push, and targeted closure. If
another discovery pass would be needed, record `review_cap_reached`; do not
start pass 6. Move the verified pushed slice to `review/` with a capped
`review_handoff` once accepted fixes and closure finish. Seek a separate human
disposition for release readiness; preserve automated review state and follow
`release-manifest.md`.

# Code Review Pack

Build `<feature_dir>/<plan_slug>.reviews/code-review-pack/` for one immutable
base/review SHA boundary shared by fresh reviewers. Required files:

```text
index.md
changed-files.txt
diff-stat.txt
changes.diff
ownership-map.md
verification-summary.md
evidence-manifest.json
acceptance-gates.md
deterministic-checks.md
hash-manifest.sha256
```

Index pins plan/parent branch/base, branch/review commit/tree, UTC creation,
standards sources and evidence links; link approved parent/map/design checkpoint.
Record actual surfaces against checkpoint and new owners/coordinators/lifecycle
interception/template replacements. Without AGENTS identify docs/config/contracts/
tests/patterns used, not invented policy. Trim also needs testing/CI conventions
or explicit absence. Prepared packs name authoring parent/intended placement;
provisional packs identify unreviewed/moved ancestors and relevant inherited
interactions. Scope remains pinned diff until accepted-parent mapping.

Ownership map assigns changed paths to plan/owner. Capture literal deterministic
commands/exits/output. Include smallest determining chain: source, generator/config,
consumer/runtime binding/effective result, pinned revisions/objects/SHA-256 and
explained omissions. Generated changes need source and effective content with
capability input/config/toolchain identities. Review-required external files need
exact copies or sufficient pinned excerpts inside reviewer repository/pack with
authoritative source/revision/replay identity and hash; paths/hashes/commands alone
are insufficient. Keep bulk trees external as code paths, not escaping Markdown links.

Evidence manifest records review SHA and every required check with exact fields:
`id`, `kind` (agent/external), `required`, `verified_sha`, `last_run_sha`, `method`
(direct/identity_reuse/null), `command`, `runtime`, `result`
(passed/failed/pending/blocked_by_environment), `input_identity`, `result_identity`,
`log_path`, `log_sha256`, `reuse_evidence_path`, `reuse_evidence_sha256`. Use explicit
nulls. Direct pins both SHAs to tested tip; reuse pins verified_sha current, retains
origin run, valid log and capability-defined content-addressed input/result proof.
Only required passed agent checks verified for review SHA qualify. Link logs/proof
from verification summary using safe local Markdown links.

Hash every pack file except hash-manifest itself, including nested copies. Validate
after every create/refresh; fix errors before review:

```bash
python3 <skill-root>/scripts/validate_review_pack.py <pack-dir> <repo-root>
```

Validator checks repository boundary/local links, fields/hashes/logs. Acceptance
gates separately list human/external passed/pending/blocked by environment, tested
SHA/release, owner/procedure/prerequisites/evidence/unblock condition. Pending external
proof is no automatic code defect and remains required for acceptance/production.

## Identity and refresh

Use explicit object IDs for diff (including binary), commit/tree, base ancestry,
parent-head movement, local/upstream/fetched-remote/reviewed/verified equality,
clean-worktree checks and capability source/effective identities. Failed check,
unexplained delta or review-tip mismatch blocks review; moved parent makes pinned
review provisional, not invalid by itself.

Build before pass 1. Fix/restack refreshes pins/diff/hashes/checks/evidence. Reuse
proven unchanged capability inputs, never rerun checks merely for fresh review.
Evidence-only closure keeps base/commit/tree and refreshes affected proof/hashes.
Fresh reviewers receive pinned diff, approved slice/parent/map/checkpoint, standards,
reproducible inputs and checks; exclude implementation analysis, prior findings,
triage/fix narratives/conclusions/hints. Distinguish behavioral proof from structural
assertions; structure cannot replace owned runtime proof.

Restack/test-only mapping rules are authoritative in build `code-review-loop.md`.
Pack records old/new ranges/pins, range-diff/delta classifications, determining
identities and parent interaction proof, all three original reviewed SHAs and
intermediate mappings. Equal patches alone are insufficient. Focused unequal
mappings include per-commit comparison/affected tests/exact checks and chosen path's
three original-session confirmations or independent generated-conflict review.
Test-only mappings include changed-test runs, unchanged production/effective inputs,
terminal ledger and originating-session closures. Missing proof/unmapped changes
need fresh discovery below cap; retain prior clean reviews only through valid mappings.
Trim carries through its separate rules. Link specialized capability/reproduction
evidence and exact commands, without copying ecosystem procedures.

Return pack path, base/review SHAs, refreshed files, deterministic status and blockers.

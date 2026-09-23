# Trim Review

Run this phase after every candidate in a bounded wave is implemented,
verified, and pushed, and before any correctness discovery pass for that wave.
Review branches concurrently against their own pinned parent-to-tip diffs.
An unreviewed or moving parent leaves a descendant provisional; it does not
pause that descendant's trim review.

## Standards and scope

For each branch, read the approved plan, design checkpoint, neutral review pack,
and applicable `AGENTS.md`, testing policy, `CONTRIBUTING`, CI rules, and nearby
tests. Use repository rules when present; do not require a new policy file.
Treat nearby patterns as evidence, not binding policy. Keep tests required by a
binding source and the smallest tests that prove candidate-owned behavior.

Use one fresh Claude, Codex, and Cursor reviewer per trim pass. Preflight
external reviewers and launch all three concurrently with the existing
reviewer scripts; use the host's native reviewer for its provider. Give each
the same pinned pack and the prompt below, with its own reviewer slug and
artifact path. Save prompts, raw outputs, session details, and accepted
outputs under `<feature_dir>/<slug>.reviews/trim-review-pass<N>/`. Check that
each output has the required sections, exact SHAs, and concrete evidence;
repair omissions in the same session. Do not reuse correctness review output.

```text
Review phase: trim. Reviewer: <slug>. Trim pass: <N>.
Repository: <root>. Plan: <path>. Neutral pack: <path>.
Pinned parent SHA: <full SHA>. Verified branch tip: <full SHA>.

Confirm both SHAs resolve, the parent is an ancestor, and the parent-to-tip
diff matches the pack; stop if any check fails. Review only that diff. Read
project instructions and testing policy where present. Find concrete
complexity that can be removed
without losing approved behavior, binding checks, or meaningful proof of
candidate-owned behavior. Focus on duplicate or low-signal tests, oversized
fixtures, fake provider/server/persistence lifecycles, broad mocks, redundant
abstractions, speculative compatibility, and machinery larger than the change
it verifies. Do not propose a reduction merely to shorten code or tests. Do
not perform a correctness review or mark correctness clean.

For each proposal, cite changed files and the policy, duplication, or ownership
evidence; name the smallest removal and explain what evidence remains. If
nothing should be removed, say so. Report an obvious correctness concern only
as a separate observation for the later correctness review.

## Trim findings
- [<slug>-trim-p<N>-<NN>] [path:line] <removable complexity> - Evidence: <specific source or comparison> - Reduction: <smallest change> - Retained proof: <test, check, or binding policy evidence>
## Policy conflicts
- <conflict and sources, or None>
## Correctness observations
- <observation for later review, or None>
## Trim result
- <Proportionate | Changes advised | Policy conflict>
```

Write `- None` for an empty findings or observations section.

## Triage and continuation

Triage all three outputs against the pinned SHA. Accept only a concrete,
in-scope reduction whose retained evidence still satisfies the plan and
binding policy; record rejected suggestions and reasons in
`<feature_dir>/<slug>.reviews/trim-review-ledger.md`. A style preference or
test-count target alone is insufficient. If the implementation is already
proportionate, leave it unchanged. Correctness observations do not count as
trim findings or correctness approval.

Fix accepted findings from the earliest affected branch forward. Use the
normal selective stage, new commit, exact-tip verification, and leased push
rules. Refresh its pack and run another trim pass on the changed branch until
no accepted reduction remains. If the same concern recurs after two passes,
reassess the design checkpoint and resolve its cause instead of polishing
incrementally. Trim passes are separate from the five-pass correctness cap.

After upstream trim fixes settle, restack affected descendants in dependency
order and verify each changed tip. Preserve a trim result across a restack
only with an equal `range-diff` and evidence that the new parent preserves the
branch's effective behavior; otherwise run a new trim pass. Record each
branch's trim status, reviewed or mapped tip, and ledger path in the manifest.
Start correctness pass 1 for the wave only after every branch has a
proportionate trim result on its current verified tip or valid mapping. Later
correctness fixes need another trim pass only if they introduce substantial
new code or test machinery or invalidate that mapping. A trim result never
counts as a correctness review.

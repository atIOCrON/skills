# Trim Review

Start a branch's trim as soon as its own tip is verified and pushed and its
parent SHA is pinned. Launch all eligible branches concurrently, subject only
to reviewer capacity. Review each pinned parent-to-tip diff. An unfinished or
moving ancestor leaves a descendant provisional; it does not delay its trim
pass. A verified descendant may push provisionally on its recorded parent SHA
even if the ancestor ref advanced, provided the pinned SHA remains the tip's
ancestor, integrity checks pass, and the push uses an explicit lease against
the expected remote branch state, including absence for a new branch. Restack
at the wave boundary.

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
rules. Within one branch, triage pass N, apply accepted reductions, verify and
push the new tip, refresh its pack, then start pass N+1 immediately. Do not wait
solely for an ancestor restack. Passes on different branches may overlap.
Continue until no accepted reduction remains. If the same concern recurs after
two passes, reassess the design checkpoint and resolve its cause instead of
polishing incrementally. Trim passes are separate from the five-pass
correctness cap.

For each pass, record its UTC completion time at triage, reviewed SHA, accepted
fix SHA, and any reason pass N+1 is waiting in the trim ledger. Mark the fix
SHA pending until its verified push; use `null` only if no fix was accepted.
Name the concrete missing gate, such as an unverified tip, unpushed tip, failed
integrity check, or reviewer capacity. Use `null` when no next pass is needed.
Ancestor movement alone is not a blocker. Record each branch's trim status,
reviewed or mapped tip, and ledger path in the manifest.

At the wave boundary, after upstream fixes settle, restack affected descendants
in dependency order and verify each changed tip. Retain an already proportionate
trim result through a valid restack mapping under `code-review-loop.md`. For a
manual resolution, inspect every resolved hunk and the complete new
parent-to-tip diff against the old proportionate diff. Carry the trim result
forward only when this inspection and effective-identity evidence establish
that the resolution added or reworked no branch-owned code, tests, configuration,
or patch content and introduced no redundancy under the new parent. Record the
old and new SHAs, diff comparison, resolved hunks, identity proof, and conclusion
in the trim ledger; update the manifest's trim SHA and evidence. This trim-only
carry-forward does not preserve correctness reviews; apply the separate
`code-review-loop.md` mapping rules. A new SHA alone needs no trim
pass. New or reworked branch-owned content, changed effective behavior, an
unexplained diff, or uncertain proportionality requires a fresh trim pass.
Start correctness pass 1 when trim is proportionate on its verified tip or
recorded carry-forward, even if other branches are still trimming.
Keep descendant correctness reviews provisional until parent mappings settle.
Later correctness fixes need another trim pass only if they introduce
substantial new code or test machinery or invalidate that mapping. A trim
result never counts as a correctness review.

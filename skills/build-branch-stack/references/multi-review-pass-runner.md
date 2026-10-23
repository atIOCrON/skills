# Multi Review Pass Runner

One numbered code-review pass requires repository/host, phase/pass/label, plan,
envelope/placeholders, artifact path, neutral pack, base/tip and owning code-review
instructions. Fresh parallel Claude/Codex/Cursor: matching native host if supported,
other two preflighted CLIs. Owner handles triage/fixes, not self-review. Use finding-ID
slugs and identical rendered envelope+supplied instructions, no invented prompt or
independently installed skill.

## Launch and artifacts

Owning loop creates `<feature_dir>/<plan_slug>.reviews/<phase>-pass<N>/`; write prompts
before launch, native unchanged. CLI commands:

```bash
"$orchestration_skill_root/scripts/launch_codex_review.sh" <artifact_dir>/codex-prompt.md <artifact_dir> {repo_root}
"$orchestration_skill_root/scripts/launch_claude_review.sh" <artifact_dir>/claude-prompt.md <artifact_dir>
"$orchestration_skill_root/scripts/launch_cursor_review.sh" <artifact_dir>/cursor-prompt.md <artifact_dir> {repo_root}
```

Retain `<reviewer>-prompt.md`, `-raw-attempt<N>.md`, `.md` (accepted normalized),
`-session.md`, `-exit-code`, `-stderr.log`, `-attempts.md`, and `-failure.md` on
failure/stop. Raw/attempts immutable. Metadata binds provider/transport/session/phase/
pass/redacted operation/paths/bytes/failure; coordinator registers original/parent/
replacement/repair contexts in runtime history. Redact body as <prompt-file-stdin>.
Closure artifacts: -closure-round<N>-prompt.md and -closure-round<N>.md. Resume native
origin or:

```bash
"$orchestration_skill_root/scripts/resume_review.sh" <codex|claude|cursor> <closure-prompt> <artifact_dir> {repo_root} closure-round<N>
```

Focused substance clarification uses same transport with content-clarification-round<N>,
saved question/response/original, no extra pass. For code output locally run:

```bash
"$orchestration_skill_root/scripts/repair_code_review_output.sh" <reviewer> <artifact_dir> {repo_root} <pass-number> [--coordinator-assessment <assessment.json>]
```

Normalization saves source-stem-normalization-round<N>.md/.json/-validation.md
with ID mapping/hashes/diagnostics/acceptance; coordinator adds draft/assessment.
Allowlist exact outputs and link pass/triage proof. Follow format-repair invocation
when helper cannot transform safely. Never contact/restart solely for formatting.
Codes 0/10/11/12 mean expected/format/possible-content-gap/unusable; assess whole
response with saved scope/identity evidence, not headings alone. Receipt validated
means substantively complete pinned review with findings preserved. Count after all
three plus triage/mutation check; operational JSON still needs schema validation.

## Liveness and isolation

Poll parallel group on shared 30-second tick; ten minutes is soft checkpoint, not
timeout. Classify transport completed/failed/still-running/liveness-lost and output
valid/format-repairable/completion-repairable/fresh-retry-required. Dead session does
not invalidate usable complete output. Recover saved proof/clarify substance; fresh
review only for unrecoverable coverage/unusable output/unresolved contradictions.

Empty output fails even exit 0: retain captured ID/raw evidence, try resumable ID
once, otherwise one fresh transient retry. Never retry deterministic auth/trust/
permission/command/scope/interactive setup failure; inspect failure artifact/final
attempt decision before relaunch. Stop failed processes.

Before launch hash pack/pre-existing artifacts and snapshot repository. Exclude
only exact expected outputs; after group check allowlist/hashes/all tracked and
untracked state. Unexplained mutation blocks. Review explicit SHAs read-only;
overlapping provisional implementation needs preprepared separate checkout outside
snapshot or independent clone unable to alter reviewer metadata. Keep refs/pack
pinned and never relax mutation checks.

Failure/manual stop `<reviewer>-failure.md`:

```markdown
# <reviewer> Failure
## Reviewer
<reviewer slug>
## Phase And Pass
<phase>, pass <N>
## Attempts
<attempt count and actions>
## Elapsed / Status Checks
<elapsed and observations>
## Failure Class
<failure or repair classification>
## Pass Outcome
<stopped-blocked or continued-by-user-override>
## Override Reason
<reason, or None>
## Detail
<concise diagnostic and artifact paths>
```

Return reviewer table/output/session/failure paths/mutation result and
ready-for-triage, blocked or continued-by-user-override.

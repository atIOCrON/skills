# Multi Review Pass Runner

Run one numbered review pass for one review phase.

## Inputs

Require:

- repository root;
- host provider: `codex`, `claude`, or `cursor`;
- phase: `plan-review` or `code-review`;
- pass number;
- reviewer label;
- plan path;
- prompt envelope path;
- artifact directory;
- neutral review-pack path;
- pinned review base and commit SHAs;
- reviewer instructions supplied by the owning loop from
  `references/code-review.md`;
- placeholder values required by the prompt envelope.

## Reviewers

Run `claude`, `codex`, and `cursor` for every pass in fresh parallel contexts.
Use the implementing host's native sub-agent for its matching reviewer (for
example, a Codex sub-agent when Codex is the host). Launch the other two through
the bundled CLI scripts below and preflight those CLIs. Reviewer slugs are
defined in `references/orchestration-finding-ids.md`.

Combine the supplied bundled reviewer instructions with the same rendered
prompt envelope for each reviewer. Replace the envelope's existing
placeholders only; do not improvise reviewer prompts or tell reviewers to load
an independently installed skill.

## Artifacts

`<artifact_dir>` is created by the owning loop at
`<feature_dir>/<plan_slug>.reviews/<phase>-pass<N>/`.

Persist for each reviewer:

```text
<artifact_dir>/<reviewer>-prompt.md
<artifact_dir>/<reviewer>-raw-attempt1.md
<artifact_dir>/<reviewer>.md
<artifact_dir>/<reviewer>-session.md
<artifact_dir>/<reviewer>-exit-code
<artifact_dir>/<reviewer>-stderr.log
<artifact_dir>/<reviewer>-attempts.md
```

On failure or manual stop, also persist:

```text
<artifact_dir>/<reviewer>-failure.md
```

If closure is later requested by the owning loop, it should persist:

```text
<artifact_dir>/<reviewer>-closure-round<N>-prompt.md
<artifact_dir>/<reviewer>-closure-round<N>.md
```

Keep raw responses and repair attempts unchanged. `<reviewer>.md` is the accepted
normalized copy. Normalization writes `<source-stem>-normalization-round<N>.md`,
`.json` (ID mappings, hashes, diagnostics and acceptance basis), and
`-validation.md`. Coordinator repairs also save a draft and assessment JSON.
Allowlist these exact files and link them from triage/pass evidence.

Session metadata records provider, transport, session reference, phase, pass,
redacted command or native operation, artifact paths, output bytes, and failure
path when applicable. The build orchestrator registers every reviewer context,
including replacement and repair contexts, in the manifest's `sessions` history
under `references/orchestration-runtime.md`; retain persistent and parent IDs
when available and link the saved session metadata.

## Commands

Write every rendered prompt before launch. Send the host review prompt unchanged
to a fresh native reviewer. Launch each non-host reviewer with its provider
script:

Codex review:

```bash
"$orchestration_skill_root/scripts/launch_codex_review.sh" <artifact_dir>/codex-prompt.md <artifact_dir> {repo_root}
```

Claude review:

```bash
"$orchestration_skill_root/scripts/launch_claude_review.sh" <artifact_dir>/claude-prompt.md <artifact_dir>
```

Cursor review:

```bash
"$orchestration_skill_root/scripts/launch_cursor_review.sh" <artifact_dir>/cursor-prompt.md <artifact_dir> {repo_root}
```

Each script generates a fresh session, feeds the prompt on stdin, and writes
`<reviewer>-raw-attempt<N>.md` (one file per transport attempt),
`<reviewer>-session.md` (session metadata), `<reviewer>-exit-code` (the
numeric exit status), `<reviewer>-stderr.log` (stderr for each attempt), and
`<reviewer>-attempts.md` (redacted command shape, byte counts, exit code, and
retry decision per attempt) into the artifact directory.
The redacted command shape records `<prompt-file-stdin>`, not the prompt body.

For closure, resume the native reviewer through the host or run:

```bash
"$orchestration_skill_root/scripts/resume_review.sh" <codex|claude|cursor> <closure-prompt> <artifact_dir> {repo_root} closure-round<N>
```

For substantive clarification, use the same transport with a focused question
and label `content-clarification-round<N>`. Save the question and response;
preserve the original and reassess completeness. Clarification adds no pass.

After code review, native and CLI hosts save the raw response and prompt metadata,
then run this local helper, which never contacts a reviewer:

```bash
"$orchestration_skill_root/scripts/repair_code_review_output.sh" <reviewer> <artifact_dir> {repo_root} <pass-number> [--coordinator-assessment <assessment.json>]
```

The helper repairs recognizable headings and unique legacy IDs. For other
formatting, apply `code-review-format-repair-invocation.md` yourself. Complete,
understandable reviews proceed to triage despite formatting failures; helper
limits never authorize a formatting retry or restart.

Validator codes are diagnostics: `0` expected shape, `10` formatting,
`11` possible content gaps, `12` missing/unusable output. Missing headings are
formatting; missing fields may be established elsewhere. Assess the whole review
and saved scope/identity evidence before deciding substance is missing.

A pass counts after all three reviews are substantively complete on the pinned
scope/SHA, triage finishes, and the mutation check passes. Receipt `validated: true`
records that assessment and preserved findings, not perfect prose formatting.
Link the repair/assessment evidence and retain diagnostics. Repairs add no pass;
operational JSON still requires schema validation.

## Liveness And Failures

- Start all three reviewers in parallel.
- Poll on a shared 30-second tick.
- Treat 10 minutes as a soft checkpoint, not a timeout.
- Classify transport as `completed`, `failed`, `still-running`, or
  `liveness-lost`. Then classify output as `valid`, `format-repairable`,
  `completion-repairable`, or `fresh-retry-required`.
- Follow `code-review-format-repair-invocation.md` for local repair and substantive
  clarification. Fresh discovery is needed only when coverage cannot be recovered,
  output is unusable, or substantive contradictions cannot be resolved. A dead or
  unresumable session does not invalidate a completed usable response.
- When output is empty but a session ID was captured, try that session once
  before starting a fresh reviewer. With no captured session ID, use a fresh
  reviewer.
- Retry once in a fresh session for transient transport failures only when no
  resumable session exists.
- Do not retry deterministic setup failures: auth/login, workspace trust,
  permission denied, command not allowed, inaccessible review scope, or
  interactive prompt requests. Before any owning-loop retry, inspect
  `<reviewer>-failure.md` when present and the final retry decision in
  `<reviewer>-attempts.md`; do not re-launch when the launcher classified the
  failure as deterministic.
- Treat zero-byte stdout as failure even when the reviewer exits `0`. Preserve
  any captured session ID and raw output before deciding whether to resume or
  launch fresh.
- Reviewers are read-only and use explicit commit SHAs. Write prompts, then hash
  the neutral pack and every pre-existing artefact. Snapshot repository state
  before launching the parallel group. Exclude only the exact output files each
  launcher is expected to create, not whole artefact directories. After all
  reviewers finish, verify the new-file allowlist, pre-existing hashes, and all
  other tracked and untracked state. Stop on any unexplained change.
- If implementation overlaps this pass, prepare a separate checkout outside
  the snapshot before launch, or use an independent clone that cannot change
  reviewer repository metadata. Keep the review commit, branch tip, and pack
  pinned. Provisional edits must not touch the snapshotted checkout or artefacts.
  Do not relax the mutation check for implementation changes.
- Do not leave failed reviewer processes running.

## Failure Artifact

On reviewer failure or manual stop, write `<reviewer>-failure.md` using this
template:

```markdown
# <reviewer> Failure

## Reviewer
<reviewer slug>

## Phase And Pass
<phase>, pass <N>

## Attempts
<attempt count and what each attempt did>

## Elapsed / Status Checks
<elapsed time and the liveness checks observed>

## Failure Class
<failure or repair classification>

## Pass Outcome
<stopped-blocked or continued-by-user-override>

## Override Reason
<reason, or None>

## Detail
<short launcher diagnostic with artifact paths or failure summary>
```

## Output

Return:

- reviewer status table;
- output artifact paths;
- session metadata artifact paths;
- failure artifact paths;
- worktree-mutation status;
- pass outcome: `ready-for-triage`, `blocked`, or
  `continued-by-user-override`.

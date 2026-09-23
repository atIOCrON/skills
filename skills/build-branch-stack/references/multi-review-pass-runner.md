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

For format repair, persist every prompt, response, and validation result:

```text
<artifact_dir>/<reviewer>-format-repair-round<N>-prompt.md
<artifact_dir>/<reviewer>-format-repair-round<N>.md
<artifact_dir>/<reviewer>-format-repair-round<N>-validation.md
```

`<reviewer>.md` is canonical only after validation succeeds. Never overwrite
the raw response or a repair attempt.

Session metadata records provider, transport, session reference, phase, pass,
redacted command or native operation, artifact paths, output bytes, and failure
path when applicable.

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

After each code-review launch, validate and, when necessary, repair the output
in the same session:

```bash
"$orchestration_skill_root/scripts/repair_code_review_output.sh" <codex|claude|cursor> <artifact_dir> {repo_root} <pass-number>
```

For a native host reviewer, preserve its raw response, run
`validate_code_review_output.py`, and send
`code-review-format-repair-invocation.md` to that same native reviewer. Apply
the same three-attempt limit and promote its response to `<reviewer>.md` only
after validation succeeds.

The validator returns `0` for valid output, `10` for `format-repairable`, `11`
for `completion-repairable`, and `12` for `fresh-retry-required`. The repair
runner returns `12` when a fresh reviewer is required after applying the rules
below.

## Liveness And Failures

- Start all three reviewers in parallel.
- Poll on a shared 30-second tick.
- Treat 10 minutes as a soft checkpoint, not a timeout.
- Classify transport as `completed`, `failed`, `still-running`, or
  `liveness-lost`. Then classify output as `valid`, `format-repairable`,
  `completion-repairable`, or `fresh-retry-required`.
- `format-repairable` means non-empty review analysis with malformed
  presentation. `completion-repairable` means analysis exists but required
  sections or evidence are missing. Resume the same reviewer with the standard
  repair envelope for up to three attempts. Preserve its analysis and do not
  repeat repository inspection or open new findings.
- Use a fresh reviewer only when the original session cannot be resumed,
  liveness is lost, the output shows no usable review, the reviewer abandons or
  materially contradicts its analysis, or three same-session repairs fail.
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

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
- reviewer instructions supplied by the owning loop from
  `references/code-review.md`;
- placeholder values required by the prompt envelope.

## Reviewers

Run `claude`, `codex`, and `cursor` in fresh parallel contexts. Use the host's
native sub-agent for its matching reviewer and CLI sessions for the other two.
Reviewer slugs are defined in `references/orchestration-finding-ids.md`.

Combine the supplied bundled reviewer instructions with the same rendered
prompt envelope for each reviewer. Replace the envelope's existing
placeholders only; do not improvise reviewer prompts or tell reviewers to load
an independently installed skill.

## Artifacts

`<artifact_dir>` is created by the owning loop at
`plans/<plan_slug>.reviews/<phase>-pass<N>/`.

Persist for each reviewer:

```text
<artifact_dir>/<reviewer>-prompt.md
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
<artifact_dir>/<reviewer>-closure-prompt.md
<artifact_dir>/<reviewer>-closure.md
```

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
`<reviewer>.md` (output),
`<reviewer>-session.md` (session metadata), `<reviewer>-exit-code` (the
numeric exit status), `<reviewer>-stderr.log` (stderr for each attempt), and
`<reviewer>-attempts.md` (redacted command shape, byte counts, exit code, and
retry decision per attempt) into the artifact directory.
The redacted command shape records `<prompt-file-stdin>`, not the prompt body.

For closure, resume the native reviewer through the host or run:

```bash
"$orchestration_skill_root/scripts/resume_review.sh" <codex|claude|cursor> <closure-prompt> <artifact_dir> {repo_root}
```

## Liveness And Failures

- Start all three reviewers in parallel.
- Poll on a shared 30-second tick.
- Treat 10 minutes as a soft checkpoint, not a timeout.
- Classify each reviewer as `completed`, `failed`, `still-running`, or
  `liveness-lost`. Base the `completed`/`failed` classification on the
  persisted `<reviewer>-exit-code` and output files.
- Retry once for transient failures: non-zero exit, empty output,
  invalid/non-review output, missing required sections/evidence, lost liveness,
  or unresumable session/chat.
- Do not retry deterministic setup failures: auth/login, workspace trust,
  permission denied, command not allowed, inaccessible review scope, or
  interactive prompt requests. Before any owning-loop retry, inspect
  `<reviewer>-failure.md` when present and the final retry decision in
  `<reviewer>-attempts.md`; do not re-launch when the launcher classified the
  failure as deterministic.
- The CLI launch scripts must treat zero-byte stdout as a launcher failure even
  when the reviewer exits `0`; they retry once and write a populated failure
  artifact if the retry does not produce output.
- Reviewers are read-only. Snapshot `git status --porcelain` before and after
  each reviewer; stop if it changes.
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
<transient or deterministic failure class>

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

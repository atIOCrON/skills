# Orchestrator Runtime

The host is `codex`, `claude`, or `cursor`.

- Use the host's native sub-agents for implementation and its matching reviewer.
  Use CLI sessions for the other two reviewers.
- Run `claude`, `codex`, and `cursor` in fresh parallel contexts for every
  discovery pass. All three must complete successfully.
- Use a fresh context for each discovery pass. Reuse the implementation
  sub-agent for fixes and the originating reviewer context for closure.

These automated reviews are pre-review evidence, not repository approval. A
qualified independent reviewer or required Code Owner must approve the final
SHA under repository policy.

Use native execution's start, wait, resume, and final-output capture operations.
Persist native output and session metadata in the same artifact shape as CLI
reviewers.

Resolve `orchestration_skill_root` to the directory containing the active
`SKILL.md`. Invoke bundled scripts with absolute paths under that directory.

Record the host provider and provider-to-transport mapping for each run.

## Build Identity

For a new build, generate `stack-build-<YYYYMMDDTHHMMSSZ>` from UTC time and
create `plans/builds/<build-id>/manifest.json` in the original workspace. Require
an unused directory; on collision, obtain a new UTC second rather than overwrite
or reuse another build. Generate the ID once, without a scope slug. Record
`build_id`, the same value in legacy `release_id` for schema compatibility,
`created_at`, and a concise scope description in the manifest. Report its ID
and path. Repairs, added workers and resumed sessions retain the existing ID;
an independent new build gets a new ID. Preserve all existing build IDs.

## Session History

Maintain `sessions` in the build manifest for every contributing context:
orchestrator, implementation, fixes, verification, trim, and correctness review.
Register a session when it starts; update its handoff when it finishes or stops.
For each entry, record:

- `provider`, `role`, and `transport` (`native` or `cli`);
- `session_id`: the provider's persistent chat/thread/session ID;
- `parent_session_id`: the parent context's ID, when available;
- `worker_ref`: the native worker name or runtime reference;
- `plans`, `worktree`, and `commits`: assigned scope and resulting Git SHAs;
- `status`, `started_at`, `ended_at`, and `evidence`: UTC times and saved
  outputs or handoff paths.

Use IDs returned by the provider or verified local metadata. A worker name such
as `/root/implement` is not a persistent session ID. If an ID is unavailable,
record `null` and an `identity_note`; preserve the worker reference and evidence.
Do not infer IDs or resumability from names.

Keep all prior entries. Resuming the same context updates its entry; a fresh or
forked context adds one and links its predecessor with `replaces_session_id`
when applicable. On build resumption, retain legacy session fields and add only
history supported by evidence. Session history records contributions; the
SHA-pinned checks and reviews remain authoritative for readiness.

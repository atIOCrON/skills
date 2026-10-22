# Orchestrator Runtime

Use one coordinating chat and persistent, independent implementation chats.
Release acceptance owners use the same provider transports, execution ownership,
progress retrieval, pause/resume and recovery rules. Their caller assigns testing
scope and names chats `<branch name without feature/> - Acceptance`; it does not
assign the implementation or review route below. Keep acceptance and implementation
owners separate. Native sub-agents do not own acceptance.
New implementation owners use the coordinator's agent product/provider by
default under the selection rules below.
Create one owner chat per independent plan, or one for an approved dependency
chain. Name it `<branch name without feature/> - Implementing`; for a chain,
use its first branch and record every assigned plan. Reuse it for amendments,
verification failures, review findings, and work invalidated by restacking.
Native sub-agents may supply fresh independent reviews; they do not own
implementation. Never use the implementation conversation as its own reviewer.

The implementation owner completes implementation, checks, trim, correctness
loops, closure, and fixes on pinned authoring bases. The coordinator owns
scheduling, canonical plan state and manifest, final order, restacking,
publication, and evidence transfer. After each restack, the coordinator decides
which checks and reviews remain applicable under the existing equivalence and
mapping rules, then sends necessary fixes or fresh review work to that owner.

Give every owner the coordinator's provider, persistent ID, readable name,
canonical manifest path, and return route. Explicitly require reports containing
branch, commit, authoring parent, checks, trim/correctness outcomes, receipts,
remaining dependencies, and handoff evidence. Send a verified candidate early
to unlock dependent work; send worker completion when its own loops finish.
The coordinator promptly retrieves and imports handoffs even when final stack
placement is pending. Keep prompts brief: scope, pins, ownership, instructions
and evidence paths, requested action, and return condition.

## Execution Ownership

Keep one active execution owner per implementation session, across GUI and CLI.
Record the active surface/process and its lease in session history. Before a
follow-up, transfer, pause, or resume, check whether that session is running.
Queue steering through supported messaging, or wait for its turn to stop;
never run a second CLI process against a session executing in the GUI.
A desktop-launch command exiting proves handoff only, not implementation completion.

An individual pause retains the chat, worktree, pins, evidence, and assignment.
Record its reason and explicit resume condition; do not auto-resume it while
other eligible work proceeds. Explicit exclusions remain excluded. A pause
request is pending until acknowledged or execution is confirmed stopped.
On resume, reuse the ID and reconcile branch/remote pins before assigning work.
If a session is genuinely unavailable, preserve history and evidence, diagnose
the transport, and register an explicit replacement linked to its predecessor.
Do not start a replacement merely because work is slow or needs fixes.

## Implementation Provider Selection

Select the implementation provider before discovering or choosing its transport.
Match the coordinator's agent product/provider: ChatGPT → ChatGPT, Codex → Codex,
Claude → Claude, Cursor → Cursor. Inherit the coordinator's model/settings where
supported; do not introduce overrides unless the user requests them. The shared
ChatGPT/Codex transport section does not make those products interchangeable.

Use another implementation provider only when the user explicitly requests or
authorizes it. CLI availability, authentication, convenience, and additional
capacity do not authorize a provider change. If the matching provider cannot
create a persistent implementation chat, report the limitation and request a
provider choice; do not silently fall back to another provider or a native
sub-agent. Continue unrelated eligible work while that decision is pending.

Resume existing owners in their original chats and providers; a coordinator
change does not migrate them. Apply these selection rules to replacement owners
as well. Record the coordinator provider, selected owner provider, and any
explicit user override with its source in session history before creation.
These rules also govern acceptance owners; the multi-provider reviewer
requirements below remain separate.

## Provider Transports

Inspect available tool schemas or installed CLI help before dispatch. Keep
provider IDs, readable names, processes, prompts, outputs, exit codes, and UTC
times. Missing capabilities block that transport, not unrelated owners. Honor
host authorization rules for chat creation and messaging; retain the user's
workflow authorization where available. If direct report-back messaging lacks
required human authorization, save the handoff and let the coordinator read it.
Do not claim that another chat's request itself grants messaging authority.

### ChatGPT/Codex

- **Create:** call `list_projects`, select the intended repository project,
  then `create_thread` with `target.type: project`, local environment, owner
  name and a brief bootstrap that awaits assignment. Register its returned ID
  before sending substantial work. These are normal project chats visible in the
  GUI. Verify the title; use `set_thread_title` if normalization changed the
  required name. Assign an isolated checkout explicitly in the prompt; a shared project
  directory is not isolation. Use managed worktree creation only when permitted
  by the tool and user instructions. Omit model overrides unless requested.
- **Assign/follow up:** use `send_message_to_thread` with the returned `threadId`
  and `hostId`. Retain that chat's settings and send fixes to the same ID.
  A setup `clientThreadId` is not a usable `threadId`; wait for setup completion.
- **Progress/return:** use `wait_threads` for bounded, batched waits with cursors
  (up to eight targets per call); use `timeoutMs: 0` for a snapshot. Read missing
  handoff detail with `read_thread`, including pagination when needed. Import
  completed results before another wait. Use the same messaging tool to report
  back when authorized; otherwise retrieve the owner final response/evidence.
- **Pause/resume:** send a cooperative pause and await its acknowledgement. For
  immediate interruption, use the chat's supported GUI Stop control when
  available; `wait_threads` does not stop execution. Resume with an explicit
  follow-up to the same ID after confirming it is idle. Do not archive a chat
  to pause it.

### Claude

Create from the assigned checkout with a brief bootstrap when substantial work
must wait until the chat is visible. The first command executes its prompt
before returning the ID:

```bash
claude -p "<bootstrap or assignment>" -n "<chat name>" --output-format json
```

Save the JSON and extract `session_id`; require a successful result. Once the
CLI turn exits, hand that session to Claude Desktop through a pseudo-terminal:

```bash
script -q /dev/null claude --desktop --resume <session_id> </dev/null
```

A supported PTY launcher can replace `script`. Check the GUI session identity,
bootstrap history, and a short continuation response before claiming same-chat
GUI continuation. Creation and sidebar visibility alone are insufficient.

- **Assign/follow up:** message the same Desktop session through available
  supported session tools or its GUI. For CLI execution, first confirm Desktop
  is idle and release/transfer its execution ownership through supported controls,
  then run from the original checkout:
  `claude --resume <session_id> -p "<follow-up>" --output-format json`.
  After that turn exits, reopen Desktop with the same PTY handoff when needed.
  An idle GUI can still hold a provider session lock. If the handoff reports
  that the session is open elsewhere, keep the existing owner and use its
  supported surface; diagnose/release ownership before retrying. Never clear
  locks, fork the chat, or start another implementation owner to bypass it.
- **Progress/return:** read supported Desktop session status/messages or the
  owned CLI process output. Capture JSON results and exit status; for ongoing
  turns use supported streaming output or verified session transcript metadata.
  Pin any local transcript lookup to this session ID and checkout; do not scrape
  unrelated conversations. Owners save handoffs to their assigned evidence
  path for coordinator import when no direct messaging route is available.
- **Pause/resume:** use Desktop's Stop control for immediate interruption or
  send a cooperative pause and await acknowledgement. For an owned interactive
  CLI process, interrupt through its PTY; for a noninteractive process use its
  process controller and record the partial result. Confirm stopped before
  transferring surfaces. Resume the same ID with `--resume`, or message that
  idle GUI session. Do not use `--continue` or create another session for fixes.

### Cursor

Use independent persistent CLI chats. Resolve the installed agent executable
(`agent` here; other installations may use `cursor-agent`) through its help.
The editor's `cursor` command is not automatically the agent CLI.
From the assigned checkout, the installed commands are:

```bash
agent create-chat
agent --resume <chatId> -p "<assignment>" --output-format json
```

- **Create/assign:** save the ID from `create-chat`, then assign work with
  `--resume <chatId>`. Record the ID and readable owner name in the manifest;
  the creation command has no name argument. CLI names can also be set through
  a supported interactive `/rename`, when available. Treat these chats as
  CLI-only; do not claim editor GUI visibility.
- **Follow up/resume:** after the prior process stops, run the same explicit
  `--resume <chatId>` command with the amendment, findings, or resume request.
  Use the same checkout and one process per chat; avoid implicit latest-chat
  commands. Honor workspace trust and configured permissions. Trust only the
  assigned inspected checkout; do not add broad permission bypass flags.
- **Progress/return:** capture the owned process output, exit status and JSON
  `session_id`; it must match the assigned ID. `--output-format stream-json`
  supports live progress. Read saved outputs/handoffs without launching another
  turn just to ask for status. `agent ls` is an interactive resume picker, not
  a JSON progress API.
- **Pause/resume:** interrupt the owned interactive process through its PTY or
  stop the owned noninteractive process through its controller. Preserve partial
  output and confirm exit; alternatively request a pause in the next turn.
  Leave the chat persisted, record the explicit resume condition, and resume
  its exact ID. Do not send a second resume while a process is active.

## Review Contexts

Run fresh Claude, Codex, and Cursor reviewers in parallel for every discovery
pass; all three must complete successfully. Use the host's matching native
reviewer where supported and CLI sessions for the other two under
`multi-review-pass-runner.md`. Discovery contexts remain independent of owner
chats; closure resumes the originating reviewer. Keep existing preflight,
read-only review packs, pass caps, normalization, closure, verification,
evidence-reuse and release gates. Automated reviews are pre-review evidence;
repository policy still requires its independent reviewer or Code Owner.

Resolve `orchestration_skill_root` to the active `SKILL.md` directory and use
absolute bundled paths. Record each provider-to-transport mapping.

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

Register every contributing coordinator, implementation/acceptance owner and reviewer
when it starts; update its handoff when it completes, pauses or stops. Under
schema-v2, use `extensions.sessions`, `schedule.extensions.coordinator`, and
`schedule.work[].extensions.owner` for builds. Releases use `extensions.sessions`
for acceptance owners, assigned requirements, candidate/environment pins and
evidence links. Preserve legacy top-level `sessions` when
resuming historical records. Do not add fields outside the canonical schema.

Record each session's `provider`, `role`, `transport` (`project-chat`,
`desktop-session`, `cli`, or `native-reviewer`), `session_id`, readable `name`,
coordinator/parent ID, `worker_ref`, plans, checkout, authoring pins, commits,
status, active execution surface/process, lease, UTC times, and evidence links.
Work extensions also retain `authoring_base`, owner ID, pause/resume condition,
worker-completion receipt, and accepted/restacked pin separately. Coordinator
extensions retain final order, exclusions, capacity, and publication handoffs.
Keep completion evidence on its original SHA even if a restack invalidates
current-tip coverage. Review and check applicability remains SHA-pinned.

Use provider-returned IDs or verified metadata. Names and native worker refs
are not persistent IDs. Record an unavailable coordinator/reviewer ID as null
with an identity note; do not claim a resumable implementation owner without a
verified ID. Resuming the same chat updates its entry; an actual replacement
adds history with `replaces_session_id`. Preserve prior contributions and caps.

Read `provider-transport-validation.md` for the latest smoke-test scope and
limitations. Recheck changed provider capabilities before relying on them.

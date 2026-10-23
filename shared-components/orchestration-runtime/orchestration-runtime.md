# Orchestrator Runtime

One coordinator owns scheduling/canonical state/moves/order/restacks/publication/
evidence transfer and applicability. Persistent independent owners complete each
plan (or approved dependency chain), including implementation/checks/trim/correctness/
closure/fixes. Name `<branch without feature/> - Implementing`, first branch for
chain; record all plans and reuse owner after amendments/failures/restacks. Fresh
native sub-agents may review, never implement or review their own implementation
conversation. Release acceptance uses separate persistent `<branch without feature/> - Acceptance`
owners with caller-assigned test scope/pins, same runtime, no implementation route
or native acceptance ownership.

Give each owner coordinator provider/ID/name, canonical path, return route, scope/
pins/lease, instructions/evidence and return condition. Require early verified
candidate and final completion: branch/commit/authoring parent, checks, trim/
correctness receipts/outcomes, dependencies/blockers/paths. Retrieve/import promptly,
even before placement. Keep prompts brief; launcher exit is dispatch, not completion.

## Provider and execution ownership

New owners match coordinator product exactly (ChatGPT/Codex/Claude/Cursor), inheriting
settings without unsolicited model overrides. Different provider needs explicit user
authorization; installed/authenticated CLI or capacity grants none. Missing persistent
transport requires provider choice, never fallback/native implementer. Existing owners
resume original provider/ID even after coordinator change. Record selection/override
source before creation, also for replacement/acceptance owners.

One active executor per session across GUI/CLI; record surface/process/lease, check
before follow-up/transfer/pause/resume and queue supported steering or wait. Never
start CLI while GUI executes. Pause retains assignment/chat/worktree/pins/evidence/
reason/explicit resume condition until acknowledged/stopped; no auto-resume/reassignment.
Resume same ID after pin reconciliation. Replace only diagnosed genuine unavailability,
not slowness/fixes, retaining history/replacement link.

Inspect tool schemas/installed help; capture IDs/names/processes/prompts/results/exits/
UTC times. Missing capability blocks transport only. Honor human creation/messaging
authorization; another chat's request grants none. Unauthorized push reporting saves
handoff for retrieval instead.

## Provider transports

### ChatGPT/Codex

- list_projects→create_thread for intended project/local environment, required name,
  bootstrap awaiting assignment. Register usable threadId before work (clientThreadId
  is setup-only); repair normalized title via set_thread_title. Require GUI-visible
  project chat and isolated checkout; shared project directory is not isolation.
  Managed worktree only when permitted; omit model overrides.
- Assign/follow up via send_message_to_thread with exact threadId/hostId/settings.
  Retrieve with cursor-based bounded wait_threads batches up to eight (zero for
  snapshot); read_thread/pagination for missing detail. Import before waiting.
  Same tool reports back only if human-authorized, else retrieve final/saved handoff.
- Cooperative pause needs acknowledgement; immediate Stop uses supported GUI.
  Wait never stops, archive never pauses. Confirm idle before explicit same-ID resume.

### Claude

From assigned checkout save successful result/session_id (first prompt executes):

```bash
claude -p "<bootstrap or assignment>" -n "<chat name>" --output-format json
```

After CLI exits hand same session to Desktop through PTY:

```bash
script -q /dev/null claude --desktop --resume <session_id> </dev/null
```

Supported PTY launcher may replace script. Verify GUI ID/bootstrap/continuation,
not visibility alone. Follow up in supported Desktop surface. CLI handback requires
idle Desktop and supported ownership release, then original checkout:
`claude --resume <session_id> -p "<follow-up>" --output-format json`.
Reopen same Desktop after exit if needed. Idle GUI may retain lock; “open elsewhere”
requires existing surface/diagnosis/release, never clearing lock/fork/replacement.
Use no implicit --continue. Read only owned process/status/stream or transcript
metadata pinned to ID/checkout, never unrelated chats; save outputs/exits/handoffs.
Pause through Desktop Stop, owned PTY interrupt/process controller or acknowledged
cooperative request. Preserve partial output and confirm stop before transfer/resume.

### Cursor

Resolve installed agent via help (agent here, sometimes cursor-agent), not editor
cursor command. From assigned checkout:

```bash
agent create-chat
agent --resume <chatId> -p "<assignment>" --output-format json
```

Record ID before assignment/readable manifest name; creation has no name argument.
Supported interactive /rename is optional. CLI-only, no claimed editor visibility.
Same-ID/checkout follow-ups only after prior process stops; no latest-chat shortcut.
Honor inspected workspace trust/permissions, no broad bypass. Capture exit/output/
matching JSON session_id; stream-json supports live progress, saved results status
without new turn. agent ls is interactive picker, not JSON API. Pause owned PTY/
process or acknowledged request, preserve partial output/stopped state and resume
exact persisted ID/condition, never concurrently.

## Reviews and history

Fresh parallel Claude/Codex/Cursor discovery contexts must all succeed substantively;
matching native host where supported, other two preflighted CLIs under
multi-review-pass-runner. Closure resumes originating session. Preserve pack/mutation/
normalization/cap/verification/reuse/release gates. Automated review does not replace
repository independent reviewer/Code Owner. Skill root is active SKILL.md directory;
use absolute bundled paths and record provider/transport mapping.

New build ID once-generated UTC stack-build-<YYYYMMDDTHHMMSSZ> in original plans/builds.
Require unused directory; collision obtains new UTC second, never overwrite/reuse.
Record ID/time/scope/path; repairs/resumes/new owners retain ID, independent new build
gets new one. Preserve historical release_id only where format permits, never v2 alias.

Register every coordinator/owner/reviewer at start/handoff/pause/stop. V2 builds use
extensions.sessions, schedule.extensions.coordinator, work extensions.owner; releases
session extensions hold acceptance scope/environment/pins/evidence. Preserve old
sessions in historical formats. Record provider/role/transport (project-chat,
desktop-session, cli, native-reviewer), persistent ID/name, parent/coordinator,
worker ref/plans/checkout/pins/commits/status, executor/lease, UTC times/evidence.
Work extensions retain authoring base/pause-resume/original completion/accepted pin;
schedule extensions retain order/exclusions/capacity/publication handoffs.
Completion history does not qualify rewritten tips.

Use provider IDs/verified metadata, never name/native ref as persistent ID.
Unavailable coordinator/reviewer ID=null with note; resumable implementer requires
verified ID. Resume updates entry, real replacement adds replaces_session_id retaining
history/caps. Read provider-transport-validation.md for test limits; recheck changed
capabilities after updates.

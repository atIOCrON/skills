# Provider Transport Validation

Smoke tests on 2026-10-13 (Australia/Sydney). Prompts requested token replies,
no tools and no project-file access or changes. Claude and Cursor ran from
empty temporary directories; Codex used a normal local skills project chat.
These tests establish transport continuity, not implementation correctness.

| Provider | Persistent ID | Observed result |
| --- | --- | --- |
| Codex | `01a1349e-cbd3-7e02-aa7b-02af9796cb05` | Normal project chat named `transport-smoke-test - Implementing`; create, message, wait, read, cooperative pause and explicit resume passed. Follow-up recalled `CODEX_BOOTSTRAP_OK`. |
| Claude | `ab5f66f6-8472-4ed5-bbe6-7376ceaa556d` | CLI bootstrap, PTY Desktop handoff, GUI continuation, CLI continuation and turn-boundary pause/resume passed with the same ID and remembered `CLAUDE_CONTINUITY_7`. |
| Cursor | `ebcbf96d-fcb7-4f13-ade9-e84ad47e6668` | `agent create-chat`, assignment, explicit-ID follow-up and turn-boundary pause/resume passed. JSON retained the ID and remembered `CURSOR_CONTINUITY_9`. CLI-only. |

Claude CLI was 2.1.288; the GUI continuation transcript reported 2.1.295.
Cursor Agent was `2026.10.01-14929f9`. Help confirmed `create-chat` takes no
name argument and `--resume [chatId]` selects a persisted chat. The readable
Cursor name therefore belongs in the manifest; interactive renaming was not
needed or tested. No model overrides were supplied.

Claude GUI showed `claude.ai/epitaxy/local_<session_id>`, the bootstrap and
`CLAUDE_CONTINUITY_7 GUI_CONTINUATION_OK`. Its transcript retained that ID and
`entrypoint: claude-desktop`. CLI handback recalled the GUI token and returned
`CLI_HANDBACK_OK`. A subsequent Desktop reopening was rejected with:
`Session <id> is open in another terminal. Run /desktop there instead.`
The existing GUI remained open. Repeated CLI/GUI ownership transfer is therefore
not fully verified; an idle surface alone is insufficient proof of lock release.
The runtime now requires supported ownership release and forbids bypassing locks.

Cursor first refused the untrusted temporary workspace. Rerunning with `--trust`
on that inspected empty directory and read-only `--mode ask` passed. No broad
permission bypass was used. Test output was captured outside the repository.

Not exercised: interruption during an active tool/process, crash recovery,
provider Desktop session messaging APIs, direct owner-to-coordinator push
reports, managed worktree setup, streaming progress, cloud ChatGPT execution,
or a complete multi-plan implementation/review/restack/release run. Coordinator
retrieval of Codex final responses and Claude/Cursor saved outputs was tested.
The three-provider review requirements and Git/release gates remain unchanged.

Command semantics were checked against installed help and the official
[Claude Desktop documentation](https://code.claude.com/docs/en/desktop#coming-from-the-cli)
and [Cursor CLI parameters](https://prod.cursor.com/docs/cli/reference/parameters).
Revalidate after provider updates; these results do not establish GUI visibility
for Cursor or universal availability of Claude Desktop handoffs.

## Repository Validation

Bundle synchronization and `git diff --check` passed. The repository skill
validator passed against an isolated copy of the tracked skills plus new
references. Its full-checkout run stopped on the pre-existing untracked
`safe-dev-disk-cleanup` skill's invocation metadata. That skill was left intact.
The generic skill-creator validator rejects this repository's existing
`disable-model-invocation` frontmatter key; the repository validator supports it.

Existing schedule tests (11), evidence-reuse tests (29), review normalization
tests (18), and both reviewer/runtime launcher smoke suites passed. These are
regression checks of the retained gates and transports; they do not constitute
a full build under the revised workflow.

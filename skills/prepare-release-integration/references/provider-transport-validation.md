# Provider Transport Validation

Smoke tests: 2026-10-13 Australia/Sydney; token-only prompts, no tools/project-file
changes. Claude/Cursor used empty temporary directories; Codex used local skills
project chat. These establish continuity, not implementation correctness.

| Provider / persistent ID | Tested continuity |
| --- | --- |
| Codex `01a1349e-cbd3-7e02-aa7b-02af9796cb05` | GUI project chat `transport-smoke-test - Implementing`; create/message/wait/read/cooperative pause/resume; recalled `CODEX_BOOTSTRAP_OK` |
| Claude `ab5f66f6-8472-4ed5-bbe6-7376ceaa556d` | CLI bootstrap→PTY Desktop→GUI continuation→CLI handback, same ID and `CLAUDE_CONTINUITY_7`; turn-boundary pause/resume |
| Cursor `ebcbf96d-fcb7-4f13-ade9-e84ad47e6668` | create-chat/assignment/explicit-ID follow-up/pause/resume; same JSON ID and `CURSOR_CONTINUITY_9`; CLI-only |

Versions: Claude CLI 2.1.288, GUI transcript 2.1.295; Cursor Agent
`2026.10.01-14929f9`. No model overrides. Claude GUI URL retained
`claude.ai/epitaxy/local_<session_id>`, bootstrap and `GUI_CONTINUATION_OK`,
`entrypoint: claude-desktop`; CLI recalled GUI context as `CLI_HANDBACK_OK`.
Desktop reopening then failed “Session <id> is open in another terminal. Run
/desktop there instead.” Existing GUI stayed open: repeated surface/lock transfer
is not fully verified; use supported ownership release, never lock bypass.

Cursor help confirmed create-chat has no name argument and explicit resume selects
persisted ID; manifest stores readable name. Interactive rename was untested.
Initial trust refusal was resolved with `--trust` for the inspected empty directory
and read-only `--mode ask`, no broad bypass. Outputs stayed outside repository.

Untested: active-tool interruption, crash recovery, Desktop messaging APIs, direct
owner push reports, managed-worktree setup, streaming, cloud ChatGPT and full
multi-plan implement/review/restack/release. Coordinator retrieval of Codex finals
and Claude/Cursor saved results was tested. Revalidate installed help after updates;
Cursor GUI visibility/Claude Desktop availability are not established universally.
Official references: [Claude Desktop](https://code.claude.com/docs/en/desktop#coming-from-the-cli),
[Cursor parameters](https://prod.cursor.com/docs/cli/reference/parameters).

Historical repository checks passed: bundle sync/diff checks, isolated tracked-skill
validation, schedule (11), evidence reuse (29), normalization (18) and both launcher
smoke suites. Full checkout then hit pre-existing untracked safe-dev-disk-cleanup
metadata; generic skill-creator validator rejects repository-supported
`disable-model-invocation`. These results are not a current full-build certification.

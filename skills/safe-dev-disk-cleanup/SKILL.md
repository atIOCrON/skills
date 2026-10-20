---
name: safe-dev-disk-cleanup
description: Audit and reclaim space from local development folders, Git worktrees, and Docker artifacts while preserving active dependencies and unique work.
disable-model-invocation: true
metadata:
  layer: capability
---

# Safe Development Disk Cleanup

Use this skill for local development disk audits and cleanups. An analysis request authorizes inspection; remove files only when the user has requested cleanup. Honor earlier authorization and any explicit decision to discard obsolete test data or skip backups.

1. **Inventory.** Measure allocated folder sizes and free space. Find Git worktrees across relevant repositories, including nested checkouts. Check active task records, processes, open files, and Docker volume and bind-mount references from both running and stopped containers. Age and folder names alone do not establish that content is disposable.
2. **Classify.** Separate active work, reproducible dependencies/build output, unique source or evidence, and obsolete data. Inspect staged, unstaged, untracked, and ignored files. Check where each worktree's Git database lives and whether its commits survive removal. A commit need not be merged if a durable reference in a surviving repository retains it.
3. **Preserve narrowly.** Compare candidate evidence with surviving copies by content hash. Put unique evidence beside an existing slice plan; otherwise use an indexed central archive. Save local changes and pin unique commits before deleting their checkout or Git database. Record original paths and hashes. Avoid replacing large disposable directories with full backups of generated files or databases the user chose to discard.
4. **Remove in dependency order.** Recheck Git state and current use immediately before deletion. Never remove a Docker volume referenced by a container. Remove child worktrees before a parent that holds their shared Git metadata. Use `git worktree remove` for registered worktrees, and prune only verified stale registrations. Keep a resumable removal record.
5. **Verify.** Check retained file hashes and Git references, confirm protected folders remain, and measure free space again. Report deletions, retained material and its location, unresolved items, and measured space change. Do not add parent and child sizes or equate allocated blocks with physical recovery on copy-on-write filesystems.

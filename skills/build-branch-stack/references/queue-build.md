# Build Selection and Stack Ownership

Coordinator's original-workspace manifest/plans are authoritative, not worktree
copies. Owners receive coordinator identity/return route/absolute manifest. Use
runtime/dispatch for persistent owners and scheduling for capacity/isolation.

## Selection and order

Accept optional specs, slices, branches or a repair/resume manifest. Impose no
branch cap. Require slice/parent/map approval and eligible parent stages under
`orchestration-plans-layout.md`; reject draft, stale, superseded, `in_release`,
merged or fulfilled build inputs. Repair inputs include the release record,
affected branches and publisher evidence that affected ready CRs are draft.

Explicit specs resolve approved maps; named slices exclude siblings. Honor scope/
order/base/layout/pauses/exclusions/resume, adding only demonstrated prerequisites
within authority. Without scope, discover and drain the queue without asking for
selection; inspect unfinished manifests/sessions/refs/handoffs and resume the uniquely
applicable build including owned in_progress work. Never duplicate branches/take over
live coordinator/infer tail by names/dates. Investigate ambiguous ownership/selection;
ask only unresolved choice.

Discover approved specs/to_do, approved maps and to_do children plus resumed work.
Group explicitly classified standalone legacy slices by slug; report unmapped work.
Stale/missing maps/unapproved children/inconsistent selection block affected work;
continue others. Human to_do selection needs no agent plan-review artifacts/reapproval.
Record scope before dispatch; at checkpoints append newly selected approved to_do
specs, preserving started blocks/frozen candidates. Draft/backlog adds no scope.
Finish when no eligible selected work/active owner remains, reporting blockers/
external work without endless polling; empty queue without resume is success/no-op.

Order specs by cross-spec prerequisites, explicit priority, estimated time/complexity/
risk; favor quick/unlocking work, slug tie-break with rationale. Within spec respect
prerequisites then quick work. Accept contiguous spec blocks, prioritizing current
fixes/placement while dispatching later specs. Advance after selected block accepted/
verified/pushed, not ancestor reviews/external acceptance. Reorder only wholly
unaccepted deferred blocks with reasons; partial acceptance preserves prefix/later
prepared results, block split requires user override. Resolve cycles via landed
prerequisites/existing authority or block, never fabricate dependency/violate order.

## Authoring and acceptance

Starting branch is base unless an existing parent is specified. Create plan branches
by default; follow `git-branch-commit.md` for base resolution, creation and adoption
checks. Check/refetch parent pins before each plan/final handoff.

Default new layout linear; explicit dependency/base-targeted overrides, resumes
retain authorized layout. First acceptance uses pinned start, then tail. If start
is not eventual integration base, record actual anchor as base, eventual base in
scope and inherited unmerged work for release. Parent/target/stacking_reason record
placement; code_prerequisites/dependency_reason real code needs or none. Prove
prerequisite inclusion/verification in cumulative authoring base, not review qualification.

Reserve work names/order without empty branches/placeholder SHAs. Independent owners
may share verified authoring base; separate prepared result from final placement,
update checks/pin after fixes. Import owner receipts/packs/ledgers/completion promptly
under operational-records; preserve original worker_completion pin/outcome/dependencies.
Prepared completion may be provisional or capped, never accepted tail/review stage.

After owner completion/lease return, coordinator backs up/transfers only owned range
onto tail under git-branch-commit, resolves/compares/verifies/lease-pushes. Finish/
isolate passes before source/pack rewrite. Apply code-review-loop/trim-review mappings,
return invalidated work to same owner and transfer receipts/counts without resets.
Convert provisional completion to clean only on valid accepted-tip qualification,
otherwise running/null phase SHA; never provisional status in branches. Record
verified pushed placement, then advance schedule.extensions.tail.
Failed review moves return affected slices to `in_progress`.

## Shared mutations and releases

Coordinator alone writes/moves/accepts/restacks/publishes except explicit leases/
handoffs naming scope/expected pins/owner/return. Session provenance grants no lease.
For unexplained ref movement, staged/unstaged overlap, failed leases or missing
artefacts, follow the integrity rules in `from-reviewed-plan-to-git-handoff.md`.
Use `orchestration-plans-layout.md` for build-authorized prerequisite/split drafts
and approval; update map, graph and manifest.
Owners retain isolated authoring/fixes/reviews. Assign review ownership to avoid
duplicate passes; other agents' pinned reviews/release snapshots use separate outputs,
coordinator imports evidence/CR state. Default selected release is qualified ancestry-
closed prefix pinned in plans/releases/active/<id>/preparation.json with build links;
release owns candidate checks/acceptance, never unfinished queue freeze.

Before ready publication/assembly/merge hand off stable source pins, holding only
affected rewrites. Draft affected ready CRs/invalidate stale candidates before upstream
fixes/restacks. After final-base merge reconcile landed work/remaining descendants;
retain sources/evidence until then. Queue grants no extra merge/deploy/notification/
publication authority.

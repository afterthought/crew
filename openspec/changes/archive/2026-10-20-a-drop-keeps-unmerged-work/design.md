# Design

## Context

Every place crew removes goes through one function, the tidy (`plan.py` `tidy`), which `crew unit drop`, `crew chore drop` and `crew bolt drop` reach on the team's host through `tidy_after`, `crew unit free` and `crew chore free` call directly, and every read of the team (`reap`) runs. Once the kit's `wt remove` has removed a place and left its branch to crew, the tidy deletes a unit's or a chore's branch outright with `git branch -D`. Only a dropped fix's branch is judged first (record 0028): `fix_branch_gone` runs `git cherry <bolt> <branch>`, and `fix_branch_kept` keeps the branch when a `+` line shows a commit whose patch the bolt lacks, or when git cannot compare the two.

A later unit of the same name already lands on an existing branch: `PLACE` makes the worktree on `unit/<unit>` when the branch is there. But the branch keeps the upstream it had, the old bolt's, and the stages read a unit's bolt from that upstream (`gather.upstreams`, `tidy_over`), so a re-added unit would read as belonging to a bolt it is not in.

Record 0003 is the decision; the `plan.10` rule (`docs/architecture/plan.md`) is the rule this builds, and its details already say how a unit's branch is to be judged: "by git cherry against its bolt, and against origin's main when the bolt is gone, kept and named when git cannot compare". The areas touched are `plan.md`'s (`plan.py`) and `briefs.md`'s (the planner's role). The rules relied on: `plan.9` (only crew's own worktrees, through the kit's tool), `plan.10` (judged by `git cherry`), `read.1` (what crew cannot read keeps the branch), `code.7` (the judgment is a function of facts), `code.6` (no `git reset`, nothing staged by hand), `tests.4` (each case in the lowest tier that holds it), `docs.2` (README, skill and usage move together), `docs.7` (the rule pages are the design agent's).

## Goals / Non-Goals

**Goals:**

- No branch of a unit or chore that holds a commit whose patch neither its bolt nor (with the bolt gone) the kit's main has is deleted by crew, whichever command removed its place.
- Whoever dropped or freed the work reads, in the command's own output, which branch was kept and why; the run record holds it too.
- A unit or chore added again under a kept branch's name builds on that branch and reads as the new bolt's.

**Non-Goals:**

- A fix's judgment stays as record 0028 built it: against its bolt, kept when it tracks none. A fix's merged-ness, `gather.fix_merged`, which still judges by ancestry, is not changed here.
- `crew bolt drop --requeue` still refuses while a unit has a worktree; record 0003 says a requeued unit should lose its worktree and keep its branch, which is other work.
- `crew bolts` and the board do not list kept branches (record 0003: they are visible in git), so the agents' views and `status.js` do not change (`code.8`: nothing the views draw moves).
- `plan.10`'s details and `_open.md` are amended by the design agent after the landing (`docs.7`).

## Decisions

### One judgment for every branch a tidy removes

The tidy's last step, once `wt remove` has left the branch, becomes one act for unit, chore and fix branches: `branch_gone`, which `fix_branch_gone` becomes. It reads what to compare the branch with, runs `git cherry <target> <branch>` in the kit's main checkout, and hands the result to a pure decision, `branch_kept`, which `fix_branch_kept` becomes. A branch with no `+` line goes; one with any, or one git cannot compare, is kept.

What to compare with is a decision of its own, `branch_target`, from plain facts: the branch's kind, the upstream it tracks, whether that upstream branch still exists, and the ref crew reads the kit's main at now (`gather.now_ref`, origin's main for a kit with an origin, `plan.18`). For a unit or chore it is the bolt while `bolt/<bolt>` exists, else main now; for a fix it is its bolt, or nothing, which keeps the branch, as today.

Why the bolt first, and main only once it is gone: a branch is cut from its bolt, and the bolt holds everything main held when it was given, so the bolt answers "did this work arrive" for every unit still in flight. When the bolt has landed or been dropped its branch is gone, and main is the only place the work could have arrived (`plan.10` details). Comparing with both at once was considered; it adds a second `git cherry` for the rare commit that reached main by another bolt, and errs on the keeping side when skipped.

Why patches and not ancestry: sluice lands a unit by rebasing it onto the bolt, so the commits on the bolt carry new hashes. `git cherry` compares each commit's patch id, which survives the rebase. It skips merge commits, so a dependent's branch that took another unit's head by a merge counts only its own commits. A commit whose patch changed on the way, in a conflict resolved during the rebase, reads as unmerged and its branch is kept: the safe side, as record 0003 says. Read 2026-10-20 with git 2.54.0 in a scratch repository: a branch whose commit was cherry-picked onto the bolt prints no `+` line; a merge commit on the branch is not listed; with the upstream deleted, `git cherry bolt/b unit/d` exits 128 with "fatal: unknown commit bolt/b", and `for-each-ref`'s `%(upstream:short)` still names the gone branch, so whether the bolt exists must be read with `rev-parse --verify`, not from the upstream.

This one judgment also covers units and chores whose work ended by a merge or a landing, not only by a drop. Record 0003 extends the rule to landing, and `plan.10` rules out `git branch -D` on any branch with unmerged patches. A merged unit's branch holds nothing whose patch the bolt lacks, so it still goes.

### What the command says

A kept branch is named on one line, the same shape a dropped fix's has today:

`<place> is removed, and unit/<u> is kept at <sha>: <why its work is over>, and it holds <n> commit(s) whose patch <target> lacks (git cherry), the user's to keep or delete; a unit added as <u> starts from it`

A chore's line ends "a chore added as <c> starts from it"; a fix's keeps today's words. A branch git cannot compare says git's own error in place of the count. A branch that goes keeps today's line, "<place> and <branch> are removed; the branch was at <sha>". The drop's output carries this line because the drop prints what the tidy on the team's host said (`tidied`).

### One run-record entry per kept branch

The drop's own entry (`unit.drop`, `bolt.drop`) is written with the plan's commit, on the host that wrote the plan, before the tidy runs on the team's host, so it cannot know what the tidy kept. The tidy therefore writes its own entry, act `branch.kept`, on the team's host under the team's label: `On` the branch as its object (`unit/<u>`, `chore/<c>`, `fix/<bolt>/<name>`, each already a run-record kind, which is the branch's own name) and `team/<team>`; `From` the bolt's object when the bolt was the target; `Head` the commit it is at; `Count` the commits whose patch the target lacks; `Why` why its work is over. `crew trace unit/<u>` then shows the drop and the branch kept. The entry is written once: a kept branch has no worktree, so no later read reaches it. Recording only kept branches, not every removed one, is enough for "the run-record entry names the branch": a removed branch is gone with the work it did not hold.

### A kept branch is taken by the next unit of its name

`PLACE`, when it finds the branch and no place, makes the worktree on the branch and, for a place that tracks (units, chores and fixes all do), sets the branch's upstream to the base it was given, the unit's bolt, and prints `KEPT=<sha>`. `make_place` returns that commit with what it returns today, and the construct's start (a chore's code start) prints "<place> starts from the kept <branch>, at <sha>". The branch is not rebased onto the new bolt: the construct agent finds the old change in its worktree and revises it, as its brief says, and the merge's submission takes it onto the bolt.

No mark is set on a kept unit or chore branch. A branch of that name can only be one crew kept or one the user made, and taking it is what record 0003 decided for the name; `read.4` rules out adopting an existing place or a running pane, not a unit's own branch, and a fix's place still refuses an existing branch (`teams.3`).

## Risks / Trade-offs

- [A merged unit whose rebase resolved a conflict keeps its branch] → It is named on the read that removes its place and recorded; the user deletes it with `git branch -D`. Record 0003 accepts this side.
- [Kept branches accumulate unseen] → Each is named once in the command that kept it and in the run record; `git branch --list 'unit/*'` lists them. Listing them in `crew bolts` is not asked for.
- [A re-added unit starts on a branch cut from an old bolt or main] → The stages read the branch's own commits from its merge-base, and the merge's submission to sluice is checked on the bolt with the unit merged, so a stale base fails the gate, never the bolt.
- [A journey test whose dropped unit's branch holds a stub construct's commit changes its expected line] → The task that changes the tidy updates those expectations.

## After deploy

Nothing: crew is live on each host once the bolt lands, and every behaviour here is proved by the logic, contract and end-to-end tiers.

## Task notes

**1.1** `branch_target(kind, up, up_exists, main_ref)` returns the ref to compare with, or None for a fix tracking no bolt. `branch_kept(target, cherry)` is `fix_branch_kept` generalised: it returns None when the branch goes, else why it is kept, and the count of `+` lines for the record. Keep its words for a fix as they are; `tests/py/test_fix.py`'s cases for `fix_branch_kept` move to the new name. Cases in `tests/py/test_tidy.py`: unit with its bolt present compares with the bolt; unit with the bolt gone compares with main now; chore alike; fix with no upstream gets None; `+` lines counted, `-` lines and an empty output go, a non-zero exit keeps with git's words.

**1.2** In `tidy`, the `git branch -D` after a removed unit's or chore's place becomes `branch_gone(main, branch, kind, up, now, path, over)`; the existing `branch in dropped` path for fixes calls the same, as does the loop over dropped fixes with no worktree. `branch_gone` writes `record.emit(t["label"], "branch.kept", ...)` only when it keeps. Mention `branch.kept` where `record.py`'s docstring names what an entry may carry, if anywhere; no new field is needed (`Head`, `Count` are allowed).

**1.3** Contract cases in `tests/contract/test_git.py` pin what crew assumes of git: a branch whose commit was cherry-picked or rebased onto the bolt gives no `+` line; a merge commit on the branch is not listed; a deleted upstream makes `git cherry` exit non-zero and `rev-parse --verify -q refs/heads/<up>` fail while `%(upstream:short)` still names it.

**2.1** `PLACE` gains, in its existing-branch arm, `[ "$track" = track ] && git branch -q --set-upstream-to="$base" "$branch"` and `echo "KEPT=$(git rev-parse --short "$branch")"`; `kit.place_said` ignores keys it does not read, so check it still parses. Only the arm that makes a new worktree on an existing branch prints `KEPT`; a place already there prints nothing new.

**3.1** In `tests/t-journey-fix.sh` (or the journey whose world fits best), a dropped unit whose branch holds a commit of its own is kept and named in the drop's output, a `branch.kept` entry names it in the run record (`record_of`), and a unit added again under its name starts from it, its place on the kept commit and its branch tracking the new bolt. Existing expectations of "<place> and unit/<u> are removed" for units whose branch holds a stub commit change to the kept line. Run `tests/moon-tasks` if a test's reads change.

**4.1** README, section on worktrees going: replace "when a removed branch held commits of its own, crew says the commit it was at" with the kept branch, named and recorded, and the next unit of its name starting from it. The planner's role: "A drop removes the worktrees and branches of what it drops" gains "keeping, named, each branch that holds work the bolt lacks, for a unit added again under its name to start from".

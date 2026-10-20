# Design

## Context

A landing is two commands: `crew bolt submit`, whose `LANDING` script submits the bolt's branch to main through sluice from `<kit>/places/land-<bolt>` on the team's host, and `crew bolt land`, which takes the bolt and its work out of the plan and asks the team's host for a tidy (`tidy_after`, `crew _tidy --landed <bolt>`). The tidy (`plan.py` `tidy`) removes every place whose work is over; once `a-drop-keeps-unmerged-work` lands, each unit's, chore's and fix's branch goes only through one judgment, `branch_gone` over the pure `branch_target` and `branch_kept`, comparing the branch with its bolt while `bolt/<bolt>` exists and with the kit's main now (`gather.now_ref`) once it does not. The bolt's own branch, marked `branch.bolt/<bolt>.crew given` when crew made it, is deleted outright by the tidy's last loop once no plan has the bolt (`bolt_branch_over`), whatever it holds.

So at a landing, while the tidy's worktree loop runs, every unit and fix of the bolt is still compared with the bolt, whose branch stands until that last loop. Work that reached the bolt but not main, such as a submission to the bolt sluice landed after the landing's was formed, reads as merged; its branch goes, and then the bolt's branch goes with the only copy.

Sluice lands a submission as a merge commit whose second parent is the submitted head (sluice ADR 0006, read 2026-10-20 on sluice main 3d354b9; crew's main e5ea06e1 has `d42078c8` as its second parent), so the bolt's commits stay reachable from main. The intent's reason for `git cherry`, that a landing rebases the bolt, holds for landings made before sluice (the signal's `a21c849`, "pre-rebase commits") but not for sluice's. `git cherry` is right either way: it lists no commit reachable from main, and it finds a commit whose patch main holds under another hash, as crew's own rebase of a dependent's place and pre-sluice landings leave. Read 2026-10-20 with git 2.54.0 in a scratch repository: after a `--no-ff` merge of a unit into a bolt and of the bolt into main, `git cherry main bolt/b` and `git cherry main unit/u` print nothing; a commit added to `bolt/b` after that prints one `+` line.

Record 0003 is the decision, in its paragraph on landing; signal `2026-10-07-swancloud-planner-a46c6cb9/01` is the finding. The rules relied on: `plan.9` (only crew's own worktrees and marked bolt branches, through the kit's tool), `plan.10` (a branch with patches its bolt or main lacks is kept and named, judged by `git cherry`), `plan.16` (a landing's procedure), `plan.18` (main now is `origin/main`, which `crew bolt land` fetches on the team's host before its tidy), `read.1` (what crew can't compare is kept), `read.4` (a bolt branch crew did not mark is left alone), `code.7` (each judgment a function of facts), `tests.4` and `tests.12` (each case in the lowest tier). The areas touched are `plan.md`'s (`plan.py`) and `briefs.md`'s (`main-ops.md`).

## Goals / Non-Goals

**Goals:**

- After a landing, nothing of the bolt's work that main holds is left in the kit, and nothing main lacks is deleted, whichever read of the team does the sweep.
- Whoever lands the bolt reads, in `crew bolt land`'s own output, each branch kept and why.

**Non-Goals:**

- The landing's own worktree, `<kit>/places/land-<bolt>`, which `LANDING` removes and names when git cannot: `plan.9` does not list it among the tidy's, and adding it is the design agent's.
- A fix still held by a slot when its bolt lands: freeing that slot is `a-fix-of-a-landed-bolt-is-swept-with-it`; once it is freed, this change's judgment applies to the fix's branch.
- A dropped bolt's branch, which goes as today: record 0003 judges dropped work against the bolt, and the user's drop is the word for the bolt itself.
- The bolt's branch on GitHub, which sluice's `branch delete` ends once `no-worktree-holds-main-or-a-bolt-branch` part 1 is built (`plan.19`); this change judges the host's local branch, which `plan.9` keeps crew's.
- The views and `status.js` do not change: kept branches are not drawn (record 0003), so `code.8` has nothing to move.

## Decisions

### The landing marks the bolt's branch landed

`LANDING`, once sluice says the submission landed and main moved (`RC=0`, `NEW` not `OLD`), sets `branch.bolt/<bolt>.crew landed` when the branch carries crew's mark already, and prints `MARKED=yes` or why not. A branch with no mark is not crew's (`read.4`) and stays unmarked. Git drops the mark with the branch.

Why a mark, not the `--landed` the tidy is already handed: the tidy that `crew bolt land` asks for is not the only read that sweeps. When the team's host does not answer, the next read does it (`tidied`), and a place kept at the landing for uncommitted changes goes on a later read; each must know the bolt landed. The mark is written on the host whose kit holds the branch, by the script that saw sluice land it, and the tidy already reads crew's marks with one `git config --get-regexp`. Considered: whether the bolt's head is an ancestor of main, which is commit identity and is what the intent rules out; the run record's `bolt.submit` entry, which no tidy reads and `read.5` keeps off the hosts; the `--landed` flag alone, which the next read does not get.

### What a landed bolt's work is compared with

`branch_target` takes one fact more, whether the branch's bolt is marked landed. Its rule becomes: a unit's, chore's or fix's branch is compared with main now when its bolt is marked landed or its bolt's branch is gone; with its bolt while the bolt stands unlanded; and a fix tracking no bolt gets nothing, which keeps it, as record 0028 has it.

Comparing with main, not the bolt, once the bolt has landed: the bolt is the place work arrived on its way to main, and once it has landed, main is where the work must be for its branch to be redundant. A branch holding nothing main lacks holds nothing the bolt lacks either, since the bolt landed whole, so nothing that went before goes less now; what changes is the case where the bolt holds what main lacks.

A fix whose bolt's branch is gone was compared with that gone branch, which git cannot do, so every such fix's branch was kept. It is compared with main as a unit's is, since `plan.10` names main as the target once the bolt is gone and record 0003's landing paragraph names fixes beside units.

### The bolt's own branch

The tidy's last loop reads each marked bolt branch's mark value. For one marked `landed` whose bolt no plan has and no worktree holds, it runs `git cherry <main now> bolt/<bolt>` and hands the result to `branch_kept`, the same decision as every other branch, with main as its target: no `+` line, the branch goes, saying `bolt/<b> is removed: bolt <b> has landed, and <main> holds every commit of it (git cherry); it was at <sha>`; any `+` line or a comparison git refuses, the branch is kept, its mark unset so no later read deletes it, named `bolt/<b> is kept at <sha>: bolt <b> has landed, and it holds <n> commit(s) whose patch <main> lacks (git cherry), the user's to keep or delete`, and recorded. A branch marked `given`, a dropped bolt's or one landed by a crew older than this, goes as `bolt_branch_over` has it today.

A legacy bolt worktree under `<kit>/bolts/` whose bolt is over and which the tidy removes leaves its branch to this same judgment, not to the plain `git branch -D` after a removed place.

The bolt's branch is judged after the worktree loop, as today, so every place is judged while the mark is there to read; the marks are read once, before the loop.

### What is recorded

Each branch kept writes the `branch.kept` entry `a-drop-keeps-unmerged-work` adds, on the team's host under the team's label: `On` the branch (`bolt/<b>`, `unit/<u>`, `chore/<c>`, `fix/<b>/<n>`) and `team/<team>`, `From` the landed bolt (`bolt/<b>`; the run record has no kind for a kit's main, so the target is in the `Why`), `Head`, `Count` and `Why`, composed from names (`record.3`): "bolt <b> has landed, and <main> lacks its patches".

### What `crew bolt land` says

It prints what the tidy on the team's host said, as it does today (`tidy_after`, `tidied`): each place and branch removed, each kept with why. When the host does not answer, it says the next read sweeps, and that read keeps what main lacks by the mark.

## Risks / Trade-offs

- [A bolt landed by a crew older than this carries the `given` mark] → Its branch goes as today, once; every landing after this lands carries the mark.
- [The host's `origin/main` lags at a later read] → `crew bolt land` fetches it on the team's host before its tidy; a later read on a stale `origin/main` can only keep more, never delete what main lacks.
- [A unit whose commit's patch changed in a conflict resolved on its way to main keeps its branch] → Named and recorded; the user deletes it. Record 0003 accepts this side.
- [The spec's "A bolt lands on main on the user's word" says the bolt's branch is then removed, unqualified] → The new requirement states when it is kept; that requirement is rewritten by `no-worktree-holds-main-or-a-bolt-branch`, so this change leaves its text to that one.

## After deploy

Nothing: crew is live on each host once the bolt lands, and every behaviour here is proved by the logic, contract and end-to-end tiers.

## Task notes

**1.1** In `LANDING`, after `new=…`, when `rc` is 0 and `new` differs from `old`: `git config --get "branch.bolt/$bolt.crew" >/dev/null && git config "branch.bolt/$bolt.crew" landed && marked=yes || marked=no`, and print `MARKED=%q` on the assignments line. `landing_said` reads it only to name a mark it could not set ("crew could not mark bolt/<b> landed: its branch carries no mark of crew's"); a landing is a landing either way. Contract: the existing landing case in `tests/contract/test_git.py` (`landing`) asserts the mark reads `landed` after a landing, stays `given` after a refused one, and is absent once the branch is deleted. Logic: `tests/py/test_landing.py`, `landing_said` with `MARKED=no`.

**1.2** `branch_target(kind, up, up_exists, up_landed, main_ref)`: cases in `tests/py/test_tidy.py` for a unit, a chore and a fix whose bolt stands marked landed (main), stands unlanded (the bolt), is gone (main, the fix's new case), and a fix with no upstream (None). The tidy reads `up_landed` from the mark values it reads once, before the worktree loop.

**1.3** The bolt's branch: a pure `bolt_branch_judged(bolt, bolts, worktree, mark, cherry)`, or `bolt_branch_over` grown to it, returning keep, go or leave with its words; `branch_kept` gives the count and why. Logic cases: landed and nothing beyond main goes; landed with a `+` line is kept; landed and git cannot compare is kept; given goes as today; a bolt still planned or held by a worktree is left. The act unsets the mark when it keeps, and emits `branch.kept`. A legacy `<kit>/bolts/<bolt>` worktree's branch, after its removal, goes through the same act.

**2.1** `tests/t-journey-land.sh`: after `crew bolt submit`, `git config branch.bolt/tenant-environments.crew` reads `landed`; after `crew bolt land`, the line `bolt/tenant-environments is removed: bolt tenant-environments has landed, and … holds every commit of it` replaces the "is in no plan" one. The dropped bolt's expectation, `bolt/console-pages is removed: bolt console-pages is in no plan`, stands. Run `tests/moon-tasks` only if a test's reads change.

**3.1** README, the sentence that begins "Every worktree crew made goes, with its branch, once its work is over": a bolt's branch goes once no plan has it and no worktree is on it, a landed bolt's only when main holds every commit of it, else kept and named; a landed bolt's units' and fixes' branches are compared with main. `main-ops.md` step 3, "The bolt's branch goes too": goes once main holds every commit of it, and a branch of the bolt's work holding a commit main lacks is kept and named, the user's. Update any phrase `tests/t-briefs.sh` pins there.

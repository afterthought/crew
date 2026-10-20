# Design

## Context

Why this change exists is in proposal.md. What crew does today:

- `gather.kit` lists a fix only from a worktree directly under `<kit>/places/` on a `fix/` branch: its branch, path, bolt (its upstream, when that begins `bolt/`), whether it has merged (`fix_merged`) and whether its conductor dropped it. A fix branch with no place is not listed at all.
- `fix_merged(main, branch, bolt)` is true when `refs/heads/bolt/<bolt>` holds the fix's tip and the fix has moved since its reflog's first entry. With the bolt's branch gone it is false.
- `slot_stage` reads a slot's fix as `merged`, `dropped` (its bolt is in no plan), `fix`, or `none` when the kit lists no fix by that name. `crew.reaped` frees a slot on `merged`, `landed`, `dropped` or `left`, so `none` keeps it for ever.
- `tidy_over` ends a fix's place once it has merged, was dropped, or its bolt is in no plan, and `tidy` then deletes its branch. A fix branch with no worktree goes only when it was dropped (`fixes_dropped`).

What the box held on 2026-10-20 (read over ssh on chuck-herdr-alpha, crew at e5ea06e, `/workspace/switchboard-kit/main`): the four fixes swb-3's slots held, `fix/mains-fleet-build-publishes-a-release/the-run-start-answers-its-grant` and `…/the-unit-tests-hold-without-git`, `fix/a-workload-under-a-path-is-known/a-fresh-head-for-the-fleet` and `…/carry-main-after-swb-2`, each have two reflog entries (made, then one commit), `origin/main` holds each tip, their upstreams read `[gone]`, no `branch.<fix>.crew` mark, and no place under `places/`. The kit holds about forty more `fix/` branches in the same state from earlier bolts. So every slot read `none`, and nothing removed the branches. Who removed the places is not known; the change does not depend on it.

git's behaviour relied on, read with git 2.54.0 in a scratch repository: a branch whose upstream branch was deleted keeps `branch.<b>.merge`, and `for-each-ref --format=%(upstream:short)` still prints the upstream's name (`bolt/b`), with `%(upstream:track)` printing `[gone]`. A branch tracking a remote-tracking branch prints `origin/bolt/<b>` there.

Pages of `docs/architecture/` whose areas this touches: `plan.md` (`plugin/lib/plan.py`, `plugin/lib/gather.py`), `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/`). Rules relied on: `teams.1` and `teams.3` (the rules this makes true), `plan.9` and `plan.10` (what the tidy removes, and that a branch holding anything its bolt or main lacks is kept), `plan.18` (main is read at `gather.now_ref`), `plan.19` (bolts on GitHub, places cut from `origin/bolt/<bolt>`), `read.1` (with the plan unread nothing is taken as dropped or landed by it), `read.4` (only crew's own `fix/` branches), `state.4`, `code.1` (`gather.py` stays standard library), `code.7` (the stage and the sweep are decisions on plain facts), `code.8` (no view changes), `tests.4`, `tests.10`, `tests.11`. Nothing here departs from a rule.

## Goals / Non-Goals

**Goals:**
- A slot holding a fix is freed once the fix has merged, landed with its bolt, or its bolt was dropped, whether or not its place stands.
- A fix's branch goes once its work is over, place or no place, and nothing a branch holds that its bolt and main lack is ever lost.
- A fix's bolt and its merge are read from whichever branch the fix tracks, so the move of bolts to GitHub (`no-worktree-holds-main-or-a-bolt-branch` part 1) needs nothing more for fixes.

**Non-Goals:**
- Units' and chores' places still read their bolt from an upstream beginning `bolt/`; their move to `origin/bolt/<bolt>` is part 1's.
- A fix branch with no place whose bolt is still planned and that has not merged is left alone and not named: `crew fix … --drop` ends it, as today.
- A slot holding a fix whose place and branch are both gone still reads `none`. crew has nothing left to read it from; `crew unit free` frees it.
- The landing guard (`fixes_in_flight`), the board's ledger and the sites page keep reading fixes from their places.
- Who removed swb-3's fixes' places.

## Decisions

### 1. A fix's facts come from its branch

`gather.py` gains one read of a fix branch's facts, used for a fix's place and for a fix branch with none:

- **bolt**: the bolt its upstream names, `bolt/<bolt>` or `origin/bolt/<bolt>`, with the ref it names (`refs/heads/bolt/<bolt>` or `refs/remotes/origin/bolt/<bolt>`); none when the upstream is neither.
- **merged**: that ref exists, holds the fix's tip, and the fix has moved since it was made (its reflog's first entry), as `fix_merged` reads today.
- **on_main**: the kit's main now (`gather.now_ref`, `plan.18`) holds the fix's tip.
- **moved**: the fix's tip differs from its reflog's first entry.

`fix_merged` reads the bolt at the ref the fix tracks when that names the bolt, and at `refs/heads/bolt/<bolt>` otherwise, so its other callers (the drop's refusal of a merged fix, the merge stage's end) read the same thing.

`gather.kit` keeps `fixes` as it is, each place's entry gaining `on_main` and `moved`, and adds `fix_branches`: for each `fix/` branch no worktree holds, its facts, keyed by branch. A separate key keeps the board, the sites page and the landing guard, which draw places, unchanged (`code.8`).

Alternatives considered:
- *Put place-less fixes in `fixes` with no path.* Every reader of `fixes` uses the path for a worktree or a site; each would need a guard, and the views would change for no gain.
- *Ask gather only for the fixes a slot holds.* The tidy needs every fix branch anyway, and the read is cheap (decision 4).

### 2. A fix's stage, one decision

`plan.py` gains a decision of plain facts, a fix's stage from its facts and whether its bolt is planned (`True`, `False`, or `None` when the plan could not be read):

1. `landed` when `on_main` and `moved`: main holds the fix's own work, as a unit reads landed once main holds its change, checked first as for a unit.
2. `merged` when `merged`.
3. When the bolt is in no plan: `landed` when `on_main` (a fix that never moved, its bolt landed), else `dropped`.
4. Otherwise `fix`.

With the plan unread, step 3 is skipped (`read.1`). `slot_stage` takes the fix from `fixes`, else from `fix_branches`, else reads `none` as today. A fix just cut from a bolt at a commit main holds reads `fix` while the bolt is planned, since it has not moved.

### 3. The tidy ends a landed fix and sweeps place-less branches

- `tidy_over` gives a fix's place, ahead of its other reasons, "`<fix>` has landed on main" when the stage decision reads `landed`; the place and branch then go as a merged fix's do. It reads the fix's bolt from either upstream form.
- After the worktrees, beside the dropped branches it sweeps today, `tidy` takes each `fix/` branch that no worktree and no slot of this host's teams in the checkout holds and that is not marked dropped, and removes it with `git branch -D` when the stage decision reads `merged` or `landed`: its tip is then held by its bolt or main, so nothing is lost (`plan.10`). It says `<branch> is removed: <why>; it was at <sha>`, or `<branch> is kept: <git's words>` when git refuses. Any other place-less fix branch is left as it is and not named. A function of the facts and the held set decides which go (`code.7`); the deletes stay thin around it.
- `crew.reaped` says a landed slot's work "has landed on main", which holds for a unit and a fix alike.

### 4. What the reads cost

The facts for place-less branches are read with as few processes as git allows: one `git for-each-ref --merged=<main now> refs/heads/fix/` gives `on_main` for every fix branch at once; a branch's reflog is read only when main or its bolt's ref holds its tip, and its bolt's `merge-base` only when that ref exists. A leftover whose bolt is gone and whose work main lacks costs nothing beyond the one listing. On the box the first read sweeps the forty-odd landed branches; after that few place-less fix branches remain.

## Risks / Trade-offs

- [A host's `origin/main` lags GitHub's, so a fix of a just-landed bolt reads `dropped` rather than `landed`] → the slot is freed either way. The landing runs on the team's host and its push moves that host's `origin/main`, and the bolt's local branch usually still stands there, so the fix reads `merged` first.
- [A never-moved fix of a dropped bolt cut at a commit main holds reads `landed`] → it holds nothing of its own; its slot is freed and its branch goes, as a dropped one's would. Only the words differ.
- [Sweeping branches crew did not remove before] → only `fix/` branches, crew's by `teams.3`, and only those whose tip main or their bolt holds (`plan.10`, `read.4`).
- [A fix's reflog expired] → `moved` reads false; the fix reads `landed` only once its bolt is in no plan, and its branch goes then.

## After deploy

None: crew has no deploy, and every scenario is proved by a check in this change.

## Task notes

### 1.1 A fix's facts

In `plugin/lib/gather.py`: the upstream parse (both forms), the facts read, `fix_merged` by the tracked ref, and `fix_branches` in `kit`'s answer, with the module's docstring naming it. Contract cases in `tests/contract/test_gather.py`, beside "a fix is listed with its bolt and reads merged only once it moved and the bolt holds it":
- a fix merged into its bolt, the bolt merged into main and its branch deleted, the fix's place removed: listed in `fix_branches` with `on_main` and `moved` true and `merged` false;
- the same with its place standing: its `fixes` entry carries `on_main` and `moved`;
- a fix tracking a remote-tracking `origin/bolt/<bolt>` against a bare remote: its bolt read, and merged once that ref holds its tip;
- a fix just cut at main's commit: `on_main` true, `moved` false.

### 1.2 A fix's stage

The decision of decision 2 in `plugin/lib/plan.py`, used by `slot_stage`. Logic cases in `tests/py/test_tidy.py`'s `slot_stage` class: extend the kit facts with `on_main`, `moved` and a `fix_branches` entry, and pin landed (moved and on main), landed (never moved, bolt in no plan, on main), merged, dropped, fix (just cut, bolt planned), place-less landed and merged read from `fix_branches`, none (neither), and with the plan unread nothing read `dropped` or landed by the plan.

### 2.1 The tidy

`tidy_over`'s landed reason and both upstream forms, and the place-less sweep's decision, in `plugin/lib/plan.py`. Logic cases in `tests/py/test_tidy.py`'s `TestOver` (a landed fix's place is over with "has landed on main"; one tracking `origin/bolt/t` is crew's and over once merged) and a new class for the sweep (a merged or landed branch goes; one a slot or worktree holds stays; one marked dropped is left to the dropped sweep; one holding work main and its bolt lack stays; one whose bolt is planned and not merged stays).

### 2.2 The slot's words

`crew.reaped`'s `landed` words in `plugin/lib/crew.py`; its case in `tests/py/test_slots.py`'s `TestReaped`.

### 3.1 The journey

In `tests/t-journey-land.sh` (or `t-journey-fix.sh` if the fixture there is simpler), a fix whose place is removed by hand with `git worktree remove` after its merge has landed on the bolt, its branch left as on the box: the team's next `crew status` shows its slot free and says the branch is removed. Add any file the case newly reads to its `# Reads:` line, run `tests/moon-tasks`, and commit `tests/moon.yml` if it changed (`tests.10`).

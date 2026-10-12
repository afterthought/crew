# Design

## Context

See proposal.md for why and record 0023, point 7, for the decision; this is how. What shapes it:

- **A bolt's worktree today.** `crew bolt give` makes `bolt/<bolt>` from main's fresh head and its worktree at `<kit>/bolts/<bolt>` on it (`make_place`). The conductor and ops start there (`crew.py` `bolt_place`), ops deploys and proves from it, and main-level ops lands from it with `wt merge main --no-squash --no-remove`, which rebases `bolt/<bolt>` onto main, runs the kit's pre-merge gate and fast-forwards main (`main-ops.md` step 3, `plan.8`). A carrying fix becomes the bolt's head by `git reset -q --keep <fix head>` in that worktree (`carry_move`), after which crew runs `wt hook post-merge --target=bolt/<bolt>` there (`carry`). The tidy knows the worktree as crew's by `<kit>/bolts/<folder>` on `bolt/<folder>` (`tidy_over`).
- **sluice's protection** (sluice's `phase-1-integrations.md` section 2): a reference-transaction hook refuses, with exit 128, every update of a protected branch but sluice's own gix moves: `git merge` (fast-forward too), `git commit`, `git reset --hard <other>`, `git rebase`, `git update-ref`, `git branch -f`, `git fetch . a:bolt/x`, `wt merge bolt/x`; it allows a branch's creation and its deletion once no submission to it is queued, waiting, testing or landing. A move made while a worktree holds the branch leaves that worktree's index and files behind its HEAD.
- **worktrunk** (v0.80.0): `wt merge <target>` pushes to the local target whether or not a worktree holds it (probed: `bolt/x` moved with no worktree on it, and a worktree on a branch tracking it then read `behind 1`); post-merge hooks run "in the target branch's worktree (the primary worktree if the target has none)".
- **The kits' post-merge hooks** (read 2026-10-12): crew's `bolt-verify.sh {{ target }}` verifies the target's revision from an archived copy; swancloud's `flake-gate verify` checks "this worktree's branch at its head"; switchboard's `post-merge-verify` runs every suite in the target's worktree. Run in the kit's main checkout after a merge into a bolt, the last two check main.
- **sluice's landing commit** carries its verdict as trailers: `Sluice-Submission`, `Sluice-From`, `Sluice-Tested` and `Sluice-Result: <result> (<ran> run, <replayed> replayed)` (sluice record 0006).
- **The kit's declaration and adapters** (`a-kit-declares-its-toolchain-and-tests`): `.config/sluice.toml`'s `[tests]` and `kit.py`'s toolchain step, setup and sourcing. sluice's gates name each branch pattern's checks under `[branches."<pattern>"] required`, a tag as `#<tag>` or a target as `<project>:<task>`.

Rules relied on: `plan.8` (amended below), `plan.9` (amended below), `plan.10` (a branch with patches main lacks is kept), `plan.16` (one landing procedure), `teams.3` (a fix's branch and place), `teams.5` (amended below), `teams.9`, `read.1`, `read.4` (crew follows and removes only the checkout and branches it made), `code.6` (crew moves only branches it made; nothing discards), `code.7` (following, the bolt's line and the verification's targets are functions of facts), `roles.3` (crew follows the bolt, not a brief asking the conductor to), `state.3`, `tests.5` (amended below), `tests.6`, `tests.11`; and `code.8`, on main since 2026-10-12, which this change keeps without touching the agents' views, since they draw bolts and units and not their branches. Pages whose area this touches: `plan.md`, `teams.md`, `briefs.md`, `tests.md`, `docs.md`.

Departures: `plan.8` has the landing rebase the bolt's branch, `teams.5` and record 0015 have a carrying fix move it, and `tests.5` has the bolt's verification run by the kit's post-merge hook; each now names `land/<bolt>` or crew's verification instead, and each is amended as below.

## Goals / Non-Goals

**Goals:**
- No worktree has a bolt's branch checked out, so sluice can move and protect it and nothing of crew's goes stale or is refused.
- What lands, and what a carrying fix moves, is a branch crew made and sluice never protects.
- The worktree ops deploys from is at the bolt's head whenever ops proves it.
- Every kit's bolt is verified the same way, from its own declaration.

**Non-Goals:**
- Landing a bolt onto main through sluice (a merge commit, conflicts resolved by merging main into the bolt): for when main itself goes through sluice, a departure from `plan.8` and record 0015 the user has not asked for.
- The kits' own changes to their post-merge hooks and declarations, each in its repository.
- Bounding how many verifications run on a host at once across kits: crew's own suite's `tests.9` slots stay crew's; sluice's runner caps its own runs (sluice record 0012).

## Decisions

### Two branches per bolt

`crew bolt give` makes `bolt/<bolt>` from main's fresh head with `git branch`, then the checkout with `git worktree add --track -b land/<bolt> <kit>/bolts/<bolt> bolt/<bolt>`, and makes it ready through the kit's declaration. `bolt/<bolt>` is the bolt's line: units are made from it and merge into it, by `wt merge bolt/<bolt>` or `wt submit bolt/<bolt>` as now. `land/<bolt>` is crew's, and is what lands. The conductor and ops start in the checkout as now (`bolt_place`).

### The checkout follows its bolt

```python
def following(bolt, on, busy, level, behind, carried):
    """What crew does with the bolt's checkout when it reads the bolt (teams.17): None when it is level or the bolt was
    carried (land/<bolt> holds commits bolt/<bolt> lacks); "follow" when land/<bolt> is behind bolt/<bolt> and nothing
    is in progress; ("refuse", <why>) when the checkout is not on land/<bolt> or has an operation in progress."""
```

The facts are read on the team's host, in the checkout: its branch, an operation in progress (`IN_PROGRESS`), and whether `land/<bolt>` is `bolt/<bolt>`, an ancestor of it (behind) or holds commits it lacks (carried). For "follow", crew runs `git merge --ff-only bolt/<bolt>` in the checkout: it moves `land/<bolt>`, the index and the files together, keeps untracked files and a local edit the move does not touch, and refuses, changing nothing, when the move would overwrite a local edit. A refusal, the decision's or git's, is recorded as a refused `bolt.follow` and told to the conductor with its words; nothing else waits on it. A follow is recorded as `bolt.follow`, from the old head to the new.

crew reads the bolt, and follows, when the wait reads that a unit's or fix's merge stage has delivered (the bolt holds it), and in `crew prove` before it asks ops; a follow that is refused there refuses the proof, since ops would prove another head than the bolt's.

### What lands, and what a carry moves

main-ops's step 3 is the same command from the same checkout, `wt merge main --no-squash --no-remove`, now merging `land/<bolt>`: it rebases `land/<bolt>` onto main, runs the kit's pre-merge gate, and fast-forwards main. A conflict is aborted with `git rebase --abort` there, leaving `land/<bolt>` where it was; `bolt/<bolt>` is never touched by a landing. Step 1 gains a check: the bolt's row in `crew bolts` shows the checkout level with its bolt, or carried, and the proof was of that head.

`crew fix <team> <name> --merge` judges the carry against `land/<bolt>`'s head (as `a-carrying-fix-is-judged-by-its-commits` judges it against the bolt's), and `carry_move` moves `land/<bolt>` to the fix's head by `git reset -q --keep` in the checkout, under the same refusals (not on `land/<bolt>`, an operation in progress, uncommitted changes, a head moved since the judgment): crew moving a branch it made, which `code.6` allows. crew then verifies the new head (below) in place of running the kit's post-merge hooks, and the conductor asks ops for a new proof, as now.

Once `land/<bolt>` holds commits `bolt/<bolt>` lacks, the bolt's line is `land/<bolt>`:

```python
def line_of(bolt, carried):
    """The branch a bolt's units and fixes are made from and merge into (teams.5): land/<bolt> once a fix carried the
    bolt onto main, else bolt/<bolt>."""
```

A fix made after a carry is `fix/<bolt>/<name>` from `land/<bolt>`, tracking it, and merges with `wt merge land/<bolt> --no-squash --no-remove` even in a kit on sluice, since sluice protects only the branches its policy names; so does a unit placed in the carried bolt for its landing (`plan.5`).

### crew verifies the bolt's head through the kit's test adapter

After each follow and each carry, crew starts, in the background on the team's host, the verification of `land/<bolt>`'s new head:

- In a kit that merges through sluice, a head whose commit carries `Sluice-Result: pass` is recorded green, by sluice's landing, with no run.
- Otherwise, when the kit's declaration names a runner and `[branches."bolt/*"] required`, crew makes a place for that revision, `<kit>/places/verify-<bolt>--<rev7>`, detached at it, makes it ready through the declaration, runs the test adapter there (moon: the required tags resolved to tasks with `moon query tasks`, then `moon exec <targets> --on-failure continue`, each task's result read from `.moon/cache/runReport.json`; command: `sh -c <command>`, one check), records the outcome, and removes the place. Two follows in a row verify side by side, each in its own place; a revision whose run is still alive is not started again.
- A kit that declares no runner or no required checks for bolt branches gets no verification from crew, and `crew bolt verify` says so.

The record is per revision, under the kit's git common dir, `crew/verify/<bolt>/<rev>.rec`, one recutils record as `bolt-verify.sh` writes now: `State` (running, green or red), `Rev`, `By` (`crew` or `sluice`), `Started`, `Ended`, `Pid`, a `Failed` field per failing check, and `Log`. `crew bolt verify <bolt>` prints the record of `land/<bolt>`'s head, exiting 0 only when it is green: no record reads as not verified, a running record whose process is gone as interrupted, and a record crew cannot read is named, never green. `--again` runs it again for the same head, refused while its run is alive. These are `merge-gate`'s three requirements for crew's own bolt, now true of every kit's, in `kit-toolchain`.

The test adapter's run and read are sluice's: crew ports them into `kit.py` beside the setup, with `required_targets(required, tasks)` deciding the targets from the required list and `moon query tasks`' output, and `results(report, targets)` reading the report, both in the logic tier.

### The tidy

`tidy_over` knows a bolt's checkout as `<kit>/bolts/<folder>` on `land/<folder>`, and, until every bolt given before this change has landed, on `bolt/<folder>`; over once no plan has the bolt, as now. The checkout goes through the kit's `wt remove`, and `land/<bolt>` by `plan.10`'s judgment. `bolt/<bolt>`, which no worktree holds, is then judged by `plan.10` too and deleted when main holds its patches; a delete sluice's hook refuses, a submission to the bolt still queued, keeps the branch, named with the hook's words, and the next read tries again. A verification place, `places/verify-<bolt>--<rev7>`, is crew's once its run has ended or its process is gone.

### A bolt given before this change

A bolt whose checkout is on `bolt/<bolt>` keeps that shape until it lands: crew follows nothing for it, a carry moves `bolt/<bolt>` as now, and main-ops lands it as now. `following` reads it as not on `land/<bolt>` and says so once, not as a refusal. No checkout is converted in place, since `bolt/<bolt>` may already be protected by sluice.

### crew's own repository

`.config/wt.toml` loses `[post-merge]`, and its comment says crew verifies a bolt through its declaration; `.config/hooks/bolt-verify.sh` and `bolt-status.sh` go; `.config/sluice.toml` gains `[branches."bolt/*"]` with `required` naming the tag crew's test tasks carry. CLAUDE.md's *Proving and landing a bolt* says `crew bolt verify <bolt>` where it says `bolt-status.sh` and `bolt-verify.sh`. The merge gate is unchanged: it runs in the worktree being merged.

### The briefs

`conductor.md`: the bolt is built on `bolt/<bolt>`, which no worktree holds, and its checkout `{{KIT_DIR}}/bolts/<bolt>` is on `land/<bolt>`, which crew keeps at the bolt's head; the bolt's verification is `crew bolt verify <bolt>`. `ops.md`: ops deploys and proves from the checkout at the head crew last followed, names that head in the proof, and never checks out `bolt/<bolt>` or commits in the checkout. `main-ops.md` step 1 gains the checkout's check; step 3 says the merge lands `land/<bolt>` and the abort leaves `land/<bolt>` and main where they were; the carry "makes the fix the head of what lands". `t-briefs.sh` pins each with a phrase (`tests.6`).

## Rules this changes, on acceptance

Written by the design agent once the user accepts record 0023 (`docs.7`).

- `plan.8`: "…meets main only at its landing, which rebases its landing branch `land/<bolt>` onto main in the bolt's checkout through the kit's hooks…; when the landing's rebase conflicts nothing lands, the team's fix carries the bolt's commits onto main with the conflict resolved, crew makes that the head of `land/<bolt>`, and no agent moves a bolt's branch or its landing branch by hand."
- `plan.9`: "…directly under `<kit>/bolts/` on a `land/` branch, or under `<kit>/places/` on a `unit/` or `fix/` branch or detached for a verification…"; its details name the old shape kept until those bolts land, and `bolt/<bolt>` judged and removed with no worktree.
- `teams.5`: a fix that carries the bolt "becomes the head of `land/<bolt>` by crew's move"; and "once a fix has carried the bolt, its later units and fixes are made from and merge into `land/<bolt>`".
- A new `teams.17`: "No worktree holds a bolt's branch: the bolt's checkout is on `land/<bolt>`, which crew brings level with `bolt/<bolt>` by a fast-forward in the checkout whenever it reads the bolt moved and before a proof, and which only a landing's rebase or a carry otherwise moves."
- `tests.5`: "…the bolt's verification is crew's, through the kit's declaration, after each move of `land/<bolt>`, or a passing sluice landing of that head…".
- Record 0015's carry names `land/<bolt>` (amended by record 0023).

## Risks / Trade-offs

- [A kit's post-merge hook that checks its worktree's own branch, run in main after a merge into a bolt] → it checks main, harmless but wasted, until the kit makes it main's only; listed in the proposal's Impact as the kit's change before this reaches its host.
- [A kit with no declaration loses the bolt verification its post-merge hook gave it] → `crew bolt verify` says the kit declares no required checks; the kit writes its declaration, which `a-kit-declares-its-toolchain-and-tests` already asks of it.
- [A cold verification place per revision] → the toolchain step and setup run in each, about 20 s for a devenv toolchain before the checks; moon replays what any worktree of the kit already passed, through the shared outputs; sluice's piece 11 caches the toolchain, and crew's adapter takes that when it lands.
- [Kit tooling that names a worktree by its branch] → the bolt's checkout is named `land-<bolt>` where it was `bolt-<bolt>`; it is still on a branch.
- [A hand checkout of `bolt/<bolt>` elsewhere] → git no longer stops it, since no worktree holds the branch; sluice's hook stops any move of it, and the briefs say never to.
- [A follow refused by a local edit in ops's checkout] → recorded and told to the conductor; the proof refuses until ops's checkout is clean, so no proof names a head it did not deploy.

## Proof on real work

Once the bolt has landed and every host has pulled, on the next bolt given in a kit on sluice: the bolt's checkout is on `land/<bolt>`, `git status` there is clean after each landing sluice makes, and `crew bolt verify` reads green by sluice's landing; on the next in a kit that merges with `wt merge`: `crew bolt verify` reads the run of its head. The conductor says so; nothing is the user's.

## Task notes

### 1.1

`bolt give` as *Two branches per bolt* says; `make_place` takes the base and the tracking it needs. `tests/t-journey-units.sh`: after give, `bolt/<bolt>` is at main's head, the checkout is on `land/<bolt>` tracking it, and `git worktree list` shows no worktree on `bolt/<bolt>`.

### 1.2

`following` and its facts in `plan.py`, and `tests/py/test_follow.py`: level, behind, carried, not on `land/<bolt>`, an operation in progress, and a bolt of the old shape. The act after the merge stage's delivered and in `crew prove`. A contract case in `tests/contract/test_git.py`: a worktree on `land/x` tracking `bolt/x`, `bolt/x` moved by `git update-ref` (as sluice's gix moves it, no worktree touched); `git merge --ff-only bolt/x` there keeps an untracked file and an edit to an untouched file, and with an edit to a file the move changes, exits non-zero and changes nothing. `tests/t-journey-units.sh`: a unit's merge leaves the checkout level and records `bolt.follow`; a local edit the follow would overwrite is told to the conductor and refuses `crew prove`.

### 1.3

`wt merge bolt/<bolt>` into a branch no worktree holds: a case in `tests/contract/test_wt.py` pinning that it moves the branch and runs post-merge hooks in the primary worktree.

### 2.1

The landing and the carry as *What lands, and what a carry moves* says: `carry_judgment` reads `land/<bolt>`, `carry_move` moves it, `line_of` and its logic cases, `merge_how` and a unit's or fix's place from `line_of`. `tests/t-journey-fix.sh`: a carry moves `land/<bolt>` and leaves `bolt/<bolt>` where it was; a fix after the carry is made from and merges into `land/<bolt>`. `tests/t-journey-land.sh`: the landing lands `land/<bolt>`; a conflicting landing aborted leaves both branches where they were.

### 3.1

The test adapter's run and read in `kit.py`, with `required_targets` and `results` in `tests/py/test_kit.py` (a tag, a target, a tag matching nothing, a report with a passed, a failed, a replayed and a missing task), and the verification as *crew verifies the bolt's head* says, with `crew bolt verify <bolt> [--again]` in `plugin/bin/crew`, its usage header, README and the skill (`docs.2`). `tests/t-journey-units.sh`: a follow starts a verification that reads running then green, with a stand-in `moon` whose `exec` writes a run report; a red check is named with its log; a sluice-landed head with `Sluice-Result: pass` reads green by sluice with no run; a kit with no required checks reads as declaring none.

### 4.1

The tidy as *The tidy* says, with `tests/py/test_tidy.py` cases for `land/<folder>`, the old shape, a verification place, and `bolt/<bolt>` with no worktree kept for patches main lacks or for a refused delete.

### 5.1

crew's own repository and the briefs as *crew's own repository* and *The briefs* say; `tests/t-merge-gate.sh` loses its verification cases, which `tests/t-journey-units.sh`'s now hold for every kit; `tests/moon-tasks`; `tests/suite --affected` ends with "0 failed".

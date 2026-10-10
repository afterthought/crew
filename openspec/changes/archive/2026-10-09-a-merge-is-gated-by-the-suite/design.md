# Design

## Context

See proposal.md for why. What shapes the approach:

- Every merge in crew is run by an agent with worktrunk: the merge stage and a fix's merge run `wt merge bolt/<bolt> --no-squash --no-remove` from the unit's or fix's place (`plan.py` 2531, `plugin/bin/crew` 565, `coder.md` "Merging"), and main-level ops lands a bolt with `wt merge main --no-squash --no-remove` from the bolt's worktree (`main-ops.md` step 3). Both forbid `--no-hooks` and `--yes`. crew has no `.config/wt.toml`, so these merges run no check today.
- worktrunk's hooks (worktrunk's `hook.md` and `merge.md`, read for this change): `pre-merge` runs after the rebase and before the fast-forward, in the worktree being merged, and a failure aborts the merge with the target untouched. `post-merge` runs in the background once the merge has landed, in the target branch's worktree (`bolts/<bolt>` for a merge into a bolt, the main checkout for a landing), with output logged where `wt config state logs` finds it. `{{ target }}` names the target branch. The project's hooks are read from `.config/wt.toml` in the worktree the command runs in. Project hooks run only once the user has approved them (`wt config approvals add`); in a session that can't prompt, an unapproved hook fails the command, and approval is asked again whenever a hook's command changes.
- `tests/run` runs every `tests/t-*.sh` serially, about twenty minutes, prints `FAIL  <name>` for each failure and `<n> passed, <m> failed`, and exits non-zero on any failure (`tests.1`). It finds crew through its own path, so it runs the same from any copy of the tree. The live test `t-sites-live` skips itself unless `CREW_TEST_LIVE=1`.
- switchboard-kit has this shape already (`switchboard-kit/main/.config/wt.toml`, `.config/hooks/post-merge-verify.sh`, `main-outcome.sh`): a pre-merge gate, and a post-merge run of every suite that records its outcome under the git common dir, read with `main-status`. This design follows it, cut to what crew needs.
- Claude Code stops a foreground command at ten minutes. A twenty-minute gate run in the foreground is killed before it ends, and nothing lands.

Rules relied on: `tests.5` (this change builds its first half: the gate and the verification; the moon tasks are `the-suite-runs-as-moon-tasks`), `tests.1` (the gate runs the suite only through `tests/run`), `tests.2` (no live test in the gate), `tests.6` (each new brief sentence pinned in `t-briefs.sh`), `state.3` (a landing goes through the kit's merge hooks; this gives crew's hooks a body), `state.4` (the verification's record is plain files, and reading it writes nothing), `read.1` (a head with no record, or a record that can't be read, never reads green), `code.1` (no package added to devenv), `code.6`, `docs.5`. Areas touched: `tests.md` (`.config/**`, `tests/**`), `briefs.md` (`plugin/roles/`), `docs.md` (`CLAUDE.md`, `docs/architecture/_open.md`, `openspec/`).

Departure: record 0008 expects the briefs to "become true for crew without a word changed". Two sentences change, one in the coder's brief and one in main-level ops's, because a gate this long cannot finish in a foreground command (see the decision below). Nothing they say about the gates themselves changes.

## Goals / Non-Goals

**Goals:**
- A unit's, fix's or bolt's merge in crew lands only when the whole suite passes on the exact tree that lands.
- After every merge into a bolt, a verification of the bolt's new head that ops can read, check against the head, and run again.

**Non-Goals:**
- Speed: the suite runs serially at its present cost. Parallel moon tasks and replay of an identical tree are `the-suite-runs-as-moon-tasks`.
- A check that main is red, a clean-tree check, or a second try for a flaky test: switchboard-kit has them; record 0008 doesn't ask for them, and crew's suite runs no emulator.
- Changing what any test checks, or `tests/run`.
- Hooks for any other kit, or crew's own commands: `crew` still never runs a merge.

## Decisions

### The gate is one pre-merge hook running the whole suite

`.config/wt.toml` holds `[pre-merge] suite = "devenv shell -- env CREW_TEST_LIVE= tests/run"`. It runs for every target: a merge into a bolt, and a bolt's merge onto main. Emptying `CREW_TEST_LIVE` keeps the live test out even when the merging shell has it set. The output the agent sees is `tests/run`'s own, which names each failing test and its last lines.

Alternatives: a gate only on the tests the branch changed, as switchboard-kit's `test-changed`, is not possible honestly in crew: every command crosses `plan.py`, so every change to `plugin/` touches every test (the reading's "Found"). Narrowing is the moon unit's replay, not this gate's. A gate on bolt merges only, leaving main to the post-merge verification: record 0008 gates both.

### The verification runs after each merge into a bolt, on a frozen copy of the merged revision

`.config/wt.toml` holds `[post-merge] verify = "devenv shell -- sh .config/hooks/bolt-verify.sh {{ target }}"`. The script:

1. Takes the branch it is given, or the current one when run by hand. A branch not named `bolt/<bolt>` is not verified: it says so and exits 0. So a landing on main starts nothing in crew's live main checkout.
2. Reads the branch's revision once, `git rev-parse <branch>`.
3. Refuses when the record of that revision says it is running and its process is alive.
4. Detaches, as switchboard-kit's `post-merge-verify.sh` does (`nohup wt step tether -- sh "$0" …`), so a run worktrunk starts is not cut off when worktrunk's own process ends, and is ended when the bolt's worktree is removed at landing.
5. Exports that revision with `git archive <rev> | tar -x` into a scratch directory made by `mktemp -d` under the temp dir (named `crew-verify.XXXXXX`, checked and removed the way `tests/run` checks and removes its own), and runs `env CREW_TEST_LIVE= tests/run` from there, its output to the log.
6. Records the outcome, and removes the scratch copy.

Running on a copy is what makes the outcome true of its revision: merges into a bolt land one after another, each verification takes twenty minutes, and a run in the bolt's worktree would have the next merge change its files mid-run. With copies, two merges in a row give two runs side by side, each of its own revision; that costs machine time until the moon unit, and is correct.

Alternatives: run in the bolt's worktree with a lock, as switchboard-kit does on main: the lock orders runs, but a merge still rewrites the files under a run in progress. A detached `git worktree add`: registers a worktree crew didn't lay out, which `read.4` makes crew leave alone forever if a run dies. Supersede an older run when a newer one starts: loses the older revision's outcome, which tells a fix which merge broke the bolt.

### The record is a recutils record per revision, under the git common dir

Each run writes `<git common dir>/bolt-verify/<bolt>/<rev>.rec` and `<rev>.log`, where every worktree of crew on the host reads them. The record is one recutils record, readable with `cat` or `recsel`:

```
State: running | green | red
Rev: <full revision>
Subject: <the revision's subject>
Started: <UTC time>
Ended: <UTC time, once ended>
Pid: <the run's process>
Failed: <test name>        (one field per failing test, red only)
Log: <path of the log>
```

It is written to a temporary file and renamed into place, so a reader never sees half of one. When a run starts it removes the records and logs of its bolt's other revisions whose runs have ended, so the directory holds the newest outcome of each run in flight and no history. A record keyed by revision is what lets two runs side by side never overwrite each other, and lets the reader find the one for the head without trusting whichever finished last.

Alternatives: one `status.json` per bolt, as switchboard-kit: the last writer wins, and the older of two runs side by side could write over the newer. JSON: needs `jq` to read, where crew's state is already recutils (`state.4`).

### One reader prints the head's outcome, and writes nothing

`sh .config/hooks/bolt-status.sh [<bolt>]`, from a bolt's worktree (the bolt is the current branch's when not named), prints the record of `bolt/<bolt>`'s current revision, and exits 0 only when it reads `green`. A `running` record whose `Pid` no longer answers `kill -0` is printed as `interrupted`; the file is left as it is (`state.4`). No record for the head prints `not verified: <rev>` and, when there is one, the newest other revision's state for context, and exits non-zero. A record it cannot read is named, and exits non-zero (`read.1`). It uses only `sh`, `git`, `sed` and `grep`, so it runs with or without devenv, and over `ssh` from main-level ops.

ops reruns a verification with `devenv shell -- sh .config/hooks/bolt-verify.sh` from the bolt's worktree, which the ops brief already describes ("run the kit's merge verification yourself from the bolt's worktree"). CLAUDE.md names both commands, since the ops brief says a kit's CLAUDE.md does.

### A long merge is run in the background

The coder's brief gains, under "Merging": the merge's checks can take longer than a command is allowed to run, so run `wt merge` in the background and wait for it to end; never start it again while it runs, and never shorten it. main-level ops's step 3 gains the same. Both are true of every kit and are pinned in `t-briefs.sh` (`tests.6`). Without them a merge stage would be killed at ten minutes every time, and nothing would ever land in crew.

## Risks / Trade-offs

- [Every merge in crew takes about twenty minutes more, and two merges in a row run two suites at once] → Accepted by record 0008 ("a slow gate costs minutes and no gate costs a broken main"). The moon unit cuts it.
- [The first merge carrying `.config/wt.toml` stops on worktrunk's approval prompt] → The user approves crew's hooks once per host before it (Migration Plan). An agent never approves for the user and never adds `--yes`, as the briefs already say.
- [`wt step tether` is marked experimental by worktrunk] → It is what switchboard-kit's verification runs under today. If it is missing, `nohup` alone still detaches; the run then outlives a removed bolt worktree, which only wastes time, since it works on its own copy.
- [A test that reads crew's git history would fail from a `git archive` copy] → No test does today (they read `$CREW`'s files only, `tests/lib.sh` line 12). Task 4.1 runs the whole suite from such a copy once, so one that starts to will show.
- [Records of landed bolts stay under the git common dir] → One record and one log per bolt; a later run on a bolt of the same name clears them.
- [A host machine sleeping mid-run leaves a record reading `running` with a live process] → The run resumes when the machine wakes; the reader shows `running` until it ends.

## Migration Plan

1. Before this unit's merge stage, on the host that holds its bolt (mac-studio): the user runs `wt config approvals add` in crew and approves the two commands. The unit's own merge is the first one gated, since worktrunk reads a project's hooks from the worktree the command runs in, here the unit's place.
2. Merge as usual: the gate runs on this unit's tree, and the bolt's verification starts after.
3. Before any merge on the box after the bolt lands: the user runs `wt config approvals add` in `/workspace/crew/main` there.

Rollback: revert `.config/wt.toml`; merges then run no check again.

## Proof on real work

Once this unit has merged into its bolt (steps 1–4), and once the bolt has landed and every host has pulled (5–6):

1. This unit's merge into its bolt printed the suite's lines and `… passed, 0 failed` before the bolt moved.
2. From `bolts/<bolt>` on mac-studio, `sh .config/hooks/bolt-status.sh` printed `running` with the bolt's head, then `green` with the same revision. `wt config state logs` shows the post-merge hook's log naming `bolt-verify.sh`.
3. The next unit or fix merged into the bolt: the gate ran in its merge stage, run in the background by the stage's agent, and ops read the verification of the new head as its brief says, without asking the user to run anything.
4. A merge whose tree fails a test (a fix with a deliberately red commit, on the user's word, or the first real red) was refused, and the bolt did not move.
5. main-level ops's landing showed the gate's output, main moved only after `0 failed`, and no verification ran in crew's main checkout (no new record under `bolt-verify/` for main, no suite in `wt config state logs` from main).
6. On the box, after the user's approval there, a merge into a bolt of a team hosted there was gated and verified the same way.

## Task notes

**1.1** `.config/wt.toml`, new. Open with a comment in the style of switchboard-kit's: what each hook runs, where (the gate in the worktree being merged, after the rebase; the verification in the target's worktree, in the background), that a red gate refuses the merge with nothing landed, that the verification's outcome is read with `bolt-status.sh` and is the bolt's verification ops reads, that agents never run the hooks by hand nor bypass them with `--no-hooks` or `--yes`, and that the first run on a host needs the user's `wt config approvals add`. Then the two hooks exactly as Decisions give them; keep each command a single string so an approval matches it.

**1.2** `tests/t-merge-gate.sh`, new, with the guard line and an opening comment (`tests.2`), and `command -v wt … || fail` as `t-merge.sh` does. It builds a scratch repository under `$T`, not a crew kit: copy `$CREW/.config/` into it, add a stand-in `tests/run` that prints `ok    t-a` and `FAIL  t-b` lines and exits non-zero when the tree holds a file named `red`, and a stand-in `devenv` in a directory of the test's own put first on `PATH`, which drops `shell --` and runs the rest. Approve the hooks in the scratch HOME with `wt config approvals add --yes` (a test's own sandbox, never the user's; check that the approvals file landed under `$HOME`, and set `XDG_CONFIG_HOME` under `$T` if worktrunk reads it). Then, with `--no-squash --no-remove`: a `unit/x` merge into `bolt/b` with `red` is refused, the output names `t-b`, and `bolt/b` is unmoved; without it, it lands; a `fix/b/y` the same; a merge of the bolt into `main` with `red` is refused and main is unmoved; with `CREW_TEST_LIVE=1` exported the stand-in sees it empty.

**2.1** `.config/hooks/bolt-verify.sh`, new, POSIX `sh`, in the order Decisions give. The bolt name is the branch less `bolt/`; refuse a name outside `code.4`. The failing test names are the `FAIL  <name>` lines of `tests/run`'s output. Trap HUP, INT and TERM to remove the scratch copy and leave the record `running` (the reader turns a dead `running` into `interrupted`). `TMPDIR` names the temp dir as in `tests/run`.

**2.2** `.config/hooks/bolt-status.sh`, new, as Decisions give it. Exit codes: 0 green; 1 red, interrupted, running or not verified; 2 a record it can't read or a branch that isn't a bolt.

**2.3** In `tests/t-merge-gate.sh`: give the stand-in suite a way to be slow (it waits while a file named `hold` exists in `$T`), so a run can be caught mid-way. After a green merge into `bolt/b`, poll `bolt-status.sh` (with `/bin/sleep`, as `t-bolts.sh` does, and a bound) until `green` with the bolt's head; after a merge carrying a failing test, `red` with `Failed: t-b`; with `hold` in place, two merges in a row leave two `running` records for two revisions, and releasing it ends both, each with its own outcome; a merge onto `main` writes no record; a `running` record whose `Pid` is a finished process reads `interrupted`; a record replaced with garbage is named and exits 2; a hand rerun on a head whose run is alive is refused, and on an interrupted head starts a new run that ends green.

**3.1** `plugin/roles/coder.md`, "Merging", after the `wt merge` block; `plugin/roles/main-ops.md`, step 3. Plain words, one sentence each, as Decisions give it. Add each sentence's key phrase to `tests/t-briefs.sh`: the coder's beside the brief checks at lines 4, 88 or 110, main-level ops's in the `for want` at line 74.

**3.2** `CLAUDE.md`. Under "Tests": every `wt merge` in crew runs the whole suite as its gate, and an agent runs the merge in the background. Under "Proving and landing a bolt", "Before landing": the bolt's proof is its verification, green at the bolt's head, read with `sh .config/hooks/bolt-status.sh` from the bolt's worktree, and run again with `devenv shell -- sh .config/hooks/bolt-verify.sh` there when nothing has merged since; the landing's own gate runs the suite once more.

**3.3** `docs/architecture/_open.md`, "Accepted, not built": the `tests.5` line names only the moon tasks (`the-suite-runs-as-moon-tasks`) as not built, and drops the clause that crew has no `.config/wt.toml`. `tests.md` `tests.5`'s "Not built: `_open.md`" stays, since the moon half is still open.

**4.1** Run `devenv shell -- tests/run` in this worktree, then once more from a copy: `git archive HEAD | tar -x -C <scratch>` and `devenv shell -- <scratch>/tests/run`. Both must print `0 failed`. The second is what the verification will run.

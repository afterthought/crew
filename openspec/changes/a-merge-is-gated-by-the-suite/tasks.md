# Tasks

## 1. A red suite refuses a merge

- [x] 1.1 crew's `.config/wt.toml` runs the whole suite, inside devenv and without the live test, as a pre-merge gate on every `wt merge`, and says in its opening comment what each hook does and that agents never bypass it (design: Task notes 1.1).
- [x] 1.2 `tests/t-merge-gate.sh` shows, with the real `wt` in a scratch repository, that a red suite refuses a unit's, a fix's and a bolt's merge with the target unmoved and the failing test named, and that a green one lands (design: Task notes 1.2).

## 2. The bolt is verified after each merge

- [ ] 2.1 `.config/hooks/bolt-verify.sh` runs the whole suite on a frozen copy of a bolt's merged revision, detached, and records the outcome per revision under the git common dir, starting nothing for a branch that isn't a bolt and refusing a second live run of the same revision; `.config/wt.toml` runs it as the post-merge hook (design: Decisions "The verification runs after each merge", "The record"; Task notes 2.1).
- [ ] 2.2 `.config/hooks/bolt-status.sh` prints the verification of the bolt's current head, reads a dead run as interrupted and a missing or unreadable record as not green, writes nothing, and exits 0 only on green (design: Decisions "One reader"; Task notes 2.2).
- [ ] 2.3 `tests/t-merge-gate.sh` shows a merge's verification ending green and red at the bolt's head, two runs side by side each keeping its own revision's outcome, no run after a merge onto main, the interrupted, not-verified and unreadable readings, and a hand rerun refused while alive and started after a cut-off (design: Task notes 2.3).

## 3. The briefs and the docs

- [ ] 3.1 The coder's and main-level ops's briefs each say, in one sentence, that a merge's checks can outlast a command's time limit so the merge runs in the background and is waited for, and `tests/t-briefs.sh` pins both (design: Decisions "A long merge"; Task notes 3.1).
- [ ] 3.2 CLAUDE.md says every merge in crew is gated by the suite and that a bolt's proof is its verification, green at its head, read and rerun with the two commands (design: Task notes 3.2).
- [ ] 3.3 `docs/architecture/_open.md` lists only the moon tasks of `tests.5` as not built (design: Task notes 3.3).

## 4. The suite

- [ ] 4.1 `devenv shell -- tests/run` prints `0 failed` in this worktree and again from a `git archive` copy of its head (design: Task notes 4.1).

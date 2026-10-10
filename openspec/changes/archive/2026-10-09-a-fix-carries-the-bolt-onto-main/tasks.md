# Tasks

## 1. crew's fix merge carries the bolt

- [x] 1.1 `plan _carry` judges whether a fix carries its bolt onto main by `git range-diff` pairing, and with `--move` moves the bolt's branch to the fix's head in a clean bolt worktree whose heads have not moved, refusing and naming anything else (design: *crew judges the fix before it starts a merge stage*, *crew moves the bolt in the bolt's worktree*; Task notes 1.1; `read.1`, `read.2`, `code.6`).
- [x] 1.2 `crew fix <team> <name> --merge` ends the fix's agent, moves the bolt, runs the kit's post-merge hooks on it, records `fix.carry` and prints the move when the fix carries the bolt, and starts the merge stage as today, saying why, when it does not; the usage header says so (design: *The bolt's checks are the kit's post-merge hooks*, *What `--merge` prints and records*; Task notes 1.2; `teams.2`, `teams.5`, `record.3`, `record.6`, `docs.2`).
- [x] 1.3 `tests/t-fix.sh` proves the carry, the checks run and not approved, the fixes that merge instead, and the refusals, and `tests/suite t-fix` ends with "0 failed" (Task notes 1.3; `tests.4`).

## 2. The briefs and docs say so

- [x] 2.1 The main-ops, conductor, coder and ops briefs say how a landing's conflict becomes a fix that carries the bolt, what that fix's agent does, and that the bolt is proven again before it lands, each pinned in `t-briefs.sh`, and `tests/suite t-briefs` ends with "0 failed" (design: *The briefs*; Task notes 2.1; `tests.6`, `briefs.2` departure).
- [x] 2.2 README and the crew skill say what `--merge` now does and what a conflicting landing leads to, and `tests/suite t-docs` ends with "0 failed" (Task notes 2.2; `docs.2`).
- [x] 2.3 `teams.5`'s details name what builds the carry and `_open.md` no longer lists it, with `plan.md` and the `teams.5` rule line left as they are, and `tests/suite --affected` ends with "0 failed" (Task notes 2.3; design: *Risks / Trade-offs*).

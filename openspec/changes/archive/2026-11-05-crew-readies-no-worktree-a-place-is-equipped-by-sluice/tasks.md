# Tasks

Each check is a moon task of the `tests` project run through `tests/suite`. `logic` is `tests:logic`, `contract` is `tests:contract`, and an end-to-end test `t-<name>` is `tests:t-<name>`. Build the groups in order. Submit nothing, and never run `wt submit --help`.

## 1. The records

- [x] 1.1 Record 0023 carries the line "Superseded in part 2026-11-05" under its title and the amendment "crew readies no worktree; a place is equipped by sluice at Flume's asking" at its end, as Task notes 1.1 word them (design, Decision 1; Task notes 1.1). Verify that its two greps after Task notes 1.3 each print 1.
- [x] 1.2 Record 0024 carries its line and its amendment, which close the question it left open of `enterShell`'s install (design, Decisions 1 and 3; Task notes 1.2). Verify that its two greps after Task notes 1.3 each print 1.
- [x] 1.3 Record 0028 carries its line and its amendment, which give point 1 to Flume (design, Decision 1; Task notes 1.3). Verify that its two greps after Task notes 1.3 each print 1.

## 2. The spec

- [x] 2.1 The change removes every `kit-toolchain` requirement and retires the capability, and nothing of crew's outside the records and the archive cites the spec. That includes `tests/py/test_kit.py`, whose docstring cites Flume's record 0036 and whose unused `SCRIPT` is gone (design, Decision 2; Task notes 2.1). Verify that `openspec validate crew-readies-no-worktree-a-place-is-equipped-by-sluice --strict` passes, that `git grep -n kit-toolchain -- plugin tests README.md CLAUDE.md docs/architecture` prints nothing, and that `tests/suite logic` ends with "0 failed".

## 3. The words

- [x] 3.1 `.config/sluice.toml`'s opening comment, `README.md`'s line on places and `kit.py`'s docstring say crew readies no worktree and that sluice equips a place at Flume's asking. `t-docs` fails unless the README and the policy's comment say so, and `tests/moon.yml` is in step with its `# Reads:` line (design, Decision 5; Task notes 3.1). Verify `tests/suite t-docs` ends with "0 failed".

## 4. The shell

- [x] 4.1 The toolchain crew's policy names only activates. `enterShell` runs no `proto install`, and the task `crew:proto:install` installs a missing pin before the shell's entry, skipped by its status while every pin is installed. A new contract case runs the policy's toolchain and finds `proto activate` and no `proto install`, and the contract task takes `.config/sluice.toml` as an input (test-suite, "The toolchain crew's policy names only activates"; design, Decisions 3 and 4; Task notes 4.1). Verify `tests/suite contract` ends with "0 failed".

## 5. The change's tests

- [x] 5.1 Every test the change affects passes (Task notes 5.1). Verify `tests/suite --affected` ends with "0 failed".

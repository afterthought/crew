# merge-gate Specification

## Purpose

crew's own repository checks what it merges: a merge into a bolt or onto main is refused when crew's suite is red, and a bolt is verified by the whole suite after each merge into it, with an outcome ops reads.

## ADDED Requirements

### Requirement: A merge into a bolt is refused when the suite is red

A unit's or fix's `wt merge bolt/<bolt>` in crew SHALL run crew's whole suite through `tests/run`, inside crew's devenv, on the tree about to land, after the rebase and before the bolt moves. When any test fails, the merge SHALL be refused, the bolt SHALL be left where it was, and the merge's output SHALL name each failing test. The gate SHALL run without `--no-hooks` or `--yes`, and SHALL NOT run the live test.

#### Scenario: A red suite refuses a unit's merge
- **WHEN** a unit's place holds a change under which one test fails, and its merge stage runs `wt merge bolt/<bolt> --no-squash --no-remove`
- **THEN** the merge fails naming that test, and `bolt/<bolt>` is at the commit it was at before

#### Scenario: A green suite lets the merge land
- **WHEN** every test passes on the rebased tree
- **THEN** `bolt/<bolt>` holds the unit's commits

#### Scenario: A fix is gated the same way
- **WHEN** a fix on `fix/<bolt>/<name>` merges into its bolt
- **THEN** the same gate runs on the fix's rebased tree and refuses it when the suite is red

#### Scenario: The live test stays out
- **WHEN** the gate runs in an environment where `CREW_TEST_LIVE=1` is set
- **THEN** the live test is skipped as it is without the variable

### Requirement: A bolt's merge onto main is refused when the suite is red

A bolt's `wt merge main`, run by main-level ops from the bolt's worktree, SHALL run the same gate on the tree about to land on main, and SHALL be refused, with main left where it was, when any test fails.

#### Scenario: A red bolt does not land
- **WHEN** main-level ops runs `wt merge main --no-squash --no-remove` from a bolt's worktree and one test fails on the rebased tree
- **THEN** the merge fails naming that test, and main is at the commit it was at before

### Requirement: Every merge into a bolt starts the bolt's verification

After every merge into `bolt/<bolt>`, the whole suite SHALL run on the revision the bolt then holds, in the background, on a copy of that revision that no later merge or edit changes. Its outcome SHALL be recorded per revision where every worktree on the host can read it: running, green, or red with each failing test and the run's log. A merge onto main SHALL start no verification. Two runs SHALL NOT verify the same revision at once.

#### Scenario: A merge is verified
- **WHEN** a unit merges into `bolt/<bolt>`
- **THEN** a verification of the bolt's new head starts, and reads `running` until it ends `green` or `red`

#### Scenario: A red verification names what failed
- **WHEN** a test fails in the verification of the bolt's head
- **THEN** the outcome reads `red` with that test's name and the path of the run's log

#### Scenario: A later merge during a run
- **WHEN** a second merge lands on the bolt while the first merge's verification is still running
- **THEN** the first run finishes on the revision it started with, the second merge's run verifies the new head, and each outcome is recorded for its own revision

#### Scenario: Landing on main
- **WHEN** a bolt merges onto main
- **THEN** no verification runs in the main checkout

### Requirement: The bolt's verification is read for its head

One command, run in a bolt's worktree, SHALL print the verification of the bolt's current head: its state, revision, when it ran, each failing test and the log's path. It SHALL exit zero only when that state is green. A head with no recorded run SHALL read as not verified, never as another head's outcome. A run recorded as running whose process is gone SHALL read as interrupted. A record the command cannot read SHALL be named, and SHALL NOT read as green.

#### Scenario: ops reads a green bolt
- **WHEN** the last merge's verification passed and nothing has merged since
- **THEN** the command prints `green` with the bolt's head and exits zero

#### Scenario: The head has moved
- **WHEN** a merge landed after the last recorded run and its own run has not started
- **THEN** the command says the head is not verified, and exits non-zero

#### Scenario: A run cut off
- **WHEN** the run of the bolt's head was killed before it recorded an end
- **THEN** the command prints `interrupted`, and exits non-zero

### Requirement: ops runs the verification again on the same head

The verification SHALL be runnable by hand from a bolt's worktree on the bolt's head, with the same record, for when a run was cut off or a machine was fixed and nothing has merged since. It SHALL refuse to start while a run of the same revision is still alive.

#### Scenario: A rerun after a cut-off run
- **WHEN** ops runs the verification from the bolt's worktree after the head's run was interrupted
- **THEN** a new run of the same revision starts, and its outcome replaces the interrupted one

#### Scenario: A rerun while one is running
- **WHEN** ops runs the verification while the head's run is still alive
- **THEN** it refuses, saying a run of that revision is in progress

# test-suite Specification

## Purpose

How crew's own tests are run: one task per test file, side by side, a test whose inputs already passed replayed instead of run again, the tasks kept in step with the test files, and which tests an agent runs while it works, leaving the whole suite to the merge gate.

## Requirements

### Requirement: The suite runs as one task per test file, in parallel

crew's suite SHALL run as one moon task per `tests/t-*.sh`, each running that one test through `tests/run`, with the tasks run side by side. One command SHALL run every task, the tasks named, or only the tasks a change affects, and the merge gate and the bolt's verification SHALL run the suite through it. The live test SHALL NOT be a task.

#### Scenario: Every test runs, side by side
- **WHEN** the whole suite is run on a tree no run has passed
- **THEN** every test but the live one runs as its own task, several at once, and the run ends with `<n> passed (0 replayed), 0 failed`

#### Scenario: The live test stays out
- **WHEN** the whole suite is run with `CREW_TEST_LIVE=1` set
- **THEN** the live test is not run

### Requirement: A run reports every test and every failure

The command SHALL run every selected task even when one fails. It SHALL print one line per test saying whether it passed, was replayed or failed, then each failing test's output, then how many passed, how many of those were replayed and how many failed, and SHALL exit non-zero when any failed.

#### Scenario: One failure does not stop the others
- **WHEN** one test fails
- **THEN** every other selected test still runs, the failing test is named on a `FAIL  <name>` line with its output, and the command exits non-zero

### Requirement: A test whose inputs already passed is replayed

A task SHALL be replayed from moon's cache, without running the test, when its inputs are identical to those of a run of the same task that passed on the same host, in any worktree of crew, the main checkout, or the bolt's verification copy. A run that failed SHALL never be replayed. The command SHALL run every selected task without the cache when asked to.

#### Scenario: The gate replays the coder's run
- **WHEN** a coder's run passed every test on a unit's tree, and its merge's rebase leaves that tree unchanged
- **THEN** the merge gate replays every test, and the merge lands in about the time moon takes to check the cache

#### Scenario: The bolt's verification replays the gate
- **WHEN** a merge into a bolt passed its gate, and the bolt's verification starts on the revision that merge landed
- **THEN** the verification replays every test and reads green

#### Scenario: A test-only edit reruns one test
- **WHEN** only `tests/t-merge.sh` changed since a run that passed
- **THEN** only `t-merge` runs, and every other test is replayed

#### Scenario: A change to plugin/ reruns everything
- **WHEN** a file under `plugin/` changed since a run that passed
- **THEN** every test runs

#### Scenario: A failure is not replayed
- **WHEN** a test failed on a tree, and the suite runs again on the same tree
- **THEN** that test runs again

### Requirement: A task's inputs are everything its test reads

A task's inputs SHALL be everything its test reads from crew's tree: `plugin/`, `tests/run`, `tests/lib.sh`, `tests/stubs/`, crew's devenv files, the test file itself, and every other file of crew's the test reads. Files Python writes while a test runs SHALL NOT be inputs.

#### Scenario: Python's own files change nothing
- **WHEN** a run leaves `__pycache__` files under `plugin/`
- **THEN** the next run on the same tree replays every test that passed

### Requirement: Every test has a task, and the suite refuses when they are out of step

The tasks SHALL be generated from the test files by a script. The suite SHALL refuse to run, naming the test, when a test has no task, when a task has no test, when a task's inputs differ from what the script generates, or when a test reads a file of crew's outside the inputs its task names.

#### Scenario: A new test with no task
- **WHEN** a coder adds `tests/t-new.sh` and runs the suite without generating the tasks again
- **THEN** the suite refuses before running anything, naming `t-new`, and says how to generate the tasks

#### Scenario: A test reads a file its task does not name
- **WHEN** a test reads `$CREW/README.md` and its task's inputs do not include `README.md`
- **THEN** the suite refuses, naming the test and the file

### Requirement: The tests do not collide when run at once

Every test SHALL pass when the whole suite runs in parallel exactly as when it runs serially: no test SHALL share a file, a directory, a port or a process with another test, or depend on finishing within a time that contention can exceed.

#### Scenario: Parallel matches serial
- **WHEN** the whole suite runs once serially through `tests/run` and once as parallel tasks without the cache
- **THEN** both runs pass every test

### Requirement: An agent runs only the tests its change affects

A coder building or fixing a change, and a verify checking one, SHALL run only the tests its change affects, or tests it names, and never the whole suite by hand; the whole suite SHALL be run by the merge gate at each merge and by the bolt's verification after it. CLAUDE.md and the coder's, verify's and construct's briefs SHALL say so, and a change's tasks SHALL end with the tests it affects green, not the whole suite.

#### Scenario: A coder checks its work
- **WHEN** a coder in a unit's place wants to know its change is green
- **THEN** CLAUDE.md tells it to run the suite for the tests its change affects, with uncommitted edits counted, and that the merge gate runs the rest

#### Scenario: A change touching only one test
- **WHEN** a coder's change edits only `tests/t-merge.sh`, on a bolt that holds nothing main doesn't, and it runs the affected tests
- **THEN** only `t-merge` runs

#### Scenario: A bolt that already holds other work
- **WHEN** the bolt already holds a merged change to `plugin/`, its verification passed, and a coder's change edits only `tests/t-merge.sh`
- **THEN** the affected tests are every test, `t-merge` runs, and every other test is replayed from the bolt's verification

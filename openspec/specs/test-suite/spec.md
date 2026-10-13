# test-suite Specification

## Purpose

How crew's own tests are run: one task per test file, side by side, a test whose inputs already passed replayed instead of run again, the tasks kept in step with the test files, and which tests an agent runs while it works, leaving the whole suite to sluice's run of each submission.

## Requirements

### Requirement: The suite runs as one task per test file, in parallel

crew's suite SHALL run as one moon task per `tests/t-*.sh`, each running that one test through `tests/run`, with the tasks run side by side. One command SHALL run every task, the tasks named, or only the tasks a change affects, and sluice SHALL run the same tasks, by their `check-full` tag, on every submission to a bolt or to main. The live test SHALL NOT be a task.

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

A coder building or fixing a change, and a verify checking one, SHALL run only the tests its change affects, or tests it names, and never the whole suite by hand; the whole suite SHALL be run by sluice on each submission. CLAUDE.md and the coder's, verify's and construct's briefs SHALL say so, and a change's tasks SHALL end with the tests it affects green, not the whole suite.

#### Scenario: A coder checks its work
- **WHEN** a coder in a unit's place wants to know its change is green
- **THEN** CLAUDE.md tells it to run the suite for the tests its change affects, with uncommitted edits counted, and that sluice runs the rest

#### Scenario: A change touching only one test
- **WHEN** a coder's change edits only `tests/t-merge.sh`, on a bolt that holds nothing main doesn't, and it runs the affected tests
- **THEN** only `t-merge` runs

#### Scenario: A bolt that already holds other work
- **WHEN** the bolt already holds a merged change to `plugin/` whose tests passed in a worktree on the host, and a coder's change edits only `tests/t-merge.sh`
- **THEN** the affected tests are every test, `t-merge` runs, and every other test is replayed from that run

### Requirement: Every suite on a host shares the host's test slots
Every crew test on a host, whichever worktree, team or suite runs it, SHALL take one of the host's test slots before it runs and hold it until it ends, killed or not, and a test that finds none free SHALL wait its turn. A host SHALL have `CREW_TEST_SLOTS` slots, else its cores less two and at least two; a count that is not a number SHALL be refused. A test started inside another's slot SHALL run in that slot.

#### Scenario: Two tests and one slot
- **WHEN** a host has one slot and a second test starts while the first holds it
- **THEN** the second waits, and runs once the first lets its slot go

#### Scenario: A killed test
- **WHEN** a test holding a slot is killed
- **THEN** its slot is free again for the next test

#### Scenario: No count given
- **WHEN** `CREW_TEST_SLOTS` is not set on a host with ten cores
- **THEN** the host has eight slots

### Requirement: A test waits on a condition, never on the clock
No fixed sleep SHALL decide a test's outcome: a test SHALL wait on the condition it proves, ending as soon as it holds, with a limit that holds on a host loaded far past its cores, ten minutes for a wait on a condition and thirty for a background wait; a test that needs time to have passed SHALL move the time rather than wait for it.

#### Scenario: A follower's tails on a loaded host
- **WHEN** the test of `crew events --follow` runs on a host loaded past its cores and the follower's tails take longer than usual to start
- **THEN** the test waits until they start, up to ten minutes, and passes

#### Scenario: A commit in an earlier second
- **WHEN** a test needs a commit made before a stage began
- **THEN** it backdates the commit rather than sleeping into the next second

### Requirement: The test runners enter crew's shell themselves
`tests/run` and `tests/suite` SHALL run inside crew's devenv shell. Started outside it, with no `DEVENV_ROOT`, each SHALL run itself again under `devenv shell --` from its own checkout, whichever folder it was started from, and go on there. A shell that sets no `DEVENV_ROOT` SHALL stop it, saying so, rather than have it enter again; a host with no devenv SHALL stop it, saying so, before any test runs.

#### Scenario: Started outside the shell
- **WHEN** `tests/run no-such` is started from another folder with no devenv shell in its environment
- **THEN** devenv is run once, from the checkout, as `devenv shell -- <checkout>/tests/run no-such`, and inside it the run says there is no test `t-no-such`

#### Scenario: The suite started outside the shell
- **WHEN** `tests/suite --no-such` is started the same way
- **THEN** devenv is run once as `devenv shell -- <checkout>/tests/suite --no-such`, and inside it the suite prints its usage and exits 2

#### Scenario: A shell that sets no DEVENV_ROOT
- **WHEN** the shell a runner enters sets no `DEVENV_ROOT`
- **THEN** the runner exits 2, saying devenv shell set no `DEVENV_ROOT`, and devenv was run once

#### Scenario: No devenv on the host
- **WHEN** a runner is started outside the shell on a path with no devenv
- **THEN** it exits 2, saying devenv is not on the host's path, and runs nothing

### Requirement: An agent runs crew's tools through the shell per command
CLAUDE.md SHALL name how an agent runs crew's application tools, through crew's shell per command, `devenv shell -- <command>`; no role brief and no crew skill SHALL name it, since how a kit's tools are run is the kit's CLAUDE.md's to say (`tests.7`).

#### Scenario: The docs are checked
- **WHEN** crew's suite runs
- **THEN** it fails if CLAUDE.md does not hold `devenv shell -- `, or if any role brief or crew skill does

### Requirement: A worktree stays clean of the shell's working files
A crew checkout SHALL carry an `.envrc` that enters crew's devenv shell, for a person whose shell runs direnv, and SHALL ignore devenv's and direnv's working files and the tests' `.venv`, so entering the shell per command never leaves a worktree with untracked files.

#### Scenario: The checkout is checked
- **WHEN** crew's suite runs
- **THEN** it fails unless `.envrc` holds `use devenv` and `.gitignore` holds `.devenv/`, `.direnv/`, `tests/.venv/` and `!.envrc`

### Requirement: A test whose inputs already passed on the host is replayed

A task SHALL be replayed from moon's cache, without running the test, when its inputs are identical to those of a run of the same task that passed on the same host, in any worktree of crew or the main checkout. A run that failed SHALL never be replayed. The command SHALL run every selected task without the cache when asked to, and sluice's run of a submission to a bolt or to main SHALL replay nothing.

#### Scenario: A worktree replays another's run
- **WHEN** a coder's run passed every test on a unit's tree, and another worktree of crew on the host runs the suite on the same inputs
- **THEN** every test is replayed

#### Scenario: A submission replays nothing
- **WHEN** a unit is submitted to its bolt, or a bolt to main
- **THEN** sluice runs every test afresh, since crew's policy accepts no replay

#### Scenario: A test-only edit reruns one test
- **WHEN** only `tests/t-merge.sh` changed since a run that passed
- **THEN** only `t-merge` runs, and every other test is replayed

#### Scenario: A change to plugin/ reruns everything
- **WHEN** a file under `plugin/` changed since a run that passed
- **THEN** every test runs

#### Scenario: A failure is not replayed
- **WHEN** a test failed on a tree, and the suite runs again on the same tree
- **THEN** that test runs again

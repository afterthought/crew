## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: The suite runs as one task per test file, in parallel

crew's suite SHALL run as one moon task per `tests/t-*.sh`, each running that one test through `tests/run`, with the tasks run side by side. One command SHALL run every task, the tasks named, or only the tasks a change affects, and sluice SHALL run the same tasks, by their `check-full` tag, on every submission to a bolt or to main. The live test SHALL NOT be a task.

#### Scenario: Every test runs, side by side
- **WHEN** the whole suite is run on a tree no run has passed
- **THEN** every test but the live one runs as its own task, several at once, and the run ends with `<n> passed (0 replayed), 0 failed`

#### Scenario: The live test stays out
- **WHEN** the whole suite is run with `CREW_TEST_LIVE=1` set
- **THEN** the live test is not run

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

## REMOVED Requirements

### Requirement: A test whose inputs already passed is replayed
**Reason**: Its scenarios are of the merge gate and the bolt's verification, which record 0026 replaces with sluice's run of each submission.
**Migration**: "A test whose inputs already passed on the host is replayed".

## ADDED Requirements

### Requirement: A bolt's head is verified through its kit's test adapter
After every move of `land/<bolt>`, a follow of the bolt or a carry, crew SHALL verify its new head in the background on the team's host, by running the checks the kit's declaration requires of bolt branches through the test adapter, in a place of its own for that revision made ready through the declaration and removed after. A head sluice landed with a passing verdict SHALL need no run. The outcome SHALL be recorded per revision, where every worktree of the kit on the host can read it.

#### Scenario: A merge into a bolt in a kit on moon
- **WHEN** a unit merges into a bolt with `wt merge`, and crew follows the bolt
- **THEN** a verification of the new head runs the bolt branches' required tasks with `moon exec`, and reads `running` until it ends `green` or `red`

#### Scenario: A red check
- **WHEN** a required check fails in the verification of the bolt's head
- **THEN** the outcome reads `red`, naming that check and the path of the run's log

#### Scenario: A run already alive
- **WHEN** crew follows the bolt to a revision whose verification is still running
- **THEN** no second run of that revision starts

#### Scenario: Two follows in a row
- **WHEN** a second unit merges while the first merge's verification still runs
- **THEN** each revision is verified in its own place, and each outcome is recorded for its own revision

#### Scenario: A head sluice landed
- **WHEN** sluice lands a unit on the bolt with a passing verdict, and crew follows the bolt
- **THEN** the head reads green, by sluice's landing, and nothing is run

#### Scenario: A kit that declares no checks for bolts
- **WHEN** a kit's declaration names no `required` checks for bolt branches
- **THEN** crew runs no verification, and says the kit declares none

### Requirement: A bolt's verification is read and run again through crew
`crew bolt verify <bolt>` SHALL print the verification of `land/<bolt>`'s head, its state, revision, by whom, when it ran, each failing check and the log's path, and SHALL exit zero only when that state is green; any other state, a missing record or one crew cannot read SHALL NOT read as green. With `--again` it SHALL verify the same head again.

#### Scenario: ops reads a green bolt
- **WHEN** the last follow's verification passed and the bolt has not moved since
- **THEN** `crew bolt verify <bolt>` prints `green` with the head and exits zero

#### Scenario: The head has moved
- **WHEN** crew followed the bolt after the last recorded run and the new head's run has not started
- **THEN** it says the head is not verified, and exits non-zero

#### Scenario: A run cut off, run again
- **WHEN** the head's run was killed before it recorded an end, and ops runs `crew bolt verify <bolt> --again`
- **THEN** the first read says `interrupted`, and a new run of the same revision starts and replaces it

#### Scenario: A record crew cannot read
- **WHEN** the head's record is not one crew wrote
- **THEN** `crew bolt verify` names it and exits non-zero

#### Scenario: Again while one runs
- **WHEN** `crew bolt verify <bolt> --again` runs while the head's run is alive
- **THEN** it refuses, saying a run of that revision is in progress

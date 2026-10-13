# merge-gate Specification

## Purpose
Every merge into a bolt and every landing on main is a submission sluice tests on the checks the kit's policy requires and lands only when they pass; a bolt's verification is sluice's verdict on its last landing, and crew's own policy requires its whole suite.

## Requirements

### Requirement: Every merge into a bolt or onto main is a submission sluice gates
Every merge into a bolt, a unit's, a chore's or a fix's, and every landing of a bolt on main SHALL be a submission to sluice, which lands it as a merge commit only when the checks the kit's policy requires of the target branch pass on the target with the submission merged, and otherwise lands nothing and leaves the target where it was. crew SHALL run no merge gate or verification of its own, and nothing of crew's SHALL move a bolt's branch or main by git.

#### Scenario: A red check refuses a unit's merge
- **WHEN** a unit's place holds a change under which a required check fails, and its merge stage runs `wt submit bolt/<bolt> --no-remove`
- **THEN** the submission fails naming the check, and `bolt/<bolt>` is at the commit it was at before

#### Scenario: A green submission lands
- **WHEN** every required check passes on the bolt with the unit merged
- **THEN** `bolt/<bolt>` is a merge commit sluice made, holding the unit's commits

#### Scenario: A landing is gated the same way
- **WHEN** main-level ops runs `crew bolt submit <bolt>` and a required check of main fails on main with the bolt merged
- **THEN** nothing lands, and main is at the commit it was at before

### Requirement: A bolt's verification is sluice's verdict on its last landing
A bolt's verification SHALL be read from the `Sluice-Result` trailer of the merge commit at the bolt's head, which sluice writes on every landing: green only when it starts `passed`; none when the head is no landing of sluice's; unknown when there is no head to read. crew SHALL never read a bolt's verification as green from anything but that trailer.

#### Scenario: A bolt after a landing
- **WHEN** the last submission to `bolt/b` landed with `Sluice-Result: passed (9 run, 0 replayed)`
- **THEN** `crew bolts` shows the bolt's verification green, naming its head and that verdict

#### Scenario: A bolt nothing has landed on
- **WHEN** `bolt/b`'s head is a commit sluice did not make
- **THEN** its verification reads none, and the bolt is not offered for landing

### Requirement: crew's own policy gates its bolts and main on its whole suite
crew's `.config/sluice.toml` SHALL require the `check-full` tasks of every `bolt/*` branch and of `main`, run open on the host, and SHALL accept a replayed task for a bolt and none for main, so a landing runs every test afresh. The live test SHALL be no task.

#### Scenario: crew's policy
- **WHEN** crew's `.config/sluice.toml` is read
- **THEN** `[branches."bolt/*"]` and `[branches.main]` each require `#check-full`, the bolt's trust holds `cache` and main's does not

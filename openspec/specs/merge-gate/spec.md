# merge-gate Specification

## Purpose
Every merge into a bolt and every landing on main is a submission sluice tests on the checks the kit's policy requires and lands only when they pass; a bolt's verification is sluice's verdict on its last landing, and crew's own policy requires its whole suite.

## Requirements

### Requirement: Every merge into a bolt or onto main is a submission sluice gates
Every merge into a bolt, every landing on main, and every commit that reaches a kit's main, the user's and the design agent's among them, SHALL be a submission to sluice from a branch, landed as a merge commit only when the checks the kit's policy requires of the target pass with it merged, and otherwise landing nothing. Nothing of crew's SHALL move a bolt's branch or main by git, or run a merge gate or verification of its own.

#### Scenario: A red check refuses a unit's merge
- **WHEN** a unit's place holds a change under which a required check fails, and its merge stage runs `sluice submit bolt/<bolt> --no-wait --json`
- **THEN** its agent's `sluice wait` exits 1 naming the check, and `bolt/<bolt>` is at the commit it was at before

#### Scenario: A green submission lands
- **WHEN** every required check passes on the bolt with the unit merged
- **THEN** `bolt/<bolt>` is a merge commit sluice made, holding the unit's commits

#### Scenario: The design agent's record
- **WHEN** the design agent writes a decision record for a kit
- **THEN** it commits the record on a branch in a worktree of its own, submits it with `sluice submit main --no-wait --json` and waits on it with `sluice wait`, and the kit's main holds it only once sluice lands it, when the agent removes the worktree and its branch

#### Scenario: A landing is gated the same way
- **WHEN** main-level ops runs `crew bolt submit <bolt>` and a required check of main fails on main with the bolt merged
- **THEN** nothing lands, and main is at the commit it was at before

#### Scenario: A submission is never read from a listing
- **WHEN** an agent waits on its submission to a kit's main or a bolt
- **THEN** it reads the outcome from `sluice wait`'s exit and record, never from `sluice status <branch>`'s listing, which a decided submission leaves

### Requirement: A bolt's verification is sluice's verdict on its last landing
A bolt's verification SHALL be read from the `Sluice-Result` trailer of the merge commit at the bolt's head, which sluice writes on every landing: green only when it starts `passed`; none when the head is no landing of sluice's; unknown when there is no head to read. A landing beside the queue SHALL read as the verdict that covers it. crew SHALL never read a bolt's verification as green from anything but that trailer or, for a landing beside, sluice's record of it.

#### Scenario: A bolt after a landing
- **WHEN** the last submission to `bolt/b` landed with `Sluice-Result: passed (9 run, 0 replayed)`
- **THEN** `crew bolts` shows the bolt's verification green, naming its head and that verdict

#### Scenario: A bolt nothing has landed on
- **WHEN** `bolt/b`'s head is a commit sluice did not make
- **THEN** its verification reads none, and the bolt is not offered for landing

### Requirement: crew's own policy gates its bolts and main on its whole suite
crew's `.config/sluice.toml` SHALL require the `check-full` tasks of every `bolt/*` branch and of `main`, run open on the host, and SHALL accept no replayed task for either, so every submission runs every test afresh. The live test SHALL be no task.

#### Scenario: crew's policy
- **WHEN** crew's `.config/sluice.toml` is read
- **THEN** `[branches."bolt/*"]` and `[branches.main]` each require `#check-full` and trust `open` alone, and its executor is `open`

### Requirement: A landing beside reads as the verdict that covers it
A head that names a submission and no `Sluice-Tested`, which sluice lands beside its queue with nothing run, SHALL read as the verdict that covers it, from sluice's record of that submission (`sluice status <n> --json`, its `covered_by`), never from its trailer's words: green only when the record has it landed beside the queue as the head and names a covering verdict that passed, naming that verdict's run and replay counts and the revision it landed as; otherwise unknown, saying why.

#### Scenario: Covered by a verdict that passed
- **WHEN** every unit of `bolt/b` has merged, its head is a take-main fix sluice landed beside its queue as `#1319`, and sluice's record of `#1319` names the verdict that covers it, at `e25fea4`, `passed (141 run, 0 replayed)`
- **THEN** `crew bolts` shows its verification green, naming `#1319` landed beside with nothing run and the covering verdict `passed (141 run, 0 replayed)` at `e25fea4`, and `b` is a row of its kit's landings card that can land

#### Scenario: A record that names no covering verdict
- **WHEN** `bolt/b`'s head is a landing beside whose record, written by sluice 0.68.1, names no covering verdict, as sluice before 0.69.0 writes none
- **THEN** its verification reads unknown, saying sluice's record names none and that the bolt reads proven once a landing on it carries a verdict of its own or names the one that covers it, and the bolt is not offered for landing

#### Scenario: The trailer alone
- **WHEN** `bolt/b`'s head is a landing beside whose `Sluice-Result` opens `passed (0 run, 0 replayed)`, and sluice's record of its submission can't be read
- **THEN** its verification reads unknown, saying why the record can't be read, and never green

#### Scenario: A record of something else
- **WHEN** sluice's record of the head's submission has it landed as another commit, not landed, or covered by a verdict that did not pass or that crew can't read
- **THEN** its verification reads unknown, naming which

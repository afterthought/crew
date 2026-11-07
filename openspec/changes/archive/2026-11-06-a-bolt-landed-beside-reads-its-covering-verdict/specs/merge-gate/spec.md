## MODIFIED Requirements

### Requirement: A bolt's verification is sluice's verdict on its last landing
A bolt's verification SHALL be read from the `Sluice-Result` trailer of the merge commit at the bolt's head, which sluice writes on every landing: green only when it starts `passed`; none when the head is no landing of sluice's; unknown when there is no head to read. A landing beside the queue SHALL read as the verdict that covers it. crew SHALL never read a bolt's verification as green from anything but that trailer or, for a landing beside, sluice's record of it.

#### Scenario: A bolt after a landing
- **WHEN** the last submission to `bolt/b` landed with `Sluice-Result: passed (9 run, 0 replayed)`
- **THEN** `crew bolts` shows the bolt's verification green, naming its head and that verdict

#### Scenario: A bolt nothing has landed on
- **WHEN** `bolt/b`'s head is a commit sluice did not make
- **THEN** its verification reads none, and the bolt is not offered for landing

## ADDED Requirements

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

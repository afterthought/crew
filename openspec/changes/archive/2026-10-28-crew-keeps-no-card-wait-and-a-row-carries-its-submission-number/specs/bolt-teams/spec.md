## MODIFIED Requirements

### Requirement: A give to a team holding a waiting bolt restarts its roles at their next stop
A give to a team that holds a proven bolt SHALL restart neither its conductor nor its ops at once: each SHALL be restarted at its next stop, once idle, as an agent whose team's bolt changed under it is, the conductor fresh and ops with its conversation. The conductor's greeting at that restart SHALL name the bolt it now builds, the bolt that waits to land as a row of its kit's landings card, main-level ops's, that crew tells it when the user sends that bolt's reading and `crew card read land/<bolt>` then gives the notes, and each fix in flight on it. It SHALL name no wait to start. A give to a team that holds no bolt SHALL restart both at once, as before.

#### Scenario: A give while the conductor waits on its landing card
- **WHEN** `crew bolt give swc-1` gives `ssh-fix` while swc-1 holds `doctor-rows`, a row of its kit's landings card, and swc-1-conductor is idle
- **THEN** the conductor is restarted fresh once idle, and its first message says it builds `ssh-fix`, that `doctor-rows` waits to land as a row of the kit's landings card, that crew tells it when the user sends `land/doctor-rows`'s reading and `crew card read land/doctor-rows` gives the notes, and names no `crew card wait`

## ADDED Requirements

### Requirement: A submission's number is on its bolt's row from the submit
While a submission stands in sluice's queue, crew SHALL show its number and state on its bolt's row in `crew bolts`, text and JSON, from the first read after the submit, whoever made it, read from sluice's record of the queue on the team's host: a merge into `bolt/<bolt>` on its unit's, chore's or fix's line, and the bolt's landing on its kit's main, from `bolt/<bolt>` or a pull request opened from it, on the bolt's head line.

#### Scenario: A unit's merge under test
- **WHEN** unit `a`'s merge agent runs `sluice submit bolt/y --no-wait --json` and sluice answers `#41`, which it then tests
- **THEN** the next `crew bolts` shows `a`'s line with `#41 under test`, and its JSON gives `a` a submission of id 41 and state `testing`

#### Scenario: A bolt's landing queued on main
- **WHEN** main-level ops's `crew bolt submit y` has been answered `#355` and sluice has it queued on main
- **THEN** `crew bolts` shows `y`'s head line with `landing #355 queued`

#### Scenario: Read again after the session that submitted it ended
- **WHEN** a conductor restarts while unit `a`'s merge `#41` stands passed on `bolt/y` and nothing waits on it
- **THEN** `crew bolts` still shows `a`'s line with `#41 passed, to land next`

#### Scenario: Decided
- **WHEN** sluice lands `#41` on `bolt/y`
- **THEN** `a`'s line shows no submission and reads its stage as merged once the bolt holds its change archived

#### Scenario: sluice's record can't be read
- **WHEN** `sluice overview --json` fails on the team's host, or prints a document crew does not read
- **THEN** each held bolt of that kit on the host says its submissions can't be read and why, once, and no line shows a number or says it has none

### Requirement: A landing standing in sluice is waited on again, not submitted again
When `crew bolt submit <bolt>` finds the bolt's landing standing in sluice on its kit's main at the bolt's head, it SHALL submit nothing and SHALL wait on that submission again, as it waits on one it made, saying it waits on the number it found; the landing's end SHALL be read and recorded as for any landing. A landing standing at another head SHALL be said, naming its number and head, and the bolt SHALL be submitted as before.

#### Scenario: Ops restarted while its landing stood
- **WHEN** swancloud-ops's session ended while `crew bolt submit y` waited on `#355`, still queued on main at `y`'s head, and the restarted ops runs `crew bolt submit y`
- **THEN** nothing is submitted, the command says it waits on `#355` again, and once sluice lands it `y` is said landed and recorded as any landing is

#### Scenario: A standing landing at an older head
- **WHEN** `#350` stands on main for `y` at `abc1234`, and `y`'s head is now `def5678`
- **THEN** `crew bolt submit y` says `#350` stands at `abc1234`, and submits `y` at `def5678` as before

## MODIFIED Requirements

### Requirement: A bolt's landing entry records its time by holder
Every `bolt.land` entry crew writes SHALL record two things: the bolt's age, in whole minutes, from its start, the newest entry of the run record that made its branch, to its landing, as `Age`; and the minutes of that age each holder held, as `Split`, in the order team, kit, team-or-kit, user, hold, nobody, each named with its minutes, `team 130, kit 12, team-or-kit 0, user 40, hold 0, nobody 3`, team-or-kit being the minutes of a submission's stay in sluice that crew can't split between queued and under test, and team the minutes the bolt's own work held it. The split SHALL be made by the same rule the board's head line uses, and its minutes SHALL sum to `Age`. The landing SHALL be the moment sluice's record says the bolt's landing submission was decided, or the entry's own time when no submission of the bolt landed. sluice's record of the bolt's submissions SHALL be read once, on the kit's host, when the entry is written. When the start or that record can't be read, the entry SHALL carry neither field, and the landing SHALL go on as it does today.

#### Scenario: A bolt lands
- **WHEN** main-level ops closes the landing of `b`, started 6h 10m before sluice landed it, with its work holding it 3h 20m, kit 25m, user 2h 05m, hold 0 and nobody 20m
- **THEN** its `bolt.land` entry holds `Age: 370` and `Split: team 200, kit 25, team-or-kit 0, user 125, hold 0, nobody 20`

#### Scenario: A merge whose checks' start sluice's record does not keep
- **WHEN** `b`'s merge `#41` stood in sluice for seventeen minutes, and sluice's record read at the landing gives when it was submitted and decided but not when its checks began
- **THEN** those seventeen minutes are in `Split`'s team-or-kit, not its team or its kit, and `Split` still sums to `Age`

#### Scenario: sluice's record can't be read at the landing
- **WHEN** `sluice status` fails on the kit's host as `b`'s landing is recorded
- **THEN** the `bolt.land` entry is written without `Age` and `Split`, and the landing is closed as it is today

## REMOVED Requirements

### Requirement: A stage's end is recorded when crew sees it
**Reason**: Record 0047 move 5: crew starts no stage and waits on none; a stage's start and end are Flume's, carried back as the runner's records. crew writes no `stage.start` or `stage.end` (`record.5` retires as a rule of entries crew writes).
**Migration**: The runner's records of a place's stages; `crew trace` still reads the `stage.*` entries already on the branch.

## ADDED Requirements

### Requirement: A bolt's landing entry records its time by holder
Every `bolt.land` entry crew writes for a bolt a team held SHALL record two things: the bolt's age, in whole minutes, from its newest give to its landing, as `Age`; and the minutes of that age each holder held, as `Split`, in the order team, kit, user, hold, nobody, each named with its minutes, `team 130, kit 12, user 40, hold 0, nobody 3`. The split SHALL be made by the same rule the board's head line uses. The landing SHALL be the moment sluice's record says the bolt's landing submission was decided, or the entry's own time when no submission of the bolt landed. When the give or sluice's record of the bolt's submissions can't be read, the entry SHALL carry neither field, and the landing SHALL go on as it does today.

#### Scenario: A bolt lands
- **WHEN** main-level ops closes the landing of `b`, given 6h 10m before sluice landed it, with team 3h 20m, kit 25m, user 2h 05m, hold 0 and nobody 20m
- **THEN** its `bolt.land` entry holds `Age: 370` and `Split: team 200, kit 25, user 125, hold 0, nobody 20`

#### Scenario: sluice's record can't be read at the landing
- **WHEN** `sluice status` fails on the team's host as `b`'s landing is recorded
- **THEN** the `bolt.land` entry is written without `Age` and `Split`, and the landing is closed as it is today

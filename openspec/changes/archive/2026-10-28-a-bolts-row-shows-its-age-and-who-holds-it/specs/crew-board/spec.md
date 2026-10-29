## ADDED Requirements

### Requirement: A held bolt's head line shows its age and who held its time
Each held bolt's head line SHALL show, in the Construction lane, in the board's JSON and in every agent's band that draws it, the bolt's age since its newest give and the minutes of that age each holder held, leaving out a holder that held none. It SHALL also show who holds the bolt now and since when; for a hold, what the hold is for. Once nobody has held the bolt for five minutes, the line SHALL say it is stalled. When the give, the stages or the submissions can't be read, the line SHALL say the age or the split can't be told and why, and SHALL never show a guessed share. No card SHALL be raised and no one told because of a bolt's age.

#### Scenario: The bands
- **WHEN** the follower writes swb-1-conductor's view and the planner's
- **THEN** each draws `b`'s head line with its age, its shares and who holds it now, as the lane does

#### Scenario: Stalled
- **WHEN** nothing of `b` has run, stood in sluice, had a card open or been held for seven minutes
- **THEN** those seven minutes are nobody's, and the line says `b` is stalled since they began

#### Scenario: Nobody for a moment
- **WHEN** a stage of `b` ended two minutes ago and nothing has started since
- **THEN** the line says nobody holds `b` since then, and does not say it is stalled

#### Scenario: A give that can't be read
- **WHEN** the run record holds no give of `b` in the days the board reads
- **THEN** `b`'s head line says its age can't be told and why, and shows no share

### Requirement: Each minute of a bolt's life goes to one holder
Each minute of a held bolt's life SHALL go to exactly one holder, the first of these that applies:

1. the team, while a stage of the bolt's units, chores or fixes runs other than a merge;
2. the kit, while one of the bolt's submissions (a merge into its branch, or its landing on its kit's main) is under test in sluice;
3. the team, while a merge stage of the bolt's runs or one of its submissions stands in sluice not under test;
4. the user, while a card of the bolt's is open;
5. a hold, while one is recorded on the bolt;
6. nobody.

A submission whose start of checks sluice's record does not give SHALL be counted under test for its whole stay.

#### Scenario: A team at work
- **WHEN** bolt `b` was given to swb-1 three hours ago, a code stage ran for two hours, a batch card holding its unit was open for forty minutes with nothing running, and nothing held it for twenty minutes
- **THEN** `b`'s head line in the lane says `3h 00m`, team `2h 00m`, user `40m`, nobody `20m`, and names no kit or hold share

#### Scenario: A merge under test
- **WHEN** unit `a`'s merge `#41` into `bolt/b` stood queued for five minutes and then under test for twelve, while `a`'s merge stage ran throughout and no other stage ran
- **THEN** the five minutes are the team's and the twelve the kit's, and while `#41` is under test the line says the kit holds `b` since the start of its checks

#### Scenario: A stage beside a merge under test
- **WHEN** unit `c`'s code stage runs while unit `a`'s merge `#41` is under test
- **THEN** those minutes are the team's

#### Scenario: A decided merge whose checks' start is not kept
- **WHEN** sluice's record of `#41`, landed, gives when it was submitted and when it was decided but not when its checks began
- **THEN** its whole stay, from submitted to decided, is the kit's

### Requirement: Each holder is read from what crew already keeps
Every holder of a bolt's time SHALL be read from what crew already keeps, and nothing SHALL be recorded to make the reading:

- **Stages**: the run record's stage starts and ends for the bolt's work since the give.
- **Submissions**: sluice's record of each submission of the bolt: when it was submitted, when its checks began, and when it was decided.
- **Cards**: the run record's card posts and closes. A card is the bolt's when:
  - it is under the bolt's own key, `land/<bolt>`;
  - it is a batch's card holding work of the bolt's;
  - it is a proposal's card whose changes name the bolt or its work;
  - it is the kit's landings card, counted from the end of the bolt's last merge;
  - it is a question an agent of the bolt's team asked the user while the team held the bolt;
  - or its post names the bolt or its work.
- **Holds**: the run record's hold of the team's host, from its hold to its go.

#### Scenario: The user's card
- **WHEN** every unit of `b` has merged, nothing runs, and its kit's landings card has been open for an hour
- **THEN** that hour is the user's, and the line says the user holds `b` since the card's post, naming its key

#### Scenario: A question from the team
- **WHEN** swb-4's unit stopped short and swb-4-conductor's question to the user is open, with nothing of its bolt running
- **THEN** the minutes since its post are the user's

#### Scenario: A held host
- **WHEN** nothing of `b` runs and no card of it is open, while its team's host was held by the user at 14:02 and not yet let go
- **THEN** the minutes since 14:02 are the hold's, and the line says `b` is held since 14:02 because its host is held, naming who held it

## MODIFIED Requirements

### Requirement: The follower follows each kit's queue through sluice's overview
The host's follower SHALL learn that a kit's merge queue moved from sluice's overview alone. It SHALL keep one `sluice overview --json --watch` running in each kit whose queue its read shows, on the kit's host, take a line whose document differs from the last (its time aside) as the queue's move, and read the queue from that line. Where no watch can run, because the host's sluice has no watch or the kit's watch ended or could not start, it SHALL ask `sluice overview --json` once on its clock instead, and open an ended watch again at the next tick. A gather of a kit SHALL read the decided submissions of the kit's held bolts from sluice's record with `sluice status <branch> --all --json`, for each held bolt's branch and for the kit's main, and SHALL run no overview of its own while a watch's line gives the queue. Between gathers, a submission that has left the queue SHALL count as it last stood until the line that no longer holds it. crew SHALL read and name no folder of sluice's.

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box is queued in sluice, and the kit's overview watch prints a new line
- **THEN** the follower's next refresh, within a few seconds, shows the submission's number on the unit's row, gathers no kit and starts no sluice

#### Scenario: One watch for each kit
- **WHEN** the follower on mac-studio reads two partitions whose bolts are both in switchboard-kit on the box
- **THEN** it keeps one overview watch for switchboard-kit, over one ssh to the box, and a refresh that gathers the kit takes its queue from the watch's line, running no overview of its own and asking sluice only for its held bolts' records

#### Scenario: A host whose sluice has no watch
- **WHEN** the box's sluice refuses `--watch`
- **THEN** the follower asks the box's kits' overviews once at each tick of its clock, in that tick's one ssh to the box, and not between ticks

#### Scenario: A watch ends
- **WHEN** the ssh holding switchboard-kit's watch drops
- **THEN** the kit's row says its queue can't be read and why until the next tick, which opens the watch again and asks the overview once

#### Scenario: A held bolt's decided merges
- **WHEN** the follower gathers switchboard-kit while bolt `b`, held by swb-1, has had two merges decided and one standing
- **THEN** the gather reads `b`'s branch's and main's records from sluice once each, and `b`'s line counts all three merges' time in the gate

## MODIFIED Requirements

### Requirement: The follower follows each kit's queue through sluice's overview
The host's follower SHALL learn that a kit's merge queue moved from sluice's overview alone. It SHALL keep one `sluice overview --json --watch` running in each kit whose queue its read shows, on the kit's host, take a line whose document differs from the last (its time aside) as the queue's move, and read the queue from that line. Where no watch can run, because the host's sluice has no watch or the kit's watch ended or could not start, it SHALL ask `sluice overview --json` once on its clock instead, and open an ended watch again at the next tick. A gather of a kit SHALL start no sluice process while a watch's line gives the queue, and at most one `sluice overview --json` where none does; it SHALL run no `sluice status`, for a held bolt's branch or for the kit's main. The follower SHALL keep, for each kit, every submission of a held bolt it has seen stand, with when it was submitted and, once a candidate tested it, when its checks began, and SHALL keep it across later lines and gathers while the bolt is held. When a line no longer holds a kept submission, the follower SHALL take it as decided at the time that line's recent events give for it, or at that line's own time when they name it in no event, reading nothing else. crew SHALL read and name no folder of sluice's.

#### Scenario: A merge moves in sluice's queue
- **WHEN** a unit's merge into a bolt of switchboard-kit on the box is queued in sluice, and the kit's overview watch prints a new line
- **THEN** the follower's next refresh, within a few seconds, shows the submission's number on the unit's row, gathers no kit and starts no sluice

#### Scenario: One watch for each kit
- **WHEN** the follower on mac-studio reads two partitions whose bolts are both in switchboard-kit on the box
- **THEN** it keeps one overview watch for switchboard-kit, over one ssh to the box, and a refresh that gathers the kit takes its queue from the watch's line and starts no sluice process

#### Scenario: A host whose sluice has no watch
- **WHEN** the box's sluice refuses `--watch`
- **THEN** the follower asks the box's kits' overviews once at each tick of its clock, in that tick's one ssh to the box, and not between ticks

#### Scenario: A watch ends
- **WHEN** the ssh holding switchboard-kit's watch drops
- **THEN** the kit's row says its queue can't be read and why until the next tick, which opens the watch again and asks the overview once

#### Scenario: A held bolt's decided merges
- **WHEN** the follower gathers switchboard-kit while bolts `b` and `c` are held there, with merges of both decided and one of `b`'s standing
- **THEN** the gather runs no `sluice status`, for `bolt/b`, `bolt/c` or main, and the rows of `b` and `c` are drawn from the overview the watch last printed and what the follower kept of each submission

#### Scenario: A merge decided between gathers
- **WHEN** `b`'s merge `#41`, kept since it was submitted at 14:00 and tested from 14:05, leaves the queue on a line whose recent events say it landed at 14:17
- **THEN** the follower keeps `#41` decided at 14:17, starts no process to learn it, and still holds it after the next gather of the kit

#### Scenario: A withdrawn merge
- **WHEN** a kept merge of `b` leaves the queue on a line printed at 14:20 whose recent events do not name it
- **THEN** the follower keeps it decided at 14:20

### Requirement: A held bolt's head line shows its age and who held its time
Each held bolt's head line SHALL show, in the Construction lane, in the board's JSON and in every agent's band that draws it, the bolt's age since its newest give and the minutes of that age each holder held, leaving out a holder that held none. Minutes crew can't split between the team and the kit SHALL be shown as the team's or the kit's, with why, never added to either. It SHALL also show who holds the bolt now and since when; for a hold, what the hold is for. Once nobody has held the bolt for five minutes, the line SHALL say it is stalled. When the give, the stages or the submissions can't be read, the line SHALL say the age or the split can't be told and why, and SHALL never show a guessed share. No card SHALL be raised and no one told because of a bolt's age.

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

#### Scenario: Minutes that can't be split
- **WHEN** twelve minutes of `b`'s age were a decided merge's stay in sluice whose checks' start crew does not hold
- **THEN** the line shows `team or kit 12m` among its shares, says that sluice's record of the merge keeps no start of its checks, and counts those minutes in neither the team's share nor the kit's

### Requirement: Each minute of a bolt's life goes to one holder
Each minute of a held bolt's life SHALL go to exactly one holder, the first of these that applies:

1. the team, while a stage of the bolt's units, chores or fixes runs other than a merge;
2. the kit, while one of the bolt's submissions (a merge into its branch, or its landing on its kit's main) is under test in sluice, from the start of its checks to its decision;
3. the team or the kit, unsplit, while one of the bolt's submissions is in sluice, from its submit to its decision, and crew holds no start of its checks; and for the whole run of a merge stage that ended when crew holds no submit of that merge's work within it;
4. the team, while a merge stage of the bolt's runs, or one of its submissions stands in sluice not under test, or a decided submission stood from its submit to the start of its checks;
5. the user, while a card of the bolt's is open;
6. a hold, while one is recorded on the bolt;
7. nobody.

The team's share of a merge SHALL end at its submit unless the submission stands queued, and no minute between a submit and its decision SHALL go to the team under its merge stage when crew can't tell queued from under test.

#### Scenario: A team at work
- **WHEN** bolt `b` was given to swb-1 three hours ago, a code stage ran for two hours, a batch card holding its unit was open for forty minutes with nothing running, and nothing held it for twenty minutes
- **THEN** `b`'s head line in the lane says `3h 00m`, team `2h 00m`, user `40m`, nobody `20m`, and names no kit, hold or team-or-kit share

#### Scenario: A merge under test
- **WHEN** unit `a`'s merge `#41` into `bolt/b` stood queued for five minutes and then under test for twelve, while `a`'s merge stage ran throughout and no other stage ran
- **THEN** the five minutes are the team's and the twelve the kit's, and while `#41` is under test the line says the kit holds `b` since the start of its checks

#### Scenario: A stage beside a merge under test
- **WHEN** unit `c`'s code stage runs while unit `a`'s merge `#41` is under test
- **THEN** those minutes are the team's

#### Scenario: A decided merge with its checks' start
- **WHEN** `#41`, landed, was submitted at 14:00, its checks began at 14:05 as the follower saw while it stood, and it was decided at 14:17
- **THEN** 14:00 to 14:05 are the team's, 14:05 to 14:17 the kit's, and no minute of it is team-or-kit

#### Scenario: A decided merge whose checks' start is not kept
- **WHEN** `#41`, landed, was submitted at 14:00 and decided at 14:17, and neither the overview the follower kept nor sluice's record gives when its checks began
- **THEN** 14:00 to 14:17 are team-or-kit, though `a`'s merge stage ran throughout, and none of them is the team's or the kit's

#### Scenario: A merge that ended before the follower saw it
- **WHEN** the follower started after `a`'s merge stage of 13:50 to 14:20 and its merge's submission were over, so it holds no submit of `a`'s merge
- **THEN** 13:50 to 14:20 are team-or-kit

### Requirement: Each holder is read from what crew already keeps
Every holder of a bolt's time SHALL be read from what crew already keeps, and nothing SHALL be recorded to make the reading:

- **Stages**: the run record's stage starts and ends for the bolt's work since the give.
- **Submissions**: sluice's overview, as the follower's watch or one ask of it printed it, and what the follower kept of each submission from it: the number and where it came from, when it was submitted, when its checks began where a candidate testing it gave that, and when it was decided, from the recent events of the line that no longer held it. A landing on main is the bolt's when it came from `bolt/<bolt>`, from a pull request opened from it, or when its number is the one the run record's queued `bolt.submit` of the bolt names. No gather SHALL read sluice's record of a branch's submissions; a read made once at an act, as the landing's, MAY.
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

#### Scenario: A row drawn from the overview
- **WHEN** the follower's watch of switchboard-kit prints a line holding `b`'s merge `#41` under test since 14:05 and recent events naming `#40` landed at 13:58
- **THEN** `b`'s head line counts `#41` the kit's since 14:05 and `#40` decided at 13:58, read from that line and what the follower kept, with no sluice process started

#### Scenario: A landing by pull request
- **WHEN** main's recent events name `#52`, from `pull/9`, landed, and the run record's queued `bolt.submit` of `b` names `#52`
- **THEN** `#52` is `b`'s landing

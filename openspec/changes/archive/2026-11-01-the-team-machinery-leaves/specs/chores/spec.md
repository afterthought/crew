## ADDED Requirements

### Requirement: Chores are written by the planner, the design agent and the user
The planner SHALL write a chore only by proposal, the design agent only `chore add --repo`, and the user any. No other agent SHALL write a chore.

#### Scenario: An agent outside the role table orders a chore
- **WHEN** an agent that is not the planner, the design agent or the user runs `crew chore order bump-biome --first`
- **THEN** it is refused, naming who may write a chore, and the plan is unchanged

#### Scenario: The design agent queues a chore
- **WHEN** the design agent runs `crew chore add archive-x "Archive change x" --repo crew`
- **THEN** the chore is queued in crew's queue, with no proposal

## MODIFIED Requirements

### Requirement: After means for a chore what it means for a unit
A unit or chore of a started bolt SHALL be launched only once each `After`, a chore as a unit, has landed on the bolt, the runner holding its launch meanwhile, so its place is cut from a bolt that holds their work, as bolt-teams "A dependent launches once its After work has landed" has it; `crew bolts` SHALL show it `waiting` on them until then.

#### Scenario: A unit after a chore
- **WHEN** unit `b` of started `x` has `After: bump-biome`, and the chore's code has not yet committed
- **THEN** `crew bolts` shows `b` waiting on `bump-biome`

#### Scenario: The chore's code has delivered
- **WHEN** the chore's code has committed in its place, and its submission to `bolt/x` has not landed
- **THEN** `crew bolts` still shows `b` waiting on `bump-biome`, since a dependent waits for its After work to land on the bolt and not for its code

#### Scenario: The chore merges
- **WHEN** the chore lands on `bolt/x`
- **THEN** the runner launches `b`'s place, cut from a bolt that holds the chore's work, and `crew bolts` shows the chore merged and `b` no longer waiting on it

### Requirement: A chore shows as a chore
`crew bolts`, its JSON, the board and the page SHALL show a chore among the units of its bolt or queue in build order, marked as a chore. The run record SHALL name it `chore/<name>`, its writes `chore.add`, `chore.order`, `chore.after`, `chore.move` and `chore.drop`, and `crew trace <bare name>` SHALL try a unit, then a chore, then a bolt, then a signal.

#### Scenario: A trace by a chore's name
- **WHEN** `crew trace bump-biome` runs for a chore whose add and stages the run record holds, from before teams left or since
- **THEN** it prints the chore's add and each entry on it, as written

## REMOVED Requirements

### Requirement: A chore is built by code, verify and merge
**Reason**: Record 0047 move 5, record 0050 part 3: crew starts no stage in a slot; a chore is built as Flume's chore kind, launched through the runner on the crossed path.
**Migration**: The crossed path's launch of a chore (`teams-cross-to-flume-as-their-bolts-land`); `crew chore run` is gone.

### Requirement: A chore's stage starts only when it may
**Reason**: Record 0047 move 5: `crew chore run` and `crew unit run` leave; what a chore's stage may start on is the crossed path's launch and Flume's kind.
**Migration**: The crossed path's launch rules.

### Requirement: A chore's stage ends at its deliverable
**Reason**: Record 0047 move 5: a stage's end is Flume's, read from the runner's records; `crew chore wait` leaves.
**Migration**: A chore's stage as `crew bolts` reads it.

### Requirement: A chore's slot and place go when its work is over
**Reason**: Record 0047 move 5, record 0049 part 4: no slot; a chore's place is Flume's, tidied by Flume.
**Migration**: None in crew.

### Requirement: Chores are written by a unit's hands
**Reason**: Record 0047 move 5: no conductor orders a chore of its bolt (`roles.1`).
**Migration**: "Chores are written by the planner, the design agent and the user", added by this change.

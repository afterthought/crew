# Spec Delta

## Purpose

Handles a finding that blocks the unit it was found in: the user is asked at once, a small change stays inside the unit, and a large one goes out to curation and design while the unit is held from merging until what came of it has.

## ADDED Requirements

### Requirement: A finding that blocks a unit is the conductor's question to the user
When a stage or the conductor finds something that stops a unit of its bolt, the conductor SHALL put it to the user in its pane, in the words of whoever raised it. When the user says what to change, the conductor SHALL amend the unit by running construct again with the user's words. Only when the user says the change is large, or the question is one for design, SHALL the conductor record it as a blocking signal.

#### Scenario: A small change
- **WHEN** a code stage stops short because the change misnames a file, and the user says which file it should be
- **THEN** the conductor runs construct again with the user's words, the unit returns to review, and no signal is recorded

#### Scenario: A question for design
- **WHEN** a construct stage stops on a question the design does not answer and the user says to take it to design
- **THEN** the conductor records it with `crew signal … --blocks <unit>`

### Requirement: A blocking signal holds its unit
`crew signal … --blocks <unit>` SHALL record the signal and, in the same commit, mark the unit held by it in the plan. The capture SHALL say which unit it blocks. It SHALL be accepted only from an agent of the team that holds the unit's bolt, or from the user, and only for a unit that has not merged.

#### Scenario: The conductor blocks its unit
- **WHEN** swb-2's conductor runs `crew signal design-undecided "<what it asserts>" --excerpt "<the words>" --kind question --blocks cfn-lint-treefmt`
- **THEN** one commit on the flywheel's branch holds the capture, the signal, and `Hold: signals/<id>` on the unit

#### Scenario: Another team's unit
- **WHEN** swb-1's conductor names a unit of the bolt swb-2 holds
- **THEN** it is refused, and nothing is written

### Requirement: A held unit does not merge
`crew unit run <unit> merge` SHALL be refused while the unit carries a hold, naming the signal and where it stands: not yet curated, or on the agenda as an item. A held unit's other stages SHALL remain startable. `crew bolts` SHALL show a held unit as held, with the signal.

#### Scenario: Merge is refused
- **WHEN** the conductor runs the merge stage of a held unit
- **THEN** it is refused, the message names the signal and its agenda item, and a refused entry is recorded

#### Scenario: Work goes on
- **WHEN** the user tells the conductor to carry on coding the parts the question does not touch
- **THEN** `crew unit run <unit> code` starts as usual

### Requirement: A hold ends with what settles its signal
A unit's hold SHALL be lifted in the same commit as the write that settles its signal with no new unit: a standing move of `attach`, `challenge`, `answered` or `drop`; the signal's item closed as `dropped`; or its item closed as `decided` with no unit among its results. crew SHALL then tell the unit's conductor what settled it. A `route` or `join`, or a `revive`, SHALL leave the hold in place.

#### Scenario: A direct answer from design
- **WHEN** the design agent closes the signal's item as decided, with a decision record and no unit
- **THEN** the same commit lifts the hold, the conductor is told the record, and the conductor amends the unit with the answer

#### Scenario: Curation finds it already settled
- **WHEN** a delivery moves the blocking signal `answered`, naming a decision record
- **THEN** the delivery's commit lifts the hold, and the conductor is told the record and the reason

#### Scenario: The signal is put on the agenda
- **WHEN** the blocking signal is joined to a design item
- **THEN** the unit is still held, and `crew agenda` shows the item as holding that unit

### Requirement: A unit that came of the finding must merge first
When a unit whose source is the blocking signal's agenda item enters the held unit's bolt, the same commit SHALL replace the hold with a dependency: the held unit comes `After` the new unit. The held unit SHALL then be unable to merge until the new unit has merged into the bolt.

#### Scenario: A new unit is routed back in
- **WHEN** the user approves a proposal that adds a unit from the blocking item to the held unit's bolt
- **THEN** one commit adds the unit, removes the hold, and gives the held unit `After: <the new unit>`

#### Scenario: The new unit was queued first
- **WHEN** the design agent queued the unit in a session and a later approved proposal moves it into the bolt
- **THEN** the hold becomes the dependency at that approval

### Requirement: A unit that came of a blocking finding goes into the held unit's bolt
A proposal that would add or move a unit whose source is an item holding a unit SHALL be refused unless it puts that unit into the held unit's bolt, or also releases the hold. The refusal SHALL name the held unit and its bolt.

#### Scenario: Placed elsewhere
- **WHEN** the planner proposes the new unit for a different bolt
- **THEN** the proposal is refused, saying the item holds a unit of another bolt and its unit belongs there or the hold is to be released

### Requirement: The user's word releases a hold
`crew unit release <unit> "<why>"` SHALL remove a unit's holds, with the reason in the commit. It SHALL be run by the user, by the unit's conductor on the user's word, or inside an approved proposal. It SHALL NOT remove a dependency.

#### Scenario: The user decides not to wait
- **WHEN** the user tells the conductor the unit may merge without the answer
- **THEN** the conductor runs `crew unit release <unit> "<the user's reason>"`, and the merge stage can start

### Requirement: Holds are shown and recorded
`crew agenda` SHALL show, on an item, each unit it holds. Placing a hold, turning it into a dependency, lifting it and releasing it SHALL each leave a run-record entry naming the unit and the signal.

#### Scenario: Tracing a held unit
- **WHEN** `crew trace unit/<unit>` runs for a unit that was held and then merged
- **THEN** it shows the blocking signal's capture and the hold, the move and item, the new unit's proposal, approval and merge, and the held unit's merge after it

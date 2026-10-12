# Spec Delta

## ADDED Requirements

### Requirement: The planner posts a batch as one card
The planner SHALL post each batch as one partition card, keyed `batch/<n>`, naming every unit the batch holds, however many; a batch SHALL NOT be split across cards. A batch's answer SHALL be the user's; no agent SHALL answer a batch card.

#### Scenario: Seven changes due
- **WHEN** a batch holds seven changes
- **THEN** the planner posts one card for it, naming all seven units

## MODIFIED Requirements

### Requirement: The reviewer summarizes a batch
The reviewer SHALL read each due change whole and write one summary file holding, for each unit, its team, what the change does, the decisions it took, its risks, what it touches named in words, and anything the user would likely care about, as paragraphs and plain lists with no code block, no table and no path. The batch SHALL end at that file, its deliverable, and the reviewer SHALL write nothing else. The run record SHALL name the batch, each unit it holds and the commit each unit's change was read at.

#### Scenario: A batch of three
- **WHEN** a batch holds three units' changes from two teams
- **THEN** the reviewer's file holds one section for each of the three, naming its team, and the run record names the three units and their commits

#### Scenario: What a change touches
- **WHEN** the reviewer summarizes a change whose Touches lists the card hook and its test
- **THEN** its section names them in words, with no code block and no path

### Requirement: A batch card is read and answered in Pending You
A batch card SHALL be a notice that asks nothing, which the user sends back with one tap. It SHALL say first, in plain words, that there is nothing to answer and that notes on a unit go in its reading session or in the card's own note naming the unit. It SHALL carry each unit's summary as prose that wraps on a phone, never in a code block or an attachment, and the link to a plannotator session on each unit's whole OpenSpec change, one session for each unit. A unit's notes SHALL be the annotations the user sends from its session and the card's own note. A decision in a unit's session SHALL NOT answer or withdraw the card. The sessions SHALL end when the card closes.

#### Scenario: The user drills in
- **WHEN** the user opens a batch card holding three units
- **THEN** the card says there is nothing to answer and where notes go, shows each unit's summary as prose, and has three links, each opening a plannotator session on one unit's whole change

#### Scenario: Every unit fine
- **WHEN** the user sends a batch card of six units back with one tap and no note, having sent nothing from any session
- **THEN** the card is answered, no unit is constructed again, and the user picked and typed nothing

#### Scenario: Notes written in a session
- **WHEN** the user annotates one unit's change in its session and sends the annotations
- **THEN** the planner sends them to that unit's conductor as that unit's notes at once, and the card stays open for the user

#### Scenario: A session approved
- **WHEN** the user approves one unit's session without annotations
- **THEN** that unit is fine, nothing is sent for it, and the card stays open for the user

### Requirement: Notes reach the unit's conductor
The planner SHALL send the user's notes, word for word, to the conductor of the team of each unit they are for: a unit's session annotations to its own conductor, and the card's own note to the conductor of each unit the note speaks of, naming every unit it went to. A note that speaks of no unit the planner can tell SHALL go to every unit's conductor, saying so. The planner SHALL NOT split, reword or summarize a note. A unit with no annotations and of which the note does not speak SHALL be fine. The card's closing line SHALL name the units notes went to.

#### Scenario: Fine
- **WHEN** the user sends nothing from a unit's session and the card's note does not speak of it
- **THEN** nothing about the unit changes, and its change is no longer due

#### Scenario: One note for two units
- **WHEN** the user's note on the card speaks of `x1` and `z1`, of teams swb-1 and atl-1
- **THEN** swb-1's conductor gets the note word for word as `x1`'s notes, atl-1's conductor gets it as `z1`'s, each message names both units, and the card's closing line names `x1` and `z1`

#### Scenario: A note that names no unit
- **WHEN** the user's note on a card of three units speaks of none of them that the planner can tell
- **THEN** each of the three units' conductors gets the note word for word, saying it named no unit

## REMOVED Requirements

### Requirement: The planner posts a batch as cards of at most five units
**Reason**: A batch is one card, never split by five (`briefs.13` as amended 2026-10-11; record 0005). The card asks no choice, so Pending You's five options no longer bound it.
**Migration**: Replaced by "The planner posts a batch as one card". A batch posted before this lands keeps its `batch/<n>-<k>` cards until each closes.

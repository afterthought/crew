# Spec Delta

## Purpose

Keeps the list of what curation and people have put before the planner and the user: each item a proposed intent or a question in a lane, with the signals it rests on, readable at any time, and closed only by what came of it.

## ADDED Requirements

### Requirement: The agenda is a list anyone can open at any time
`crew agenda [--label <label>] [--lane plan|design] [--all] [--json]` SHALL list the flywheel's open items from any host: each one's number, lane, kind, kit, subject and weight, and any open proposal that would plan it. Items SHALL be records in `agenda.rec` on the flywheel's branch. An item's number SHALL be given once and never reused, and an item SHALL never be removed.

#### Scenario: The user opens the agenda
- **WHEN** the user asks the operator agent what needs deciding
- **THEN** `crew agenda --lane design` lists each open design item with its subject and weight

#### Scenario: A closed item is still citable
- **WHEN** a decision record cites `agenda/7` and item 7 was closed a month ago
- **THEN** `crew agenda 7` still prints it, with how it closed

### Requirement: An item's signals and weight are read, never stored
An item's signals SHALL be the signals whose standing move targets it. Its weight SHALL be how many signals, from how many captures and of which sources, over what span of event dates. Neither SHALL be stored on the item.

#### Scenario: Weight by event date
- **WHEN** an item's three signals come from a meeting on Monday and a conductor's capture on Thursday, all curated on Friday
- **THEN** its weight reads three signals, two captures, Monday to Thursday

#### Scenario: A signal is moved away
- **WHEN** the user replaces a signal's move so that it targets another item
- **THEN** the first item's weight falls, with no write to the item

### Requirement: One item is read with its evidence
`crew agenda <n>` SHALL print the item and each of its signals: its id, kind, who asserted it, the assertion, the excerpt with its grade, the capture's source and event date, and the reason of the move that put it there. For a closed item it SHALL print how it closed and its results.

#### Scenario: The design agent takes up an item
- **WHEN** the user names item 7 in the design agent's pane
- **THEN** the design agent runs `crew agenda 7` and reads the question, the signals and the words they rest on, and nothing of the other unmoved signals

### Requirement: An item is added by hand from signals
`crew agenda add "<subject>" --lane plan|design --signal <id>...` SHALL create an item and move each named signal to it, `route` or `join` by the lane, in one commit. It SHALL require at least one signal, each without a standing move. It SHALL be run by the user or by an agent on the user's word.

#### Scenario: A design talk the user starts
- **WHEN** the user raises something new in the design agent's pane and wants it settled
- **THEN** the design agent records the user's words as a signal and adds a design item from it, and the session works that item

#### Scenario: A signal already moved
- **WHEN** `crew agenda add` names a signal with a standing move
- **THEN** it is refused, naming the move

### Requirement: An item changes lane with a reason
`crew agenda lane <n> plan|design "<why>"` SHALL change an open item's lane and keep the reason on the item. Sending a plan item to the design lane SHALL drop, in the same commit, any open proposal that would add a unit from it. The planner SHALL send to the design lane any plan item whose unit's intent needs a decision only the user can make.

#### Scenario: The planner finds a decision in a plan item
- **WHEN** the planner cannot word a unit's intent for item 8 without choosing between two designs
- **THEN** it runs `crew agenda lane 8 design "<the decision it needs>"`, and item 8 is on the design agenda with that note

#### Scenario: The user sends a proposed unit back
- **WHEN** the user reads a proposal and says item 8 needs design
- **THEN** the lane change drops the open proposal, naming the item as the reason

### Requirement: A design item is closed by what was decided
`crew agenda close <n> decided --result <ref>...` SHALL close an item with at least one result, each of which exists and cites the item: a committed decision record or intent whose text names `agenda/<n>`, or a unit whose source is `agenda/<n>`. `crew agenda close <n> dropped "<reason>"` SHALL close it with nothing decided. A closed item SHALL keep its results and the date.

#### Scenario: A session decides
- **WHEN** the design agent closes item 7 with a decision record and a queued unit
- **THEN** crew checks the record is committed and names `agenda/7` and the unit's source is `agenda/7`, and item 7 is `decided` with both as results

#### Scenario: A result that does not cite the item
- **WHEN** a result names a decision record whose text does not mention `agenda/7`
- **THEN** the close is refused, naming the record

#### Scenario: The design already answers it
- **WHEN** the session finds the design already settles the question
- **THEN** the item is closed `dropped`, the reason naming the page that answers it

### Requirement: A unit names the item it came from
`crew unit add … --item <n>` SHALL add the unit with `agenda/<n>` as a source. An agent's `crew unit add` SHALL be refused unless it names an open item, or is the planner's `--signal`. The design agent SHALL add units only from a design item, into a kit's queue; the planner only from a plan item, inside a proposal. The user at a shell SHALL add units freely.

#### Scenario: The design agent queues a unit of a session
- **WHEN** the design agent runs `crew unit add <unit> "<intent>" --repo <kit> --item 7` while item 7 is open in the design lane
- **THEN** the unit is queued with `Source: agenda/7`

#### Scenario: A unit with no item
- **WHEN** the design agent runs `crew unit add` with no `--item`
- **THEN** it is refused, and the message says to add an item from the user's words first

#### Scenario: The wrong lane
- **WHEN** the planner proposes a unit from an item in the design lane
- **THEN** the proposal is refused; a design item is the user's to decide

### Requirement: A unit's builder reads the item
A unit whose source is `agenda/<n>` SHALL give its construct stage that source, and the construct agent SHALL read the item and its signals with `crew agenda <n>` before writing the change.

#### Scenario: Construct from an item
- **WHEN** a unit added from item 8 reaches construct
- **THEN** its prompt names `agenda/8`, and the change's proposal quotes the excerpts the item rests on

### Requirement: Agenda acts are in the run record
Creating an item, changing its lane and closing it SHALL each leave a run-record entry naming `agenda/<n>`, the signals or results involved, and the commit. A unit added with `--item` SHALL name the item as what it came from.

#### Scenario: Tracing an item
- **WHEN** `crew trace agenda/7` runs
- **THEN** it shows the signals captured, the moves that joined them, the item, the session's close with its results, and each unit that came of it

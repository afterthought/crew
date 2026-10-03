# Spec Delta

## Purpose

Decides what each signal means, in batches and against the design as it stands, by a session that only judges: every unmoved signal gets one move with its reason, and the signals that should lead somewhere are put before the planner or the user.

## ADDED Requirements

### Requirement: Curation is its own pass, run on the user's word
`crew curate <label>` SHALL start a curator session for one batch, in a `curator` tab of the main level's workspace, on the main level's host. It SHALL be run only when the user asks for it. One curator SHALL run per flywheel at a time. The curator SHALL be a session of its own, never the design agent or the planner, and its tab SHALL be closed once its batch is delivered and its agent is no longer working.

#### Scenario: The user asks for curation
- **WHEN** the user tells the operator agent to curate wldn's signals
- **THEN** `crew curate wldn` starts `wldn-curator` in the `wldn` workspace on the main level's host, with its batch

#### Scenario: A curator is already running
- **WHEN** `crew curate wldn` runs while wldn's curator is up
- **THEN** it is refused, naming the batch in hand

#### Scenario: Nothing to curate
- **WHEN** no signal in scope is without a standing move
- **THEN** it says so and starts nothing

### Requirement: A batch is fixed when curation starts
A batch SHALL be every signal with no standing move, in the flywheel's state and in the partition's first blueprints repo, at the commits read when `crew curate` runs, or with `--only <capture>...` those of the named captures. A signal recorded after that SHALL wait for the next batch.

#### Scenario: A signal arrives mid-run
- **WHEN** a conductor records a signal while the curator is working
- **THEN** the batch and its delivery do not include it, and it is unmoved afterwards

#### Scenario: Choosing captures
- **WHEN** `crew curate wldn --only <capture>` runs while 192 meeting signals are also unmoved
- **THEN** the batch is that capture's signals alone

### Requirement: The work order is everything the curator needs
`crew curate` SHALL write a work order on the main level's host holding the batch's captures and signals as files, the open agenda items with their signals, the plan's bolts with their goals and its units with their intents, where the standing design is to be read, and the delivery's format. The curator SHALL read the design in the main checkouts and SHALL write nothing but its delivery.

#### Scenario: A lagging checkout
- **WHEN** the blueprints checkout on the main level's host is behind
- **THEN** the work order still holds every signal of the batch, exported at the commits the batch was fixed at

#### Scenario: The curator has an idea of its own
- **WHEN** the curator notices something that is not a judgment on a signal
- **THEN** it records it with `crew signal` and carries on, and that signal is not in its batch

### Requirement: Each signal gets one move, with its reason
A move SHALL be one of `attach`, `challenge`, `join`, `answered`, `route` and `drop`, and SHALL carry a reason a stranger could weigh. `route` SHALL target a plan-lane agenda item and `join` a design-lane item. `attach` SHALL target a unit, a bolt or an open intent already under way; `challenge` a standing page of the design; `answered` what settled it. A target that does not resolve, or a move with no reason, SHALL be refused.

#### Scenario: A plan-ready signal
- **WHEN** the planner could write a unit's intent from a signal with no decision only the user can make
- **THEN** its move is `route`, to a plan item

#### Scenario: A signal that needs the user
- **WHEN** a signal raises a design question, a tradeoff or something to investigate
- **THEN** its move is `join`, to a design item

#### Scenario: Work already planned
- **WHEN** a signal asks for what a queued unit already says
- **THEN** its move is `attach`, to that unit, and nothing new is planned

#### Scenario: A target that does not exist
- **WHEN** a move challenges a page that is not on its repository's main
- **THEN** the delivery is refused, naming the move

### Requirement: Routed and joined signals are gathered into agenda items
A delivery SHALL create the agenda items its `route` and `join` moves target, or target items already open in the same lane. A new item SHALL rest on at least one signal of the batch. A design item's subject SHALL say what is unsettled and not the answer; a plan item's subject SHALL say what was asked for, in the asserter's terms, and SHALL name its kit.

#### Scenario: Three signals, one question
- **WHEN** three signals of a batch raise the same design question
- **THEN** the delivery creates one design item, and all three join it

#### Scenario: A signal for an open item
- **WHEN** a signal fits an item already open in the design lane
- **THEN** it joins that item, whose weight grows, and no new item is made

#### Scenario: An item with no signal
- **WHEN** a delivery holds an item no move targets
- **THEN** the delivery is refused

### Requirement: A delivery covers its batch exactly, in one commit
`crew curate deliver <file>` SHALL be accepted only when every signal of the batch has exactly one move, no other signal has one, and every move and item passes its checks. It SHALL then write every move and every new item in one commit on the flywheel's branch. Delivering again SHALL write nothing. A signal of the batch that gained a move by hand during the run SHALL be named, and the delivery refused until it leaves that signal out.

#### Scenario: Sixty signals
- **WHEN** a curator delivers moves for a batch of sixty signals
- **THEN** one commit adds sixty moves and the items they made

#### Scenario: A signal left out
- **WHEN** a delivery has no move for one signal of the batch
- **THEN** it is refused, naming the signal, and nothing is written

#### Scenario: Delivered twice
- **WHEN** the same delivery is run again
- **THEN** it says the batch was delivered and at which commit, and writes nothing

### Requirement: The planner is told what waits for it
When a delivery leaves open plan items, crew SHALL tell the planner which. For design items crew SHALL tell no one: they are on the agenda for the user to open.

#### Scenario: Two plan items and a design item
- **WHEN** a delivery creates plan items 8 and 9 and design item 10
- **THEN** the planner is told of 8 and 9, and no agent is prompted about 10

### Requirement: A person's hand is curation too
`crew signal move <id> <move>` and `crew agenda add` SHALL write the same records a delivery writes, under the same checks, when run by the user or by an agent on the user's word. An agent SHALL NOT move a signal by hand on its own judgment.

#### Scenario: The user drops a signal
- **WHEN** the user tells the operator agent to drop a signal as noise
- **THEN** `crew signal move <id> drop --reason "<why>"` records the move, by the operator agent, in the user's words

### Requirement: Only the user replaces a move
A signal SHALL have one standing move: its latest, which no later move replaces. A second move for a signal SHALL be refused unless it is given with `--replace "<why>"`, by the user or on the user's word, and the new record SHALL name the move it replaces. `crew signal revive <id> "<why>"` SHALL leave the signal without a standing move, so the next batch takes it. No move SHALL ever be changed or removed.

#### Scenario: A wrong drop
- **WHEN** the user revives a signal the curator dropped
- **THEN** a `revive` record names the drop it replaces, the drop is still in the file, and the signal is in the next batch

#### Scenario: A second move without the user
- **WHEN** `crew signal move` names a signal that has a standing move, without `--replace`
- **THEN** it is refused, naming the move it has

#### Scenario: Moving a signal to another item
- **WHEN** the user replaces a signal's `join` to item 7 with a `join` to item 12
- **THEN** item 7's weight falls by one signal and item 12's grows

### Requirement: Curation is in the run record
Starting a batch, delivering it, each move, each replacement and each item created SHALL leave a run-record entry. A move's entry SHALL name the signal and its target; the moves of one delivery SHALL share its commit.

#### Scenario: Tracing a routed signal
- **WHEN** `crew trace signals/<id>` runs for a signal a delivery routed
- **THEN** it shows the capture, the move with the curator's name and session, and the item

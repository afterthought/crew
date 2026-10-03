# Spec Delta

## MODIFIED Requirements

### Requirement: The design agent elaborates on main
The design agent SHALL keep the partition's design true on main: the books, specs and constitution in its blueprints repos and kits, and the decision records. It SHALL NOT curate signals or read the unmoved ones. It SHALL work the agenda items the user takes up, reading each with `crew agenda <n>`, and SHALL record what a session decides as decision records, intents and queued units that cite the item, then close the item with them. It SHALL answer a conductor's design question. Work its elaboration calls for SHALL be queued as units, never put into a bolt by the design agent.

#### Scenario: Elaboration produces work
- **WHEN** a session on item 7 records a decision that needs building
- **THEN** the design agent queues a unit with `--item 7` whose sources are the item and the decision's page, and the planner places it by proposal

#### Scenario: A batch of signals arrives
- **WHEN** a curator delivers forty moves and three design items
- **THEN** the design agent is told nothing, and reads an item only when the user takes it up

### Requirement: The planner plans across bolts
The planner SHALL be the only agent that proposes bolts, the placing of units into bolts, and their splitting, ordering or moving between bolts, and SHALL change the plan only through a proposal the user approves. It SHALL turn each plan-lane agenda item into a proposed unit, and SHALL send to the design lane an item whose intent needs a decision only the user can make. A change to an active bolt SHALL be agreed by that bolt's conductor, with `crew plan agree`, before the proposal can be approved. The planner SHALL NOT start units or drive a team.

#### Scenario: A finding mid-bolt
- **WHEN** curation routes a conductor's finding about work outside its bolt's goal to plan item 8
- **THEN** the planner proposes a unit from item 8 for the queue or another bolt, and the conductor's bolt keeps its goal

#### Scenario: New work beside a bolt in flight
- **WHEN** the planner judges that new work belongs in the bolt swb-2 holds
- **THEN** it proposes the unit for that bolt, swb-2's conductor agrees or says why not, and the unit is in the bolt only once the user has approved the proposal

#### Scenario: An item that needs a decision
- **WHEN** a plan item cannot be worded as a unit without choosing between designs
- **THEN** the planner sends it to the design lane with the decision it needs, and proposes nothing from it

### Requirement: Signals reach the plan only through a route
A signal recorded through crew SHALL live on the flywheel's branch of its state repository, and a signal read from a meeting or a channel in the partition's first blueprints repo, both in the signals model that repo's `signals/README.md` gives. An agent that notices something outside its own unit SHALL record it as a signal with `crew signal`, quoting the words that show it, and SHALL tell no other agent about it. A signal SHALL reach the plan only after it has been curated: through a plan item the planner proposes a unit from, or a design item a session decides. The one exception SHALL be what the user tells the planner directly.

#### Scenario: A finding from a bolt
- **WHEN** ops on swb-1 finds a defect in a shared service the bolt does not own
- **THEN** it records a signal quoting the output that shows the defect, tells nobody, and carries on

#### Scenario: An uncurated signal
- **WHEN** the planner tries to propose a unit from a conductor's signal that has no move
- **THEN** it is refused, saying the signal has not been curated

#### Scenario: The user tells the planner directly
- **WHEN** the user tells the planner to queue something, in the planner's pane
- **THEN** the planner records the user's words as a signal and proposes the unit from it, and the user's approval routes that signal to the unit

### Requirement: Every move is written through crew and never merged
Every move SHALL be appended to `moves.rec` on the flywheel's branch of its state repository, through crew: by a curator's delivery, by `crew signal move`, by `crew agenda add`, or by the approval of a unit the planner proposed from the user's direct word. The moves SHALL be `attach`, `challenge`, `join`, `answered`, `route` and `drop`, and `revive`, which leaves a signal unmoved. Each write SHALL be fetched over https, applied to the tip of the branch, checked with `recfix --check`, committed, and pushed without force, applied again to the new tip when the push is refused. A signal SHALL have one standing move; a second is refused unless it is the user's replacement, which names the move it replaces.

#### Scenario: Moves from two hosts
- **WHEN** a delivery is written on the box while the user's drop of another signal is written on mac-studio, both through crew
- **THEN** every move is in `moves.rec`, nothing is merged, and the file passes `recfix --check`

#### Scenario: A signal moved twice
- **WHEN** `crew signal move` names a signal that already has a standing move, without `--replace`
- **THEN** it is refused, naming the move it has

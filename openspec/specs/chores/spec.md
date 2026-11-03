# chores Specification

## Purpose
A chore beside a unit and a fix: planned maintenance in a kit, a version bump, a config alignment, an archive of a proven change, that changes nothing a spec says must be true, planned like a unit and built in its bolt by code, verify and merge with no OpenSpec change, no construct and no review (`plan.11`, record 0001).

## Requirements

### Requirement: A chore is a Unit record marked as a chore
A chore SHALL be a record of the plan's Unit set marked `Kind: chore`, holding its name, repo, bolt (none while queued), its words as `Intent`, its sources and its `After`, and never `Amended`. It SHALL sit in the file among the units in build order, and `After` SHALL name units and chores of the same bolt either way round.

#### Scenario: A chore in a bolt
- **WHEN** the user runs `crew chore add bump-biome "Biome follows the shell's version" --bolt tooling --before b`
- **THEN** `plan.rec` holds `Unit: bump-biome` with `Kind: chore` in bolt `tooling`, ahead of unit `b`, and `recfix --check` passes

#### Scenario: An amended mark on a chore
- **WHEN** a hand edit gives a chore an `Amended` field
- **THEN** crew's next write refuses, naming the chore: a chore has no amendment

### Requirement: A chore changes nothing a spec says must be true
A chore SHALL be maintenance that changes nothing a spec says must be true and needs no decision the design has not made: a tool or dependency bump, a pin or config aligned, the archive of a change whose every task is ticked, a rename or a moved file, a stale instruction, citation or line of documentation. Its code SHALL touch nothing under `openspec/` but such an archive.

#### Scenario: An archive with a task open
- **WHEN** a chore's words are to archive a change one of whose tasks is not ticked
- **THEN** its coder stops and says so through crew, and archives nothing

### Requirement: A chore's name is taken once in a kit
A chore's name SHALL be refused when the plan holds a unit or chore by it, when the kit's main holds an OpenSpec change by it, open or archived, or when main's history holds a commit carrying `Chore: <name>`. A unit's name SHALL be refused for the last as well.

#### Scenario: The name of a landed chore
- **WHEN** a chore named `bump-biome` has landed and left the plan, and someone adds a unit or a chore named `bump-biome`
- **THEN** it is refused, naming the chore main holds

### Requirement: Chores are written by a unit's commands
`crew chore add`, `crew chore order`, `crew chore after`, `crew chore move` and `crew chore drop` SHALL take the flags of the unit command of the same name and make its refusals, `--signal` routing a signal to `chore/<name>` and `--unblocks` placing it ahead of a held bolt's first unmerged unit or chore. There SHALL be no `chore split` and no `chore amend`. A unit command naming a chore, or a chore command naming a unit, SHALL be refused, naming its kind and the command that takes it.

#### Scenario: A unit command on a chore
- **WHEN** someone runs `crew unit drop bump-biome "<reason>"` for a chore
- **THEN** it is refused: bump-biome is a chore, dropped with `crew chore drop`

#### Scenario: A chore from a signal
- **WHEN** the user runs `crew chore add bump-biome "…" --bolt tooling --signal <id>`
- **THEN** the chore is added and the signal's move is `route` with `Target: chore/bump-biome`, in the same commit

### Requirement: A chore's stage is read from its kit
crew SHALL read a chore's stage from its kit on its team's host, nothing recorded by hand; the first rule that holds is the stage: `queued` with no bolt; `unknown` when its host does not answer or its place tracks no bolt crew can read; `landed` when main's history holds a commit carrying `Chore: <name>`; `merged` when `bolt/<bolt>` holds one; `verify` when its place holds a commit of its own beyond the bolt; `code` when its place holds none; `ready` or `waiting` with no place.

#### Scenario: Coded and not yet verified
- **WHEN** a chore's place holds two commits beyond its bolt
- **THEN** `crew bolts` shows it `chore verify`, and no file was written to say so

#### Scenario: Merged
- **WHEN** the bolt holds the chore's commits, each carrying `Chore: bump-biome`, and its place is gone
- **THEN** its stage is `merged`

#### Scenario: What its place took is not its own
- **WHEN** a chore's place has taken a unit's head and holds no commit of the chore's own
- **THEN** its stage is `code`

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

### Requirement: A chore is never constructed or reviewed
No batch SHALL hold a chore, the planner SHALL never be told a batch is due for one, and a bolt's landing SHALL never wait on a batch for one. A chore's verify report SHALL be no rail row and have no card, as a unit's has none: its findings marked fix are fixed in one round (`teams.17`).

#### Scenario: A bolt of chores
- **WHEN** every chore of a bolt has merged and the bolt holds no unit
- **THEN** its landing row is offered with no batch due

### Requirement: A proposal carries chores the user takes row by row
A proposal SHALL hold the chore commands as it holds the unit commands. `crew plan proposed` SHALL show a chore's add as "New chore `<name>`" with its words. Its card SHALL count a chore new to a bolt among what the user can leave out, and `crew plan approve <n> --clear <chore>` SHALL leave it out as a unit is left out.

#### Scenario: A batch of chores
- **WHEN** the planner proposes `bolt new upkeep …` and three `chore add … --bolt upkeep`, and the user clears one on the card
- **THEN** the approval adds the bolt and the two chores the user kept, and the proposal records the third as cleared

### Requirement: A chore shows as a chore
`crew bolts`, its JSON, the board and the page SHALL show a chore among the units of its bolt or queue in build order, marked as a chore. The run record SHALL name it `chore/<name>`, its writes `chore.add`, `chore.order`, `chore.after`, `chore.move` and `chore.drop`, and `crew trace <bare name>` SHALL try a unit, then a chore, then a bolt, then a signal.

#### Scenario: A trace by a chore's name
- **WHEN** `crew trace bump-biome` runs for a chore whose add and stages the run record holds, from before teams left or since
- **THEN** it prints the chore's add and each entry on it, as written

### Requirement: Chores are written by the planner, the design agent and the user
The planner SHALL write a chore only by proposal, the design agent only `chore add --repo`, and the user any. No other agent SHALL write a chore.

#### Scenario: An agent outside the role table orders a chore
- **WHEN** an agent that is not the planner, the design agent or the user runs `crew chore order bump-biome --first`
- **THEN** it is refused, naming who may write a chore, and the plan is unchanged

#### Scenario: The design agent queues a chore
- **WHEN** the design agent runs `crew chore add archive-x "Archive change x" --repo crew`
- **THEN** the chore is queued in crew's queue, with no proposal

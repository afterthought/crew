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

### Requirement: Chores are written by a unit's hands
The planner SHALL write a chore only by proposal, a conductor only `chore order` and `chore after` within the bolt its team holds, the design agent only `chore add --repo`, and the user any.

#### Scenario: A conductor orders a chore of its bolt
- **WHEN** swb-1's conductor runs `crew chore order bump-biome --first` for a chore of the bolt swb-1 holds
- **THEN** the chore is first in the bolt, and the run record has `chore.order` on `chore/bump-biome`

#### Scenario: The design agent queues a chore
- **WHEN** the design agent runs `crew chore add archive-x "Archive change x" --repo crew`
- **THEN** the chore is queued in crew's queue, with no proposal

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
A unit or chore SHALL be `ready` once each `After` has something committed to build on, a unit's change once its construct has finished or a chore's code once its commits are in its place, and `waiting` until then, never waiting on a merge; its new place SHALL take the head of each unmerged one as it stands, recorded on its start as `Took`, and it SHALL merge only after each has merged. When one merges, the dependent's place SHALL be rebased onto the bolt.

#### Scenario: A unit after a chore
- **WHEN** unit `b` has `After: bump-biome`, and the chore's code has not yet committed
- **THEN** `b` is `waiting`, and its construct is refused naming the chore's code

#### Scenario: The chore's code has delivered
- **WHEN** the chore's code has committed in its place and the conductor runs `crew unit run b construct`
- **THEN** `b`'s construct starts, its place holds the chore's work, and its start records `Took: bump-biome@<head>`

#### Scenario: The chore merges
- **WHEN** the chore merges into the bolt
- **THEN** `b`'s place is rebased onto the bolt, leaving out the chore's work as it took it

### Requirement: A chore is built by code, verify and merge
`crew chore run <chore> code|verify|merge ["<words>"]` SHALL start the stage in a slot of the team holding the chore's bolt, a fresh agent at that stage's effort, on `chore/<name>` branched from the bolt in `<kit>/places/chore-<name>`, made at its first code. Code SHALL be sent `Chore <name>: <its words>`, verify `Verify chore <name>: <its words>`, merge the unit's merge prompt, each followed by any words given.

#### Scenario: Code
- **WHEN** the conductor runs `crew chore run bump-biome code` for a ready chore
- **THEN** a free slot holds it, its place is made from the bolt on `chore/bump-biome`, and the fresh agent is sent `Chore bump-biome: Biome follows the shell's version`

### Requirement: A chore's stage starts only when it may
crew SHALL refuse a chore's code while an `After` has nothing committed to build on, any stage of a merged or landed chore, verify before its place holds a commit of its own beyond the bolt, and merge before a verify has delivered since its last code began, while a commit of its own lacks the `Chore: <name>` trailer, naming that commit, or while an `After` has not merged. A chore has no construct and no settle: `crew unit run` naming a chore SHALL be refused, naming its kind.

#### Scenario: Construct on a chore
- **WHEN** someone runs `crew unit run bump-biome construct`
- **THEN** it is refused: bump-biome is a chore, which has no construct

#### Scenario: A commit without the trailer
- **WHEN** the conductor runs `crew chore run bump-biome merge` and one commit beyond the bolt lacks `Chore: bump-biome`
- **THEN** the merge is refused, naming that commit

### Requirement: A chore's stage ends at its deliverable
A chore's code SHALL end at a commit on its branch made since the stage began, its verify at a report for it saved since then, and its merge at its bolt holding a commit carrying its trailer, or at its agent saying what it needs; `crew chore wait <chore>` SHALL wait on it as `crew unit wait` waits on a unit's. Its end SHALL be recorded on `stage/<chore>/<stage>` and `chore/<name>`.

#### Scenario: Code delivered
- **WHEN** the chore's coder commits on `chore/bump-biome` and goes idle
- **THEN** `crew chore wait bump-biome` answers that it delivered its branch's head

### Requirement: A chore is never constructed or reviewed
No batch SHALL hold a chore, the planner SHALL never be told a batch is due for one, and a bolt's landing SHALL never wait on a batch for one. A chore's verify report SHALL be a rail row keyed `verify/<chore>/<stamp>`, whose card is its conductor's.

#### Scenario: A bolt of chores
- **WHEN** every chore of a bolt has merged and the bolt holds no unit
- **THEN** its landing row is offered with no batch due

### Requirement: A chore's slot and place go when its work is over
A slot holding a chore SHALL be freed once the chore has merged, landed, been dropped or left the team's bolt, and its agent is not working. Its place SHALL be removed through the kit's own worktree tool once its work is over, as every worktree crew made is.

#### Scenario: A merged chore
- **WHEN** a chore's merge has delivered and the team is next read
- **THEN** its slot is free and `places/chore-<name>` is gone

### Requirement: A proposal carries chores the user takes row by row
A proposal SHALL hold the chore commands as it holds the unit commands. `crew plan proposed` SHALL show a chore's add as "New chore `<name>`" with its words. Its card SHALL count a chore new to a bolt among what the user can leave out, and `crew plan approve <n> --clear <chore>` SHALL leave it out as a unit is left out.

#### Scenario: A batch of chores
- **WHEN** the planner proposes `bolt new upkeep …` and three `chore add … --bolt upkeep`, and the user clears one on the card
- **THEN** the approval adds the bolt and the two chores the user kept, and the proposal records the third as cleared

### Requirement: A chore shows as a chore
`crew bolts`, its JSON, the board and the page SHALL show a chore among the units of its bolt or queue in build order, marked as a chore. The run record SHALL name it `chore/<name>`, its writes `chore.add`, `chore.order`, `chore.after`, `chore.move` and `chore.drop`, and `crew trace <bare name>` SHALL try a unit, then a chore, then a bolt, then a signal.

#### Scenario: A trace by a chore's name
- **WHEN** `crew trace bump-biome` runs for a chore that has merged
- **THEN** it prints the chore's add, each stage's start and end, and its slot's freeing

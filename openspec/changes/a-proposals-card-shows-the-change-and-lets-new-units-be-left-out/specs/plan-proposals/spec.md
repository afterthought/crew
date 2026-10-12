## MODIFIED Requirements

### Requirement: Approval applies a proposal exactly as it was read
`crew plan approve <n>` SHALL apply the proposal's commands in order to the plan at the branch's tip and close the proposal as `approved`, in one commit. When any command would now be refused, the approval SHALL be refused, naming the command and the reason, and the plan and the proposal SHALL be unchanged. What follows a direct command (a rebased unit, a freed slot, a conductor told) SHALL follow the approval. `crew plan approve <n> --clear <unit>...` SHALL apply the commands the user kept: each cleared unit SHALL be one the proposal adds or moves into a bolt, every command that names only cleared units SHALL be left out, and when a command left in names a cleared unit the approval SHALL be refused, naming that command and the unit, with nothing changed. The approved proposal SHALL record each cleared unit.

#### Scenario: A proposal is approved
- **WHEN** the user approves proposal N, which creates a bolt and adds a unit to it
- **THEN** one commit adds the bolt and the unit and marks the proposal approved, and no reader sees the bolt without the unit

#### Scenario: The plan moved since
- **WHEN** a unit the proposal moves was dropped after the proposal was written
- **THEN** the approval is refused, naming that command, and the proposal stays open

#### Scenario: A unit with a worktree is moved
- **WHEN** an approved proposal moves a unit in construct to another bolt in the same checkout and the rebase conflicts
- **THEN** the rebase is undone, the approval is refused, and the plan and the proposal are unchanged

#### Scenario: A unit from a signal
- **WHEN** an approved proposal holds `unit add … --signal <id>`
- **THEN** the same commit adds the unit and the signal's `route` move

#### Scenario: A new unit left out
- **WHEN** proposal N drops `a`, adds `b` and `c` to bolt `y`, and orders `c` first, and the user approves it with `c` cleared
- **THEN** one commit drops `a`, adds `b`, makes no unit `c`, runs no order of `c`, marks the proposal approved and records `c` as cleared

#### Scenario: A unit moved in from the queue left out
- **WHEN** proposal N moves queued unit `q` into bolt `y` and the user clears `q`
- **THEN** the approval applies the rest, and `q` stays in the queue as it was

#### Scenario: A kept command names a cleared unit
- **WHEN** proposal N adds `b` and `c` to bolt `y`, `c` with `--after b`, and the user clears `b` and keeps `c`
- **THEN** the approval is refused, naming the `unit add c` command and `b`, the plan and the proposal are unchanged, and the planner writes the proposal again without `b`

#### Scenario: A unit that is not new is cleared
- **WHEN** `crew plan approve N --clear a` names a unit proposal N only amends
- **THEN** the approval is refused, naming `a` and the units the proposal adds or moves in, and nothing changes

## ADDED Requirements

### Requirement: A proposal's card is drawn from the plan and the proposal
`crew plan card <n> [--label L]` SHALL read only the flywheel's branch and print, as JSON, every part of proposal n's card: its title with the counts, its summary, its background, its questions and its artifacts. It SHALL write the card's picture, a PNG 780 pixels wide, on the host it runs on, and print where. It SHALL draw the picture and the text itself, with no browser, no other program and no agent, and SHALL write nothing to the branch or the run record.

#### Scenario: A proposal that drops, amends and adds
- **WHEN** `crew plan card N` runs for a proposal that drops one unit of bolt `y`, amends one and adds two
- **THEN** it prints a title ending "1 dropped, 1 amended, 2 new?", a summary naming the unit count before and after and `y`'s goal, and writes a PNG 780 pixels wide

#### Scenario: Run on a host with no browser
- **WHEN** `crew plan card N` runs on a host where no browser and no image tool is installed
- **THEN** it writes the picture all the same

#### Scenario: A closed proposal
- **WHEN** `crew plan card N` runs for a proposal that is approved or dropped
- **THEN** it is refused, saying the proposal is closed

### Requirement: The picture shows each bolt once approved
The picture SHALL show, for each bolt the proposal touches, its units in the order they would hold once approved, numbered; each dropped unit struck where it stood, with its reason; each amended unit's intent as it stands struck above its new intent; each unit new to the bolt marked new; each unit moved out struck with the bolt it goes to; and each reordered unit marked moved. A unit added to or moved to the queue SHALL be shown under its kit's queue.

#### Scenario: A drop and an amendment
- **WHEN** the picture is drawn for a proposal that drops `a` from bolt `y` and amends `b`
- **THEN** `a` stands unnumbered where it stood, struck, with its reason; `b` shows its old intent struck above the new one

#### Scenario: A move between bolts
- **WHEN** the picture is drawn for a proposal that moves `m` from bolt `x` into bolt `y`
- **THEN** `x`'s section shows `m` struck, saying it goes to `y`, and `y`'s shows `m` marked new

### Requirement: The change reads as text on a phone
The card's text artifact SHALL be the change in monospace lines of at most forty characters: the bolt and its unit count before and after, then one block per change headed by its kind (`DROP`, `AMEND`, `ADD`, `MOVE`, `ORDER`, `SPLIT`, `AFTER`, `NEW BOLT`, `ORDER BOLT`, `DROP BOLT`) with the unit or bolt and what it says, then the order once approved with each unit marked new (`+`), amended (`~`) or moved (`↕`). A name longer than a line SHALL wrap at its hyphens.

#### Scenario: The text of a proposal
- **WHEN** `crew plan card N` prints the card for a proposal that drops `a` with a reason and adds `c`
- **THEN** its text artifact holds a `DROP` block naming `a` with the reason, an `ADD` block naming `c` with its intent, and `ONCE APPROVED` listing `c` with `+`, and no line is longer than forty characters

### Requirement: The card's questions are the approval and the new units
When proposal n adds or moves into a bolt one to fifteen units, its card SHALL ask `plan`, approving it, its detail the case as bullets and its rationale how to object (not approving, and saying why in the note), then one `units-<k>` question per group of at most five new units, shared evenly, every unit recommended so it arrives ticked. A lone new unit SHALL be a choice of keeping it or leaving it out. No question SHALL ask for words.

#### Scenario: Seven new units
- **WHEN** `crew plan card N` runs for a proposal that adds seven units
- **THEN** the card has the question `plan` and two unit questions of four and three units, every unit recommended

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c`
- **THEN** the card's second question is a choice between keeping `c` and leaving it out, keeping `c` recommended

#### Scenario: How to object to a drop
- **WHEN** `crew plan card N` runs for a proposal that drops `a` and adds `c`
- **THEN** the rationale of `plan` says that to keep the dropped unit the user does not approve and says why in a note, and that a note beside an approval changes nothing applied

### Requirement: A card with no new unit, or more than fifteen, is a plain approval
When proposal n adds or moves into a bolt no unit, or more than fifteen, its card SHALL be a plain approval with no unit question, and the card of more than fifteen SHALL say it links the proposal's plannotator session.

#### Scenario: No new unit
- **WHEN** the proposal only drops and amends
- **THEN** the card is an approval with no question of units

#### Scenario: Sixteen new units
- **WHEN** the proposal adds sixteen units
- **THEN** the card is an approval with no question of units, and says it links the proposal's plannotator session

### Requirement: A card's answers are gathered before the approval
`crew plan answer <n> <question> <answer>...` SHALL record one question's answer for proposal n on the host it runs on: `plan` with `approve` or `decline`, and `units-<k>` with the units the user left ticked. Once it holds `plan`'s approval and every unit question's answer, it SHALL apply the approval with each unticked unit cleared, as `crew plan approve <n> --clear` would; until then it SHALL apply nothing and name the questions it waits on.

#### Scenario: A card the user split
- **WHEN** the user splits proposal N's card, approves on one split, and the planner runs `crew plan answer N plan approve`
- **THEN** nothing is applied and crew says it waits on `units-1`; when the planner then runs `crew plan answer N units-1 b` from the other split, the approval is applied with every other new unit cleared

#### Scenario: Declined
- **WHEN** the planner runs `crew plan answer N plan decline`
- **THEN** nothing is applied, the gathered answers are discarded, and crew says the user's note is theirs to act on, writing the proposal again or dropping it

### Requirement: An answer the card did not ask is refused
`crew plan answer` SHALL refuse a question the card does not ask, a unit its question does not hold, an answer that differs from one it already holds for that question, and a closed proposal, recording nothing.

#### Scenario: The same question answered twice
- **WHEN** `crew plan answer N units-1 b` runs after `crew plan answer N units-1 b c`
- **THEN** it is refused, naming the answer crew already holds

### Requirement: A note beside an approval goes to the planner after it
`crew plan answer <n> plan approve --note "<text>"` SHALL NOT hold the approval for the note. Once the approval is applied, crew SHALL print the note to the planner as the user's word, to propose whatever it asks as a new proposal.

#### Scenario: Approved with a note
- **WHEN** the user approves proposal N with the note "split b in two later" and the planner records it with `--note`
- **THEN** once every answer is in, the approval is applied, and crew prints "split b in two later" as the user's word for the planner's next proposal

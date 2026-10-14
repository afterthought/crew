## MODIFIED Requirements

### Requirement: A proposal is put before the user whole
`crew plan propose` SHALL, once a proposal is accepted into the plan, raise its card itself in the planner's name, keyed `proposal/<n>`, drawn from the plan and the proposal as record 0018 has it. Any agent that puts one of the planner's proposals before the user in a pane, the planner, a conductor or the operator agent, SHALL show what `crew plan proposed <n>` prints, in its own pane or opened beside it, and SHALL NOT name the proposal by its number alone; the number SHALL follow the words, as a reference. The agent SHALL ask for the user's answer in words, SHALL NOT recite a command for the user to answer with, and SHALL run the answering command only on the user's word.

#### Scenario: The planner proposes
- **WHEN** the planner has written proposal N and `crew plan propose` accepts it
- **THEN** its card is open, and when the user is in the planner's pane the planner shows what `crew plan proposed N` prints and asks them to approve it or say what to change

#### Scenario: The user asks what waits on them
- **WHEN** the operator agent answers where things stand and proposal N is open
- **THEN** its answer shows what `crew plan proposed N` prints, not only that proposal N is open

#### Scenario: The user says yes
- **WHEN** the user tells the agent showing proposal N to approve it
- **THEN** that agent runs `crew plan approve N`, which closes the card with what was applied

#### Scenario: A proposal with three new units
- **WHEN** the planner's proposal adding three units to a bolt is accepted as number 4
- **THEN** its card is open with the counts, the case, the change drawn and in text, an approval and a question listing the three units ticked

### Requirement: A proposal is dropped with a reason, or replaced
`crew plan drop <n> "<reason>"` SHALL close an open proposal as `dropped` with the reason, applying nothing, withdraw its chain's card with the reason, and tell the planner when someone else dropped it. `crew plan propose <file> --replaces <n>` SHALL drop proposal n and write its successor in one commit, the successor naming the one it replaces, and SHALL change the chain's card in place to the successor with the note "Rewritten as proposal <successor> after your note"; the chain's card SHALL stay keyed by its first proposal, and the rail's row for the successor SHALL carry it.

#### Scenario: The user rejects a proposal
- **WHEN** the user drops proposal N with a reason
- **THEN** the proposal is `dropped`, the plan is unchanged, its card is withdrawn with the reason, and the planner is told the reason

#### Scenario: The planner revises
- **WHEN** the planner proposes again with `--replaces N` after the user asked for a different placement
- **THEN** proposal N is `dropped`, proposal N+1 is `open` and names N, agreements given to N do not carry over, and the card keyed `proposal/N` shows N+1 with the change note

### Requirement: A proposal's card is drawn from the plan and the proposal
When crew raises or changes a proposal's card it SHALL read only the flywheel's branch and build every part of the card: its title with the counts, its summary, its background, its questions and its artifacts, and SHALL draw the card's picture, a PNG 780 pixels wide, itself, with no browser, no other program and no agent. There SHALL be no `crew plan card` command.

#### Scenario: A proposal that drops, amends and adds
- **WHEN** crew raises the card for a proposal that drops one unit of bolt `y`, amends one and adds two
- **THEN** its title ends "1 dropped, 1 amended, 2 new?", its summary names the unit count before and after and `y`'s goal, and its picture is a PNG 780 pixels wide

#### Scenario: Run on a host with no browser
- **WHEN** crew raises a proposal's card on a host where no browser and no image tool is installed
- **THEN** it draws the picture all the same

#### Scenario: A closed proposal
- **WHEN** a proposal is approved or dropped
- **THEN** its card is closed or withdrawn, and crew draws no card for it again

### Requirement: The change reads as text on a phone
The card's text artifact SHALL be the change in monospace lines of at most forty characters: the bolt and its unit count before and after, then one block per change headed by its kind (`DROP`, `AMEND`, `ADD`, `MOVE`, `ORDER`, `SPLIT`, `AFTER`, `NEW BOLT`, `ORDER BOLT`, `DROP BOLT`) with the unit or bolt and what it says, then the order once approved with each unit marked new (`+`), amended (`~`) or moved (`↕`). A name longer than a line SHALL wrap at its hyphens.

#### Scenario: The text of a proposal
- **WHEN** crew raises the card for a proposal that drops `a` with a reason and adds `c`
- **THEN** its text artifact holds a `DROP` block naming `a` with the reason, an `ADD` block naming `c` with its intent, and `ONCE APPROVED` listing `c` with `+`, and no line is longer than forty characters

### Requirement: The card's questions are the approval and the new units
When proposal n adds or moves into a bolt one to fifteen units or chores, its card SHALL ask `plan`, approving it, its detail the case as bullets and its rationale how to object (not approving, and saying why in the note), then one `units-<k>` question per group of at most five new units or chores, shared evenly, every one recommended so it arrives ticked. A lone new unit SHALL be a choice of keeping it or leaving it out. No question SHALL ask for words.

#### Scenario: Seven new units
- **WHEN** crew raises the card for a proposal that adds seven units
- **THEN** the card has the question `plan` and two unit questions of four and three units, every unit recommended

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c`
- **THEN** the card's second question is a choice between keeping `c` and leaving it out, keeping `c` recommended

#### Scenario: How to object to a drop
- **WHEN** crew raises the card for a proposal that drops `a` and adds `c`
- **THEN** the rationale of `plan` says that to keep the dropped unit the user does not approve and says why in a note, and that a note beside an approval changes nothing applied

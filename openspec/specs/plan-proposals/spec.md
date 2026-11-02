# plan-proposals Specification

## Purpose
Makes every change the planner would make to a flywheel's plan a proposal the user reads and approves before it takes effect, with the agreement of any conductor whose bolt it touches, so that where work goes is the user's decision and what was approved is exactly what is applied.

## Requirements

### Requirement: The planner changes the plan only by a proposal
A command that would write the plan, run by a partition's planner, SHALL be refused with a message naming `crew plan propose`. The planner SHALL change the plan only by writing a proposal, which changes nothing until it is approved.

#### Scenario: The planner adds a unit directly
- **WHEN** `wldn-planner` runs `crew unit add <unit> "<intent>" --repo switchboard-kit`
- **THEN** it is refused, the plan is unchanged, and the message names `crew plan propose`

#### Scenario: The planner creates a bolt directly
- **WHEN** `wldn-planner` runs `crew bolt new <bolt> "<goal>" --repo switchboard-kit`
- **THEN** it is refused in the same way

### Requirement: Other agents write the plan only within their own job
A conductor SHALL write directly only `crew unit split`, `crew unit order`, `crew unit after`, `crew chore order` and `crew chore after`, and only on units and chores of the bolt its team holds. The design agent SHALL write directly only `crew unit add` and `crew chore add` into a kit's queue. A dispatcher's `crew bolt give` and the main-level ops' `crew bolt land` SHALL stay direct. Any other plan write by an agent crew started SHALL be refused, naming the planner. The user at a shell SHALL write the plan directly.

#### Scenario: A conductor narrows a unit of its bolt
- **WHEN** swb-2's conductor runs `crew unit split` on a unit of the bolt swb-2 holds
- **THEN** the split is written, with no proposal

#### Scenario: A conductor adds a unit to its bolt
- **WHEN** swb-2's conductor runs `crew unit add <unit> "<intent>" --bolt <its bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: A conductor adds a chore to its bolt
- **WHEN** swb-2's conductor runs `crew chore add <chore> "<words>" --bolt <its bolt>`
- **THEN** it is refused, and the message says to tell the planner

#### Scenario: The design agent queues a unit
- **WHEN** the design agent runs `crew unit add <unit> "<intent>" --repo <kit>`
- **THEN** the unit is queued, with no proposal

#### Scenario: The user at a shell
- **WHEN** the user runs `crew bolt new` in a terminal
- **THEN** the bolt is written, with no proposal

### Requirement: A proposal is a case and the commands it would run
`crew plan propose <file>` SHALL write one Proposal record to `proposals.rec` on the flywheel's branch: its number, the planner's case, the plan commands it would run in order, who wrote it and when, and its state, `open`. The commands SHALL be among `bolt new`, `bolt order`, `bolt drop`, `unit add`, `unit amend`, `unit move`, `unit split`, `unit order`, `unit after`, `unit drop`, `chore add`, `chore move`, `chore order`, `chore after` and `chore drop`. A number SHALL be given once and never reused, and a proposal SHALL never be removed or its commands changed.

#### Scenario: A new bolt with two units
- **WHEN** the planner proposes `bolt new cfn-checks …`, `unit add cfn-nag-security-check … --bolt cfn-checks` and `unit move retire-suite-cfn-lint cfn-checks`, with its case
- **THEN** proposal N holds the case and those three commands in that order, in state `open`, and the plan is unchanged

#### Scenario: A command a proposal cannot hold
- **WHEN** a proposal file holds `bolt give swb-1`
- **THEN** the proposal is refused, naming the command, and nothing is written

#### Scenario: Someone other than the planner
- **WHEN** a conductor runs `crew plan propose`
- **THEN** it is refused; only the partition's planner and the user write proposals

#### Scenario: An amendment to a unit in flight
- **WHEN** the planner proposes `unit amend <unit> "<new intent>"` for a unit in code in a bolt a team holds
- **THEN** the proposal is written, the unit's intent is unchanged, and that bolt's conductor is told

#### Scenario: A chore's words changed
- **WHEN** the planner proposes `chore drop bump-biome "…"` then `chore add bump-biome "<new words>" --bolt tooling`
- **THEN** the proposal is written; a chore has no amendment, so its words change by a drop and an add

### Requirement: A proposal is checked when it is written
Before a proposal is written, each of its commands SHALL be applied in order to a copy of the plan at the branch's tip, and SHALL pass every refusal and rule that command has when run directly. A proposal with a command that would be refused SHALL be refused, naming the command and the reason, and nothing SHALL be written.

#### Scenario: A later command depends on an earlier one
- **WHEN** a proposal creates a bolt and then adds a unit to that bolt
- **THEN** it passes, because the unit is checked against the plan as the first command leaves it

#### Scenario: A unit name the kit already has
- **WHEN** a proposal adds a unit whose name the kit's main already has as a change
- **THEN** the proposal is refused, naming that command and the name

#### Scenario: Moving merged work
- **WHEN** a proposal moves a unit that has merged into its bolt
- **THEN** the proposal is refused, as the move would be

### Requirement: A proposal is read as the user would read it
`crew plan proposed` SHALL list the open proposals from any host, each with its number, who wrote it, when, the first line of its case and what it waits on. `crew plan proposed <n>` SHALL print the case and then each change in plain words: a new unit's intent beside the sources it rests on and the goal of the bolt it would join, a move's bolts with their goals, a new bolt's goal, a drop's reason. Under each change's plain words it SHALL print the command approval will run for that change, so the sequence of adds, moves and drops reads as the plan commands it is. For an open proposal it SHALL then name, in words, each conductor whose agreement it still waits on, the conductors that have agreed, and the user, without the commands that answer it. `--json` SHALL give the same.

#### Scenario: A unit for an existing bolt
- **WHEN** proposal N adds a unit to a bolt a team holds
- **THEN** `crew plan proposed N` shows the unit's intent, the bolt's goal beside it, and that the bolt's conductor has not yet agreed

#### Scenario: Each change shows its command
- **WHEN** proposal N creates a bolt, adds a unit to it and moves a queued unit into it
- **THEN** `crew plan proposed N` prints under each of the three changes, in order, the `crew` command approval will run for it

#### Scenario: Waiting on, in words
- **WHEN** proposal N is open and waits on a conductor and the user
- **THEN** `crew plan proposed N` names both and what each would do, and prints no `crew plan agree`, `crew plan approve` or `crew plan drop` command

#### Scenario: Nothing open
- **WHEN** no proposal is open
- **THEN** `crew plan proposed` says so

### Requirement: A bolt in flight is changed only with its conductor's agreement
When a proposal is written, crew SHALL tell the conductor of each bolt a team holds that the proposal touches, with the commands that touch it. `crew plan agree <n>`, run by that conductor, SHALL record the team's agreement on the proposal. Approval SHALL be refused while any touched bolt held by a team has no recorded agreement, naming the conductor.

#### Scenario: The conductor agrees
- **WHEN** swb-2's conductor runs `crew plan agree 4` for a proposal that adds a unit to its bolt
- **THEN** the proposal records swb-2's agreement, and the planner is told

#### Scenario: Approval before agreement
- **WHEN** `crew plan approve 4` runs while swb-2 has not agreed
- **THEN** it is refused, naming `swb-2-conductor`, and nothing changes

#### Scenario: A conductor whose bolt is not touched
- **WHEN** swb-1's conductor runs `crew plan agree 4` and the proposal touches no bolt swb-1 holds
- **THEN** it is refused

#### Scenario: A bolt given after the proposal was written
- **WHEN** a planned bolt the proposal touches is given to a team before approval
- **THEN** approval is refused until that team's conductor has agreed

### Requirement: Work a bolt in flight needs to land goes into that bolt
Landing SHALL be part of every bolt's goal. A unit that a bolt held by a team needs before it can be proven or land SHALL be proposed into that bolt, ordered ahead of the units that wait on it, and marked with the bolt it unblocks (`--unblocks <bolt>` on the `crew unit add` or `crew unit move` the proposal runs). crew SHALL refuse a proposal that marks a unit as unblocking a held bolt but places it in the queue or in another bolt. `crew plan proposed <n>` SHALL show the mark beside the unit. The planner's and the conductor's briefs SHALL say this, and a dispatcher given a planned bolt whose units only serve a bolt a team already holds SHALL tell the planner to fold them into the held bolt instead of waiting for a free team.

#### Scenario: A conductor's bolt can't land without new work
- **WHEN** swb-1's conductor tells the planner its bolt can't land until two pins agree
- **THEN** the planner's proposal adds the unit to swb-1's bolt, ahead of the units waiting on it, marked as unblocking that bolt, and the user reads the mark on the proposal

#### Scenario: Unblocking work placed elsewhere
- **WHEN** a proposal marks a unit `--unblocks biome-follows-the-shell` but adds it to the queue or to a new bolt
- **THEN** writing the proposal is refused, naming the held bolt

#### Scenario: A new bolt that only serves a held bolt
- **WHEN** the dispatcher is told of a new bolt whose units only finish a bolt swb-1 holds
- **THEN** it does not give the new bolt to a team, and tells the planner to move its units into swb-1's bolt

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

### Requirement: Only the user approves
`crew plan approve` SHALL be run by the user, or by an agent on the user's word in that agent's pane. An agent SHALL NOT approve a proposal on its own judgment. The run record SHALL show who ran the approval and in which session.

#### Scenario: The user says yes to the planner
- **WHEN** the user reads proposal N in the planner's pane and says to go ahead
- **THEN** the planner runs `crew plan approve N`, and the entry names the planner and its session, where the user's words are

#### Scenario: Nobody has said yes
- **WHEN** a proposal is open and the user has said nothing about it
- **THEN** no agent approves it, and it is listed as waiting on the user

### Requirement: A proposal is dropped with a reason, or replaced
`crew plan drop <n> "<reason>"` SHALL close an open proposal as `dropped` with the reason, applying nothing, withdraw its chain's card with the reason, and tell the planner when someone else dropped it. `crew plan propose <file> --replaces <n>` SHALL drop proposal n and write its successor in one commit, the successor naming the one it replaces, and SHALL change the chain's card to the successor with the note "Rewritten as proposal <successor> after your note", in place while it waits on the user, and once the user's note answered it as a new version following the card they answered; a card that asks its rows as questions, its rows filling more than one list, or whose form the successor changes, a hold-to-approve, a choice, one list or lists, SHALL be withdrawn with the note while it waits and the successor's posted following it, since Pending You changes no card's questions or kind in place; the chain's card SHALL stay keyed by its first proposal, and the rail's row for the successor SHALL carry it.

#### Scenario: The user rejects a proposal
- **WHEN** the user drops proposal N with a reason
- **THEN** the proposal is `dropped`, the plan is unchanged, its card is withdrawn with the reason, and the planner is told the reason

#### Scenario: The planner revises
- **WHEN** the planner proposes again with `--replaces N` after the user asked for a different placement
- **THEN** proposal N is `dropped`, proposal N+1 is `open` and names N, agreements given to N do not carry over, and the card keyed `proposal/N` shows N+1 with the change note

### Requirement: Each step of a proposal is in the run record
Writing, agreeing, approving and dropping a proposal SHALL each leave a run-record entry naming `proposal/<n>` and the bolts and units its commands name. Each change an approval applies SHALL leave its own entry, with the proposal as what it came from and the approval's commit.

#### Scenario: Tracing a unit
- **WHEN** `crew trace unit/<unit>` runs for a unit an approved proposal added
- **THEN** it shows the proposal written, any agreement, the approval, and the unit's add, in order

### Requirement: An amendment is read as before and after
For a `unit amend` command, `crew plan proposed <n>` SHALL show the unit's intent as it stands and as it would be, the unit's bolt, team and stage, and what approval sets in motion: for a unit with a worktree, that the approval itself runs construct again on its team's host and the unit goes on from its tasks once that construct has committed, its revised change due for the next batch, with no approval asked.

#### Scenario: An amendment to a unit in code
- **WHEN** proposal N amends the intent of a unit in code in the bolt swb-2 holds
- **THEN** its page shows both intents, that the unit is in code under swb-2, that swb-2's conductor has or has not agreed, and that on approval construct runs again at once on swb-2's host and the unit then goes on from its tasks, its revised change in the next batch

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
- **THEN** its card is open, titled "Plan change to <bolt>: 3 new", with the case, the change drawn and in text, a paragraph per unit, and one list of the three units ticked

### Requirement: A proposal can be opened in plannotator
`crew plan proposed <n> [--label L] --open` SHALL write the proposal, exactly as `crew plan proposed <n>` prints it, to a file on the host it runs on, and open that file in plannotator for the user to read and annotate: beside the caller with `plannotator-tui herdr open` when it runs in herdr, inline with `plannotator-tui` otherwise. It SHALL read only the flywheel's branch, so it works from any host. It SHALL write nothing to the branch or the run record. `--open` SHALL be refused without `<n>` and with `--json`.

#### Scenario: Opened from the rail's shell
- **WHEN** the user runs `crew plan proposed 3 --label wldn --open` in a herdr pane
- **THEN** plannotator opens beside it with the same text `crew plan proposed 3 --label wldn` prints

#### Scenario: Without a number
- **WHEN** `crew plan proposed --open` is run
- **THEN** it is refused, saying `--open` needs a proposal's number

### Requirement: A proposal's card is drawn from the plan and the proposal
When crew raises or changes a proposal's card it SHALL read only the flywheel's branch and build every part of the card: its title "Plan change to <bolt or queue>: <counts>", no question and no proposal number; its summary, a sentence of what the planner proposes and why from the case; a paragraph per new unit and per dropped unit as inline Markdown on its face, the intent and a "Direction" line from the proposal's `Do` line and case, a dropped unit's with its why; its background; its boxes and its artifacts; and SHALL draw the card's picture, a PNG 1560 pixels wide at twice a phone's pixel density so it is sharp on a Retina screen, itself, with no browser, no other program and no agent.

#### Scenario: A proposal that drops, amends and adds
- **WHEN** crew raises the card for a proposal that drops one unit of bolt `y`, amends one and adds two
- **THEN** its title is "Plan change to y: 1 dropped, 1 amended, 2 new", its summary says what the planner proposes in a sentence, its face holds a paragraph for each new unit and the dropped one, and its picture is a PNG 1560 pixels wide

#### Scenario: Run on a host with no browser
- **WHEN** crew raises a proposal's card on a host where no browser and no image tool is installed
- **THEN** it draws the picture all the same

#### Scenario: A closed proposal
- **WHEN** a proposal is approved or dropped
- **THEN** its card is closed or withdrawn, and crew draws no card for it again

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
- **WHEN** crew raises the card for a proposal that drops `a` with a reason and adds `c`
- **THEN** its text artifact holds a `DROP` block naming `a` with the reason, an `ADD` block naming `c` with its intent, and `ONCE APPROVED` listing `c` with `+`, and no line is longer than forty characters

### Requirement: The card's questions are the approval and the new units
When proposal n makes units or chores new to a bolt or to a kit's queue, its card SHALL ask only those: one `multi` list and nothing else to tap, a box per new unit or chore, ticked, each with its intent as its detail and what clearing it does as its consequence; its intent SHALL be `decide`. What else the proposal changes, a drop, an amendment, a move, an order or a new bolt, SHALL be drawn on the card's face, its picture and its text and SHALL apply with it, and SHALL NOT be a box, and the card's summary SHALL say so. Send SHALL apply the change with the boxes as they stand, a new unit cleared left out, and the planner told which. A proposal of one new unit or chore SHALL be the choice of adding it or leaving it out instead, adding it recommended, since a Pending You list holds two at least. No approve block SHALL sit inside the card and no question SHALL ask for words. A proposal of more than five new units or chores SHALL be grouped into `questions` of at most five boxes each, in the plan's order.

#### Scenario: One dropped, three new
- **WHEN** crew raises the card for a proposal that drops `a` and adds `b`, `c` and `d`
- **THEN** the card is one list of three boxes, `b`, `c` and `d`, every one ticked, with no box for `a`; its face holds a paragraph for `a`'s drop; and sending it as it stands applies the proposal whole, `a` dropped

#### Scenario: How to object to a drop
- **WHEN** the card of a proposal that drops `a` and adds `b`, `c` and `d` is raised
- **THEN** its summary says that what it drops or amends applies with it, and no box on it keeps `a`

#### Scenario: A move alone
- **WHEN** the proposal moves bolt `y` first and changes no unit
- **THEN** the card is a hold-to-approve of risk low

#### Scenario: A new unit left out beside an amendment
- **WHEN** the proposal amends `x` and adds `b` and `c`, and the user clears `c` and sends
- **THEN** `x`'s amendment and `b` are applied, `c` is left out, and the planner is told `c` was left out

#### Scenario: One new unit
- **WHEN** the proposal adds one unit `c` and nothing else
- **THEN** the card is the choice of adding `c` or leaving it out, adding `c` recommended, and Send applies the side picked

#### Scenario: One new unit beside a drop
- **WHEN** the proposal drops `a` and adds `c`
- **THEN** the card is the choice of adding `c` or leaving it out, and `a`'s drop applies whichever side is sent

#### Scenario: Seven new units
- **WHEN** crew raises the card for a proposal that adds seven units
- **THEN** the card has two questions of four and three boxes, every one ticked

### Requirement: A card with no new unit, or more than fifteen, is a plain approval
When proposal n makes no unit or chore new to a bolt or the queue, whether it drops, amends, moves or orders units or makes or orders bolts, alone or in any mix, or when it makes more than fifteen new, its card SHALL be a hold-to-approve of low risk, reversible, with no boxes and its change drawn on its face, its picture and its text. Approving it SHALL apply it whole; declining it SHALL apply nothing. The card of a proposal that drops or amends SHALL say that declining with a note keeps what it drops or amends. The card of more than fifteen SHALL say it links the proposal's plannotator session.

#### Scenario: Drops alone
- **WHEN** the proposal drops `a`, `b` and `c` and nothing else
- **THEN** the card is a hold-to-approve with no boxes, its face holds a paragraph for each dropped unit with its why, its summary says declining with a note keeps what it drops, and approving it drops all three

#### Scenario: Drops with an amendment and an order
- **WHEN** the proposal drops `a`, amends `x` and orders `d` first
- **THEN** the card is a hold-to-approve with no boxes, and approving it applies all three

#### Scenario: Keeping a dropped unit
- **WHEN** the user declines a drops-alone card with the note "keep b", and the planner runs `crew plan answer N plan decline --note "keep b"`
- **THEN** nothing is applied, and crew says the user's note is the planner's to act on, writing the proposal again or dropping it

#### Scenario: No new unit
- **WHEN** the proposal only orders a unit first
- **THEN** the card is a hold-to-approve with no boxes, and approving it applies it whole

#### Scenario: Sixteen new units
- **WHEN** the proposal adds sixteen units
- **THEN** the card is a hold-to-approve with no boxes, and says it links the proposal's plannotator session

### Requirement: A card's answers are gathered before the approval
`crew plan answer <n> <question> <answer>...` SHALL record one question's answer of open proposal n's card on the host it runs on, checked against the card crew builds for the proposal: `rows-<k>` with the ids of the boxes the user left ticked, `rows-1` for a card of one list, and for a lone new unit the side picked; or, for a hold-to-approve, `plan` with `approve` or `decline`. Once it holds every question's answer, it SHALL apply the change with the boxes as they stand, each new unit unticked cleared as `crew plan approve <n> --clear` clears it, the approved proposal recording each of those units as cleared, and crew SHALL close the card with what was applied; until then it SHALL apply nothing and name the questions it waits on.

#### Scenario: A card the user split
- **WHEN** proposal N adds seven units, the user sends the card's first list, and the planner runs `crew plan answer N rows-1` with its four boxes
- **THEN** nothing is applied and crew says it waits on `rows-2`; when the planner then runs `crew plan answer N rows-2` with two of its three boxes, the change is applied with the third unit left out

#### Scenario: Declined
- **WHEN** the planner runs `crew plan answer N plan decline` for a hold-to-approve
- **THEN** nothing is applied, the gathered answers are discarded, and crew says the user's note is theirs to act on, writing the proposal again or dropping it

#### Scenario: A box the card no longer asks
- **WHEN** the planner runs `crew plan answer N rows-1 keep:a add:b` for a proposal that drops `a` and adds `b` and `c`
- **THEN** it is refused, naming the boxes `rows-1` holds, `add:b` or `add:c`, and nothing is recorded

### Requirement: An answer the card did not ask is refused
`crew plan answer` SHALL refuse a question the card does not ask, a box its question does not hold, a lone row answered with other than one of its two sides, an answer that differs from one it already holds for that question, and a closed proposal, recording nothing.

#### Scenario: The same question answered twice
- **WHEN** `crew plan answer N rows-1 add:b` runs after `crew plan answer N rows-1 add:b add:c`
- **THEN** it is refused, naming the answer crew already holds

### Requirement: A note beside an approval goes to the planner after it
`crew plan answer <n> <question> <answer>... --note "<text>"` SHALL NOT hold the change for the note. Once the change is applied, crew SHALL print the note to the planner as the user's word, to propose whatever it asks as a new proposal.

#### Scenario: Approved with a note
- **WHEN** the user sends proposal N's boxes with the note "split b in two later" and the planner records them with `--note`
- **THEN** once every answer is in, the change is applied, and crew prints "split b in two later" as the user's word for the planner's next proposal

### Requirement: A proposal's card has no command of its own
There SHALL be no `crew plan card` command: a proposal's card is crew's, raised by `crew plan propose`.

#### Scenario: The command asked for
- **WHEN** an agent runs `crew plan card 4`
- **THEN** crew says it has no such command, and proposal 4's card is the one `crew plan propose` raised when the proposal was accepted

### Requirement: A proposal rests only on accepted records
Before a proposal is written, crew SHALL read every decision record named as a source by each bolt the proposal creates and each unit or chore it makes new to a bolt or the queue (one it adds, or moves into a bolt). Each record SHALL be read on its kit's main as GitHub holds it now. When any is not accepted there, the proposal SHALL be refused, naming each such unit or bolt, the record's number and kit, and what main holds, and nothing SHALL be written and no card raised.

#### Scenario: A unit names a proposed record
- **WHEN** the planner proposes `bolt new a-team-of-one-slot-lands-its-bolt … --repo crew` and `unit add a-bolts-unblocker-is-built-whatever-slots-its-team-has … --bolt a-team-of-one-slot-lands-its-bolt --source docs/adr/0033-a-unit-waiting-to-merge-yields-its-slot-to-the-work-it-waits-on.md`, and crew's main holds record 0033 with `status: proposed`
- **THEN** the proposal is refused, naming that unit, record 0033 of crew and that main holds it proposed; no proposal is written and no card is raised

#### Scenario: A record the user rejected
- **WHEN** a new unit's source names a record its kit's main holds with `status: rejected`
- **THEN** the proposal is refused, naming the record and that main holds it rejected

#### Scenario: An accepted record with an amendment still proposed
- **WHEN** a new unit's source names a record whose file on main says `status: accepted` and holds an amendment marked "Status: proposed"
- **THEN** the proposal is refused, naming the record and that main holds it accepted with an amendment still marked proposed

#### Scenario: A record main does not hold yet
- **WHEN** a new unit's source names `docs/adr/0040`, and its kit's main has no file numbered 0040 in `docs/adr/`
- **THEN** the proposal is refused, naming record 0040 and that main holds no such record

#### Scenario: A new bolt's source
- **WHEN** a proposal's `bolt new` names a proposed record with `--source`
- **THEN** the proposal is refused, naming the bolt and the record

#### Scenario: A queued unit moved into a bolt
- **WHEN** a proposal moves a queued unit into a bolt, and the unit's sources in the plan name a proposed record
- **THEN** the proposal is refused, naming the unit and the record

#### Scenario: Every record accepted
- **WHEN** every record the proposal's new bolts and units name is accepted on its kit's main, with no amendment marked proposed
- **THEN** the proposal is written and its card raised, as without records

#### Scenario: A record of another repository
- **WHEN** a new unit of crew names `agentplot/sluice:docs/adr/0022` as a source
- **THEN** record 0022 is read on agentplot/sluice's main, not crew's, and judged the same way

#### Scenario: A kit's main that cannot be read
- **WHEN** a new unit names a record, and its kit's main cannot be fetched from GitHub
- **THEN** the proposal is refused, naming the repository and why it could not be read, and nothing is written

#### Scenario: Work the proposal does not make new
- **WHEN** a proposal only reorders, amends or drops units already in a bolt, whose sources name a proposed record
- **THEN** no record is read for them, and the proposal is written

### Requirement: A record is named in a source by its path
crew SHALL take a source to name a decision record wherever it holds `docs/adr/<four digits>`, with or without the rest of the record's file name. A record named so SHALL be the kit's of the bolt or unit that names it, unless `<owner>/<name>:` or `<owner>/<name>` and a space comes right before it, when it SHALL be that repository's. One source MAY name several records. A record named only in words, such as "record 0026", SHALL NOT be read.

#### Scenario: A source holding several records and other pages
- **WHEN** a source reads `docs/adr/0029 (accepted 2026-10-14); docs/architecture/core.md read.5`
- **THEN** crew reads record 0029 of the unit's kit, and nothing else of that source

#### Scenario: A record named in words
- **WHEN** a source reads `record 0026 point 4`
- **THEN** crew reads no record for it

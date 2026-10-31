## ADDED Requirements

### Requirement: crew's release carries a kind for each main-level role
crew's plugin SHALL carry a Flume declaration, `plugin/flume/kinds.toml`, of five kinds, `crew-design`, `crew-planner`, `crew-reviewer`, `crew-ops` and `crew-operator`, each landing nothing, its branches prefixed by its name, and holding one stage, `turn`, whose prompt is `plugin/flume/turn.md` beside it and whose one deliverable is a report in the place's own folder, `report:{{state}}/turn.md`. The declaration SHALL name no model, no instructions and no environment.

#### Scenario: The declaration as Flume reads it
- **WHEN** `plugin/flume/kinds.toml` is read as TOML
- **THEN** it holds the five kinds, each with `lands` false, one stage named `turn` with `report:{{state}}/turn.md` as its one deliverable and `turn.md` as its prompt, and no `model`, `instructions` or `env` in any table

### Requirement: A turn's prompt starts and ends the turn
`plugin/flume/turn.md` SHALL have the run start with `crew role start` and end with `crew role end`, writing its report at `{{report}}`, and SHALL place `{{needs}}` in a sentence saying the run asks the user only on a card and stops short only when `crew role start` refuses. It SHALL ask for no `{{brief}}`.

#### Scenario: The prompt's parts
- **WHEN** `plugin/flume/turn.md` is read
- **THEN** every part in double braces is one Flume fills for a stage with a report deliverable and no `makes`, `{{needs}}` among them, and `{{brief}}` is not among them

### Requirement: An ask is a record naming a role
An ask SHALL be a record of `asks.rec` on the partition's flywheel branch, written through crew as every write there is: its number, the role it asks, who or what asks, what kind of ask it is, the record it names where it names one, its key where it must be written once, the words it carries where it carries any, and when it was written.

#### Scenario: A malformed ask
- **WHEN** a write would add an ask with no role
- **THEN** `recfix --check` refuses it and nothing is committed

### Requirement: An ask with a key is written once
An ask whose key `asks.rec` already holds SHALL write nothing and say so, on the tip it was first tried on and on any tip a refused push is applied again to.

#### Scenario: One answer seen twice
- **WHEN** the followers of deneb and mac-studio both sweep the card of madswan's proposal 12, answered at 10:04, while madswan's planner runs as its kind
- **THEN** `asks.rec` on `madswan/main` holds one ask of the planner keyed by that card's answer, and the second write says the ask is there

### Requirement: An ask is written with the act that makes it
An ask SHALL be written in the same commit as the act that makes it, where that act writes to the flywheel's branch, and in a commit of its own where it does not.

#### Scenario: A capture
- **WHEN** an agent captures a signal through crew in madswan, whose design agent runs as its kind
- **THEN** the capture's commit holds an ask of the design agent keyed by the signal's id

### Requirement: A tell, a notice or a send to a role that runs as its kind is an ask
A `crew tell` to a role its partition runs as its kind, by an agent or the user, and every notice crew sends it, SHALL be written as an ask of the role from the sender, `crew` for a notice, carrying the text; a `crew send` to the partition SHALL be an ask of its operator carrying whom it was sent to and the text. Nothing SHALL be typed into any pane for it.

#### Scenario: A tell to the planner
- **WHEN** madswan's planner runs as its kind, no standing agent of it is up, and madswan-design runs `crew tell madswan-planner "record 0053 is accepted"`
- **THEN** an ask of the planner from madswan-design holds those words, nothing is typed into any pane, and the command says it asked madswan-planner

#### Scenario: crew's own notice
- **WHEN** a proposal of madswan's is approved and the planner runs as its kind
- **THEN** an ask of the planner from crew says the proposal was approved, where today the planner is told

### Requirement: A capture and a landing are asks
A signal captured through crew SHALL be an ask of a design agent that runs as its kind, one per signal, keyed by the signal's id. A bolt's landing, as crew's read of it records it, SHALL be an ask of a planner and of a design agent that run as their kinds, keyed by the bolt; a landing that did not land SHALL be an ask of a main-level ops that runs as its kind, with sluice's words, keyed by the submission.

#### Scenario: A landing
- **WHEN** a bolt of swancloud lands and crew's read of the landing records it, while swancloud's planner and design agent run as their kinds
- **THEN** that write holds an ask of the planner and one of the design agent, each naming the bolt

### Requirement: A card's answer, an opening and a batch are asks
A card's answer found by the follower's card sweep on a card in the name of a role that runs as its kind SHALL be an ask of that role, keyed by the card's request and when it was answered. The user opening a role SHALL be an ask of it. A batch from `crew review` SHALL be an ask of a reviewer that runs as its kind, and a batch delivered an ask of the planner.

#### Scenario: A deploy approved from the phone
- **WHEN** swancloud's ops runs as its kind and the user approves `deploy/deneb` on the phone
- **THEN** the follower's next card sweep writes one ask of ops naming `deploy/deneb`

### Requirement: A role that stands is asked nothing
For a role its partition does not run as its kind, no tell, notice, send, capture, landing, card's answer, opening or batch SHALL write an ask: each SHALL do what it does today.

#### Scenario: A role still standing
- **WHEN** wldn's planner stands, and `crew tell wldn-planner "<text>"` runs
- **THEN** the text is typed into wldn-planner's pane as today, and no ask is written

### Requirement: A tell finds a standing agent of the role first
A tell to a role its partition runs as its kind SHALL be typed into a standing agent of it that is still up, as a tell is today, and written as an ask only once crew has read that none is up. When crew cannot read whether one is up, the tell SHALL refuse, naming what it could not read, and write nothing.

#### Scenario: The standing agent not yet stopped
- **WHEN** madswan's planner was named to run as its kind a minute ago, its standing agent is still up and idle, and the design agent tells it
- **THEN** the text is typed into the standing agent's pane, and no ask is written

### Requirement: A place that waits on a role is pending for the role
A place the runner's records show waiting on its caller, stopped short asking or having found work, past its send-back bound, lost, stalled, or holding its submission for a word, whose launch request names `<label>/<role>` as its recipient, SHALL be pending for that role as an unanswered ask is, keyed by its request and when that wait began, with no ask written for it. A place whose stage delivers while its kind runs through SHALL be pending for no role. The role's next run SHALL take each.

#### Scenario: A stage asks the planner
- **WHEN** a construct in a place crew launched for madswan stops short asking which bolt a finding belongs in, its request's recipient `madswan/planner`, and the runner's records show it waiting
- **THEN** the planner's next run takes it with its work, its place and its words

#### Scenario: A stage that delivers
- **WHEN** a unit's construct delivers and its code stage starts
- **THEN** nothing is pending for the planner from it

### Requirement: A role's landed work is pending for the role
A place `crew role land` launched for a role SHALL be pending for that role once the runner's records show it landed, keyed by its request, so the role's next run reads what landed.

#### Scenario: A record lands
- **WHEN** the chore madswan's design run launched for record 0053 lands on crew's main
- **THEN** the design agent's next run takes it, and records the record's status with `crew record`

### Requirement: A role record names its run
`roles.rec` on the partition's flywheel branch SHALL hold one record for each role its partition runs as its kind, naming its address, `<label>/<role>`; its run's name, `<label>-<role>`; the main level's host; the partition's first blueprints repository as the teams file names it; crew's kinds and the kind `crew-<role>`; the place's name, `<label>`; the stream the partition's `flume` names for the role; the priority 0; the intent `<label>-<role>`; and the role's model and effort.

#### Scenario: The planner's record
- **WHEN** madswan runs its planner as its kind and its record is written
- **THEN** it names `madswan/planner`, `madswan-planner`, deneb, `afterthought/blueprints`, `crew-planner`, `madswan`, the intent `madswan-planner` and Fable 5.1

### Requirement: Role records follow the teams file
crew SHALL write `roles.rec` to match the teams file at `crew main up` and in the commit of an ask whose role's record is missing or differs, and SHALL remove the record of a role the teams file no longer runs as its kind.

#### Scenario: The planner moves
- **WHEN** madswan's teams entry names a stream for its planner, and `crew main up madswan` runs
- **THEN** `roles.rec` on `madswan/main` holds the planner's record

#### Scenario: An ask before main up
- **WHEN** the teams entry names a stream for the planner, no record of it is on the branch, and a tell to the planner writes an ask
- **THEN** the ask's commit holds the planner's record too

#### Scenario: The planner stands again
- **WHEN** madswan's teams entry names the planner `false` again, and `crew main up madswan` runs
- **THEN** `roles.rec` holds no record of the planner

### Requirement: A role has at most one run, wanted while anything is pending
What is pending for a role SHALL be each of its asks and each place that waits on it that no turn ended by `crew role end` took. The role SHALL be wanted while anything is pending, and the runner on its record's host SHALL keep at most one run of it, so asks written during a run wait for the next and a burst of them is one run.

#### Scenario: A burst
- **WHEN** three asks of madswan's planner are written within a minute and no run of it stands
- **THEN** one run of the planner takes all three

#### Scenario: An ask during a run
- **WHEN** the planner's run has taken two asks, and a third is written before it ends
- **THEN** the third is still pending once the run's turn ends, and the planner is wanted again

#### Scenario: Nothing pending
- **WHEN** every ask of the planner has been taken by a turn that ended
- **THEN** the planner is not wanted

### Requirement: A run's start takes everything pending
`crew role start`, run in a role's run, SHALL take everything pending for the role and record, in one commit, the turn that took it. With nothing pending, it SHALL record no turn and say so. Run anywhere but a role's run, it SHALL refuse, naming where it runs, and write nothing.

#### Scenario: Two asks waiting
- **WHEN** the planner's run starts with an ask from the design agent and a card's answer pending
- **THEN** `crew role start` records a turn taking both

#### Scenario: Nothing waiting
- **WHEN** the planner's run starts with nothing pending
- **THEN** `crew role start` records no turn and says nothing waits, so the run ends its turn

#### Scenario: Not a run
- **WHEN** `crew role start` runs in a change's place
- **THEN** it refuses, saying it runs only in a run of a crew role, and writes nothing

### Requirement: A run's start gives its brief and what it took
`crew role start` SHALL write the role's brief, filled for its partition as `crew-role` fills it, to a file on the host, and print the file's path to read whole first, then each ask it took, oldest first, with who asked, what, the record it names and its words, then each place that waits on the role, with its work, its place and its words, and last that Pending You's `list_pending` gives the run's own cards.

#### Scenario: What the planner's run reads
- **WHEN** the planner's start took an ask from the design agent and a card's answer
- **THEN** it prints the brief's path, then the design agent's words, then the card's key, then the line on `list_pending`

### Requirement: A start takes again what a lost run took
A turn of the role still open when a run starts SHALL be recorded superseded by the new turn, which takes its asks again; a superseded turn SHALL answer nothing.

#### Scenario: A run that was lost
- **WHEN** the planner's earlier run took an ask and was lost before its end, and its run is retried
- **THEN** the new start records the earlier turn superseded and takes that ask again

### Requirement: A run's end answers what it took
`crew role end --report <path> "<what was done>"` SHALL record the run's open turn ended with those words, in one commit, and write the report at the path, naming the turn, what it took and what was done. With no open turn of the run, it SHALL write the report saying no turn was taken, record nothing on the branch, and say so, so every run delivers its stage. Run anywhere but a role's run, it SHALL refuse and write nothing.

#### Scenario: A turn ends
- **WHEN** the planner's run has acted on what it took and runs `crew role end --report <path> "proposed the fix bolt"`
- **THEN** the turn is recorded ended, the asks it took are no longer pending, and the report is written at the path

#### Scenario: No turn open
- **WHEN** a run that found nothing pending runs `crew role end --report <path> "nothing waited"`
- **THEN** the report is written at the path saying no turn was taken, the branch is unchanged, and the command says so

### Requirement: A run is named as its role
A run SHALL be named `<label>-<role>`, `<label>-ops` for main-level ops, read from the place it runs in, `crew-<role>--<label>`, the place its role record named, for a role its partition runs as its kind. Every crew command the run makes SHALL take that name and partition as a standing agent's `CREW_AGENT` and `CREW_LABEL` give them: the plan's role table, the cards' owners and the run record's entries SHALL treat the run as the role, and a command forwarded to another host SHALL carry them.

#### Scenario: The planner's run proposes
- **WHEN** the planner's run runs `crew plan propose <file>`
- **THEN** the proposal is the planner's, its card is raised in madswan-planner's name, and a direct plan write by the run is refused as the planner's is

#### Scenario: A place of another kind
- **WHEN** a crew command runs in a fix's place with no `CREW_AGENT`
- **THEN** it names no role as its caller

### Requirement: A run's brief says how a turn goes
A role's brief SHALL say, for a role that runs as its kind, that its turn starts with `crew role start`, acts on what that took, and ends with `crew role end`; that it waits in its session on nothing, and that what it would have waited for, an answer, a submission, a review or a tell, reaches its next run as an ask; and that it asks the user only on a card in its own name. For a standing role it SHALL say that its work reaches it as tells and cards in its pane.

#### Scenario: Every brief filled
- **WHEN** each of the five briefs prints for a partition that runs all five as their kinds
- **THEN** each holds the turn's words, and no token is left unfilled

### Requirement: A role's work that lands is a place it launches
`crew role land <repo> <name> --brief-file <file>`, run in a role's run, SHALL launch through the runner a place of Flume's own chore kind in that repository, on its default branch, its brief the file's text whole and the run's address its recipient. A repository neither the teams file nor the plan names SHALL be refused, and so SHALL a run outside a role's run. No role's run SHALL submit to sluice.

#### Scenario: The design agent's records
- **WHEN** madswan's design run writes the text of a record and its rule's amendment to a file and runs `crew role land afterthought/crew record-0053 --brief-file <file>`
- **THEN** a chore launch in `afterthought/crew` on its default branch is written for the runner, with the file's text as its brief and `madswan/design` as its recipient

### Requirement: The user opens a role to talk
`crew role open <role> [--label L]` SHALL write an ask from the user to open the role, and say that its run opens as the place `crew-<role>--<label>` on the main level's host. Where the runner's records on the role's host show a run of the role live, it SHALL write nothing and name that run's place. Where those records cannot be read, it SHALL refuse, naming what it could not read.

#### Scenario: No run live
- **WHEN** no run of madswan's design agent stands and the user runs `crew role open design --label madswan`
- **THEN** an open ask of the design agent from the user is written, and the command names `crew-design--madswan` on deneb

#### Scenario: A run live
- **WHEN** a run of madswan's design agent is live and the user runs `crew role open design --label madswan`
- **THEN** nothing is written, and the command names the live run's place to talk to now

### Requirement: A turn the user opened lasts their conversation
A turn that took an open ask SHALL greet the user in its pane and keep the conversation there until the user says they are done, and then end.

#### Scenario: Talking a design through
- **WHEN** the design agent's run took the user's open ask and the user talks a design through in its pane
- **THEN** the run's turn goes on until the user says they are done, and then it runs `crew role end`

### Requirement: Main-level ops's landing from a run does not wait
`crew bolt submit`, run in ops's run, SHALL return once each bolt is queued, leaving the landing's waiter on the host as today, and crew's read of each landing SHALL write its asks.

#### Scenario: A landing that conflicts
- **WHEN** ops's run submits bolt `y` on the user's send, its turn ends, and `y`'s landing conflicts with main
- **THEN** crew's read of the landing writes an ask of ops with sluice's words, and ops's next run takes it

### Requirement: A run's model is its definition's
A role record SHALL name the model and the effort of the role's definition after the teams file's `roles.<role>` override, the runner's launch SHALL pass the model, and the kinds file SHALL name neither.

#### Scenario: An override
- **WHEN** wldn's teams entry sets `roles.planner.model` and wldn's planner runs as its kind
- **THEN** wldn's planner's role record names that model, and madswan's names the definition's

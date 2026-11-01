# main-level Specification

## Purpose
Above a partition's bolt teams: a design agent that elaborates on main, a planner across the bolts, a dispatcher on each host that runs them, and ops that lands them. Signals are what reaches them from outside.

## Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, its state repository (`state`, as `<owner>/<name>`), the machine and session its main level runs in, and, from version 4, `flume`, naming each of its five main-level roles, `design`, `planner`, `reviewer`, `ops` and `operator`, as `false` while it stands or as the Flume stream its runs run in on the main level's host. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default. A partition with no `state`, or at version 4 with no `flume`, SHALL be an error naming the field and the machine's configuration as the fix, never a default, and so SHALL a `flume` that leaves a role out, names another key, or gives a role anything but `false` or a stream's name. crew SHALL read versions 2, 3 and 4 of the file, every role standing in a file below 4. A partition's `roles.<role>` MAY name a `session` for a main-level role other than the dispatcher, a session of the main level's machine in the partition, where that role runs while it stands; any other session SHALL be an error naming it.

#### Scenario: clients/willdan
- **WHEN** `teams.json` lists `wldn` as `clients/willdan` with willdan-blueprints and `WilldanGroup/crew-state`, running on the box in `wldn-2`
- **THEN** `crew main up wldn` starts its main level in `wldn-2` on the box, and wldn's plan is read from `wldn/main` of `WilldanGroup/crew-state`

#### Scenario: A partition with no state repository
- **WHEN** a partition's entry has no `state`
- **THEN** crew refuses to load the teams file, naming the partition and the missing field

#### Scenario: The planner in a session of its own
- **WHEN** swancloud's entry names `roles.planner.session` as `swancloud-2`, a session of deneb in partition personal
- **THEN** `swancloud-planner` runs in `swancloud-2` and its other main-level roles in the main level's session

#### Scenario: A session of another partition
- **WHEN** swancloud's `roles.planner.session` names `madswan-1`, a session of partition business
- **THEN** crew refuses to load the teams file, naming the planner, the session and its partition

#### Scenario: A partition with no flume
- **WHEN** a partition's entry in a version 4 file has no `flume`
- **THEN** crew refuses to load the teams file, naming the partition, the field and swancloud's `lib/crew-teams.nix`

#### Scenario: A role crew has no kind for
- **WHEN** madswan's `flume` names `dispatcher`, leaves out `operator`, or gives `planner` the value `true`
- **THEN** crew refuses to load the teams file, naming the partition and the role

#### Scenario: The file before version 4
- **WHEN** `teams.json` is at version 3
- **THEN** crew loads it, and every main-level role of every partition stands

### Requirement: The main level is one herdr workspace
`crew main up <label>` SHALL open a herdr workspace named `<label>` in the main level's session. It SHALL hold a `design` tab with the design agent, a `planner` tab with the planner, an `ops` tab with the main-level ops and an `operator` tab with the partition's operator, each only while it stands, and start each. A role that runs as its kind SHALL get no tab and no start: `crew main up` SHALL instead write its role record to match the teams file, and SHALL end a standing agent of it still running once that agent is not working, leaving one working and saying so. It SHALL then start a dispatcher on every host where the partition's teams run.

Every agent crew starts outside a team, the main level's standing roles and each dispatcher, SHALL be greeted once it is up, exactly once per start, as a team's conductor is: told to read where the partition stands and carry on with what is its role's. The greeting SHALL be marked as crew's. An agent brought back by `crew revive` or `crew main up` after the main level was taken down SHALL be greeted the same way, so none sits idle until someone tells it what to do. `crew revive` SHALL bring back no role its partition runs as its kind.

#### Scenario: The main level comes up
- **WHEN** `crew main up wldn` runs and wldn's `flume` names every role `false`
- **THEN** `wldn-design`, `wldn-planner`, `wldn-ops` and `wldn-operator` start in the `wldn` workspace, and `wldn-dispatch-chuck-herdr-alpha` starts on the box, and each is greeted once it is up

#### Scenario: Two roles run as their kinds
- **WHEN** madswan's `flume` names a stream for its reviewer and its planner, and `crew main up madswan` runs
- **THEN** the `madswan` workspace has no `planner` tab and no planner is started or greeted, `roles.rec` on `madswan/main` holds the planner's and the reviewer's records, and the design agent, ops and the operator start as today

#### Scenario: A standing planner from before
- **WHEN** madswan's `flume` has just come to name a stream for its planner, `madswan-planner` still stands idle in its tab, and `crew main up madswan` runs
- **THEN** `madswan-planner`'s standing agent is ended and the command says so; had it been working, it would be left and named

#### Scenario: The main level comes back
- **WHEN** the user runs `crew main down swancloud` and then `crew main up swancloud`
- **THEN** each of its standing agents starts and is greeted, and picks up its role from the rail and the bolts without the user or the operator telling it to

#### Scenario: Brought up again while it is up
- **WHEN** `crew main up wldn` runs while its agents and dispatchers are up
- **THEN** none is started and none is greeted

#### Scenario: Revived after a restart
- **WHEN** a host restarts, `wldn-design`'s pane comes back with no agent in it, and `crew revive` runs there
- **THEN** `wldn-design` is brought back and greeted once, and no agent that came back by itself is greeted

#### Scenario: An agent waiting on a question
- **WHEN** `crew main up wldn` starts `wldn-planner` stopped on a question in its pane
- **THEN** the design agent and ops are greeted without waiting on it, the command says `wldn-planner` waits on a question and will be greeted once it is answered, and it is greeted once, after the answer

#### Scenario: An agent that never settles
- **WHEN** an agent `crew main up` started is still not ready to greet when crew stops waiting for it
- **THEN** the command says so, names the `crew tell` that would greet it, and still succeeds

### Requirement: The design agent elaborates on main
The design agent SHALL keep the partition's design true on main: the books, specs and constitution in its blueprints repos and kits, the decision records, and the curation of signals with the moves `attach`, `challenge`, `new-territory`, `answered` and `drop`, each written only through `crew signal move`. It SHALL answer a conductor's design question. Work its elaboration calls for SHALL be queued as units, never put into a bolt by the design agent, each with an intent that names the outcome and sources that name the records governing it, never the mechanism.

A ruling the design agent gives about how a service or a system behaves SHALL name, in the message that carries it, the documentation page or the reading it rests on. Before ruling about something that exists, the design agent SHALL read it itself with the credentials it has: the live configuration, the stack, the policy, the code on main. Where it has neither documentation nor a reading, it SHALL say so and ask for the reading, and SHALL give no ruling on that point until the reading is back. A ruling SHALL say what must be true and what must not change, and SHALL leave the steps to the construct. A construct's linked questions SHALL be answered together, in one answer, after reading.

#### Scenario: Elaboration produces work
- **WHEN** the design agent records a decision that needs building
- **THEN** it queues a unit whose intent says what becomes true and whose source is the decision's page, and tells the planner

#### Scenario: A question about a live service
- **WHEN** a conductor asks whether an existing CloudFormation stack can take over a resource, and the design agent can read the stack with its credentials
- **THEN** it reads the stack and the service's documentation before answering, and its answer names the page and the reading it rests on

#### Scenario: Nothing to rest a ruling on
- **WHEN** a question turns on how a service behaves, and the design agent can neither find the documentation nor read the thing itself
- **THEN** it says so, names the reading it needs and asks for it, and rules on that point only once the reading is back

#### Scenario: A sequence is asked for
- **WHEN** a construct asks in what order to take over an AWS boundary
- **THEN** the design agent answers with what must be true when the takeover is done and what must not change along the way, and the construct works out the steps from its own reading

#### Scenario: Linked questions
- **WHEN** a conductor carries three questions from one construct about the same stack
- **THEN** the design agent reads what they turn on and answers all three in one message

### Requirement: The planner plans across bolts
The planner SHALL be the only agent that proposes bolts, the placing of units into bolts, and their splitting, ordering or moving between bolts, and SHALL change the plan only through a proposal the user approves. It SHALL route signals to work. A change to an active bolt SHALL be agreed by that bolt's conductor, with `crew plan agree`, before the proposal can be approved. The planner SHALL NOT start units or drive a team.

An intent the planner writes SHALL name the outcome, and the unit's sources SHALL name the records that govern it; the intent SHALL NOT name the mechanism. Corrections to a unit whose construct is still running SHALL be held and proposed as one amendment once that construct has settled, unless one of them blocks the team now, which SHALL be proposed at once with the others held so far.

#### Scenario: A finding mid-bolt
- **WHEN** swb-1's conductor reports that a unit needs work outside the bolt's goal
- **THEN** the planner proposes queuing that work or adding it to another bolt, and swb-1's bolt keeps its goal

#### Scenario: New work beside a bolt in flight
- **WHEN** the planner judges that new work belongs in the bolt swb-2 holds
- **THEN** it proposes the unit for that bolt, swb-2's conductor agrees or says why not, and the unit is in the bolt only once the user has approved the proposal

#### Scenario: A changed mechanism
- **WHEN** a construct finds that the way a unit's sources describe doing something won't work, and the records are amended
- **THEN** the unit's intent still holds, and the planner proposes no amendment for it

#### Scenario: Corrections arrive during construct
- **WHEN** two corrections to a unit arrive while its construct is still running, and neither stops the team
- **THEN** the planner holds both, and once the construct has settled proposes one `unit amend` that carries both

#### Scenario: A correction that blocks the team
- **WHEN** a correction arrives without which the unit's construct, or another unit, cannot go on
- **THEN** the planner proposes the amendment at once, with any other corrections it holds for that unit

### Requirement: A dispatcher allocates each host's work
A dispatcher SHALL run on each host where the partition's teams run, in a herdr workspace `<label> dispatch`. It runs in the main level's session if that is on the host, otherwise in the session of the host's first team by name. It SHALL give that host's teams their bolts, start and stop them, and watch their health and their accounts' use. It SHALL NOT change a bolt's content or drive a unit.

#### Scenario: Two hosts
- **WHEN** the partition's teams run on the box and on mac-studio
- **THEN** each host has its own dispatcher, and asking either one about allocation answers for its host only

### Requirement: Main-level ops lands bolts by one procedure
The main-level ops SHALL land bolts whose verification is green on the user's word: their send on a kit's landings card, which crew raises in ops's name, the word for every bolt they ticked, in the card's order unless their note moves one; or their words in ops's own pane. It SHALL submit them with one `crew bolt submit <bolt>...` in that order, which queues each in sluice behind the one before and closes each with `crew bolt land` as it lands. It SHALL push nothing, level no host and move no branch by git. A bolt that does not land for its own content, a conflict or a failed check, SHALL be told to its conductor in sluice's words, the rest going on. A bolt whose landing sluice or its host stopped SHALL be reported as a finding outside any bolt and submitted again by the same `crew bolt submit` once what stopped it is cleared, on the word it has, with no new word of the user's. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user sends swb-1's bolt ticked on willdan's landings card
- **THEN** the main-level ops runs `crew bolt submit` on it, which lands it through sluice and closes it with `crew bolt land`, and the plan no longer holds the bolt

#### Scenario: Several bolts in order
- **WHEN** the user sends `land/crew` with `y`, `z` and `w` ticked in that order
- **THEN** the main-level ops runs `crew bolt submit y z w` once, as a background command, and sluice lands them in that order

#### Scenario: A note moves the order
- **WHEN** the user sends `land/crew` with `y` and `z` ticked and a note saying `z` goes first
- **THEN** the main-level ops runs `crew bolt submit z y`

#### Scenario: A landing that conflicts
- **WHEN** `crew bolt submit y z` says `y` did not land because it conflicts with main
- **THEN** the main-level ops moves nothing, tells `y`'s conductor and the user sluice's words, and `z` lands all the same

#### Scenario: No word from the planner
- **WHEN** the planner tells the main-level ops that a bolt may land
- **THEN** the main-level ops lands nothing until the user's send on the kit's landings card with the bolt ticked, or the user's words in its pane

#### Scenario: A landing deploys nothing
- **WHEN** a swancloud bolt lands
- **THEN** nothing is deployed by the landing, and main is deployed only by a later act on the user's word for that deploy

#### Scenario: The brief lands bolts together
- **WHEN** main-level ops's brief is read
- **THEN** it says to submit every bolt the user ticked with one `crew bolt submit` in the card's order, and says nothing of landing one bolt at a time

#### Scenario: A landing sluice stopped
- **WHEN** `crew bolt submit y z` says `y` did not land because the host could not run main's checks, nothing of the bolt's
- **THEN** the main-level ops tells no conductor, records what stopped it as a signal and tells the planner, `z` lands all the same, and once the host runs checks again ops runs `crew bolt submit y` on the user's send that still stands, asking the user nothing

### Requirement: Signals reach the plan only through a route
Signals SHALL stay in the partition's first blueprints repo, in the signals model its `signals/README.md` gives. A bolt's agents SHALL record a finding outside their bolt as a signal there with `crew signal`. A signal SHALL become work only through a `route` move written by `crew unit add --signal`.

#### Scenario: A finding from a bolt
- **WHEN** ops on swb-1 finds a defect in a shared service the bolt does not own
- **THEN** it records a signal in willdan-blueprints, and the planner decides whether to route it

### Requirement: Every move is written through crew and never merged
Every move SHALL be appended to `moves.rec` on the flywheel's branch of its state repository, through crew: `route` by `crew unit add --signal`, and `attach`, `challenge`, `new-territory`, `answered` and `drop` by `crew signal move <id> <move>`. Each SHALL be fetched over https, applied to the tip of the branch, checked with `recfix --check`, committed, and pushed without force, applied again to the new tip when the push is refused. A signal SHALL have one move; a second is refused.

#### Scenario: Moves from two hosts
- **WHEN** a route is written on the box while curation writes a drop on mac-studio, both through crew
- **THEN** both moves are in `moves.rec`, one after the other, nothing is merged, and the file passes `recfix --check`

#### Scenario: A signal moved twice
- **WHEN** `crew signal move` names a signal that already has its move
- **THEN** it is refused, naming the move it has

### Requirement: Any agent crew starts is reached by name
`crew tell <agent> "<text>"` SHALL prompt any agent crew starts, by its name alone, in the host and session where it runs. An agent that is not up SHALL be reported and the command SHALL fail, with nothing sent. An agent waiting on a question in its pane SHALL be reported the same way, naming the wait, and nothing SHALL be typed into the question: a tell is delivered as a prompt the agent receives, never as text that lands in a dialog and is lost. An agent is waiting on a question when herdr reports it blocked, or when it has opened a question or a plan for the user's answer in Claude Code and that call has no answer yet in its session, however the dialog looks on screen. The agent's session is the one herdr names for its pane, or, when herdr names none, the newest session crew recorded of that agent starting in that pane. When neither names a session, herdr's reading of the pane alone SHALL guard the tell, and a missing session SHALL NOT refuse it. When crew cannot read whether the agent is waiting on a question, it SHALL refuse the same way, naming what it could not read, and type nothing. crew's greetings and notices SHALL be delivered on the same terms.

A tell to a role its partition runs as its kind, `<label>-<role>`, whose standing agent is not up, SHALL NOT fail for it: it SHALL be written as an ask of the role, from the sender, `crew` for crew's own notice, carrying the text, and the command SHALL say it asked the role and type nothing. A standing agent of that role still up SHALL be told as today.

#### Scenario: A conductor asks the design agent
- **WHEN** swb-1's conductor on the box runs `crew tell wldn-design "<question>"`
- **THEN** the design agent in `wldn-2` receives the question

#### Scenario: The agent is waiting on a question
- **WHEN** `crew tell wldn-ops "<text>"` runs while wldn-ops has a question open in its pane
- **THEN** the command fails, says wldn-ops is waiting on a question in its pane, and nothing is typed there; the sender tells it again once the question is answered

#### Scenario: A question herdr does not see
- **WHEN** wldn-ops has a question open in its pane that herdr reports as idle, and `crew tell wldn-ops "<text>"` runs
- **THEN** the command fails the same way, and nothing is typed there

#### Scenario: The question is answered
- **WHEN** the user answers or dismisses wldn-ops' question, and `crew tell wldn-ops "<text>"` runs again
- **THEN** wldn-ops receives the text as a prompt

#### Scenario: crew cannot read whether a question is open
- **WHEN** wldn-ops opened a question and crew cannot read its session to learn whether it has been answered
- **THEN** `crew tell wldn-ops "<text>"` fails naming what it could not read, and nothing is typed there

#### Scenario: A conductor greeted while it waits on a question
- **WHEN** crew greets a conductor that has a question open which herdr reports as idle
- **THEN** the greeting waits until the question is answered, as it does for one herdr reports blocked, and is then sent once

#### Scenario: A main-level agent herdr names no session for
- **WHEN** wldn-planner sits idle in `wldn-2` after herdr's own restore resumed its pane, herdr names no Claude session for that pane, and the design agent runs `crew tell wldn-planner "<text>"`
- **THEN** wldn-planner receives the text as a prompt, marked with who sent it

#### Scenario: A question open in a pane herdr names no session for
- **WHEN** herdr names no Claude session for wldn-planner's pane and reports it idle, crew's record names the session that last started in that pane, that session has a question open, and `crew tell wldn-planner "<text>"` runs
- **THEN** the command fails, says wldn-planner is waiting on a question in its pane, and nothing is typed there

#### Scenario: Neither herdr nor crew names a session
- **WHEN** herdr names no Claude session for wldn-planner's pane and crew holds no record of a session of wldn-planner starting in that pane
- **THEN** `crew tell wldn-planner "<text>"` is typed unless herdr reports the agent blocked, and herdr's own refusal of a blocked agent at the moment of typing still fails it with nothing typed

#### Scenario: A pane crew cannot find
- **WHEN** herdr on the agent's host lists no agent named wldn-planner in its session
- **THEN** `crew tell wldn-planner "<text>"` fails saying it is not up, and nothing is sent

#### Scenario: A role that runs as its kind
- **WHEN** madswan's planner runs as its kind, herdr lists no agent named madswan-planner, and swc-3's conductor runs `crew tell madswan-planner "<text>"`
- **THEN** an ask of the planner from swc-3-conductor holds the text, nothing is typed, and the command says it asked madswan-planner

### Requirement: Main-level ops reports results as one glyph per line
Whenever the main-level ops reports the results of a landing's checks, of main's deploy or of any test or proof it ran, it SHALL list them first, before any prose, one bullet per suite, check or proof: ✅ passed, with its counts where the tool gave them; ❌ failed, with how many failed and one line on why; ⏳ not yet run, or still running. It SHALL NOT state a result only in a sentence, nor fold several into one bullet.

#### Scenario: A landing whose gate is still running
- **WHEN** the main-level ops reports a landing while the merge's checks still run
- **THEN** its message opens with a ⏳ bullet for those checks, and says the bolt has not landed yet

#### Scenario: A landing that went through
- **WHEN** the merge's checks passed and main was deployed and found healthy
- **THEN** its message opens with a ✅ bullet for the checks, with their counts, and one for main's deploy, before it says the bolt is closed

### Requirement: A deploy and every operation are approved and recorded through crew
A kit's deployer SHALL ask crew for each deploy of a `manual` environment with `crew ops offer <env> --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]`, the notes file the kit's release notes for the range from the environment's last deployed commit to the offered one as the kit's changelog tool writes them, the steps file the range's after-deploy steps one a line as the deployer gathers them (`step <n> <doer> <when> <environments> <why> <text>`), which SHALL raise the deploy's card in main-level ops's name, keyed `deploy/<env>`, with the notes and the steps on its face and nothing of them written by crew, change it when a newer head is offered, post it again when the commit already offered is offered again with the same files and main-level ops holds no card open under `deploy/<env>`, writing no second offer, and tell main-level ops the line that adopts it, `call get_request (requestId <id>, name <role>)`; the user's word SHALL be holding that card, recorded with `crew ops approve`. `crew ops record --act end` SHALL close the card with the deploy's outcome. `crew ops step` SHALL raise a step's card, keyed `op/<env>/<n>`, when the step's doer is the user or the step is marked held for the user's word, SHALL change it when the step is recorded again while it is open with other words, another doer or another hold, printing the line that adopts it whether it changed it or not, and SHALL close it when the step is recorded done or declined. `crew ops word` SHALL give the commit the word is for until that deploy's end is recorded. Every `crew ops` command SHALL run where the partition's main level runs.

#### Scenario: A deploy offered and approved
- **WHEN** the deployer offers mac-studio a deploy of main's head and the user holds its card
- **THEN** main-level ops runs `crew ops approve`, the row leaves the rail, `crew ops word mac-studio` prints the commit until the deploy's end is recorded, and `crew ops record mac-studio --act end` closes the card with each step's outcome

#### Scenario: An approval for another commit
- **WHEN** `crew ops approve` names a commit other than the open offer's
- **THEN** it is refused, recorded as refused, and no word is given

#### Scenario: An operation the user is to take
- **WHEN** the deployer records a step whose doer is the user as waiting, after a deploy or on its own
- **THEN** the rail shows it under operations with its `do` card until it is recorded done or declined, and `crew ops steps` gives its latest state

#### Scenario: A held step
- **WHEN** the deployer records a step whose doer is main-ops and marked held, after mac-studio's deploy
- **THEN** the rail shows it under operations with a card asking now, when quiet or skip, and the step runs when the user answers

#### Scenario: The same commit offered again after its card was refused
- **WHEN** Pending You refused deneb's deploy card for `ddcf2cb`, and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** crew posts deneb's deploy card under `deploy/deneb`, the run record gains no second `ops.offer` for it, and main-level ops is told the line that adopts the card

#### Scenario: The same commit offered again while its card is open
- **WHEN** swancloud-ops's card for deneb's offer of `ddcf2cb` is open, and the deployer offers deneb `ddcf2cb` again with the same notes and steps
- **THEN** nothing is written, posted or changed

### Requirement: A decision record is accepted only on the user's yes
Every decision record the design agent writes, and every amendment it makes to one, SHALL be committed as proposed. A record or an amendment SHALL become accepted only on the user's yes, recorded in the record with the date and the user's words: given in the pane where the record was settled with them, or on the one card crew raises for it through `crew record` when it was not. Until the yes, a rule drawn from the record SHALL be written marked as proposed, and no unit SHALL be queued from it.

#### Scenario: A new record
- **WHEN** the design agent writes record 0021 in crew's `docs/adr/` from the signals, with the user not in its pane
- **THEN** it commits the record with the status proposed and runs `crew record crew 21 --proposed`, which raises one card asking the user to accept it, in the record's words, and queues no unit from it yet

#### Scenario: The user says yes
- **WHEN** the user approves the card for record 0021
- **THEN** the design agent commits the record as accepted by the user on that date, takes the proposed mark off each rule drawn from it, runs `crew record crew 21 --accepted`, which closes the card, and only then queues the units it calls for

#### Scenario: An amendment to an accepted record
- **WHEN** the design agent amends record 0005, which is accepted, with the user not in its pane
- **THEN** the amendment is marked proposed in the record, the card crew raises carries the amendment's words, and the amendment is accepted only on the user's yes

### Requirement: A record the user does not accept is revised or rejected
On a note asking for changes, the design agent SHALL revise the record, still proposed, commit it and run `crew record … --proposed` again, which closes the card the user answered with the new commit named and puts the revised record on a new card that follows it; a record revised while its card still waits on the user changes the card in place with the new commit named. On a no, it SHALL mark the record rejected, in the user's words, take out the rules drawn from it, and run `crew record … --rejected`, which closes the card.

#### Scenario: The user asks for changes
- **WHEN** the user answers the card with a note asking for a change
- **THEN** the design agent revises the record, commits it still proposed, and the card the user answered is closed, "Revised at …", naming the new commit, with a new card for the revised record following it

#### Scenario: The user says no
- **WHEN** the user rejects the card
- **THEN** the record's status becomes rejected with the user's words, every rule drawn from it is taken out, and the card is closed with the commit

### Requirement: The user's own words are their decision
What the user settled in their own words in the design talk SHALL be quoted in the record as their decision; when a card is raised for the record, it SHALL say which part that is, and when the user settled the whole record in the pane, their yes there SHALL be recorded and no card raised.

#### Scenario: The user's own words
- **WHEN** the user said in the design talk "the landing still needs my yes", and the record rests on it
- **THEN** the record quotes those words as the user's decision, and the card, when one is raised, says that part is the user's own

### Requirement: A record's status is recorded through crew
`crew record <kit> <number> --proposed|--accepted|--rejected` SHALL record the record's status with its commit in the run record, and SHALL refuse a status the record's file does not hold at that commit.

#### Scenario: A status the file does not hold
- **WHEN** the design agent runs `crew record crew 32 --accepted` while the file at HEAD still says proposed
- **THEN** the command refuses, naming the file's status, and records nothing

### Requirement: A record's card is raised unless it was settled in the pane
`crew record <kit> <number> --proposed` SHALL put the record at its commit on its card in the design agent's name, raising the card the first time and changing it in place at each new commit, unless `--settled-in-pane --excerpt "<words>"` says the user settled it in the pane; with `--alternatives <file>`, which hands the Markdown of the alternatives a rule of the user's decided between, the rules and each loosened, the card SHALL be a choice.

#### Scenario: A record a rule decided
- **WHEN** the design agent runs `crew record switchboard-kit 32 --proposed --alternatives docs/adr/0032-alternatives.md`
- **THEN** the card is a choice of loosening the rules as drafted, accepting as ruled, or sending back, with the file on its face, and the design agent is woken by the answer

#### Scenario: A record settled in the pane
- **WHEN** the user says "Yes, accept 31 as written" in the design agent's pane, and the design agent commits record 31 as proposed and runs `crew record crew 31 --proposed --settled-in-pane --excerpt "Yes, accept 31 as written"`
- **THEN** the status is recorded with the user's yes as given in the pane, naming the transcript record the words came from and not the words, and no card is raised

### Requirement: A record's card is closed with its accepted or rejected status
`crew record <kit> <number> --accepted` or `--rejected` SHALL close the record's card with the commit that holds the status.

#### Scenario: A record from the signals, accepted on its card
- **WHEN** the design agent runs `crew record crew 32 --proposed`, the user accepts the card, and the design agent commits it accepted and runs `crew record crew 32 --accepted`
- **THEN** the card was raised, and is closed with the accepting commit

### Requirement: A signal names where what its words point at lives
An agent recording a signal whose words point at something made elsewhere (another conversation, a page or prototype, an artifact, files in another repo, a spike) SHALL find it and name in the signal's sentence where it lives, in a form another agent can open: `<owner>/<repo>:<path>`, a branch, or an artifact's link. A conversation's id alone SHALL NOT stand for what the conversation made. The excerpt SHALL stay the words as said.

#### Scenario: The user pastes a conversation's id
- **WHEN** the user asks the planner for work and pastes the id of a conversation, held in another repo, that wrote the design pages and published the artifact the work rests on
- **THEN** the signal the planner records quotes the user's words, id and all, and its sentence names those pages by repo and path and the artifact by its link

### Requirement: A unit made from a signal names what the signal points at
A unit the planner proposes from a signal, or the design agent queues from one, SHALL name with `--source` what the signal points at, beside the signal itself.

#### Scenario: Work queued from a signal that names a page
- **WHEN** the planner proposes a unit from a signal whose sentence names a page in another repo
- **THEN** the unit's sources are the signal and that page, and the construct's prompt carries both

### Requirement: A greeting is taken or sent again
A greeting crew sends, to a conductor or to any agent crew starts outside a team, SHALL be sent only once the agent is ready for input, and crew SHALL then read the agent's transcript to see that Claude received it within a short time. When it does not, and the agent sits idle or done, crew SHALL clear what was left typed in the agent's input and send the greeting once more. Exactly one greeting SHALL reach the agent per start.

#### Scenario: A greeting taken at once
- **WHEN** `crew up swb-1` starts the conductor and its transcript shows the greeting received moments after crew sent it
- **THEN** crew says swb-1-conductor was greeted, records one greeting, and sent it once

#### Scenario: A greeting left typed
- **WHEN** crew greets wldn-planner and the planner's transcript shows nothing received within the time, while it sits idle
- **THEN** crew clears the planner's input, sends the greeting once more, and says it was greeted once the transcript shows it

### Requirement: A greeting not taken is reported, with nothing left typed
When the second sending of a greeting is not taken either, crew SHALL leave nothing typed, record no greeting, and say the agent was not greeted, with the `crew tell` that would greet it. When crew cannot read whether the greeting was taken, it SHALL send nothing more and say what it could not read. A greeting that is not delivered SHALL fail nothing else the command does.

#### Scenario: A greeting never taken
- **WHEN** neither sending of wldn-design's greeting shows in its transcript within the time
- **THEN** its input is cleared, crew says wldn-design was not greeted and gives the `crew tell wldn-design "<greeting>"` that would greet it, no greeting is recorded, and `crew main up` goes on with its other agents

### Requirement: A deploy held at a gate whose reviewer is the user waits as the user's step
A deploy a hosted deployer holds at a gate whose reviewer is the user SHALL be recorded by whoever dispatched it as a step that is the user's, waiting, the gate's link its text and the deploy's commit its `--to` when known, with no offer posted for it. Its rail row, the board's Operation lane and main-level ops's view SHALL say the deploy waits at its gate for the user.

#### Scenario: A stand dispatched to dev's gate
- **WHEN** a crew agent dispatches a run that waits at dev's gate, whose one reviewer is the user, and records `crew ops step dev --to 4f2a9c1 --key gate-38612817613 --doer user --state waiting --text <file holding the run's link>`
- **THEN** the rail shows the row `op/dev/<n>` under operations, saying the deploy of 4f2a9c1 to dev waits at its gate for the user with the gate's link, its card is raised, and no deploy offer is made for that commit

#### Scenario: The gate in the views
- **WHEN** the gate's step waits on dev
- **THEN** the board's Operation lane says it waits at its gate for the user, and main-level ops's view names it the gate of 4f2a9c1, not a step after 4f2a9c1

### Requirement: A gate's step ends when the gate is passed or rejected
A gate's step SHALL be recorded done when the deployer's run shows the gate passed, by whoever dispatched it, or by main-level ops on the user's Done; and declined when the gate is rejected or on the user's Skip. Its card SHALL close with that state, as every step's card does.

#### Scenario: The gate passed
- **WHEN** the deployer's run shows it has passed the gate, and its dispatcher records the step done
- **THEN** the step's card is closed as done, and its row leaves the rail

#### Scenario: The user taps Done
- **WHEN** the user approves at the gate and taps Done on the card
- **THEN** main-level ops runs the row's done command, and the card closes

#### Scenario: The gate rejected
- **WHEN** the user rejects the deployment at the gate and taps Skip on the card
- **THEN** main-level ops runs the row's decline command, and the card closes as declined

### Requirement: The main level is a workspace in each of its sessions
`crew main up <label>` SHALL open a `<label>` workspace in each session the main level's roles run in, each role's tab in its session's, and start each role there; `crew main down`, `crew main status`, `crew review` and `crew revive` SHALL find each role in its session.

#### Scenario: Design and planner on two accounts
- **WHEN** swancloud's planner runs in `swancloud-2` and the rest of its main level in `swancloud-1`, and `crew main up swancloud` runs
- **THEN** `swancloud-planner` starts in the `swancloud` workspace of `swancloud-2`, and the design agent, ops and the operator in `swancloud-1`'s

### Requirement: A role is never started twice when its session changes
`crew main up` SHALL refuse while a role's agent still runs in a session it no longer stands in, naming it, and `crew main down` SHALL end it there. Panes a state folder recorded in another session than the one its agents run in now SHALL be set aside and said, never taken for that session's.

#### Scenario: A role moved while it runs
- **WHEN** wldn's teams file names a session for its planner while `wldn-planner` still runs in `wldn-2`, and `crew main up wldn` runs
- **THEN** it refuses, naming `wldn-planner`, its session and pane, and that `crew main down wldn` ends it

#### Scenario: Panes recorded in another session
- **WHEN** swancloud's main level moves from `swancloud-2` to `swancloud-1` and a main-level command runs
- **THEN** the panes recorded in `swancloud-2` are set aside and said, and no agent of `swancloud-1` at the same pane id is taken for one of the main level's

### Requirement: A main-level role starts only on its main level's host
`crew-role <label> design|planner|ops|operator|reviewer`, fresh or with `resume`, SHALL start its agent only on the host the teams file names for that partition's main level. On any other host it SHALL refuse, naming the agent, the main level's host and this host, and start no Claude.

#### Scenario: The planner started on the standby
- **WHEN** the teams file puts swancloud's main level on deneb and `crew-role swancloud planner` runs on mac-studio
- **THEN** it refuses, saying that swancloud's main level runs on deneb, not mac-studio, and that crew starts `swancloud-planner` only there, and no Claude is started

#### Scenario: On its host
- **WHEN** `crew-role swancloud planner` runs on deneb
- **THEN** the planner starts as it does today

### Requirement: A main-level agent resumed off its host is given no identity
When herdr resumes a session without crew's environment and crew's record of it names a partition's design agent, planner, ops, operator or reviewer, crew SHALL give it its name, identity, pane name and brief back only on the host the teams file names for that main level. On any other host the session SHALL get none of them, its record SHALL be left as it was, and it SHALL be told at each start that it is no agent of crew's there, which host the main level runs on, and to do nothing of crew's.

#### Scenario: A replayed pane on the standby
- **WHEN** the teams file puts swancloud's main level on deneb, and herdr on mac-studio resumes a session whose record there names `swancloud-planner`
- **THEN** its commands see no `CREW_AGENT`, `CREW_LABEL` or `SLUICE_AGENT`, its pane is not named `swancloud-planner`, its record is unchanged, and it is told that swancloud's main level runs on deneb and that it is no agent of crew's on mac-studio

#### Scenario: Compacted on the standby
- **WHEN** that session on mac-studio is compacted
- **THEN** it is given no brief, and is told again that it is no agent of crew's there

#### Scenario: Resumed on its host
- **WHEN** herdr on deneb resumes a session whose record names `swancloud-planner`
- **THEN** it gets its name, identity and pane name back, and its brief at a compaction, as today

#### Scenario: The teams file can't be read
- **WHEN** herdr resumes a session whose record names `swancloud-planner` and crew can't read the teams file
- **THEN** it gets no identity, and is told that crew can't tell where swancloud's main level runs, and why

#### Scenario: A team's agent
- **WHEN** herdr resumes a session whose record names `crw-5-conductor` or `swancloud-dispatch-deneb`
- **THEN** it gets its identity back as today, without the teams file being read for it

### Requirement: A record settled in the pane takes the user's words, read as theirs
`crew record … --proposed --settled-in-pane` SHALL record the record settled in the pane only from the user's words, given with `--excerpt`, which crew reads in the caller's own session transcript on this host as the user's (`signals.5`), and only when the caller is the partition's design agent. Otherwise it SHALL refuse with the reason, record nothing and raise no card. Either flag without the other SHALL be refused.

#### Scenario: The design agent's own words
- **WHEN** the design agent runs `crew record crew 31 --proposed --settled-in-pane --excerpt "<words>"`, and the words are only in what the design agent wrote itself
- **THEN** crew refuses, saying only the user's own words in the pane settle a record and to run `crew record crew 31 --proposed` so the user answers on its card, and records nothing

#### Scenario: Another agent's tell of the user's yes
- **WHEN** the words are in the design agent's transcript only in a `[crew tell from swancloud-planner]` message
- **THEN** crew refuses, naming swancloud-planner as the one who said them, and records nothing

#### Scenario: Words crew cannot read as anyone's
- **WHEN** the words are only in crew's own message, in a tool's output, or in a record crew can't classify
- **THEN** crew refuses, saying which, and records nothing

#### Scenario: A transcript crew cannot read
- **WHEN** the caller's session has no transcript on this host, its transcript can't be read, or it has not been written for more than 15 minutes
- **THEN** crew refuses with that reason and records nothing

#### Scenario: Another caller
- **WHEN** an agent other than the partition's design agent, or the user at a terminal, runs `crew record … --proposed --settled-in-pane --excerpt "<words>"`
- **THEN** crew refuses, saying only the design agent records a record settled in its pane, and records nothing

#### Scenario: A flag without the other
- **WHEN** `--settled-in-pane` is given without `--excerpt`, or `--excerpt` without `--settled-in-pane`
- **THEN** crew refuses, naming the flag that is missing, and records nothing

### Requirement: A landing said in ops's pane is checked as the user's words before it is submitted
When the word to land is the user's own words in main-level ops's pane, ops SHALL run `crew bolt submit <bolt> --excerpt "<the user's words>"`. Before anything is submitted, crew SHALL look for the words in the caller's own live session transcript, on the host where the command runs, and SHALL go on only when it finds them in a record the session received that it reads as the user's under `signals.5`: typed in the pane, or a `crew tell` from `<user>@<host>`. A later echo of the same words, in a tool's output or a tell, SHALL NOT hide the user's record. crew SHALL refuse the command, submitting nothing and recording no word to land, in each of these cases:
- the words are not in the transcript, or are only in what the agent wrote itself;
- the record holding them is a tool's output, crew's own message, or another agent's tell, which the refusal names;
- crew cannot read the transcript, or cannot tell that it is the live session's.

A landing on the user's words SHALL be recorded on the landing's `bolt.submit` entry, naming the caller, its session, the transcript record the words were read from and the words' length, and holding none of the words (`record.3`); a refusal SHALL record crew's own message alone. Without `--excerpt`, `crew bolt submit` SHALL land on the landing card's approval as before, and its entry SHALL name no transcript record. Several bolts landed on one sentence SHALL be named in one command, in order, their words read once before any is submitted, and each landed bolt's entry SHALL name the same record.

#### Scenario: Typed in ops's pane
- **WHEN** the user types "Land crw-5's bolt" in swancloud-ops's pane, and ops runs `crew bolt submit y --excerpt "Land crw-5's bolt"`
- **THEN** the bolt is submitted to main, and the `bolt.submit` entry names the transcript record and the length of the words, and none of the words

#### Scenario: Through the rail's answer command
- **WHEN** the user runs `crew tell swancloud-ops "Land bolt y."` at a shell, and ops runs `crew bolt submit y --excerpt "Land bolt y."`
- **THEN** the bolt is submitted, since a tell from `<user>@<host>` is the user's

#### Scenario: Ops's own words
- **WHEN** ops writes "the user wants bolt y landed" in its own reply and runs `crew bolt submit y --excerpt "the user wants bolt y landed"`
- **THEN** the command is refused, saying the words are not in a record the session received, nothing is submitted and main is where it was

#### Scenario: Words another agent passed on
- **WHEN** swancloud-operator tells ops "The user says land bolt y", and ops runs `crew bolt submit y` with those words
- **THEN** the command is refused, naming swancloud-operator as the one who said them and saying the user lands a bolt on its card or in ops's pane, and nothing is submitted

#### Scenario: The card's approval
- **WHEN** crw-5's conductor tells ops "Land bolt y. The user approved it on Pending You.", and ops runs `crew bolt submit y`
- **THEN** the bolt is submitted as before, and its entry names no transcript record

### Requirement: A landing said in ops's pane closes its card naming the user's words
When a bolt whose landing was submitted on the user's words in ops's pane is closed by `crew bolt land`, crew SHALL say on its kit's landings card, first, that it landed on the user's word in ops's pane, with the user's words, then where GitHub's main holds the landing: changing the card in place while other rows can still land, and once none can, closing it with those words, as any landing card of the bolt's own its conductor still holds closes; the run record SHALL keep the close's outcome without the words. A card still waiting on the user SHALL be closed as answered in the conversation, so that Pending You shows it answered rather than only withdrawn. When `crew bolt land` cannot read the words back, because it runs on another host than the submission did, the card SHALL close naming in whose pane and when the word was given, without the words, and the command SHALL say so. A landing on the card's approval SHALL close its card as before.

#### Scenario: The card closes with the user's words
- **WHEN** ops submitted bolt `y` on the user's words "Land crw-5's bolt" in its pane, and runs `crew bolt land y`
- **THEN** `land/crew`, with no other row that can land, closes as answered in the conversation, "Landed on the user's word in swancloud-ops's pane, "Land crw-5's bolt"; landed on GitHub's main at `<sha>` (#<n>); …", and the `card.close` entry's outcome holds no words of the user's

#### Scenario: Another row still waits
- **WHEN** ops submitted bolt `y` on the user's words in its pane, bolt `z` of crew is a row of `land/crew` that can land, and `crew bolt land y` runs
- **THEN** `land/crew` is changed in place, saying first that `y` landed on the user's word in swancloud-ops's pane with their words, and `z` stays its row

#### Scenario: Closed on another host
- **WHEN** bolt `y` was submitted on the user's words on deneb, and `crew bolt land y` runs on mac-studio
- **THEN** `land/crew` closes naming swancloud-ops's pane and the time of the word, with no words, and the command says the words are kept on deneb

#### Scenario: Landed on the card
- **WHEN** the user sent `land/crew` with `y` ticked on Pending You, and ops ran `crew bolt submit y`, which closed `y` as it landed
- **THEN** `land/crew` closes as any landings card the user answered, naming no pane

### Requirement: Ops lands a bolt on a send that still stands
`crew card read land/<kit>` SHALL name each bolt an earlier send of the user's still lands, at its head now, with the `crew bolt submit` that lands it, whether or not a landings card of the kit is open; a bolt whose head now crew cannot read SHALL be named as one it cannot tell of, and left out of the command. Main-level ops SHALL land such a bolt on that send, asking the user nothing, once its conductor says it is proven.

#### Scenario: No card open
- **WHEN** the user's send on `land/crew` ticked `z`, its card closed with `z` held for sluice's refusal, `z`'s take-main fix has merged, and no landings card of crew is open
- **THEN** `crew card read land/crew` by swancloud-ops names `z` as landing on the user's earlier send and prints `crew bolt submit z --label swancloud`, and refuses nothing

#### Scenario: A head crew cannot read
- **WHEN** an earlier send ticked `z`, and `z`'s branch is on no ref crew can read where the kit's forecasts are made
- **THEN** `crew card read land/crew` says it cannot tell whether the send still lands `z`, and why, and the command it prints leaves `z` out

#### Scenario: The brief lands on a standing send
- **WHEN** main-level ops's brief is read
- **THEN** it says a bolt the user ticked whose head moved only by taking main in lands on that send once its conductor says it is proven, with nothing asked, and that the user's words in ops's pane stand the same way

### Requirement: A landing stopped in ops's pane is recorded as the user's words
When the user's own words in main-level ops's pane stop a bolt's landing, ops SHALL run `crew bolt leave <bolt>... --excerpt "<the user's words>"`. Before recording anything, crew SHALL read the words in the caller's own live session transcript as it reads a landing said in ops's pane, and SHALL refuse in the same cases, recording no stop. A stop SHALL be recorded on each bolt as a `bolt.leave` entry naming its head, the caller, its session, the transcript record the words were read from and the words' length, and holding none of the words (`record.3`), and crew SHALL raise the bolt's kit's landings card. A stop SHALL end when the user ticks the bolt on a send of that card, when ops lands it on the user's words, or when its head moves.

#### Scenario: Stopped in the pane
- **WHEN** the user types "Hold the phone bolt, don't land it yet" in swancloud-ops's pane, and ops runs `crew bolt leave builds-reach-the-phone --excerpt "Hold the phone bolt, don't land it yet"`
- **THEN** a `bolt.leave` entry on `bolt/builds-reach-the-phone` is recorded with its head, the transcript record and the words' length, and none of the words, and `land/swancloud` is raised showing it unticked as left

#### Scenario: Words that are not the user's
- **WHEN** ops runs `crew bolt leave builds-reach-the-phone --excerpt "<words>"` with words only another agent's tell holds
- **THEN** crew refuses, naming the tell, and records no stop

#### Scenario: Landed on their words later
- **WHEN** the user later tells ops to land the bolt, and ops runs `crew bolt submit builds-reach-the-phone --excerpt "<their words>"`
- **THEN** the stop ends, and the bolt is no longer left

### Requirement: A red main's fix is a fix place on main where a crossed team builds the kit
`crew main fix <kit> <name> "<the failure's words>"`, main-level ops's or the user's on reading the kit's main red after a landing, SHALL append a launch of the fix kind on `main`, named `main--<name>`, its brief the failure's words, its submission held and its recipient `<label>/ops`, on the host of the crossed team that builds the kit, `--team` choosing among several and required when they run on different hosts. `--drop` SHALL drop it.

#### Scenario: Main red after a landing
- **WHEN** crew's main fails its checks after a landing, crw-4 is crossed and builds crew, and ops runs `crew main fix crew a-test-reads-its-fixture "<the check's words>"`
- **THEN** `requests.rec` gains a launch of `fix` named `main--a-test-reads-its-fixture` on `main`, its submission held, recipient `madswan/ops`, on deneb

### Requirement: A red main's fix stays a bolt of one chore where no crossed team builds the kit
Where no crossed team builds the kit, `crew main fix` SHALL be refused, naming a bolt of one chore, proposed first among the planned, as the way.

#### Scenario: No crossed team builds the kit
- **WHEN** no crossed team builds switchboard-kit and ops runs `crew main fix switchboard-kit gate-word "<words>"`
- **THEN** it is refused, naming a bolt of one chore proposed first among the planned

### Requirement: A fix of main lands on the user's send
Once a fix of main's code has delivered and its submission waits held, the kit's landings row SHALL carry it; `crew main fix <kit> <name> --send`, ops's on the user's send and read as a landing's words are, SHALL append the retry of its submission, and nothing else SHALL submit it.

#### Scenario: The user's send
- **WHEN** the runner's record shows `main--a-test-reads-its-fixture`'s code delivered and its submission held, and the user sends the kit's landings card with it ticked
- **THEN** ops's `crew main fix crew a-test-reads-its-fixture --send` appends a retry of its submission

### Requirement: A role that runs as its kind is not started by crew-role
`crew-role <label> <role>`, fresh or with `resume`, SHALL refuse a role its partition runs as its kind, naming `crew role open <role> --label <label>`, and start no Claude. `crew main status <label>` SHALL say of each such role that it runs as its kind, whether the runner's records show a run of it standing, and how many asks wait for it since when.

#### Scenario: The planner started by hand
- **WHEN** madswan's planner runs as its kind and `crew-role madswan planner` runs
- **THEN** it refuses, saying madswan's planner runs as its kind and is opened with `crew role open planner --label madswan`, and no Claude starts

#### Scenario: Main status
- **WHEN** madswan's planner runs as its kind, two asks of it wait and no run of it stands, and `crew main status madswan` runs
- **THEN** it says the planner runs as its kind, that no run stands, and that two asks wait, with the oldest's age

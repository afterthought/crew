# main-level Specification

## Purpose
Above a partition's bolt teams: a design agent that elaborates on main, a planner across the bolts, a dispatcher on each host that runs them, and ops that lands them. Signals are what reaches them from outside.

## Requirements

### Requirement: Partitions are declared in the teams file
`teams.json` SHALL list each partition with a main level. Each entry gives the partition's label (`wldn`, `madswan`, `swancloud`), its swancloud name, its blueprints repos, its state repository (`state`, as `<owner>/<name>`), and the machine and session its main level runs in. The first blueprints repo listed SHALL be the one the partition's signals and elaboration go to by default. A partition with no `state` SHALL be an error naming the field and the machine's configuration as the fix, never a default.

#### Scenario: clients/willdan
- **WHEN** `teams.json` lists `wldn` as `clients/willdan` with willdan-blueprints and `WilldanGroup/crew-state`, running on the box in `wldn-2`
- **THEN** `crew main up wldn` starts its main level in `wldn-2` on the box, and wldn's plan is read from `wldn/main` of `WilldanGroup/crew-state`

#### Scenario: A partition with no state repository
- **WHEN** a partition's entry has no `state`
- **THEN** crew refuses to load the teams file, naming the partition and the missing field

### Requirement: The main level is one herdr workspace
`crew main up <label>` SHALL open a herdr workspace named `<label>` in the main level's session. It SHALL hold a `design` tab with the design agent, a `planner` tab with the planner, and an `ops` tab with the main-level ops, and start each. It SHALL then start a dispatcher on every host where the partition's teams run.

Every agent crew starts outside a team, the main level's three, each dispatcher and the operator agent, SHALL be greeted once it is up, exactly once per start, as a team's conductor is: told to read where the partition stands and carry on with what is its role's. The greeting SHALL be marked as crew's. An agent brought back by `crew revive` or `crew main up` after the main level was taken down SHALL be greeted the same way, so none sits idle until someone tells it what to do.

#### Scenario: The main level comes up
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-design`, `wldn-planner` and `wldn-ops` start in the `wldn` workspace, and `wldn-dispatch-chuck-herdr-alpha` starts on the box, and each is greeted once it is up

#### Scenario: The main level comes back
- **WHEN** the user runs `crew main down swancloud` and then `crew main up swancloud`
- **THEN** each of its agents starts and is greeted, and picks up its role from the rail and the bolts without the user or the operator agent telling it to

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
The main-level ops SHALL land a bolt whose verification is green on the user's word, given by approving the bolt's landing card, which the bolt's conductor posts and passes on with `crew tell`, or said in ops's own pane: it SHALL submit the bolt to main through sluice with `crew bolt submit <bolt>`, push main without force, run `crew bolt land`, and, for crew, bring every host's checkout up to main. It SHALL move no branch by git, and SHALL stop and tell the user when the kit's main is behind GitHub's or GitHub refuses the push. A landing that does not land SHALL be told to the bolt's conductor in sluice's words. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

#### Scenario: Landing
- **WHEN** the user approves swb-1's landing card and its conductor tells the main-level ops
- **THEN** the main-level ops runs `crew bolt submit`, pushes main, runs `crew bolt land`, and the plan no longer holds the bolt

#### Scenario: A landing that conflicts
- **WHEN** `crew bolt submit` fails because the bolt conflicts with main
- **THEN** the main-level ops moves nothing, and tells the bolt's conductor and the user sluice's words

#### Scenario: No word from the planner
- **WHEN** the planner tells the main-level ops that a bolt may land
- **THEN** the main-level ops lands nothing until the user's approval of the landing card, or the user's words in its pane

#### Scenario: A landing deploys nothing
- **WHEN** a swancloud bolt lands
- **THEN** nothing is deployed by the landing, and main is deployed only by a later act on the user's word for that deploy

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
`crew tell <agent> "<text>"` SHALL prompt any agent crew starts, by its name alone, in the host and session where it runs. An agent that is not up SHALL be reported and the command SHALL fail, with nothing sent. An agent waiting on a question in its pane SHALL be reported the same way, naming the wait, and nothing SHALL be typed into the question: a tell is delivered as a prompt the agent receives, never as text that lands in a dialog and is lost. An agent is waiting on a question when herdr reports it blocked, or when it has opened a question or a plan for the user's answer in Claude Code and that call has no answer yet in its session, however the dialog looks on screen. When crew cannot read whether the agent is waiting on a question, it SHALL refuse the same way, naming what it could not read, and type nothing. crew's greetings and notices SHALL be delivered on the same terms.

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

### Requirement: Main-level ops reports results as one glyph per line
Whenever the main-level ops reports the results of a landing's checks, of main's deploy or of any test or proof it ran, it SHALL list them first, before any prose, one bullet per suite, check or proof: ✅ passed, with its counts where the tool gave them; ❌ failed, with how many failed and one line on why; ⏳ not yet run, or still running. It SHALL NOT state a result only in a sentence, nor fold several into one bullet.

#### Scenario: A landing whose gate is still running
- **WHEN** the main-level ops reports a landing while the merge's checks still run
- **THEN** its message opens with a ⏳ bullet for those checks, and says the bolt has not landed yet

#### Scenario: A landing that went through
- **WHEN** the merge's checks passed and main was deployed and found healthy
- **THEN** its message opens with a ✅ bullet for the checks, with their counts, and one for main's deploy, before it says the bolt is closed

### Requirement: A deploy and every operation are approved and recorded through crew
A kit's deployer SHALL ask crew for each deploy of a `manual` environment with `crew ops offer <env> --to <sha> --from <sha|none> [--notes <file>] [--steps <file>]`, the notes file the kit's release notes for the range from the environment's last deployed commit to the offered one as the kit's changelog tool writes them, the steps file the range's after-deploy steps one a line as the deployer gathers them (`step <n> <doer> <when> <environments> <why> <text>`), which SHALL raise the deploy's card in main-level ops's name, keyed `deploy/<env>`, with the notes and the steps on its face and nothing of them written by crew, change it when a newer head is offered, and tell main-level ops the line that adopts it, `call get_request (requestId <id>, name <role>)`; the user's word SHALL be holding that card, recorded with `crew ops approve`. `crew ops record --act end` SHALL close the card with the deploy's outcome. `crew ops step` SHALL raise a step's card, keyed `op/<env>/<n>`, when the step's doer is the user or the step is marked held for the user's word, SHALL change it when the step is recorded again while it is open with other words, another doer or another hold, printing the line that adopts it whether it changed it or not, and SHALL close it when the step is recorded done or declined. `crew ops word` SHALL give the commit the word is for until that deploy's end is recorded. Every `crew ops` command SHALL run where the partition's main level runs.

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
`crew record <kit> <number> --proposed` SHALL put the record at its commit on its card in the design agent's name, raising the card the first time and changing it in place at each new commit, unless `--settled-in-pane` says the user settled it in the pane; with `--alternatives <file>`, which hands the Markdown of the alternatives a rule of the user's decided between, the rules and each loosened, the card SHALL be a choice.

#### Scenario: A record a rule decided
- **WHEN** the design agent runs `crew record switchboard-kit 32 --proposed --alternatives docs/adr/0032-alternatives.md`
- **THEN** the card is a choice of loosening the rules as drafted, accepting as ruled, or sending back, with the file on its face, and the design agent is woken by the answer

#### Scenario: A record settled in the pane
- **WHEN** the design agent commits record 31 as proposed after the user settled it beside them and runs `crew record crew 31 --proposed --settled-in-pane`
- **THEN** the status is recorded with the user's yes as given in the pane, and no card is raised

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

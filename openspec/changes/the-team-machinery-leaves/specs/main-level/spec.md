## ADDED Requirements

### Requirement: The planner plans across bolts by proposal alone
The planner SHALL be the only agent that proposes bolts, the placing of units into bolts, and their splitting, ordering or moving between bolts, and SHALL change the plan only through a proposal the user approves. It SHALL route signals to work. A change to a bolt in flight SHALL wait on the user's approval alone. The planner SHALL NOT start a unit's stage.

An intent the planner writes SHALL name the outcome, and the unit's sources SHALL name the records that govern it; the intent SHALL NOT name the mechanism. Corrections to a unit whose construct is still running SHALL be held and proposed as one amendment once that construct has settled, unless one of them blocks the bolt's work now, which SHALL be proposed at once with the others held so far.

#### Scenario: A finding mid-bolt
- **WHEN** a stage stops short reporting that a unit needs work outside its bolt's goal
- **THEN** the planner proposes queuing that work or adding it to another bolt, and the bolt keeps its goal

#### Scenario: New work beside a bolt in flight
- **WHEN** the planner judges that new work belongs in a bolt in flight
- **THEN** it proposes the unit for that bolt, no agent's agreement is asked, and the unit is in the bolt only once the user has approved the proposal

#### Scenario: A changed mechanism
- **WHEN** a construct finds that the way a unit's sources describe doing something won't work, and the records are amended
- **THEN** the unit's intent still holds, and the planner proposes no amendment for it

#### Scenario: Corrections arrive during construct
- **WHEN** two corrections to a unit arrive while its construct is still running, and neither stops the bolt's work
- **THEN** the planner holds both, and once the construct has settled proposes one `unit amend` that carries both

#### Scenario: A correction that blocks the bolt's work
- **WHEN** a correction arrives without which the unit's construct, or another unit, cannot go on
- **THEN** the planner proposes the amendment at once, with any other corrections it holds for that unit

### Requirement: Any agent crew starts is reached by its name
`crew tell <agent> "<text>"` SHALL prompt any agent crew starts, by its name alone, in the host and session where it runs. An agent that is not up SHALL be reported and the command SHALL fail, with nothing sent. An agent waiting on a question in its pane SHALL be reported the same way, naming the wait, and nothing SHALL be typed into the question: a tell is delivered as a prompt the agent receives, never as text that lands in a dialog and is lost. An agent is waiting on a question when herdr reports it blocked, or when it has opened a question or a plan for the user's answer in Claude Code and that call has no answer yet in its session, however the dialog looks on screen. The agent's session is the one herdr names for its pane, or, when herdr names none, the newest session crew recorded of that agent starting in that pane. When neither names a session, herdr's reading of the pane alone SHALL guard the tell, and a missing session SHALL NOT refuse it. When crew cannot read whether the agent is waiting on a question, it SHALL refuse the same way, naming what it could not read, and type nothing. crew's greetings and notices SHALL be delivered on the same terms.

#### Scenario: The planner asks the design agent
- **WHEN** `wldn-planner` on the box runs `crew tell wldn-design "<question>"`
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

#### Scenario: An agent greeted while it waits on a question
- **WHEN** crew greets `wldn-ops` while it has a question open which herdr reports as idle
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

### Requirement: A greeting to a main-level agent is taken or sent again
A greeting crew sends to any agent it starts SHALL be sent only once the agent is ready for input, and crew SHALL then read the agent's transcript to see that Claude received it within a short time. When it does not, and the agent sits idle or done, crew SHALL clear what was left typed in the agent's input and send the greeting once more. Exactly one greeting SHALL reach the agent per start.

#### Scenario: A greeting taken at once
- **WHEN** `crew main up wldn` starts `wldn-ops` and its transcript shows the greeting received moments after crew sent it
- **THEN** crew says wldn-ops was greeted, records one greeting, and sent it once

#### Scenario: A greeting left typed
- **WHEN** crew greets wldn-planner and the planner's transcript shows nothing received within the time, while it sits idle
- **THEN** crew clears the planner's input, sends the greeting once more, and says it was greeted once the transcript shows it

### Requirement: A main-level agent resumed off its host is given no identity, and nothing else of crew's is
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

#### Scenario: A team's agent from before
- **WHEN** herdr resumes a session whose record names `crw-5-conductor` or `swancloud-dispatch-deneb`
- **THEN** it is given no name, identity or brief, crew modelling no such agent

## MODIFIED Requirements

### Requirement: The main level is one herdr workspace
`crew main up <label>` SHALL open a herdr workspace named `<label>` in the main level's session. It SHALL hold a `design` tab with the design agent, a `planner` tab with the planner, an `ops` tab with the main-level ops and an `operator` tab with the partition's operator, and start each, and nothing else.

Every agent crew starts, the main level's four, SHALL be greeted once it is up, exactly once per start: told to read where the partition stands and carry on with what is its role's. The greeting SHALL be marked as crew's. An agent brought back by `crew revive` or `crew main up` after the main level was taken down SHALL be greeted the same way, so none sits idle until someone tells it what to do.

#### Scenario: The main level comes up
- **WHEN** `crew main up wldn` runs
- **THEN** `wldn-design`, `wldn-planner`, `wldn-ops` and `wldn-operator` start in the `wldn` workspace, each is greeted once it is up, and no dispatcher starts on any host

#### Scenario: The main level comes back
- **WHEN** the user runs `crew main down swancloud` and then `crew main up swancloud`
- **THEN** each of its agents starts and is greeted, and picks up its role from the rail and the bolts without the user or the operator telling it to

#### Scenario: Brought up again while it is up
- **WHEN** `crew main up wldn` runs while its agents are up
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
The design agent SHALL keep the partition's design true on main: the books, specs and constitution in its blueprints repos and kits, the decision records, and the curation of signals with the moves `attach`, `challenge`, `new-territory`, `answered` and `drop`, each written only through `crew signal move`. It SHALL answer a design question a stage, the planner or ops brings it. Work its elaboration calls for SHALL be queued as units, never put into a bolt by the design agent, each with an intent that names the outcome and sources that name the records governing it, never the mechanism.

A ruling the design agent gives about how a service or a system behaves SHALL name, in the message that carries it, the documentation page or the reading it rests on. Before ruling about something that exists, the design agent SHALL read it itself with the credentials it has: the live configuration, the stack, the policy, the code on main. Where it has neither documentation nor a reading, it SHALL say so and ask for the reading, and SHALL give no ruling on that point until the reading is back. A ruling SHALL say what must be true and what must not change, and SHALL leave the steps to the construct. A construct's linked questions SHALL be answered together, in one answer, after reading.

#### Scenario: Elaboration produces work
- **WHEN** the design agent records a decision that needs building
- **THEN** it queues a unit whose intent says what becomes true and whose source is the decision's page, and tells the planner

#### Scenario: A question about a live service
- **WHEN** a question reaches the design agent asking whether an existing CloudFormation stack can take over a resource, and the design agent can read the stack with its credentials
- **THEN** it reads the stack and the service's documentation before answering, and its answer names the page and the reading it rests on

#### Scenario: Nothing to rest a ruling on
- **WHEN** a question turns on how a service behaves, and the design agent can neither find the documentation nor read the thing itself
- **THEN** it says so, names the reading it needs and asks for it, and rules on that point only once the reading is back

#### Scenario: A sequence is asked for
- **WHEN** a construct asks in what order to take over an AWS boundary
- **THEN** the design agent answers with what must be true when the takeover is done and what must not change along the way, and the construct works out the steps from its own reading

#### Scenario: Linked questions
- **WHEN** three questions from one construct about the same stack reach the design agent together
- **THEN** the design agent reads what they turn on and answers all three in one message

### Requirement: Ops lands a bolt on a send that still stands
`crew card read land/<kit>` SHALL name each bolt an earlier send of the user's still lands, at its head now, with the `crew bolt submit` that lands it, whether or not a landings card of the kit is open; a bolt whose head now crew cannot read SHALL be named as one it cannot tell of, and left out of the command. Main-level ops SHALL land such a bolt on that send, asking the user nothing, once `crew bolts` reads it proven.

#### Scenario: No card open
- **WHEN** the user's send on `land/crew` ticked `z`, its card closed with `z` held for sluice's refusal, `z`'s take-main fix has merged, and no landings card of crew is open
- **THEN** `crew card read land/crew` by swancloud-ops names `z` as landing on the user's earlier send and prints `crew bolt submit z --label swancloud`, and refuses nothing

#### Scenario: A head crew cannot read
- **WHEN** an earlier send ticked `z`, and `z`'s branch is on no ref crew can read where the kit's forecasts are made
- **THEN** `crew card read land/crew` says it cannot tell whether the send still lands `z`, and why, and the command it prints leaves `z` out

#### Scenario: The brief lands on a standing send
- **WHEN** main-level ops's brief is read
- **THEN** it says a bolt the user ticked whose head moved only by taking main in lands on that send once `crew bolts` reads it proven, with nothing asked, and that the user's words in ops's pane stand the same way

### Requirement: Main-level ops lands bolts by one procedure
The main-level ops SHALL land bolts whose verification is green on the user's word: their send on a kit's landings card, which crew raises in ops's name, the word for every bolt they ticked, in the card's order unless their note moves one; or their words in ops's own pane. It SHALL submit them with one `crew bolt submit <bolt>...` in that order, which queues each in sluice behind the one before and closes each with `crew bolt land` as it lands. It SHALL push nothing, level no host and move no branch by git. A bolt that does not land for its own content, a conflict or a failed check, SHALL be held on its row in sluice's words, the rest going on. A bolt whose landing sluice or its host stopped SHALL be reported as a finding outside any bolt and submitted again by the same `crew bolt submit` once what stopped it is cleared, on the word it has, with no new word of the user's. A landing SHALL deploy nothing. Until a kit's deployer records its deploys through crew, the main-level ops SHALL deploy that kit's main only on the user's word for that deploy. A failure after landing SHALL be a fix on main.

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
- **THEN** the main-level ops moves nothing, tells the user sluice's words, `y` held on its row, and `z` lands all the same

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
- **THEN** the main-level ops holds nothing on `y`'s row, records what stopped it as a signal and tells the planner, `z` lands all the same, and once the host runs checks again ops runs `crew bolt submit y` on the user's send that still stands, asking the user nothing

## REMOVED Requirements

### Requirement: A dispatcher allocates each host's work
**Reason**: Record 0047 move 5, record 0050 part 3: the dispatcher leaves with the teams it gave bolts to; what runs is the user's choice on the rail, reaching Flume as each place's priority.
**Migration**: None in crew: the crossed path's launch and the rail's order (`teams-cross-to-flume-as-their-bolts-land`).

### Requirement: The planner plans across bolts
**Reason**: Record 0047 move 5: no conductor agrees to a change to its bolt (`plan.4`), and there is no team for a correction to block.
**Migration**: "The planner plans across bolts by proposal alone", added by this change.

### Requirement: Any agent crew starts is reached by name
**Reason**: Record 0047 move 5: no conductor; its two scenarios of a conductor's tell and a conductor's greeting leave.
**Migration**: "Any agent crew starts is reached by its name", added by this change.

### Requirement: A greeting is taken or sent again
**Reason**: Record 0047 move 5: no conductor is greeted; its scenario of a team's `crew up` leaves.
**Migration**: "A greeting to a main-level agent is taken or sent again", added by this change.

### Requirement: A main-level agent resumed off its host is given no identity
**Reason**: Record 0047 move 5: no team's agent or dispatcher is resumed with an identity of crew's.
**Migration**: "A main-level agent resumed off its host is given no identity, and nothing else of crew's is", added by this change.

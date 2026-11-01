## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: A role that runs as its kind is not started by crew-role
`crew-role <label> <role>`, fresh or with `resume`, SHALL refuse a role its partition runs as its kind, naming `crew role open <role> --label <label>`, and start no Claude. `crew main status <label>` SHALL say of each such role that it runs as its kind, whether the runner's records show a run of it standing, and how many asks wait for it since when.

#### Scenario: The planner started by hand
- **WHEN** madswan's planner runs as its kind and `crew-role madswan planner` runs
- **THEN** it refuses, saying madswan's planner runs as its kind and is opened with `crew role open planner --label madswan`, and no Claude starts

#### Scenario: Main status
- **WHEN** madswan's planner runs as its kind, two asks of it wait and no run of it stands, and `crew main status madswan` runs
- **THEN** it says the planner runs as its kind, that no run stands, and that two asks wait, with the oldest's age

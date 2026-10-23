# host-holds-and-updates Specification

## Purpose
How crew is put on the brakes, a host at a time, before herdr is upgraded or a host rebooted, and how an update of crew, or of an agent's brief, reaches every standing agent at its next stop, each agent's band saying the crew it runs (`teams.19`).

## Requirements

### Requirement: A host can be held
`crew hold <host>|--all "<why>"` SHALL hold each host named, or every host crew runs agents on: crew SHALL start no agent there until `crew go`, refusing with the hold's words every command that would, and SHALL tell every standing agent up there to finish the step it is in and start nothing new. A stage already running SHALL end as it would. With `--now` crew SHALL end every crew agent there at once. The run record SHALL name the host and never the why.

#### Scenario: Held
- **WHEN** the user runs `crew hold deneb "herdr 0.9.6"`
- **THEN** each standing agent up on deneb is told the hold, and `crew up crw-4` on deneb is refused naming who held it and why

#### Scenario: Held at once
- **WHEN** the user runs `crew hold --all "reboot" --now`
- **THEN** every crew agent on every host crew runs agents on is ended, each stage's end recorded, and its conductor runs it again after go

### Requirement: A held host says when it is quiet
`crew hold status` SHALL say what still works on each held host: an agent working, one waiting on a question to the user, one running background work of its own other than crew's waits, a stage not yet ended, and crew's tests running. `crew hold wait` SHALL wait until each host is quiet and then end every crew agent there, its panes kept, and SHALL stop at its timeout saying what still works.

#### Scenario: Waiting on a submission
- **WHEN** swancloud-ops runs `wt submit main` in the background on a held host
- **THEN** `crew hold status` names it, and `crew hold wait` ends nothing until the submission is over

### Requirement: Go lifts a hold
`crew go <host>|--all` SHALL lift the hold, bring each standing agent whose pane is empty back with its conversation, greeted as `crew revive` greets it, tell each one still up that the hold is lifted, run each console's tabs again, and restart every agent an update made due.

#### Scenario: After herdr's restart
- **WHEN** the user restarts herdr on a host whose agents `crew hold wait` ended, then runs `crew go` there
- **THEN** each standing agent is back with its conversation, its effort, mode and folders, and the conductors are greeted

### Requirement: An update makes a standing agent due a restart
crew SHALL record at each agent's start the crew it loaded and what it was started with. A standing agent whose brief, model, effort or folders changed since, or whose loaded part of crew's plugin changed, SHALL be due a restart; a change to crew's code alone SHALL make none due, since every command runs crew's checkout as it is.

#### Scenario: A brief changed
- **WHEN** a landing changes the planner's brief
- **THEN** the planner is due a restart

#### Scenario: Code alone changed
- **WHEN** a landing changes only `plugin/lib/plan.py`
- **THEN** no agent is due

### Requirement: A due agent is restarted at its next stop
crew SHALL restart a due agent once herdr reads it idle with no question open and no background work of its own but crew's waits: at the end of its turn, and for one sitting idle when crew's checkout or the teams file moves or on `crew update`. A conductor SHALL start fresh; every other standing role SHALL resume its conversation and be told what changed. Nothing SHALL be restarted on a held host. A restart SHALL end with its agent running: on crew as it now is once the agent has exited, or as it was when it could not be ended. A restart whose agent has not exited when its stop gives up SHALL watch it for ten minutes and start it the moment it exits; one whose agent still runs after that SHALL leave it running, still due, and say so. A later restart that finds the agent exited by an earlier restart's keys, its pane kept and no start of it since, SHALL start it without a stop. No restart SHALL leave its agent's pane a shell with no agent in it.

#### Scenario: At the end of its turn
- **WHEN** the planner is due and ends its turn
- **THEN** the planner is resumed with its new brief and told the crew it now runs and what changed

#### Scenario: Running a submission
- **WHEN** swancloud-ops is due and runs `wt submit main` in the background
- **THEN** it is restarted only once the submission is over and its turn ends

#### Scenario: Slow to exit
- **WHEN** swb-1-ops is due and is restarted, and it is still up when the stop's `/exit` and Ctrl+C have had their time, then exits a few seconds later
- **THEN** it is resumed on crew as it now is and told what changed, and its restart's log ends "swb-1-ops is restarted on crew"

#### Scenario: Never exits
- **WHEN** swb-1-ops is due and is restarted, and it is still up ten minutes after its stop gave up
- **THEN** it is left running as it was, nothing is started in its pane, and its restart's log says it did not exit and runs on, its next turn's end handing it back

#### Scenario: Exits after the restart gave up
- **WHEN** a restart of swb-1-ops gave up and left it running, and it later exits with its pane kept and nothing has started it since, and its restart is handed again
- **THEN** that restart starts it in its pane without a stop, resumed and told what changed

#### Scenario: Exited by something else
- **WHEN** swb-1-ops is due and not up, and no restart of its session gave up on it, or its team was taken down with `crew down`
- **THEN** the restart starts nothing and says it is not up

### Requirement: A band shows the crew its agent runs
Each standing agent's band SHALL show the crew version it started on, and once it is due the version it takes at its next stop. Every band on a held host SHALL open with the hold: who held it, since when and why.

#### Scenario: Due
- **WHEN** the planner started on crew v0.12.1 and v0.13.0 changed its brief
- **THEN** its band's first line ends with "crew v0.12.1 → v0.13.0 at its next stop"

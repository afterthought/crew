## MODIFIED Requirements

### Requirement: A host can be held
`crew hold <host>|--all "<why>"` SHALL hold each host named, or every host crew runs agents on, the hosts of its partitions' main levels: crew SHALL start no agent there until `crew go`, refusing with the hold's words every command that would, and SHALL tell every standing agent up there to finish the step it is in and start nothing new. With `--now` crew SHALL end every crew agent there at once. The run record SHALL name the host and never the why.

#### Scenario: Held
- **WHEN** the user runs `crew hold deneb "herdr 0.9.6"`
- **THEN** each main-level agent up on deneb is told the hold, and `crew main up swancloud` on deneb is refused naming who held it and why

#### Scenario: Held at once
- **WHEN** the user runs `crew hold --all "reboot" --now`
- **THEN** every crew agent on every host crew runs agents on is ended, and each is brought back by `crew go`

### Requirement: Go lifts a hold
`crew go <host>|--all` SHALL lift the hold, bring each standing agent whose pane is empty back with its conversation, greeted as `crew revive` greets it, tell each one still up that the hold is lifted, run each console's tabs again, and restart every agent an update made due.

#### Scenario: After herdr's restart
- **WHEN** the user restarts herdr on a host whose agents `crew hold wait` ended, then runs `crew go` there
- **THEN** each main-level agent is back with its conversation, its effort, mode and folders, and greeted

### Requirement: A due agent is restarted at its next stop
crew SHALL restart a due agent once herdr reads it idle with no question open and no background work of its own but crew's waits: at the end of its turn, and for one sitting idle when crew's checkout or the teams file moves or on `crew update`. Every standing role SHALL resume its conversation and be told what changed. Nothing SHALL be restarted on a held host. A restart SHALL end with its agent running: on crew as it now is once the agent has exited, or as it was when it could not be ended. A restart whose agent has not exited when its stop gives up SHALL watch it for ten minutes and start it the moment it exits; one whose agent still runs after that SHALL leave it running, still due, and say so. A later restart that finds the agent exited by an earlier restart's keys, its pane kept and no start of it since, SHALL start it without a stop. No restart SHALL leave its agent's pane a shell with no agent in it.

#### Scenario: At the end of its turn
- **WHEN** the planner is due and ends its turn
- **THEN** the planner is resumed with its new brief and told the crew it now runs and what changed

#### Scenario: Running a submission
- **WHEN** swancloud-ops is due and is waiting in the background on a landing it submitted
- **THEN** it is restarted only once the submission is over and its turn ends

#### Scenario: Slow to exit
- **WHEN** swancloud-ops is due and is restarted, and it is still up when the stop's `/exit` and Ctrl+C have had their time, then exits a few seconds later
- **THEN** it is resumed on crew as it now is and told what changed, and its restart's log ends "swancloud-ops is restarted on crew"

#### Scenario: Never exits
- **WHEN** swancloud-ops is due and is restarted, and it is still up ten minutes after its stop gave up
- **THEN** it is left running as it was, nothing is started in its pane, and its restart's log says it did not exit and runs on, its next turn's end handing it back

#### Scenario: Exits after the restart gave up
- **WHEN** a restart of swancloud-ops gave up and left it running, and it later exits with its pane kept and nothing has started it since, and its restart is handed again
- **THEN** that restart starts it in its pane without a stop, resumed and told what changed

#### Scenario: Exited by something else
- **WHEN** swancloud-ops is due and not up, and no restart of its session gave up on it, or its main level was taken down with `crew main down`
- **THEN** the restart starts nothing and says it is not up

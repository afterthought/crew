## MODIFIED Requirements

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

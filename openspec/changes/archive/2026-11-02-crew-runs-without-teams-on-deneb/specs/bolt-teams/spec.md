## REMOVED Requirements

### Requirement: A conductor reads a stuck report before it asks
**Reason**: The conductor leaves crew with the rest of the team machinery (record 0047 move 5; `the-team-machinery-leaves`, whose archive this change brings back). crew starts no stage, waits on none and reports none stuck, so no conductor is left to read a stuck report. `a-stuck-report-carries-what-the-agent-said-and-did` (#430) added this requirement after that change was taken off main, so that change's deltas do not remove it.
**Migration**: A Flume place that stops short has its question shown to the planner, design or ops and is answered by a retry, as "A place is answered by a retry" has it. What a quiet place has done is Flume's to read and report.

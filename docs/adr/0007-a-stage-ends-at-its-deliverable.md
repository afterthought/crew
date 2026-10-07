# A stage ends at its deliverable, not at a quiet pane

- Status: proposed, for the user's reading
- Date: 2026-10-07
- Deciders: the user ("we have agents all over the place that are waiting on processes; pass to design and see what it comes up with"), through swancloud-operator-mac-studio; swancloud-design
- Sources: wldn-ops's findings on brd-1 (sessions ab0db8d8 and e9d417aa, 2026-10-07 17:19 to 19:21; stage-one-stands' fourth verify at 13:29, twice); `openspec/changes/run-record/design.md` ("A stage's end"); `plugin/roles/conductor.md` (running the stages; the building loop), `verify.md`, `coder.md`, `ops.md`; `openspec/specs/bolt-teams/spec.md`

## Context and problem statement

What was seen. A verify agent started the kit's suites in the background at 17:19:41 and ended its turn at 17:20:31 to wait for them; herdr showed it idle; `crew unit wait` returned at 17:20:33, "settled, in verify, 17/17 tasks", and recorded the stage's end; the suites' notice woke the agent at 17:20:35, and it wrote its report at 17:21. The end crew recorded named no report, so the conductor, told only that the stage had settled, waited by reading the agent's pane for a line that never came, and read the report two hours later. The same early end happened to another unit's verify twice that morning.

What crew does today. `crew unit wait` takes the first state herdr calls settled, idle, done or blocked, as the end of the stage, and records `stage.end` with the stage the kit now shows, the task count and the branch head. Verify's brief ends its reply with the report's path, for the conductor to read from the pane. Nothing in crew says what a stage must have produced for it to be over, so a pane that has gone quiet is the only sign there is, and an agent that stops to wait on a process it started, or on a tool, or on a question, looks the same as one that has finished.

The user's point: this is not about verify. Agents everywhere wait on processes.

## What must be true

1. **Every stage has one deliverable, and the stage ends when it exists.** The deliverable is a thing in the kit or on the team's host, read there, nothing kept by hand:

   | stage | its deliverable |
   |---|---|
   | construct | the change on the unit's branch, its planning complete |
   | code | every task ticked, each in a commit on the unit's branch |
   | verify | the report file for this run, under the team's reports folder |
   | merge | the merge commit on the bolt |
   | a fix's code, a chore's code | its commits on its branch |
   | ops's proof of a bolt | the proof file for the bolt |

   A stage can also end short: the agent stops and says what it needs, a decision, a fact about a live system, the user's word. That is an end too, with no deliverable, and it is told, not found.

2. **A quiet pane is never an end.** Between a stage's start and its deliverable the agent may end turns, start processes and wait on them, be woken by them, ask and be answered, any number of times. None of that is the end of the stage. A quiet pane with no deliverable and no stop-short means the stage is still running or is stuck; crew says which, and never "done".

3. **The end carries its outcome to whoever waits on it.** The one who waits on a stage, today the conductor through `crew unit wait`, learns the end together with what was delivered: the report's path, the merge's commit, the head with every task ticked; or that the agent stopped short, with what it needs in the agent's own words, carried by crew's message to the conductor and never by the run record. The conductor never reads a pane to learn a stage's outcome, and the run record's `stage.end` names the deliverable as an object, as it names the branch head.

4. **Stuck is reported, not waited out.** A stage whose agent has been quiet beyond a time crew sets, with no deliverable and no stop-short, is reported to the conductor as stuck, naming the stage and the agent, so that the conductor acts or asks the user; no agent waits two hours on a limit for an end that was already there.

5. **The same rule for every wait.** Whatever crew does for a unit's stages it does for a fix, a chore and ops's proof: each has its deliverable in the table, and whoever waits on it waits for that.

## What is left to the construct

How crew tells "still running" from "stuck", whether by the processes the agent started, by what the agent declares it waits on, by the harness's own notice of background work, or by the deliverable alone with a clock; how `crew unit wait` finds the deliverable for each stage; and whether an agent's brief changes how it waits. The record rules the outcome and the constraints above, and the construct brings its reading of herdr and the harness back.

## Considered options

1. The rule above: a stage ends at its deliverable or its stop-short, told with its outcome.
2. Keep herdr's settled state as the end, and have each brief tell its agent never to end a turn while something it started is running.
3. Keep herdr's settled state as the end, and have the conductor confirm the deliverable itself after each settle.

Option 2 fixes verify's case and nothing else: an agent that is asked a question, or that the harness wakes for its own reasons, is quiet without having finished, and the rule lives in every brief instead of in crew. Option 3 is what the conductor fell back to by hand, reading a pane for two hours; it keeps the knowledge of each stage's deliverable in the conductor's brief rather than in crew, where `crew bolts` already reads most of it.

## Consequences

- One unit in crew once the user accepts this: `crew unit wait`, the run record's `stage.end`, the conductor's and verify's briefs, the `run-record` and `bolt-teams` specs.
- The rail's verify row, "a report newer than the branch's head", becomes "the stage's deliverable exists and waits on the user", the same reading.

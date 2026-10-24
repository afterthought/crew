# A stuck report carries what the agent said and did

## Why

On 2026-10-23 slc-1's fix round committed its fix and went quiet; crew's wait found no deliverable, called the agent stuck after fifteen minutes with "nothing it needs said", and the conductor asked the user, though the agent's pane said what it had done and its branch held the commit (madswan signal 2026-10-23-slc-1-conductor-a4b46840/01). The user: "The agent just fucking didn't bother reading the pain and you're making it sound like it has to do with archiving. You're framing the problem wrong" (signal 2026-10-23-swancloud-design-02db4224/01). Record 0007 as amended that day, and `teams.4` with it, settle the frame: no stage is reported stuck, and nobody is asked about it, before crew has read what the agent last said and what its branch holds since the stage began, and the report carries both, so whoever reads it sees what the agent did without opening a pane.

## What Changes

- **A stuck report carries the agent's last words.** When a wait finds a quiet agent past crew's limit, it reads, from the agent's own Claude transcript, the last message the agent wrote since the stage began, and the report quotes it with its time. When the agent wrote nothing since the stage began, or crew can't read the transcript, the report says so and why.
- **A stuck report carries what the branch holds since the stage began.** The same look reads the commits on the stage's branch made since the stage began, newest first, each by its short sha and subject, and the report lists them, or says the branch holds none since the stage began at its head, or what crew could not read.
- **The report is read before it is made.** Both reads happen in the look that finds the agent stuck, before the wait answers; the wait never answers stuck on a verdict alone.
- **A code stage with no task list at its head delivers by its commits.** A code stage on a unit whose change is archived at its head, as a fix round's can be, ends at a commit since it began, as a fix's code does. The planner's chore `a-code-stage-with-no-task-list-delivers-by-its-commit`, which this unit's branch holds, built it; this change puts it in the spec and pins slc-1's case.
- **The conductor reads the report before it asks.** The conductor's brief says that on a stuck report it reads the agent's words and the commits first, and acts on what they settle: an agent that says it needs something is answered as a stop-short is; work committed with the next stage following goes on to that stage. It asks the user, and runs the stage again or waits again on the user's word, only when the report settles nothing. A fix round reported stuck is read the same way.
- README, the crew skill and `crew`'s usage header say what a stuck answer carries (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a stage quiet too long is reported stuck with the agent's last words and the branch's commits since the stage began; a code stage whose head has no task list delivers by its commit; a fix round reported stuck is read before anyone is asked; the conductor reads a stuck report before it asks the user.

## Impact

- `plugin/lib/plan.py` (`stage_wait`, `background`, `look`, a new pure `stuck_said` and the thin read of the branch's commits), `plugin/lib/transcript.py` (a new `last_words`), `plugin/lib/gather.py` (a new `since`, the commits on a branch from a time), `plugin/roles/conductor.md`, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage header, README.
- Tests: `tests/py/test_wait.py`, `tests/py/test_transcript.py`, `tests/py/test_stage_ends.py`, `tests/contract/test_gather.py`, `tests/t-journey-units.sh`, `tests/t-briefs.sh`.
- The run record is unchanged: a stuck answer is still no `stage.end`, and the agent's words never enter the record (`record.3`).
- Nothing the board or the mod draws changes: no view carries a stuck answer (`code.8` not reached).
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/lib/transcript.py
plugin/lib/gather.py
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
README.md
tests/py/test_wait.py
tests/py/test_transcript.py
tests/py/test_stage_ends.py
tests/contract/test_gather.py
tests/t-journey-units.sh
tests/t-briefs.sh
tests/moon.yml
```

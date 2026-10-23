# Proposal

## Why

The user can answer a batch only by tapping its card or sending its reading session. When the card was posted from a host the main level has since left, nobody can see the tap: on 2026-10-22 batches 13, 14 and 15 had been approved on cards posted from mac-studio, the planner's waits on deneb never heard it, and the bolts held by those batches were never offered for landing. The user then said so in the planner's pane, and crew had no way to take those words as the answer (signal 2026-10-22-swancloud-planner-3b6cb27a/01). Record 0031, as amended and accepted on 2026-10-22, makes the user's own words in a main-level pane the third way to answer a batch, as they already accept a record and land a bolt (`briefs.12`, `briefs.13`).

## What Changes

- When the user answers a batch in their own words in the planner's pane or the operator's, that agent runs `crew card answer batch/<n> --excerpt "<the user's words>"`. crew looks for the words in that agent's own session transcript and records the batch answered only when it reads them as the user's (`signals.5`). The agent's own words, and words another agent passed on with `crew tell`, are refused and record nothing.
- The answer counts the same as a tap on the batch's card. The batch's row leaves the rail and the board. The planner's wait on the batch ends. Once every unit's latest change has been in an answered batch, the bolts waiting on it are offered for landing at the next rail read on their team's host.
- The user's words are the batch's note. When the operator ran the command, crew tells the planner the words, and the planner sends each unit's part to its conductor, as it does with any batch note. When the planner ran it, the planner sends them itself.
- crew closes the batch's card as answered, naming the words, when the card is held on the host where the command runs. When the card is held elsewhere, on a host the main level has left, the batch is answered anyway, and the card is closed as answered by the rail's sweep on the host that holds it.
- Whichever answer comes first counts. A batch already answered on its card, in its session or in a pane is refused a second time, and so is one that waits on nothing.
- The run record keeps the answer without the words (`record.3`): the batch, who ran the command, the session, the transcript record the words came from, and how long they were.
- The planner's and the operator's briefs say when to run the command and what to do with the words.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `review-batches`: a batch is also answered by the user's own words in a main-level pane, read from that session's transcript as theirs. Those words are its note, and they close its card and offer its bolts for landing as a tap does.

## Impact

- `plugin/lib/plan.py`: the new `crew card answer` command and its parser; `batch_closed` takes the pane answer as final; `row_gone` gives a pane-answered batch's card the "answered" outcome; `batch_wait` ends on the answer; the module's usage text.
- `plugin/lib/transcript.py`: a check that finds the newest received record in which the user said the words, so that a later echo of the same words in a tool's output does not hide them.
- `plugin/roles/planner.md`, `plugin/roles/operator.md`: *Batches*, and how the operator handles a batch answered in its pane.
- Tests: `tests/py/test_batches.py`, `tests/py/test_rail.py`, `tests/py/test_transcript.py`, a new `tests/py/test_batch_answer.py`, `tests/t-briefs.sh`.
- `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`: the new command, as `docs.2` asks.

## Touches

```
plugin/lib/plan.py
plugin/lib/transcript.py
plugin/roles/planner.md
plugin/roles/operator.md
tests/py/test_batches.py
tests/py/test_rail.py
tests/py/test_transcript.py
tests/py/test_batch_answer.py
tests/t-briefs.sh
README.md
plugin/skills/crew/SKILL.md
plugin/bin/crew
```

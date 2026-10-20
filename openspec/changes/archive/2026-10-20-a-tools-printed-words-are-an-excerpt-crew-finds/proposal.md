# Proposal

## Why

On 2026-10-20 crw-2's conductor tried twice to record a finding whose excerpt was a line a crew command had printed, and `crew signal` refused both times, saying the words were not in its session's transcript (signal 2026-10-20-swancloud-planner-1fab5a67/02). The design agent read why (`docs/architecture/signals.md`, `signals.2`, read 2026-10-20): the command, `crew card wait`, had run as a Claude Code background task. A background task's output goes to a file, and reaches the session's transcript only when the agent reads that file. The conductor had seen the line in its pane's summary, never read the file, and quoted the line with a capital letter crew had not printed. So the refusal was right under `signals.2`, but it told the conductor only that it had reworded the words. Nothing told it the one step that would have let it record the finding itself: read the task's output, then quote it.

## What Changes

- **A refusal says how a tool's words reach the transcript.** When `crew signal` refuses an excerpt, its message still says the words are not in the session's transcript and to quote them as received. It now also says that a background task's output is in the transcript only once the agent has read the output file its task notification names, and to read it and record the signal again.
- **Every brief that records findings says the same.** The shared sentence on recording a finding says a refusal means the words were reworded, or are a background task's output the agent has not read yet.
- **A tool's printed words, a crew command's own output among them, are found as received.** Nothing in the check changes: once a tool's output is in the transcript, read from a background task's file or printed by a command run in the foreground, the excerpt is verified and asserted by a tool. New logic cases pin this on records shaped as Claude Code writes them. Words copied with a changed letter are still refused.
- README's Signals section says what a refusal means, both cases.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `signal-capture`: a refused excerpt's message names the background task's output beside the paraphrase, and a tool's output read into the session is verified as a tool's. (The excerpt check's requirements are still in the unarchived `checked-capture` change, so this delta adds a requirement rather than modifying one.)

## Impact

- `plugin/lib/plan.py`: the signal command's refusal, its words decided by a function of the verdict (`code.7`).
- `plugin/lib/crew.py`: `signal_how`, the sentence every recording brief shares.
- `tests/py/test_signals.py`, `tests/py/test_transcript.py`: the refusal's words, and the check on a background task's output before and after it is read and on a crew command's printed line.
- `tests/t-briefs.sh`: the briefs carry the new clause. `tests/t-journey-signals.sh` keeps passing unchanged, since the refusal still begins with its present words.
- `README.md`: the Signals section's paragraph on refusals (`docs.2`). The usage header and `plugin/skills/crew/SKILL.md` say nothing of refusals, so they do not change.
- Not here: crew reading a background task's output file itself, and naming the nearest words it found (see design, *Decisions*).

## Touches

```
plugin/lib/plan.py
plugin/lib/crew.py
tests/py/test_signals.py
tests/py/test_transcript.py
tests/t-briefs.sh
README.md
```

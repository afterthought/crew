# Proposal

## Why

When an agent records a finding, crew looks for its quoted words in the agent's own session transcript and refuses them when the only place they appear is something the agent wrote itself: that is a paraphrase, not a quote (`signals.2`). Since Claude Code 2.1.303, though, the transcript also holds a copy of every message Claude Code sends the model, the agent's own earlier replies among them, under a record type the check does not skip. So an agent that quotes a sentence it wrote a turn ago gets it recorded as `found` instead of refused, and the paraphrase refusal is weaker than the rule says (signal 2026-10-20-swancloud-planner-94f45ad3/01, found by crw-4 building `a-tools-printed-words-are-an-excerpt-crew-finds`).

## What Changes

- **An agent quoting itself is refused again.** The check passes over Claude Code's copies of what it sent the model, as it already passes over the records the agent wrote. Words that are only in the agent's replies, or only in those copies, are refused as a paraphrase.
- **What the user typed and what a tool printed are verified as before.** Their originals are still searched, so their grade, who asserted them and the record the capture names do not change; the copy beside each original is simply not read.
- **crew names the record type it relies on.** The transcript reader's list of known facts about Claude Code's format gains the copy record, `api-request-blob`, with the transcript it was read from, and says what happens when that stops holding: a quote of the agent's own words grades `found` again, and nothing is stopped.
- Logic cases pin all three on records shaped as Claude Code 2.1.303 writes them.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `signal-capture`: an agent's own words are never found, whether in its own replies or in Claude Code's copies of the messages it sent the model. Added as a requirement of its own, since the excerpt check's grades are not yet a requirement of this capability's main spec.

## Impact

- `plugin/lib/transcript.py`: `check` skips records of type `api-request-blob` as it skips those of type `assistant`; its docstring and the module's header name the new format fact and the grade it lowers when it stops holding.
- `tests/py/test_transcript.py`: cases on a transcript holding the agent's reply, its copy, and the user's message with its copy.
- Read and unchanged: `tests/py/test_signals.py`, whose refusal message and capture naming hold as they are; `received`, which reads only records of type `user` and `queue-operation`, so the copies never counted there; README's Signals section, which already says a signal is refused when the words are only in what the agent wrote itself.
- Not here: `docs/architecture/signals.md`, whose `signals.2` details already record this reading and are the design agent's (`docs.7`).

## Touches

```
plugin/lib/transcript.py
tests/py/test_transcript.py
```

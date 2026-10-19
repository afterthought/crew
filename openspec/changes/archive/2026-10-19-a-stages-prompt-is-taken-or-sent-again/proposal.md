# A stage's prompt is taken or sent again

## Why

On 2026-10-10, at 03:00Z, crw-2-unit-1 sat with its `/opsx:apply` prompt typed into its pane and never submitted. crew had said the code stage started; the conductor waited on it; nothing happened until the operator agent, on the user's word, pressed Enter ("crw-2-unit-1's /opsx:apply prompt had been typed but never submitted; on the user's word I pressed Enter and it is now working", signal 2026-10-10-crw-2-conductor-fc928fa0/01).

crew types a stage's prompt with `herdr agent prompt` and reads nothing back. herdr says plainly that a successful submission "does not prove the agent started a turn". So a prompt that lands before Claude is ready for it, or whose Enter is lost, looks to crew exactly like a stage that began, and only someone reading the pane finds out. Rule `teams.15` already says what must hold instead; this change builds it.

## What Changes

- When crew starts a stage (construct, code, verify, merge, a fix, a fix's merge) it waits until the fresh agent is ready for input, sends the stage's prompt, and then reads the agent's own transcript to see that Claude received it. It does not say the stage started until it has.
- When the transcript does not show the prompt within a short time, crew clears whatever was left typed in the input and sends the prompt once more, and reads again.
- When the second sending is not taken either, crew clears the input, records the stage as never started, and the command fails saying so and how to run it again. Nothing is left typed in the pane, and no stage end is owed for it.
- The same holds for crew's greetings (a conductor's, and each agent's crew starts outside a team): sent once the agent is ready, read back, sent once more, and reported as not delivered when the second is not taken.
- An agent that never becomes ready for input (it stays on a question in its pane, or herdr never names its session) gets nothing typed, and its stage is reported as never started.
- When crew cannot read whether the prompt was taken (the agent went straight to work but its transcript shows no prompt, or the transcript can't be read), it sends nothing more, records no start, and says what it could not read.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: new requirements that a stage begins only when its agent takes its prompt, that a prompt not taken is sent once more, and that a stage whose prompt is not taken never started.
- `main-level`: new requirements that a greeting is taken or sent again, and that a greeting not taken is reported with nothing left typed.

## Impact

- `plugin/bin/crew`: `run_stage` hands the prompt to crew's builder instead of typing it, and records the start only once it is taken; `prove` asks for the same reading.
- `plugin/lib/crew.py`: one sending that waits for the agent to be ready, reads the transcript, clears and sends again; greetings and the proof's tell use it.
- `plugin/lib/transcript.py`: reads whether a session received a given prompt after a given point, runnable on the agent's host.
- The stub herdr writes what it is sent into the stub session's transcript, and can be told to leave a prompt typed and untaken.
- Every agent picks this up at the next command crew runs; nothing to restart.

## Touches

```
plugin/bin/crew
plugin/lib/crew.py
plugin/lib/transcript.py
tests/stubs/herdr
tests/t-prompt-taken.sh
tests/t-transcript.sh
tests/t-unit-run.sh
tests/t-greet.sh
tests/t-fix.sh
tests/t-stage-ends.sh
tests/t-amend.sh
tests/t-amend-intent.sh
tests/t-reads-once.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
docs/architecture/teams.md
docs/architecture/_open.md
openspec/specs/bolt-teams/spec.md
openspec/specs/main-level/spec.md
```

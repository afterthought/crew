# Proposal

## Why

On deneb, `crew tell swancloud-planner` was refused while the planner sat idle in its own session, swancloud-2: "could not tell swancloud-planner on deneb: herdr names no session for it, so crew can't tell whether it is waiting on a question; nothing was sent" (signal 2026-10-22-swancloud-design-09c0a0eb/01). Herdr finds the planner's pane by name, but names no Claude session for it, as happens after herdr's own session restore resumes a pane and before `crew main up` starts the role again through crew. crew needs that session only to read the mark its own hook leaves when an agent opens a question, and without it refuses every tell. So no agent can reach the planner, and since a partition's main-level roles now sit in sessions of their own (swancloud `herdr.3`, amended 2026-10-20), an agent in the partition's first session can reach no main-level agent in its second. Every message between agents goes through `crew tell` (`roles.4`), so there is no other way to reach it.

## What Changes

- crew's session-start hook records, with each crew agent's session, the herdr session and pane the session started in, at a start through crew and at a resume by herdr alike.
- When herdr names no Claude session for an agent's pane, crew reads the agent's session from its own record on the agent's host instead: the newest session of that agent that started in that pane. It reads the question mark of that session, so a tell is still refused while the agent waits on a question crew's hook saw.
- When neither herdr nor crew's record names a session, herdr's own reading of the pane guards the tell, as it already does for an agent started before crew's hook existed: the tell is typed unless herdr reports the agent blocked, and herdr's own refusal at the moment of typing still stops it.
- So a tell is refused only when crew cannot find the agent's pane, when the agent waits on a question, or when crew cannot read what it needs from a host or a mark. A missing herdr session alone no longer refuses it. The greetings and notices that go through the same reading gain the same session.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: the requirement "Any agent crew starts is reached by name" says how a tell is guarded when herdr names no session for the agent's pane.

## Impact

- `plugin/hooks/session-start`: the record gains the pane's herdr session and pane id.
- `plugin/lib/questions.py`: a second way to ask, by agent, herdr session and pane, that finds the session in crew's records and answers its mark with the session it found.
- `plugin/lib/crew.py`: `agent_reading` asks for the session that way when herdr names none; `waits_on_question` no longer refuses for want of a session.
- `tests/stubs/herdr`: a pane herdr names no session for, as herdr answers for one after its restore.
- Tests in the logic tier (`tests/py/test_review.py`, a new `tests/py/test_questions.py`) and end to end (`tests/t-session-hook.sh`, `tests/t-journey-main.sh`).
- `README.md`, its main-level paragraph.

## Touches

```
plugin/hooks/session-start
plugin/lib/questions.py
plugin/lib/crew.py
tests/stubs/herdr
tests/py/test_review.py
tests/py/test_questions.py
tests/t-session-hook.sh
tests/t-journey-main.sh
tests/moon.yml
README.md
```

# A tell never lands in a question

## Why

On 2026-10-07 the operator agent sent wldn-ops a request with `crew tell` while wldn-ops had a question open in its pane. crew said "told", but the text went into the question's form and wldn-ops never received it; the user noticed and the request was sent again by hand ("i don't think it got it since it had a userquestion tool open", signal 2026-10-07-swancloud-operator-mac-studio-09fca02b/01). A tell that says it was delivered when it was not is worse than one that fails: nobody knows to send it again.

herdr already refuses to type into an agent it sees waiting at a question (`agent_blocked`), and crew relied on that. It did not see this one: the box ran herdr 0.9.3, wldn-ops' question was open from 18:56 to 19:29, and herdr took the 19:26 prompt. herdr reads Claude Code's state from the screen alone, so crew needs a reading of its own that does not depend on how a dialog looks.

## What Changes

- `crew tell`, and every greeting and notice crew sends through the same path, checks before typing whether the agent is waiting on a question in its pane. When it is, nothing is typed, the command fails, and it says the agent is waiting on a question and to tell it again once the question is answered.
- crew knows a question is open from two readings: herdr reporting the agent `blocked`, and a mark crew's own plugin leaves when a crew agent opens Claude Code's question dialog (`AskUserQuestion`) or plan approval (`ExitPlanMode`). The mark counts until the agent's transcript holds that call's answer, so a question answered, dismissed or abandoned stops counting without crew having to see it close.
- herdr's own `agent_blocked` refusal, when it still happens, is reported in the same words instead of as a bare herdr error.
- When crew cannot tell whether a question is open (herdr names no session for the agent, or a mark exists but the transcript can't be read), it refuses and says what it could not read, rather than typing.
- Greeting a conductor waits on a question crew's mark shows just as it waits on one herdr shows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: the requirement "Any agent crew starts is reached by name", which already says a tell to an agent waiting on a question fails with nothing typed, becomes true and gains the case where crew cannot tell.

## Impact

- `plugin/lib/crew.py`: `tell` reads the agent before typing; `greet` waits on the same reading.
- A new stdlib-only reader in `plugin/lib/`, piped to the agent's host the way `gather.py` is, and a new PreToolUse hook in `plugin/hooks/`, registered in `plugin/hooks/hooks.json`; `plugin/hooks/session-start` clears a session's mark at each start.
- Every crew agent picks up the hook at its next start; until then only herdr's own reading guards it.
- Stub herdr refuses a prompt to a blocked agent with `agent_blocked`, as herdr does.

## Touches

- `plugin/lib/crew.py` (`tell`, `agent_get`, `greet`)
- `plugin/lib/questions.py` (new)
- `plugin/hooks/questions` (new), `plugin/hooks/hooks.json`, `plugin/hooks/session-start`
- `plugin/bin/crew` (usage header only)
- `tests/stubs/herdr`, `tests/t-notify.sh`, `tests/t-greet.sh`, `tests/t-session-hook.sh`
- `README.md`, `plugin/skills/crew/SKILL.md`
- `docs/architecture/teams.md` (`teams.11` details), `docs/architecture/_open.md`
- `openspec/specs/main-level/spec.md` (by delta)

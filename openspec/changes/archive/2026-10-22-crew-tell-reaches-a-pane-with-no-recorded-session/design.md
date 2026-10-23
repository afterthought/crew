# Design

## Context

See proposal.md for why. A tell reads its agent before it types (`teams.11`; the archived `a-tell-never-lands-in-a-question` design): `crew.py` `waits_on_question` calls `agent_reading`, which asks herdr for the agent by name (`agent get`), refuses nothing when herdr reports it `blocked` (that is a wait), and otherwise takes the Claude session from the item's `agent_session.value` and pipes `questions.py <session id>` to the agent's host to read the mark crew's PreToolUse hook (`plugin/hooks/questions`) left when the agent opened a question or a plan. When herdr names no session, `agent_reading` returns none and `waits_on_question` turns that into "herdr names no session for it", which `tell_refusal` refuses.

Herdr learns a Claude Code session only from its own integration hook, which "reports Claude Code session identity to the local Herdr socket on session start" (herdr 0.9.5 docs, Integrations, "Claude Code"); crew does not control that hook (swancloud `lib/agent-config.nix` installs it). On deneb on 2026-10-22 herdr named none for the planner's pane in swancloud-2, idle and found by its name (the signal's capture). Why herdr's hook gave it none there is not read here; crew must not depend on it.

crew already keeps its own record of every crew agent's session: `plugin/hooks/session-start` writes `~/.local/state/crew/sessions/<session id>` with `CREW_AGENT` at every start crew makes (`crew-role` puts `CREW_AGENT` in the environment), and rewrites it at herdr's resume of a recorded session (source `startup` or `resume`), which keeps the session id. That record is how herdr's resumed pane gets its name back, so a pane herdr finds by an agent's name almost always has one. It does not say which pane the session runs in. Herdr injects `HERDR_SESSION` and `HERDR_PANE_ID` into every pane it manages (herdr's skill, "Herdr injects the caller's context"; read in a pane on deneb in this construct: `HERDR_SESSION=swancloud-1`, `HERDR_PANE_ID=wH:p2`), and the hook already reads `HERDR_PANE_ID` to rename the pane.

Rules relied on: `teams.11`, `roles.4`, `read.1`, `read.2`, `read.3`, `code.1`, `code.3`, `code.7`, `state.4`, `tests.4`, `tests.11`, `docs.2`, `docs.4`, `docs.7`. Pages whose areas this touches: `teams.md` (`plugin/lib/crew.py`), `tests.md` (`tests/`), `docs.md` (`README.md`, `openspec/`). swancloud `herdr.3` places the main-level roles in sessions of their own; `herdr.12` is herdr's resume after a restore.

## Goals / Non-Goals

**Goals:**
- A tell reaches an agent whose pane herdr names no session for, still refused while that agent waits on a question crew's hook saw.
- A tell is refused only when crew cannot find the pane, the agent waits on a question, or crew cannot read a host or a mark.

**Non-Goals:**
- Why herdr's integration named no session for the planner's pane: that is swancloud's hook and herdr's, not crew's.
- `ready_for` and `read_back`, which a sending read back (`teams.15`: greetings, the notice of a restart) uses: they gain the session from crew's record through `agent_reading`, and with neither session they still report the agent not greeted, since they need a transcript to read back.
- `hold.py`'s readings and `plan.py` `background`, which read herdr's session for an agent's own work: unchanged.
- The rule page's details (`teams.11`, which names no-session refusal nowhere), left to the design agent (`docs.7`).

## Decisions

### 1. crew's record names the pane its session started in

`session-start` writes two more lines in every record it writes: `CREW_HERDR_SESSION` from `HERDR_SESSION` and `CREW_PANE` from `HERDR_PANE_ID`, each empty when the variable is absent (a session outside herdr). It writes them at a start through crew, and at herdr's resume of a recorded session, where it already rewrites the record, replacing the old values. A main-level agent herdr replays off its host keeps its record as it was, as now. Nothing that reads records today is changed by two more keys: `last_conversation`, `brief_due` and the update check read the keys they name.

Alternatives considered:
- *The newest record of the agent's name, whatever its pane.* A herdr restore of a saved layout that still holds an old pane of the same agent, in another session on the host, rewrites that record at the same moment, and the tell would read another session's mark.
- *Read the session from the pane's process* (`pane process-info`, `claude --resume <id>`). A fresh start by crew carries no session id in its arguments, and the shim's argv is not crew's to rely on (`read.2`).
- *Report the session to herdr from crew's hook.* herdr's agent session is its integration's to report; a second reporter would race it.

### 2. Asking for the session by pane

`questions.py` gains a second form: `questions.py --pane <herdr session> <pane id> <agent>`. It lists `~/.local/state/crew/sessions/`, takes the records whose `CREW_AGENT`, `CREW_HERDR_SESSION` and `CREW_PANE` are those given, picks the newest by its file's time, and reads that session's mark as the first form does, answering with it `"session": <id>`; with no such record it answers `{"session": null, "question": null}`. A records folder it cannot list is `{"unread": ...}` naming it (`read.1`). Choosing the record is a function of plain facts, the records as (time, session id, fields) and the three names, so it is proved in the logic tier (`code.7`, `tests.11`). It stays standard library only and writes nothing (`code.1`, `state.4`): crew pipes its own copy to the host, so a host whose crew is older still answers, and a host whose hook is older has records without a pane, which match nothing.

`agent_reading` asks this form when herdr's item names no session, with the session `place_of_agent` gives, the item's `pane_id` and the agent's name, through `piped` as now (`code.3`, `read.3`); a host that does not answer is what crew could not read, as now. The session it gets back is the agent's session for every caller of `agent_reading`.

### 3. With neither session, herdr's reading guards the tell

When herdr names no session and crew's record names none for that pane, `agent_reading` answers no session and nothing unread, and `waits_on_question` no longer turns that into a refusal. The tell is typed unless herdr reports the agent blocked, and herdr's own `agent_blocked` at the moment of typing still refuses it in crew's words (`typed_refusal`).

This departs from `read.1`, as the archived design's decision 5 did for an agent started before the hook: crew cannot read whether a question it would have marked is open, and goes on rather than refusing. Why: every message between agents goes through `crew tell` (`roles.4`), so a refusal leaves the agent unreachable by any agent until a hand restarts it; the case is narrow once records name their pane (a pane named by hand, a record written by a hook older than this change until the agent's next start, a `/clear` inside a herdr-resumed session, whose new session has no record), and herdr's reading of the screen still guards it.

### 4. The docs

README's main-level paragraph gains one sentence: when herdr names no session for an agent's pane, crew reads the session it recorded of that agent in that pane, and with neither, herdr's reading alone guards the tell. The usage header of `plugin/bin/crew` and the crew skill's **Blocked** line say nothing this changes, so they stay (`docs.2`). The spec's requirement is restated by this change's delta (`docs.4`).

## Risks / Trade-offs

- [A tell typed into a question herdr does not see, for an agent with neither session] → Narrowed by decision 1 to panes with no current record; herdr's screen reading and its `agent_blocked` still guard; it closes at the agent's next start through crew or herdr.
- [A pane id reused for another agent's pane in the same session] → herdr does not reuse closed pane ids ("Closed tab and pane IDs are not reused", herdr's skill), and the record must also name the agent.
- [A pane moved to another workspace gets a new id, so its record matches nothing] → the tell falls to decision 3 until the agent's next start.

## Migration Plan

None: records written before this change lack the two keys and match nothing, so their agents' tells fall to herdr's reading until each agent's next start, which writes them.

## After deploy

None: the case is reproduced on the stubs, a pane herdr names no session for, and nothing about it needs a live host to be true.

## Task notes

**1.1** `plugin/hooks/session-start`: in the record written when `CREW_AGENT` is set, add `CREW_HERDR_SESSION={HERDR_SESSION or ''}` and `CREW_PANE={HERDR_PANE_ID or ''}` after `CREW_BRANCH`; in the rewrite at herdr's resume (`source in LOADS`), drop the old two from `saved` as it drops `CREW_BRANCH` and write the current ones. Say so in the docstring's record sentence. `tests/t-session-hook.sh` gains: a crew start in a pane (`HERDR_SESSION=s HERDR_PANE_ID=w1:p2`) records both; a resume of that recorded session in another pane records the new pane and session, not the old; a start outside herdr records both empty. Verify `tests/suite t-session-hook` ends with "0 failed".

**1.2** `plugin/lib/questions.py`: a function of plain facts, `session_in(records, agent, session, pane)`, records as (mtime, session id, fields dict), answering the session id of the newest matching record or None; a `--pane <herdr session> <pane id> <agent>` form that reads the records (skipping one it cannot read, refusing a folder it cannot list), calls `session_in`, and answers `{"session": null, "question": null}` or the first form's answer for that session with `"session"` added. Check each argument against its pattern before any path is built: a herdr session and an agent `^[a-z0-9][a-z0-9-]*$` (`code.4`), a pane `^[A-Za-z0-9:]+$`. Docstring: the second form, the record keys it reads, which hook writes them. New `tests/py/test_questions.py`: the newest of two matching records wins; a record of the same agent in another pane, or another session, or with no pane keys, is not taken; another agent's record in the pane is not taken; none matching is None. Verify `tests/suite logic` ends with "0 failed".

**2.1** `plugin/lib/crew.py`: `agent_reading`, when herdr names no session, pipes `questions.py --pane <session> <pane_id> <name>` (`session` from `place_of_agent`, `pane_id` from herdr's item, skipped as no session when it is not a string), takes `sid` from the answer's `session`, and returns as it does now for a session's mark; no session from either is (status, False, None, None). `here_reading` passes the same arguments to the same entry the command line uses. `waits_on_question` drops its "herdr names no session for it" line; its docstring and `agent_reading`'s say the record and the departure (Decision 3). `ready_for`'s "as herdr named no session for it" becomes "as crew found no session for it". `tests/py/test_review.py` `TestTell`: the no-session row goes; an idle agent with no session and nothing unread is told (None). Verify `tests/suite logic` ends with "0 failed".

**2.2** `tests/stubs/herdr`: `herdr --session S stub nosession <agent> on|off`, so `agent get` and `agent list` leave out `agent_session` for that agent's pane while on, as herdr's item does when its integration reported none (the stub's docstring says so). `tests/t-journey-main.sh`, after `crew main status`: with the planner's session dropped, `crew tell wldn-planner` reaches it marked with its sender (the log holds the `agent prompt`); with its session dropped and the question hook's mark open for the session crew recorded in its pane (made as `t-session-hook` makes one, under the planner's host's home), the tell fails saying it is waiting on a question and the log holds no prompt for it; with the record's pane keys removed (`rewrite` from `tests/lib.sh`), the tell goes again. Run `tests/moon-tasks` and commit `tests/moon.yml` if it changes. Verify `tests/suite t-journey-main` ends with "0 failed".

**3.1** `README.md`, the main-level paragraph's sentence on a tell to an agent waiting on a question: add the sentence of Decision 4. Verify `tests/suite t-docs t-briefs` ends with "0 failed".

**3.2** Verify `tests/suite --affected` ends with "0 failed".

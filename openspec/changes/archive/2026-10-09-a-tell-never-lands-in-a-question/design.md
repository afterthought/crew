# Design

## Context

Every message crew sends an agent goes through `crew.py` `tell` (`roles.4`): `crew tell`, the greetings, and the notices `plan.py` sends conductors, dispatchers and the planner. `tell` runs `herdr --session <s> agent prompt <name> "<mark> <text>"` on the agent's host and reports any failure as "could not tell <name> on <host>: <herdr's stderr>". It reads nothing about the agent first. `greet` does read it: it polls `agent_status` and, while herdr says `blocked`, waits up to five minutes for the question to be answered.

herdr 0.9.3 refuses `agent prompt` to an agent it sees `blocked` ("an approval or question UI"), returning `{"error":{"code":"agent_blocked",…}}` on stderr with exit 1 and typing nothing (herdr CLI reference and socket API, v0.9.3; changelog 0.8.2, #2788). For Claude Code, herdr learns that state from the screen alone: its Claude Code integration reports only the session's identity (herdr Integrations, "Claude Code"). On 2026-10-07 that was not enough. wldn-ops on chuck-herdr-alpha, running herdr 0.9.3 (system generation 25, built 03:09 that day), called `AskUserQuestion` with two questions at 18:56:06; the answer came back at 19:29:37 (its transcript, session 4ec81fa0, Claude Code 2.1.286). The operator's `crew tell wldn-ops` at 19:26:40 printed "told": herdr accepted the prompt, so it did not see that dialog as `blocked`, and the 505 characters went into the form.

The agent's transcript can't show an open question either: Claude Code writes a tool call's record only once the tool returns (`transcript.py`'s docstring; checked again in this change's construct session, where a running Bash call's own command was absent from the transcript until it returned). Claude Code's hooks can: `PreToolUse` runs before a tool is processed, matches `AskUserQuestion` and `ExitPlanMode` by name, and receives `session_id`, `transcript_path` and `tool_use_id` (Claude Code hooks reference, "PreToolUse", "Common input fields"). The answer, when it comes, is a record holding a `tool_result` whose `tool_use_id` is the call's (wldn-ops' transcript above).

crew's plugin already carries two hooks: `session-start`, which records each crew agent's session in `~/.local/state/crew/sessions/<session id>`, and `cards`, a PostToolUse hook. Reading another host with a crew that may be older is done by piping a stdlib-only script to `python3 -` there (`gather.py`, `plan.py` `survey`).

Pages whose areas this touches: `teams.md` (`plugin/lib/crew.py`, `plugin/bin/crew`), `tests.md` (`tests/`), `docs.md` (`README.md`, `docs/`, `openspec/`), `briefs.md` (`plugin/skills/crew/SKILL.md`). Rules relied on: `teams.11`, `teams.7`, `roles.4`, `read.1`, `read.2`, `read.3`, `code.1`, `code.3`, `state.4`, `tests.4`, `docs.2`, `docs.4`.

## Goals / Non-Goals

**Goals:**
- No tell, greeting or notice is typed while the agent is waiting on a question, whether or not herdr sees the question.
- A refused tell says why in plain words and fails, so the sender knows to send it again.

**Non-Goals:**
- Waiting for the question to be answered and then delivering. A tell is refused, not queued; only a greeting waits, as it already does.
- Stage prompts typed by `run_stage` in `plugin/bin/crew` into a fresh agent, and the `/exit` and `/clear` it types. These are not tells, and go to an agent crew has just started.
- Permission prompts herdr does not see. crew's agents run with permissions bypassed; herdr's own reading still covers the ones it recognizes.
- Telling the user, or the sender's brief, what to do after a refusal beyond the refusal's own words.

## Decisions

### 1. Two readings: herdr's, and a mark crew's own hook leaves

An agent is waiting on a question when herdr reports it `blocked`, or when crew's mark says it opened `AskUserQuestion` or `ExitPlanMode` and the call has no answer yet. herdr's reading covers approval prompts and anything else it recognizes; the mark covers Claude Code's question and plan dialogs however they draw. Either one is enough to refuse.

Alternatives considered:
- *herdr's `blocked` alone.* That is what failed on 2026-10-07: herdr's own refusal already does exactly this, and the dialog got past it.
- *Read the pane's screen in crew.* The same kind of reading herdr does and missed, written a second time against a screen whose layout Claude Code does not document (`read.2`).
- *The transcript alone.* An open call is not in it until it returns.
- *Report the state to herdr from the hook* (`pane.report_agent`). herdr would then take Claude Code's whole state from crew instead of the screen, and crew's waits rest on herdr's `working` and `idle`. Too wide for this change.

### 2. The mark

A PreToolUse hook, `plugin/hooks/questions`, registered in `hooks.json` with the matcher `AskUserQuestion|ExitPlanMode`, writes `~/.local/state/crew/questions/<session id>` holding the call's `tool_use_id` and the `transcript_path` from its input, as one JSON object, written to a new file and moved over the old. It writes only for a session crew started, known as the `cards` hook knows it (`CREW_AGENT`, or the record `session-start` keeps), and nothing for a subagent's call (an input with `agent_id`), whose answer would land in another transcript. It reads nothing else, prints nothing, decides nothing about the call, and always exits 0. A later question in the same session replaces the mark.

`session-start` removes the session's mark at every start, so a session resumed after its pane died with a question open does not carry a mark whose answer will never be written.

### 3. When the mark counts

The mark counts while the transcript it names holds no record with a `tool_result` whose `tool_use_id` is the mark's. Claude Code writes that record when the dialog closes, answered or dismissed, so crew never has to see the dialog close. The transcript is written asynchronously and may lag a moment behind an answer; a tell in that moment is refused, the safe way round.

The reading is a stdlib-only module, `plugin/lib/questions.py`, which `crew.py` pipes to `python3 - <session id>` on the agent's host through `on_machine`, as `plan.py` pipes `gather.py` (`code.1`, `code.3`), so a host whose crew is older still answers. It answers one JSON object on stdout: no mark, a mark that is answered, a mark that is open, or a mark whose transcript it could not read, with what it could not read. It writes nothing (`state.4`). Its docstring names the two facts of Claude Code it leans on, the hook's input fields and the `tool_result`'s `tool_use_id`, and where they were read (`read.2`).

### 4. What `tell` does

1. Read the agent with `herdr agent get` on its host. Not up: report it as now ("could not tell <name> on <host>: it is not up") and fail.
2. herdr says `blocked`: refuse.
3. Take the session from herdr's `agent_session.value` and read the mark there. Open: refuse. herdr names no session, the host does not answer (`read.3`), or the mark's transcript can't be read: refuse naming what could not be read (`read.1`).
4. Type the prompt. If herdr still answers `agent_blocked` (a question opened since step 2), refuse in the same words.

The refusal, on standard error: `<name> is waiting on a question in its pane: nothing was sent; tell it again once the question is answered`. The one for what crew could not read: `could not tell <name> on <host>: <what could not be read>, so crew can't tell whether it is waiting on a question; nothing was sent`. `tell` returns False and `crew tell` exits 1, as for any failed tell now; the callers in `plan.py` already report a failed notice and go on. A refused tell writes no run-record entry, as a failed one writes none now.

`agent_status` and `tell` share the one `agent get`; `greet`'s loop asks the same question `tell` does (herdr's `blocked`, or an open mark) and waits on either the same way, printing its existing line once (`teams.7`: still exactly one greeting).

### 5. Agents started before the hook

An agent's hooks are loaded when its session starts. Until each standing agent's next start, and on a host whose crew has not pulled, there is no mark to find, and crew cannot tell a question the hook never saw from no question at all. In that window `tell` relies on herdr's reading alone, as it does today. This departs from `read.1`, which would refuse: refusing would stop every tell, greeting and notice to every running agent at landing until each restarts, worse than the failure being fixed, and the window closes with each agent's next start. The *Proof on real work* restarts the standing agents.

### 6. The rules and the docs

`teams.11` stays as written. Its details lose "crew.py `greet` already waits on `blocked`" as the source and "`tell` types regardless until … lands", and name the two readings and the hook; `_open.md` drops the `teams.11` item. The `main-level` spec's requirement was written ahead of this build by the design commit 9f8c4b5 (against `docs.4`); this change's delta restates it with the case crew cannot read and the greeting, so the spec and the build agree when it is archived. README's main-level paragraph, the crew skill and the usage header of `plugin/bin/crew` say a tell is refused while its agent waits on a question (`docs.2`).

## Risks / Trade-offs

- [A question opens between crew's reading and its typing] → herdr's own check runs at the moment of typing and covers the dialogs it recognizes; the window is one host round trip. Accepted.
- [Claude Code changes its hook input or how a tool's result is recorded] → the mark is never written, or never reads as answered. The first leaves crew where it is today; the second refuses tells to that agent until its next start, loudly. `questions.py` names the facts it leans on, so the change is found in one place.
- [A mark whose answer is never written, such as a session killed mid-question and resumed] → `session-start` clears it at the resume.
- [Each tell costs one more call on the agent's host, two over ssh for a remote agent] → acceptable for a message sent by hand or at a stage's end.
- [Agents started before the hook] → decision 5.

## Migration Plan

Nothing to migrate: the mark directory is made on first write, and a host with no marks reads as no question open. Rolling back removes the hook entry and the reading; marks left behind are read by nothing.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled, with the standing agents restarted:
- On mac-studio, have a crew agent ask the user a question with two questions in it (as wldn-ops did) and leave it open. `crew tell <agent> "<text>"` fails saying the agent is waiting on a question, and the text is not in the dialog. Answer it; the same tell then arrives as a prompt.
- The same from mac-studio to an agent on chuck-herdr-alpha, through ssh.
- While the dialog is open, read `herdr agent get <agent>`: if herdr reports `blocked` for it, note that herdr now sees this dialog; either way the tell is refused.

## Task notes

### 1.1

`tests/stubs/herdr`'s `agent prompt` to an agent whose stub status is `blocked` exits 1 with `{"error":{"code":"agent_blocked","message":…}}` on stderr and appends nothing to its prompts, as herdr 0.9.3 does (CLI reference, `agent prompt`). The stub's `die` writes a bare string error today; this one is coded, since `tell` reads the code. `/exit` to a blocked agent is unchanged. Check that existing tests that set `blocked` and prompt still pass (`t-greet` sets `blocked` and waits; it prompts only once `idle`).

### 1.2

`plugin/hooks/questions`, shaped like `cards`: a docstring saying what it records and why, input read from stdin, nothing printed, exit 0 always. Who is a crew session: as `cards` decides it, `CREW_AGENT` in the environment or `~/.local/state/crew/sessions/<session id>` present. Write the mark with a temporary file in the same directory and a rename. `hooks.json` gets a `PreToolUse` entry with matcher `AskUserQuestion|ExitPlanMode`, timeout 10, and its description gains a clause for it. `session-start` removes `~/.local/state/crew/questions/<session id>` at every start of a crew session, before anything else it does, ignoring a missing file. `tests/t-session-hook.sh` gains the cases: hooks.json runs it; a crew agent's `AskUserQuestion` writes the mark with the id and path; an `ExitPlanMode` does too; a non-crew session, a subagent's call (`agent_id` present) and unreadable input write nothing and exit 0; a session's start removes its mark. Verify `tests/suite t-session-hook` ends with "0 failed".

### 1.3

`plugin/lib/questions.py`: `python3 questions.py <session id>`, or piped as `python3 - <session id> < questions.py`. Session ids are checked with the same pattern `session-start` uses before any path is built. Answers one JSON object: `{"question": null}` with no mark; `{"question": "open", "id": …}`; `{"question": "answered", "id": …}`; `{"unread": "<what>"}` when the mark is unreadable, names no transcript, or the transcript can't be read. Reads the transcript line by line as JSON, skipping lines that don't parse, and looks for an object with `type: tool_result` and the mark's `tool_use_id` anywhere in a record (the same "walk every value" stance as `transcript.py`). Imports only the standard library (`code.1`); `crew.py` reads it once, as `plan.py` reads `GATHER`. Proved through 2.1's cases.

### 2.1

In `crew.py`: one function that answers whether an agent is waiting on a question, from one `agent get` and, for a session, one run of `questions.py` on the agent's host, returning the agent's status, whether it waits on a question, and what could not be read; `tell` and `greet` both use it. `tell` follows Decisions 4 in that order, with the messages there. `crew tell`'s exit stays `0 if tell(...) else 1`.

`tests/t-notify.sh` gains, against an agent on chuck-herdr-alpha (the stub's session id for a pane is `sid-<pane>`; make the mark by running the hook as that host with a transcript under that host's home):
- herdr reports `blocked`: `crew tell` fails with the refusal, and the log holds no `agent prompt` for it.
- herdr reports `idle` and the mark is open, the 2026-10-07 case: the same.
- The transcript gains the call's `tool_result`: the same tell is delivered, marked as before.
- The mark names a transcript that is missing: fails naming it, nothing typed.
- A tell from crew itself (a notice) to an agent waiting on a question is refused the same way and the notice's command goes on.
The existing tell cases keep passing. Verify `tests/suite t-notify` ends with "0 failed".

### 2.2

`greet` waits on an open mark as it waits on `blocked`, with the same line and the same five minutes. `tests/t-greet.sh` gains: a conductor herdr reports `idle` with an open mark is not greeted until the transcript holds the answer, then greeted once. Verify `tests/suite t-greet` ends with "0 failed".

### 3.1

Usage header line for `crew tell` in `plugin/bin/crew`: add that it is refused while the agent waits on a question. README's main-level paragraph (the one ending "`crew tell` prompts any of these agents by name, wherever it runs, marked with who sent it."): one sentence that a tell to an agent waiting on a question in its pane, seen by herdr or by crew's own hook, fails with nothing typed and says to send it again once the question is answered; mention the hook beside the PreToolUse hook README already describes for cards. The crew skill's **Blocked** line: a tell to a blocked agent is refused, so answer or report the question first. Verify `tests/suite t-docs t-briefs` ends with "0 failed".

### 3.2

`docs/architecture/teams.md`, `teams.11`'s details: Source becomes the `main-level` spec, `crew.py` `tell` and `plugin/hooks/questions`; drop "`crew.py` `greet` already waits on `blocked`" and the "until … lands" sentence; add that herdr's screen reading missed the 2026-10-07 dialog, so a mark from crew's own hook is the second reading, and that an agent started before the hook relies on herdr alone until its next start (a departure from `read.1`, design decision 5). `docs/architecture/_open.md`: remove the `teams.11` line. Verify `tests/suite --affected` ends with "0 failed".

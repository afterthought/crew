# Design

## Context

Why this change exists is in proposal.md. What crew does today:

- `run_stage` in `plugin/bin/crew` ends the slot's agent, runs `start` (which waits up to 30 seconds for the folder-trust question or for herdr to call the agent idle, and goes on either way), then types the prompt with `h agent prompt "<pane>" "<prompt>"` and records `stage.start`, appending the owed end to the stages file. It reads nothing back. Unit stages, a fix's code and a fix's merge all go through it.
- `prove` sends ops its request with `py tell "$TEAM-ops" "…"` and records the proof's `stage.start` when the tell returns 0.
- `greet_agent` in `plugin/lib/crew.py` waits until the agent is idle or done with no question open (`waits_on_question`: herdr's `blocked`, or crew's own question mark), then calls `tell`, which types the `[crew]`-marked text with `herdr agent prompt` and records `greet`. It too reads nothing back.

What the vendors say, read for this change:

- **herdr 0.9.3**, `herdr agent prompt --help` and `herdr --skill`: `agent prompt` "sends text followed by encoded Enter as one ordered submission. It reports successful submission only after both have been written; that alone does not prove the agent started a turn." Its `--wait` gate returns `agent_prompt_stalled` when no `working` or `blocked` state is seen within five seconds, and herdr warns: "A timeout or stalled response does not prove the prompt was never delivered; do not blindly submit it again." `idle` and `done` both mean the agent is ready for input. `agent send-keys <agent> <key>` sends logical keys such as `ctrl+c`. `agent get` gives the Claude session as `agent_session.value`, from herdr's Claude integration.
- **Claude Code**, interactive-mode reference: `Ctrl+C`, when nothing is running, "the first press clears the prompt input and a second press exits Claude Code". Double `Esc` clears a draft too, but on an empty input opens the rewind menu, so it is not used.
- **Claude Code's transcript** (2.1.292, this construct's own session 0bd4a771 and swc-2-conductor's session e78bbab4 of 2026-10-08):
  - A fresh session's transcript does not exist until its first prompt. This session's first records, the SessionStart hook's and the prompt's, are stamped 0.1 seconds apart although the hook ran seconds earlier. The stub claude and README already say the same: a conversation is written once it has a message.
  - A plain prompt is a record of type `user` whose `message.content` is the text as sent, `[crew tell from …]` mark included.
  - A slash command is a `user` record holding `<command-name>/opsx:propose</command-name>` and `<command-args>…</command-args>`, the arguments as typed. `transcript.py` already reads this form (`SLASH`, `stage_args`).
  - A prompt sent while the agent is working is queued, and recorded at once as `{"type":"queue-operation","operation":"enqueue","content":"<text>"}`, then as a `user` record when Claude submits it.

Pages of `docs/architecture/` whose areas this touches: `teams.md` (`plugin/bin/crew`, `plugin/lib/crew.py`), `signals.md` (`plugin/lib/transcript.py`), `tests.md` (`tests/`), `docs.md` (README, `docs/`, `openspec/`), `briefs.md` (`plugin/skills/crew/SKILL.md`). Rules relied on: `teams.15` (the rule this builds), `teams.4`, `teams.2`, `teams.7`, `teams.11`, `roles.4`, `read.1`, `read.2`, `read.3`, `code.1`, `code.2`, `code.3`, `state.4`, `tests.4`, `tests.8`, `docs.2`, `docs.4`. Nothing here departs from a rule.

## Goals / Non-Goals

**Goals:**
- A stage crew starts either begins, with its prompt in the agent's transcript, or crew says it never started. No prompt sits typed in a pane waiting for a hand.
- Greetings and ops's proof request get the same guarantee.
- A prompt is never sent a second time into an agent that took the first.

**Non-Goals:**
- `crew tell` from an agent or the user, and the notices `plan.py` sends. They keep one sending; whether they should be read back too is for the planner (named in the construct's final message).
- The `/exit` and `/clear` crew types to end or clear an agent.
- Running the stage again by itself. A stage that never started is reported; the conductor runs it again.
- herdr's `--wait` stall gate. It reads activity, not delivery, and herdr itself says a stall does not prove the prompt was lost.

## Decisions

### 1. The transcript is the reading

The prompt was taken when the agent's transcript holds a record, written after crew sent it, that is that prompt as Claude received it. That is the one place the prompt lands only once Claude has it.

Alternatives considered:
- *herdr's `--wait` and `agent_prompt_stalled`.* It reads whether the agent got busy within five seconds. A slow start reads as stalled though the prompt was taken, and herdr warns against sending again on it, which is exactly what this change must do safely.
- *Reading the pane for the typed text.* The screen's layout is Claude Code's and undocumented (`read.2`); `teams.11` already found that a screen reading misses.

### 2. Ready for input

Before each sending crew waits until herdr reports the agent `idle` or `done`, `waits_on_question` finds no question open, and herdr names the agent's session. For a stage's fresh agent the wait lasts up to 60 seconds after `start` returns. A greeting keeps `greet_agent`'s waits (90 seconds, five minutes once a question is open). An agent that never becomes ready gets nothing typed, and the outcome is "never started" with the reason: it is not up, it waits on a question in its pane, or herdr names no session.

### 3. Where the transcript ended before the sending

Just before sending, crew notes the session herdr names and the length in bytes of that session's transcript, 0 when it has none (a fresh session has none until its first prompt). After sending, it reads only the complete lines written past that point. If herdr names a different session after the sending, crew reads that session's transcript from its start. So a greeting identical to one an earlier start received is never mistaken for this one.

### 4. What counts as the prompt received

A line past the noted point counts when it is:
- a record of type `user` any of whose strings, with whitespace collapsed, contains the sent text with whitespace collapsed; or
- for a sent text of the form `/<command> <args>`, a `user` record holding `<command-name>/<command></command-name>` whose `<command-args>`, collapsed, equal `<args>` collapsed; or
- a record of type `queue-operation` with `operation` `enqueue` whose `content` holds the sent text, collapsed. The prompt is queued, and Claude submits it when the turn ends.

Records of type `assistant` never count. The reading's docstring names these facts of Claude Code's format and where they were read (`read.2`). When they stop holding, every stage is sent twice and reported as never started: loud, never a silent false start.

### 5. The time, and sending again

crew reads the transcript about once a second for up to 15 seconds after each sending. Claude Code writes the prompt's record as it submits it, so a taken prompt shows within a second or two even on a loaded host. The environment variable `CREW_TAKEN_WITHIN` (seconds) shortens the 15 seconds for the tests (`tests.8`). No production caller sets it.

When the time passes with nothing received:
- **The agent is `idle` or `done`.** The prompt was not taken. crew sends one `ctrl+c` with `herdr agent send-keys <agent> ctrl+c`, which clears whatever was left typed in the input. It waits two seconds, so that a press on an already empty input, which arms Claude's "press again to exit", lapses. Then it sends again, from step 2.
- **The agent is `working`.** It may have taken the prompt with the record still to come. crew keeps reading, with no `ctrl+c` and no second sending, for up to 60 more seconds. If the record never comes, crew cannot tell. A `working` agent is never interrupted and never sent the prompt again.
- **The agent is `blocked`, or crew cannot read the transcript or herdr.** crew cannot tell, and sends nothing more (`read.1`).

After the second sending is not taken, and the agent is `idle` or `done`, crew sends one more `ctrl+c` so nothing is left typed, and the outcome is "never started".

### 6. One sending, three outcomes, run on the agent's host

`crew.py` gains one function that does decisions 2 to 5 for an agent by name and returns one of three outcomes:
- **taken**, with how many sendings it took;
- **never**, with why: not ready, or not taken twice;
- **unread**, with what crew could not read.

The transcript reading lives in `transcript.py`, which imports only the standard library. It gains a command-line entry so `crew.py` can pipe it to `python3 -` on the agent's host through `on_machine`, as it pipes `questions.py` (`code.1`, `code.3`): one call answers where a session's transcript ends, another whether a prompt was received past a point. Both answer one JSON object, an unreadable transcript as `{"unread": "<what>"}`, and write nothing (`state.4`). A host that does not answer is unread, named (`read.3`).

`tell` gains a way to send through this function instead of its single `agent prompt`, keeping its own checks and its mark. `greet_agent` and the proof's tell use it; `crew tell` and the notices do not.

`run_stage` stops typing the prompt itself. It calls a new `crew.py stage-prompt <agent> <prompt>`, which sends the prompt unmarked, as a stage's own prompt is (`roles.4`), and exits:
- 0 when taken;
- 3 when never started, saying why on standard error;
- 1 when crew could not tell, saying what it could not read.

### 7. What is recorded and said

- **Taken.** As today: `stage.start` (or `fix.start`, `fix.merge`) with the stage's objects, the owed end in the stages file, and the command's line naming the slot and stage. A greeting records `greet` and says "<agent> greeted".
- **Never started.** `run_stage` records the act with `--refused "<reason>"` on the same objects. It carries the same `Amended` field and entry id an amended construct passes, so the plan's mark still names an entry. Nothing goes in the stages file, so `crew unit wait` finds no stage owed (`teams.4`). The slot stays held and its idle agent stays up; the next `crew unit run` ends it and starts afresh (`teams.2`). The command fails with: `<agent> never took its <stage> prompt for <unit or fix>, sent twice; the stage never started and nothing is left typed in its pane: run it again with crew unit run <unit> <stage>`. For a fix it names `crew fix <team> <name> …`. When the agent was never ready, the sentence says why in place of "sent twice", and nothing was typed.
- **Never taken, for a greeting.** No `greet` entry. The greeting prints `<agent> did not take its greeting, sent twice; nothing is left typed; once it is ready: crew tell <agent> '<text>'` and returns false, which fails nothing else (`teams.7`).
- **Never taken, for the proof.** `prove` records the proof's start as refused, owes no proof, and fails saying the proof never started.
- **Cannot tell.** The same refused entry and failure, naming what could not be read. Nothing more is sent or pressed.

## Risks / Trade-offs

- [A prompt taken but its record written more than 15 seconds later while the agent is already idle again] → crew would clear and send again, and the agent would get the prompt twice. Claude writes the record as it submits, and a stage's prompt keeps its agent working far longer than 15 seconds, so this needs a greeting answered in under 15 seconds with its record lost. Accepted.
- [Claude Code changes how it records prompts] → every sending reads as not taken, and stages fail as never started, loudly, naming the agent. The reading's docstring names the facts to re-read.
- [The one `ctrl+c` lands on an agent that just became busy] → crew presses only after reading `idle` or `done`. A turn that starts between that reading and the key would be interrupted, and the transcript would then hold the prompt, so the second sending is not made. The window is a fraction of a second.
- [A stage that never started leaves its slot held with an idle agent] → by design: the unit is still in flight. The conductor runs the stage again, which ends that agent first.
- [Each stage start now takes a transcript reading or two] → about a second when the prompt is taken at once. In the tests the stub writes the record as it is sent, so nothing waits.

## Proof in dev

crew has no deploy; this list is worked on real work once the bolt has landed and every host has pulled (CLAUDE.md, "Proving and landing a bolt"). Every check below can only be made against live herdr and Claude Code.

1. **Ctrl+C clears a draft.** On mac-studio, in a scratch herdr pane running Claude Code 2.1.292 or later, type text into the idle agent's input without submitting it. Then run `herdr agent send-keys <agent> ctrl+c`. The input is cleared, Claude Code is still running, and two seconds later `herdr agent prompt <agent> "say hi"` is received as one prompt. This is the vendor fact decision 5 rests on, read from Claude Code's documentation only.
2. **A real stage is taken first time.** The first `crew unit run <unit> code` on a real team after landing prints that the slot has the unit in code. `crew events --about stage/<unit>/code` shows one start and no refusal, and the agent's transcript holds `<command-name>/opsx:apply</command-name>` with the unit's name in its arguments.
3. **A real greeting is taken first time.** `crew main up <label>` or `crew revive` on mac-studio and on the box says each agent it started was greeted, once.
4. **No false refusals over a day.** After a day of normal work across the teams, `crew events` shows no stage or proof start refused as "never took its prompt", unless a pane really was left with its prompt typed. In that case the refusal, not a typed prompt, is what the conductor saw.

## Task notes

### 1.1 Where a transcript ends, and whether it received a prompt

In `plugin/lib/transcript.py`:
- `end(session)`: the session's transcript path and its length in bytes, `0` with no path when `find` finds none. Also say whether the file exists, so a caller can tell "no transcript yet" from "can't read".
- `received(session, offset, text)`: whether any complete line past `offset` is the prompt as decision 4 defines it. Reuse `lines`, `collapse`, `strings`, `kind` and `stage_args`. Generalise the slash match from `/opsx:` to any `/<command>` only inside this function; leave `SLASH` and `asserter` as they are.

Add `if __name__ == "__main__":` with `end <session>` and `received <session> <offset> <text>`, each printing one JSON object (`{"path": …, "size": n}`, `{"received": true|false}`, or `{"unread": "<what>"}`). Keep the module stdlib-only. Extend the docstring with the transcript facts in this design's Context, where they were read, and what happens when they stop holding.

Tests go in `tests/t-transcript.sh`. Cover: a plain prompt, a marked greeting, a slash command with arguments, a queued enqueue, an assistant record quoting the prompt (not received), a match only before the offset (not received), and an unreadable transcript (unread).

### 1.2 The stub takes or leaves a prompt

`tests/stubs/herdr`, `agent prompt` to an unblocked agent, other than `/exit`, appends a record to the transcript of the agent's stub session `sid-<pane>`, at `$HOME/.claude/projects/<the pane's cwd, every non-alphanumeric a dash>/sid-<pane>.jsonl`. Create the folder and file if needed. The record carries a `timestamp`, as Claude's do:
- a `/<command> <args>` prompt as `{"type":"user","message":{"role":"user","content":"<command-name>/<command></command-name>\n<command-args><args></command-args>"}}`;
- any other prompt as `{"type":"user","message":{"role":"user","content":"<text>"}}`.

A test-only command `herdr --session S stub leave <agent> <n>` makes the next `n` prompts to that agent untaken: each is appended to the agent's `typed` text in the stub state, and nothing goes in the transcript. `agent send-keys <agent> ctrl+c` empties `typed`. Then a test can assert both that a prompt was left untaken and that nothing is left typed at the end. Say both in the stub's docstring (`tests.4`).

Check the tests that read a slot's transcript: `t-stage-ends`' "no transcript for its session" expectation, and any fixture a test writes with `transcript` before a stage starts, which `cat >` would overwrite. Fix the expectations, or write such fixtures after the stage starts, so each test still proves what its comment says.

### 2.1 One sending

In `plugin/lib/crew.py`, one function (for example `send_taken(fleet, name, text, ready_wait)`) does decisions 2 to 5 through `on_machine` and returns `("taken", n)`, `("never", reason)` or `("unread", what)`.
- Pipe `transcript.py` as `questions.py` is piped (a module-level `TRANSCRIPT = (LIB / "transcript.py").read_text()`).
- Read `CREW_TAKEN_WITHIN` once, as whole seconds, defaulting to 15. Refuse a value that is not a positive whole number through `fail()` (`code.2`).
- The "working" grace is 60 seconds, and the ready wait for a stage's agent is 60 seconds. Keep each a named constant.

`tell(…)` gains `taken=False`. When true it sends through this function rather than its single `agent prompt`, after its existing checks, and keeps its mark. The `crew.py tell` command line accepts a trailing `--taken`.

Add `crew.py stage-prompt <agent> <prompt>`, with exits 0, 3 and 1 as decision 6 says, and its usage in the module docstring.

Write `tests/t-prompt-taken.sh`, with its opening comment and `lib.sh` line (`tests.2`). Through `crewpy stage-prompt` against stub agents, cover: taken at once (one prompt in the log, no `ctrl+c`); left once then taken (two prompts, one `ctrl+c` between, nothing typed after); left twice (exit 3, two `ctrl+c`, nothing typed); blocked throughout (exit 3, nothing typed, the reason names the question); working with no record (exit 1, one prompt, no `ctrl+c`). Set `CREW_TAKEN_WITHIN=1`, and wait on conditions, never on fixed sleeps (`tests.8`). Run `tests/moon-tasks` and commit `tests/moon.yml`.

### 2.2 Greetings

`greet_agent` calls `tell(…, record=False, taken=True)`.
- On never: print the line in decision 7 and return False, recording no `greet`.
- On unread: print what could not be read and return False.

Add to `tests/t-greet.sh`: a conductor whose greeting is left once is greeted, with two prompts in the log and one `greet` entry. One left twice is not greeted: no `greet` entry, the line with the `crew tell`, and nothing typed.

### 3.1 Stages

In `run_stage`, replace the `h agent prompt` line with `py stage-prompt "$(name_of "$slot")" "$prompt"`, capturing its standard error.
- On exit 0, go on as today.
- Otherwise, emit the entry with `--refused "<the message>"` and the same `"$@"` (which carries `--field Amended=yes --commit … --id …` for an amended construct). Write nothing to the stages file, print the message, and exit 1.

The message's wording is decision 7's. `run_stage` knows the stage, the held name and the object, so it can name the command to run again. Pass it what it needs, and keep the wording in one place.

Add to `tests/t-unit-run.sh`: a code stage whose prompt is left once starts, with one `stage.start`. One left twice fails with the never-started line: a refused entry in the run record, no line in the stages file, the slot still held, and `crew unit run` of the same stage then starting it. Add to `tests/t-fix.sh` one fix whose prompt is left twice, failing the same way.

### 3.2 The proof's request

In `prove`, send with `py tell "$TEAM-ops" "…" --taken`.
- On failure, record the proof's `stage.start` as refused with the tell's message, owe nothing, and exit 1, saying the proof never started.
- A tell refused for a question in ops's pane fails down the same branch: it too records the proof's `stage.start` as refused and says the proof never started, as decision 7 has it for any request ops never took.

Add to `tests/t-stage-ends.sh` (where `crew prove` is tested) one proof whose request is left twice.

### 3.3 A merge crew cannot tell was taken

`run_stage`'s branch for `stage-prompt`'s exit 1 is built, but no test runs it through `crew unit run`. In `tests/t-unit-run.sh`, with `CREW_TAKEN_WITHIN=1`, run `stub leave swb-1-unit-1 1 blocked` and then `crew unit run a merge`: the stub leaves the prompt typed and puts the agent on a question, so once the second passes crew reads it waiting on a question and cannot tell (decision 5). This reaches the same branch as an agent that went to work with no record, without the 60-second working grace, which `t-prompt-taken` already waits out once; add no knob for that grace. Check that the command fails with `crew could not tell whether swb-1-unit-1 took its merge prompt for a`, naming `crew unit run a merge`; that the run record's last start on `stage/a/merge` is refused with that line; that the stages file owes no merge; and that the herdr log shows the merge prompt once and no `ctrl+c`. Clear the stub agent's question afterwards if later cases need the slot.

### 3.4 A fix whose agent is never ready

In `tests/t-fix.sh`, start one fix with its agent named in `CREW_TEST_BLOCKED`, so the stub stops it on a question once it has its name. Check that `crew fix` fails with the line saying the agent never took its fix prompt for that fix "as it was waiting on a question in its pane", naming `crew fix <team> <name> …` to run it again; that the herdr log shows no prompt typed to it; that the run record holds a refused `fix.start`; and that the stages file owes nothing. The case waits out crew's 60-second ready wait; where the file allows, start it in the background beside its other cases, as `t-prompt-taken` does, rather than adding a knob for that wait.

### 4.1 The docs and the rule

- README's Teams section, where it says a stage's agent is sent its command, and the greeting paragraph near "crew's greetings and notices go the same way": say a stage begins only once its agent's transcript shows the prompt, sent once more if not, and is otherwise reported as never started with nothing left typed; and that a greeting is read back the same way.
- The `crew unit run`, `crew fix` and `crew prove` lines in `plugin/bin/crew`'s usage header and in `plugin/skills/crew/SKILL.md` get the same words, briefly (`docs.2`).
- In `docs/architecture/teams.md`, the details of `teams.15` drop "not built: `_open.md`" and name the source: `run_stage`, `crew.py` `send_taken` (or its final name) and `stage-prompt`, `transcript.py` `received`, `tests/t-prompt-taken.sh`.
- Remove `teams.15`'s line from `docs/architecture/_open.md`.

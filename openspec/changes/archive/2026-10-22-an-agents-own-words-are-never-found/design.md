# Design

## Context

`transcript.check` walks every string of every complete line of the live session's transcript, knowing no field name, and passes over three kinds of line: those of top-level type `assistant`, what the agent wrote; the `crew signal … --excerpt` command lines inside a string; and lines naming a path in `skip`, the writing of an excerpt file. A hit in a `user` record is `verified`, with its asserter read from the record (`signals.5`); a hit in any other record is `found`; no hit is `refused` (`signals.2`). See proposal.md, *Why*, for what goes wrong.

Facts of Claude Code's format this rests on, read on deneb on 2026-10-22 from Claude Code 2.1.303's transcript of session f965a6bb-1725-4522-8d49-576f4bb1fc50 (crw-6-unit-2, a chore's verify of 2026-10-20, under `~/.claude/projects/-Users-chuck-Code-github-afterthought-crew-places-chore-a-drops-close-of-its-card-carries-no-question/`), and again in 2.1.307's transcript of this construct's own session:

- Each message Claude Code sends the model is also written as a line `{"type": "api-request-blob", "sessionId": "<id>", "hash": "<sha256>", "message": {"role": "user" | "assistant" | "system", "content": [...]}}`. It has no `uuid` and no `timestamp`.
- A copy of role `assistant` holds the agent's `thinking`, `text` and `tool_use` blocks; one of role `user` holds the user's `text` and the tools' `tool_result` blocks; one of role `system` holds Claude Code's own context and `tool_addition` blocks. In f965a6bb, the agent's sentence "Diff reviewed; checking the sweep's close tuples, then running the affected logi…" is at line 110, type `assistant`, and its copy at line 105, type `api-request-blob`, role `assistant`. Today's `check`, run on that file with its freshness lifted, grades that sentence `found` at line 105.
- Every `user` and tool text a copy holds is also in a record of its own; the only words found in copies alone were Claude Code's own `system` reminders. The same file holds `api-request` lines, hashes and parameters, and one `api-request-shape`, the system prompt and the tool definitions: neither holds anything the agent wrote, and they are left as they are.

Rule pages whose area this touches: `signals.md` (`transcript.py`) and `tests.md` (`tests/`).

## Goals / Non-Goals

**Goals:**

- An excerpt that is only in the agent's own writing, its own records or Claude Code's copies of them, is refused (`signals.2`).
- Every excerpt that is verified today keeps its grade, asserter and source record.
- The module's header names the new format fact, the transcript it was read from, and what falls when it stops holding.

**Non-Goals:**

- The refusal's message and the briefs' words: "quote the words as you received them" already covers an agent quoting itself (`plan.excerpt_refusal`, unchanged).
- `received`, which counts only records of type `user` and `queue-operation`; a copy never counted there.
- `pending`, `started_commands` and `last_at`: a copy holds no `toolUseResult`, `<task-notification>` it is not already in its own record, or timestamp.

## Decisions

### Skip the copy record type whole, as the agent's own records are skipped

`check` passes over a line whose top-level type is `assistant` or `api-request-blob`, held as one set of the types the agent's writing and its copies come under, so the format fact is one word in one place. Nothing in a copy is lost: what the session received is in its own record, which keeps winning as the source (`signals.3` banks that record's line, which has the uuid and time a copy lacks).

Considered: skipping only copies whose `message.role` is `assistant`. Rejected: it leans on a second field of an undocumented format where one top-level type does, and the copies of role `user` and `system` add no record the session received that the check doesn't already have. The one thing it would keep, a `found` grade for Claude Code's own `system` reminders, is no one's assertion a finding should rest on.

Considered: reading `message.role` across every record and skipping any whose role is `assistant`. Rejected for the same reason, and because the module's stance is to know as few field names as it can.

### The header says what the fact holds and what falls without it

The module docstring's paragraph on the two facts of the format becomes three: a type of `user` marks a record the session received, one of `assistant` a record the agent wrote, and one of `api-request-blob` Claude Code's copy of a message it sent the model, the agent's own among them, read from session f965a6bb as above. When the copy's type changes, a quote of the agent's own earlier words grades `found` again: a grade too high, never a capture stopped. The `refused` line of the grade table gains "or Claude Code's copies of what it sent the model", and `check`'s docstring says the same.

### Where the cases go

The check is a function of a file under a scratch HOME: logic cases in `tests/py/test_transcript.py`, `TestCheck`, beside `test_words_only_in_the_agents_own_record_nowhere_or_only_in_a_crew_signal_command_are_refused` (`tests.4`, `tests.11`). A builder for the copy record sits beside `wrote`, `tool` and `ran`, its comment naming the version and session it was read from as theirs do. No test file is added or removed, so `tests/moon.yml` does not change (`tests.10`).

### What this change does not edit

`docs/architecture/signals.md`: its `signals.2` details already say what this unit holds to and are the design agent's (`docs.7`). README's Signals section already says a signal is refused when the words are nowhere but in what the agent wrote itself, which is what this makes true again; no command's behaviour changes, so the usage header and the skill stay as they are (`docs.2`). `tests/py/test_signals.py` decides on verdicts, not transcripts, and holds as it is.

## Risks / Trade-offs

- [Claude Code renames or reshapes the copy] → The agent's own words grade `found` again, as on 2.1.303 today; nothing that is not a paraphrase is refused. The header names the version and session the fact was read from, so the next reading knows what to compare.
- [Claude Code's own reminders are refused when quoted] → They are words neither the user nor a tool said; the refusal's "as you received them, from the user or from a tool's output" is right for them.
- [A future copy holds something received nowhere else] → It would be refused rather than found. The reading of 2.1.303 and 2.1.307 found no such words but Claude Code's own; a later reading that does is a new signal.

## After deploy

None: the change is a decision on a file, proved whole by the logic tier.

## Task notes

**1.1**

In `plugin/lib/transcript.py`, add beside `FRESH` a constant naming the types whose lines are the agent's writing, `assistant` and `api-request-blob`, with a comment saying the second is Claude Code's copy of each message it sends the model (2.1.303, session f965a6bb). In `check`, the first line of the loop skips a line whose `kind(v)` is in that set, in place of `== "assistant"`. Update `check`'s docstring ("lines of type assistant what the agent wrote" gains its copies) and the module header as *The header says what the fact holds and what falls without it* gives. Nothing else in the module changes.

**1.2**

In `tests/py/test_transcript.py`, add a builder `copied(role, content)` beside `wrote`: `{"type": "api-request-blob", "sessionId": "s", "hash": "<64 hex>", "message": {"role": role, "content": content}}`, no `uuid` or `timestamp`, under a comment saying it is shaped as Claude Code 2.1.303 writes it (deneb, session f965a6bb, 2026-10-22). Then cases in `TestCheck`:

- The agent's own reply: a user record, then `wrote("a-50", "The sweep leaves cards open on a closed row.")` and `copied("assistant", [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "The sweep leaves cards open on a closed row."}])`, in either order: that sentence is `refused unknown None None`.
- A command the agent ran: an assistant record with a `tool_use` block whose `input.command` is `echo "cards stay open on a closed row"`, and its copy of role `assistant`: "cards stay open on a closed row" is refused.
- Only in a copy: `copied("system", [{"type": "text", "text": "The user hasn't heard from you in a while"}])` alone with a user record: those words are refused.
- The user's words and their copy: `user("u-51", "Close the open cards on a dropped row.")` then `copied("user", [{"type": "text", "text": "Close the open cards on a dropped row."}])`: `verified user 1 u-51`.
- A tool's output and its copy: `tool("u-52", "3 cards left open")` then `copied("user", [{"type": "tool_result", "tool_use_id": "t", "content": "3 cards left open"}])`: `verified tool 1 u-52`.

Run `devenv shell -- moon run tests:logic` before and after 1.1: the first three cases fail before it (`found`) and every case passes after.

**2.1**

Run `tests/suite --affected` once, all tasks done; it ends with "0 failed".

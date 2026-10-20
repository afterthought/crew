# Design

## Context

`crew signal`, run by an agent, looks for its excerpt in the agent's own Claude Code transcript (`transcript.check`) and refuses it only when the transcript is the live session's and the words are nowhere in it but in what the agent wrote itself (`signals.2`). Who asserted words that are found is read from the record (`signals.5`): a record holding a `tool_result` block is a tool's. So a tool's output that reached the transcript, a crew command's among them, is already verified as a tool's; `test_transcript.py` pins it for a `tool_result` with string and block content.

What went wrong on 2026-10-20 is read in `signals.2`'s details (the design agent, for this unit, then named `a-tools-words-are-not-lost`): crw-2's conductor quoted "No session was started for card land/every-deploy-offer-reaches-the-user". `crew card wait` had run as a background task. Claude Code writes a background task's output to a file under the session's tasks folder, and the transcript gets only the call's record, with an empty `stdout` and a `backgroundTaskId`, and later a `<task-notification>` naming the `<output-file>` and a one-line summary. The output reaches the transcript only when the agent reads that file. crew had also printed the line lowercase. The refusal was right; its words, "quote the words as you received them, from the user or from a tool's output", sent the conductor looking for a rewording it had not made, and it gave up.

What the unit holds to, from that reading: a tool's words an agent quotes are the words as its transcript received them, so an output read from a task's file is read into the pane first, and crew's refusal names that case, a background task's output, beside the paraphrase.

Facts of Claude Code's format this rests on, read on mac-studio on 2026-10-20 from Claude Code 2.1.303's transcripts (session 3e419169 under `~/.claude-madswan-madswan/projects/-Users-chuck-Code-github-afterthought-crew-main/`, and a coder's session 6bf3f15e):

- A background Bash call is answered by a `type: user` record whose `toolUseResult` is `{"stdout": "", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false, "backgroundTaskId": "<id>"}`.
- Its end is a `queue-operation` record whose `content` is `<task-notification>` with `<task-id>`, `<tool-use-id>`, `<output-file>/private/tmp/claude-501/<folder>/<session>/tasks/<id>.output</output-file>`, `<status>` and `<summary>Background command "<description>" completed (exit code 0)</summary>`. The output itself is not in it.
- A Read of a file is answered by a `type: user` record whose `tool_result` content is the file with a line number and a tab before each line, and whose `toolUseResult` is `{"type": "text", "file": {"filePath", "content", "numLines", "startLine", "totalLines"}}`, `content` the file's text as it is.

The check walks every string of a record, so the raw `content` of a Read is searched beside the numbered lines: two lines quoted together match there.

Rule pages whose area this touches: `signals.md` (`plan.py`'s signal command), `teams.md` (`crew.py`), `briefs.md` (the words every recording brief carries, built in `crew.py`), `tests.md` and `docs.md` (README).

## Goals / Non-Goals

**Goals:**

- An agent refused for a background task's output learns from the refusal what to do, and records the finding itself.
- The briefs say what a refusal means in the same two cases.
- Logic cases pin that a tool's printed words, a crew command's line and a background task's output once read, are verified as a tool's, and that a background task's output not yet read, and a printed line recapitalized, are refused.

**Non-Goals:**

- The check's matching, its grades and who it says asserted the words do not change (`signals.2`, `signals.5`).
- crew does not read a background task's output file, and the refusal does not show the nearest words it found (see *Decisions*).
- Claude Code's `api-request-blob` records (see *Risks*).

## Decisions

### The transcript stays the one place crew searches

crew searches only what the session received, as `signals.2` has it and the reading of 2026-10-20 rules: the refusal was right. A capture is the one record the session received that holds the excerpt, and its raw record is that transcript line, banked on the host (`signals.3`). A task's output file is not a record the session received, sits under a temporary folder Claude Code clears, and has no uuid or time crew could name the capture by.

Considered: following each `<output-file>` a task notification names and searching those files too. Rejected: it would record as "received" words the agent never had before it, and the capture would point at a file that is gone within days. The agent reading the file is one step, and it puts the words in the transcript where every rule already holds.

### The refusal's words, decided by a function of the verdict

The refusal becomes a decision, `excerpt_refusal(v)` in `plan.py` beside `signal_refusal`: the message for a `refused` verdict, `None` for any other (`code.7`). `signal` fails with it through `fail()` (`code.2`). The message keeps its present opening, which `t-journey-signals.sh` and the run record's `Refused:` entry are matched on, and adds the background task's case:

> the excerpt is not in your session's transcript: quote the words as you received them, from the user or from a tool's output. A background task's output reaches your transcript only once you read the output file its task notification names: read that file, then record the signal again

It says nothing of the case of the letters: "as you received them" already asks for the words exactly.

Considered: naming in the refusal which background tasks the session has started, read with `transcript.pending`. Rejected: the source names the case, not the task, and a task told over is no longer pending, which is exactly the conductor's case.

### The briefs' sentence

`signal_how` in `crew.py`, shared by the six briefs that record findings, says today "a refusal means the words were reworded". It keeps those words, which `t-briefs.sh` checks, and goes on: "or are a background task's output you have not read: read the output file its task notification names, then record the signal again."

### Where the cases go

The refusal's words are a decision on a verdict: a logic case in `test_signals.py`. The check on the transcript shapes above is `transcript.check` on files under a scratch HOME: logic cases in `test_transcript.py`, beside the existing tool-output case (`tests.4`, `tests.11`). The briefs' words are `t-briefs.sh`'s, as now. No test is added or removed, so `tests/moon.yml` does not change (`tests.10`).

### What this change does not edit

`docs/architecture/` is the design agent's (`docs.7`): `signals.2`'s details already say what this unit holds to, and are left as they are. The usage header and `plugin/skills/crew/SKILL.md` say nothing of refusals; README's Signals section does, and gains the background task's case (`docs.2`).

## Risks / Trade-offs

- [The format changes] Claude Code may one day put a background task's output in the transcript, or stop naming the output file. → The refusal's sentence is then advice the agent no longer needs; nothing is refused that the transcript holds. The fixtures name the version they were read from.
- [An agent's own words found, not refused] Claude Code 2.1.303, read on mac-studio on 2026-10-20, also writes `api-request-blob` records, copies of the messages it sends the model, among them the agent's own (`message.role: assistant`) under a top-level type that is not `assistant`. The check skips only records of type `assistant`, so on that version words the agent wrote in an earlier turn grade `found` rather than refused. This weakens `signals.2`'s refusal of a paraphrase and is not this unit's to change; it is named for the planner and the design agent. This unit's cases build their transcripts by hand and do not depend on it.

## Task notes

### 1.1

In `plan.py`, beside `signal_refusal`, add `excerpt_refusal(v)`: the message in *The refusal's words* for a verdict whose grade is `refused`, `None` otherwise. In `signal`, replace the inline `v.grade != "refused" or fail(...)` with `excerpt_refusal(v) and fail(excerpt_refusal(v))`, as `signal_refusal` is used two lines above. Nothing else in `signal` moves.

In `tests/py/test_signals.py`, a case (in `TestFiles`, beside the slug refusals, or a class of its own) that a refused verdict's message begins with the present words, "the excerpt is not in your session's transcript: quote the words as you received them", and names a background task's output and its output file; and that `verified`, `found` and `unverified` verdicts give `None`.

Run `devenv shell -- moon run tests:logic`, then `tests/suite t-journey-signals`, which must pass unedited.

### 1.2

In `tests/py/test_transcript.py`, in `TestCheck`, with records shaped as *Context* gives (add small builders beside `tool` and `wrote` if they read better):

- A conductor's transcript holding the foreground Bash result of `crew card wait`, its `tool_result` content and its `toolUseResult.stdout` both `no session was started for card land/every-deploy-offer-reaches-the-user`: that excerpt is `verified tool`; `No session was started for card land/every-deploy-offer-reaches-the-user` is refused.
- A transcript holding the background call's record (empty `stdout`, a `backgroundTaskId`, a `tool_result` that does not hold the line) and the task notification naming its output file: the line is refused.
- The same transcript with a Read of that output file after it, its `tool_result` the numbered lines and its `toolUseResult.file.content` the raw text of two lines: each line, and the two quoted together across the line break, are `verified tool`, the Read's record the source.

These pass with today's `transcript.py`: they pin behaviour, and `transcript.py` is not edited. If one fails, the check does not do what `signals.2` and `signals.5` say; stop and say so rather than changing the check.

### 2.1

In `crew.py`'s `signal_how`, extend the sentence as *The briefs' sentence* gives. In `tests/t-briefs.sh`, in the loop over the six recording briefs, keep the `has "$out" "a refusal means the words were reworded"` and add a `has` for "or are a background task's output you have not read". Run `tests/suite t-briefs`.

### 2.2

In README's Signals section, the paragraph beginning "A signal is refused only when": add that the refusal says so, and that a background task's output is in the transcript only once the agent has read the output file its task notification names, so the agent reads it and records the signal again. Run `tests/suite t-docs`.

### 3.1

Run `tests/suite --affected` once, all tasks done; it ends with "0 failed".

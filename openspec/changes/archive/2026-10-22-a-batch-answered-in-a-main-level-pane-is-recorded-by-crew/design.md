# Design

## Context

Today a batch can be answered in only two ways. The planner's `crew card wait batch/<n>` (`plan.py` `batch_wait`, `batch_waited`) hears the card or the reading session, and closes the card with `row_card_close`. `batch_closed` then reads the batch closed from that `card.close` in the run record, and that drives three readers. `awaiting_answer` frees the units, so `land_facts` builds the landing card and `rail_rows` gives the landing row its word to land. `record_reading` drops the batch's row. `batch_facts` raises no card. The rail's sweep then raises the landing card on the team's host as soon as the row is offered. So "offered for landing as on a tap" comes for free once `batch_closed` counts the pane answer. This change adds a third input to `batch_closed`. It does not add a new landing path.

Two facts on main shape the approach:

- **The run record never holds typed text** (`record.3`). The user's words can't be stored in the `batch.answer` entry. They live in the transcript, and the entry points at them: the caller's session, which `record.emit` writes, and the transcript record's id, in `From` as `session/<sid>/<uuid>`, the same shape as a capture's key. Every reader after the command, meaning the wait, the sweep and the rail, works from the entry alone and says *in whose pane* and *when*, not the words. Only the command itself has the words, and it passes them on in the three places they belong: the held card's close, the tell to the planner, and its own output.
- **`transcript.check` returns the last received record that holds the words.** An echo of the user's words in a later tool output, such as this command's own earlier output or a `crew card wait` printing a note, would be graded `tool`, and the answer refused. `crew signal` avoids this for its own command lines with `COMMAND`, which is narrower than what is needed here.

Rules relied on: `briefs.12`, `briefs.13` (a batch answered by the user's words in a main-level pane, and its card closed by them); `signals.5` (who asserted a record, which `transcript.asserter` reads); `record.3` (no words in the record); `read.1` (a transcript crew can't read refuses, never guesses); `read.2` (a field read only against the tool as it is); `read.5` (the entry reaches the branch as every entry does, and every host reads the batch answered from there); `code.2` (refusals through `fail()`); `code.7` (the refusal and the reading of the record are functions of facts, tested in the logic tier); `roles.4` (a tell is marked, and `[crew]` is crew's own, never the user's). `code.8`: no new thing the board or bands draw. A batch answered in a pane is a batch row that goes, as one answered on its card does, so `board.agent_views` and `status.js` are unchanged.

Pages whose areas this touches: `plan.md` (`plan.py`), `signals.md` (`transcript.py`), `briefs.md` (`plugin/roles/`), `tests.md` (`tests/`), `docs.md` (README, SKILL.md, `plugin/bin/crew`'s usage). It does not touch `record.md`: `record.py` is unchanged, since the entry uses fields the descriptor already allows.

## Goals / Non-Goals

**Goals:**
- One command records a batch answered from words crew reads in the caller's own transcript as the user's, and refuses everything else.
- The answer is final and counts exactly as a tap does for the rail, the board, the landing and the batch's card.
- The user's words reach the planner, and through it the units' conductors, once.

**Non-Goals:**
- Raising again a batch card left on another host. That is proposal 209's unit, `a-batchs-card-left-on-another-host-is-raised-again`, which stands beside this change. Here, a batch answered in a pane raises no card again, since `batch_facts` reads it closed.
- Any other row answered in a pane. A record and a landing already are, and a proposal is not.
- `crew record --settled-in-pane` reading the user's words from the transcript. Record 0031's amendment says it does, but on main it takes the flag on trust. This change does not alter it.

## Decisions

### 1. The command is `crew card answer batch/<n> --excerpt "<words>"`

It belongs with the batch's other card commands (`session`, `wait`, `end`, `read`), takes the rail row's key, and is dispatched by `plugin/bin/crew`'s existing `card)` case. It takes one key, so three batches answered in one sentence are three runs with the same words. It runs on the caller's own host, never forwarded, because the transcript is there (`session_here`, as `check_excerpt` uses it). Only the planner and the operator of the batch's partition may run it, read with `role()`. The amendment names those two panes, and no other agent's pane holds the user's batch answers. A key of any other kind, and an old `batch/<n>-<k>`, is refused, naming `batch/<n>`.

Considered: `crew review <label> --answered <n>`. `review` starts the reviewer and waits for its summary, and has nothing to do with the card's answer. Also considered: a flag on `crew card wait`. That wait has no words in hand.

### 2. The words are checked as `crew signal` checks an excerpt, preferring the user's record

`transcript.check` gains a `want` argument. With `want="user"`, it returns the verdict of the newest received record holding the words that `asserter` reads as the user's. Only when there is none does it return the last received record, as now, so that the refusal can name who did say them. The command refuses the answer unless the verdict is `verified` and asserted by `user`. Each other verdict gets its own refusal:
- `refused`: the words are only in what the agent wrote itself.
- `agent:<name>`: another agent's tell, naming that agent.
- `crew`: crew's own message.
- `tool`: a tool's output.
- `found`: crew can't tell who wrote them.
- `unverified`: its reason (`read.1`).

`stage_by` is `None`, since neither role runs a stage.

Considered: reading the whole of the user's last message as the answer, with no excerpt. Then the agent could not pick which message answered the batch, and a later unrelated message would be taken as the note.

### 3. One entry, `batch.answer`, read by `batch_closed` as final

The act is `batch.answer`, on `batch/<n>`, with `Key: batch/<n>`, `Batch: <n>`, `Chars: <length of the words>`, `From: session/<sid>/<record>`, and `By` (the caller, via `record.emit`). Its record id is the transcript record's uuid, or its line hash when it has none, as `capture_named` makes a capture's key. `batch_closed` adds `batch/<n>` and every old `batch/<n>-<k>` key the entries carry for each batch answered so, after its loop. So no `card.post` after the answer opens the batch again, whichever order the hosts' entries arrive in. The refusal before the entry is a pure function: `pane_answer_refusal(n, entries, verdict, caller_kind)`. It returns the words of the first refusal in the spec's order, or `None`. The order is: no such batch; answered already (any key of batch `n` in `batch_closed`, naming how); waits on nothing (`batch_settled`); then the verdict.

### 4. The card is closed where it is held; the record keeps no words

After the entry, the command closes the planner's card under `batch/<n>` on this host through `row_card_close`, with the outcome `Answered in <agent>'s pane: <words>` cut as `cards.close_call` cuts. The `card.close` entry's `Outcome` is `Answered in <agent>'s pane`, without the words. That needs `card_closed` and `row_card_close` to take the words for Pending You apart from the outcome they record. With no card held here, the command says so, naming the host the record shows it posted from when there is one, and that the rail's sweep there closes it. `row_gone` gives a `batch/` key answered in a pane the outcome `Answered in <agent>'s pane at <HH:MMZ>`, so the sweep acks a card the user had answered and withdraws one still pending with those words. `batch_wait` reads the record each round, before the card. Once it holds `batch.answer` for its key, the wait prints `batch/<n>: answered in <agent>'s pane at <time>` and closes the card it holds with that outcome. That close ends the session, as a close does. The wait never prints the words, since the planner already has them from decision 5.

### 5. The words reach the planner once

When the caller is the operator, the command tells the planner through `tell_planner`, marked `[crew]` (`roles.4`): `Batch <n> was answered in <operator>'s pane: "<words>". Send each unit's part to its conductor, as you send a batch's notes.` When the caller is the planner, the command's output holds the words and no tell is sent. Either way, the planner sends them as *Batches* step 3 sends any note. A tell that fails is said, and the answer stands. Then, and only then, the operator carries the user's words to the planner itself with `crew tell`, as its brief already allows for a request in the user's words. That tell answers nothing, since the batch is already recorded. The operator sends nothing to a conductor.

### 6. The briefs

The planner's *Batches* gains a step: when the user answers a batch in your pane in their own words, run `crew card answer batch/<n> --excerpt "<their words, as they wrote them>"` once per batch, then send the words as step 3. "Never answer a batch card yourself" becomes "never answer a batch yourself". Only the user's own words in your pane answer it. When an agent tells you the user's answer, tell it the user answers on the card or in your pane, and record nothing. The operator gains the same command for its pane, with the words going to the planner through crew, and no tells of its own to conductors.

## Risks / Trade-offs

- [An agent quotes only part of the user's words as the excerpt, and drops a note] → The briefs say to quote everything the user said of the batch, as they wrote it. The excerpt must be in one received record, so it can't stitch messages together.
- [The transcript is more than `FRESH` old, for example when the agent ran the command long after the user spoke] → The check reads the transcript as written moments before the command, so it is fresh whenever the agent runs the command at once. When it is not, the refusal says why, and nothing is recorded (`read.1`).
- [Another host's crew is older and doesn't know `batch.answer`] → It reads the batch as still waiting until it takes crew's main. That is the same as any new act. A landing is offered by the newer crew's rail read on the team's host. The entry uses only fields the descriptor already allows, so `recfix` passes everywhere.
- [The planner's wait and the command both try to close the card on the same host] → The command closes it first, and `card_under` then holds none, so the wait's close says none was held. The wait reads the answer before the card each round, so it never records the card "closed outside crew".

## Migration Plan

None. Batches answered before this change keep their `card.close` and `batch.close` entries as they are.

## After deploy

None. Every scenario is proved by the logic tier and `t-briefs`.

## Task notes

**1.1** In `transcript.py`, `check(session, excerpt, skip=(), stage_by=None, want=None)`. In the loop, keep `received_user` beside `received`: the last user-kind hit whose `asserter(...)` is `"user"`. With `want == "user"` and `received_user` set, return its verdict. Otherwise return as now. Cases in `tests/py/test_transcript.py`, on transcripts written to a temp HOME as its cases do:
- the user's line, then a tool result echoing it: verified, user;
- only a `[crew tell from swancloud-operator]` line holding it: `agent:swancloud-operator`;
- only an assistant line: refused;
- a `[crew tell from chuck@deneb]` line: user.

**2.1** In `plan.py`, `batch_closed(entries)` collects the batch numbers of `batch.answer` entries that were not refused. After its loop, it returns `closed` plus `batch/<n>` and every `batch/<n>-<k>` key seen in any entry's `Key`, for each such `n`. Add `pane_answered(entries)`, returning `{key: (by, at)}` for every batch key answered so. `row_gone` uses it before `batch_settled` for a `batch/` key. Cases in `tests/py/test_batches.py`:
- an answer closes `batch/13`;
- a `card.post` under `batch/13` after the answer leaves it closed;
- an answer of batch 6 posted as `batch/6-1` and `batch/6-2` closes both;
- a refused answer closes nothing;
- `awaiting_answer` no longer names the units of batch 13;
- `row_gone("batch/13", …)` returns `("Answered in swancloud-planner's pane at 20:17Z", None)`.

In `tests/py/test_rail.py`: a landing row whose only waiting batch was answered in a pane carries `crew tell <label>-ops "Land bolt y."` as after a tap, and the batch's row is gone.

**3.1** `pane_answer_refusal(n, entries, verdict, kind)` is a pure function, where `kind` is `role()`'s kind for the caller and `verdict` is a `transcript.Verdict`. It returns `None` or the refusal's words, checked in this order:
1. The caller is not the planner or operator.
2. The record holds no `review.batch` for `n`.
3. A key of `n` is in `batch_closed`: "batch n was answered already", naming a pane answer's agent when `pane_answered` has one.
4. The batch is in `batch_settled`, with its words.
5. The verdict, as decision 2 lists.

Cases in a new `tests/py/test_batch_answer.py`, one per refusal and one passing, plus the operator's and the planner's passing verdicts.

**3.2** `card_answer(fleet, a)`, wired as `crew card answer <key> --excerpt <words> [--label L]` in the `card` subparser and the dispatch. The steps are thin around 3.1:
- `role(fleet, CREW_AGENT)` must be planner or operator, and its label is the partition (a `--label` naming another is refused).
- The key must match `batch/(\d+)`.
- Read the entries as the rail reads them for the label, refused when they can't be read whole (`read.1`).
- Get the verdict from `transcript.check(sid, words, want="user")` with `sid` from `session_here(record.session(), crew.this_host())`.
- Call `pane_answer_refusal`, and `fail()` on its words.
- `record.emit(label, "batch.answer", [key], frm=[f"session/{sid}/{rid}"], Key=key, Batch=str(n), Chars=len(words))`.
- `row_card_close` for `f"{label}-planner"` on this host, with the words for Pending You and `Answered in <caller>'s pane` recorded (decision 4). That needs a `said=` argument through `row_card_close` to `card_closed`, used in `close_call` in place of the outcome.
- `tell_planner` when the caller is the operator.
- Print `batch <n> answered in <caller>'s pane`, then the words when the caller is the planner, then what became of the card.

Tested by `tests/py/test_batch_answer.py` with a stand-in `CardActs`, as `test_card_commands.py` does: the entry's fields, no words in any entry, the card closed with the words, the tell sent only for the operator, and nothing emitted on a refusal.

**3.3** `batch_wait`: each round, before reading the card, check `pane_answered(acts.entries(label))` for its key. When it is there, print the line from decision 4, `row_card_close` the card with that outcome, print `acts.end(label, key)`'s words, and return. Case in `tests/py/test_batch_answer.py` with a stand-in `acts` whose entries gain the answer on the second round.

**4.1** `planner.md` *Batches* and `operator.md`: the words of decision 6. `tests/t-briefs.sh` checks for each brief's new sentence with `has`, as its other checks do. `plan.py`'s usage docstring, `plugin/bin/crew`'s usage header, README's batches paragraph and SKILL.md's command table name `crew card answer batch/<n> --excerpt "<words>"`, as `docs.2` asks.

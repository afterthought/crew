## Context

See proposal.md, *Why*. A Pending You card is reachable only under the sign-in of the host it was posted from (ADR 0005 as amended 2026-10-11; `a-card-lost-to-its-owner-is-posted-again`, archived 2026-10-14). That change handled a card its owner's own host lost by signing in again. It did not handle a card left on a host the main level no longer runs on, which is what stranded batches 13, 14 and 15 on mac-studio once swancloud's main level moved to deneb (signal 2026-10-22-swancloud-planner-3b6cb27a/01).

Rules this change rests on: `briefs.12` (a bolt is offered for landing only once every unit's latest change has been in a batch the user answered, on its card or by its reading session's send; a card Pending You lost is no answer, and its row waits for its card posted again), `briefs.13` (one card per thing, under its key; a batch's card closed by a tap or by its session's send), `read.1` (crew does not guess what it can't read), `read.5` (the run record is read from the branch), `state.4` (the rail's views write nothing; its sweep is the act), `code.7` (a decision is a function of facts), `code.8` (what the agents' views draw). It touches the areas of `plan.md` (`plan.py`), `tests.md` (`tests/`) and `docs.md` (README, the skill, `openspec/`), and `teams.md` for `plugin/bin/crew`'s usage header only. It edits nothing under `docs/` (`docs.7`), and moves nothing `board.agent_views` or `status.js` draw: a batch read with no card is closed by the same `batch_closed` every view already reads (`code.8`).

What crew does today, read on main at 2558214:

- **The rail's sweep skips a card held on another host.** `sweep_judged` skips every card whose `host` isn't this host. It raises a row's card only when no card under the row's key is open on any host (`out["none"]`). A batch card posted from mac-studio and never closed stays open in the run record forever, so on deneb the row is neither swept nor raised.
- **A card lost on the posting host is raised without saying so.** When the card was recorded lost there (`card.close` with `State: lost`), deneb's sweep puts the row in `none`. `raise_batch` then goes through `row_card_change`, which finds no card held on deneb (`cards.card_under` over `cards.host_entries`, this host's entries alone), so `card_posted` posts it plainly, with no word that an older copy is dead.
- **The wait drops a session's send when no card is held.** In `batch_wait`, when `batch_waited` returns `("read", …)` and `card` is None (none held on this host, or found lost during the wait), the code skips `row_card_close`, ends the session and returns, recording nothing. The batch stays unanswered, and `awaiting_answer` keeps holding its bolts' landings. When a card is held but its close comes back lost or refused, `row_card_close` returns None and nothing records the batch read either.
- **`batch_closed` reads only card acts.** It reads a batch's key as closed only on a `card.close` with a `Card`. crew's `batch.close`, which the sweep records for a batch that waits on nothing, is read only by the sweep's own "done once" check.

## Goals / Non-Goals

**Goals:**
- A batch whose card the main level's host can't reach gets one live card on that host, saying the older copy is dead.
- A batch whose reading session the user sends is answered whether or not a card of it is held there.

**Non-Goals:**
- Reaching, asking after or closing the older copy. No agent can reach it from another sign-in, and the user dismisses it in the app.
- Recording a batch answered by the user's words in a main-level pane, which is the sibling unit `a-batch-answered-in-a-main-level-pane-is-recorded-by-crew`.
- Proposal cards or other rows' cards left on another host. The intent and the signal name batches. Proposal cards are also the planner's, so they can be stranded the same way; that is named for the planner in the change's report.

## Decisions

### One decision says which copy the main level's host can't reach

A new function in `cards.py`, `stranded(entries, key, owner, here)`, beside `card_under`, is a pure function over the run record's entries in the order they were written. It returns the id of the owner's newest card under the key when this host can't reach it, and None otherwise. That id goes into the new card's report line. It returns:

- the card id, when the owner's last act under the key is a `card.post` (done, naming a card) whose `Host` is not `here` and that no later `card.close` closes;
- the card id, when the owner's last act under the key is a `card.close` of that card with `State: lost`, on any host;
- None for anything else: a card posted on this host (the existing lost-card path asks Pending You about it), a card closed any other way (the row's own state decides), or no card at all.

A refused post or close changes nothing, as in `card_under`. The function reads only facts, so the logic tier proves it (`code.7`).

### The rail's sweep on the main level's host raises the batch's card again

`sweep_judged` gets a new bucket, `again`: [(row, older card id)]. A batch row (`batch/<n>` in record 0031's form) goes there when its owner's host, `owners[key][1]` (the partition's main machine, `row_owner`), is this host, and `stranded` over the whole record read (`read["logs"]`, the branch and every host that answered) names a card. Such a row is not also put in `none`. The card held elsewhere is still skipped by the per-card loop, since `c["host"] != here`, so nothing asks Pending You about it from here.

`sweep_cards` raises each `again` row through `raise_batch`, handed `dict(row, dead=<older card>)`. A card posted reports as `did="lost"` on the older card with `new` set to the new card, and words that name where the older copy was: "held on <host>, which this host's sign-in does not reach: posted again as <new>", or for one recorded lost, "lost to <owner>: posted again as <new>". `swept_cards` then drops the older card and adds the new one, as it does for the existing lost path. A raise that posts nothing, because `batch_facts` finds the batch's point passed, is reported `left` with "its batch no longer waits to be read", and a refused raise is said the way `raised` already says it.

The sweep reads the whole record, not this host's entries, because the copy is by definition on another host. That record is the branch plus each host that answered (`record.gather`). A partition whose record did not answer whole is already left unswept by `sweep_cards` (`read.1`), so `stranded` never judges a part.

Raising again also covers a batch card that was simply posted before the main level moved and was never answered. That is the case in the signal, and it is why the rule reads "on another host" and not "lost".

Considered: recording the older copy as lost before posting again. That would say crew read something it did not: no Pending You call can reach the card from here. The rail's existing rule, that a newer card by the same owner under the same key replaces the older (`record_reading`), already takes the new card as the row's.

### The raise posts with the dead-copy summary when handed an older copy

`raise_batch` reads `row.get("dead")`. When it is set, the builder it hands `row_card_change` is `cards.batch_card` wrapped by `cards.posted_again`. That wrapper prepends `cards.DEAD`, "An older copy of this card was lost: dismiss it in the app.", the same words the lost-card path already posts. `card_built` calls the builder again with the session's link, so the wrapper carries through. Nothing else in `raise_batch` changes: `batch_facts` still decides whether the batch's point has come, and `row_card_change` still posts, since no card is held on this host.

### A session sent records the batch read when no card was closed

In `batch_wait`, once `batch_waited` gives `("read", words, outcome)`:

- with a card held, `row_card_close` closes it as now; when it returns a card id, the card's close is the record;
- when no card was held, or `row_card_close` returns None (lost, refused or none), crew records `batch.close` on `batch/<n>` in the planner's name, with `Key: batch/<n>`, `State: read`, `Outcome: <outcome>`, and why `batch(<n>): read in its session`. It then ends the session as now.

The choice between the two is a small decision function, `batch_read_close(closed_card)`, which returns whether crew records the batch's own close. Its test reads as the spec's scenarios. The wait's loop stays thin around it (`code.7`).

`batch.close` is reused rather than a new act. It is already crew's close of a batch in the planner's name, keyed by the card key, with an `Outcome`, and the rail and the README already name it. `State: read` tells it apart from the sweep's close of a batch that waits on nothing, which carries no `State`.

### `batch_closed` reads crew's close of a batch

`batch_closed` counts a `batch.close` that was not refused as closing its `Key`, card or none, and a later `card.post` under the key opens it again, as now. A close as lost still leaves the key open. Counting the sweep's `batch.close` of a settled batch changes nothing visible: such a batch is already closed through `batch_settled` in `record_reading`, `batch_facts` and `sweep_judged`. `awaiting_answer` only reads batches holding a unit's latest change, which a landed or dropped unit's settled batch no longer matters to. The sweep's "done once" set in `sweep_judged` already unions the two, and stays as it is.

A card still open under a key closed this way (the refused-close case, or the stranded copy) is a card whose row is gone. On its own host the sweep withdraws it with `row_gone`'s words. A stranded copy on another host is listed among the open cards with no row, naming its host, as any stray card is today.

## Risks / Trade-offs

- [The user answered the stranded copy and is asked again] → batches 13, 14 and 15 were answered on mac-studio's cards, and the new cards ask the user once more. That is the cost of a card crew can't read. The sibling pane-answer unit records those three when it lands first, and then no card is raised again.
- [The older copy stays listed as an open card with no row once its batch closes, naming a host the main level left] → it ages out of the rail after `CARD_DAYS` (14 days), as any stray card does. Closing it needs that host's sign-in. Named for the design agent in the report.
- [A host's sign-in that lost a card it posted, and whose main level never moved] → unchanged: the existing lost path posts it again on that host.

## After deploy

Nothing. crew is live on a host once its main is pulled, and every behaviour here is proved in the logic tier and in `tests/t-cards.sh` on the stub Pending You. Whether batches 13 to 15 get new cards on deneb depends on what the pane-answer unit recorded first, which is the planner's to read on the rail, not a step of this change.

## Task notes

### 1.1

`stranded(entries, key, owner, here)` in `cards.py`, after `card_under`, with a docstring in the style of its neighbours, implementing *One decision says which copy*. Read `Host` from the entry, which `record.emit` writes on every entry. Cases in `tests/py/test_cards.py` (a new class beside the lost-card cases): posted on another host and open → its id; posted here → None; posted elsewhere then closed (any state but lost) → None; closed as lost, here or elsewhere → its id; lost then a newer post here → None; a refused post or close changes nothing; another owner's card under the key → None. Run `tests/suite logic`.

### 2.1

In `sweep_judged`, add `again` to `out` and to the docstring's return. For each row in `rows` whose key is `batch/<n>` (`re.fullmatch(r"batch/\d+", key)`) and whose `owners.get(key)` host is `here`, compute `cards.stranded(entries, key, owner, here)`. When it names a card, append `(row, card)` to `again` and leave the row out of `none`. Mind the order: `none` is computed after the card loop, so filter it against the keys put in `again`. `refused_lately(entries, now, key=...)` applies to `again` as to `none`. In `sweep_cards`, drop an `again` row whose kind has no raise as `none` does, include `again` in the `any(j.values())` check, and act on `again` after `held`, using `raised(l, dict(row, dead=card), owner)` and reporting as *The rail's sweep on the main level's host* says. The older card's host for the words is the `Host` of its post, which `stranded`'s caller reads from the entries: return it from a small helper or read it inline. Keep `stranded` returning the id alone. Update `sweep_cards`' docstring.

### 2.2

In `raise_batch`, when `row.get("dead")`, hand `row_card_change` a builder that is `lambda f: cards.posted_again(cards.batch_card(f))`. Say so in its docstring.

### 2.3

In `tests/py/test_rail.py`, `TestSweepJudged`: a batch row whose card (from `card(...)` with `host="mac-studio"`) was posted on mac-studio, read with `here` the box and `owners` naming the box, is in `again` with that card and not in `none`. The same read on mac-studio puts nothing in `again`. A batch whose card was recorded lost on mac-studio (a `did(...)` close with `State="lost"`) and has no newer post is in `again`. A proposal row in the same position is not in `again`. A row in `again` whose last post was refused lately is left. In `TestSweep`: the `Acts` stand-in's raise for a batch, handed `dead`, posts; the sweep's `done` reports `lost` on the older card with `new`, and words naming mac-studio; `swept_cards` drops the older card and adds the new. In `tests/py/test_cards.py`, beside `test_the_sweeps_raise_of_a_batch_whose_card_is_lost_posts_it_again…`: `raise_batch` handed `dead` with no card held on this host posts one card whose summary starts with `cards.DEAD`, records no `card.close`, and handed no `dead` posts the plain summary. Run `tests/suite logic`.

### 3.1

`batch_read_close(closed)` in `plan.py` beside `batch_waited`: True when `closed` (what `row_card_close` returned, or None when no card was held) is None. In `batch_wait`, on `done[0] == "read"`: when a card is held, call `row_card_close` and keep its return. When `batch_read_close` says so, emit `batch.close` as *A session sent records the batch read* says, print `batch/<n>: recorded read, <outcome>`, and when no card was closed end the session with `acts.end` and print what it says, as the `closed` branch does. Then return. Update `batch_wait`'s docstring: a session sent with no card held, or one lost or not closed, records the batch read.

### 3.2

`batch_closed` in `plan.py` counts a `batch.close` with a `Key` starting `batch/`, not refused, as a close of that key, with no `Card` needed. Keep a `card.post` (with a `Card`) opening the key and a lost `card.close` leaving it open. Update the docstring. In `tests/py/test_batches.py` `TestAnswered`: a unit's latest change in batch 7 with a `batch.close` `State: read` under `batch/7` waits on nothing; a later `card.post` under `batch/7` opens it again; a refused `batch.close` closes nothing. In `tests/py/test_cards.py`, `batch_read_close`'s cases. In `tests/py/test_rail.py` `TestRecord`, a batch closed by crew's read has no row. Run `tests/suite logic`.

### 3.3

In `tests/t-cards.sh`, after the case "a session whose link only the host could open…": batch 4 recorded with `batch 4`, its session started with `planner session batch/4` and no card raised, then decided with `decide` as approved. `planner wait batch/4` prints `batch/4: approved` and the recorded-read line, and `entries batch.close` holds `batch/4 read Read; no notes` in `wldn-planner`'s name. The existing `expect_fail "no card and no session of batch/4…"` line moves to a batch number with neither (batch 5). Then a case where the card is held but its close is refused (the stub's refusal for `ack_answer`/`cancel_request`, as other cases in the file make one) records `batch.close` too. Run `tests/suite t-cards`.

### 4.1

README, in the rail's sweep sentence (*Pending You* section): a batch's card posted from a host other than the main level's, or recorded lost to the planner there, is posted again on the main level's host at its next rail read, its summary saying the older copy is dead. In the `crew card wait batch/<n>` sentence: a session sent records the batch read, crew's own close in the planner's name, when no card of it is closed on the main level's host. In the batches paragraph: a batch read so counts as answered for a bolt's landing. The crew skill's `crew rail` and `crew card wait` rows, and `plugin/bin/crew`'s usage header for `crew rail` and `crew card wait`, say the same in a clause each (`docs.2`). Run `tests/suite t-docs`, then `tests/suite --affected` once, at the end.

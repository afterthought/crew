# Design

## Context

See proposal.md for why. Today a batch's rail row lasts until the run record holds a `card.close` under its key (`plan.py` `batch_closed`, read by `record_reading` into the batches' `closed` keys, which `rail_rows` skips). The rail's sweep (`sweep_cards`, judged by `sweep_judged`) posts a card through the kind's raise (`raise_batch`) for every row with none open, and closes a card whose row is gone with the words `row_gone` gives, for a batch always "its batch no longer waits to be read". A batch answered in the pane, or before crew raised cards (record 0031), has no close, so it stays a row and gets a card however long ago its work landed.

The rule is already written: `briefs.12`'s details rule out "a card posted for a batch every unit of which has landed, or whose units' latest changes a later batch holds, which waits on nothing, its row ended by the event that ended it", and name this unit as the fix. The design agent ruled on 2026-10-20, writing this unit's sources, that a batch closes when nothing of it waits, each unit landed, dropped, or its latest change in a later batch: a dropped unit's change waits on nothing. Record 0031 §1 has crew close its cards at the event that ends them; `briefs.11` has no agent close a row's card, so the planner cannot withdraw these.

Rules this design rests on: `briefs.11`, `briefs.12`, `state.4` (a view writes nothing), `code.7` (a decision is a function of facts), `read.1` (what can't be read closes nothing), `code.8` (the agents' views), `docs.2`, `docs.6`. Pages whose area the change touches: `briefs.md` (the planner's brief), `docs.md` (README); `plan.py`'s own page is `plan.md`, none of whose rules this changes.

## Goals / Non-Goals

**Goals:**
- A batch that waits on nothing is no row, on the rail and the board, from the facts alone.
- crew records its close once, saying why, and withdraws any card open under it with the same words.
- No card is ever posted for such a batch.

**Non-Goals:**
- A bolt dropped with `--requeue`: its units go back to the queue, still in the plan, and are not dropped, so their batch stays a row until answered or held by a later batch.
- Telling the planner before crew posts a card, which the signal's quote asks: not in this unit's intent.
- The landing gate: crew's close is not the user's answer, and `awaiting_answer` is unchanged.

## Decisions

### 1. What "waits on nothing" means, unit by unit

A unit of batch n no longer waits on it when any of these holds:
- it has landed: a `bolt.land` entry, not refused, names `unit/<u>` among its objects (the landing writes every unit of the bolt there, `plan.py` `bolt_land`'s `w.on`);
- it was dropped after batch n was made: a `unit.drop` entry, or a `bolt.drop` entry, not refused, names `unit/<u>` among its objects and is later than batch n's `review.batch` entry. `crew unit drop` writes `unit.drop` on `unit/<u>` (`op_unit_drop`), a proposal's approval writes the same entry for each drop it applies (`plan_approve`'s `record.emit` of each op), and `crew bolt drop` without `--requeue` names every unit it removes on its `bolt.drop` (`op_bolt_drop`'s `w.on`); or
- a later batch holds it: some `review.batch` m > n, not refused, lists `u` at any commit.

A batch, or for an old batch an old `batch/<n>-<k>` card's five units (`batch_cards`, `card_part`), waits on nothing when every unit it holds is one of those. Any other unit, one that has not landed, was not dropped since and that no later batch holds, keeps the batch a row as today.

"After batch n was made" because a unit's name can come back: a unit that never merged has no change on main, so `plan.7` lets a unit be added again under a dropped one's name, and a drop from before batch n was made says nothing of the change batch n holds. A drop is read by entry order, `At` then `Id`, as the run record is read everywhere else. A requeued bolt's units are not dropped (Non-Goals).

"Any commit" rather than "the unit's latest change": a batch holds only a change no batch held before (`due_changes`), so when a later batch is made it holds the unit's latest change, which is the sources' words. Read against the latest change at every read instead, batch 5 would come back as a row the moment its unit was constructed a third time, its newest change in no batch yet, though batch 5 then holds the unit two changes back. With "a later batch holds it" the close never undoes itself: landings, drops and batches are only ever added, and a unit added again after its drop does not undo the drop of the change batch n held. Alternative considered: reading crew's own close entry back as what keeps a batch closed. Rejected, because then the board, which writes nothing (`state.4`), would show a batch the rail had already closed.

### 2. The decision is one function of the entries

`batch_settled(entries)` (the name is the coder's to keep or change) returns `{key: words}` for each batch card key, `batch/<n>` or an old `batch/<n>-<k>` (from `batch_cards(n, units, batch_posts(entries))`), that waits on nothing, whether or not any card of it closed. It starts no process (`code.7`) and is tested in the logic tier.

Its words say why, with the units in the batch's order:
- `its batch waits on nothing: x1 and x2 have landed` (`x1 has landed` for one, `cards.joined` for the list);
- `its batch waits on nothing: batch 7 holds a newer change of x1` (the newest later batch holding each unit; one clause per such batch, oldest first);
- `its batch waits on nothing: x2 was dropped` (`x2 and x3 were dropped` for more);
- any of these, in the order landed, dropped, held later, joined by `; `.

Each unit is counted once, the first of landed, dropped, held later that is true of it: a unit both landed and held later is counted as landed, and one dropped after a later batch held it, or held by a later batch after it was added again, is counted as dropped.

### 3. Where the decision is read

- `record_reading` adds the settled keys to the batches' `closed` and keeps the words as `held["settled"]`. `rail_rows` already skips a closed key, so the row is gone on every read, the board's included (`state.4`), and `sweep_judgment` already counts a closed key with no card open as dead, so a reading session crew started for it ends with the next sweep.
- `batch_closed` keeps meaning what the user's answer closed. `awaiting_answer` reads only it, so crew's close is never the user's answer (`briefs.12`). No settled batch holds a unit's latest change that the landing waits on: a landed unit's bolt is no longer in the plan, a dropped unit is in no bolt, and a unit a later batch holds has a newer latest change than the one this batch held.
- `row_gone` gives a `batch/…` key the settled words when the entries settle it, else its words as now. So the sweep's existing path withdraws an open card with the same words as the close (cancel with the words as the reason; `card_closed` picks the act from the card's state).
- `batch_facts` returns None for a settled key, as it does for a closed one, so `crew review --wait` raises no card for a batch that already waits on nothing.

### 4. crew's close is its own entry, `batch.close`

The sweep records each settled key once as `batch.close` on `batch/<n>`, `by` the partition's planner (the row's owner, `row_owner`), with `Key` the card key and `Outcome` the words, and `why` "batch: closed by crew, it waits on nothing". It is not a `card.close`: no card may exist, the rail's card reading and `batch_closed` key off `Card`, and a `card.close` under a batch's key counts as the user's answer.

It is written:
- only by the sweep on the partition's main-level host, where the batches and their cards are recorded and where the planner's cards are posted, as `sweep_judged` posts only where the owner runs;
- only when the read's entries hold no `batch.close` under that key, not refused, so a second read records nothing;
- only when the partition's record answered whole there (`sweep_cards` already leaves such a partition unswept and says so, `read.1`);
- before the sweep opens its Pending You bridge, so a host not signed in still records the close, the card's withdrawal waiting for a read that can reach Pending You.

A refused or failed `record.emit` is said, as `emit` says it, and the next read tries again.

The sweep's result gains one `done` item per close, `did` "closed", `card` None, `new` None, with the words; one card withdrawn under such a key is its own `done` item, as today. `rail_text` prints a close with no card as `batch/3 (wldn), wldn-planner, no card: closed: <words>` rather than naming a card `None`.

### 5. The documents

README's rail paragraph says the batches group holds the batches that still wait on the user, and its batches paragraph and run-record acts gain crew's close (`batch.close`), its units landed, dropped or held by a later batch; the planner's brief says crew closes a batch's card when the user sends it back or when the batch waits on nothing, each of its units landed, dropped or held by a later batch (`docs.2`). Nothing under `docs/architecture/` or `docs/adr/` changes (`docs.7`).

### 6. The agents' views

The board's batch rows and the agents' bands are drawn from the same rows, in the same shape; a settled batch is simply not among them (`code.8`'s "not ruled out: a change that moves nothing the views draw").

## Risks / Trade-offs

- [A unit landed more than 60 days after its batch falls outside `BATCH_DAYS`] → the batch itself falls out of the window first, since a batch is always older than the landing of its units; nothing to do.
- [A host's uncarried entries are missing from the read] → the decision only ever closes on entries it holds, so a missing landing keeps a batch a row, never the other way (`read.1`), and the sweep records nothing for such a partition.
- [wldn's 23 open cards] → they are crew's, posted on the box in the planner's name; the first rail read there after landing withdraws each one whose batch waits on nothing, with its words. A batch among them holding a unit that has neither landed nor been batched again stays a row and keeps its card, as the user asked.

## Task notes

**1.1** Put `batch_settled` beside `batch_closed`. Landed units from `bolt.land` entries' `unit/<u>` objects, not refused; later batches from `batches(entries)`. For each n and each `(key, part)` of `batch_cards(n, units, batch_posts(entries))`, settled when every unit of `part` is landed or in some batch m > n. Words as Decision 2. Cases in `tests/py/test_batches.py`: every unit landed; held again later; both; one unit still waiting (not settled); a refused landing or refused batch counts for nothing; the unit constructed a third time stays settled; an old `batch/<n>-<k>` card settled on its own five.

**1.2** `record_reading`: `closed |= set(settled)`, `held["settled"] = settled`. `row_gone`: for kind `batch`, `(None, batch_settled(entries)[key])` when the key is settled. `batch_facts`: None when `key` is settled. Leave `batch_closed` and `awaiting_answer` alone and add a case in `tests/py/test_batches.py` that `awaiting_answer` is unchanged by a settled batch (spec scenario "crew's close is not the user's answer"). Cases in `tests/py/test_rail.py` that `rail_rows` has no row for a settled batch, `batch/<n>` and `batch/<n>-<k>`, and does for one unit still waiting; `row_gone`'s parametrized table gains the settled words.

**1.3** `sweep_judged` gains `settled`: `[(key, words)]` for each settled key with no `batch.close` under it, not refused, in `entries`, whose owner (`owners`, as for `none`) runs here. Since `rows` no longer hold settled keys, take them from `batch_settled(entries)` and owner as `row_owner` gives a batch's, the planner on the partition's main machine; pass it in rather than reading the fleet inside (`code.7`). `sweep_cards` writes them with `acts.emit` (Decision 4) before its bridge, and adds the `done` items; a partition with only closes to write still has them written when it has nothing for the bridge. Cases in `tests/py/test_rail.py` on the stand-in acts: a settled batch with no card records one `batch.close` and posts nothing; one whose card is open there records the close and withdraws the card with the same words; a second read records nothing; the sweep on a host other than the main machine records nothing; a host with no Pending You sign-in (the stand-in's bridge refusing) still records the close; a partition whose record did not answer whole records nothing.

**1.4** `rail_text`'s sweep line for a `done` item with neither `card` nor `new`, per Decision 4; a case in `tests/py/test_rail.py`.

**1.5** In `batch_settled`, a unit of batch n is dropped when a `unit.drop` or `bolt.drop` entry, not refused, names `unit/<u>` among its `On` and comes after batch n's `review.batch` entry in the entries' order (Decision 1); `batches(entries)` gives each batch's number and `At` but not its place in the list, so take the entry's index or compare `(At, Id)`, whichever the coder finds reads plainer. The words gain the dropped clause and the order landed, dropped, held later, each unit counted once (Decision 2); update the docstring. `row_gone` and the sweep need nothing new: they read `batch_settled`. Cases in `tests/py/test_batches.py`: a unit dropped by `crew unit drop` after the batch settles it, "x1 was dropped"; one dropped by a bolt drop without requeue; a refused drop counts for nothing; a drop before the batch was made counts for nothing (the name added again and batched); one unit landed, one dropped and one held later, the three clauses in order; a unit dropped after a later batch held it counted as dropped; a batch with one unit dropped and another still waiting is not settled. A case in `tests/py/test_rail.py` that the sweep withdraws an open card under a batch whose last unit was dropped, with the dropped words.

**2.1** README: the rail paragraph (the batches group's words), the batches paragraph (crew's close of a batch that waits on nothing, each unit landed, dropped or held by a later batch) and the run record's `Act` list (`batch.close`). `plugin/roles/planner.md` line on the rail's proposal and batch rows: the card closes when the user sends it back or when the batch waits on nothing, each of its units landed, dropped or held by a later batch, crew saying why. Where either already names "landed or held by a later batch", add "dropped" there. Run `tests/suite briefs docs` if either checks those words.

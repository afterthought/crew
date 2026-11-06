# A kit's landings card changes in place, and is not raised again for a forecast that flips

## Why

On the Willdan box (wldn, chuck-herdr-alpha), crew withdrew switchboard-kit's landings card, `land/switchboard-kit`, and posted it again six times between 03:11Z and 04:10Z on 2026-11-06 (Pending You requests req_0fa38f08, req_7c72f476, req_94993350, req_38682903, req_28e96a3b and req_12486acd). Each time the card flipped between `a-deploy-row-follows-its-stack-to-the-end` alone and that bolt plus `identity-and-access-reads-as-the-locked-mockups`, and each new post interrupted the user (signal `afterthought/crew-state:swancloud/main signals/2026-11-06-swancloud-operator-1e1b6c68/01-crew-churns-a-kits-landings-card`). Record 0031 §3 says one card per thing, changed in place, and Pending You's guide says a card whose content changed is updated with a change note, never withdrawn and posted again.

wldn's run record on the box shows what moved each time:

| At | The card | What moved |
|---|---|---|
| 03:11:18Z | posted, `a-deploy-row` alone | identity-and-access's take-main fix `take-main-620becd` was in flight, so its row was held with no box |
| 03:15:15Z | closed "changed in kind", a list of two posted | `take-main-620becd` merged at 03:14:33Z: identity-and-access read proven at `2a7944c` |
| 03:17:51Z | closed "changed in kind", `a-deploy-row` alone posted | `take-main-8a51c2b` started at 03:17:27Z |
| 03:21:20Z | closed "changed in kind", a list of two posted | `take-main-8a51c2b` merged at 03:20:37Z: proven at `d36f207` |
| 04:02:08Z | closed "changed in kind", `a-deploy-row` alone posted | main moved to `88ecba1` (sluice formed on `3a8ca60` at 03:59:52Z), and the raise's own forecast at 04:02:04Z found `d36f207` in conflict with it on `docs/spec/console-and-navigation.md` |
| 04:10:08Z | closed "changed in kind", a list of two posted | `take-main-88ecba1` merged at 04:09:26Z: proven at `1b76e67` |

Two things made it churn.

1. **Why the card was withdrawn rather than changed.** A landings card's form is read from how many rows can land (`cards.landings_form`): one row is a hold-to-approve, and two to five rows are one list. Pending You's `update_request` takes no `kind`, and a list must hold at least two options (`post_request` and `update_request`, pendingyou 0.39.0, read on 2026-11-06). So a card going from one row to two, or from two to one, cannot change in place. `landings_step` returns its change with `kind_changed`, and `row_card_change` closes the card, "changed in kind: a new card follows it", and posts a new one.
2. **Why the row came and went.** The forecast did not flip with nothing moved. Each come and go matches a move in the record: a take-main fix starting, which holds the row with no box (`landing_rows`, rail-cards "A take-main fix holds its row as taking main first"); the same fix merging, which brings the row back proven at a new head; or main landing work the bolt conflicts with. crew read the forecast the same way on every pass. The record shows no forecast read differently from one pass to the next. sluice's forecasts and the raise's own `git merge-tree` agree at every head and revision of main they share: at `2a7944c` against `8a51c2b`, sluice met only the queued #1367 at 03:18:41Z, and the raise found no conflict with main at 03:15:21Z. So no sluice clause is at fault. One take-main fix was not needed: `take-main-8a51c2b`, started at 03:17:27Z on the wait's forecast of 03:12:32Z, was of `c45166f`, a head the bolt had left at 03:14:33Z. That is the stale relay that #442 (`v0.41.1`, landed 01:06Z the same day) fixed.

What turned a bolt taking main in into a new card was the row leaving the card while it took main in. A bolt taking main in keeps its own work and the user's approval (record 0031 as amended 2026-10-24), so its row should stay where it is.

## What Changes

- **A row taking main first stays on the card.** While any row of a kit's landings card can land, each bolt held only to take main first beside it is a row of the card: a box left unticked, with a detail saying why it takes main first and a consequence saying that, ticked, it lands once its team has taken main in and sluice has proven it, the user's send standing through it. It is never ticked or proposed while it conflicts (`plan.8`). With no row that can land there is no card, as before. A row taking main first that an earlier send still lands stays held with no box.
- **Its coming and going changes the card in place.** The card's form is read from all the rows it shows, so a bolt coming to take main first or coming back from it keeps the form and changes the one card with a change note: "z takes main first: …", "z's head is now def5678; z can land again". The card follows only when its form must change, as when a second bolt joins a card of one.
- **The run record marks such a row.** The card's `Heads` mark a row taking main first `:main`, beside `:left`, so the next raise knows what the card showed. An unticked row the card showed taking main first is no bolt the user left: it gets no `landing.left`, no "Left:" line, and its conductor is still told its take-main fix.
- **A tick on it stands.** A bolt the user ticked while its row took main first keeps their send, as a bolt ticked and then taking main in does. `crew card read land/<kit>` now leaves out a ticked bolt with a conflict recorded at the head the card showed only while the bolt still stands there or has a conflict recorded at its head now. The bolt's head now is read where it lives, so a bolt whose take-main fix has moved it lands on the send. Before, such a bolt was left out of every read while the card stayed open.
- README and the crew skill say this (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a row taking main first stays on its kit's landings card as an unticked box beside rows that can land, so a bolt taking main in and coming back changes the card in place; the card's form counts it; a tick on it stands through the take-main fix.

## Impact

- `plugin/lib/plan.py`: the new decision `card_rows`; `landings_step`, `left_now`, `rows_unsent`, `card_heads` and the new `heads_taking`, `kit_card_state` and `landings_raised`; `main_firsts` reads each bolt's head now.
- `plugin/lib/cards.py`: `landings_card` builds a row taking main first, and the new `taking_said` and `row_said`; `landings_form`'s count.
- `README.md`, `plugin/skills/crew/SKILL.md`.
- Tests: `tests/py/test_landings.py`, `tests/py/test_cards.py`, `tests/py/test_card_commands.py`.
- The run record keeps no new field: `:main` is a mark inside `Heads` as `:left` is. Nothing the board or the mod draws changes (`code.8` not reached), and nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/lib/cards.py
README.md
plugin/skills/crew/SKILL.md
tests/py/test_landings.py
tests/py/test_cards.py
tests/py/test_card_commands.py
```

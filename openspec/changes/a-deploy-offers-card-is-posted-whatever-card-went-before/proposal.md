# Proposal

## Why

From 23:54Z on 2026-10-19 to 00:16Z on 2026-10-20, Pending You refused every deploy card crew raised for swancloud's offers of `ddcf2cb` (deneb, mac-studio, macbook-pro, chuck-herdr-alpha, swancloud-srv), each with "This is swc-2-conductor's card; leave it. You're "swancloud-ops": act only on the cards you posted". The cause is in crew: a deploy card follows the landing card of the bolt whose landing left main at the deployed head. That card was swc-2-conductor's, for `the-box-works-in-wldn-prod`. Pending You takes `follows` only to a card of the asker's own. The user had no deploy card for an hour, and asked on recovery's card: "i don't have a card for this. it's taking for fucking ever" (signal `2026-10-20-swancloud-planner-c422e742/01`).

swancloud-srv's own offer of `f358fdf` at 00:16 went through, because no landing left main there and its card followed nothing. The rail did name each refusal, but the board and the agents' views showed the rows only as "no card open". An offer of the same commit again did nothing, so only the rail's sweep, ten minutes later, tried each card again, and each of those followed the same landing card and was refused again.

## What Changes

- A card crew posts follows only a card posted in its own owner's name. A deploy's card follows its environment's last deploy card when the user declined that card, and otherwise follows nothing. It never follows a landing card. The landings a deploy carries are already named on the card's face, with each bolt the run record holds a landing of.
- A deploy card's post that Pending You refuses is recorded as refused with Pending You's words. crew already does this; a case taken from the run record of 2026-10-19 23:54Z to 2026-10-20 00:16Z now pins it.
- A row whose last card post was refused, with no card open, is shown as owing its card wherever the row's marker is drawn: the board's text, every agent's view above its prompt (main-level ops's deploy rows among them) and the page. The page also carries the refusal's words. `crew rail` already prints them on the row's card line.
- `crew ops offer` of the commit already offered, with the same files, posts the deploy's card again when main-level ops holds no card open under `deploy/<env>`. It still changes nothing while a card is open, and it writes no second offer to the run record.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a card follows only its owner's own card, and a deploy's card follows only its environment's declined deploy card.
- `main-level`: an offer of the commit already offered posts the deploy's card again when none is open.
- `crew-board`: a rail row's marker says when the row owes its card because its post was refused, in the board's text and the agents' views.
- `board-page`: the page's marker says the same, with the refusal's words.

## Impact

`plugin/lib/cards.py` (`follows_of`, `posted_cards`), `plugin/lib/ops.py` (`offer`, `raise_deploy`, `raise_step`), `plugin/lib/plan.py` (the landing card's two `follows_of` calls), `plugin/lib/board.py` (`marker` and what it is handed, `card_of`), `plugin/lib/page.html` (the marker's words), README's *Operations* and board paragraphs and the `crew ops offer` usage in `ops.py`'s header (`docs.2`), and their cases in `tests/py/`. The mod, `plugin/hooks/status.js`, draws the views' lines as it is handed them, so its code does not change.

## Touches

```
plugin/lib/cards.py
plugin/lib/ops.py
plugin/lib/plan.py
plugin/lib/board.py
plugin/lib/page.html
README.md
tests/py/**
```

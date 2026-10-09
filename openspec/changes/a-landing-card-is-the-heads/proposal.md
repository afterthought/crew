# Proposal

## Why

When a bolt's landing fails and the team proves it again on a new head, the user gets no new landing card. The rail keys a landing card `land/<bolt>`, the same key as the card already answered, and Pending You returns that resolved card instead of posting a new one, so the conductor ends up asking in its pane, which nobody watches (signal `2026-10-09-crw-1-conductor-7097d44f/01-a-landing-card-key-cannot-be-asked-twice`). A key is one question, and a bolt proven again on a new head is a new question: the landing row's key carries the bolt's head, as a review's carries its unit's (ADR 0005 as amended 2026-10-09, "A landing's key is the bolt's head's"; `briefs.11` as amended on main).

## What Changes

- **A landing card's key names the bolt's head.** The rail's landing row is keyed `land/<bolt>/<head>`, the first seven characters of the bolt's branch head, the way a review row is keyed `review/<unit>/<head>`. A bolt proven again after a fix moved its head has a new key, so its landing card is a new card, and the user is asked again.
- **The old landing card is closed by its owner with the outcome.** When the bolt's head moves under a landing card (a fix merged into the bolt, or a fix that carried the bolt onto main), the conductor closes the card under the old key with what happened, and posts the new one once the bolt is proven again. A card left open under an old head belongs to no row, so `crew rail` lists it with the tell that asks its owner to close it, as it already does for a review card of an old head.
- **crew's card hook and `crew card session` know the new form.** The hook records a card posted under `land/<bolt>/<head>` as the landing row's card, on `bolt/<bolt>`; a card under the bare `land/<bolt>` is no longer a row's key. `crew card session` still refuses every landing key, which has nothing to read.
- **The card discipline says it.** The conductor's brief keys its landing card `land/<bolt>/<head>`, and the card discipline the planner's and conductor's briefs share says that a row whose key changes is a new question: close the old card with the outcome and post one under the new key.
- **The rail-cards spec says so**, by a delta to its card-key requirement, archived after `the-rail-is-answered-through-cards`; and the card-sessions spec's refusal names the landing key's new form, archived after `a-card-links-a-plannotator-session`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: each rail row's card key, and what its owner does when the key changes. A landing row's key is `land/<bolt>/<head>`, a bolt proven again on a new head has a new landing card, and the card under a row's old key is closed by its owner with the outcome. (`rail-cards` is written by `the-rail-is-answered-through-cards`, built and not yet archived; this delta is archived after it.)
- `card-sessions`: the landing key `crew card session` refuses is `land/<bolt>/<head>`. (`card-sessions` is written by `a-card-links-a-plannotator-session`, built and not yet archived; this delta is archived after it.)

## Impact

- `plugin/lib/gather.py`: each bolt's answer carries its head's commit beside the head's time.
- `plugin/lib/plan.py`: `rail_rows()` keys the landing row with the head; `CARD_KEYS` and `card_of()`'s message name the new form.
- `plugin/hooks/cards`: the landing key's pattern.
- `plugin/lib/crew.py`: `cards_how()`, a row whose key changes.
- `plugin/roles/conductor.md`: the landing card's key, and the old card closed when a fix moves the bolt's head.
- `README.md`: the rail's card keys.
- Tests: `tests/t-rail.sh`, `tests/t-cards.sh`, `tests/t-card-session.sh`, `tests/t-briefs.sh`.

## Touches

`plugin/lib/gather.py` (a bolt's head), `plugin/lib/plan.py` (`rail_rows()`, `CARD_KEYS`, `card_of()`), `plugin/hooks/cards` (shared with any unit that refuses a card by its key, such as `a-teams-cards-are-its-conductors`), `plugin/lib/crew.py` (`cards_how()`, shared with every unit that changes the card discipline), `plugin/roles/conductor.md` (*Cards* and *Fixes*), `README.md`, `tests/t-rail.sh`, `tests/t-cards.sh`, `tests/t-card-session.sh`, `tests/t-briefs.sh`, `openspec/specs/rail-cards/spec.md` (by delta) and `openspec/specs/card-sessions/spec.md` (by delta).

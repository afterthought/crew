# Proposal

## Why

On 2026-10-09 a bolt team's landing card showed the user the command to land the bolt by hand, with a Done button. The user's reaction: "The whole point is telling the agent to land the build." The partition's operator agent then posted a second card for the same landing, because Pending You's reminder tells every session to put what it needs from the user on a card. The conductor's brief already said the landing card is a high-stakes approval, so by `roles.3` crew now refuses a row's card in any other form. The operator agent's brief says plainly that it posts no card. (Signal `2026-10-09-swancloud-operator-mac-studio-47cdc78c/01-land-card-is-a-manual-step-and-doubled`; ADR 0005 as amended 2026-10-09; `briefs.13`.)

## What Changes

- **Each row's card has one form, the row's.** A proposal's card is an approval. A unit's review card is a review: it looks good, or it needs changes, with the user's note. A verify report's card is a choice among the conductor's options. A bolt's landing card is a high-stakes approval: yes has the conductor tell main-level ops to land, and it is held to send in the Pending You app. No row's card is a step for the user to do, and no landing card carries the landing's own command.
- **crew refuses a row's card in another form, before Pending You sees it.** When a crew agent posts a card under a row's key, crew's card hook checks the card's form against the row's. A card of the wrong kind, a landing card that isn't high stakes, an approval with options, or a step for the user on any row but the landing never reaches Pending You. The refusal names the form to use. The same check runs when such a card is changed in place, so a landing card cannot lose its high stakes later.
- **The briefs name each form in Pending You's own terms.** The conductor's and the planner's card rules say which kind of card each row is, and the card discipline both briefs share says that crew refuses another form.
- **The operator agent posts no card.** A team's wait that has a card is already before the user, so the operator agent sends nothing for it: no card, no notification. A wait with no card, such as a question asked in a pane or a row whose card is not open, is shown as a herdr notification, as now. Pending You's reminder to put things on a card does not apply to the operator agent.
- **The rules read as built.** The open-items page no longer lists `briefs.13`, its detail names the check, and README says crew refuses a row's card in another form.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the form each row's card takes, and crew's refusal of a row's card in another form.
- `operator-agent`: the operator agent posts no card, sends nothing for a wait that has one, and shows a wait with none as a notification.

## Impact

- `plugin/hooks/cards` and `plugin/hooks/hooks.json`: a check before Pending You's `post_request` and `update_request` that refuses a row's card in another form, beside the record the hook already writes after each card act.
- `plugin/lib/crew.py`: the card discipline (`cards_how()`) says crew refuses a row's card in another form.
- `plugin/roles/conductor.md`, `plugin/roles/planner.md`: each row's card form, in Pending You's terms.
- `plugin/roles/operator.md`: no card, and a notification only for a wait with no card.
- `docs/architecture/briefs.md`, `docs/architecture/_open.md`, `README.md`.
- Tests: `tests/t-cards.sh`, `tests/t-briefs.sh`.
- Another bolt, `a-teams-cards-are-its-conductors`, has already built a check of its own in the same hook, run before the same tool: crew refuses a card under any key but one of the agent's own rows. Whichever of the two bolts lands second puts both checks in one place (design.md, decision 2).

## Touches

`plugin/hooks/cards`, `plugin/hooks/hooks.json` (shared: the hook map), `plugin/lib/crew.py` (`cards_how()`), `plugin/roles/conductor.md` (*Cards*), `plugin/roles/planner.md` (*Cards*), `plugin/roles/operator.md` (*When an agent waits on the user*), `docs/architecture/briefs.md` (`briefs.13`'s detail), `docs/architecture/_open.md`, `README.md` (the cards paragraph), `tests/t-cards.sh`, `tests/t-briefs.sh`, `tests/moon.yml` (shared: only when a test's reads change), `openspec/specs/rail-cards/spec.md` and `openspec/specs/operator-agent/spec.md` (by delta).

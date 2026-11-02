# Proposal

## Why

A bolt the user chose not to land yet is rebuilt every time main moves. builds-reach-the-phone (swc-3) has waited since 2026-10-23, unticked on its kit's landings card, and each move of main forecast it in conflict and started a take-main fix for it, `fix/builds-reach-the-phone/take-main-0306be7` among them: a slot's work and a sluice run on a loaded host each time, for a bolt nothing lands until the user ticks it. Each fix also moved its head, so the bolt came back as a fresh row and was asked for again. The user, 2026-10-24, through the operator: "I've noticed that we've been rebuilding the bolt with the about:phone even though it's parked. We keep rebuilding it probably because the main branch is changing" (signal 2026-10-24-swancloud-design-f4cdfd2a/01). Record 0036 as amended 2026-10-24 and accepted 2026-10-26, and `teams.21`, say what must be true instead.

## What Changes

- **A bolt the user left** is one they cleared on their send of its kit's landings card, or one whose landing they stopped in their own words in main-level ops's pane. It stays left until they tick it on a later send or land it in their words, or until its head moves.
- **A left bolt is still forecast** against main on every move of main and on every conductor's wait, as any bolt is. Its row on the card keeps its box and says whether it lands clean or would take main first, and on which files; a waiting card is changed in place when that becomes true.
- **No take-main fix starts for a left bolt.** crew tells its conductor no fix while it is left, a conductor's wait says the forecast once and says to take nothing in, and the rail's landing row says it would take main first once ticked and leaves it out of the tell that lands. So its head moves by no hand of crew's, and it stays left on each card that follows.
- **When the user ticks it**, crew acts on the send at once: a conflict with what main has landed holds its row as taking main first, its conductor is told the take-main fix then, the command ops reads off the send leaves it out, and the user's send stands for it through the fix, as for any ticked bolt taking main in.
- **The user's stop in ops's pane is recorded.** Ops records it with `crew bolt leave <bolt> --excerpt "<the user's words>"`, which crew checks against ops's own transcript as the user's words before recording anything, as it checks a landing said in the pane. The bolt is then shown on the card as one the user left.
- A bolt not yet asked or ticked takes main in at once, as it does today.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: a row the user left keeps its box and says whether it would take main first, with no fix started; ticking it starts the fix and holds the row taking main first; a bolt stopped in ops's pane is shown as left; reading the send acts on it at once.
- `bolt-teams`: a conductor's wait, and the card's own forecast, tell no take-main fix for a bolt the user left, and say the fix once the user ticks it.
- `crew-rail`: a left bolt forecast to conflict with main says it would take main first once ticked, and is left out of the tell that lands.
- `main-level`: ops records a landing the user stopped in its pane, checked as the user's words.

## Impact

- `plugin/lib/plan.py`: the landings card's raise (`raise_landings`, `landing_rows`, `main_told`, `landings_step`'s note), the conductor's wait (`reach`, `bolt_said`, `bolt_forecast`), the rail (`rail_rows`), `crew card read` of a landings card (`card_read`, `landing_lines`), a new `crew bolt leave`, and new decisions for which bolts are left and which forecasts a tell has already said.
- `plugin/lib/cards.py`: a left row's forecast words.
- `plugin/bin/crew`: the command's usage.
- The conductor's and main-level ops's briefs, README and the crew skill (`docs.2`).
- Tests in the logic tier and end to end (`tests/t-journey-land.sh`).

## Touches

```
plugin/lib/plan.py
plugin/lib/cards.py
plugin/bin/crew
plugin/roles/conductor.md
plugin/roles/main-ops.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_landings.py
tests/py/test_forecast.py
tests/py/test_rail.py
tests/py/test_cards.py
tests/py/test_card_commands.py
tests/py/test_pane_landing.py
tests/py/test_parser.py
tests/t-journey-land.sh
tests/moon.yml
```

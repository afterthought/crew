# Proposal

## Why

On 2026-10-20 crw-2's landing card for `every-deploy-offer-reaches-the-user` went up with no reading session, though crew already starts one with every landing card. Its conductor's `crew card wait` said no session had been started, and `crew card session` opened one by hand minutes later without trouble. Why the raise's session did not open was printed only on the raising command's error output, which nothing keeps, so nobody can tell. The run record shows a post and a change and nothing else. (Signal 2026-10-20-swancloud-planner-1fab5a67/01; record 0031 §3 as amended 2026-10-19; `briefs.9`, `briefs.13`.)

`briefs.9` gives every landing card one reading session on the bolt's changes against main, with its link in the card's words. Its details say what this unit holds to: a session that could not open at a raise is recorded with the card's post, its reason goes on the card and in the run record (`read.1`), and the raise tries what `crew card session` does, reading the bolt after the host has fetched.

## What Changes

- When a landing card's reading will not open at a raise, crew tries once more the way `crew card session` does, before giving up. It fetches the kit's main on the team's host, reads the bolt's landing afresh and opens the reading again. Only when that also fails is the card raised without a reading. This covers every point that raises or changes the card: a merge's end, a fix's end, the rail's sweep, a preview's end and `crew card session`.
- A landing card raised without its reading says so, says why, and names `crew card session land/<bolt>` as how the bolt's conductor starts it. The card then changes to carry the link. The command is written as the conductor's act, not as a step for the user (`briefs.13`).
- The run record keeps why. A card's post or change whose reading could not open records crew's own message about it on that entry, in a new field, `Unread`. The raising command's output names `crew card session` too.
- `crew card wait land/<bolt>` no longer stops because no session was started. If the conductor holds the landing card open and no reading runs (the raise could not open it, or a decision the wait gave was forgotten), the wait starts the reading as `crew card session` does. That changes the card to carry the link, and the wait then waits on it. If the reading still will not open, the wait is refused, saying why and naming `crew card session land/<bolt>`. If no landing card is held, it is refused as before.
- The conductor's brief, the crew skill, the command's usage (`plugin/bin/crew` and `plan.py`'s) and README say all of this, together (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `card-sessions`: the requirement that a card whose session could not start is raised all the same now covers the landing's retry, its words naming `crew card session` and the reason kept in the run record. A wait on a landing card starts its reading when none runs.

## Impact

- `plugin/lib/plan.py`: `raise_land` and the landing's reading at a raise, `card_built` and `unopened`, the card's post and change entries (`card_posted`, `row_card_change`), and `card_wait` for a `land/` key.
- `plugin/lib/record.py`: the run record's descriptor and `EXTRA` gain `Unread`.
- `plugin/roles/conductor.md`, `plugin/skills/crew/SKILL.md`, README's card-session paragraph, and the usage text in `plan.py`.
- Tests: `tests/py/test_cards.py`, `tests/py/test_landing.py`, `tests/t-journey-land.sh`, the stub plannotator (a way to refuse its next starts), and `tests/t-briefs.sh` if the brief's checked words move.
- No change to the card's approval, its face, who lands it (`plan.16`), or the batch's and the long proposal's sessions.

## Touches

```
plugin/bin/crew
plugin/lib/plan.py
plugin/lib/record.py
plugin/roles/conductor.md
plugin/skills/crew/SKILL.md
README.md
tests/py/test_cards.py
tests/py/test_landing.py
tests/t-journey-land.sh
tests/t-briefs.sh
tests/stubs/plannotator
tests/moon.yml
```

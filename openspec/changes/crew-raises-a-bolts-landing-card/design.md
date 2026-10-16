# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give the landing card its form and the act that sends it; this change raises, changes, withdraws and closes it at the bolt's own events. It relies on `plan.16` as record 0031 amends it (a bolt lands on the user's approval of the landing card crew raises in its conductor's name), record 0025 (the bolt's proof is sluice's verdict at its head), `tests.5`, `teams.3` (a fix on the bolt), `briefs.11`, `briefs.13`, `code.7`, `code.9`, `read.1` and `state.4`. It touches the areas of `plan.md` and `teams.md`.

## Goals / Non-Goals

Goals: one landing card per bolt, raised by crew once the bolt reads proven, whichever read finds it first; changed when its head moves, withdrawn on a defect and raised again after the fix; closed at the landing.

Non-goals: the landing's form, which `crew-builds-every-card-from-its-facts` builds; the rail's read posting a card that has none, which `the-rail-shows-and-sweeps-every-card` does through this change's raise; the conductor's brief, which `only-crew-raises-a-rows-card` rewrites; a card's link to a running environment for the bolt (record 0031 §9).

## Decisions

### 1. When a bolt reads proven

The landing's point needs one rule: a bolt reads proven when every unit and chore has merged, every unit's latest change has been in a batch, and the bolt's head carries a green `Sluice-Result` (record 0025). The merge's end and the rail read both read it (`plan.py`'s landing row already does); whichever runs first posts, the other finds the card by its key in the run record and does nothing.

| Event | Command | Act |
|---|---|---|
| a bolt reads proven | the merge's end (`crew unit wait`, `crew chore wait`) and `crew rail` | post `land/<bolt>` |
| the head moves while open | the merge's end | change ("head is now …") |
| landed | `crew bolt land` | close with the landing's outcome |
| a defect noted | `crew fix` started on the bolt | withdraw ("held for a fix: …") |

`raise_land`, the landing's raise, reads `landing_facts`, the bolt, its units and chores, sluice's verdict and when, how far main has moved, the batches each unit was read in, and sluice's pull request when the submission at the head has one, and calls the act; it finds the landing's point not come until the bolt reads proven. A landing raised again after a fix follows the card the defect note held, as `follows_of` reads it. The landing's row and card key is the bolt's, `land/<bolt>`, not the head's: `rail_rows`, `CARD_KEYS`, the conductor's branch of `card_refusal` and the card hook's `KEYS` line give it.

### 2. The landing's close waits on who keeps which folders

What `crew bolt land` closes the card with, the landing's outcome, says what the landing did: the merge, and what became of the hosts' folders. Which folders crew keeps level after a landing, and who keeps them, is the record of who keeps which folders, the recovery session's next design talk. This change is built once that record is accepted, and the close's words are the ones it settles.

### 3. Not in this change

Not in this change, for the design agent's queue beside record 0031 §9: the approval on the card as the act that takes the pull request out of draft so it enters sluice's queue ("pending you should be the thing that flips another check in GitHub or switches the pull request from a draft to approved so that it enters the actual Sluice queue"), and a link to the bolt's preview environment once sluice's previews exist ("Sluice can manage preview environments … being able to have a link for that").

## Risks / Trade-offs

- Until `only-crew-raises-a-rows-card` rewrites the conductor's brief, it still tells the conductor to post the landing card itself, marked high stakes, which Pending You refuses on an approval; crew's card is the one the user sees.

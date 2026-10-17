# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give the landing card its form and the act that sends it; this change raises, changes, withdraws and closes it at the bolt's own events. It relies on `plan.16` as record 0031 amends it (a bolt lands on the user's approval of the landing card crew raises in its conductor's name), record 0025 (the bolt's proof is sluice's verdict at its head), `tests.5`, `teams.3` (a fix on the bolt), `briefs.11`, `briefs.13`, `code.7`, `code.9`, `read.1` and `state.4`. It touches the areas of `plan.md`, `teams.md`, `briefs.md` and `tests.md`.

## Goals / Non-Goals

Goals: one landing card per bolt, raised by crew once the bolt reads proven, whichever read finds it first; changed when its head moves, withdrawn on a defect and raised again after the fix; closed at the landing.

Non-goals: the landing's form, which `crew-builds-every-card-from-its-facts` builds; the rail's read posting a card that has none, which `the-rail-shows-and-sweeps-every-card` does through this change's raise; a card's link to a running environment for the bolt (record 0031 §9).

## Decisions

### 1. When a bolt reads proven

The landing's point needs one rule: a bolt reads proven when every unit and chore has merged, every unit's latest change has been in a batch, the bolt's head carries a green `Sluice-Result` (record 0025), and no fix is in flight on it, since a fix started on the bolt holds its landing until the fix merges or is dropped, and the bolt would otherwise read proven again at once at the head the fix held. A fix is in flight while its place stands and it has neither merged into the bolt nor been dropped (`fixes_in_flight`, a dropped fix read by its `branch.<fix>.crew dropped` mark, `gather.kit`). The landing's row stands as before, from the moment every unit has merged, keyed `land/<bolt>`, and says what the bolt waits on: its verification, a unit's change for a batch, or "lands once <fix> has merged or been dropped"; its card is raised only once the bolt reads proven, so the sweep's raise for a row whose point has not come posts nothing. The merge's end and the rail read both read it; whichever runs first posts, the other finds the card by its key in the run record and does nothing.

| Event | Command | Act |
|---|---|---|
| a bolt reads proven | the merge's end (`crew unit wait`, `crew chore wait`, `crew fix --wait`) and `crew rail` | post `land/<bolt>` |
| the head moves while open | the merge's end | change ("head is now …") |
| landed | `crew bolt land` | close with the landing's outcome |
| a defect noted | `crew fix` started on the bolt | withdraw ("held for a fix: …") |

`raise_land`, the landing's raise, runs on the team's host, where its conductor's cards are, and reads `landing_unready` from the kit first, then `landing_facts` from the partition's run record: the bolt, its units and chores, sluice's verdict and when, how far main has moved since the bolt last met it, the batches each unit was read in, and sluice's pull request when the submission at the head went through one (its `Sluice-From` trailer); it calls the act, which posts when no card is held and changes the held one in place, and does nothing, saying nothing, until the bolt reads proven. `landing_act` is which act each event takes, as facts. A fix's start withdraws each landing card the conductor holds, `landing_held`. A landing raised again after a fix follows the card the defect note held, as `follows_of` reads it. The landing's row and card key is the bolt's, `land/<bolt>`, not the head's: `rail_rows`, `CARD_KEYS`, the conductor's branch of `card_refusal` and the card hook's `KEYS` line give it.

### 2. The landing's close is record 0032's

`crew bolt land` closes the card on its team's host, where its conductor holds it, with "landed on GitHub's main at `<sha>` (#<n>); every host's folder follows by swancloud's timer within minutes", the number sluice's submission's when main's head carries one: record 0032 settles the words, and `no-worktree-holds-main-or-a-bolt-branch` 4.2 builds the close. The write that ends the bolt no longer tells its conductor to close a card.

### 3. Not in this change

Not in this change, for the design agent's queue beside record 0031 §9: the approval on the card as the act that takes the pull request out of draft so it enters sluice's queue ("pending you should be the thing that flips another check in GitHub or switches the pull request from a draft to approved so that it enters the actual Sluice queue"), and a link to the bolt's preview environment once sluice's previews exist ("Sluice can manage preview environments … being able to have a link for that").

### 4. The conductor's brief

`conductor.md`'s *Cards* says crew raises the landing card once the bolt reads proven; that the conductor adopts it with the line its merge's end prints, or that `crew tell` brings it when a rail read raised it; and what it does on the answer: the tell to main-level ops on a yes, a fix on a defect note, which withdraws the card. *The building loop* and *Talking to the user* say the same. It posts and closes no landing card. `tests/t-briefs.sh` pins the words (`tests.6`, `plan.16`).

## After deploy

1. Each team's conductor restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.

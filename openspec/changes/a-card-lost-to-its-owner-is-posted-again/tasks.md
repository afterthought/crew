# Tasks

## 1. Every brief that cards a row says what to do with a lost card

- [x] 1.1 The card discipline in the planner's and the conductors' briefs, and main-level ops's *Deploying main*, say when a card is lost, when to check, and to post it again under the row's key with the fixed sentence naming the older copy dead, from one paragraph in `crew.py` (design: *The words are crew's, said once*; Task notes 1.1; `briefs.11`, `briefs.13`).
- [ ] 1.2 `tests/t-briefs.sh` checks the lost card's words in the shared discipline and in main-level ops's brief, and `tests/suite t-briefs` ends with "0 failed" (Task notes 1.2).

## 2. The rail shows the live card

- [x] 2.1 `crew rail` names the open card's id on a row's card line, and takes a newer card posted under a key by the same owner as the row's, the older as lost (design: *The rail names the open card's id*, *A newer post under a key, by the same owner, replaces the older*; Task notes 2.1; `read.1`, `state.4`).
- [ ] 2.2 `tests/t-rail.sh` proves the id on the card line, a re-posted card replacing the older on the row and among the cards with no row, and another owner's card not replacing it, and `tests/suite t-rail t-board t-card-sweep` ends with "0 failed" (Task notes 2.2).

## 3. The docs say so

- [ ] 3.1 README and the crew skill say the rail's card line names the open card's id, and what happens to a lost card, and `tests/suite --affected` ends with "0 failed" (Task notes 3.1; `docs.2`).

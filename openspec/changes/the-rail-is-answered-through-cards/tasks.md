# Tasks

## 1. crew records its agents' cards

- [x] 1.1 The run record takes a card's id and row key, in day files begun before and after the change (design.md, Task notes 1.1).
- [x] 1.2 A crew agent's post, update, withdrawal or close of a Pending You card is a run-record entry naming its row, its card and its key, holding no text from the card, and the hook never fails a tool call (design.md, Task notes 1.2).
- [x] 1.3 `tests/t-cards.sh` holds each act, both result shapes, an unkeyed card, the cases that write nothing, and a resumed session (design.md, Task notes 1.3). Verify `devenv shell -- tests/run t-cards t-session-hook t-record` ends with "0 failed".

## 2. The rail shows each row's card

- [x] 2.1 Each rail row prints its card key and whether a card is open for it and whose, and the rail lists open cards with no row, each with a `crew tell` to its owner, read in one run-record read per partition (design.md, Task notes 2.1).
- [x] 2.2 `tests/t-rail.sh` holds every row's key, a card opened and closed, a stray card, an unreachable host's cards, and the rail writing nothing (design.md, Task notes 2.2). Verify `devenv shell -- tests/run t-rail` ends with "0 failed".

## 3. crew names the card a change ends

- [x] 3.1 Approving, dropping, replacing or agreeing to a proposal, an amendment, and every plan write that takes a unit or bolt from a team name the row's card to its owner, printed when the owner made the change and told otherwise (design.md, Task notes 3.1). Verify `devenv shell -- tests/run t-proposals t-amend` ends with "0 failed".
- [x] 3.2 `crew unit run` names the review or verify card its stage ends (design.md, Task notes 3.2).
- [x] 3.3 `crew unit approve` by anyone but the conductor tells the conductor to close its review card (design.md, Task notes 3.3). Verify `devenv shell -- tests/run t-unit t-unit-run t-merge` ends with "0 failed".

## 4. The briefs and the docs

- [x] 4.1 The planner's and the conductor's briefs share one card discipline, filled from the teams file (design.md, Task notes 4.1).
- [x] 4.2 The planner's brief has it post, act on and close a card for each proposal it opens (design.md, Task notes 4.2).
- [x] 4.3 The conductor's brief has it post, act on and close the review, verify and landing cards, and tell the operator agents only of waits with no card (design.md, Task notes 4.3).
- [ ] 4.4 Main-level ops takes the word to land through the conductor's landing card (design.md, Task notes 4.4). Verify `devenv shell -- tests/run t-briefs t-roles` ends with "0 failed".
- [ ] 4.5 The README and the crew skill describe the cards on the rail (design.md, Task notes 4.5). Verify `devenv shell -- tests/run` ends with "0 failed".

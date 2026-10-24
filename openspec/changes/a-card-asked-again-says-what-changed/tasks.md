## 1. The answer is kept

- [x] 1.1 crew says what the user answered on a card in its own words, from names alone, and the run record's entries may carry it as `Answer` (design, Decision 1; Task notes 1.1); passes `tests/py/test_cards.py`.
- [x] 1.2 Every close of a card the user answered records its `Answer`, a close as answered in a pane recording the pane, and a waiting card's withdrawal records none (design, Decisions 1 and 6; Task notes 1.2); passes `tests/py/test_card_commands.py`.

## 2. A follow-on says what was answered, or is not posted

- [x] 2.1 crew finds the answered card a post comes after and makes the opening that says when it was answered, with what, and what changed since, or none when nothing changed (design, Decisions 2, 3 and 5; Task notes 2.1); passes `tests/py/test_cards.py`.
- [x] 2.2 Every post that follows a card the user answered opens with that paragraph and follows that card, and one with nothing changed is recorded `stands` and not posted (design, Decisions 3 and 5; Task notes 2.2); passes `tests/py/test_card_commands.py`.
- [x] 2.3 The rail's sweep raises no card for a row whose follow-on was withheld (design, Decision 5; Task notes 2.3); Verify `tests/suite logic` ends with "0 failed".

## 3. Each raise says what changed

- [x] 3.1 A record revised and a proposal rewritten after the user's answer say what changed, a rewrite with the same commands and case withheld (design, Decision 4; Task notes 3.1); passes `tests/py/test_proposal_card.py` and `tests/py/test_proposal_life.py`.
- [x] 3.2 A deploy offered again after a decline and a step after its deploy or the step before say what changed, an offer at the declined head with the same files withheld (design, Decision 4; Task notes 3.2); passes `tests/py/test_ops.py`.
- [x] 3.3 A kit's landings card that follows the user's send says what the send landed, held and left and what moved since, a left bolt still shown (design, Decision 4; Task notes 3.3); passes `tests/py/test_landings.py`.

## 4. The affected tests

- [ ] 4.1 The tests this change affects pass (design, Task notes 4.1); Verify `tests/suite --affected` ends with "0 failed".

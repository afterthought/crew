# Tasks

## 1. The raise opens the landing's reading, twice if it must

- [x] 1.1 What follows a first refusal of the landing's reading is a function of facts: try again with the fresh landing, raise nothing because the bolt no longer reads proven, or stand on the first reason. Its cases pass in `tests/py/test_landing.py` (design, Decision 1; Task notes 1.1).
- [x] 1.2 `raise_land` opens the reading itself before it builds the card. On a refusal it fetches the kit's main on the team's host, reads the landing afresh and opens the reading once more, handing the card its link or its reason (design, Decision 1; Task notes 1.2).
- [ ] 1.3 `card_built` starts nothing when the facts already carry the reading's link or its reason. A landing card without its reading names `crew card session land/<bolt>` as the conductor's act, in its words and in the command's output, with the cases in `tests/py/test_cards.py` updated and added (design, Decision 2; Task notes 1.3).
- [ ] 1.4 Through `ReadingActs`, a raise whose first start fails and second opens posts the link, one whose both fail posts a card naming `crew card session`, and one whose fresh read is not proven posts nothing. The cases pass in the logic tier (Task notes 1.4).

## 2. The run record keeps why

- [ ] 2.1 A landing card's `card.post` and `card.update` entries hold `Unread` with crew's message when its reading could not open, and none when it opened. The field is in the run record's descriptor, and its cases pass in `tests/py/test_cards.py` (design, Decision 3; Task notes 2.1).

## 3. The conductor's wait starts a missing reading

- [ ] 3.1 `crew card wait land/<bolt>` with no session and the conductor's card open starts the reading as `crew card session` does and waits on it. A start that refuses is refused naming why and `crew card session land/<bolt>`, and no card held is refused as before, with the decision's cases in `tests/py/test_cards.py` (design, Decision 4; Task notes 3.1).

## 4. Briefs and docs

- [ ] 4.1 `conductor.md`'s landing paragraph says the wait starts a missing reading, and what a card or a wait that could not open it says and which command starts it. `tests/suite t-briefs` passes (design, Decision 5; Task notes 4.1).
- [ ] 4.2 The crew skill's wait row, the usage in `plugin/bin/crew` and `plan.py`, and README's card-session paragraph say the same together. `tests/suite t-docs` passes (Task notes 4.2).

## 5. End to end

- [ ] 5.1 The stub plannotator can refuse its next starts. `tests/t-journey-land.sh` proves the second try's link on the card, a card raised without its reading naming `crew card session` with `Unread` in the box's run record, and the conductor's wait starting the reading and changing the card. `tests/suite t-journey-land` passes, and `tests/moon.yml` is regenerated if the test's reads changed (Task notes 5.1).

## 6. Checks

- [ ] 6.1 `tests/suite logic`, `tests/suite t-journey-land t-briefs t-docs t-cards t-journey-review`, then `tests/suite --affected` once, all report 0 failed (Task notes 6.1).

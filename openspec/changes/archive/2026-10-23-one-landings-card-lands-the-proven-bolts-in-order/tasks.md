## 1. What a landings card holds, as decisions

- [x] 1.1 A `land/<x>` key is read as a kit's landings card when `x` is a kit a team of the partition builds and as a bolt's otherwise, its run-record object `kit/<kit>` or `bolt/<bolt>`, and a bolt named as a kit of its partition is refused at the plan write that adds it (design, Decision 1; Task notes 1.1); passes `tests/py/test_landings.py`.
- [x] 1.2 The card's rows are the kit's proven bolts in the plan's order, a bolt with a fix in flight or a landing sluice refused at its present head held with no box (design, Decisions 7 and 9; Task notes 1.2); passes `tests/py/test_landings.py`.
- [x] 1.3 Each row carries the conflicts forecast against main and each row above it, by `git merge-tree` on the kit's building host after a fetch, a forecast crew cannot make said and holding nothing (design, Decision 5; Task notes 1.3); passes `tests/py/test_landings.py`.

## 2. The card's form and its life

- [x] 2.1 crew builds `land/<kit>` as an approve of risk high for one row, one ticked list with `highStakes` for two to five, lists of five for more, held rows on the face, each row carrying its bolt's facts, forecast, reading, preview and pull request (design, Decision 3; Task notes 2.1); passes `tests/py/test_cards.py`.
- [x] 2.2 A landings card follows only the kit's last one in ops's name, answered and closed with rows left (design, Decision 8; Task notes 2.2); passes `tests/py/test_cards.py`.
- [x] 2.3 One decision says whether the kit's card is posted, changed, followed, left, withdrawn or closed with what landed, held and was left, a send ticking none closing it (design, Decision 8; Task notes 2.3); passes `tests/py/test_landings.py`.

## 3. Raising the card on the main host from each row's host

- [x] 3.1 A row's reading and preview are opened, kept or ended on its team's host by `crew _land-row`, and every event that changed a bolt's card hands the kit card's raise to the partition's main machine with `crew _land-card` (design, Decision 2; Task notes 3.1); passes `tests/py/test_landings.py` and `tests/py/test_card_commands.py`.
- [x] 3.2 `raise_landings` on the main machine posts, changes, follows or closes `land/<kit>` in `<label>-ops`'s name, naming a host that does not answer and raising the rest (design, Decisions 2 and 8; Task notes 3.2); passes `tests/py/test_landings.py`, and `tests/suite t-journey-land` ends with "0 failed".
- [x] 3.3 The merge's end, a fix's start, a preview's end, `crew card session land/<bolt>`, `crew card wait land/<bolt>` and `crew bolt land` keep a bolt's reading and preview as its row's and change the kit's card, a session or wait on a bolt that is no row refused (design, Decisions 2 and 4; Task notes 3.3); passes `tests/py/test_card_commands.py`, and `tests/suite t-cards` ends with "0 failed".

## 4. Landing the ticked bolts in order

- [x] 4.1 `crew bolt submit <bolt>...` submits one kit's bolts in order, each queued behind the one before on its host or after it ended on another, closes each with `crew bolt land` as it lands, records a refused one at its head and goes on, exiting non-zero naming each that did not land (design, Decision 6; Task notes 4.1); passes `tests/py/test_landing.py`, and `tests/suite t-journey-land` ends with "0 failed".
- [x] 4.2 `crew card read land/<kit>` prints the ticked bolts in the card's order and the `crew bolt submit` that lands them (design, Decision 8; Task notes 4.2); passes `tests/py/test_card_commands.py`.

## 5. The rail, the board and the agents' views

- [x] 5.1 The rail has one landing row per kit, owned by `<label>-ops` on the partition's machine, naming each bolt in order with what it waits on and the tell that lands those that can, and its sweep withdraws an old `land/<bolt>` card as a row of its kit's card (design, Decision 9; Task notes 5.1); passes `tests/py/test_rail.py`.
- [x] 5.2 The board and the agents' bands mark each bolt from its kit's landing row and draw the card above ops's prompt (design, Decision 9; Task notes 5.2; `code.8`); passes `tests/py/test_board.py`, and `tests/suite mod` ends with "0 failed".

## 6. The briefs and the docs

- [x] 6.1 Main-level ops's brief takes the kit's landings card and its send as the word and lands the ticked bolts with one `crew bolt submit` in the card's order, saying nothing of one bolt at a time; the conductor's brief raises and passes no landing card and tells ops its bolt is proven; the planner's brief, crew's card words, the skill, README and the command's usage say the same (design, Decision 10; Task notes 6.1); `tests/suite t-briefs t-docs` ends with "0 failed".

## 7. Integration

- [x] 7.1 Run `tests/moon-tasks` and commit `tests/moon.yml` for the tests added or changed, then `tests/suite --affected` ends with "0 failed".

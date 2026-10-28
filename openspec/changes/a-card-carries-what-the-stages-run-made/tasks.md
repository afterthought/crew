# Tasks

## 1. What a stage made reaches its batch's card

- [ ] 1.1 A made line is read as written, a durable thing by its address, a running thing by its branch and revision, and a line crew can't read carried as its text (design, Decision 2; Task notes 1.1): passes `tests/py/test_made.py`, `tests/suite logic` ends with "0 failed".
- [ ] 1.2 The conductor's wait reads `made.jsonl` in the place's git directory at each look and at the stage's end and keeps each new line once, as written, under the stage first seen, on the team's host (design, Decisions 1 and 3; Task notes 1.2): passes `tests/py/test_made.py`, `tests/suite logic` ends with "0 failed".
- [ ] 1.3 A batch's card carries each unit's made lines under its paragraph, read from the copies on each unit's team's host, a silent host named and nothing refused, and the copies go when the bolt lands or is dropped (design, Decision 4; Task notes 1.3): passes `tests/py/test_cards.py` and `tests/py/test_made.py`, `tests/suite logic` ends with "0 failed".
- [ ] 1.4 A line kept for a unit in a batch whose card waits on the user changes that card in place, and one kept after the user answered leaves it as it is (design, Decision 4; Task notes 1.4): passes `tests/py/test_made.py`, `tests/suite logic` ends with "0 failed".

## 2. A preview comes up on the user's ask and goes on their done

- [ ] 2.1 A landings row carries the bolt branch and head where the kit's policy names a preview and "no preview" where it names none, and its post asks sluice for nothing (design, Decision 5; Task notes 2.1): passes `tests/py/test_landing.py`, `tests/py/test_landings.py` and `tests/py/test_cards.py`, `tests/suite logic` ends with "0 failed".
- [ ] 2.2 `crew card preview <key> <thing> [--done]`, run by the card's owner, brings a row's or a line's thing up through sluice on the team's host, lists its addresses on the card while it is up, releases it on `--done`, and refuses another caller or a thing the card does not carry (design, Decision 6; Task notes 2.2): passes `tests/py/test_card_commands.py`, `tests/suite logic` ends with "0 failed".
- [ ] 2.3 A preview is released when a moved head leaves it at the old head, with nothing asked at the new one, when its card closes or its row goes, by the rail sweep for any card key, and only once no other record of crew's names its revision; a preview an older crew asked at a row's post is released at the first row read (design, Decision 7 and Migration Plan; Task notes 2.3): passes `tests/py/test_rail.py` and `tests/py/test_card_commands.py`, `tests/suite logic` ends with "0 failed".
- [ ] 2.4 The land journey posts a row with no preview asked, brings it up on ops's `crew card preview`, releases it on `--done`, and releases one brought up again at the landing (design, Decisions 5 to 7; Task notes 2.4): Verify `tests/suite t-journey-land` ends with "0 failed".

## 3. A landed revision's card

- [ ] 3.1 A deploy's card and a landing's close name the commit landed and carry no preview (design, Decision 9; Task notes 3.1): passes `tests/py/test_cards.py` and `tests/py/test_landing.py`, `tests/suite logic` ends with "0 failed".

## 4. Briefs and usage

- [ ] 4.1 Main-level ops's and the planner's briefs say to reply in the thread and run `crew card preview` when the user writes on their card asking for a preview or saying they are done, and the conductor's says the landing row's preview comes up only on the user's ask (design, Decision 8; Task notes 4.1): Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 4.2 `crew card preview` is named in `plugin/bin/crew`'s usage, README and the crew skill together (design, Decision 6; Task notes 4.2): Verify `tests/suite t-docs` ends with "0 failed".

## 5. Integration

- [ ] 5.1 `tests/moon-tasks` leaves `tests/moon.yml` in step with the tests, and the tests the change affects pass: Verify `tests/suite --affected` ends with "0 failed".

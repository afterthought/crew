# Tasks

## 1. A landing's later try is recorded and reaches its card

- [x] 1.1 `crew card session land/<bolt>` records each try of the reading as `card.reading` in the conductor's name, done or refused, records nothing for a link given again or a refusal before the try, changes a waiting card that stands without its reading even when its session runs, and takes a `say` the rail can silence (design, Decisions 1–3; Task notes 1.1).
- [x] 1.2 The landing session's cases pass in `tests/py/test_cards.py`'s `TestLandingSession` (Task notes 1.2).

## 2. The rail's read tries a landing card's reading

- [x] 2.1 The sweep's reading try sends a `land/` key through the landing's session start, silenced, and every other key as before (design, Decision 4; Task notes 2.1).
- [x] 2.2 The sweep's judgment holds a landing card standing without its reading ten minutes or more among the cards to try. Its case passes in `tests/py/test_rail.py`'s `TestSweepJudged` (design, Decision 5; Task notes 2.2).
- [x] 2.3 A waiting landing card is tried and listed opened, one whose try refuses is listed left with why, and an answered one is not tried. The cases pass in `tests/py/test_rail.py`'s `TestSweep` (Task notes 2.3).

## 3. The landing card's words

- [x] 3.1 A landing card raised without its reading says crew tries it again when the rail is read, beside the conductor's command. Its case passes in `tests/py/test_cards.py` (design, Decision 6; Task notes 3.1).

## 4. Briefs and docs

- [x] 4.1 The conductor's brief says the rail's read tries a landing card's missing reading too. `tests/suite t-briefs` passes (design, Decision 7; Task notes 4.1).
- [x] 4.2 README, the crew skill, and the usage in `plugin/bin/crew` and `plan.py` say the same together. `tests/suite t-docs` passes (Task notes 4.2).

## 5. Checks

- [x] 5.1 `tests/suite logic`, `tests/suite t-briefs t-docs`, then `tests/suite --affected` once, all report 0 failed (Task notes 5.1).

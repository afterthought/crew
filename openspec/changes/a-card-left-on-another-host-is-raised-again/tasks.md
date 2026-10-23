# Tasks

## 1. Every row's card is raised again where its owner runs

- [ ] 1.1 The rail's sweep judges every row's card, not a batch's alone, stranded on its owner's host, proved by `TestSweepJudged` in `tests/py/test_rail.py` (design, *Task notes* 1.1).
- [ ] 1.2 The sweep raises each such row through its kind's raise handed the older copy and reports what it did, proved by `TestSweep` in `tests/py/test_rail.py` (design, *Task notes* 1.2).
- [ ] 1.3 A proposal's, landing's, deploy's and step's raise handed an older copy posts its card saying that copy is dead, proved in `tests/py/test_cards.py` and `tests/py/test_ops.py` (design, *Task notes* 1.3).

## 2. A record's card is raised again from its record

- [ ] 2.1 The sweep on the main level's host judges a still-proposed record's stranded card, with whether it offered alternatives, proved by `TestSweepJudged` in `tests/py/test_rail.py` (design, *Task notes* 2.1).
- [ ] 2.2 The record's raise posts its card again from the record on the kit's main, or refuses naming the `crew record` command when it offered alternatives, proved in `tests/py/test_rail.py` and `tests/py/test_cards.py` (design, *Task notes* 2.2).
- [ ] 2.3 `crew record --proposed` records whether its card offered alternatives and posts saying the older copy is dead when one is stranded, proved in `tests/t-cards.sh` (design, *Task notes* 2.3).

## 3. Docs

- [ ] 3.1 README, the crew skill and `plugin/bin/crew`'s usage header say the rail's sweep raises every card left on another host again and what `crew record --proposed` does with one, proved by `tests/t-docs.sh` and `tests/suite --affected` (design, *Task notes* 3.1).

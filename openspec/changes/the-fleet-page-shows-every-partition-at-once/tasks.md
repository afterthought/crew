# Tasks

## 1. The fleet's data

- [x] 1.1 Every partition of the teams file is on the fleet's data in order, with its plan's commit, what could not be read, and each host it runs on with the sessions its agents run in and each session's Claude account, said so when the hosts file names none (design, Decisions 2; Task notes 1.1); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 Each partition's kits carry their main's last landing and what is queued for it, and its teams their bolt, each slot at work, holding or free, how many are at work and what the conductor waits on, with its attention in the board's words (design, Decisions 3 and 4; Task notes 1.2); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".

## 2. The page and its links

- [x] 2.1 The fleet page links each partition's page and each team's dock in the layout of its own file, and a partition's page links back to the fleet page in its own, none where crew cannot tell (design, Decision 5; Task notes 2.1); passes `tests/py/test_fleet.py` and `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 2.2 The fleet page is one file that loads nothing, its tokens the partition page's, light and dark, stacked under 760 px, every text set as text, with no control but links (design, Decision 5; Task notes 2.2); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".

## 3. The command and its docs

- [x] 3.1 `crew page --fleet` writes the fleet page whole from one read of every partition, by default beside the partitions' pages, prints its path, each partition's header and every host that did not answer, and refuses a label with it (design, Decisions 1 and 6; Task notes 3.1); verify `tests/suite t-journey-board` ends with "0 failed".
- [x] 3.2 README, the crew skill and the command's usage say what the fleet page shows and how it and the partitions' pages link (design, Context; Task notes 3.2); verify `tests/suite t-docs` ends with "0 failed".
- [ ] 3.3 The tests the change affects pass: verify `tests/suite --affected` ends with "0 failed".

# Tasks

## 1. The subscriptions' data

- [x] 1.1 The published use is read from one file per host in `~/.local/state/crew/usage/`, each checked against the published shape before any of it is used, a file that is not JSON or not of the shape named with what is wrong and the other files' readings kept (design, Decision 1; Task notes 1.1); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 Every account of the hosts file's sessions and of the readings is a subscription, showing its newest reading made with its five-hour, seven-day and per-model use as published, which host read it and how long ago, every other host's reading or failure, and that its use could not be read or that no host published it (design, Decisions 2 and 3; Task notes 1.2); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".
- [ ] 1.3 Each subscription lists the sessions on it by host with crew's agents in each, each team's slots at work and its conductor's wait as its partition's block says them, a session running no crew agent said so, and the partitions on it, while where a partition runs is unchanged (design, Decision 4; Task notes 1.3); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".

## 2. The page and the command

- [ ] 2.1 The fleet page shows the subscriptions above the partitions, each with its use as words and plain bars, its readings' hosts and ages, its sessions and partitions, and each unreadable file marked, every text set as text, still loading nothing and stacked under 760 px (design, Decision 5; Task notes 2.1); passes `tests/py/test_fleet.py`, verify `tests/suite logic` ends with "0 failed".
- [ ] 2.2 `crew page --fleet` reads the published use beside crew's state, shows it on the page, prints each file it could not read and that no use is published when none is, and still writes the page (design, Decision 6; Task notes 2.2); verify `tests/suite t-journey-board` ends with "0 failed".

## 3. Docs

- [ ] 3.1 README, the crew skill and the command's usage say what the subscriptions section shows, where its use is read from and what the command prints of it (design, Context; Task notes 3.1); verify `tests/suite t-docs` ends with "0 failed".
- [ ] 3.2 The tests the change affects pass: verify `tests/suite --affected` ends with "0 failed".

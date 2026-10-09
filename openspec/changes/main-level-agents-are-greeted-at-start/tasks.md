# Tasks

## 1. Every agent crew starts outside a team is greeted once

- [x] 1.1 `crew.py` greets any agent crew starts outside a team by its name, with its role's greeting, marked `[crew]`, waiting on it as it waits on a conductor, recording a `greet` entry, and refusing a team's agent or an unknown name; the conductor's greeting is unchanged (design.md, Task notes 1.1).
- [x] 1.2 `crew main up`, `crew _dispatch up`, `crew operator up` and `crew revive` greet each agent outside a team they start or bring back, side by side, and nothing they found already up, and still succeed when a greeting can't be sent (design.md, Task notes 1.2).
- [ ] 1.3 `tests/t-main.sh` holds the `main-level` delta's scenarios: one greeting per agent per start, none for a second `crew main up`, one more after down and up, an agent waiting on a question greeted after its answer without holding back the others, and one that never settles reported with nothing sent (design.md, Task notes 1.3). Verify `tests/suite t-main` ends with "0 failed".
- [ ] 1.4 `tests/t-operator.sh` and `tests/t-revive.sh` hold the `operator-agent` delta's scenarios and the revive scenario, and a team's agent or an unknown name is refused (design.md, Task notes 1.4). Verify `tests/suite t-operator t-revive t-greet t-standing` ends with "0 failed".

## 2. The documents say it

- [ ] 2.1 The usage of `plugin/bin/crew`, README and the crew skill say that `crew main up`, `crew operator up` and `crew revive` greet each agent they start (design.md, Task notes 2.1). Verify `tests/suite t-docs` ends with "0 failed".
- [ ] 2.2 `teams.7` reads as built and `_open.md` no longer lists it (design.md, Task notes 2.2). Verify `tests/suite --affected` ends with "0 failed".

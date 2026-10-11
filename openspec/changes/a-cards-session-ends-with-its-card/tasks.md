# Tasks

## 1. Every rail read ends the sessions of closed cards and gone rows

- [x] 1.1 `crew card sweep --label <label>`, run on a host with the rail's judgment on standard input, ends each session crew recorded there whose key is neither live nor blind, at least two minutes old and not being started, and prints what it did (design: *The reading host judges; each host ends its own*; Task notes 1.1; `read.4`, `code.2`).
- [x] 1.2 `end_session` keeps a key's session and ends nothing when plannotator's list can't be read, and says so (design: *plannotator's list unread: keep the record*; Task notes 1.2; `read.1`).
- [ ] 1.3 `crew rail` sweeps every host of each partition it read and prints each session it ended, with its host and why, and each host it could not check (design: *The reading host judges*, *What is known, and what is not*, *What the rail prints*; Task notes 1.3; `read.1`, `read.3`, `code.3`).
- [ ] 1.4 The rail tab's refresh sweeps as `crew rail` does, and `crew board` does not (design: *Why the rail, and not the board*; Task notes 1.4; `state.4`).
- [ ] 1.5 `tests/t-card-sweep.sh` proves each scenario of the delta's three new requirements, `tests/moon.yml` is regenerated, and `tests/suite t-card-sweep` ends with "0 failed" (Task notes 1.5).
- [ ] 1.6 `tests/t-card-session.sh` proves a session kept when plannotator's list can't be read, and `tests/suite t-card-session t-cards t-rail` ends with "0 failed" (Task notes 1.6).

## 2. The docs say so

- [ ] 2.1 README, the crew skill and `crew`'s usage header say every rail read ends the sessions of closed cards and gone rows and says which, and `tests/suite --affected` ends with "0 failed" (Task notes 2.1; `docs.2`).

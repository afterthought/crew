# Tasks

## 1. A restart ends with its agent running

- [x] 1.1 A restart finding its agent not up starts it without a stop only when herdr lists its pane with no agent, a mark names the session an earlier restart typed its exit into, and it was not taken down, and says why not otherwise (design, Decision 3; Task notes 1.1); passes `tests/py/test_hold.py` in the logic tier, `tests/suite logic`.
- [x] 1.2 `Agents` can watch for an agent's exit after its stop gave up, adding it to the agents it ended once herdr reads it gone and typing nothing more into its pane (design, Decision 1; Task notes 1.2); passes `tests/py/test_hold.py` in the logic tier, `tests/suite logic`.
- [ ] 1.3 `crew _renew` watches for ten minutes after its stop gives up and starts the agent the moment it exits, leaves a still-running agent as it was and says so, keeps and clears its mark, and starts an agent its earlier restart's keys ended (design, Decisions 1 to 3; Task notes 1.3); passes `tests/py/test_hold.py` in the logic tier, `tests/suite logic`.
- [ ] 1.4 The stub herdr has an agent slow to exit, and the hold journey proves a slow exit restarted, an agent that never exits left running, and a late exit brought back by the next restart (Task notes 1.4); Verify `tests/suite t-hold` ends with "0 failed".

## 2. The change's tests

- [ ] 2.1 The tests the change affects pass (Task notes 2.1); Verify `tests/suite --affected` ends with "0 failed".

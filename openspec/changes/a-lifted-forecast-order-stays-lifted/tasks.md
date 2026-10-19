# Tasks

## 1. The forecast orders nothing; a settle does

- [x] 1.1 A forecast between two unmerged units reaches the later one and writes no `After` (design.md, Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_forecast.py`.
- [x] 1.2 One decision says, from the run record, the plan and whether a branch holds the other's work, which pairs crew orders and which it lifts (design.md, Decisions 2, Task notes 1.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_forecast.py`.
- [x] 1.3 Every conductor's wait orders and lifts what the decision says before it forecasts, in the conductor's name, with `After` or `Lifted` and `Settle` on the entry (design.md, Decisions 3 to 5, Task notes 1.3). Verify `tests/suite t-journey-slots t-journey-merge` ends with "0 failed".
- [ ] 1.4 The wait on a settle that ends delivered or short orders or lifts for its unit and says so in its answer (design.md, Decisions 3, Task notes 1.4). Verify `tests/suite t-journey-merge` ends with "0 failed".

## 2. The journeys

- [ ] 2.1 The slots journey's forecast between two units tells the later one and leaves the plan with no `After` (design.md, Task notes 2.1). Verify `tests/suite t-journey-slots` ends with "0 failed".
- [ ] 2.2 A journey proves a settle that takes the other's work orders the pair and holds its merge, and a settle that stops short lifts an order crew wrote at a forecast (design.md, Task notes 2.2). Verify `tests/suite t-journey-merge` ends with "0 failed".

## 3. The briefs and the docs

- [ ] 3.1 The conductor's and planner's briefs say crew orders and lifts its own forecast orders and that nobody proposes lifting one, checked by `t-briefs.sh` (design.md, Decisions 6, Task notes 3.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 3.2 README, the crew skill and `crew unit wait`'s usage say how a settle orders two units and what crew's order writes record (design.md, Task notes 3.2). Verify `tests/suite --affected` ends with "0 failed".

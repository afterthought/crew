# Tasks

## 1. The briefs carry the rules

- [x] 1.1 The design agent's brief says a ruling names what it rests on, is made after reading the thing itself, rules the outcome and constraints rather than the sequence, and answers linked questions together, and that a unit it queues names the outcome and its governing records, never the mechanism (design.md, Task notes 1.1). Verify the new `wldn design` checks in `tests/t-briefs.sh` pass.
- [x] 1.2 The planner's brief says an intent names the outcome and the records that govern it, never the mechanism, and that corrections to a unit under construction are batched into one amendment once its construct settles unless one blocks the team (design.md, Task notes 1.2). Verify the new `wldn planner` checks in `tests/t-briefs.sh` pass.
- [ ] 1.3 The conductor's brief says linked design questions go to the design agent together, a reading it asks for comes from the team's ops, the answer goes back to the stage with the reading it names, and the planner hears when a construct it holds corrections for settles (design.md, Task notes 1.3). Verify the new `swb-1 conductor` checks in `tests/t-briefs.sh` pass, and `devenv shell -- tests/run` ends with "0 failed".

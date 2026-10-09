# Tasks

## 1. crew refuses a card or an area under another key

- [x] 1.1 `plan.py` decides, from the plan and the teams file, whether a crew agent may post a card under a key or make an area under a key, and gives the refusal's words naming the key to use (design.md, Task notes 1.1).
- [ ] 1.2 The card hook refuses Pending You's `post_request` and `create_area` from a crew session before the call runs, by that decision, refusing too when it cannot read what it decides from, and lets every other session and tool through (design.md, Task notes 1.2).
- [ ] 1.3 `tests/t-cards.sh` holds every scenario of the three refusal requirements in the `rail-cards` delta (design.md, Task notes 1.3). Verify `tests/suite t-cards t-card-session` ends with "0 failed".

## 2. The briefs

- [ ] 2.1 Every stage brief and ops's say in one shared sentence that they post no card and make no area (design.md, Task notes 2.1).
- [ ] 2.2 ops writes what a proof leaves the user under *Left for the user* in its proof file and posts no card for it (design.md, Task notes 2.2).
- [ ] 2.3 The conductor posts the landing card once the proof is clean or clean but for the user's steps, with those steps first on it, and treats a failed step as a fix, never a landing (design.md, Task notes 2.3).
- [ ] 2.4 The card discipline the planner and the conductor share says crew refuses any other key and names the key to use (design.md, Task notes 2.4).
- [ ] 2.5 `tests/t-briefs.sh` pins a phrase of each of 2.1 to 2.4 in the brief it lands in (design.md, Task notes 2.5). Verify `tests/suite t-briefs t-roles` ends with "0 failed".

## 3. The rules and README

- [ ] 3.1 `briefs.11` reads as built, its item leaves `_open.md`, and README's cards paragraph says crew refuses a card or an area under another key (design.md, Task notes 3.1). Verify `tests/suite --affected` ends with "0 failed".

# Tasks

Built after the one-process refactor lands, and after `a-kit-declares-its-toolchain-and-tests` and `a-carrying-fix-is-judged-by-its-commits`.

## 1. The bolt's checkout on its own branch

- [ ] 1.1 `crew bolt give` makes `bolt/<bolt>` from main's head and the checkout on `land/<bolt>` tracking it, with no worktree on `bolt/<bolt>`, and `t-journey-units` shows it (design: *Two branches per bolt*; Task notes 1.1; `plan.8`, `read.4`).
- [ ] 1.2 crew brings the checkout level with `bolt/<bolt>` after a merge stage delivers and in `crew prove`, by `following` and a fast-forward in the checkout, refusing and telling the conductor when it can't, and a refused follow refuses the proof; the logic, contract and journey cases pass, and `tests/suite logic contract journey-units` ends with "0 failed" (design: *The checkout follows its bolt*; Task notes 1.2; `code.6`, `code.7`, `roles.3`).
- [ ] 1.3 A contract case pins that `wt merge` moves a branch no worktree holds and runs post-merge hooks in the primary worktree, and `tests/suite contract` ends with "0 failed" (Task notes 1.3; `tests.11`).

## 2. What lands, and what a carry moves

- [ ] 2.1 The landing lands `land/<bolt>` and never moves `bolt/<bolt>`; a carry is judged against and moves `land/<bolt>`; after a carry, units and fixes are made from and merge into `land/<bolt>`; `t-journey-fix` and `t-journey-land` prove each, and `tests/suite logic journey-fix journey-land` ends with "0 failed" (design: *What lands, and what a carry moves*; Task notes 2.1; `plan.8`, `teams.5`, `code.6`).

## 3. The bolt's verification

- [ ] 3.1 crew verifies `land/<bolt>`'s head after every follow and carry through the kit's test adapter, in a place per revision, or reads a passing sluice landing; `crew bolt verify <bolt> [--again]` prints and reruns it; README, the skill and the usage header say so; the logic and journey cases pass, and `tests/suite logic journey-units docs` ends with "0 failed" (design: *crew verifies the bolt's head through the kit's test adapter*; Task notes 3.1; `read.1`, `tests.5`, `docs.2`).

## 4. The tidy

- [ ] 4.1 The tidy knows a bolt's checkout on `land/<folder>`, and on `bolt/<folder>` for a bolt given before this change, removes a verification place once its run is over, and judges `bolt/<bolt>` with no worktree by `plan.10`, keeping it when sluice's hook refuses; the logic cases pass, and `tests/suite logic` ends with "0 failed" (design: *The tidy*, *A bolt given before this change*; Task notes 4.1; `plan.9`, `plan.10`, `read.4`).

## 5. crew's own repository and the briefs

- [ ] 5.1 crew's `[post-merge]` verification, `bolt-verify.sh` and `bolt-status.sh` are gone and its declaration names its bolt branches' required checks; the conductor's, ops's and main-ops's briefs say where the bolt is built, deployed from and landed, each pinned in `t-briefs`; CLAUDE.md says `crew bolt verify`; and `tests/suite --affected` ends with "0 failed" (design: *crew's own repository*, *The briefs*; Task notes 5.1; `tests.6`, `docs.2`).

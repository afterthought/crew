# Tasks

## 0. Before anything else

- [x] 0.1 unit-amendments and the-rail-is-answered-through-cards are archived, so this change's deltas find the requirements they added (design.md, Decision 0; Task notes 0.1). Verify `openspec validate units-build-at-once-and-are-reviewed-in-batches --strict` reports the change valid.
- [ ] 0.2 `openspec/changes/concurrent-units` is gone, and the rules that cite it cite this change (design.md, Decision 0; Task notes 0.2). Verify `openspec validate units-build-at-once-and-are-reviewed-in-batches --strict` reports the change valid and `tests/suite --affected` ends with "0 failed".

## 1. Stages without a review gate

- [ ] 1.1 A unit's stage reads as the `bolt-plan` delta lists it: construct waits on each After unit's construct and never on a merge, code is accepted at `planned`, merge waits on each After unit's merge, and settle runs only for a verified unit (design.md, Decisions 1 to 3 and 6; Task notes 1.1). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 1.2 `crew unit approve`, the `review` rail row and its card key are gone, and an amended unit's mark stops counting once its construct has committed again (design.md, Decision 3; Task notes 1.2). Verify `tests/suite --affected` ends with "0 failed".

## 2. Building side by side

- [ ] 2.1 crew reads a unit's Touches before code, refuses code without them, names an overlap in the later unit's code prompt, and gives verify the paths changed and not declared (design.md, Decision 4; Task notes 2.1). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 2.2 Each of the conductor's waits forecasts conflicts with `git merge-tree`, writing no ref, and a forecast reaches the later unit once: told when idle, in its next stage's prompt, or as a settle stage (design.md, Decision 5; Task notes 2.2). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 2.3 A dependent's place takes its After units' heads when it is made and is rebased onto the bolt when each merges, only while its agent is idle; an amended After unit is carried to its dependent; two unmerged units forecast to conflict are ordered by `After` (design.md, Decisions 2 and 5; Task notes 2.3). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 2.4 The settle stage starts for a verified unit a forecast or amendment reaches, and ends at a commit made since it began, or stops short when nothing needs to change (design.md, Decision 6; Task notes 2.4). Verify `tests/suite --affected` ends with "0 failed".

## 3. Batches

- [ ] 3.1 Due changes are counted across the partition from the run record, a batch is due at N or at T hours, the planner starts the reviewer with `crew review <label>`, the reviewer's file is its deliverable, the planner posts cards of at most five units keyed `batch/<n>-<k>`, which the card hook allows, `crew card session` starts one session for each unit of a card on its team's host, and a bolt is offered for landing only once every unit's latest change has been in a batch (design.md, Decision 7; Task notes 3.1). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 3.2 crew refuses a partition whose teams-file entry carries no batch setting, naming the field; the setting itself is written by swancloud's unit `partitions-carry-their-batch-setting`, landed first (design.md, Decision 10; Task notes 3.2). Verify `tests/suite --affected` ends with "0 failed".

## 4. Merging through sluice

- [ ] 4.1 A kit opts into sluice by a flag in its config, and its merge stage then runs `wt submit bolt/<bolt>`, else `wt merge` as now (design.md, Decision 8; Task notes 4.1). Verify `tests/suite --affected` ends with "0 failed".

## 5. Briefs and docs

- [ ] 5.1 `conductor.md`, `planner.md`, `construct.md`, `coder.md` and `verify.md` say what design.md Decision 9 says, `reviewer.md` exists, and `tests/t-briefs.sh` pins the new phrases. Verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [ ] 5.2 README, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` name `crew review` and the settle stage, drop `crew unit approve`, and describe batches and the merge command (`docs.2`). Verify `tests/suite t-docs` ends with "0 failed".
- [ ] 5.3 The rules record 0014 amended read as built, and `_open.md` no longer lists them (design.md, Decision 11). Verify `tests/suite --affected` ends with "0 failed".

## 6. Proof on real work

- [ ] 6.1 Work design.md's *Proof on real work* once the bolt has landed and every host has pulled.

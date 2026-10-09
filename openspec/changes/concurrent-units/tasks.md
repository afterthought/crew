# Tasks

## 1. Stages without a review gate

- [ ] 1.1 A unit's stage reads as the `bolt-plan` delta lists it: construct never waits on `After`, code waits on each After unit's construct and is accepted at `planned`, and merge waits on each After unit's merge (design.md, Decisions 1 to 3; Task notes 1.1). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 1.2 `crew unit approve`, the `review` rail row and its card key are gone, and an amended unit's mark stops counting once its construct has committed again (design.md, Decision 3; Task notes 1.2). Verify `tests/suite --affected` ends with "0 failed".

## 2. Building side by side

- [ ] 2.1 crew reads a unit's Touches before code, refuses code without them, tells the later of two overlapping units, and gives verify the paths changed and not declared (design.md, Decision 4; Task notes 2.1). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 2.2 Each of the conductor's waits forecasts conflicts with `git merge-tree` and tells the later unit's agent once per pair of heads, writing no ref (design.md, Decision 5; Task notes 2.2). Verify `tests/suite --affected` ends with "0 failed".
- [ ] 2.3 A dependent's place takes its After units' heads when its code starts and is rebased onto the bolt when each merges, only while its agent is idle; a conflicting rebase is undone and handed to its agent (design.md, Decision 2; Task notes 2.3). Verify `tests/suite --affected` ends with "0 failed".

## 3. Batches

- [ ] 3.1 Due changes are counted from the run record, a batch is due at N or at T hours, `crew review <team>` runs a fresh reviewer whose file is its deliverable, the conductor posts one batch card, and a bolt is offered for landing only once every unit's latest change has been in a batch (design.md, Decision 6; Task notes 3.1). Verify `tests/suite --affected` ends with "0 failed".

## 4. Merging through sluice

- [ ] 4.1 The merge stage runs `wt submit bolt/<bolt>` where sluice is available for the kit, else `wt merge` as now (design.md, Decision 7; Task notes 4.1). Verify `tests/suite --affected` ends with "0 failed".

## 5. Briefs and docs

- [ ] 5.1 `conductor.md`, `construct.md`, `coder.md` and `verify.md` say what design.md Decision 8 says, `reviewer.md` exists, and `tests/t-briefs.sh` pins the new phrases. Verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [ ] 5.2 README, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` name `crew review`, drop `crew unit approve`, and describe batches and the merge command (`docs.2`). Verify `tests/suite t-docs` ends with "0 failed".
- [ ] 5.3 The rules record 0014 amended read as built, and `_open.md` no longer lists them (design.md, Decision 10). Verify `tests/suite --affected` ends with "0 failed".

## 6. Proof on real work

- [ ] 6.1 Work design.md's *Proof on real work* once the bolt has landed and every host has pulled.

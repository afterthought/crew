# Tasks

## 1. The briefs leave a change's content to the kit

- [x] 1.1 The construct brief names no proof list, task shape or *Task notes*, and says a change's content is the kit's, from its `openspec/config.yaml` through `/opsx:propose` (design, Decision 1; Task notes 1.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 1.2 The coder's brief names no work that needs dev, and the results section every brief carries names no *Proof in dev* list (design, Decision 2; Task notes 1.2). Verify `tests/suite t-briefs` ends with "0 failed".

## 2. crew's config says crew's conventions

- [x] 2.1 crew's `openspec/config.yaml` carries crew's rules for specs, design and tasks and the apply guidance to tick a task only when its check passes, and OpenSpec hands them over (design, Decision 3; Task notes 2.1). Verify `openspec instructions tasks --change a-change-holds-what-is-true-and-what-is-proved --json` lists the three tasks rules with no warning.
- [x] 2.2 The docs' test reads crew's config and checks each convention (design, Decision 4; Task notes 2.2). Verify `tests/suite t-docs` ends with "0 failed".

## 3. Integration

- [x] 3.1 Everything this change affects passes (Task notes 3.1). Verify `tests/suite --affected` ends with "0 failed".

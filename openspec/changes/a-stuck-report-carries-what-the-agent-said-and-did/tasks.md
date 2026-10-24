# Tasks

## 1. What crew reads

- [x] 1.1 `transcript.last_words` gives the text of the agent's own last message since a time, read across the records that share its message id, a subagent's never, a message before the time never, and None for a transcript it cannot read, its format fact named in the module's docstring (design, Decision 1; Task notes 1.1). Passes `tests/py/test_transcript.py` (`tests/suite logic`).
- [x] 1.2 `gather.since` gives the commits along a branch's first parent from its head, beyond a base when given, as short sha, committer time and subject, newest first, or None when git refuses (design, Decision 2; Task notes 1.2). Passes `tests/contract/test_gather.py` (`tests/suite contract`).

## 2. The stuck report

- [x] 2.1 A stuck answer opens with the stuck line ending "nothing it needs said through crew", then lists the branch's commits since the stage began, at most ten, or says it holds none and names its head, then quotes the agent's last words since the stage began with their time, cut at 2,000 characters on a line's end with how much more and where, saying in each part what crew could not read (design, Decisions 3 and 4; Task notes 2.1). Passes `tests/py/test_wait.py` (`tests/suite logic`).
- [x] 2.2 The wait reads the agent's last words and its branch's commits in the look that finds it stuck, and only then, and answers with the report; a chore's commits are its own beyond its bolt (design, Decisions 2 and 3; Task notes 2.2). Verify `tests/suite t-journey-units` ends with "0 failed".

## 3. A code stage with no task list

- [x] 3.1 slc-1's case is pinned: a fix round's code stage on a unit whose change is archived at its head delivers at its commit since it began, as the chore built it (design, Decision 6; Task notes 3.1). Passes `tests/py/test_stage_ends.py` (`tests/suite logic`).

## 4. The conductor and the docs

- [x] 4.1 The conductor's brief has it read a stuck report's words and commits first, act on what they settle, and ask the user, running the stage again or waiting again on their word, only when the report settles nothing, a stuck fix round read the same way (design, Decision 5; Task notes 4.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [ ] 4.2 README, the crew skill and `crew`'s usage header say what a stuck answer carries, that a code stage whose head has no task list ends at its commit, and that the conductor reads the report before it asks (design, Decisions 3, 5 and 6; Task notes 4.2; `docs.2`). Verify `tests/suite t-docs` ends with "0 failed".

## 5. The change's tests

- [ ] 5.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".

# Tasks

## 1. What the landing reads and decides

- [x] 1.1 A read on the team's host fetches the bolt's branch from origin and reports both copies, the policy at GitHub's, and which holds the other, and kit reads it or refuses naming what was printed (design, Decision 1; Task notes 1.1); passes `tests/py/test_kit.py`, verified by `tests/suite logic` ending with "0 failed".
- [x] 1.2 One pure decision names the head a landing submits, whether it levels the host's copy, and what it says, refusing a diverged bolt or a read that failed (design, Decision 2; Task notes 1.2); passes `tests/py/test_landing.py`, verified by `tests/suite logic` ending with "0 failed".

## 2. The landing levels the copy and submits GitHub's head

- [x] 2.1 `SUBMIT` levels the host's copy to the head given by a guarded `update-ref` before it cuts, brings a standing landing worktree's files along, refuses when its head is not the head given, and levels nothing when it waits on an earlier submission (design, Decision 3; Task notes 2.1); passes `tests/contract/test_git.py`, verified by `tests/suite contract` ending with "0 failed".
- [x] 2.2 `crew bolt submit` reads and decides before it readies the pull request, submits nothing of a bolt it refuses, and says when it levelled a copy (design, Decision 4; Task notes 2.2); passes `tests/py/test_landing.py` and `tests/py/test_bolt_commands.py`, verified by `tests/suite logic` ending with "0 failed".

## 3. Proved end to end, and said

- [x] 3.1 A bolt whose host copy lags GitHub's lands at GitHub's head, main holding the merge the copy lacked (design, Decision 4; Task notes 3.1); verified by `tests/suite t-journey-land` ending with "0 failed".
- [x] 3.2 README and the crew skill say the landing submits GitHub's head, levelling the host's copy first, and refuses a diverged bolt (design, Decision 2; Task notes 3.2); verified by `tests/suite t-docs` ending with "0 failed".
- [x] 3.3 The tests the change affects pass; verified by `tests/suite --affected` ending with "0 failed".

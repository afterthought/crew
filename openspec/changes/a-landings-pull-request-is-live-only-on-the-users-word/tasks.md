# Tasks

## 1. crew reads and decides the pull request's state

- [x] 1.1 crew reads whether a kit's policy at main takes pull requests into main, and what `gh pr list` said of a bolt's open pull request into main, refusing what it can't read (design, Decision 3 and 4; Task notes 1.1). Passes `tests/py/test_kit.py`.
- [x] 1.2 crew decides from facts alone whether to draft, ready or leave a bolt's pull request, says what it did, and reads and marks it on the team's host only where the kit's main takes pull requests (Decision 4 and 5; Task notes 1.2). Passes `tests/py/test_landing.py`.

## 2. The pull request follows the user's word

- [x] 2.1 `crew bolt submit` readies the bolt's draft pull request before it submits, refusing with nothing submitted when it can't, and leaves it a draft, said with its link, when the bolt does not land (Decision 2 and 5; Task notes 2.1). Verify `tests/suite t-journey-land` ends with "0 failed" and passes `tests/py/test_landing.py`.
- [ ] 2.2 A fix's start drafts the bolt's ready pull request as its landing card is held, and a unit's, chore's or fix's merge into the bolt drafts it before it starts or does not start, naming the pull request (Decision 2; Task notes 2.2). Verify `tests/suite t-journey-units` ends with "0 failed" and passes `tests/py/test_bolt_commands.py`.

## 3. Docs and stubs

- [ ] 3.1 README, the crew skill and `crew`'s usage header say a landing that does not land leaves its pull request a draft and the next `crew bolt submit` readies it (Task notes 3.1, `docs.2`). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 3.2 The tests' `gh` is a stub that `tests/run` requires, and `tests/moon.yml` is regenerated with `tests/moon-tasks` (Decision 6; Task notes 3.2). Verify `tests/suite logic` ends with "0 failed".

## 4. The affected tests

- [ ] 4.1 The tests the change affects pass. Verify `tests/suite --affected` ends with "0 failed".

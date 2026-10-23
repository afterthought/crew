# Tasks

## 1. crew's record names the pane, and is read by pane

- [ ] 1.1 crew's session-start hook records the herdr session and pane each crew agent's session started in, at a start through crew and at herdr's resume alike (design, Decision 1; Task notes 1.1); verify `tests/suite t-session-hook` ends with "0 failed".
- [ ] 1.2 `questions.py` answers, for an agent's herdr session and pane, the newest session crew recorded of that agent starting there and that session's question mark, or no session (design, Decision 2; Task notes 1.2); passes `tests/py/test_questions.py`, verify `tests/suite logic` ends with "0 failed".

## 2. A tell reaches a pane herdr names no session for

- [ ] 2.1 A tell to an agent herdr names no session for reads the session from crew's record of its pane, and with neither is guarded by herdr's reading alone, never refused for the missing session (design, Decisions 2 and 3; Task notes 2.1); passes `tests/py/test_review.py`, verify `tests/suite logic` ends with "0 failed".
- [ ] 2.2 On the stubs, a main-level agent whose pane herdr names no session for is told, is refused while the session crew recorded in its pane has a question open, and is told again with no record of its pane (design, Decision 3; Task notes 2.2); verify `tests/suite t-journey-main` ends with "0 failed".

## 3. Docs and the affected tests

- [ ] 3.1 README's main-level paragraph says how a tell is guarded when herdr names no session for the agent's pane (design, Decision 4; Task notes 3.1); verify `tests/suite t-docs t-briefs` ends with "0 failed".
- [ ] 3.2 The tests this change affects pass (Task notes 3.2); verify `tests/suite --affected` ends with "0 failed".

# Tasks

## 1. The refusal and the check

- [x] 1.1 `crew signal`'s refusal of an excerpt keeps its present opening and names a background task's output, which is in the transcript only once its output file is read, decided by `excerpt_refusal` in `plan.py` and proved by a case in `tests/py/test_signals.py` and `tests/suite t-journey-signals` passing unedited (design: *The refusal's words*; Task notes 1.1; `code.7`, `signals.2`).
- [ ] 1.2 Logic cases in `tests/py/test_transcript.py` prove, on records shaped as Claude Code 2.1.303 writes them, that a crew command's printed line is verified as a tool's and refused recapitalized, and that a background task's output is refused until a Read of its file puts it in the transcript, then verified as a tool's, two lines together included, with `transcript.py` unchanged (design: *Context*; Task notes 1.2; `signals.2`, `signals.5`).

## 2. What the agents and the README say

- [ ] 2.1 Every brief that records findings says a refusal means the words were reworded or are a background task's output not yet read, proved by `tests/suite t-briefs` (design: *The briefs' sentence*; Task notes 2.1).
- [ ] 2.2 README's Signals section says a refusal names both cases, proved by `tests/suite t-docs` (Task notes 2.2; `docs.2`).

## 3. The whole change

- [ ] 3.1 `tests/suite --affected` ends with "0 failed" (Task notes 3.1; `tests.5`).

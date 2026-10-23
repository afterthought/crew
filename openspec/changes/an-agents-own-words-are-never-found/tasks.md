# Tasks

## 1. The check

- [x] 1.1 `transcript.check` passes over lines of type `api-request-blob` as it passes over lines of type `assistant`, and the module's header and `check`'s docstring name that format fact, the 2.1.303 transcript it was read from and the grade that falls when it stops holding, proved by the cases of 1.2 passing in the logic tier, `tests/suite logic` (design: *Skip the copy record type whole*, *The header says what the fact holds*; Task notes 1.1; `signals.2`).
- [ ] 1.2 Logic cases in `tests/py/test_transcript.py` prove, on records shaped as Claude Code 2.1.303 writes them, that the agent's own reply and its own command are refused though Claude Code copied them, that words only in a copy are refused, and that the user's words and a tool's output with their copies beside them stay verified with their own record as the source, passing with `devenv shell -- moon run tests:logic` (design: *Context*, *Where the cases go*; Task notes 1.2; `signals.2`, `signals.5`, `tests.4`).

## 2. The whole change

- [ ] 2.1 `tests/suite --affected` ends with "0 failed" (Task notes 2.1; `tests.5`).

# Tasks

## 1. The landing

- [x] 1.1 `crew signal land <capture-dir>` checks the folder whole and refuses, naming the file, what the design's checks rule out, with logic cases in `tests/py/test_signals.py` (design: *The checks, before any write*; `signals.3`, `signals.4`, `signals.6`, `code.4`, `code.7`).
- [x] 1.2 It lands the folder in one commit on the flywheel's branch with a `capture` entry, passes over what the branch holds the same, refuses what differs and writes nothing for a capture landed already, with logic cases and one step of `tests/t-journey-signals.sh` (design: *The write*; `state.1`, `plan.1`).
- [x] 1.3 `crew signal land --help` begins with its usage, a signal's slug can't be `land`, and README, SKILL.md and the usage header name the command, `tests/t-docs.sh` passing (`docs.2`).

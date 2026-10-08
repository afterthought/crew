# Tasks

## 1. A stage ends at its deliverable

- [x] 1.1 The run record takes a stage end's `Ended` and `Delivered`, and `crew trace` finds `report/` and `proof/` objects; `t-record.sh` and `t-events.sh` still pass (design: *The run record*; Task notes 1.1).
- [x] 1.2 `transcript.py` names the background tasks an agent's session started and has not been told are over, and the time of its last record, or says it could not read them (design: *Still running or stuck*; Task notes 1.2; `read.2`).
- [x] 1.3 crew reads whether each stage's deliverable exists since the stage began, for construct, code, verify, merge, a fix, a fix's merge and ops's proof (design: *What each deliverable is, and how it is read*; Task notes 1.3).
- [x] 1.4 A wait returns at a delivered end (recording it), a stop-short, a stuck stage, a gone agent or its timeout, each as the one line the design gives (design: *The wait*; Task notes 1.4).
- [x] 1.5 A late end is recorded only once its deliverable exists, and ending a slot's or ops's agent records the owed end as delivered or stopped (design: *The run record*; Task notes 1.5; `record.5`).
- [x] 1.6 `crew needs "<words>"` ends its caller's stage short and carries the words to the waiting wait or, with none, to the conductor in a marked tell, never into the run record; it is refused for anyone without an owed stage and for empty words (design: *Stopping short*; Task notes 1.6; `record.3`, `roles.4`).
- [x] 1.7 `crew unit wait` takes `--stuck`, `crew fix <team> <name> --wait` and `crew prove <team> [--wait]` exist, `stop` ends an owed proof, and the usage header names them (design: *The wait*, *Ops's proof is a stage*, *A fix waits the same way*; Task notes 1.7; `docs.2`).
- [x] 1.8 The conductor, construct, coder, verify and ops briefs wait, stop short and write the proof file as the design says, with `{{NEEDS}}` built once in `crew.py` (design: *The briefs*; Task notes 1.8; `briefs.6`, `briefs.8`).
- [ ] 1.9 `tests/t-stage-ends.sh` proves each deliverable, the stuck clock with and without background work and transcript, the stop-short both ways, the gone agent, a fix's wait and the proof (Task notes 1.9; `tests.2`, `tests.4`).
- [ ] 1.10 `t-record-team.sh`, `t-amend.sh` and `t-fix.sh` read the new ends, and `t-briefs.sh` pins the briefs' new phrases (Task notes 1.10; `tests.6`).
- [ ] 1.11 `teams.4` names its sources and leaves `_open.md`, and README and the crew skill describe the new waits, `crew needs`, `crew prove` and the new fields (Task notes 1.11; `docs.2`).
- [ ] 1.12 `devenv shell -- tests/run` ends with "0 failed".

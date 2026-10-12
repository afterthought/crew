# Tasks

## 1. The plan holds chores

- [x] 1.1 The Unit descriptor allows `Kind` (`enum chore`); `Plan` reads units, chores and both apart; crew's own rules refuse `Amended` on a chore and check `After` across kinds; `crew chore add|order|after|move|drop` are built by the unit's ops with the kind from the command, refusing a record of the other kind; `may_write` gives chores the unit's table; a name is refused when main holds a chore trailer by it; and logic cases in `tests/py/test_chores.py` prove each (design: *The plan marks a chore*, *The commands mirror a unit's*, *A name is taken once in a kit*; `plan.1`, `plan.5`, `plan.7`, `roles.1`).

## 2. A chore's stage is read from its kit

- [x] 2.1 gather.py reads each kit's chore trailers on main and each bolt and each chore's place, in its one read; `Stages.of` reads a chore's stage by the design's table and a unit after a chore waits on its merge; a bolt is landed once every unit and chore is; and logic cases prove the table, with a contract case pinning the trailer reading on real git (design: *A chore's stage is read from its kit*, *`After` across kinds is met at the chore's merge*; `state.2`, `plan.12`, `read.1`).

## 3. A chore is built by code, verify and merge

- [x] 3.1 `plan _run --chore` decides by `chore_refusal`, makes the place at its first code, refuses a merge while a commit lacks the trailer, prints the stage's prompt, and refuses a stage of the other kind; `crew chore run|wait|free` in bash take the chore's slot and run its stages; `Owed`, the deliverables, the slots, the tidy and `transcript.STAGE` know a chore; logic cases prove each decision, and `tests/t-journey-chores.sh` proves the wiring from `chore add` through code, verify and merge to the slot's freeing (design: *Running a chore's stages*, *A stage ends at its deliverable*, *Slots and places*; `teams.1`, `teams.2`, `teams.4`, `teams.5`, `teams.15`, `plan.9`, `tests.12`).

## 4. Chores everywhere work is counted

- [x] 4.1 A team's give, a bolt's landing and drop, work a held bolt needs, the rail's verify and landing rows, the card hook and the card sweep count chores; no batch holds a chore; a proposal carries the chore commands, `describe`, `summary`, `objects` and the card read them and `--clear` leaves a chore out; and logic cases prove each (design: *Batches, review and the landing*, *Proposals and the card*; `plan.3`, `briefs.11`, `briefs.12`, `signals.7`).
- [x] 4.2 `crew bolts`, its JSON, the board, each agent's view (`code.8`) and the page show a chore as one, `crew sites` lists its place, and the run record's `chore/` objects, acts and trace are read, with logic cases for the views, the page and the record (design: *Views*, *The run record*; `record.1`, `record.3`).

## 5. The briefs and docs say so

- [x] 5.1 The coder's, verifier's, conductor's, planner's and design agent's briefs say what a chore is to each, pinned by phrases in `tests/t-briefs.sh`; README, the crew skill and the usage headers say the commands; `plan.9`, `plan.11`, `plan.13`, `teams.1`, `teams.5` and `signals.7` are amended and `_open.md` no longer lists the chore kind; `tests/moon.yml` is in step; and `tests/suite --affected` ends with "0 failed" (design: *Briefs and docs*; `tests.6`, `docs.2`, `docs.5`).

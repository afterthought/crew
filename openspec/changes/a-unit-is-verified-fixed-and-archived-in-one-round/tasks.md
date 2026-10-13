# Tasks

## 1. The report says what to do, and one fresh coder fixes it

- [x] 1.1 `verify.md` checks the code against the unit's change as written and ends the report with *What to do*, each finding marked fix or leave; `coder.md` makes code told a report's path the one round of fixes, fixing what is marked fix and only those; `conductor.md`'s table, building loop and chore paragraph take the marks as they stand, with no card, nothing taken to the planner and a fix round that fails a stuck stage; `operator.md` waits on no verify report. Checked by `tests/t-briefs.sh`, "a verify is one round with no card" and "the conductor posts no verify card" (design: *The report marks each finding*, *One fix round is a code stage told the report's path*; `teams.17`, `briefs.2`, `briefs.13`).

## 2. A verify stands through its fix round

- [x] 2.1 `verified` reads a delivered verify since the unit's last construct, so a code start after it undoes nothing, and `chore_refusal` merges a chore once its verify has delivered. Checked by `tests/py/test_forecast.py` `TestVerified` and `tests/py/test_chores.py` `test_chore_refusal`; the wiring by `tests/t-journey-merge.sh`, a forecast reaching a unit fixed after its verify as a settle, and `tests/t-journey-chores.sh`, a chore merged after its fix round (design: *A verify stands through its fix round*; `teams.5`, `teams.14`).

## 3. A unit's merge archives its change first

- [x] 3.1 `coder.md`'s merge archives a unit's change with `openspec archive <unit> --yes` and commits it before the merge command; `gather.archived` reads a branch's archived changes and `gather.place` a place's archived change; `deliverable_facts` and `delivered` end a unit's merge only once its bolt holds the change archived. Checked by `tests/contract/test_gather.py` `test_a_place_whose_merge_archived_its_change_reads_it_from_the_archive_and_the_bolt_then_holds_it_archived`, `tests/py/test_stage_ends.py` `TestMerge`, and `tests/t-journey-merge.sh`, a unit merged once its change is archived (design: *A unit's merge archives its change first, and delivers only so*; record 0006, `state.2`, `read.1`, `teams.4`).

## 4. No verify row, key or card

- [x] 4.1 `RAIL` and `rail_rows` make no verify row and `survey` asks for no reports folder; `card_refusal` gives no agent a verify key, the card hook has no verify form and records a close under an old one, and `card_of`, `card_row` and `card_session` know no verify document; `stray_cards` and the sweep judge no verify key blind; `ends_row` and `stage_ended_row` go, and `lost_rows` and `amend_told` name no verify row. Checked by `tests/py/test_rail.py`, `test_cards.py`, `test_card_commands.py`, `test_review.py`, `test_amend.py` and `test_prompts.py`, and `crew card`'s requirements by `tests/t-card-commands.sh` on a landing card; the wiring by `tests/t-journey-review.sh`, `t-card-commands.sh`, `t-journey-land.sh`, `t-journey-plan.sh` and `t-journey-chores.sh` (design: *The verify row, its key and its card go*; `briefs.11`, `briefs.13`, `briefs.16`).
- [x] 4.2 The board's units carry no markers, and ✎ goes from the board, the operator's view and the page. Checked by `tests/py/test_board.py` and `tests/t-journey-board.sh` (`code.8`).

## 5. The docs say so

- [x] 5.1 README, the crew skill, the usage headers of `plugin/bin/crew` and `plan.py`, and the card discipline in `crew.py` say the one round, the four groups and the archive at the merge; `tests/moon.yml` is in step; and `tests/suite --affected` ends with "0 failed". Checked by `tests/t-docs.sh` and `tests/t-briefs.sh` (`docs.2`, `tests.10`).

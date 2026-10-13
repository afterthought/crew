# Tasks

## 1. A bolt's archived and open changes are read apart

- [x] 1.1 `gather.kit` gives each bolt its archived changes and the tasks of each change it holds open that main does not hold (`opened`, `carried`). Checked by `tests/contract/test_gather.py` `test_a_change_carried_onto_the_bolt_inside_another_units_merge_is_read_open_with_its_tasks` (`state.2`, `teams.17`).

## 2. Merged means archived

- [x] 2.1 `Stages.of` reads a unit merged only once its bolt holds its change archived, and a carried unit at its own stage, from its place or the change on the bolt (`carried_place`). Checked by `tests/py/test_chores.py` `TestStage::test_a_unit_has_merged_only_once_its_bolt_holds_its_change_archived`, and the rail's landing row by `tests/py/test_rail.py` (`teams.17`, `read.1`).
- [x] 2.2 `slot_stage` and `tidy` read the same, so a carried unit keeps its slot and its place. Checked by `tests/py/test_tidy.py` `TestSlotStage::test_a_unit_whose_change_the_bolt_holds_open_has_not_merged_and_is_said_carried` and `test_one_whose_place_is_gone_reads_its_stage_from_the_change_on_the_bolt`, and the tidy's wiring by `tests/t-journey-carried.sh` (`teams.1`, `plan.9`).

## 3. A carried unit is named, and its merge is its own

- [x] 3.1 `crew status` names a carried unit on its slot's line or a line of its own, its merge owed (`holds_said`, `carried_said`, `carried_units`). Checked by `tests/py/test_slots.py` `TestStatus::test_a_unit_carried_onto_its_bolt_inside_another_merge_is_named_so_its_merge_owed`, and the wiring by `tests/t-journey-carried.sh` (`teams.17`).
- [x] 3.2 A carried unit's merge makes its place again from the bolt when it is gone, archives its change there and delivers once the bolt holds it archived. Checked by `tests/t-journey-carried.sh`, "a carried unit's merge makes its place again from the bolt" (`teams.17`, `teams.4`).

## 4. The docs say so

- [x] 4.1 The conductor's and coder's briefs, README, the crew skill and the usage headers say it. Checked by `tests/t-briefs.sh` and `tests/t-docs.sh` (`docs.2`, `tests.6`).

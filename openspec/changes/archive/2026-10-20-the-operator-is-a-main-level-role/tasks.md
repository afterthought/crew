# Tasks

## 1. The operator is a main-level role

- [x] 1.1 `crew main up`, `down`, `status` and `crew revive` take `<label>-operator` as a standing role of the main level, its tab after ops', greeted once it is up. Verify `tests/suite t-journey-main` ends with "0 failed".
- [x] 1.2 `place_of_agent`, `label_of_agent`, `standing_greeting`, `brief_role` and plan's `role` and `where_of` read `<label>-operator` as the main level's. Verify `tests/suite logic` ends with "0 failed".
- [x] 1.3 Every brief names `<label>-operator` as the partition's operator and door; the operator's brief says it is a main-level role. Verify `tests/suite t-briefs t-roles` ends with "0 failed".
- [x] 1.4 The board's operator view is `<label>-operator`'s. Verify `tests/suite logic` ends with "0 failed".

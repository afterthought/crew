# Tasks

## 1. A merge is waited on with sluice wait

- [x] 1.1 `merge_command` gives `sluice submit bolt/<bolt> --no-wait --json`, and the stub sluice takes a submission without waiting and `sluice wait`. Verify `tests/suite logic t-sluice t-journey-merge t-journey-chores t-journey-fix t-journey-carried t-journey-land` ends with "0 failed".
- [x] 1.2 The coder's, conductor's, design agent's and operator's briefs submit without waiting, wait with `sluice wait`, and read no listing. Verify `tests/suite t-briefs` ends with "0 failed".

# Tasks

## 1. crew send

- [x] 1.1 A team or a partition's label resolves to its partition's operator, and an unknown name or the door sending to its own partition is refused (design.md, decision 1; Task notes 1.1). Verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 A send is a tell to the door, marked with its sender and `(sent to <name>)`, recorded as one `send` entry in the receiving partition with no tell entry, and nothing recorded when nothing was typed (decisions 2 and 3; Task notes 1.2). Verify `tests/suite logic` ends with "0 failed".
- [x] 1.3 `crew send <team or partition> "<text>"` is a command in `plugin/bin/crew` and its usage, and reaches the operator end to end (decision 6; Task notes 1.3). Verify `tests/suite t-journey-main` ends with "0 failed".

## 2. The briefs

- [x] 2.1 Every brief's roster says in one line that anything for another team or partition goes with `crew send`, and to nobody else (decision 4; Task notes 2.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 2.2 The operator's brief carries what is sent to it, and sends a teams change from a box with `crew send <label>` (decision 5; Task notes 2.2). Verify `tests/suite t-briefs t-roles` ends with "0 failed".

## 3. The documents

- [x] 3.1 README, the crew skill and the record's field comment name `crew send` (decision 6; Task notes 3.1). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 3.2 The tests' moon tasks are in step with the tests (Task notes 3.2). Verify `tests/suite --affected` ends with "0 failed".

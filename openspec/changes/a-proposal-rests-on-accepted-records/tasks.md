# Tasks

## 1. A proposal is refused when its new work rests on a record not accepted

- [x] 1.1 `crew record` and the proposal check read a record's status through one function, with `record_facts`'s refusals and words unchanged (design, Decision 4; Task notes 1.1); passes `tests/py/test_cards.py`, via `tests/suite logic`.
- [ ] 1.2 crew finds the records a source names by their `docs/adr/<number>` path, of the item's kit or of the `<owner>/<name>` before it, and none named only in words (design, Decision 2; Task notes 1.2); passes `tests/py/test_proposals.py`, via `tests/suite logic`.
- [ ] 1.3 crew judges the records read and words one refusal naming each unit or bolt, the record and what its main holds, and refuses nothing when every one is accepted (design, Decisions 4 and 5; Task notes 1.3); passes `tests/py/test_proposals.py`, via `tests/suite logic`.
- [ ] 1.4 `crew plan propose` reads the records named by the bolts it creates and the units and chores it adds or moves into a bolt, on each repository's main as GitHub holds it, and refuses before anything is written or a card raised (design, Decisions 1 and 3; Task notes 1.4); Verify `tests/suite logic` ends with "0 failed".
- [ ] 1.5 A proposal whose new unit names a proposed record is refused naming it, with the plan and the cards unchanged, and is written once the record is accepted on the kit's main (Task notes 1.5); Verify `tests/suite t-journey-plan` ends with "0 failed".

## 2. README says so

- [ ] 2.1 README's `crew plan propose` bullet says a proposal is refused when its new bolts or units name a record its main does not hold accepted (Task notes 2.1); Verify `tests/suite t-docs` ends with "0 failed".

## 3. The tests the change affects

- [ ] 3.1 Every test the change affects passes; Verify `tests/suite --affected` ends with "0 failed".

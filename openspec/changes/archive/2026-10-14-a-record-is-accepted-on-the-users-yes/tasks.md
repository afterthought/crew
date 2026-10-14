# Tasks

## 1. The check and the record

- [x] 1.1 crew's card check lets the design agent post under `record/<kit>/<number>/<commit>` for a kit of its partition, refuses it any other key naming that form, and refuses a record key from every other agent as before (design.md, D2; Task notes 1.1). Verify `tests/suite t-cards` ends with "0 failed".
- [x] 1.2 The card hook records a record card with its key on `record/<kit>/<number>`, refuses one that is not a low-risk approval without options or steps, or a change out of that form, and ends no plannotator session when it closes (design.md, D2, D3; Task notes 1.2). Verify `tests/suite t-cards` ends with "0 failed".

## 2. The rail

- [x] 2.1 `crew rail` lists open record cards under a heading of their own with who asked and when, never among the cards whose row is gone, and its usage header and the crew skill say so (design.md, D5; Task notes 2.1). Verify `tests/suite t-rail t-docs` ends with "0 failed".

## 3. The design agent's brief

- [x] 3.1 The design agent's brief has every record and amendment committed as proposed and put on one card in the record's words, accepted only on the user's yes and recorded so, the user's own words recorded as their decision, and the card's key, form, words and start-up pass (design.md, D1, D3, D4, D6; Task notes 3.1). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 3.2 `t-briefs.sh` pins each rule the brief now states (`tests.6`; Task notes 3.2). Verify `tests/suite t-briefs` ends with "0 failed".

## 4. README

- [x] 4.1 README says the design agent posts a record's card under its record key, the card's form, how it is recorded and where the rail lists it (design.md, D2, D3, D5; Task notes 4.1). Verify `tests/suite t-docs` ends with "0 failed".

## 5. The affected tests

- [x] 5.1 The moon tasks are in step with the tests and the affected tests pass. Verify `tests/moon-tasks` leaves `tests/moon.yml` unchanged, and `tests/suite --affected` ends with "0 failed".

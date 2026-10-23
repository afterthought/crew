# Tasks

## 1. crew reads the user's yes before it records a record settled in the pane

- [x] 1.1 `settled_refusal` refuses any caller but the design agent and any words crew does not read as the user's, naming who said them and pointing at the record's card. It shares its verdict half with `pane_answer_refusal`, whose words stay as they are (design, Decision 2; Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_cards.py` and `tests/py/test_batch_answer.py`.
- [x] 1.2 `crew record … --proposed --settled-in-pane --excerpt "<words>"` reads the words in the design agent's own transcript on this host before it reads the kit, refuses either flag without the other, and records the settled record naming the transcript record and the words' length, never the words (design, Decisions 1 to 3; Task notes 1.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_cards.py`.
- [x] 1.3 End to end, a record settled with the user's own words is recorded with no card, and one given another agent's tell of the user's words is refused with nothing recorded (design, Decision 3; Task notes 1.3). Verify `tests/suite t-cards` ends with "0 failed".

## 2. The brief and the docs say it

- [x] 2.1 The design agent's brief says to pass the user's yes as they wrote it and to raise the card when crew refuses it, and the usage, README and SKILL.md name `--excerpt` (design, Decision 4; Task notes 2.1). Verify `tests/suite t-briefs t-docs` ends with "0 failed".
- [ ] 2.2 The tests this change affects pass. Verify `tests/suite --affected` ends with "0 failed".

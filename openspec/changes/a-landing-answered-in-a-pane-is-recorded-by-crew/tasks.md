# Tasks

## 1. crew reads the word to land as the user's

- [ ] 1.1 A batch's and a landing's pane words are refused by one verdict check, `heard_refusal`, and every batch refusal reads as before (design, Decision 2; Task notes 1.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_batch_answer.py`.
- [ ] 1.2 `submit_word_refusal` passes only words crew reads as the user's, and names who said any others, holding none of the words (design, Decision 2; Task notes 1.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_pane_landing.py`.

## 2. `crew bolt submit --excerpt` records the word

- [ ] 2.1 `crew bolt submit <bolt> --excerpt "<words>"` refuses before anything is submitted unless the words are the user's in the caller's own transcript, records the landing's `bolt.submit` with the transcript record and the words' length and no words, and keeps the words on its host for `crew bolt land` (design, Decisions 1, 3 and 4; Task notes 2.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_parser.py` and `tests/py/test_pane_landing.py`.
- [ ] 2.2 A landing on the user's words is read from its `bolt.submit` entry, and its words are read back only when the kept file matches it (design, Decisions 3 and 4; Task notes 2.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_pane_landing.py`.

## 3. The landing card closes naming the words

- [ ] 3.1 The close of a landing on the user's words sends the word and the words first, and records the outcome without them, or names the pane and time when the words can't be read back (design, Decision 5; Task notes 3.1). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_landing.py`.
- [ ] 3.2 A waiting card closed as answered in a conversation is cancelled with Pending You's `answeredHere` and recorded closed (design, Decision 5; Task notes 3.2). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_cards.py`.
- [ ] 3.3 `crew bolt land` of a bolt landed on the user's words closes its card on the team's host with those words, answered here, and removes the kept words (design, Decision 5; Task notes 3.3). Verify `devenv shell -- moon run tests:logic` passes `tests/py/test_card_commands.py`, and `tests/suite t-journey-land` ends with "0 failed".

## 4. The brief and the docs say it

- [ ] 4.1 Main-level ops's brief says to pass the user's words with `--excerpt` when the word to land came in its pane, and that a refusal is no word to land; the usage, README and SKILL.md name the flag (design, Decision 6; Task notes 4.1). Verify `tests/suite t-briefs t-docs` ends with "0 failed".
- [ ] 4.2 The tests this change affects pass. Verify `tests/suite --affected` ends with "0 failed".

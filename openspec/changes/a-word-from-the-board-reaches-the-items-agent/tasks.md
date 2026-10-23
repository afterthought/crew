# Tasks

## 1. The word, its agent and what it answers

- [x] 1.1 Every dock page names the agent its word goes to, by its item's kind and the team holding its bolt, else the partition's operator (design, Decision 1; Task notes 1.1); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".
- [x] 1.2 `crew tell --board` reads the posted word on its standard input, refuses any word not of the form, partition, kind, agent or length it checks, and tells the agent `[crew tell from <user>@board] (on <kind> <name>) <text>`, printing `sent to <agent>`; every brief says what a tell from the board is; the usage header names the command (design, Decisions 1, 2, 3, 5 and 7; Task notes 1.2); passes `tests/py/test_board_word.py`, verify `tests/suite logic` ends with "0 failed".
- [ ] 1.3 Words that reached an agent only in a tell from the board are read as the user's but refused as the words of a landing, a batch's answer or a record settled in a pane, and the same words typed in the pane still count (design, Decision 4; Task notes 1.3); passes `tests/py/test_transcript.py` and `tests/py/test_board_word.py`, verify `tests/suite logic` ends with "0 failed".

## 2. The word in the dock

- [ ] 2.1 Every dock ends with a one-line field and Send naming its agent and saying a card is answered on the rail, posts the word to the page's own address as its one request, says what came back or that the listener did not answer, and sends nothing from a page opened from disk (design, Decision 6; Task notes 2.1); passes `tests/py/test_page.py`, verify `tests/suite logic` ends with "0 failed".

## 3. Wiring and docs

- [ ] 3.1 A word piped to `crew tell --board` reaches the planner's pane marked from the board and naming the item, records its length and not its text, and a word for an agent its kind does not go to types nothing (design, Decision 2; Task notes 3.1); verify `tests/suite t-journey-main` ends with "0 failed".
- [ ] 3.2 README and the crew skill say how a dock's word reaches the item's agent and what a tell from the board is and answers (design, Context; Task notes 3.2); verify `tests/suite t-docs` ends with "0 failed".
- [ ] 3.3 The tests the change affects pass: verify `tests/suite --affected` ends with "0 failed".

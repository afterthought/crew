# Tasks

Each check is a moon task of the `tests` project, run through `tests/suite`: `logic` is `tests:logic`. Build the groups in order. Submit nothing, and never run `wt submit --help`.

## 1. Every card field within Pending You's budgets, in one table

- [x] 1.1 The one budget table in `cards.py` holds a step's words (`STEP`), a card's about title (`ABOUT`) and a change note (`NOTE`), each with its source, and no cut to a Pending You bound in `cards.py` or `plan.py` names a bare number (design Decision 4; Task notes 1.1). Passes `tests/py/test_cards.py` and `tests/py/test_card_commands.py` (`tests/suite logic`).
- [x] 1.2 Every action step is built by `cards.step`, its words within `STEP` and its command whole: a command past the budget says "Run this command.", and a gate's link past it says to open the gate at the card's link (design Decision 3; Task notes 1.2). Passes `tests/py/test_cards.py` (`tests/suite logic`).
- [x] 1.3 A user's step of any length gets its card with its words whole: its step its first whole sentences, its title cut at whole words, and its face the words as Markdown when nothing else holds them whole (design Decisions 1, 2 and 5; Task notes 1.3). Passes `tests/py/test_cards.py` (`tests/suite logic`).
- [x] 1.4 A held step's title ends with its question within `TITLE`, and its face holds the words when the title cut them (design Decision 5; Task notes 1.4). Passes `tests/py/test_cards.py` (`tests/suite logic`).
- [x] 1.5 A card changed in place carries no face its new version lacks (design Decision 6; Task notes 1.5). Passes `tests/py/test_cards.py` (`tests/suite logic`).

## 2. Through a Pending You that refuses past the bound

- [x] 2.1 A 370-character step with no commands, posted on a fake that refuses a step of 300 characters or more, is posted with its words whole, and a step's card still refused is recorded in Pending You's words for its row's card line (design Decision 7; Task notes 2.1). Passes `tests/py/test_card_commands.py` (`tests/suite logic`).
- [x] 2.2 The stub Pending You refuses a post or an update with a step of 300 characters or more in Pending You's words (`tests.4`; Task notes 2.2). Verify `tests/suite t-cards t-journey-ops` ends with "0 failed".

## 3. The tests the change affects

- [x] 3.1 Verify `tests/suite --affected` ends with "0 failed".

# Tasks

## 1. Pending You's ended statuses

- [ ] 1.1 crew reads `resolved`, `cancelled` and `expired` as ended, recording `resolved` closed and the other two withdrawn, and changing and closing a card so reported sends nothing more, proved by the logic cases in `tests/py/test_cards.py` (design: decision 1; Task notes 1.1; `read.2`, `code.7`).
- [ ] 1.2 crew can tell, from the run record's entries alone, under which key an owner's card a new post follows is still open, proved by logic cases in `tests/py/test_cards.py` (design: decision 2; Task notes 1.2; `code.7`, `state.2`).

## 2. A card picked up by the card that follows it

- [ ] 2.1 A post that follows a card the record holds open reads that card once posted and records it closed when Pending You has ended it, the post standing whatever the read gives, proved by logic cases in `tests/py/test_card_commands.py` (design: decision 2; Task notes 2.1; `briefs.16`, `read.1`, `record.1`).
- [ ] 2.2 mac-studio's sequence of 2026-10-19 runs to a deploy card closed at its step's post, a deploy end that sends nothing, and a new card for the next offer, proved by its reproducing logic case in `tests/py/test_cards.py` (design: decision 3; Task notes 2.2; `tests.4`, `plan.14`).

## 3. A question already ended

- [ ] 3.1 Withdrawing a question whose asker has ended records a question Pending You already ended as closed and sends no `cancel_request`, proved by a logic case in `tests/py/test_rail.py` (design: decision 4; Task notes 3.1; `briefs.11`).

## 4. The stub, and the suite

- [ ] 4.1 The stub pendingyou picks up the answered card a post follows and refuses to cancel a card already ended, in Pending You's words, as Pending You does (design: decision 5; Task notes 4.1; `tests.4`).
- [ ] 4.2 `tests/suite logic` and then `tests/suite --affected` each end "0 failed" (Task notes 4.2; `tests.5`, `tests.12`).

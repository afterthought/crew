# Tasks

## 1. A row's card built from its row

- [ ] 1.1 `plugin/lib/cards.py` builds each row's card from its row and the agent's words, as the design's first decision says, refusing words or fields the row does not take. Logic cases in `tests/py/test_cards.py` replace the form cases, and `tests/suite logic` ends with "0 failed" (`briefs.9`, `briefs.13`, `code.7`).
- [ ] 1.2 `crew card post` takes the row's words and posts the built card, and no longer loads the hook. `crew card post --lost` posts a lost card again with its dead-copy line (design: *The lost card*).

## 2. The hook refuses an agent's own card calls

- [ ] 2.1 `plugin/hooks/cards` refuses a crew agent's `post_request`, `update_request`, `cancel_request`, `ack_answer` and `create_area`, naming the command, and lets reads through. Its form checks and PostToolUse half go, and `plugin/hooks/hooks.json` matches only the refused calls (`roles.3`, `briefs.16`).

## 3. The briefs

- [ ] 3.1 `crew.py` `cards_how` and `lost_card_how`, and the *Cards* sections of `conductor.md`, `planner.md`, `design.md` and `main-ops.md`, use `crew card post|change|close|read` and name no Pending You tool for a card. They hear an answer as test card 2 decided. `tests/t-briefs.sh` pins the words, and `tests/suite t-briefs` ends with "0 failed" (`briefs.16`, `tests.6`).

## 4. The tests

- [ ] 4.1 `tests/t-journey-review.sh` posts and closes its cards through `crew card` on the stub and shows an agent's own `post_request` refused. `tests/moon-tasks` is run, and `tests/suite --affected` ends with "0 failed" (`tests.1`, `tests.10`).

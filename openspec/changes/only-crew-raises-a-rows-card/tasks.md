# Tasks

## 1. Hearing

- [ ] 1.1 Every post prints the card's id and `call get_request (requestId <id>, name <role>)`, and a card raised outside its owner's turn, a landing found on a rail read or the deployer's offer, sends the owner that line with `crew tell`; `crew card read <key>` prints a card's state and closes a declined approval with the user's words. Logic: `tests/py/test_card_commands.py`, the line, whom it is told to, the answer read and the decline's close. Journey: `tests/t-cards.sh` (`briefs.16`, `state.4`).

## 2. The hook and the question

- [ ] 2.1 `plugin/hooks/cards --before` refuses a post, change or close from a role other than the four, under a row's key, and an area under any key but the kit's, and lets the rest through; the after-hook records each act with its id and key, an unreadable reply as unread. `FORMS`, `form_check`, `form_refusal`, `proposal_form` and `KEYS` go; `hooks.json` still runs the hook before every Pending You tool, and its name check, `name_refusal` with `TestNames`, stays as it is (`briefs.17`). Logic: `tests/py/test_cards.py` `TestKeys`, `TestResult` and `TestNames`, the scenarios of "A crew agent's Pending You call names only the agent itself". Journey: `tests/t-cards.sh`, a coder's post refused and a conductor's question posted and recorded (`roles.3`, `briefs.11`, `briefs.16`).

## 3. The briefs

- [ ] 3.1 `crew.py` `cards_how` is the question discipline and the hearing; `lost_card_how` goes; the *Cards* sections of `conductor.md`, `planner.md`, `main-ops.md` and `design.md`, and the stage roles' words on `crew needs`, say what the design's third decision says; `design.md` says a record whose decision a rule of the user's made between alternatives names them, the rules and each loosened, in a file `crew record --alternatives` takes, never settled silently; the planner's `Do` lines carry each new unit's direction for the card. Journey: `tests/t-briefs.sh` pins the words of each (`tests.6`, `briefs.11`, `briefs.15`).

## 4. Commands and docs

- [ ] 4.1 `crew plan card` and `crew card post|change|close` are removed from `plugin/bin/crew`, its usage header, README and `plugin/skills/crew/SKILL.md`; `crew record` and the kept `crew card read|wait|session|end` are in all three. Journey: `tests/t-docs.sh` (`docs.2`).

## 5. The suite

- [ ] 5.1 `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).

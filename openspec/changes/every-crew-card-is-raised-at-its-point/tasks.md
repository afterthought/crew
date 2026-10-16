# Tasks

## 1. The builders

- [ ] 1.1 `plugin/lib/cards.py` builds the proposal, batch, landing, deploy, step and record cards from facts, as the design's first decision says, the proposal's taking over `card_model`'s drawing. Logic: `tests/py/test_cards.py`, one case per scenario of the rail-cards delta's six form requirements, and `tests/py/test_proposal_card.py` as it stands (`code.7`, `briefs.13`).
- [ ] 1.2 The words rule in the builders: prose cut at whole sentences to the budget; a list the user scans as a text artifact on the face, one a line, at most forty characters; the artifacts the picture, inline Markdown, a text list, a link and a step's commands; each builder taking the card it follows and setting `follows`. Logic: `tests/py/test_cards.py`, the scenarios of "A card's words are the document's own" and "A card's document is inline Markdown" (`briefs.9`).
- [ ] 1.3 The proposal's card is one checkbox list, every row of the change a box set as proposed, a hold-to-approve when it has no unit rows, titled "Plan change to …" with no number, a paragraph per new and dropped unit on its face; `picture.py` draws at twice the pixel density, 1560 wide. Logic: `tests/py/test_proposal_card.py`, the scenarios of "The card is one checkbox list" and "A proposal's card is drawn from the plan and the proposal" (`briefs.13`, record 0018 as amended by record 0031 §5).

## 2. Raised, changed and closed at the event

- [ ] 2.1 `crew plan propose`, `--replaces`, `agree`, `approve` and `drop` post, change and close the proposal's card under `proposal/<n>` of the chain; a refused post is recorded and the rail shows it. Logic: `tests/py/test_proposal_life.py`, the chain's key and which act each step makes. Journey: `tests/t-cards.sh` on the stub pendingyou (`plan.4`, `briefs.11`).
- [ ] 2.2 `crew review --wait` starts the batch's session and posts its card when the reviewer's summary is delivered; `crew card wait batch/<n>` prints the notes and closes the card on the tap or the session's send. Logic: `tests/py/test_batches.py`. Journey: `tests/t-cards.sh` (`briefs.12`).
- [ ] 2.3 The merge's end and the rail read post the landing card when the bolt reads proven, change it when the head moves, `crew fix` withdraws it on a defect, `crew bolt land` closes it. Logic: `tests/py/test_landing.py` and `tests/py/test_rail.py` `TestRows`, when a bolt reads proven and which act follows. Journey: `tests/t-journey-land.sh` (`plan.16`, record 0025).
- [ ] 2.4 `crew ops offer <env> <sha> [--notes <file>] [--steps <file>]` posts or changes the deploy's card with the kit's release notes and the range's steps on its face, following the landing card that put the head on main, and tells main-level ops its id; `crew ops record --act end` closes it with the outcome; `crew ops step` posts a user's or a held step's card, one at a time, each following the one before, and closes it on done or declined. Logic: `tests/py/test_ops.py` `TestRows`, the held step's row and words, the notes handed and the offer with none, the one-at-a-time chain. Journey: `tests/t-journey-ops.sh` (`plan.14`).
- [ ] 2.5 `crew record <kit> <n> --proposed|--accepted|--rejected [--settled-in-pane] [--alternatives <file>]` records the status, raises the card unless settled in the pane, as a choice when a rule decided, closes it on accepted or rejected, and refuses a status the file does not hold or an alternatives file it cannot read. Logic: `tests/py/test_cards.py`, the record builder's two forms and the refusals. Journey: `tests/t-cards.sh` (`briefs.15`).
- [ ] 2.6 `crew card read <key>` prints a card's state and closes a declined approval with the user's words; every post prints the card's id and the hold line. Logic: `tests/py/test_card_commands.py`, the answer read and the decline's close. Journey: `tests/t-cards.sh`.

## 3. The hook and the question

- [ ] 3.1 `plugin/hooks/cards --before` refuses a post, change or close from a role other than the four, under a row's key, and an area under any key but the kit's, and lets the rest through; the after-hook records each act with its id and key, an unreadable reply as unread. `FORMS`, `form_check`, `form_refusal`, `proposal_form` and `KEYS` go; `hooks.json` matches the five tools. Logic: `tests/py/test_cards.py` `TestKeys` and `TestResult`. Journey: `tests/t-cards.sh`, a coder's post refused and a conductor's question posted and recorded (`roles.3`, `briefs.11`, `briefs.16`).

## 4. The sweep and the lost card

- [ ] 4.1 The rail read withdraws a row's card whose row is gone and a question whose asker herdr no longer lists, and posts again an open row's card that reads not found after the host signed in anew; `crew board` writes nothing. Logic: `tests/py/test_rail.py` `TestSweep`. Journey: `tests/t-cards.sh` (`read.4`, `state.4`).

## 5. Sessions

- [ ] 5.1 A session is started by crew for a batch and a long proposal alone, when the card is raised; `crew card session` prints a running link again and refuses other keys; the session ends on crew's close and on the sweep. Logic: `tests/py/test_cards.py` `TestSessions`. Journey: `tests/t-cards.sh` (`briefs.9`).

## 6. The briefs

- [ ] 6.1 `crew.py` `cards_how` is the question discipline and the hearing; `lost_card_how` goes; the *Cards* sections of `conductor.md`, `planner.md`, `main-ops.md` and `design.md`, and the stage roles' words on `crew needs`, say what the design's eighth decision says; `design.md` says a record whose decision a rule of the user's made between alternatives names them, the rules and each loosened, in a file `crew record --alternatives` takes, never settled silently; the planner's `Do` lines carry each new unit's direction for the card. Journey: `tests/t-briefs.sh` pins the words of each (`tests.6`, `briefs.11`, `briefs.15`).

## 7. The rail and the board

- [ ] 7.1 `crew rail` prints each row's card id and state, the open questions after its groups, and what the sweep did; `board.agent_views` gives each agent its open cards and `status.js` draws them. Logic: `tests/py/test_rail.py` `TestText`, `tests/py/test_board.py`. Mod: `plugin/tests/` through `tests/mod`. Journey: `tests/t-journey-board.sh` (`code.8`).

## 8. Commands and docs

- [ ] 8.1 `crew plan card` and `crew card post|change|close` are removed from `plugin/bin/crew`, its usage header, README and `plugin/skills/crew/SKILL.md`; `crew record` and the kept `crew card read|wait|session|end` are in all three. Journey: `tests/t-docs.sh` (`docs.2`).

## 9. The suite

- [ ] 9.1 `tests/t-card-commands.sh` becomes `tests/t-cards.sh` with the journeys above; `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).

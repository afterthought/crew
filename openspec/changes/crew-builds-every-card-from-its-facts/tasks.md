# Tasks

## 1. The builders

- [ ] 1.1 `plugin/lib/cards.py` builds the proposal, batch, landing, deploy, step and record cards from facts, as the design's first and fourth decisions say, the proposal's taking over `card_model`'s drawing. Logic: `tests/py/test_cards.py`, a case for each scenario of "A deploy's card is a high approval", "Landing is approved only by holding the button" and "A batch's card names every unit and links its session", and for each form the fourth decision gives the landing, the step and the record, and `tests/py/test_proposal_card.py` as it stands (`code.7`, `briefs.13`).
- [ ] 1.2 The words rule in the builders: prose cut at whole sentences to the budget; a list the user scans as a text artifact on the face, one a line, at most forty characters; the artifacts the picture, inline Markdown, a text list, a link and a step's commands; each builder taking the card it follows, as `follows_of` reads it from the run record, and setting `follows`. Logic: `tests/py/test_cards.py`, the scenarios of "A card's words are the document's own", "A card's document is inline Markdown" and "No card of crew's asks a question in words" (`briefs.9`).
- [ ] 1.3 The proposal's card is one checkbox list, every row of the change a box set as proposed, a hold-to-approve when it has no unit rows, titled "Plan change to …" with no number, a paragraph per new and dropped unit on its face; `picture.py` draws at twice the pixel density, 1560 wide. Logic: `tests/py/test_proposal_card.py`, the scenarios of "A proposal's card is drawn from the plan and the proposal" and "The change reads as text on a phone", and a case for each form of the fourth decision's proposal (`briefs.13`, record 0018 as amended by record 0031 §5).

## 2. The act

- [ ] 2.1 `row_card_post`, `row_card_change` and `row_card_close` post, change, close and withdraw a card of crew's own through `cards.Bridge` under the host's sign-in, in the role's name, under the row's key, uploading a picture as "A card's picture is uploaded" says, filed as "A card says whose it is and where it belongs" says, recording each act on the row's object with the card's id and key and printing them; a refusal, a host not signed in, an unread reply and a card not found are said and recorded as the second decision says, and refuse nothing of the event. Logic: `tests/py/test_card_commands.py`, the scenarios of "crew's card commands refuse what they cannot do, in the words that say why" and what the act sends and records for each, on a stand-in for the Bridge (`code.2`, `code.7`, `read.1`, `read.2`).

## 3. Hearing

- [ ] 3.1 Every post prints the card's id and `call get_request (requestId <id>, name <role>)`, and a card raised outside its owner's turn, a landing found on a rail read or the deployer's offer, sends the owner that line with `crew tell`; `crew card read <key>` prints a card's state and closes a declined approval with the user's words. Logic: `tests/py/test_card_commands.py`, the line, whom it is told to, the answer read and the decline's close. Journey: `tests/t-cards.sh` (`briefs.16`, `state.4`).

## 4. The suite

- [ ] 4.1 `tests/t-card-commands.sh` becomes `tests/t-cards.sh`, its journeys as they are, the journey the series' later changes add their cards to; `tests/moon-tasks` is run and `tests/moon.yml` committed; `tests/suite --affected` ends with "0 failed" (`tests.10`, `tests.11`).

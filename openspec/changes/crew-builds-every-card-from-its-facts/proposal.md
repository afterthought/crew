# crew builds every card from its facts

## Why

Record 0031 (accepted 2026-10-14, the card elaboration session; §5 amended 2026-10-15 in the card trials) settles crew's cards as one design: six cards are crew's own, each raised by crew at a fixed point of its process in the name of the role whose row it is, and an agent's question is the one open card, asked by four roles in their own name. Today every card is built by hand by the agent whose row it is, from Pending You's guide, and crew's hook refuses the ones that drift: no landing card has posted since 2026-10-11 for a flag the service refuses, 40 of 281 cards in six days had no key, agents posted second cards for the same thing under new keys, and cards nobody closed left eight plannotator sessions running. The user: "we program the cards into the Python code and then we need to define exactly what that list of cards is and what we think the contents of the card should be"; "Obviously we should have templates and/or common functions in Crew that generate cards consistently"; and, on a question an agent has, "My goal isn't to prevent agents from also using pendingyou."

The record is built as a series of eight changes, each built and landed on its own. This one is the ground the other seven stand on: every card's form, built by code from the facts of its event, and the one act through which crew posts, changes and closes its cards. It raises no card at any event; the changes after it do.

## What Changes

- **Six builders**, one for each of crew's cards, the record, the proposal, the batch, the landing, the deploy and the step, each a function of plain facts that returns what Pending You's `post_request` takes, and for a change what `update_request` takes, in the form the card trials settled with the user.
- **The words rule**: prose cut at whole sentences to Pending You's budget; a list the user scans as a text artifact on the face, one thing a line, at most forty characters; a document's substance as inline Markdown; a link as a `url` artifact; the details holding only what the face cannot.
- **`follows`**: each card names the card its thing follows, read from the run record, so one thing's chain reads as one thread on the phone.
- **The picture** of a proposal drawn at twice the pixel density, 1560 pixels wide.
- **One act** posts, changes and closes a card of crew's own through the fleet's `pendingyou mcp`, under the host's sign-in, in the role's name, under the row's key; a refusal, a host not signed in, an unread reply and a lost card are each said and recorded, and none refuses the event the card was raised for.
- `tests/t-card-commands.sh` becomes `tests/t-cards.sh`, the journey every later change of the series adds its card to.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the deploy's form; whose name a card is asked in; the landing's hold; the words, the Markdown, the picture and the batch's links of every card crew builds; how a card act that fails is said.
- `plan-proposals`: the proposal's card drawn by crew, its picture at twice the density, and its change as text.

## Impact

- Follows no change of the series. `a-landing-cards-stakes-are-its-approvals-risk` (crw-3's) lands before it as it is: its `approve` of risk high is the landing builder's form. It rests on `units-build-at-once-and-are-reviewed-in-batches`, `a-batch-cards-notes-are-its-note-and-its-sessions`, `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`, `an-image-on-a-card-is-uploaded`, `a-cards-session-ends-with-its-card`, `a-card-lost-to-its-owner-is-posted-again` and `a-record-is-accepted-on-the-users-yes`, all archived, so their deltas are in `openspec/specs/`.
- The series, in order: this change; then `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards`, `crew-record-raises-a-records-card` and `the-rail-shows-and-sweeps-every-card`, each following this one alone and built side by side; then `crew-raises-a-bolts-landing-card`, which follows this one and the rail's and waits on the record of who keeps which folders; and last `only-crew-raises-a-rows-card`, which follows all.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`). The host's sign-in, the account folders' logins and the doctor's row are swancloud's (`openspec/explorations/cards/swancloud.md`).

## Touches

```
plugin/lib/cards.py
plugin/lib/picture.py
plugin/lib/plan.py
tests/py/test_cards.py
tests/py/test_proposal_card.py
tests/py/test_card_commands.py
tests/t-card-commands.sh
tests/t-cards.sh
tests/moon.yml
```

`cards.py` gains the builders `proposal_card`, `batch_card`, `landing_card`, `deploy_card`, `step_card` and `record_card`, the words rule's `prose`, `text_list`, `markdown` and `link`, and `follows_of`; `picture.py` changes `char`, `layout` and `draw` to twice the density. `plan.py` gains the act, `row_card_post`, `row_card_change` and `row_card_close`, and changes no function it has: `card_model`, `crew plan card` and the card hook's `proposal_form` keep today's proposal card until the series' proposal and last changes replace them. `tests/t-card-commands.sh` is renamed `tests/t-cards.sh` with its journeys as they are; `tests/moon.yml` is regenerated.

# Only crew raises a row's card

## Why

Record 0031 leaves an agent one card of its own, a question, asked by four roles in their own name, and makes every other card crew's. Once the series' earlier changes raise each of the six at its event, what remains is to end the old path: crew's hook still checks a copy of each row's form and refuses a question under any key but a row's, the briefs still tell each agent to build and post its row's card, and `crew plan card` and `crew card post|change|close` still serve them. The user, on a question an agent has: "My goal isn't to prevent agents from also using pendingyou"; and on the command the reading proposed instead of Pending You's own tools: "this seems limiting. It would prevent the agent from having the flexibility to customize the card how they want using the MCP tool."

## What Changes

- **A question is the asker's.** A conductor, the planner, main-level ops and the design agent ask through Pending You's own tools in their sessions, under a key of their own. crew's hook refuses a post, change or close under a row's key and from any other role, lets the rest through, and records each on the rail; its check that every Pending You call names only the agent itself (`briefs.17`) stays as it stands, first, on every tool. A stage agent asks through `crew needs`.
- **The briefs** carry the question discipline: the chain of command for a question, Pending You's test for what is the user's, a good question's fields and the key of its own; the stage agents' say they post none and ask their conductor by `crew needs`. What each owner's *Cards* section says of its own card came with that card's change.
- `crew plan card` and `crew card post|change|close` go; README, the crew skill and `crew`'s usage header follow (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: crew raises every row's card and no agent does; one card per thing, changed in place and closed by crew; the question's checks and record; a crew agent's call in its own name alone; the hook's scope.
- `plan-proposals`: no `crew plan card`.

## Impact

- Follows every change of the series: `crew-builds-every-card-from-its-facts`, `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards`, `crew-record-raises-a-records-card`, `crew-raises-a-bolts-landing-card` and `the-rail-shows-and-sweeps-every-card`.
- Supersedes `every-crew-card-goes-through-crew` (archived as superseded) and crw-3's unit `any-question-for-the-user-gets-a-card` (dropped, its branch kept, `plan.10`).
- The question discipline takes effect at each standing agent's next fresh start. Cards open when this lands are closed by the sweep as their rows end; none is re-posted in the new form.

## Touches

```
plugin/hooks/cards
plugin/lib/plan.py
plugin/lib/crew.py
plugin/lib/cards.py
plugin/lib/ops.py
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/roles/main-ops.md
plugin/roles/design.md
plugin/roles/ops.md
plugin/roles/dispatcher.md
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_cards.py
tests/py/test_card_commands.py
tests/py/test_chores.py
tests/py/test_proposal_card.py
tests/py/test_proposal_life.py
tests/py/test_rail.py
tests/py/test_review.py
tests/t-cards.sh
tests/t-briefs.sh
tests/t-docs.sh
tests/t-journey-ops.sh
tests/t-journey-plan.sh
tests/t-journey-review.sh
tests/moon.yml
```

The card hook loses `KEYS`, `FORMS`, `form_check`, `form_refusal` and `proposal_form` and changes `check`, `refusal`, `key_refusal` and `posted`, keeping `name_refusal` and `callers` as they stand and `refusal` running the name check first; `hooks.json` keeps its matcher, `mcp__.*[Pp]ending.*[Yy]ou.*__.*`. `plan.py` changes `card_refusal`, `CARD_KEYS` (the old keys out), the rail's sweep words, `parser` and `main`; it loses `CardReads`, `card_post`, `card_change`, `card_close`, `plan_card`, `card_model`, `close_card` and the notices that name a card to close (`notices`, `lost_rows`), and `cards.py` and `ops.py` what only those read. `crew.py` rewrites `cards_how`, which the conductor's and the planner's *Cards* and main-level ops's and the design agent's *Asking the user* draw in, and `needs_how`, which the stage roles draw in, and loses `lost_card_how`, whose `{{LOST_CARD}}` leaves `main-ops.md`; a team's ops's and the dispatcher's briefs say they post no card and whom they ask; `tests/moon.yml` is regenerated.

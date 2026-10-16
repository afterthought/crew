# Only crew raises a row's card

## Why

Record 0031 leaves an agent one card of its own, a question, asked by four roles in their own name, and makes every other card crew's. Once the series' earlier changes raise each of the six at its event, what remains is to end the old path: crew's hook still checks a copy of each row's form and refuses a question under any key but a row's, the briefs still tell each agent to build and post its row's card, and `crew plan card` and `crew card post|change|close` still serve them. The user, on a question an agent has: "My goal isn't to prevent agents from also using pendingyou"; and on the command the reading proposed instead of Pending You's own tools: "this seems limiting. It would prevent the agent from having the flexibility to customize the card how they want using the MCP tool."

## What Changes

- **A question is the asker's.** A conductor, the planner, main-level ops and the design agent ask through Pending You's own tools in their sessions, under a key of their own. crew's hook refuses a post, change or close under a row's key and from any other role, lets the rest through, and records each on the rail; its check that every Pending You call names only the agent itself (`briefs.17`) stays as it stands, first, on every tool. A stage agent asks through `crew needs`.
- **Hearing.** Every post prints `call get_request (requestId req_…, name <role>)`, the call by which the owner adopts the card and the fleet's wake mod wakes it on the answer; a card raised outside its owner's turn, a landing found on a rail read or the deployer's offer, is told to the owner with that line by `crew tell`; at a fresh start the owner adopts each open card `crew rail` names; `crew card read <key>` gives a card's state and closes a declined approval with the user's words. No watcher and no webhook: the rail's sweep is the catch for a card no owner adopted.
- **The briefs** say all of it: each role's *Cards* section names what crew raises for it, how it hears, and the chain of command for a question; the stage agents' and the operator's say they post none.
- `crew plan card` and `crew card post|change|close` go; README, the crew skill and `crew`'s usage header follow (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: crew raises every row's card and no agent does; one card per thing, changed in place and closed by crew; the question's checks and record; a crew agent's call in its own name alone; the hook's scope; how an owner hears.
- `main-level`: the design agent's record accepted and revised through `crew record`.
- `plan-proposals`: no `crew plan card`.

## Impact

- Follows every change of the series: `crew-builds-every-card-from-its-facts`, `crew-raises-a-proposals-card`, `crew-raises-a-batchs-card-with-its-session`, `crew-raises-the-deploy-and-step-cards`, `crew-record-raises-a-records-card`, `crew-raises-a-bolts-landing-card` and `the-rail-shows-and-sweeps-every-card`.
- Supersedes `every-crew-card-goes-through-crew` (archived as superseded) and crw-3's unit `any-question-for-the-user-gets-a-card` (dropped, its branch kept, `plan.10`).
- The briefs take effect at each standing agent's next fresh start. Cards open when this lands are closed by the sweep as their rows end; none is re-posted in the new form.

## Touches

```
plugin/hooks/cards
plugin/hooks/hooks.json
plugin/lib/plan.py
plugin/lib/crew.py
plugin/roles/
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_cards.py
tests/py/test_card_commands.py
tests/t-cards.sh
tests/t-briefs.sh
tests/t-docs.sh
tests/moon.yml
```

The card hook loses `KEYS`, `FORMS`, `form_check`, `form_refusal` and `proposal_form` and changes `check`, `refusal`, `key_refusal` and `posted`, keeping `name_refusal` and `callers` as they stand and `refusal` running the name check first; `hooks.json` keeps its matcher, `mcp__.*[Pp]ending.*[Yy]ou.*__.*`. `plan.py` changes `card_refusal`, `CardReads`, `card_read`, `CARD_KEYS` (the old keys out), `parser` and `main`, and `row_card_post`, which prints the adopting line and tells it to an owner whose turn the card was not raised in; it loses `card_post`, `card_change`, `card_close`, `card_held`, `card_asker`, `plan_card`, `card_model`, `close_card` and the notices that name a card to close (`notices`, `lost_rows`). `crew.py` rewrites `cards_how` and loses `lost_card_how`. Every brief under `plugin/roles/` with a *Cards* section changes; `tests/moon.yml` is regenerated.

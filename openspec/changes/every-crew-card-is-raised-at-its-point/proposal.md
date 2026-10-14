# Every crew card is raised at its point

## Why

Record 0031 (accepted 2026-10-14, the card elaboration session) settles crew's cards as one design: six cards are crew's own, each raised by crew at a fixed point of its process in the name of the role whose row it is, and an agent's question is the one open card, asked by four roles in their own name. Today every card is built by hand by the agent whose row it is, from Pending You's guide, and crew's hook refuses the ones that drift: no landing card has posted since 2026-10-11 for a flag the service refuses, 40 of 281 cards in six days had no key, agents posted second cards for the same thing under new keys, and cards nobody closed left eight plannotator sessions running. The user: "we program the cards into the Python code and then we need to define exactly what that list of cards is and what we think the contents of the card should be"; "Obviously we should have templates and/or common functions in Crew that generate cards consistently"; and, on a question an agent has, "My goal isn't to prevent agents from also using pendingyou."

## What Changes

- **crew builds and raises six cards itself**, each from the facts of its event, by the command that makes or reads the event, under the host's Pending You sign-in and in the role's name: a **record**'s when `crew record <kit> <n> --proposed` runs for a record not settled in the pane; a **proposal**'s when `crew plan propose` accepts it; a **batch**'s when the reviewer delivers the summary of a batch cut at the batch clock and the planner's `crew review --wait` returns; a **landing**'s when the merge that completes a bolt is recorded, or the rail is read, and the bolt reads proven; a **deploy**'s when `crew ops offer` runs; a **step**'s when `crew ops step` records a step whose doer is the user or that is held for the user's word. No agent writes, posts or closes a row's card; `crew plan card` and `crew card post|change|close` go.
- **One card per thing, changed in place.** A proposal rewritten with `--replaces`, a landing or a deploy whose head moved, a record revised: crew changes the one card with a change note. Keys are the thing's: `proposal/<n>` of the chain's first proposal, `batch/<n>`, `land/<bolt>`, `deploy/<env>`, `op/<env>/<n>`, `record/<kit>/<number>`.
- **crew closes each card at the event that ends it**, with its outcome: an approval applied or a proposal dropped, a record accepted or rejected, a batch tapped or its session sent, a bolt landed or held for a fix, a deploy ended or failed, a step done or skipped or done by its agent; a decline is closed with the user's words when the owner reads it. crew withdraws a row's card whose row is gone, and posts an open row's card again after the host signs in anew, the older copy named dead.
- **A question is the asker's.** A conductor, the planner, main-level ops and the design agent ask through Pending You's own tools in their sessions, under a key of their own. crew's hook refuses a post, change or close under a row's key and from any other role, lets the rest through, and records each on the rail; on each rail read crew withdraws a question whose asker's session has ended. A stage agent asks through `crew needs`.
- **Hearing.** crew prints each card's id when it posts one; the owner's session adopts it with the fleet's `pendingyou hold <id>`, which the wake mod answers at once, and is woken by the answer; a card raised outside a session, the deployer's offer, is told to its owner by crew. `crew card read <key>` and `crew rail` give a card's state at a restart.
- **The briefs** say all of it: each role's *Cards* section names what crew raises for it, how it hears, and the chain of command for a question; the stage agents' and the operator's say they post none.
- README, the crew skill and `crew`'s usage header follow (`docs.2`); `board.agent_views` and the mod show each agent's open cards, questions among them (`code.8`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: the six cards raised, changed, closed and re-posted by crew; the question's checks and record; the words rule; the hook's scope.
- `card-sessions`: a session for a batch and a long proposal alone, started by crew with the card, ended by crew's close.
- `plan-proposals`: a proposal's card raised by `crew plan propose`, changed in place by `--replaces`, closed by approve and drop.
- `review-batches`: a batch's card raised by crew when the reviewer delivers its summary, closed on the tap or the session's send.
- `main-level`: the deploy's and the step's cards crew's, the held step; `crew record`.

## Impact

- `plugin/lib/cards.py` (the six builders, the Bridge's post, change and close for crew's own cards), `plugin/lib/plan.py` (propose, approve, drop, review, the merge's end, the rail's read and sweep, `crew record`, `crew card read|wait|session|end`), `plugin/lib/ops.py` (offer, end, step), `plugin/lib/crew.py` (`cards_how` rewritten to the question and the hearing; `lost_card_how` goes), `plugin/hooks/cards` and `hooks.json` (the narrowed hook), `plugin/roles/*.md`, `plugin/lib/board.py` and `plugin/hooks/status.js`, `plugin/bin/crew`, README, `plugin/skills/crew/SKILL.md`; `tests/py/test_cards.py`, `test_card_commands.py`, `test_rail.py`, `test_ops.py`, `test_proposal_card.py`, `test_board.py`, `tests/t-cards.sh` (from `t-card-commands.sh`), `t-journey-land.sh`, `t-journey-ops.sh`, `t-briefs.sh`, `t-docs.sh`, `tests/moon.yml`.
- Supersedes `every-crew-card-goes-through-crew` (archived as superseded) and crw-3's unit `any-question-for-the-user-gets-a-card` (dropped, its branch kept, `plan.10`). `a-landing-cards-stakes-are-its-approvals-risk` lands first as it is: its `approve` of risk high is the landing builder's form.
- Archive first, so their deltas are in `openspec/specs/` when this change's apply: `units-build-at-once-and-are-reviewed-in-batches`, `a-batch-cards-notes-are-its-note-and-its-sessions`, `a-proposals-card-shows-the-change-and-lets-new-units-be-left-out`, `an-image-on-a-card-is-uploaded`, `a-cards-session-ends-with-its-card`, `a-card-lost-to-its-owner-is-posted-again`, `a-record-is-accepted-on-the-users-yes`. Each is built; each archive is a chore.
- The briefs take effect at each standing agent's next fresh start. Cards open when this lands are closed by the sweep as their rows end; none is re-posted in the new form.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`). The host's sign-in, the account folders' logins and the doctor's row are swancloud's (`openspec/explorations/cards/swancloud.md`).

## Touches

```
plugin/lib/cards.py
plugin/lib/plan.py
plugin/lib/ops.py
plugin/lib/crew.py
plugin/lib/board.py
plugin/hooks/cards
plugin/hooks/hooks.json
plugin/hooks/status.js
plugin/roles/
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/
```

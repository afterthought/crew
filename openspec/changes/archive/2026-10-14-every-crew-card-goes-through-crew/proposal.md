# Every crew card goes through crew

> Superseded, never built: archived on 2026-10-14 with its specs untouched. Record 0031, accepted by the user that day, replaces it with the series of changes from `crew-builds-every-card-from-its-facts` to `only-crew-raises-a-rows-card`, where crew raises its own six cards at their events and an agent's question goes through Pending You's own tools.

## Why

The user ruled on 2026-10-12 that crew's own commands are the one way crew's agents handle Pending You cards (`briefs.16`, ADR 0005 as amended that day). `a-card-reaches-the-user-when-the-tools-drop` builds the commands. Until this change the briefs still have agents call Pending You's tools, so three things stay true:

- **Cards still get lost.** A card is still lost when a session loses its tools.
- **Agents still shape the JSON.** Each agent writes its own card, and crew's hook checks crew's idea of each row's form against what the agent wrote. When that idea drifts from Pending You's, every card of the form is refused. The landing card's `highStakes` (signal 2026-10-11-crw-2-conductor-27bc8685/01) and the proposal card's missing `approve` (signal 2026-10-11-crw-3-conductor-ed9b40fc/01) were both found by an agent failing to post.
- **Records still depend on Claude Code's rendering.** crew records a card from Claude Code's rendering of a tool's result.

## What Changes

- **crew builds a row's card from its row.** The agent gives only the words its brief asks for, and crew supplies the rest:
  - **Proposal.** The card `crew plan card <n>` prints.
  - **Landing.** An approval of risk `high`, not reversible, because `irreversible`, whose action is main-level ops landing the bolt, with the proof's steps for the user.
  - **Verify report.** A choice or multi whose options are the conductor's.
  - **Batch.** One notice naming every unit, with its one reading session's link.
  - **Decision record.** An approval of risk `low`, reversible.
  - **For every row.** The kind, the approval, `blocking` false, the link first in its words, no path and no words question.

  The hook's form checks (`FORMS`, `form_refusal`, `proposal_form`) become these builders, and `crew card post` stops loading the hook.
- **crew refuses an agent's own calls.** A crew agent's call to Pending You's `post_request`, `update_request`, `cancel_request`, `ack_answer` or `create_area` is refused before it reaches Pending You, naming the `crew card` command to use (`roles.3`). The hook's PostToolUse half, which recorded those calls, goes. The user's own sessions are untouched.
- **The briefs move to the commands.** The card discipline crew fills into the briefs (`crew.py` `cards_how`, `lost_card_how`), `conductor.md` *Cards*, `planner.md` *Cards*, `design.md` and `main-ops.md` move from Pending You's tools to `crew card post|change|close|read`. An agent no longer calls `whoami`, `list_pending`, `match_area` or `create_area` for its cards.
- **How an agent hears its answer.** The three test cards decide it (ADR 0005 as amended 2026-10-12):
  - If the wake adopts a card on `pendingyou hold <id>`, `crew card post` says to run it, and the wake does the rest.
  - If it does not, the agent reads its answer with `crew card read` when crew's notice or its own breakpoint says to.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`:
  - a row's owner posts, changes and closes its card through `crew card`, and crew builds the row's card in its row's form;
  - crew refuses a crew agent's own Pending You call that posts, changes or closes a card or makes an area;
  - how an agent hears an answer.

## Impact

- `plugin/lib/cards.py`: the builders.
- `plugin/hooks/cards`: the refusal of an agent's own calls. Its form checks and its PostToolUse half go.
- `plugin/hooks/hooks.json`: the matchers.
- `plugin/lib/crew.py`: `cards_how` and `lost_card_how`.
- `plugin/roles/conductor.md`, `planner.md`, `design.md` and `main-ops.md`: the *Cards* sections.
- Tests:
  - `tests/py/test_cards.py`, whose form cases become builder cases;
  - `tests/t-journey-review.sh`, whose hook steps become command steps;
  - `tests/t-briefs.sh`.
- `docs/architecture/_open.md`, once built, by the design agent (`docs.7`).
- **The landing builder.** It takes `a-landing-cards-stakes-are-its-approvals-risk`'s form once that held bolt lands. If this change is built first, its landing builder is that form.
- **The question keys.** `any-question-for-the-user-gets-a-card`, in the same held bolt, adds a conductor's own question keys. `crew card post` takes them as `card_refusal` allows them.
- Every agent takes the new brief at its next fresh start.
- **Before the briefs move:** the host is signed in again on each host that runs agents, and the three test cards have been read.

## Touches

```
plugin/lib/cards.py
plugin/hooks/cards
plugin/hooks/hooks.json
plugin/lib/crew.py
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/roles/design.md
plugin/roles/main-ops.md
tests/py/test_cards.py
tests/t-journey-review.sh
tests/t-briefs.sh
tests/moon.yml
```

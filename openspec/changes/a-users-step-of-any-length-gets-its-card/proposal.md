# A user's step of any length gets its card

## Why

On deneb, on 2026-11-06, crew posted no card for swancloud's after-deploy step `op/deneb/20`. Pending You refused the post with "Keep each step’s words under 300 characters." The step was the Herdr re-sign-in of swancloud's `the-fleets-pendingyou-is-0-41-0`: about 370 characters, with no command fields. The step stayed on the rail as owed, and the user never saw it (signal `afterthought/crew-state:swancloud/main signals/2026-11-06-swancloud-ops-bbe53808/01-herdr-sign-in-step-too-long-for-its-card`).

The cause is in `plugin/lib/cards.py`, `step_card`. A user's step with no commands puts its whole text in as the card's one action step. crew keeps Pending You's other budgets in one table (`TITLE, SUMMARY, DETAIL, LABEL`), but it kept none for a step's words. Pending You's schema states no bound for a step, so only its refusal says it.

## What Changes

- **A step's budget joins the one table.** `cards.STEP` is the most characters an action step's words hold, 299, read from Pending You's refusal. The two hand-written 120s for a card's `about` title and `update_request`'s change note become `ABOUT` and `NOTE` in the same table. No second table is kept anywhere.
- **Every action step crew builds holds to it.** One function, `cards.step`, builds each action step:
  - A step's words that fit are its text, as before.
  - Words that do not fit are replaced by short words that say what to do.
  - A command is never cut: a step whose command is longer than a step holds says "Run this command." with the command whole.
  - A gate's link longer than a step holds says to open the gate at the card's link. The card's *where* is still the link.
- **A user's step of any length gets its card, its words whole.**
  - Its one action step is its words when they fit. Otherwise it is its first whole sentences that fit, or its first sentence cut at whole words.
  - Its title is its words cut at whole words to the title's budget.
  - When neither the title, the step nor the summary holds the words whole, the card's face carries them whole as inline Markdown, titled "The step".
- **A held step's card keeps its question.** Its title cuts the step's words at whole words, so ", now or when the host is quiet?" always ends it within the title's budget. When the title cut the words, the face carries them whole.
- **A card changed in place drops a face it no longer carries.** `update_request` keeps any field a change leaves out. So a change now empties the artifacts of a card that carries none, and the face of a long step goes once the words are recorded again short.
- **A card still refused stays seen.** A post Pending You refuses for any other bound is recorded refused in its words, and the row's card line on the rail shows those words (rail-cards "A row's card that Pending You refused is owed until it posts"). This already holds, and a test now pins it for a step's card.
- **The stub Pending You refuses a step of 300 characters or more** in Pending You's words, on a post and on an update (`tests.4`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: each action step holds to Pending You's budget for a step's words, and a command is never cut. A user's step of any length gets its card with its words whole, on the face when nothing else holds them. A held step's title keeps its question. A gate's link too long for a step is opened at the card's link. A card changed in place drops a face it no longer carries.

## Impact

- `plugin/lib/cards.py`: the budget table, `step`, `step_card`, `change_args`, and the `ABOUT` and `NOTE` budgets.
- `plugin/lib/plan.py`: a close's outcome cut to `cards.NOTE` in place of a bare 120.
- `tests/stubs/pendingyou`: refuses a step of 300 characters or more.
- `tests/py/test_cards.py` and `tests/py/test_card_commands.py`: the cases.
- No change to the views or crew's mod (`code.8`): no bolt, unit, stage, card key or rail row changes shape.

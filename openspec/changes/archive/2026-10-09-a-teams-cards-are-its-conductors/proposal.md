# Proposal

## Why

On 2026-10-09 the user got the same Pending You card twice: brd-2's ops finished its proof with one check left for the user, told the conductor, and posted its own card for it; the conductor, on that tell, posted another; and each made the kit's area under a key of its own, so Pending You could fold neither the cards nor the areas together. Nothing stopped it: the ops brief has no card rule, and crew's card hook records a card under any key without refusing it. The user decided that a team speaks to the user with one voice, its conductor's, and that by `roles.3` crew enforces it with a check rather than firmer words (`docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md` as amended 2026-10-09; `briefs.11`; signal `2026-10-09-swancloud-operator-mac-studio-9539e922/01-ops-and-conductor-both-card-the-user`).

## What Changes

- **ops and every stage agent post no card.** What a proof leaves that only the user can do or check (a check on their Mac, a sign-in, a look at a console) goes in ops's proof file, as a step written for the user to do from a card: where, what to do or paste, and what they will see when it worked. ops tells nobody else and posts nothing. The shared text every stage brief and ops's carry for stopping short says so in one line.
- **The conductor asks that step on the bolt's landing card, as the step before approval.** The landing card is posted when the proof is clean, or clean but for the user's steps. It is still the one high-stakes card keyed `land/<bolt>/<head>`; its title and first words name the step, the step itself is on the card, and approving the card means the user did it, it worked, and the bolt may land. A note saying a step failed is a defect the conductor fixes on the bolt before it asks again. No second card is ever posted for the step.
- **crew refuses a card a crew agent posts under any key but a rail row's of its own.** Before Pending You's `post_request` runs in a session crew started, crew's card hook checks the card's key: the planner may post only `proposal/<n>` for an open proposal of its partition; a conductor only `review/<unit>/<head>` or `verify/<unit>/<stamp>` for a unit of the bolt its team holds, or `land/<bolt>/<head>` for that bolt; every other crew agent no card at all. A refused call never reaches Pending You, and the refusal names the key to use, or, for an agent with no rows, who asks the user instead.
- **crew refuses an area a crew agent makes under any key but `create-area:<owner>/<kit>`.** The same check runs before `create_area`: its key must be `create-area:` and the repository of a kit the agent's cards are filed for. The refusal names that key.
- **What crew cannot read refuses the card.** When the check cannot read the plan or the teams it decides from, the card is refused and the refusal names what could not be read (`read.1`). A session crew did not start, the user's own among them, is never checked.
- **The rules read as built.** `briefs.11` leaves the open-items page, and README says crew refuses a card or an area under another key.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rail-cards`: who may post a card and under which key, what the landing card carries when a proof leaves the user a step, and crew's refusal of any other card or area. (`rail-cards` is written by `the-rail-is-answered-through-cards`, built and not yet archived; this delta is archived after it and after `a-card-links-a-plannotator-session`.)

## Impact

- `plugin/hooks/cards` and `plugin/hooks/hooks.json`: a check before `post_request` and `create_area` that refuses a call, beside the record it already writes after each card act.
- `plugin/lib/plan.py`: which rail rows an agent owns, read from the plan, and the refusal's words; the hook imports it.
- `plugin/lib/crew.py`: the card discipline (`cards_how()`) says crew refuses any other key; the stopping-short text (`needs_how()`) says a stage agent and ops post no card.
- `plugin/roles/ops.md`, `plugin/roles/conductor.md`: the user's steps in the proof file, and on the landing card.
- `docs/architecture/briefs.md`, `docs/architecture/_open.md`, `README.md`.
- Tests: `tests/t-cards.sh` and `tests/t-briefs.sh`.

## Touches

`plugin/hooks/cards`, `plugin/hooks/hooks.json`, `plugin/lib/plan.py` (a new function beside `CARD_KEYS` and `role()`), `plugin/lib/crew.py` (`cards_how()`, `needs_how()`), `plugin/roles/ops.md`, `plugin/roles/conductor.md` (*Cards* and step 5 of the bolt's course), `docs/architecture/briefs.md`, `docs/architecture/_open.md`, `README.md` (the cards paragraph), `tests/t-cards.sh`, `tests/t-briefs.sh`, `tests/moon.yml` (shared: only when a test's reads change), `openspec/specs/rail-cards/spec.md` (by delta).

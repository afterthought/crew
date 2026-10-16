# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give a proposal's card its form and the act that sends it; this change raises, changes and closes it at the proposal's own acts. It relies on `roles.1` (the planner changes the plan only by a proposal the user approves), `roles.2` (an approval runs only on the user's word), `plan.3` and `plan.4` (a proposal is numbered once and closes only as approved or dropped), `briefs.11` and `briefs.13` as record 0031 amends them, record 0018 as amended by record 0031 §5, `code.2`, `code.7` and `state.4`. It touches the area of `plan.md`.

## Goals / Non-Goals

Goals: one card per proposal chain, raised by crew when the proposal is accepted, changed in place at each turn and closed at the act that ends it; the checkbox list applied as the user left it.

Non-goals: the proposal's form, which `crew-builds-every-card-from-its-facts` builds; a long proposal's reading session, which `crew-raises-a-batchs-card-with-its-session` starts with the card; the planner's brief, `crew plan card` and the card hook's proposal form, which `only-crew-raises-a-rows-card` changes and removes.

## Decisions

### 1. The proposal's acts and its card

| Event | Command | Act |
|---|---|---|
| a proposal accepted into the plan | `crew plan propose` | post `proposal/<n>` |
| rewritten | `crew plan propose --replaces <m>` | change the chain's card; the rail's row for `n` carries it |
| a conductor agrees | `crew plan agree` | change ("no longer waits on …") |
| applied, dropped | `crew plan approve`, `crew plan drop` | close with the outcome, or withdraw with the user's reason |

Each act is `raise_proposal`, the proposal's raise: it reads `proposal_facts`, the plan and the proposal as `card_model` reads them, builds the card with the proposal builder and calls the act, `row_card_post`, `row_card_change` or `row_card_close`, after the plan's write is made, so the write never waits on Pending You (`code.9`) and a card Pending You refuses refuses nothing of the proposal: it is in the plan whether its card posted or not, and the rail shows the row with no card and the refusal.

### 2. The chain's key

A proposal chain's card is its first proposal's: `proposal_chain` follows each proposal's `Replaces` back to the first, and its number is the card's key, `proposal/<first>`. `rail_rows` gives the open proposal's row that key, and `CardReads.open_proposals` gives the planner's card check the same keys, so a post the planner makes under its brief until the last change of the series rewrites it is checked against the chain's key. A rewrite changes the chain's card to the successor's title, summary, case, change and boxes, with the change note "Rewritten as proposal <n> after your note"; a proposal rewritten follows nothing.

### 3. Send applies the boxes as they stand

`crew plan answer` gathers every box of the card's one list, and `crew plan approve` applies the change with the boxes as they stand: a new unit or chore unticked is left out, as `--clear` leaves it out today; a dropped unit ticked "Keep <unit>" stays in its bolt; an amended unit ticked "Keep <unit>'s old intent" keeps its intent unamended. The approval's outcome on the card says what was applied and what was kept or left out, and the planner is told which. A hold-to-approve, a proposal with no unit rows, is applied whole.

## Risks / Trade-offs

- Until `only-crew-raises-a-rows-card` rewrites the planner's brief, it still tells the planner to post the proposal's card from `crew plan card`; crew's card is raised first, under the key the planner's card check then names, and the planner's post goes to Pending You under that same key.
- `card_model` and `crew plan card` keep today's card until the last change removes them, so for that time two proposal forms exist in code: crew's, which the user sees, and the old one, which the hook still checks a planner's post against.

# Design

## Context

Record 0031 and `crew-builds-every-card-from-its-facts` give a proposal's card its form and the act that sends it; this change raises, changes and closes it at the proposal's own acts. It relies on `roles.1` (the planner changes the plan only by a proposal the user approves), `roles.2` (an approval runs only on the user's word), `plan.3` and `plan.4` (a proposal is numbered once and closes only as approved or dropped), `briefs.11` and `briefs.13` as record 0031 amends them, record 0018 as amended by record 0031 §5, `code.2`, `code.7` and `state.4`. It touches the areas of `plan.md`, `briefs.md` and `tests.md`.

## Goals / Non-Goals

Goals: one card per proposal chain, raised by crew when the proposal is accepted, changed in place at each turn and closed at the act that ends it; the checkbox list applied as the user left it.

Non-goals: the proposal's form, which `crew-builds-every-card-from-its-facts` builds; a long proposal's reading session, which `crew-raises-a-batchs-card-with-its-session` starts with the card; `crew plan card` and the card hook's proposal form, which `only-crew-raises-a-rows-card` removes.

## Decisions

### 1. The proposal's acts and its card

| Event | Command | Act |
|---|---|---|
| a proposal accepted into the plan | `crew plan propose` | post `proposal/<n>` |
| rewritten | `crew plan propose --replaces <m>` | change the chain's card; the rail's row for `n` carries it |
| a conductor agrees | `crew plan agree` | change ("no longer waits on …") |
| applied, dropped | `crew plan approve`, `crew plan drop` | close with the outcome, or withdraw with the user's reason |

Each act is `raise_proposal_at`, the proposal's raise at its event: `proposal_act` decides from facts alone which act the event makes (`code.7`); the raise reads `proposal_facts`, the plan and the proposal as `card_model` reads them, from the write the event made, builds the card with the proposal builder and calls the act, `row_card_post`, `row_card_change` or `row_card_close`, after the plan's write is made, so the write never waits on Pending You (`code.9`) and a card Pending You refuses, or crew cannot build, refuses nothing of the proposal: it is in the plan whether its card posted or not, and the rail shows the row with no card and the refusal. The card is filed in the area of the kit of the first bolt or unit the proposal's commands name (`named_kit`), from that kit's checkout as the team building it keeps it, else the partition's blueprints.

Only the planner's proposals have a card: a proposal the user writes is theirs already. A rewrite by anyone else of the planner's proposal withdraws the chain's card. A card is reached only from the host that posted it, under that host's sign-in, so a change is made where the card was posted, or on the planner's own host, the partition's main machine, where a change posts the card when none is held; an agreement run on another host that holds none changes nothing there and says so, rather than posting a second card. A close that finds no card on its host closes nothing and says so, and the rail's sweep is the catch.

The rail's sweep raises a proposal row's card that is missing or lost through `raise_proposal(fleet, row, acts=None)`, the entry point every kind's raise gives the sweep: it reads the branch at its tip from the row's label and key, finds the open proposal of the chain the key names (`chain_open`), and raises it through `row_card_change`, which posts it when none is held and posts it again, its summary saying the older copy is dead, when Pending You no longer finds it; a key that is no chain's, or a chain with no proposal open, raises nothing.

### 2. The chain's key

A proposal chain's card is its first proposal's: `proposal_chain` follows each proposal's `Replaces` back to the first, and its number is the card's key, `proposal/<first>`. `open_proposals` gives each open proposal its chain's first, `rail_rows` gives the open proposal's row that key, the board's marker for the proposal follows it (`code.8`), and `CardReads.open_proposals` gives the planner's card check the same keys, so a post the planner makes under its brief until the last change of the series rewrites it is checked against the chain's key. A rewrite changes the chain's card to the successor's title, summary, case, change and boxes, with the change note "Rewritten as proposal <n> after your note"; a proposal rewritten follows nothing.

### 3. Send applies the boxes as they stand

`crew plan answer` gathers every box of the card crew builds for the proposal: its questions are `rows-<k>`, one per list of boxes, answered with the ids of the boxes left ticked (`card_asks`), `rows-1` for a card of one list and for a lone row, which is the choice of its two sides, the row as proposed recommended, since a Pending You list holds two at least (the user, 2026-10-15); a hold-to-approve's is `plan`, approve or decline. Once every question is answered, `crew plan approve` applies the change with the boxes as they stand (`answered`, `as_they_stand`): a new unit or chore unticked is left out, as `--clear` leaves it out; a dropped unit ticked "Keep <unit>" stays in its bolt; an amended unit ticked "Keep <unit>'s old intent" keeps its intent unamended. `crew plan answer` hands the approval the kept units; the command line's `--clear` stays the pane's way to leave a new unit out. The approved proposal records each unit whose row was left out as `Cleared`, and the commit's body names what was left out and what was kept. The approval's outcome on the card says what was applied and what was kept or left out (`approved_words`), and the planner is told which. A hold-to-approve, a proposal with no unit rows, is applied whole.

### 4. The planner's brief

`planner.md` says crew raises a proposal's card when `crew plan propose` accepts it, and changes it at a rewrite and at a conductor's agreement; that the planner adopts it with the line the command prints; how it gathers a proposal's answers (`crew plan answer`, as built) and applies them as they stand with `crew plan approve`; and that its `Do` lines carry each new unit's direction for the card. It posts, changes and closes no proposal card, and no longer runs `crew plan card`. `tests/t-briefs.sh` pins the words (`tests.6`).

## Risks / Trade-offs

- `card_model` and `crew plan card` keep today's card until the last change removes them, so for that time two proposal forms exist in code: crew's, which the user sees, and the old one, which no brief uses and the hook still checks a post against.
- Pending You changes a card only while it waits on the user ("`update_request` works only while the question waits on them"; once they have answered, a new card follows it). A note the user sends on the card answers it, so a rewrite after that note meets an answered card: the rewrite goes through `row_card_change` like any other, and the shared step acks the answered card with the change note and posts the successor's card following it, the run record keeping the row's key.

## After deploy

1. The planner of each partition restarted at a quiet moment, by the dispatcher, since a brief loads at a fresh start and no check can make a running agent reread it; the environments are the two hosts.

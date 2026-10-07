# The rail is answered through Pending You cards

- Status: accepted
- Date: 2026-10-07
- Deciders: the user ("yes, let's do it in a subsequent bolt so we can release the rail first"); swancloud-design
- Sources: `docs/adr/0002` (the rail); recordplane/herdr-pendingyou (the Herdr plugin, 0.2.0) and the `pendingyou` CLI (0.27.0) with the Pending You skill at pendingyou.com/docs/skill, read on 2026-10-07

## Context and problem statement

The rail (`crew rail`) lists what waits on the user, derived from the plan, the proposals and the kits, so nothing kept goes stale. It is a list to read and a shell to paste into; it does not reach the user's phone, and it does not ping. Pending You is a hosted queue of cards that agents post with their own sign-in and the user answers on a phone or, through its Herdr plugin, in a popup with one key, which wakes the agent. Its cards are kept, not derived: only the agent that posted a card can update or withdraw it, and its skill makes that the agent's duty ("a card means it's their turn now; the moment it isn't, withdraw it or change it", `update_request`, `cancel_request`, one `idempotencyKey` per question).

The user's concern: a card is shown, the plan is rewritten, and the card no longer applies.

## Decision drivers

- The rail's truth comes from state and must stay there; a second kept list is the staleness the user named.
- Every change that makes a card stale passes through crew: propose and replace, approve, drop, unit approve, construct again, merge, land.
- The user wants to be reached and to answer with a key, on the Mac or the phone.
- Client content on a third-party service is the user's call per partition.

## Considered options

1. Cards as the rail's surface: the agent that owns a decision posts one card per rail row, keyed by the row's id, and updates or withdraws it on the crew event that changes the row; the rail reconciles.
2. Cards as the rail: every decision lives only as a card.
3. No cards: the rail and the operator's notifications only.

## Decision outcome

Option 1, built after the rail has landed, and tried on swancloud before any client partition.

- **One card per rail row, by its owner.** The planner posts a card for each proposal it writes, keyed `proposal/<n>`; a conductor posts one for a unit in review, one for a verify report to decide, and one for a bolt ready to land, keyed by the unit's or bolt's name and the stage. The card shows the row's words and, as an artifact, what the user would read: the proposal as `crew plan proposed <n>` prints it, the change folder's path, the report. Its options are the row's answers.
- **A card is updated or withdrawn on the crew event that changes its row.** A replaced proposal withdraws the old card and posts the new; an approval, a drop, a rerun of construct, a merge or a landing withdraws the card for the row it removes, with a one-line outcome. crew's notice to the owning agent on each such write names the card to update or withdraw, so the agent acts on it as it does on any `[crew]` notice.
- **The rail reconciles.** `crew rail` shows, per row, whether a card is open for it, and names open cards that have no row, with the agent that owns each, so a forgotten card is seen within one refresh. crew cannot withdraw another agent's card; it tells the owner.
- **An answer wakes the owner, which acts on the user's word.** Approve wakes the planner, which runs `crew plan approve <n>`; the conductor runs `crew unit approve` or construct again with the user's note. Pending You records the answer as given in Herdr on that computer, and crew's run record records who ran the command, as it does today.
- **Landing a bolt is high stakes.** Its card is marked so, and is answered in the Pending You app with hold-to-approve, never with a key in the popup.
- **A pane's badge is the card's.** The Herdr plugin shows each waiting agent's card on its row, and the operator agent's herdr notification for a review, a report or a landing is no longer needed; its tell for a question in a pane stays, since that has no row and no card.

### What it needs outside crew

- Pending You set up on every host that runs crew agents, declared in swancloud: the `pendingyou` command line and its agent setup, the Herdr plugin from the fleet's catalog, and a sign-in per computer that the user grants; Claude Code 2.1.287 or later for the wake. A unit in swancloud.
- The user's decision, per partition, whether its proposals and diffs may sit on Pending You; swancloud first.

### Consequences

- One unit in crew after the rail's two: the card discipline in the planner's and conductor's briefs, crew's notices naming cards, and the rail's card column.
- The rail stays complete without cards; a host or partition without Pending You loses pings, not decisions.

## Pros and cons of the options

### Option 1: cards as the surface

- Good: the phone and a one-key answer; staleness bounded by crew's own events and shown by the rail; the truth never leaves state.
- Bad: two places to look until the rail shows card state; a card lingers when its owner is down until it is restarted or the user clears it in the app.

### Option 2: cards as the rail

- Bad: every decision kept by hand, which is the staleness the user named; nothing can be derived or reconciled; a card's owner down means a decision lost from view.

### Option 3: no cards

- Good: nothing hosted, nothing to keep.
- Bad: no reach to the phone, and every ping stays a pane notification the user may be watching nothing of.

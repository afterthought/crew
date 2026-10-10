# Proposal

## Why

The rail lists everything that waits on the user, but only for someone looking at it: it doesn't reach the phone and it doesn't ping. Pending You does both, and answers with one key in Herdr's popup or a tap on the phone, but its cards are kept by the agents that post them, so a card can outlive the decision it asked about. The user decided to answer the rail through Pending You cards, with each card kept true by crew's own events and shown on the rail, so a stale card is seen at once (`docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md`).

## What Changes

- **Every rail row gets one Pending You card, posted by the agent that owns the decision.** The planner posts one for each proposal it opens. A team's conductor posts one for each of its units in review, one for each verify report the user has to decide on, and one when its bolt is proven and ready to land. Each card says what the row says, carries what the user would read (the proposal's page, the change's folder, the verify report), and offers the row's answers as its options.
- **A card says whose it is and where it belongs.** It is asked in the agent's crew name (`swb-1-conductor`, `wldn-planner`), with its host and worktree. It sits in its kit's area, inside the partition's group (`wldn`, `madswan`, `swancloud`), and its title names what it asks about and its bolt ("Review the-rail-lists-what-waits-on-the-user, bolt decisions-shown-whole"). So teams, kits and partitions stay apart on the phone as they do in crew.
- **Answering a card wakes its owner, which acts on the user's word.** Approving a proposal's card wakes the planner, which approves it. Approving a review card wakes the conductor, which approves the unit, and a note asking for changes has it run construct again with those words. The verify card's answer has the conductor fix what the user chose or merge. Approving the landing card has the conductor ask the partition's main-level ops to land the bolt. Landing is marked high stakes, so it is approved by holding the button in the Pending You app, never with a key in Herdr's popup.
- **crew tells the owner when a card stops being true.** Whenever crew records a change that ends a row (a proposal approved, dropped or replaced; a unit approved, built again, merged or dropped; a bolt landed or dropped), the owner is told which card to close. When the owner made the change itself, crew's output says so; when someone else did, such as the user from the rail's shell, crew sends the owner a notice.
- **crew records every card its agents post and close.** A Claude Code hook in crew's plugin notes each card a crew agent posts, updates, withdraws or closes in Pending You, in crew's run record, keyed by the rail row it belongs to.
- **The rail shows each row's card.** Under each row, `crew rail` prints the row's card key and whether a card is open for it and whose it is. After the groups, it names any open card whose row is gone, with its owner and a pasteable `crew tell` asking the owner to close it. The rail still lists every decision without cards; a partition or host without Pending You loses the pings, not the decisions.
- **The conductor stops pinging the operator agents for what has a card.** A review, a verify report or a landing reaches the user through its card. The one-line tell to the operator agents stays for a question asked only in the conductor's pane, which has no row and no card, and for every wait in a session without Pending You.
- **The planner's and conductor's briefs teach the card discipline, the same way in both.** That covers which area and group a card goes in, the name it is asked in, one card per row keyed by that row, keeping it true, and closing it with the outcome. They also say an answer is heard by being woken, so an agent never runs anything of Pending You's from npm or waits with `hold`.

## Capabilities

### New Capabilities

- `rail-cards`: each rail row answered through one Pending You card from the agent that owns the decision, kept true by crew's events, recorded in the run record, and shown on the rail.

### Modified Capabilities

None. The rail's own requirements (`crew-rail`, from the change that built the rail) and the run record's are unchanged; what this adds to them is in `rail-cards`.

## Impact

- `plugin/hooks/hooks.json` and a new `plugin/hooks/cards`: the hook that records a crew agent's card acts.
- `plugin/lib/record.py`: two new fields, `Card` and `Key`, and the card acts.
- `plugin/lib/plan.py`: the rail's card line and its list of open cards with no row; the notices that name a card in `plan approve`, `plan drop`, `plan propose --replaces`, `unit approve`, `unit amend` and every plan write that removes a unit or a bolt from a team; and `run_check()`, behind `crew unit run`, naming the row a stage ends.
- `plugin/lib/crew.py`: a `CARDS` token shared by the planner's and conductor's briefs.
- `plugin/roles/planner.md`, `conductor.md` and `main-ops.md`.
- `README.md` and `plugin/skills/crew/SKILL.md`.
- Tests: a new `tests/t-cards.sh`; checks added to `tests/t-rail.sh`, `tests/t-proposals.sh`, `tests/t-unit.sh` and `tests/t-briefs.sh`.
- Needs, outside crew: Pending You set up on every host that runs crew agents, which swancloud's `pending-you-is-set-up-on-every-crew-host` unit does. The user's groups named for the partitions must exist in Pending You, since only the user makes groups. Which partitions' proposals and diffs may sit on Pending You is decided in swancloud's list of partitions that get it; crew follows whether an agent's session has the Pending You tools.

## Touches

`plugin/hooks/hooks.json`, `plugin/hooks/cards` (new), `plugin/lib/record.py` (`DESCRIPTOR`'s `%allowed`, `EXTRA`), `plugin/lib/plan.py` (`notify()`, `plan_propose()`, `plan_approve()`, `plan_drop()`, `unit_approve()`, `plan_agree()`, the amend tell, `run_check()`, `rail_rows()`, `rail_view()`, `proposed_at()`), `plugin/lib/crew.py` (`team_tokens()`, `main_tokens()`, a new `cards_how()`), `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `plugin/roles/main-ops.md`, `README.md`, `plugin/skills/crew/SKILL.md`, `tests/t-cards.sh` (new), `tests/t-rail.sh`, `tests/t-proposals.sh`, `tests/t-unit.sh`, `tests/t-briefs.sh`, and `openspec/specs/rail-cards/spec.md` (new, by delta).

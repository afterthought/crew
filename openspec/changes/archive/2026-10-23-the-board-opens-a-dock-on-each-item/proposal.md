# Proposal

## Why

The board the user looks at, crew's page served at `board.swancloud.net/<label>.html`, can only be looked at: nothing on it opens, so to learn more about a unit, a deploy or a signal the user goes to the terminal or another place. The user asked for the board to be interactive, a click on an item opening a drawer with its details as their flywheel-next mockup's dock does (signal 2026-10-23-swancloud-design-40a8b1a4/01), and record 0038, accepted on 2026-10-23, rules where and how: the board stays the one place, and a click on any item opens a dock over it (its §2), built in the page's one file with the dock's forms borrowed from the mockup and not its file (its §7). This is the first of the record's crew units; the word sent from the dock to the item's agent is the next one, `a-word-from-the-board-reaches-the-items-agent`.

## What Changes

- A click on any item of the board, or Enter on it, opens a **dock**: one panel over the right of the board, as the mockup's dock is (flywheel-next `design/surfaces.md` S27). The board does not move under it: nothing in the lanes reflows or scrolls when it opens or closes. Esc, its × or a click outside closes it. Under 760 px it fills the screen with a back control.
- The items that open a dock are those the record names, as the page draws them: a **signal** (a quote in Inception), a **proposal** (a sheet), a **bolt** (a ledger, planned or held), a **unit** or chore (a link of a ledger's chain or a queued slip), a **fix** (its row on a ledger), a **landing** (a record in Operation), a **deploy** (a record in Operation, and each deploy in the deploys view), an **operation** (an operation waiting on an environment), a **team** and a **subscription**.
- A team opens from a new row of pills in the board's strip, one per team of the partition, and wherever the board names a team; a subscription, the Claude account a session runs on, opens from the dock of a team that runs on it. The subscription's dock lists the partition's sessions on that account; its use and limits come with the fleet page's units, not here.
- Each dock holds the item's details as the page's data and its lineage already hold them, read from the same read and commit as the rest of the page, and nothing else: its facts, its markers in the board's own words, the items it is part of or holds, each a link that opens that item's dock, and its history from the run record as `crew trace` walks it. A page opened from another keeps a trail, and its back control returns to the one before.
- The dock's head takes its item's form, as the mockup's does (a proposal's a sheet's, a bolt's a ledger's, a landing's a record's), and the dock has no foot: the board still answers nothing (record 0010), so no dock holds a control that answers or moves anything.
- The open dock is kept in the page's address beside the team and the view, so a reload, or the page written again over this one, opens it again; an item the new page no longer holds leaves the board as it is.
- The page is still one file that loads nothing; every text in a dock is set as text.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `board-page`: the board's items open a dock with their details, over the board without moving it; the strip names the partition's teams; the page stays one self-contained file with the dock in it.

## Impact

- `plugin/lib/page.py`: the dock pages, one per item, made from the page's data and its lineage, each board item given the key of its own; each team's session and Claude account from the teams and hosts files crew already reads (`code.5`).
- `plugin/lib/page.html`: the dock, its styles from the mockup's, the strip's team pills, the clicks and keys that open and close it, and its key in the address.
- `tests/py/test_page.py`, `tests/t-journey-board.sh`: the dock pages' cases and the written page's wiring.
- README and the crew skill's line for `crew page` (`docs.2`).
- No change to `crew board`, its JSON, the agents' views or crew's mod (`code.8`: nothing the views draw moves). No service: the page is still a file (`state.4`).

## Touches

```
plugin/lib/page.py
plugin/lib/page.html
tests/py/test_page.py
tests/t-journey-board.sh
README.md
plugin/skills/crew/SKILL.md
```

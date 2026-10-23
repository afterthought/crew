# Proposal

## Why

On the served board the user cannot switch partitions: swancloud's page names madswan and wldn, and clicking either opens nothing (the user, 2026-10-11: "I cannot switch between the partitions. It's showing swancloud but I cannot click on MadSwan or Willdan.", signal 2026-10-11-crw-3-ops-4514770e/05). crew's page links each other partition as `../<label>/page.html`, crew's own folder layout, while swancloud makes every partition's page with `crew page <label> --out <work>/<label>.html` and serves them side by side as `https://board.swancloud.net/<label>.html` (swancloud `lib/board.nix`, `modules/board-server.nix`, `packages/swancloud-board`). Record 0010 rules that the served layout is the kit's and the page's partition links open the pages where the kit serves them.

## What Changes

- The page links each other partition's page in the layout of the page's own file: written as `<label>.html`, it links `<other>.html` beside it, which is how swancloud asks for and serves its pages; written as `<label>/page.html`, crew's own layout under `~/.local/state/crew/`, it links `../<other>/page.html` as it does today. A folder and a file both named for the partition are both followed (`wldn/wldn.html` links `../madswan/madswan.html`).
- A page written to a file whose name and folder name neither its partition still names every partition but links none, since crew cannot tell where the others are, and `crew page` prints a line saying the other partitions are not linked and why. Nothing links to a page that is not there.
- swancloud needs no change: its maker already writes each page as `<label>.html`, so the served board's links open the other partitions' pages from the next page made.
- README's `crew page` paragraph, crew's usage and the crew skill's line for the page say where the partition links point (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `board-page`: the header's partition links follow the layout of the page's own file, `<other>.html` beside a page written as `<label>.html` and `../<other>/page.html` beside one in crew's folder layout, and a page in neither layout names the other partitions without linking them.

## Impact

`plugin/lib/page.py` (the header's links, given the page's own path; the printed line); `plugin/bin/crew` (the usage's `crew page` lines, its first line kept so swancloud's maker still finds the command); `README.md`; `plugin/skills/crew/SKILL.md`; `tests/py/test_page.py`; `tests/t-journey-board.sh`. The page's data, the board's read and the agents' views are unchanged (`code.8`).

## Touches

```
plugin/lib/page.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_page.py
tests/t-journey-board.sh
```

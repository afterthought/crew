# Proposal

## Why

The board shows one partition at a time, so to see how the whole fleet stands the user opens each partition's page in turn and looks up the rest, which host a team runs on, which Claude account a session bills, how long since a kit's main last moved, in other places. The user asked for one place with a nice overview of every crew (signal 2026-10-23-swancloud-design-40a8b1a4/02), and record 0038, accepted on 2026-10-23, rules that it is a fleet page at the board's root: every partition at once, its hosts and sessions, its kits with each main's last landing and what is queued for it, its teams with their bolts and how busy each is, the Claude account each session runs on and its attention items, each partition's page a link away (its §1), a second file of the same maker, one file loading nothing (its consequences and §7).

## What Changes

- `crew page --fleet` writes the **fleet page**: one HTML file, its data, style and script inline and nothing loaded, made from one read of every partition in the teams file, the same read `crew board` makes of all of them.
- The fleet page has one block per partition, in the teams file's order, each holding:
  - **where it runs**: each host its teams and main level run on, marked when it did not answer, and under each host the herdr sessions the partition's agents run in, each naming the agents in it (its teams, its design agent, planner, ops and operator, its dispatcher there) and the Claude account the hosts file gives that session, or that it names none;
  - **its kits**: each kit its teams build, with the teams building it, its main's last landing in the run record's window (which bolt, the commit main then held, when and who landed it), and what is queued for that main: the bolts that wait to land, the bolts in construction, the bolts planned and the units queued;
  - **its teams**: each team with its host and session, the bolt it holds with its units' pips and how many have merged, each of its slots at work on a stage, holding work with no stage running, or free, how many of its slots are at work, and what its conductor waits on;
  - **its attention items**, in the board's own words, and how many of its cards are open.
- Each partition's name is a link to its page, and each team a link to its dock there, in the layout of the fleet page's own file: `<label>.html` beside a fleet page written as `index.html`, as the board is served; `<label>/page.html` beside one written as `page.html`, crew's own layout; none, said by the command, for any other name.
- Each partition's page links back to the fleet page in its header, in its own layout: `index.html` beside a page written as `<label>.html`, `../page.html` from a `page.html` in a folder named for its partition, as crew writes them.
- Written by default to `~/.local/state/crew/page.html`, beside the partitions' `<label>/page.html`; `--out` names another file. A host that does not answer is named on the page and in what the command prints, and everything else is shown (`read.3`).
- Nothing new is read: the hosts, sessions and accounts come from the teams and hosts files crew loads, the rest from the board's read and the run record it already reads. `crew board`, its JSON and the agents' views are unchanged.

## Capabilities

### New Capabilities

- `fleet-page`: the fleet page, every partition at once, its hosts and sessions, kits, teams and attention, each partition's page a link away.

### Modified Capabilities

- `board-page`: a partition's page links back to the fleet page in its header.

## Impact

- `plugin/lib/page.py`: `--fleet`, the fleet page's data made from the board's read of every partition, the links between the fleet page and the partitions' pages.
- `plugin/lib/fleet.html`: the fleet page's template, its tokens the page's own.
- `plugin/lib/page.html`: the header's link to the fleet page.
- `plugin/bin/crew`: `crew page`'s usage line.
- `tests/py/test_fleet.py`, `tests/py/test_page.py`, `tests/t-journey-board.sh`, `tests/moon.yml`: the fleet page's cases, the back link, the written page's wiring.
- README and the crew skill's line for `crew page` (`docs.2`).
- Serving the fleet page at the board's root is swancloud's: its maker writes `crew page --fleet --out <dir>/index.html` beside the partitions' pages, and its server answers the root with it rather than sending the bare name to the first partition's page. That is not in this change.

## Touches

```
plugin/lib/page.py
plugin/lib/fleet.html
plugin/lib/page.html
plugin/bin/crew
tests/py/test_fleet.py
tests/py/test_page.py
tests/t-journey-board.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
```

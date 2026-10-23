# Proposal

## Why

The user wants to see in one place which Claude Code subscriptions the crews use and each one's current session and weekly limits, Fable's among them, so they can tell whether the system and their subscriptions run efficiently (signal 2026-10-23-swancloud-design-40a8b1a4/02). The fleet page already names the account each session runs on, but nothing in the fleet shows a subscription's use: Claude Code shows it only in `/usage`, one sign-in at a time. Record 0038, accepted on 2026-10-23, rules that each Mac reads, for every Claude account signed in on it, the use `/usage` reads and publishes the numbers alone where crew's page reads them, and that the fleet page shows them per subscription with the sessions and partitions on it and how old the reading is, a reading a host could not make marked, and nothing computed beyond the use beside the work of the sessions on it (its §5). This change is crew's half: the fleet page reads what the hosts published and shows it. Reading and publishing on each Mac is swancloud's (`a-mac-publishes-its-sign-ins-usage`).

## What Changes

- The fleet page gains a **subscriptions** section above the partitions, one entry per Claude account: every account the hosts file gives a session, and every account a host published a reading for.
- Each subscription shows its **five-hour** and **seven-day** use, each as a percentage with when it resets, and its weekly use **by model** where the reading gives it (Opus, Sonnet, and each model the server names, such as Fable), exactly as the host holding its sign-in published them: the figures are shown, never graded or combined.
- Each subscription says **which host read it and how old the reading is** when the page was made, and lists every other host that published for it, with its own age or why it could not read.
- A reading a host **could not make** is marked so, with the host's own words for why; a subscription no host has published for says so; a published file crew cannot read is named on the page and by the command, and the rest is shown.
- Beside the use, each subscription lists **the sessions on it**, by host, with crew's agents in each and, for a team, how many of its slots are at work and what its conductor waits on, and **the partitions** whose agents run on it. Nothing is computed from the two: they sit side by side.
- crew reads the published use from one folder on the host that makes the fleet page, `~/.local/state/crew/usage/`, one file per host, in a shape this change fixes: the fields Claude Code's own `/usage` reading names, per account, with when it was read or why it could not be. crew reads nothing over ssh and no credential for it.
- `crew page --fleet` prints a line for each published file it could not read, and one saying no use is published when the folder holds none.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fleet-page`: the fleet page shows each subscription's use, the hosts that read it and how old each reading is, and the sessions and partitions on it. The capability is created by `the-fleet-page-shows-every-partition-at-once`, ahead of this change in the bolt.

## Impact

- `plugin/lib/page.py`: the read of the usage folder; the subscriptions' data, a decision on plain facts; the agents of each session, shared by where a partition runs and the sessions on a subscription; what `crew page --fleet` prints.
- `plugin/lib/fleet.html`: the subscriptions section.
- `tests/py/test_fleet.py`, `tests/t-journey-board.sh`: the subscriptions' cases and the read's wiring.
- README's `crew page --fleet` paragraph, the crew skill's row, and the usage text in `plugin/bin/crew` and `page.py` (`docs.2`).
- swancloud: its reader writes `~/.local/state/crew/usage/<host>.json` on the board's host in the shape the design fixes. That is not in this change.

## Touches

```
plugin/lib/page.py
plugin/lib/fleet.html
plugin/bin/crew
tests/py/test_fleet.py
tests/t-journey-board.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
```

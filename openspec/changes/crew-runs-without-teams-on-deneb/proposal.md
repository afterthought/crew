# crew runs without teams on deneb

## Why

The user's word of 2026-11-03 (Pending You req_6b236a29): "Deneb only now; the box later." Every crew team on deneb has landed its bolt and is closed, and deneb's main levels are down, so deneb can run crew without teams (record 0047 move 5). chuck-herdr-alpha, the box, still runs wldn's teams on today's crew and must not be touched.

crew without teams has been built and landed once already. `the-team-machinery-leaves` (#416, a2aa2c9d) landed on `bolt/crew-runs-its-work-through-flume`, the bolt landed on main (#417, 9d590e9f), and then came the design agent's pages (#418, ab7f9006) and the design agent's and planner's model (#419, ccb5f9a9). A landing on main deploys crew to every host. The box's teams file is at version 2, and a crew that reads version 5 alone refused it, so #420 (68d23639) took all of it off main. Since then main has landed the Opus fix again (#421), the crossing step (#423, 09b2cf4d: teams cross to Flume as their bolts land, and roles may run as Flume kinds), the design records #425 to #428, and the bolts #430 (a quiet agent that committed is not stuck) and #435 (crew's chores of the 24th night).

This change brings the teamless crew back onto today's main as a branch, `teamless/deneb`, whose commit swancloud can pin for deneb alone. Nothing of it reaches main: a landing there would deploy it to every host and refuse the box's teams again.

## What Changes

- **BREAKING, for the host that pins it.** crew reads `teams.json` at version 5 alone: partitions only, each naming under `flume` the Flume setting of design, planner, reviewer, ops and operator. It refuses a file at any other version, the box's version 2 among them, and a version-5 file holding a `teams` key. Each refusal names swancloud's `lib/crew-teams.nix` and does nothing (`code.5` as #418 amended it; swancloud record 0044).
- The teamless crew as #419's landing (ccb5f9a9) held it comes back whole. That is everything #416 removed and rewrote, #418's pages, the archived change `2026-11-01-the-team-machinery-leaves` and the specs synced from it. It is applied three-way against #423's landing, so main's later work is kept.
- Main's later landings are reconciled by one rule. A later landing that touched team machinery #416 removes goes with it. One that changed something that stays keeps main's version:
  - #430's stuck report goes whole: its code, its brief words, its docs and its tests. This change removes its requirement "A conductor reads a stuck report before it asks".
  - From #435, the batch reckoning at a conductor's wait and over the teams goes. The browser words of the coder and verify briefs leave with those briefs. Its fixed clock for the rail's branch-alone cases stays.
  - #421's Opus model for the design agent and the planner stays. The team crossing #423 brought back is removed as #416 removes it; the rest of #423 stays.
  - #425 to #428's records and rules stay: record 0052's amendment as accepted, `roles.9`, `briefs.15`, and `plan.md`'s lines on a plan write's entry and a read below the tip. #418's amendments are made around them.
  - Where the rule pages cite the reverted landing (9d590e9f, #417), they name this change on `teamless/deneb` instead. `_open.md` says deneb loads crew from this branch, and that the browser words were left with the stage briefs.
- The gate's checks run with `sluice exec main` once committed, and every check passes. The branch is pushed to GitHub as `teamless/deneb`. Nothing is submitted to main.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: the teams file requirement, as `the-team-machinery-leaves` left it, gains scenarios for the box's file at version 2 and for a version-5 file holding `teams`. crew refuses both.
- `bolt-teams`: the conductor's reading of a stuck report (#430) leaves with the conductor.
- The restored archive of `the-team-machinery-leaves` changes again every capability it modified: `agent-models`, `board-page`, `bolt-plan`, `bolt-teams`, `card-sessions`, `chores`, `crew-board`, `crew-rail`, `crew-sites`, `fleet-page`, `flywheel-state`, `host-holds-and-updates`, `kit-toolchain`, `main-level`, `operator-agent`, `plan-proposals`, `rail-cards`, `review-batches` and `run-record`. The restored specs are its synced specs, reconciled in the design. This change's deltas cover only what main has added since.

## Impact

- The code, briefs and tests `the-team-machinery-leaves` changed, as its proposal lists, at a2aa2c9d. The 21 files where main's later landings meet it are listed in the design with how each resolves.
- `docs/architecture/`: #418's amendments, reconciled with #425 to #428. `docs/adr/` keeps main's records.
- Main is untouched. The change lives on `change/crew-runs-without-teams-on-deneb` and is pushed as `teamless/deneb`. No release tag carries it, since CI tags main's pushes alone (`code.10`).
- Depends on swancloud pinning deneb's crew to the pushed commit and writing deneb's teams file at version 5 in the same deploy, on the user's word. The box keeps the fleet's release and its own file.
- Departs from `roles.8`, `plan.19` and `code.10` for deneb, from `docs.7` for the pages, and from crew's last-task convention. The design says why for each.

## Touches

```
plugin/lib/plan.py
plugin/lib/runner.py
plugin/lib/crew.py
plugin/lib/hold.py
plugin/lib/board.py
plugin/lib/cards.py
plugin/lib/page.py
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/fleet.html
plugin/lib/page.html
plugin/lib/ops.py
plugin/lib/record.py
plugin/lib/sites.py
plugin/lib/transcript.py
plugin/bin/crew
plugin/bin/crew-role
plugin/hooks/**
plugin/roles/**
plugin/skills/crew/SKILL.md
plugin/tests/**
README.md
CLAUDE.md
docs/architecture/**
openspec/specs/**
openspec/changes/archive/2026-11-01-the-team-machinery-leaves/**
tests/py/**
tests/contract/**
tests/t-*.sh
tests/lib.sh
tests/teams.sh
tests/units.sh
tests/journeys.sh
tests/stubs/**
tests/moon.yml
```

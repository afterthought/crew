# Proposal

## Why

The recovery of 2026-10-12 built units outside any team and landed them on main: `the-page-shows-the-deploys` beside the archived `a-deploy-is-approved-and-recorded-through-crew`, both of the bolt `deploys-go-through-crew`, which no team holds. `crew bolt land` refused a bolt no team holds as never built, so the plan could keep such a bolt forever or drop units that were built. The user: "why would we be dropping the units and not archiving them if they've been built?"

## What Changes

- `crew bolt land <bolt>` takes a bolt no team holds once its kit's main holds each of its units' changes, open or archived, and each of its chores' trailers, read on the host and main checkout of a team of the partition building that kit. It lands as any landing does: on the user's word (`roles.2`, `plan.16`), refused while a unit's latest change has been in no batch or main is behind GitHub's, its entry recording the kit and the commit main holds. Nothing is merged or pushed, since main already holds the work, and no worktree is tidied.
- It is refused for such a bolt with no units or chores, or whose kit no team of the partition builds.

## Capabilities

### Modified Capabilities

- `bolt-teams`: a bolt no team holds lands once its units are on main.

## Impact

`plugin/lib/plan.py` (`builder`, `unheld_stages`, `unheld_refusal`, `bolt_land`), `docs/architecture/plan.md` (`plan.16`), README; `tests/py/test_bolt_commands.py`, `tests/t-journey-land.sh`.

## Touches

```
plugin/lib/plan.py
docs/architecture/plan.md
README.md
tests/**
```

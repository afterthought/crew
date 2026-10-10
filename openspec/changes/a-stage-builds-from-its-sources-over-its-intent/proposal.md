# Proposal

## Why

On madswan, the user got a review card for the wrong page. The planner's intent named a measurement and its sample points; the design agent's record of what the user actually wanted landed on the kit's main three seconds after the bolt was cut. The construct read that record and still followed the intent, because nothing told it which governs. The user: "You knew what I wanted ... That is not what came out on the other end, so something got lost." Record 0004, as amended on 2026-10-10, settles it: a unit's sources govern how it is built, read as they stand on main when the stage starts, and a construct that finds the intent saying more, or saying otherwise, builds from the sources and says so (rule `briefs.14`). No brief says this yet.

## What Changes

- **A construct reads its unit's sources from main as they stand when it starts.** It reads each source as committed on its repository's main at that moment, never the copy in its own worktree, which is the bolt's as it was when the bolt was cut. So a record the design agent lands after the cut, or between two runs of construct, is the one the construct reads.
- **Where the intent and the sources differ, the sources govern.** Where the intent says more than its sources (a mechanism, a measure, a step they don't name) or says something they contradict, the construct writes the change from the sources, not the intent.
- **The construct names the difference first in its final message**: what the intent says, what the sources say instead, and which source. A construct that found no difference says nothing about it.
- The construct's brief says all of this, and `tests/t-briefs.sh` holds its phrases. Nothing crew runs changes: the prompt still carries the intent and the sources as it does today.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `bolt-teams`: a construct reads its unit's sources from main as they stand when it starts, builds from them where the intent says more or otherwise, and names the difference first in its final message.

## Impact

- `plugin/roles/construct.md`: reading the sources, and the opening of the final message.
- `tests/t-briefs.sh`: checks for the new rule in the construct's brief (`tests.6`).
- `docs/architecture/_open.md`: the `briefs.14` entry keeps only the spike, which this change does not build.
- Every team's construct stage takes the rule at once, since each construct is a fresh agent that loads its brief when it starts.

## Touches

`plugin/roles/construct.md`, `tests/t-briefs.sh`, `docs/architecture/_open.md` (shared), `openspec/specs/bolt-teams/spec.md` (by delta).

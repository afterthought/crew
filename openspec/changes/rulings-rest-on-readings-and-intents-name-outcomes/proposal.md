# Proposal

## Why

On wldn, the design agent ruled step by step how a takeover of an AWS boundary should work, from what it believed about CloudFormation and IAM, minutes after each question and without reading the service. Each fact the construct then met broke a step and brought a new ruling and a new proposal for the user to approve, when each was one short check against AWS. The planner had written the mechanism into each unit's intent, so every changed mechanism meant an amended intent, and it proposed each correction the minute it arrived. On swancloud the same day, a bolt went from two units to four, several amended in flight, from intents that named mechanisms.

wldn's agents wrote their fixes into switchboard-kit and their own memories. The user wants them in crew, so every partition's design agent, planner and conductor work this way from their next fresh start (`docs/adr/0004-rulings-rest-on-readings-and-intents-name-outcomes.md`).

## What Changes

- **The design agent rules from readings.** A ruling about how a service or system behaves names, in the message that carries it, the documentation page or the reading it rests on. Before ruling about something that exists, the design agent reads it itself with the credentials it has: the live configuration, the stack, the policy, the code on main. Where it can do neither, it says so and asks for the reading before the ruling reaches any unit.
- **The design agent rules what must be true, not the steps.** It says what must be true and what must not change, and leaves the sequence to the construct, which brings its own reading back.
- **The design agent answers a construct's linked questions as one,** after reading, not one at a time as they arrive.
- **An intent names the outcome and the records that govern it, never the mechanism.** The planner writes intents this way, and so does the design agent when it queues a unit. The how lives in the records the unit's sources name, so a changed mechanism changes no intent.
- **The planner batches corrections to a unit under construction** into one amendment once its construct has settled, unless one blocks the team now.
- **The conductor carries a construct's linked questions to the design agent together,** in the words of whoever asked, and brings the answer back to the construct with the reading it names.
- The design agent's, planner's and conductor's briefs say all of this. Nothing crew does changes: these are rules the agents work by.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `main-level`: the design agent's rulings rest on readings, rule outcome and constraints, and answer linked questions together; the planner's and design agent's intents name outcome and records; the planner batches corrections to a unit under construction.
- `bolt-teams`: the conductor carries a construct's linked design questions together and brings the answer back with its reading.

## Impact

- `plugin/roles/design.md`: answering a conductor, queuing work.
- `plugin/roles/planner.md`: writing an intent, changing what a unit builds.
- `plugin/roles/conductor.md`: what to do when a stage stops short, and the design-question line of what is not in the bolt.
- `tests/t-briefs.sh`: checks for the new rules in each brief.
- Every partition's design agent, planner and conductor take the rules at their next fresh start, or when told what changed.

## Touches

`plugin/roles/design.md`, `plugin/roles/planner.md`, `plugin/roles/conductor.md`, `tests/t-briefs.sh`, `openspec/specs/main-level/spec.md` (by delta), `openspec/specs/bolt-teams/spec.md` (by delta).

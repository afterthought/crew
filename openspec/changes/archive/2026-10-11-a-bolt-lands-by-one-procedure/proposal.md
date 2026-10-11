# A bolt lands by one procedure

## Why

The briefs, the rules and the specs gave the landing three shapes. main-ops's brief and the specs had main-level ops
deploy main as part of a landing, while `plan.14` rules that out; the word to land could come from the user, the
planner or the conductor; `briefs.11` gave main-level ops "the landings'" cards while the conductor's brief posts the
landing card; and main-ops pushed main only on a second word, so on 2026-10-11 crew's main stood 103 commits ahead of
GitHub's and the box, which pulls GitHub's, ran a crew a day old. Agents read different procedures and argued over
which was right (the user, 2026-10-11: "agents not agreeing on what the process is for landing bolts").

## What Changes

- A bolt lands by one procedure, main-level ops's (`plan.16`, new): the conductor posts the landing card once ops's
  proof is clean at the bolt's head; the user's approval on it is the word to land, and the conductor passes it to
  main-level ops with `crew tell`; ops fetches the kit's main, merges the bolt through the kit's hooks, pushes main,
  runs `crew bolt land`, and for crew brings every host's checkout up to it. The user saying so in ops's pane is the
  same word. Nothing else is: the planner passes no word on.
- The word to land is the word to push: main is pushed in the landing, never with force.
- A landing deploys nothing (`plan.14`). Until a kit's deployer records its deploys through crew, main-level ops
  deploys that kit's main only on the user's word for that deploy, a departure from `plan.14` the user ruled on
  2026-10-11.
- `briefs.11`: main-level ops's cards are the deploys' and its own questions about a landing under way, such as a
  conflict or a main behind GitHub's; the landing card is the conductor's.
- main-ops's, the conductor's and the planner's briefs, the roster, README and CLAUDE.md say the same.

## Touches

```
plugin/roles/main-ops.md
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/lib/crew.py
README.md
CLAUDE.md
docs/architecture/plan.md
docs/architecture/briefs.md
openspec/specs/main-level/spec.md
openspec/specs/bolt-teams/spec.md
tests/t-briefs.sh
```

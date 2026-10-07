# A change is archived at its merge into the bolt

- Status: accepted
- Date: 2026-10-07
- Deciders: the user ("When in the process does OPSX archive run?", "pass to design"), through swancloud-operator-mac-studio; swancloud-design
- Sources: `openspec/specs/bolt-teams/spec.md` (a unit is built stage by stage; work happens in fixed places), `bolt-plan/spec.md` (a unit's stage is read from the kits), `plugin/roles/coder.md` (merging), `ops.md` (proving the bolt), `CLAUDE.md` (proving and landing a bolt); `docs/adr/0001` (chores); swancloud's proposals 1 and 3 (archives as units)

## Context and problem statement

`openspec archive <change>` moves a change under `openspec/changes/archive/` and folds its spec deltas into `openspec/specs/`, which is where a kit says what is true. Nothing in crew runs it: no brief and no command. A unit's change lands on main still open, verify's "ready for archive" goes nowhere, and main's specs say less than its code does. Archives have been planned as units of their own, which the chore kind will make chores, one per change, each a proposal for the user. The user wants archiving in the flow.

## Decision drivers

- The specs a construct reads should be true: a unit built after another in the same bolt should see the earlier unit's requirements in the specs, not in an open change beside them.
- Nothing kept by hand and no step for the user: archiving is mechanical once the change is proven.
- What lands on main goes through the bolt and the kit's merge hooks; nothing is committed to main beside a landing.

## Considered options

1. At the unit's merge into its bolt: the merge stage archives the change first, then merges.
2. When the bolt is proven in dev, before landing: one archive per unit on the bolt, run by a crew command the conductor calls.
3. At landing, on main, by the main-level ops.
4. As today: never in the flow; a chore per change, planned and approved.

## Decision outcome

Option 1. A unit's change is archived by its merge stage: the first thing the merge does, in the unit's worktree, is `openspec archive <unit>`, committed on the unit's branch, and then the branch merges into the bolt as it does today. By then verify has passed and every task is ticked, which is what an archive needs. The bolt's specs then say what the bolt's code does; a later unit's construct and verify read them; landing carries the archived change and the merged specs to main through the kit's merge hooks.

What follows from it:

- A merged unit is read from the archive: `merged` when the bolt holds the unit's change, open or archived, as `landed` already reads main.
- Ops's proof of the bolt reads each unit's *Proof in dev* list from the archived change on the bolt.
- A change whose spec delta modifies a requirement that a sibling unit adds in the same bolt archives only after that sibling has merged; the merge is refused until then, and the conductor sets the dependency. Two units' deltas to one spec file meet at the merge as any two changes to one file do, and are resolved there keeping both intents.
- A kit whose proof on real work needs main (crew itself) keeps that proof as a section of the change's design, worked after landing from the archive, never as tasks, since open tasks would hold the unit before verify.
- Changes already on main open from before this rule (crew's run-record, state-repository and plan-proposals; swancloud's crew-state) are archived once each, as the chores already planned; no new archive units are planned after this.

### Consequences

- One unit in crew: the coder's merge section, the readers of a bolt's changes, the ops brief's proof path, and the `bolt-teams` and `bolt-plan` specs.
- `docs/adr/0001` stands: the archive of a change landed open is a chore; a change built as a unit is never one.

## Pros and cons of the options

### Option 1: at the merge

- Good: no new command, no new agent, no step for anyone; the gate it needs, every task ticked, is the merge's gate already; specs are true on the bolt from the first merge.
- Bad: archived before the bolt's proof in dev; what the proof finds is a fix or a new unit either way, so nothing is lost, and the archived design is still read.

### Option 2: when the bolt is proven

- Good: archived only after dev has run it.
- Bad: a crew command that commits in the bolt's worktree, run by the conductor at the right moment; until then, a later unit in the bolt reads its sibling's requirements from an open change, not the specs.

### Option 3: at landing, on main

- Bad: commits on main outside the bolt's merge and its hooks, or an archive folded into a landing the main-level ops performs by hand.

### Option 4: a chore per change

- Bad: a proposal and an approval per archive for something with no decision in it.

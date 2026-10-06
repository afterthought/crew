# Chores beside units and fixes

- Status: accepted
- Date: 2026-10-05
- Deciders: the user, by the question put to swancloud-design through swancloud-planner; swancloud-design
- Sources: swancloud's `openspec/explorations/rollout/plan.md` (step 2.3); Flywheel Next's glossary and requirements 59–63, 91 and 123 (`agentplot/blueprints:design/flywheel-next/requirements.md`); crew's `openspec/specs/bolt-teams/spec.md` and `bolt-plan/spec.md`; the briefs `conductor.md`, `coder.md`, `verify.md`, `planner.md`

## Context and problem statement

crew builds two kinds of work. A **unit** is one OpenSpec change: construct writes it, the user reviews and approves it, code builds it, verify checks it, merge puts it in the bolt; it is a record in the plan. A **fix** makes the system do what the spec already says: the conductor raises it on its own bolt when the bolt's verification is red or ops or the user finds a defect; it has no change and no plan record.

Maintenance that decides nothing and fixes nothing broken has had to ride as a unit. A tool-version bump (`biome-follows-the-shell`) went through a construct stage, a proposal for the user to review, code, verify and merge. Two archives of proven changes ride as units in swancloud's proposals 1 and 3 because there is nothing else to ride as. Each costs the user a review of a change that says nothing.

Flywheel Next, the model crew aligns with, has chores: "a small fix a session judges necessary but cannot or should not do itself", which when accepted is "a unit of the chore type: one agent scoped to the right place, no change directory, never a bolt of its own". Updating instructions, citations and references and similar housekeeping are chores there, not units.

What is a chore in crew and what is not, who may add one, how it is built, and how it shows in the plan and the run record?

## Decision drivers

- A chore must cost the user nothing to approve beyond the plan change that adds it: no change to read, no review stage.
- A chore must not become a side door for design: nothing a chore does may change what the specs say must be true, and a chore that needs a decision must stop.
- Hold similar things to the same rule. Work enters the plan one way; a bolt is built in slots by fresh agents; stages are read from the kit, never written down; main changes only when a bolt lands.
- Keep Flywheel Next's words and shapes where they fit, and say where crew differs and why.
- Keep crew's vocabulary true: in every brief, spec and the README, "a unit is one OpenSpec change".

## Considered options

1. A chore is its own kind of record and command, beside unit and fix: a `Chore` record in the plan, `crew chore` commands mirroring `crew unit`, stages code, verify, merge.
2. A chore is a unit with `Kind: chore`, run with the `crew unit` commands, construct and approve skipped for that kind (Flywheel's shape: a unit of the chore type).
3. A chore is a fix with a plan record: `crew fix` extended with a plan entry and a verify stage.
4. Chores may also be made on main outside any bolt, their merge their landing (Flywheel's shared-line chore).

## Decision outcome

Option 1, with chores confined to bolts (not option 4).

### What a chore is

A chore is planned maintenance in a kit: work that is due, that changes nothing the kit's specs say must be true, and that needs no decision the design has not already made. Its result can be checked against its own words by someone who has read nothing else. Chores are: a tool or dependency version bump; a pin or a config aligned with another; the archive of a change whose every task is ticked; a rename or a moved file; a stale instruction, citation or line of documentation; housekeeping of that kind.

### What a chore is not

- **Not a unit.** A unit makes something new true, and the user reviews its change before it is coded. Work that adds or changes a requirement or a scenario, or whose doing raises a question the design does not answer, is a unit.
- **Not a fix.** A fix is the conductor's answer to something broken on its bolt and has no plan record. Nothing is broken behind a chore; it is planned, so it is in the plan, placed by the planner like a unit.
- **The test, in this order.** Does it change what must be true, or need a decision? A unit. Is something on the bolt broken, a red verification or a found defect? A fix. Otherwise, a chore.
- **A chore never grows.** An agent doing a chore that finds it needs a decision, or that the change it would archive has an unticked task, stops and says so, as a fix's agent does. That is a unit, or not yet due; the chore is not widened.

### Who may add one

A chore enters the plan as a unit does, by the same hands and no others:

| who | how |
|---|---|
| the planner | by a proposal the user approves (`Do: chore add …`), into a bolt or a kit's queue; `--signal <id>` routes a signal to it and writes the signal's `route` move on approval; `--unblocks <bolt>` when a held bolt needs it before it can be proven or land, placed ahead of what waits on it |
| the design agent | to a kit's queue only (`chore add … --repo <kit>`), never into a bolt |
| the user at a shell | anywhere |

The conductor adds none: what breaks on its bolt is a fix, and what its bolt needs planned it asks the planner for, in the words it already uses for a unit. A stage agent or ops that sees maintenance due outside its job records a signal with `crew signal`; the planner routes it. Flywheel's "offer a chore" is this signal and this route, and Flywheel's acceptance on the operator's rail is the user's approval of the proposal.

### How it is built

A chore is built in its bolt, on `chore/<name>` branched from the bolt, in `<kit>/places/chore-<name>`, in a free slot of the team, three stages, each a fresh agent the conductor starts with `crew chore run <chore> code|verify|merge`:

- **code**: the coder, in the chore's worktree, told `Chore: <the chore's words>`. It does exactly what the words say, in the kit's conventions, commits as `chore:` with a `Chore: <name>` trailer on each commit, and touches nothing under `openspec/`, with one exception: the archive of a change whose every task is ticked is done with openspec's own archive command, and that is the one chore that touches `openspec/`. It stops and says so if the words need a decision, or an archive's change has an open task.
- **verify**: the verifier, in the chore's worktree, given the chore's words. It changes nothing. It checks that every commit on the branch serves the words and nothing else changed; that the tests of what changed pass; that `openspec/` is untouched, or touched only by an archive. It writes its report to a file as a unit's verify does, and the conductor decides with the user what goes back to code, with the findings, as for a unit.
- **merge**: as a unit's, into the bolt with the kit's merge hooks (`wt merge bolt/<bolt> --no-squash --no-remove`). The bolt's verification runs after it as after any merge; red is a fix. The chore's slot is freed and its place removed the next time crew reads the team.

There is no construct stage and no review: a construct or `crew unit approve` on a chore is refused, naming its kind. No new role: the coder does code and merge and the verifier does verify, at their efforts.

A chore lands with its bolt. There is no chore on main outside a bolt: main changes only when the main-level ops lands a proven bolt on the user's word, and a second path to main is what that rule exists to prevent. This is where crew differs from Flywheel Next, whose shared-line chore merges straight onto `main`.

### How it shows in the plan

`plan.rec` holds a third record beside Bolt and Unit: **Chore**, with the Unit's fields and no others: `Name`, `Repo`, `Bolt` (absent when queued), `Intent` (its words), `Source`, `After`. Chores sit in the same file in build order with the units; `After` may name units and chores of the same bolt either way round; a unit may wait on a chore and a chore on a unit. A name is taken once in a kit, by a unit or a chore.

The commands mirror the unit's, with the same flags and the same refusals: `crew chore add|move|order|after|drop`, `crew chore run <chore> code|verify|merge`. There is no `chore split` and no amendment: a chore is small, and since it has no review there is nothing to return to; its words change by a proposal that drops it and adds it again, and a chore in flight that is dropped is freed as a dropped unit is. The direct-write table is the unit's: the planner by proposal, the conductor `chore order` and `chore after` within its bolt, the design agent `chore add --repo`, the user everything.

`crew bolts` lists a bolt's chores among its units in build order, marked `chore`, each with its stage and worktree, and the queue lists queued chores the same way. `crew plan proposed <n>` shows "New chore `<name>` in bolt `<bolt>`" with its words, and a signal source as it does for a unit.

A chore's stage is read with nothing kept by hand:

| stage | read from |
|---|---|
| `queued`, `waiting`, `ready` | the plan, as a unit's |
| `code`, `verify` | the team's state on its host: the stage its slot last ran, as a fix's shows today |
| `merged` | the bolt's history holds commits carrying its `Chore:` trailer |
| `landed` | main's history does |

crew refuses verify while the code agent is working, merge before verify has run, any stage of a chore whose `After` has not merged, and a chore by a name the kit already has.

### How it shows in the run record

A chore is the object `chore/<name>` wherever a unit is `unit/<unit>`:

- the plan writes are `chore.add`, `chore.move`, `chore.order`, `chore.after` and `chore.drop`, `On` the chore and its bolt or `queue/<kit>`, `From: signals/<id>` with `--signal`; `bolt.drop` and `bolt.land` name the chores they remove as they name units; an approval's entries name the chores its `Do` lines name, `From: proposal/<n>`;
- its stages are `stage.start` and `stage.end` on `stage/<chore>/<stage>`, `chore/<name>` and `agent/<slot>`, the end with `Result` and `Head` and no `Tasks`; `slot.free` names the slot and the chore;
- a refusal carries the act refused, as any does;
- `Why` is composed from names (`plan(<bolt>): add chore <name>`); no entry holds the chore's words.

`crew trace <bare name>` tries a unit, then a chore, then a bolt, then a signal.

### Consequences

- Proposals 1 and 3 stand as written. Their archive units can be approved as units now, or the planner replaces them with chores once the kind has landed; that is the planner's call under the user's approval.
- The `bolt-plan` spec's "the plan holds only Bolt and Unit records" and the `bolt-teams` spec's places and stages are amended by the change that builds this, not before.
- The conductor's, coder's, verifier's and planner's briefs each gain a chore paragraph; the README's and the skill's one-line definitions of a unit stay true.
- The run record's acts and `crew trace`'s lookup grow by one kind.

## Pros and cons of the options

### Option 1: its own kind, beside unit and fix

- Good: "a unit is one OpenSpec change" stays true everywhere; the user's words ("a chore kind beside unit and fix") and fix's existing shape (its own command) are followed.
- Good: the record shares the unit's fields, so placement, order, dependencies, proposals and the queue work the same way and the same checks apply.
- Bad: a mirrored command family and a third record type to read.

### Option 2: a unit of kind chore

- Good: Flywheel Next's shape exactly, and the fewest new commands.
- Bad: every sentence that defines a unit as one OpenSpec change becomes false, and every unit command must branch on kind (construct, approve, the stage rules, the proposal's rendering), which is the same work spread thinner.

### Option 3: a fix with a plan record

- Good: reuses the fix's worktree and merge.
- Bad: a fix is reactive and the conductor's, a chore planned and the planner's; a fix gets no verify, and the user asked for one; mixing them blurs the one clear line crew has between planned and reactive work.

### Option 4: chores on main outside a bolt

- Good: Flywheel's shared-line chore, and a bump that every bolt needs reaches main at once.
- Bad: a second path to main beside landing, bypassing the bolt's proof and the user's word; the same need is met by a chore marked `--unblocks` in the bolt that needs it, or a chore in the next bolt.

## More information

A chore is where crew tests Flywheel Next's chore on real work with two simplifications: no shared line, and the offer made as a signal routed by the planner rather than a session's own exit. What running it shows about those two is worth a signal.

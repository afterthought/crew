# Design

## Context

Record 0001 decided the chore on 2026-10-05, before most of what a unit now is: stages ending at their deliverables (record 0007), `After` as code one unit builds on (0011), units built at once and read in batches (0014), Touches and forecasts, amendments that run construct again, the proposal's card with a choice per new unit (0018). `plan.11` holds the decision as a rule, `signals.7` the batch of chores taken row by row, and `_open.md` lists both as not built.

A unit today is a `Unit` record of `plan.rec` on the flywheel's branch; `plan.py` writes it through `Op`s that a direct run and a proposal share (`plan.3`), reads its stage from gather.py's survey of its kit (`Stages`, `state.2`, `plan.12`), and runs its stages through bash `crew unit run`, which takes a slot, asks `plan _run` whether the stage may start and what its prompt is, and starts a fresh agent sent that prompt (`teams.2`, `teams.15`); a wait ends the stage at its deliverable (`teams.4`). A fix is the template for work with no change: its own branch and place from the bolt, a code stage told `Fix: …` whose deliverable is a commit on its branch, and a merge through the kit's hooks.

The rules this rests on: `state.1`, `state.2`, `state.3`, `state.4`, `roles.1`, `roles.3`, `roles.4`, `read.1`, `read.4`, `code.1`, `code.2`, `code.4`, `code.6`, `code.7`; `plan.1`, `plan.3`, `plan.5`, `plan.7`, `plan.9`, `plan.10`, `plan.11`, `plan.12`, `plan.13`; `teams.1`, `teams.2`, `teams.4`, `teams.5`, `teams.9`, `teams.15`; `record.1`, `record.3`; `signals.4`, `signals.7`; `briefs.2`, `briefs.11`, `briefs.12`, `briefs.13`; `tests.4`, `tests.6`, `tests.11`, `tests.12`; `docs.2`, `docs.4`, `docs.5`. Pages whose area this touches: `plan.md`, `teams.md`, `record.md`, `signals.md`, `briefs.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- A chore is planned, built, read and recorded with nothing kept by hand, by the same hands and the same rules as a unit wherever record 0001 says it mirrors one.
- A unit's and a fix's behaviour do not change.
- A batch of chores reaches the user as one proposal they take or leave row by row.

**Non-Goals:**
- Curation on a cadence, the other half of `signals.7`: `curation-runs-on-a-cadence` builds it, after `curate-into-agenda`.
- Chores outside a bolt, merged straight onto main (record 0001, option 4): main changes only when a bolt lands (`state.3`).
- Running any of the chores waiting for the kind: chores run through a team.

## Decisions

### The plan marks a chore with `Kind: chore` on a Unit record

The Unit descriptor allows a `Kind` field, `%type: Kind enum chore`; a record with `Kind: chore` is a chore and every other is a unit. A chore record holds a unit's fields: `Unit` (its name, the key), `Repo`, `Bolt` (absent while queued), `Kind`, `Intent` (its words), `After` and `Source`; never `Amended`, which crew's own rules refuse on a chore (`plan.1`). `Plan` reads the two kinds apart: `units()` and `unit()` are the units alone, `chores()` and `chore()` the chores, and `work()`, `item()`, `work_of()` and `queue()` both, in file order. Every reader that is about OpenSpec changes, batches, Touches, forecasts, amendments, keeps reading units alone; every reader about work in a bolt reads both.

Record 0001 says a chore is "a third record beside Bolt and Unit" and that "chores sit in the same file in build order with the units". In recutils a record belongs to the set of the descriptor above it, so records of two sets can never interleave, and the file's order is the build order (`plan.13`, the `bolt-plan` spec). Both sentences cannot hold; this keeps the second, the one the plan's order and `After` across kinds rest on, and marks the kind by a field the schema allows instead of by a record set. The record's set keeps its name, so the plan's file reads `Unit: <name>` above `Kind: chore`; in every command, view, brief and spec a chore is called a chore, and "a unit is one OpenSpec change" stays true of every unit. Record 0001 is amended to say so, on the user's ruling of 2026-10-12.

Alternatives considered: a `Chore` record set with an `Order` field (state the plan's order twice, and the file's order stops being the plan); chores after the units with a separate order (`After` and `--before` across kinds lose their meaning); a `Kind` field on every unit (`Kind: unit` on hundreds of records that say nothing).

### The commands mirror a unit's

`crew chore add <chore> "<words>" --bolt|--repo [--source]… [--after]… [--before] [--signal] [--unblocks]`, `crew chore order <chore> --before|--first|--last`, `crew chore after <chore> <name>…|--none`, `crew chore move <chore> <bolt>|queue [--unblocks]` and `crew chore drop <chore> "<reason>"` are parsed into the same `Namespace` a unit's command is, its subject in `unit`, and built by the same `Op` functions (`op_unit_add`, `op_unit_order`, `op_unit_after`, `op_unit_move`, `op_unit_drop`), which take the kind from `a.cmd`: an add writes `Kind: chore`; the others first look the subject up and refuse a record of the other kind, naming it and its own command ("x is a chore: crew chore order x …"). `--before`, `--after` and `unit after`'s names may be either kind, within one bolt; a drop takes the dropped name out of any `After` of the group, unit or chore. `--signal` writes the route move with `Target: chore/<name>` (`signals.4`). Move keeps the unit's rebase of a place onto the new bolt for a chore too, its branch `chore/<name>`. `PLAN_WRITES`, `may_write` and `conductor_scope` read `("chore", sub)` as `("unit", sub)`: the planner by proposal, a conductor `chore order` and `chore after` within its bolt, the design agent `chore add --repo`, the user everything (`roles.1`). `chore split` and `chore amend` do not exist, so a chore's words change by a drop and an add in one proposal.

### A name is taken once in a kit

A unit's and a chore's name share the plan's key, so the plan refuses a second record by either. `name_free` refuses a name the kit's main has an OpenSpec change by, open or archived (`plan.7`), and now also a name main's history holds a chore trailer for, so a chore that has landed and left the plan keeps its name, and its trailer never makes a new chore by that name read `landed`.

### A chore's stage is read from its kit

gather.py, in the one read per host (`plan.12`), adds for each kit: `chores`, the names in `Chore:` trailers on main (`git log --grep` on the trailer line, then `%(trailers:key=Chore,valueonly)`); for each bolt, `chores`, the same on `bolt/<bolt>`; and `chore_places`, each worktree directly in `<kit>/places/` on a `chore/<name>` branch, with its path, branch, bolt (its upstream), head, head's time and `ahead`, the number of commits beyond `bolt/<bolt>`. `Stages.of` reads a chore by these, the first rule that holds:

| stage | read from |
|---|---|
| `queued` | the plan: no bolt |
| `unknown` | its team's host did not answer, or its place tracks no bolt crew can read (`read.1`) |
| `landed` | main's history holds a commit carrying `Chore: <name>` |
| `merged` | `bolt/<bolt>` holds one |
| `verify` | its place holds a commit beyond the bolt: code has delivered, and verify is next |
| `code` | its place holds nothing beyond the bolt yet |
| `ready`, `waiting` | no place: ready once each `After` has merged into the bolt or landed |

Record 0001 read code and verify from "the stage its slot last ran", the team's stages file; as amended it reads them from the kit, which says it without that file: a place holding commits of its own is code delivered, which is what verify needs, its own being its first-parent line with no merges, so what it took of others (below) never counts; whether verify has run is the run record's (`verified`), as it is for a unit's settle. A bolt's state reads `landed` once every unit and chore of it has.

### `After` means for a chore what it means for a unit

`After` says the dependent builds on the other's work (`plan.13`), and a chore is no different: the dependent starts once there is something committed to build on, never waiting on a merge, and merges only after it has merged. For a unit that is its construct's change, `planned` or later; for a chore it is its code, `verify` or later, its commits in its place (`built_on`, `CODED`, the user's ruling of 2026-10-12). `after_met` reads every dependent, unit or chore, by that one rule. A dependent's new place takes each unmerged unit's or chore's head as it stands (`took_from`, `TAKE` given each one's branch, `unit/<name>` or `chore/<name>`): a unit's at its construct, a chore's at its code, each start's `Took` recording the heads, which `took_heads` reads from either start. Every taking is a merge commit of its own, never a fast-forward, so a chore's own work is its first-parent line with no merges: its stage, its code's deliverable (`gather.own_head`) and its merge's trailer check (`CHORE_LOG`) never count what it took. When what a unit or chore comes after merges, `rebase_dependents` rebases its place onto the bolt, leaving out what it took as it took it (`rebase_leaves_out`), a chore's merge found on the bolt by its trailer (`landed_at`); a chore's rebase that conflicts is said, since no forecast reaches a chore, and its merge meets it. A chore's code run again after a dependent took it reaches the dependent at its rebase, not as an amendment: an amendment is a construct run again, which a chore has not.

### Running a chore's stages

Bash `crew chore run <chore> code|verify|merge ["<words>"]` is `crew unit run`'s path with the kind given: `plan _team-of` finds its team, the command forwards to the team's host (`code.3`), refuses while the team is down, reaps, takes the chore's slot or a free one as `<slot> chore <name> <kit>/places/chore-<name>`, asks `plan _run <chore> <stage> [words] --chore`, opens the slot's pane and runs the stage through `run_stage` (`teams.2`, `teams.15`), recording `stage.start` on `stage/<chore>/<stage>`, `chore/<name>` and `agent/<slot>`. Construct and settle are no chore's stages, and bash refuses them with the three a chore has.

`plan _run --chore` (`chore_check`) reads the chore's stage and decides by `chore_refusal`, a function of facts (`code.7`):

- any stage of a queued chore, or of one whose bolt no team holds, is refused as a unit's is;
- any stage of a merged or landed chore: "a defect in it is a fix, and new maintenance a new chore";
- code while it is `waiting`, an `After` having nothing committed to build on: "it comes after …, which has nothing committed to build on yet";
- code on a ready, coding or verified chore; the place is made at its first code from the bolt, tracking it, and takes what it comes after (`TOOK`);
- verify once its place holds a commit of its own beyond the bolt;
- merge once it is in verify and has delivered a verify since its last code began (`verified`, the same reading a unit's settle uses), once every commit of its own carries `Chore: <name>`, read with `CHORE_LOG` on the team's host and refused naming each commit that lacks it, since a commit without the trailer would leave the chore never reading merged and crew checks what the brief asks rather than trusting it (`roles.3`), and once each `After` has merged (`teams.5`).

`plan _run` without `--chore` on a chore, and `--chore` on a unit, is refused naming its kind and the command that takes it; the refusal is recorded on the chore's objects, read into `CONTEXT` once the record is found. The prompts are:

- code: `Chore <name>: <its words>`, then the conductor's or the user's words;
- verify: `Verify chore <name>: <its words>`, then theirs;
- merge: `Merge <name> into bolt/<bolt>: <the kit's merge command>`, as a unit's (`teams.5`).

`transcript.STAGE` reads the first two as stage prompts, the conductor's (`roles.4`, `signals.5`), and `crew.never_started` tells a chore's stage to run again with `crew chore run`. A code or merge run on a chore in verify ends its verify row, whose card the conductor closes, as for a unit (`ends_row`).

### A stage ends at its deliverable

A chore's stage line in the team's stages file names the chore and the object `chore/<name>`; `Owed` reads the kind from the object. The deliverables are record 0007's rows: code, a commit on `chore/<name>` since the stage began (the fix's row); verify, a report `verify-<name>-<stamp>.md` saved since it began (the unit's); merge, `bolt/<bolt>` holding a commit carrying the chore's trailer. Its end is recorded on `stage/<chore>/<stage>`, `chore/<name>` and the agent, with the stage crew then reads and the branch's head, and no tasks (`record.5`).

### Slots and places

A slot holding a chore is freed once the chore has landed, merged, been dropped from the plan or left the team's bolts, its agent no longer working (`teams.1`); `slot.free` names `chore/<name>`. Its place, `<kit>/places/chore-<name>` on `chore/<name>`, is crew's when its folder and branch agree, and its work is over once it has landed, merged into the bolt its branch tracks, or no plan has it (`plan.9`); its branch then goes as a unit's does, judged as `plan.10` has it once `a-drop-keeps-unmerged-work` lands. `gather.upstreams` reads `chore/` branches.

### Batches, review and the landing

A chore has no construct, so no delivered construct ever names it and `due_changes` never counts it: no batch holds a chore, `batch.due` never names one, and a bolt's landing waits on a batch only for its units (`briefs.12`). The landing row is offered once every unit and chore of the bolt has merged; `crew bolt land` lands once every one has landed, removes the chores with the units, and names them on its entry. A chore's verify report is a rail row, `verify/<chore>/<stamp>`, whose card is its conductor's (`briefs.11`, `briefs.13`); the card hook allows a conductor that key for a chore of its bolt.

### Proposals and the card

The five chore commands are proposable (`PROPOSABLE` is every `Op`). `objects` names `chore/<name>`, `summary` says "add chore x to b", "move chore x to b", "drop chore x", and `touched_by` reads a chore's commands as a unit's. `describe` reads "**New chore `x`** in bolt `b`" with "Chore: <its words>", the bolt's goal, its signal and its sources; the other four alike. The card counts a chore new to a bolt among the new work (`new_units`), so its question offers it as an option the user can clear, the option's words starting "Chore:", and a question holding only chores asks "Which chores go in?". `crew plan approve <n> --clear <chore>` leaves it out exactly as it leaves a unit out (`plan.3`, record 0018). A batch of chores curation routes is then one proposal: `bolt new` and a `chore add` per chore, each the user's to keep or clear (`signals.7`).

### Views

`crew bolts` lists a bolt's chores among its units in build order, its stage shown as `chore <stage>`, and queued chores the same way; its JSON gives each unit and queued entry `kind`. The board's ledger rows, planned bolts and queue carry `kind`, and its text marks a chore by `stage_of`, which each agent's view draws its ledger with too (`board.agent_views`, `code.8`), so the mod shows a chore with no change of its own: `plugin/hooks/status.js` draws the view's lines and reads no unit's fields; the page's lineage reads `chore/<name>` with its words. `crew sites` lists a chore's place as a unit's.

### The run record

`chore/` is a kind of object: `record.KINDS` holds it, a trace's bare name tries `unit/`, `chore/`, `bolt/`, then `signals/`, and a chore's move is followed as a unit's (where it moved from is not what it came from). The acts are `chore.add`, `chore.order`, `chore.after`, `chore.move` and `chore.drop`, each `On` the chore and its bolt or `queue/<kit>`; `named()` gives a refused chore command its chore's objects. No entry holds a chore's words (`record.3`).

### Briefs and docs

- **coder.md**: *A chore*: the prompt, doing exactly what the words say in the kit's conventions, each commit `chore:` with `--trailer "Chore: <name>"`, nothing under `openspec/` but `openspec archive <change>` for a change whose every task is ticked, and stopping through `crew needs` when the words need a decision or the change has an open task.
- **verify.md**: *A chore*: every commit beyond the bolt (`git log @{upstream}..HEAD`) serves the words and nothing else and carries the trailer, `openspec/` untouched but by such an archive, the tests of what changed pass; the report saved as a unit's.
- **conductor.md**: the chore rows of the stages table, chores in the building loop in the plan's order, its verify card, and that a chore is never constructed nor batched.
- **planner.md**: the test (unit, fix, chore, in that order), `Do: chore add …`, and a batch of chores as one bolt the user takes row by row.
- **design.md**: the design agent may queue a chore with `crew chore add --repo`, as it queues a unit.
- `tests/t-briefs.sh` pins each with a phrase (`tests.6`); README, the crew skill, `plugin/bin/crew`'s usage and `plan.py`'s say the commands (`docs.2`).
- Rules: `plan.9` adds `chore/` branches; `plan.11` adds that a chore is a Unit record marked `Kind: chore` and that `After` holds for it as for any unit; `plan.13`'s details name a chore's code as what a dependent builds on; `teams.1` and `teams.5` say a chore beside a unit and a fix; `plan.11`'s and `signals.7`'s details say what builds them; `_open.md` drops the `plan.11` item and names the chores waiting. This change edits `docs/architecture/`, which `docs.7`, proposed and not accepted, would leave to the design agent; the rules are amended in the same commit as the code that changes them, as `docs.5` has it.

### The chores waiting for the kind

None runs here. Each goes through a team as `crew chore add … --bolt <bolt>` in a proposal, or `--repo <kit>` from the design agent:

- **Archives of changes landed open.** `_open.md` names five, a-decision-is-shown-whole, fix-place-names-its-bolt, rulings-rest-on-readings-and-intents-name-outcomes, what-waits-on-the-user-is-one-list and worktrees-go-with-their-work: they were archived by the user's sweep of 2026-10-10 and the item is stale. On crew's main at fd0d3d8, `openspec list` shows fourteen open changes with every task ticked: a-batch-cards-notes-are-its-note-and-its-sessions, a-board-shows-the-flow-in-the-terminal, a-card-lost-to-its-owner-is-posted-again, a-cards-session-ends-with-its-card, a-carrying-fix-is-judged-by-its-commits, a-proposals-card-shows-the-change-and-lets-new-units-be-left-out, a-record-is-accepted-on-the-users-yes, a-stage-builds-from-its-sources-over-its-intent, a-stages-prompt-is-taken-or-sent-again, an-amendment-runs-construct-again-itself, an-image-on-a-card-is-uploaded, page-of-the-flow, the-page-shows-the-board, units-build-at-once-and-are-reviewed-in-batches. Each archive is a chore, in an order that respects the deltas one modifies of another (a-proposals-card-… after an-image-on-a-card-is-uploaded). checked-capture (12 of 16) is not due: an archive chore of a change with an open task stops.
- **The brief fixes with no phrase in `tests/t-briefs.sh`** (`tests.6`): 21d82af, ec593d5, 63bab58, e3d75cb and 902336e. One chore adds a phrase for each rule they added.

## Risks / Trade-offs

- [An older crew reads a plan holding a chore] → its schema refuses `Kind`, and it refuses the whole plan, naming `recfix`'s message (`read.1`). Every host is brought up to main in the landing's step; until then no chore is added.
- [A coder forgets the trailer] → the code stage still delivers its commit, verify names the commit, and the merge is refused naming it, so the chore never merges unseen into a bolt where it would never read merged.
- [A chore's trailer is borrowed] → a commit on main or a bolt carrying `Chore: <name>` for a chore it is not makes that chore read merged or landed. Only crew's chores write the trailer, and a name is taken once in a kit.
- [A dependent took a chore's head, and the chore's code runs again] → the dependent holds the chore's work as it took it until the chore merges and its place is rebased onto the bolt, leaving the old head out; no notice reaches it before, since a chore has no construct to run again.
- [A chore conflicts with a unit] → no forecast reaches either; the later of the two to merge meets it at its merge's rebase and resolves it there, as the coder brief already says for a merge.
- [Touching `docs/architecture/`] → a landing may conflict on `_open.md` (`docs.7`'s reason); the edits are small and in their own commits.

## Proof in dev

None: every behaviour is proved by the logic, contract and end-to-end tiers.

## After deploy

None.

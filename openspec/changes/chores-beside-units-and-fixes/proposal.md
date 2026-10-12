# Chores beside units and fixes

## Why

crew builds two kinds of work. A unit is one OpenSpec change, written by construct, read by the user in a batch, then coded, verified and merged; a fix is the conductor's answer to something broken on its bolt, with no plan record. Maintenance that decides nothing and fixes nothing broken has had to ride as a unit: a tool-version bump went through construct and a review of a change that said nothing, and the archive of a proven change has no way in at all. Record 0001 decided a third kind, the chore, and `plan.11` states it: planned maintenance built inside a bolt by code, verify and merge, with no construct and no review, changing nothing a spec says must be true. `signals.7` adds that a batch of chores curation routes is proposed as one bolt the user accepts or declines row by row. Neither is built (`_open.md`), and work is waiting on it: fourteen changes on crew's main whose every task is ticked and that were never archived, the brief fixes `tests.6` names with no phrase in `tests/t-briefs.sh`, and the archive of every change still landing open until `a-merged-change-is-archived` lands.

## What Changes

- **The plan marks a chore.** A chore is a record of the plan's Unit set marked `Kind: chore`, a field the plan's schema allows (`%allowed`, `%type: Kind enum chore`, `plan.1`), with a unit's other fields: its name, repo, bolt (none while queued), its words as `Intent`, sources and `After`. It sits in the file among the units in build order, and `After` may name a unit or a chore either way round. A name is taken once in a kit, by a unit or a chore: refused when the plan has it, when the kit's main has an OpenSpec change by it, or when main's history holds a chore by it.
- **Commands mirror a unit's.** `crew chore add|order|after|move|drop` take a unit's flags and make its refusals, `--signal` and `--unblocks` among them, and are written by the same hands: the planner by proposal, a conductor `chore order` and `chore after` within its bolt, the design agent `chore add --repo`, the user anything. There is no `chore split` and no `chore amend`: a chore's words change by a proposal that drops it and adds it again. `crew unit …` naming a chore, and `crew chore …` naming a unit, is refused naming its kind and the command that takes it.
- **A chore's stage is read from the kits (`state.2`).** `landed` when main's history holds a commit carrying its `Chore: <name>` trailer, `merged` when `bolt/<bolt>` does, `verify` when its place holds a commit beyond the bolt, `code` when its place holds none yet, and `ready` or `waiting` with no place, by whether each `After` has merged into the bolt; `queued` with no bolt; `unknown` when its host does not answer. Nothing is recorded by hand.
- **A chore is built by code, verify and merge.** `crew chore run <chore> code|verify|merge ["<words>"]` starts the stage in a free slot of the team, a fresh agent at that stage's effort, on `chore/<name>` branched from the bolt in `<kit>/places/chore-<name>`. Code is told `Chore <name>: <its words>`, commits as `chore:` with a `Chore: <name>` trailer on each commit, and touches nothing under `openspec/` but the archive of a change whose every task is ticked; verify is told `Verify chore <name>: <its words>`, changes nothing, and saves its report as a unit's verify does; merge merges through the kit's merge hooks as a unit does. crew refuses any stage before every `After` has merged, verify before the place holds a commit, merge before verify has run since the last code or while a commit beyond the bolt lacks the trailer, and any stage of a merged or landed chore. Each stage ends at its deliverable (`teams.4`, record 0007): code at a commit on its branch since it began, verify at its report, merge at the bolt holding the chore. `crew chore wait` and `crew chore free` are a unit's wait and free.
- **There is no construct and no review.** `crew unit run <chore> construct`, or any `crew unit run` on a chore, is refused naming its kind. A chore never enters a review batch, the planner is never told a batch is due for one, and a bolt's landing never waits on a batch for one. Its verify report is a rail row and its conductor's card, `verify/<chore>/<stamp>`, as a unit's is.
- **A proposal carries chores, and the user takes them row by row (`signals.7`).** A proposal may hold the five chore commands; `crew plan proposed` reads "New chore `<name>` in bolt `<bolt>`" with its words; the card counts a chore new to a bolt among what the user can leave out, its option's words starting "Chore:", and `crew plan approve <n> --clear <chore>` leaves it out as it leaves a unit out. A batch of chores is a proposal of one bolt whose every chore the user keeps or clears.
- **Every view shows a chore as one.** `crew bolts` lists a bolt's chores among its units in build order, marked `chore`, and queued chores in the queue; the board's ledger, queue and planned bolts mark them; `crew bolts --json` and `crew board --json` give each `kind`.
- **The run record names `chore/<name>`.** Its writes are `chore.add|order|after|move|drop`; its stages `stage.start` and `stage.end` on `stage/<chore>/<stage>` and `chore/<name>`; a slot freed names it; `bolt.land` and `bolt.drop` name the chores they remove. `crew trace <bare name>` tries a unit, then a chore, then a bolt, then a signal.
- **The rest of crew counts chores where they are work.** A team holds its bolt until every unit and chore of it has landed; a bolt lands, and its landing row is offered, once every unit and chore has; work a held bolt needs goes ahead of its first unmerged unit or chore; a slot holding a chore is freed once it has merged, landed, been dropped or left the bolt (`teams.1`); its place goes through the kit's `wt remove` once its work is over (`plan.9`). A chore takes no part in Touches or forecasts: it declares nothing, and a conflict it meets at its merge is its merge agent's.
- **The briefs and docs say so.** The coder's, verifier's, conductor's, planner's and design agent's briefs each gain what a chore is to them, pinned by `tests/t-briefs.sh` (`tests.6`); README, the crew skill and the usage headers say the commands (`docs.2`); `plan.9`, `plan.11`, `plan.13`, `teams.1` and `teams.5` are amended, `signals.7`'s details say what is built, and `_open.md` loses the chore item.
- **The chores waiting for the kind are named** (design: *The chores waiting for the kind*). None is run here: chores run through a team.

## Capabilities

### New Capabilities

- `chores`: the chore kind: how the plan marks it, its commands and who writes them, its stage read from the kits, its stages and their refusals and deliverables, its slot and place, its place in proposals and on the card, its views and its run record.

### Modified Capabilities

- `bolt-plan`: the plan holds Bolt records and Unit records, a Unit record marked `Kind: chore` being a chore.
- `plan-proposals`: a proposal may hold the five chore commands; a conductor writes `chore order` and `chore after` within its bolt and the design agent `chore add` into a queue.
- `run-record`: an entry may name `chore/<name>` and `stage/<chore>/<stage>`.

## Impact

- `plan.rec`'s Unit descriptor gains `Kind`; a branch's plan takes it at its next write, as `in_step` brings every descriptor in step. A plan written by this crew is read by an older crew only until it holds a chore, whose `Kind` the older schema refuses: every host is brought up to main in the landing's step (CLAUDE.md, *After landing*).
- gather.py reads each kit's chore trailers on main and on each bolt, and each chore's place, in the same one read per host (`plan.12`).
- No change to how a unit or a fix is built, read or recorded. A unit's name is now also refused when main's history holds a chore by it.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`).
- `code.8` is not on main: when it lands, `board.agent_views` and `plugin/hooks/status.js` mark a chore as the board does.

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/crew.py
plugin/lib/record.py
plugin/lib/transcript.py
plugin/lib/board.py
plugin/lib/page.py
plugin/lib/sites.py
plugin/bin/crew
plugin/roles/coder.md
plugin/roles/verify.md
plugin/roles/conductor.md
plugin/roles/planner.md
plugin/roles/design.md
plugin/skills/crew/SKILL.md
README.md
tests/py/
tests/contract/
tests/t-journey-chores.sh
tests/t-briefs.sh
tests/moon.yml
docs/architecture/plan.md
docs/architecture/teams.md
docs/architecture/signals.md
docs/architecture/_open.md
```

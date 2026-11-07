# Design: a forecast reads what a unit already took

## Context

The proposal gives the box's case. This change touches the areas of `plan.md` (`plugin/lib/plan.py`), `tests.md` (`tests/`) and `docs.md` (README, `openspec/`). Rules it relies on:

- `plan.13`: `After` names a unit whose code the dependent builds on, and the dependent's place takes its head. A dependent is not forecast on that unit's own work its place took once a rebase or settle rewrote it: it is forecast from the head its place took (`teams.12`).
- `teams.12`: a conflict `git merge-tree` forecasts reaches the later unit once, and never asks a unit to take the work of one that comes after it.
- `teams.14`: a forecast that reaches a unit waiting to merge starts a settle. So a false forecast costs a settle stage.
- `read.1`: what crew cannot read is said and decides nothing. A pair git cannot tell about is named and forecast nothing.
- `code.7`: the decision (`forecast_base`, `forecasts_due`) is a function of facts. git's reads stay outside it (`git_holds`, `shared_beyond`, `merge_tree`).
- `tests.4`, `tests.11`: the decision's cases go in the logic tier, and what crew assumes of git goes in the contract tier.
- `roles.5`: crew builds no mechanism one of the family's tools is designed to hold. Decision 3 reads sluice's forecast for this.

It departs from no rule.

### Where the bolt became the base

Read in `plugin/lib/plan.py` at `90e3df74`. `reach`, on each conductor's wait, builds `took` from this host's run record: `took_heads`, the `Took` of every construct or code start of the unit. It passes `took` to `forecasts_due`. For a pair (a later unit, a unit ahead of it), `forecasts_due` called `conflicts(other's head, its head, base)` with `base = took[unit][other]` whenever the other was in the unit's `After` and a head was taken, and with git's own merge base otherwise.

`Took` is written once, by TAKE at the start of construct, and only while the place holds no work of its own. Nothing records a later take. That covers a merge the agent makes in its place when an amendment tells it the unit ahead was constructed again, and a settle that merges the unit ahead's new head. Its record ends at the settle's commit (`forecast_orders` reads that a branch holds the other's work, but only to order the pair). So once the later unit holds a newer head of the earlier one than its `Took`, the forecast still runs from the old head.

For every file the earlier unit changed after that head, the old head reads as the bolt. merge-tree then sees both sides change those files from the old content: the earlier unit's side with its own lines, and the later unit's side with the same lines plus its own edits beside them. Hunks that touch or overlap conflict. That is the box's case. Every file named at 02:04Z is one the warehouse unit changed in its code stage, after 9bb35a9, and the gateway unit's settle had merged 53bd5bb. The settle path, the merge-in-place path and an `After` that is not recorded are the same fault: each is a take that `Took` does not hold. git holds every one of them.

## Decisions

### Decision 1: what a unit holds is read from git, newest first

`forecast_base(head, ohead, taken, holds, shared)` gives each unit pair's base from three facts git answers in the kit's main checkout:

1. **The later unit holds the other's head** (`holds(ohead, head)`, `git merge-base --is-ancestor`). It holds all of that unit's work, so there is nothing to forecast and no settle starts. merge-tree is not asked.
2. **Nothing was taken**, or the place no longer holds the head it took, or the other's line still holds that head. Their merge base is the base. git takes it at the newest commit both hold: the head the place took, or any newer head merged since by whatever hand. This is the box's case before and after the settle.
3. **The place still holds the head it took, the other's line no longer does, and the two share nothing beyond the bolt** (`shared(head, ohead)`, `git merge-base --all` and then `git rev-list --not <bolt>`). Then the head it took is the base. This is `plan.13`'s case: the other's rebase or settle rewrote its own work, and the later unit carries that work as it took it. When the two do share work of the other's beyond the bolt, the later unit has merged the other's rewritten line since. Their merge base is then that newer work, and it is the base.

Any of these that git cannot answer makes the pair unread. `reach` says so on standard error, naming both units, and forecasts nothing for them (`read.1`). The bolt pair is unchanged: a unit against `bolt/<bolt>` is compared from their merge base, as before.

The `After` gate on the taken head goes. A head the place took is a base only where git says the place still holds it, so an order lifted since the take no longer turns the other's carried work into a conflict of the later unit's.

Considered and not taken:

- **Always git's own merge base.** That is right for every case but `plan.13`'s rewritten one, where the merge base is the bolt and the later unit would be forecast again on the other's own rewritten files. `plan.13` rules that out.
- **Record each later take as a `Took`** (on a settle's end, or by reading merges into the place). That is a second record of what git already holds. A merge the agent makes by hand would still be missed, and the brief rules out reading what a unit holds from a commit's words (TAKE's `chore(<unit>): build on <other> as it stands`, a settle's subject).
- **Forecast from both bases and keep the paths both name.** That doubles merge-tree on every wait. It also leaves the answer to a coincidence of what each base names, where git can say outright what the later unit holds.

### Decision 2: no forecast where the later unit holds the other's head

Where the later unit holds the other's head, the merge from git's own base is clean anyway: the other's head is the base. Deciding it first, by `--is-ancestor`, makes it a fact of the decision rather than an outcome of merge-tree on a base the record chose. It holds whichever base the record would have named, and it costs one git call in place of a merge.

### Decision 3: sluice's forecast reads the same thing for what is submitted, and cannot serve the units' forecast

sluice forecasts a head as it would be submitted now (its statement, clauses 64, 65 and 47a; `sluice-core` `ops.rs` `forecast_on`, `local_refs.rs` `form`). It forms the branch's revision with each entry ahead of it in the queue, and then the head onto that, each step by `git merge-tree` from git's own merge base. It never names a base. So sluice reads what this change brings crew back to: git's merge base between the work and what it lands onto. A head that holds an entry's head meets no conflict from it there.

It cannot serve the forecast between two unmerged units. A unit in code or verify has submitted nothing, so it is no entry in any queue, and sluice has no way to put one place's head ahead of another's. Nor does sluice know the head a place took, which `plan.13`'s rewritten case needs. It could serve a unit's forecast against its bolt and whatever is queued into it (`sluice submit bolt/<bolt> --check` from the unit's place), as crew already has it serve the bolt's against main (`teams.21`). That is a separate move, and this fix does not make it.

sluice is the one owner of a forecast against what is submitted to a branch. crew's forecast between places not yet submitted is crew's own, and this fix is a correction of it, not a new mechanism (`roles.5`). sluice is not changed.

## After deploy

None. The logic and contract tiers prove what the fix does. The box runs it once its crew moves to a commit that holds it, through swancloud's pin or live worktree, and nothing about that can be checked by hand.

## Task notes

**1.1** `plugin/lib/plan.py`: `forecasts_due(live, bolt, bolt_head, conflicts, holds, shared, done, took, after_of=None)`. A unit pair takes its base from `forecast_base`. A held pair is skipped, and an unread pair is added to `unread`. `forecast_base` is Decision 1 as a decision of facts. `tests/py/test_forecast.py`: `TestDependent` drives `forecasts_due` with git's answers as pairs:

- the box's case, held whether a head was taken or not, with merge-tree not asked;
- the unit ahead moved on (its merge base);
- the rewritten case (the taken head), with an overlap of the later unit's own still forecast;
- the rewritten unit's newer work merged since (its merge base);
- a head no longer held;
- no `Took`;
- a lifted `After`;
- git unable to tell.

`TestBase` drives `forecast_base` alone. The existing callers pass git answers saying no unit holds another's work.

**1.2** `plugin/lib/plan.py`: `git_holds` (`merge-base --is-ancestor`, None on any exit but 0 or 1) and `shared_beyond` (`merge-base --all`, no common ancestor read as False, then `rev-list -n1 <bases> --not <bolt head>`, None when the bolt's head is unknown or git fails). `reach` passes them with the bolt's head as gathered. `tests/contract/test_git.py` runs `forecasts_due` on real git through `merge_tree`, `git_holds` and `shared_beyond`, from two units cut from the bolt with the later one's place taking the earlier one's head:

- the later unit merged the earlier one's new head in its place and changed the next line: no forecast, where merge-tree from the taken head, or from the bolt, names the file;
- the earlier unit moved on: forecast on its own new overlap alone, where the bolt names the design both changed too;
- a newer head merged after the one taken, then a new overlap: forecast on the overlap alone, where the taken head names the merged line too;
- the existing rewritten case: forecast nothing.

**1.3** README, the paragraph on dry runs: a later unit with one ahead of it is compared only beyond the newest of that one's work it holds, read from git, and not at all when it holds its head.

**2.1** `tests/suite --affected`, against the merge-base with main.

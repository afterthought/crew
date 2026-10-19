# Design

## Context

Why this change exists is in proposal.md. What crew does today, on main at e91f51f2:

- On every conductor's wait, `reach` in `plugin/lib/plan.py` forecasts each unmerged unit against the bolt and against each unmerged unit ahead of it (`forecasts_due`). For a conflict between two units, `forecasts_due` returns a flag that is true unless the later unit already comes after the other, and `reach` then writes `After` at once, in the conductor's name: subject `plan(<bolt>): <unit> after <other>, forecast to conflict`, act `unit.after`, on `unit/<unit>` and `bolt/<bolt>`. The forecast then reaches the unit (`deliver`): told, carried in its next prompt, or as a settle stage.
- A settle ends delivered at a commit on its branch made since it began, or short when its agent says through `crew needs` that nothing needs to change (`coder.md`); `crew needs` records that end (`Ended: short`) before the conductor's wait takes its words. The conductor then merges the unit.
- With `After` standing, the merge is refused until the other unit merges (`stage_refusal`). Nothing lifts the order but a plan write, so the planner proposes one and the user gets a card. Once lifted, nothing records that it was, and the next forecast on new heads finds the unit not after the other and writes the order back.
- A unit's merge is also refused while its branch holds another unmerged unit's change open (`carried_refusal`, `teams.17`), naming that unit as merging first. That refusal, not `After`, is what keeps a unit that took another's work from merging ahead of it when no order stands.

Pages of `docs/architecture/` whose areas this touches: `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/bin/crew`'s usage), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (README, `openspec/`). Rules relied on: `plan.13`, `teams.12` and `teams.14` (the rules this builds), `roles.1` (the conductor sets `After` within its own bolt), `state.1`, `state.2`, `read.1`, `code.2`, `code.7`, `code.8`, `roles.3`, `tests.4`, `tests.6`, `tests.10`, `tests.11`, `docs.2`, `docs.6`, `docs.7`. Nothing here departs from a rule.

## Goals / Non-Goals

**Goals:**
- A forecast never orders two units by itself; a settle that takes the other's work does, once for a pair.
- An order crew wrote whose settle found nothing to change goes without a card, including those crew wrote before this change.
- An order someone else lifted is never written back.

**Non-Goals:**
- A forecast that reaches a unit by a tell or in its next prompt, whose stage then takes the other's work. The rules name only the settle; such a unit gets no order, and the merge refusal for a carried change holds it until the other merges. Named for the design agent.
- What a forecast says to the unit. Its words are unchanged.
- A check that refuses a proposal lifting crew's own order. The user may still lift any order; this change makes the proposal needless, and the briefs say so (`roles.3`: the briefs never said it before).
- The rules' details and `_open.md`, which say this is not built: the design agent's, after the landing (`docs.7`).

## Decisions

### 1. The forecast writes nothing to the plan

`forecasts_due` returns each forecast as `(unit, other, paths, heads)`, with no flag, and `reach` no longer writes `After` for it. The forecast is recorded and delivered as now. `forecast_words` keeps "You merge after it": the words tell the agent to take the other's work, and a settle that does so is what puts the unit after it.

### 2. One decision says which pairs crew orders and which it lifts

A new decision in `plan.py`, a function of plain facts (`code.7`), takes:

- the run record's entries for the team's host, as `reach` reads them (`local_entries`);
- each unmerged unit of the bolt with its `After` names as the plan holds them, and the set of unmerged units;
- `holds(unit, other)`: whether the unit's branch holds the other's work, given to the decision as `amended_afters` and `rebase_leaves_out` are given theirs.

A **pair** is `(unit, other)` for each forecast entry on `unit/<unit>` and `unit/<other>`, both unmerged. For each pair the decision reads, in the record's order:

- **crew's writes for the pair**: a `unit.after` entry with `After: <other>` on `unit/<unit>` (written on a settle, decision 4), or one whose Why is `plan(<bolt>): <unit> after <other>, forecast to conflict` (written at a forecast, before this change);
- **crew's lifts for the pair**: a `unit.after` entry with `Lifted: <other>` on `unit/<unit>`;
- **the unit's settle ends**: `stage.end` entries on `stage/<unit>/settle`, with `Ended` and `Delivered`.

It returns the pairs to **order** and the pairs to **lift**, each with the id of the settle end that decided it:

- **Order** `(unit, other)` when the plan does not put the unit after the other; a settle of the unit ended `delivered` after a forecast for the pair; `holds(unit, other)`; crew has never written the pair's order on a settle; and crew's latest record for the pair is not a write. A latest write that the plan no longer holds was lifted by someone else, so it stays lifted.
- **Lift** `(unit, other)` when the plan puts the unit after the other; crew's latest record for the pair is a write; the unit's latest settle end since that write ended `short`, with no settle of it delivered since the write; and not `holds(unit, other)`.

An order written on a settle is never lifted by this: its settle delivered, and its branch holds the other's work. An order set by hand, or by a proposal, has no write of crew's and is never touched.

### 3. Where it runs

- **At a settle's end.** In `stage_wait`, when the owed stage is a unit's settle and the look ends it `delivered` or `short`, the wait applies the decision for that unit before it prints its answer, and adds one sentence to the answer: `<unit> now comes after <other>, whose work its settle took: it merges after <other>`, or `<unit> no longer comes after <other>: its settle found nothing to change`. The conductor learns the order from the answer it is already reading.
- **At every wait.** `reach` applies the decision for every unmerged unit of the team's bolts before it forecasts, so the forecasts read the plan as the writes left it. This lifts the orders crew wrote before this change once their settle ended short, and writes again what a settle's end could not (a refused push, a host that was down).

When crew cannot read the record, the plan or git for a pair, it orders and lifts nothing for that pair and says what it could not read on standard error, and the wait goes on (`read.1`).

### 4. The writes

Each is one `write` (`state.1`) in the conductor's name, since the wait is the conductor's (`roles.1`), with `w.quiet` holding the team so its conductor is not told a write its own wait makes, as `unmark` does:

- order: subject `plan(<bolt>): <unit> after <other>, its settle took <other>'s work`, act `unit.after` on `unit/<unit>` and `bolt/<bolt>`, fields `After: <other>` and `Settle: <the settle end's id>`;
- lift: subject `plan(<bolt>): <unit> no longer after <other>, its settle found nothing to change`, the same act and objects, fields `Lifted: <other>` and `Settle: <the settle end's id>`.

The change removes only that one `After` name, leaving the unit's others. A write refused (the plan changed, the unit gone) is said on standard error, and the next wait decides again.

### 5. Whether a branch holds the other's work

`holds(unit, other)` is true when `unit/<unit>` holds, by `git merge-base --is-ancestor`, either the other's head as the pair's latest forecast recorded it (`Heads`, `<other>@<sha7>`) or `unit/<other>`'s head now. The forecast's head is what the words told the agent to take; the head now covers an agent that took the other's newer work. Read on the team's host in the kit's main checkout, as `amendments` reads its `holds`.

### 6. The briefs

- `conductor.md`: where it says crew puts the later unit after the earlier on a forecast, it says instead that a forecast orders nothing by itself; when the later unit's settle takes the earlier's work, crew puts it after the earlier in the conductor's name and the wait says so; when the settle found nothing to change, crew lifts an order of its own at the wait; and the conductor never asks the planner or the user to lift an order crew wrote from a forecast.
- `planner.md`: never propose lifting an `After` crew wrote from a forecast; crew lifts its own.
- `t-briefs.sh` checks those phrases (`tests.6`).

### 7. The views

The board and the mod draw a unit's `After` from the plan, which this change writes as before; no object, stage or field they read changes (`code.8`).

## Risks / Trade-offs

- A unit whose stage takes the other's work after a forecast told to it, not in a settle, merges with no order: the merge refusal for a carried change holds it until the other merges, and the conductor runs its merge again then. Before this change the forecast's order did that. Named for the design agent (Non-Goals).
- Legacy orders are recognised by the subject crew wrote them with. That subject is crew's own, fixed in `reach` since the forecast began ordering, and is matched exactly; an entry older than the record's 30 days is not seen, and its order stays until someone lifts it, as today.
- A settle that stops short to ask a question, not to say nothing needs to change, also lifts an order crew wrote at a forecast. When the settle is run again and takes the other's work, decision 2 orders the pair, since crew's latest record for it is then its own lift.

## Task notes

### 1.1

In `forecasts_due`, drop the fifth element of each forecast and the `comes_after` call that made it; update its docstring. In `reach`, remove the write under `if after:` and iterate `for name, other, paths, heads in due`. Existing cases in `tests/py/test_forecast.py` that assert the flag drop it; the case `test_a_unit_already_after_the_other_is_not_put_after_it_again` and `test_one_that_comes_after_at_any_depth_is_not_put_after_it_again` become cases that the forecast is made with its four parts. Add a case that two unmerged units in conflict give the later the forecast and nothing else.

### 1.2

The decision of Decisions 2, with the legacy Why matched by one compiled pattern beside it, named in its docstring as crew's own subject from before this change. Logic cases in `tests/py/test_forecast.py`, one per scenario of the `bolt-teams` delta: a forecast with no settle orders nothing; a delivered settle that holds the other's work orders once, and a second delivered settle does not order again; a settle that delivered without holding the other's work orders nothing; a short settle orders nothing; a legacy order whose latest settle ended short and that does not hold the other's work is lifted; one whose branch holds it is not; one the plan no longer holds (lifted by the user) is neither written nor lifted, and a later delivered settle does not write it back; crew's own lift followed by a delivered settle that holds the other's work orders it; an order set by hand (no write of crew's) is never lifted; a merged other gives no pair.

### 1.3

`holds` as Decisions 5 says, thin around the decision; it reads nothing when the decision has no pair. The writes of Decisions 4. In `reach`, apply both before the forecasts loop over the bolts, then read the plan again only when a write was made.

### 1.4

In `stage_wait`, where `how == "delivered"` calls `unmark`, and where `how == "short"` is about to print, call the same apply for the settle's unit when `o.stage == "settle"` and `o` is a unit's, and append its sentence to `said`.

### 2.1

`t-journey-slots.sh`: the wait that forecasts c against a now prints no `c after a` write, the plan gives c no `After`, and c is still told. Update the test's opening comment and its `ok` line.

### 2.2

`t-journey-merge.sh`, or a new journey beside it if its ground does not fit (then run `tests/moon-tasks` and commit `tests/moon.yml`): two unmerged units forecast against each other, the later verified and waiting to merge, so the forecast starts its settle; (a) the settle merges the earlier unit's branch and commits, and the wait's answer names the order, the plan gives the later unit `After` on the earlier, the entry has `After` and `Settle`, and its merge is refused naming the earlier; (b) with an order standing as `reach` wrote it before this change, the plan's `After` and its `unit.after` entry in the host's run record under the old subject (the test writes both), a settle that stops short through `crew needs` is answered with the lift, and the plan no longer gives the order.

### 3.1

`conductor.md` in its "may" list (where it says crew puts the later after the earlier itself) and in *Forecasts and settling*; `planner.md` beside where it says crew orders merging when it forecasts a conflict. `t-briefs.sh`: replace "crew puts the later after the earlier itself" with the new phrases, and add the planner's.

### 3.2

README: replace "A forecast between two unmerged units puts the later after the earlier." with what Decisions 1 to 3 say, in one or two sentences; in the run record's fields, add `After`, `Lifted` and `Settle` on crew's order writes. `plugin/bin/crew`'s usage for `crew unit wait`: after "telling each later unit once", say it orders a later unit after an earlier one whose work its settle took and lifts an order of crew's whose settle found nothing to change. `plugin/skills/crew/SKILL.md`: one clause where it names the settle stage, that a settle taking the other's work puts the unit after it (`docs.2`).

## After deploy

Nothing. crew has nothing to deploy; the merge gate's suite proves every scenario (`tests.5`, `docs.6`).

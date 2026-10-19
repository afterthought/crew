# Design

## Context

See proposal.md for why. How it works today, from unit-amendments (archived 2026-10-09):

- `op_unit_amend` (`plan.py` 1485) replaces the intent and, for a unit with a worktree, sets `Amended: proposal/<n>` (inside an approval) or `intent` (the user directly). Its `after` step tells the conductor to run construct and to close any card for `review/<unit>` or `verify/<unit>`. If that tell fails, all that is left is a printed line.
- `run_check` (`plan.py` 2618) starts construct on a marked unit only for the user or the team's conductor (`marking = bool(mark) or st in (approved, code, verify)`). It moves the mark to the unit's head when construct starts, adds "This unit's intent was amended; revise the existing change to it." to the prompt, and names a card to close (`ENDS`) only when the stage is `review` or `verify`. On an `amended` unit that leaves `ENDS` empty.
- `plan_approve` runs each op's `after` once the approval's commit has landed. `bolt_give` already runs bash crew on a team's host from Python: `crew.on_machine(fleet, t["machine"], crew.crew_argv(fleet, t["machine"], ...))`, carrying the asker's `CREW_AGENT`, `CREW_LABEL` and `CREW_SESSION` (`code.3`).
- Bash `crew unit run` (`plugin/bin/crew` 647) forwards to the team's host, takes or reuses the unit's slot, calls `plan _run`, and through `run_stage` stops the slot's agent. Without `--force`, `run_stage` refuses to stop an agent that is working, but only after `plan _run` has written the plan. Nothing in it checks whether the team is down. It then starts the stage and, when `ENDS` is set, calls `plan _ended`, which prints the close-card line to the conductor when the conductor ran it and tells the conductor otherwise (`stage_ended_row`).
- `greet_conductor` runs `py greet "$TEAM"` on `up`, `rebuild`, `restart` (unless `--no-greet`) and `revive`. `resume` greets nobody. `crew.py` cannot import `plan.py`, because `plan.py` imports it.

Rules this rests on: `plan.15` (the rule this change builds), `plan.6` (the amended mark and the stages it gives), `plan.1` and `state.1` (the mark's move is a plan write like any other), `roles.1` and `roles.2` (only the user approves; the construct follows from an approval made on the user's word), `roles.4` (every notice is marked `[crew]`), `code.3` (the run goes to the team's host carrying the asker), `read.1` (a greeting that cannot read the plan says so), `teams.7` (one greeting per start), `teams.11` (a tell reaches its agent or fails), `briefs.11` (the cards are the conductor's), and `docs.2`. Area pages touched: `plan.md`, `teams.md`, `briefs.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- Once an amendment is approved, the only thing that can keep its construct from running is something crew names out loud: the host stopped answering, the team is down, or the slot's agent is busy. An amendment whose unit's stage crew cannot read is refused rather than approved blind.
- Every way a conductor comes back up shows it the amended units waiting on it, worked out by crew from the kit and the plan, not from what the conductor remembers.

**Non-Goals:**
- Ending a slot agent that is working in order to start the amended construct. The approval never passes `--force`. A busy agent means the run waits for the conductor, and the conductor is told so.
- The batch review's notes (`concurrent-units`). Those go through the conductor's own `crew unit run <unit> construct "<notes>"`, which this change leaves alone.
- Changing who may run `crew plan approve` or `crew unit amend`.

## Decisions

### 1. The amendment's `after` runs construct on the team's host

When the unit was marked and its bolt is held by a team, `op_unit_amend`'s `after` runs `crew unit run <unit> construct` on the team's host through `crew.on_machine(..., crew.crew_argv(...))`, the same way `bolt_give` runs `restart`. It prints whatever that command printed. This covers both a direct `crew unit amend` and an approval, because both run `after` once the write has landed. The run is recorded as the approver's `stage.start` with `Amended: yes`, through bash crew's existing path.

When the construct cannot start, nothing is written before crew knows it can, so the unit keeps its `proposal/<n>` or `intent` mark and reads `amended`:
- **The slot's agent is working.** Bash `crew unit run` refuses a construct whose slot's agent is working, without `--force`, once it has the slot and before `plan _run` writes the plan. Left to `run_stage`, the refusal would come after `plan _run` had moved the mark to the head, and the unit would read `construct` with no agent running it.
- **The team is down.** Bash `crew unit run` refuses any stage while the team's state reads down, before `reap` or `plan _run` touch anything, and says `crew up <team>` brings it back. This holds for code, verify and merge as much as for construct: a team taken down runs nothing until it is brought up, and the bolt-teams delta states it as its own requirement so it outlives this change.
- **The host stops answering** between the stage read and the run. The run's failure is named by `crew.unanswered`, as a host that did not answer.

In each, the refusal is recorded as a refused `stage.start`, and the amendment stands.

**The host does not answer from the start.** Then `op_unit_amend`'s checks cannot read the unit's stage, so crew cannot tell whether the unit has merged or which card the amendment would end. The amendment, or the approval holding it, is refused naming the host, and nothing is written (`read.1`: a stage crew cannot tell is `unknown`, never a guess). The user approves again once the host answers.

*Alternatives:* a pending-run file that the conductor's wait picks up. That is a status file, which `state.2` rules out, and it still depends on the conductor. A daemon. That breaks `state.4`.

### 2. Anyone may start construct on an amended unit

In `run_check`, the role check applies only when this construct is what marks the unit: `amended(mark)` is false, and either the stage is approved, code or verify, or a sha mark is being moved. On a unit marked `proposal/<n>` or `intent`, anyone may start construct. The user approved the amendment, and construct is the only thing the unit may do next, so starting it decides nothing. The mark then moves from `proposal/<n>` or `intent` to the head in a write made under the approver's name. That write is part of the approval's act, as `bolt give`'s restart is part of the give. README's role table says the mark's move is made by whoever starts that construct.

### 3. The prompt carries the amendment's words, read from the mark

`run_check` builds the "intent was amended" sentence from the mark, not from the caller. That way a conductor starting it later sends the same prompt as the approval would have:
- `intent`: "This unit's intent was amended by the user; revise the existing change to it."
- `proposal/<n>`: "This unit's intent was amended by proposal <n>; revise the existing change to it. The planner's case, as the user approved it: <Case>". `Case` is read from `proposals.rec` at the tip run_check already holds (`plan.12`: no second fetch).

### 4. The stale card is named through the stage's ended-row path

For an amended unit, `run_check` sets `ENDS` from the stage the unit's place reads without the mark, `place_stage(pl, None)`: `review/<unit>` or `verify/<unit>`, and nothing for any other stage. Bash crew already passes `ENDS` to `plan _ended` once the stage has started. The conductor therefore sees the card in its own output when it ran the construct, and is told otherwise (`stage_ended_row`). This is the same path the `rail-cards` requirement "crew names the card a change ends" already uses for a unit built again.

The amendment's own notice to the conductor covers the rest:
- **Started:** "Unit <unit>'s intent was amended by <proposal n | the user>, and construct runs again on it in <slot>: wait for it (crew unit wait <unit>), then take it through review again."
- **Not started:** "Unit <unit>'s intent was amended by <…>, and construct did not start: <the run's last error line>. Run it once it can (crew unit run <unit> construct); it returns to the user's review." followed by `close_card(row)` for the row the unit held before the amendment, taken from the stage `op_unit_amend`'s checks read.

So the conductor gets two notices when construct starts on a unit that had a card: the card one from `_ended` and the amendment one. Each says one thing. Merging them would mean a flag on `crew unit run` that silences a notice, and that costs more than one extra line.

### 5. The greeting names the amended units

A new internal `plan _amended <team>` prints one line naming each unit of the team's bolt whose stage is `amended`: "Units <a>, <b> were amended and no construct runs on them: run construct on each now (crew unit run <unit> construct)." It prints nothing when there are none. When the plan or the kit cannot be read, it prints "crew could not read whether a unit of your bolt waits amended (<why>): read crew bolts." and exits 0, so the greeting still goes out (`read.1`: it says so rather than guessing).

`greet_conductor` passes that line to `py greet "$TEAM" --first "<line>"`, so it opens the greeting. `crew.greet` already takes `first`, and its command line gains the option. That is still one greeting per start (`teams.7`). `crew resume` sends the line as a `crew tell` notice to each conductor it brought back, and only when the line is not empty.

The conductor's brief gains, in *Changing a unit after it was approved*: crew starts construct itself when an amendment is approved and tells you. Wait for it and take it through review. Any unit of your bolt that `crew bolts` shows as `amended` has no construct running: run construct on it. That replaces "When crew tells you a unit's intent was amended, run construct again on it".

### 6. The proposal page

`amendment()`'s closing line becomes "On approval: construct runs again at once in <team>'s slot, and the unit returns to your review."

## Risks / Trade-offs

- [The approval's run takes as long as starting an agent] → It runs the same way `bolt give`'s restart runs, within the command. The approval's commit has already landed, so a slow or failed run never undoes it.
- [A working agent in the slot keeps the construct from starting] → On purpose: crew never ends work it was not asked to end. The unit reads `amended`, and the conductor is told why and acts once that agent's stage ends.
- [The approver is named on the construct's start and the mark's write, not the conductor] → That is who acted. The run record keeps the approver's session (`code.3`), which is the honest trace.
- [`concurrent-units` modifies two of the same requirements] → Whichever archives second restates the other's wording. Named in the proposal's Impact.

## Migration Plan

Pull on every host and restart conductors for the new brief. A unit that already reads `amended` when this lands is named in its conductor's greeting at the next restart. Nothing in the plan's schema changes. Rollback: revert. Marks already set keep their meaning.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Worked by the partition's main-level ops once the bolt has landed and every host has pulled, with conductors restarted:
- The planner proposes `unit amend` for a unit in review in a held bolt. The conductor agrees, and the user approves on its card. Within the approval, a fresh construct agent starts in the unit's slot, with the new intent and the planner's case in its prompt. The conductor is told to wait for it and to close its review card, and it does. `crew trace unit/<unit>` shows `plan.approve`, `unit.amend` and `stage.start` by the approver.
- With the team's host unreachable, approve an amendment to a unit of its bolt. The approval is refused naming the host, and the plan is unchanged.
- With the team's conductor down, approve an amendment to a unit of its bolt whose slot agent is working. The approval says construct did not start and why. `crew restart <team> conductor` greets the conductor with the unit named, and once the slot is free it starts the construct.

## Task notes

### 1.1

In `op_unit_amend.after`: the team is `fleet["teams"][plan.bolt(bolt).get("Team")]`. Run `crew.on_machine(ctx.fleet, team["machine"], crew.crew_argv(ctx.fleet, team["machine"], "unit", "run", a.unit, "construct"))`, print stripped stdout and stderr, and judge started-or-not by the return code. Compute the row before the change from the stage read in the op's checks (`review` gives `review/<unit>`, `verify` gives `verify/<unit>`, anything else gives none) and keep it in the closure for the not-started notice. Send the notice with `crew.tell` as today. When the tell fails, print "<team>-conductor is not up: …" followed by whether construct is running or waits. A unit with no team (queued, or its bolt not given) is left as today: marked, with nothing to run.

In bash `crew unit run`, refuse while `$STATE/down` exists, before `reap`, and refuse a construct whose slot's agent is `working` (no `--force`) before `plan _run`, dropping a slot it had just taken; record each as a refused `stage.start` (Decision 1). When the run fails, name a host that did not answer with `crew.unanswered`, else take the run's last error line.

In `tests/t-amend-intent.sh`, the direct amendment and the approved proposal scenarios now expect a `swb-1-unit-<n>` agent prompted with `/opsx:propose …`, the conductor's notice saying construct runs again, and `stage.start` by the approver. Add scenarios where construct does not start, and in each the stage reads `amended` and the notice names the reason and the card: a stub slot agent `working`; the host's ssh failing only for the run; the team taken down with its conductor, where crew prints "<team>-conductor is not up". Add one where the host is down from the start: the amendment is refused with "cannot tell unit <unit>'s stage" and the plan's tip does not move.

### 1.2

In `run_check`: `needs_role = not amended(mark) and (bool(mark) or st in ("approved", "code", "verify"))`. Marking itself (writing the head) still happens whenever `bool(mark) or st in (...)` and the head differs. The `again` sentence comes from the mark (Decision 3). The proposal's `Case` is read from `proposals.rec` at the tip `locate` returned, using the reader `at_tip` uses. `ends` for an amended unit is `place_stage(pl, None)`, which needs the place's reading. `Stages.of` keeps it in the survey's kit (`k["places"][unit]`), so expose it on `s` the way `head` is exposed rather than reading again. In `tests/t-amend.sh`, add a planner or ops caller starting construct on a `proposal/<n>`-marked unit, accepted, beside the existing refusal for a caller who would newly mark a unit in code.

### 1.4

The refusal is already built (`plugin/bin/crew`, the `$STATE/down` check in `unit run`); only its proof for the other stages is missing. In `tests/t-amend-intent.sh`, in the team-down scenario, after the existing `expect_fail … crew unit run the-deploy-is-logged construct`, run `crew unit run <a unit of swb-1's bolt> code` and expect it to fail with "swb-1 is down; crew up swb-1 brings it back"; assert the plan's tip has not moved, no slot pane was prompted, and the run record holds a refused `stage.start` on `stage/<unit>/code` saying "swb-1 is down". No code changes.

### 2.1

`plan _amended <team>`: survey the team's bolt once (`plan.12`), list the units whose `Stages.of` stage is `amended`, and print Decision 5's line. Bash: `greet_conductor() { local first; first=$(plan _amended "$TEAM" 2>/dev/null || true); py greet "$TEAM" ${first:+--first "$first"} || true; }`. In `resume`, after the loop, for a conductor that was brought back and a non-empty line, send the line to `$TEAM-conductor` marked `[crew]` (`roles.4`): `crew.tell` with no sender marks it so, while the `py tell` command line passes the asker as sender, so add a crew-notice form to `crew.py`'s command line or reuse one if it exists. In `crew.py`'s command line: `greet <team> [--first <text>]`. In `tests/t-greet.sh`, cover: a restart greeting that names an amended unit; a resume that sends the line once with an amended unit and nothing without one; and a unit whose amended construct is running (sha mark, head unchanged), which is not named.

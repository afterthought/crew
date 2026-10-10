# Design

## Context

See proposal.md for why. The current state, after `plan-proposals`:

- A unit's stage is read from its kit by `Stages.of` in `plan.py`, the first rule that holds: `landed`, `merged`, `verify` (every task ticked), `code` (some ticked), `approved` (planning complete and a `Reviewed-by` commit since the bolt), `review` (planning complete), `construct` (the worktree exists), then `ready`, `waiting` or `queued`.
- `run_check` decides whether a stage may start. Construct is accepted only at `ready`, `construct` or `review`; code at `approved`, `code` or `verify`; verify at `verify`; merge at `verify`.
- `crew unit approve` is accepted only at `review`, and writes an empty `Reviewed-by` commit on `unit/<unit>` in the kit on the team's host. It writes nothing to the plan.
- A unit's intent is set by `crew unit add` and changed only by `crew unit split`, which narrows it before code.
- The plan holds "what is meant to be built and any hold on it, never how far the work has got" (`state-repository`).
- The planner changes the plan only by an approved proposal, and a proposal that touches a bolt a team holds needs that conductor's `crew plan agree` (`plan-proposals`). Each plan command is `checks`, `change`, `after`.
- A unit keeps its slot and its place through all its stages; each stage is a fresh agent.

The difficulty is that everything crew knows about a unit's stage comes from the kit, and a change that is written again looks, from the kit, exactly like the change that was there before: its planning is complete, it was approved once, and its tasks may be ticked. So the fact that it must be reviewed again has to be recorded.

## Goals / Non-Goals

**Goals:**
- A rewritten change is never built before the user has reviewed it again.
- A changed intent reaches the unit's construct agent and comes back through review, with no step left to memory.
- The two cases the user distinguishes stay distinct: how a unit builds what it builds is the conductor's with the user; what it builds is the planner's proposal.

**Non-Goals:**
- Amending a merged or landed unit. That is a fix, or a new unit.
- Deciding for the user whether a change is small enough to amend in place. The conductor asks; `blocking-findings` covers the large case.
- Undoing code already written for the old change. The construct agent revises the change's artifacts; the next code stage works from the tasks as they then stand.

## Decisions

### One mark in the plan: `Amended`

A Unit may carry `Amended`, added to the schema's `%allowed`. Its value says what is waited for:

| Value | Set by | Meaning | Stage |
|---|---|---|---|
| `proposal/<n>` | an approval applying `unit amend` | the intent changed; construct has not been run again | `amended` |
| `intent` | the user's direct `crew unit amend` | the same | `amended` |
| `<sha>` | `crew unit run <unit> construct` on an amended, approved, coding or verifying unit: the head of `unit/<unit>` when the stage starts | construct is running again | `construct` while the unit's head is still that sha, `review` once it has moved |

`Stages.of` checks the mark after `landed` and `merged` and before the task rules, so ticked tasks cannot make an amended unit read `code`. The kit's reading already includes each place's head, so no new call to the host is needed.

`crew unit approve` at `review` on a marked unit writes the `Reviewed-by` commit as today and then removes the mark, a plan write whose subject is `plan(<bolt>): <unit> approved after amendment`. With the mark gone the stage is read from the tasks again: `code` or `verify` where work was already done, `approved` otherwise. If the approval commit lands and the plan write fails, the mark stays and the approve can be run again; it finds the commit and only clears the mark.

*Alternatives:* reading the amendment from the kit alone (an approval is valid only if it is newer than the last commit to the change's planning files) fails because the code stage edits `tasks.md` after every approval. Resetting the tasks or removing the old approval commit rewrites history on the unit's branch. A mark is one field, and the plan already says it may hold "any hold on" the work.

### Construct again, at any stage before merge

`run_check` for construct accepts `ready`, `construct`, `review`, `amended`, `approved`, `code` and `verify`, and refuses `merged` and `landed`. At `approved`, `code`, `verify` or `amended` it sets `Amended: <the unit branch's head>` in the plan before starting the stage, in the conductor's own write (the role table of `plan-proposals` gains this one write for a conductor on a unit of its own bolt; it is made by `crew unit run`, not by a command the conductor types). At `ready`, `construct` and `review` nothing is marked: the unit has no approval to protect.

The prompt is today's, `/opsx:propose <unit> <intent> Sources: … <words>`. When the mark was `proposal/<n>` or `intent`, crew adds one sentence before the words: "This unit's intent was amended; revise the existing change to it." `construct.md` gains a paragraph for both cases: revise the change that is there, keep what still holds, and leave ticked tasks ticked only where the work they describe is still what the change asks for.

Code, verify and merge are refused while the mark is set, with "unit <unit> was amended and waits for the user's review (crew unit approve <unit>)", or at `amended`, "… and construct has not been run again".

### `crew unit amend`

A plan command in three parts, like the others:

- `checks`: the unit exists; its stage is not `merged` or `landed` (and is known);
- `change`: `Intent` replaced; when the unit has a worktree, `Amended` set to `proposal/<n>` inside an approval and `intent` when the user runs it directly;
- `after`: when the unit was marked, tell its bolt's conductor: "Unit <unit>'s intent was amended by proposal <n>. Run construct again (crew unit run <unit> construct); it returns to the user's review."

It touches the unit's bolt, so a proposal holding it needs the conductor's agreement when a team holds the bolt. It is added to the commands a proposal may hold and to the role table as the planner's by proposal only. Its entry is `unit.amend`, `On: unit/<unit>`, `From: proposal/<n>`.

`crew plan proposed <n>` prints it as:

```
4. **Amend unit `cfn-lint-treefmt`** in bolt `smoke-2` (swb-2), now in code
   Intent, as it stands: Verify cfn-lint is configured in treefmt, and configure it if not
   Intent, as proposed:  <the new intent>
   On approval: swb-2's conductor runs construct again, and the unit returns to your review.
```

### The conductor's brief

Two additions. When the user wants a unit changed after it was approved, run construct again with the user's words, at any stage before merge, and take the unit through review again; say plainly that code waits for the approval. When crew says a unit's intent was amended, run construct again and do the same. The existing sentence about a unit in review is unchanged.

### Entries and what must not break

`stage.start` for a construct that set the mark carries `Amended: yes`. `unit.approve` on a marked unit names the plan commit as well as the kit's. `crew bolts` shows the new stage word `amended`; a consumer of `--json` sees one more value of `stage`.

A unit that was never amended behaves exactly as before: the mark is absent and every rule falls through to today's.

## Risks / Trade-offs

- [The construct agent rewrites tasks that were already done] → the brief tells it to keep what still holds; the user sees the result at review, and the code stage works from the tasks as they stand.
- [A unit sits at `amended` because its conductor is down] → `crew bolts` shows the stage; the dispatcher's brief already has it keep teams with a bolt up.
- [The mark and the kit disagree after a branch is rebuilt by hand] → the stage reads `construct` while the head equals the marked sha and `review` once it differs, so a moved head errs toward review, never toward building unreviewed work.
- [A new stage word in `crew bolts --json`] → noted in the README; the only reader today is crew.

## Migration Plan

Pull on every host; restart conductors and planners for the new briefs. The schema gains an allowed field, which older plan files satisfy. A crew from before this change would refuse a plan that holds `Amended` (the field is not in its schema), so every host pulls before the first amendment. Rollback: revert, after clearing any `Amended` marks by approving or by hand at a shell.

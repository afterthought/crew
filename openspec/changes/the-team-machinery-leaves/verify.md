# Verify: the-team-machinery-leaves

Read 2026-11-01 on deneb, at `d2940c23` on `change/the-team-machinery-leaves`, cut from `bolt/crew-runs-its-work-through-flume` at `9913f249`.

**Outcome: not archived.** Every task is ticked and every check the tasks name passes. But the code fails two of the change's own ADDED requirements (findings 1 and 2), and seven requirements or scenarios of the deltas say what the code does not do (findings 3 to 9). Findings 1 to 9 are each to be fixed before archiving, in the code or in the delta, whichever the design has right (`docs.3`). Findings 10 to 13 are lesser, best fixed alongside. The change goes back to its code stage.

## Findings

### 1. A team's agent from before gets its name and identity back when herdr resumes it (fix)

main-level, "A main-level agent resumed off its host is given no identity, and nothing else of crew's is", scenario *A team's agent from before* (`specs/main-level/spec.md` 112–114): a resumed session whose record names `crw-5-conductor` or `swancloud-dispatch-deneb` "is given no name, identity or brief, crew modelling no such agent".

`plugin/hooks/session-start` `main()` (105–123) withholds identity only when `crew.main_named` (`plugin/lib/crew.py` 1519) names a main-level role. For a team's agent `main_named` returns None, so the hook goes on as for any crew agent:

- it rewrites the session record;
- it writes `export CREW_AGENT=crw-5-conductor CREW_LABEL=… SLUICE_AGENT=crw-5-conductor` through `CLAUDE_ENV_FILE`;
- it renames the herdr pane `crw-5-conductor`.

Only the brief is withheld, and only at a compaction, because `brief_role` raises and the hook's outer handler swallows the error. `tests/t-session-hook.sh` 67–72 covers that compaction case alone, so no check covers a resume or a start.

The fix: return early for any recorded agent crew does not model, before the record, the env file and the rename. Add a case for a resumed `swb-1-conductor` that checks for no env lines and no rename.

### 2. `crew bolt submit`'s refusals tell ops to tell a conductor (fix)

Design Decision 6 says a landing's conflict with main, met at the submission, launches the take-main fix on the bolt, and "No conductor is told". main-ops's brief says the same: the take-main fix is crew's ("start nothing yourself"), and a failed check is ops's own `crew fix <bolt> …`. The proposal's goal is no conductor "in code, briefs, usage, docs or tests". The command's words still say otherwise:

- `plugin/lib/plan.py` 4055–4056, a landing that is the bolt's: "Tell the bolt's conductor why: a conflict is the bolt's, and the team takes main into it by a submission to the bolt, then you submit again." Its docstring at 3988 says the same. Pinned by `tests/py/test_landing.py` 181, 203, 409, 516 and 798.
- `plan.py` 7761, a bolt whose two copies have diverged: "the way on is its team's: its conductor starts a fix (crew fix), …". The `crew fix` form it names no longer exists. Pinned by `test_landing.py` 1148 and 1722.
- `plan.py` 3590: "… was not printed whole on the team's host".

Main-level ops reads these words after every refused landing. Followed as written, they send it after an agent that no longer exists, and against its brief.

The fix: say what crew did instead: the take-main fix it launched for a conflict, a fix on the bolt for a failed check, and the bolt held on its row. Name no team or conductor, and repin the cases.

### 3. A requeue of a started bolt is not refused (delta or code)

bolt-plan, "A bolt is created, dropped and landed through crew" (`specs/bolt-plan/spec.md` 11), says `crew bolt drop` refuses "`--requeue` while a unit has a place". Scenario *Requeuing a unit that has a place* (37–39) says it is refused, naming the unit and its place, and the plan is unchanged.

`op_bolt_drop` (`plan.py` ~5332) never refuses. It requeues the units and drops each launched place, and `tests/py/test_cross.py` 189–192 asserts that: the requeue appends a drop of request 1. Decision 14 ("a drop drops the place") reads with the code, so the delta looks to be the one to change.

### 4. An amended unit of a started bolt is not marked amended (delta or code)

bolt-plan, "A unit's intent is amended through crew, its construct run again", scenario *A unit in code* (52–54): "the unit is marked amended".

`op_unit_amend` (`plan.py` 5451) marks only when `s["worktree"]` is set. A started bolt's stages come from the runner and never set `worktree`, so no `Amended` mark is written. `tests/py/test_amend.py` 115 asserts `Amended` is None. The retry of construct is made and proved, so only the mark is wrong.

### 5. The chores delta contradicts bolt-teams on `After` (delta)

These two requirements, both in this change, disagree:

- chores, "After means for a chore what it means for a unit" (`specs/chores/spec.md` 17–25), says a dependent is `ready` once the chore's code has committed, "never waiting on a merge".
- bolt-teams, "A dependent launches once its After work has landed" (`specs/bolt-teams/spec.md` 355–359), holds the dependent's launch until its After work has landed on the bolt.

The code follows bolt-teams, so the chores requirement fails as written.

### 6. Nothing holds a bolt's work while its landing is queued (delta or code)

bolt-teams, "A landing's waiter waits from the background a call at a time" (305–315), says "no unit or chore stage starts on the bolt" while the waiter waits. Scenario *Nothing starts on the bolt while the waiter waits* says crew refuses the start, saying the landing is in flight.

crew starts no stage now. The stage-start refusal that held this (`landing_refusal`) left with the stage driving, and nothing replaces it: no hold or refusal on adding work or on the runner's launches while a landing is queued. Either the requirement is rewritten for a started bolt, saying what crew holds and how, or the code holds it.

### 7. The queued-landing line is specified for ops's band but drawn in the planner's (delta or code)

crew-board, "Construction shows each bolt in flight as a ledger…", scenario *A landing recorded queued that sluice no longer has standing* (`specs/crew-board/spec.md` 42–44), names "the lane and … main-level ops's band". Before this change the scenario named the conductor's band.

`board.py` `ops_view` (~846–868) does not draw that line. Its landings rows use `landing_said`, which speaks only while sluice shows the landing standing, and it calls `bolt_row` only for a refused close. The planner's band does draw it, and `tests/py/test_board.py` 1440 checks the lane and the planner's band. By Decision 11 the planner inherits the conductor's ledger, so the delta probably meant the planner.

### 8. The stage ladder in bolt-plan is no longer what crew reads (delta)

bolt-plan, "A unit's stage is read from the kits" (156–212), still lists the ladder read from a place in the kit: `amended`, `construct`, `planned`, `code`, `verify` and the rest. `Stages.of` no longer computes it for any bolt. A started bolt's stages come from the runner; a bolt not started reads only `ready`, `waiting` or `unknown`.

`place_stage` (`plan.py` 1260) is called only by `tests/py/test_stages.py`. That is the old path's code kept by its own test, which Task notes' "Reachability decides" removes. The requirement also conflicts with bolt-plan 241–242, "never from a place in the kit".

### 9. A plan-proposals scenario describes a rebase crew no longer makes (delta)

plan-proposals, "Approval applies a proposal exactly as it was read", scenario *A unit with a worktree is moved* (`specs/plan-proposals/spec.md` 73–75), says the rebase is undone and the approval refused. `op_unit_move` (`plan.py` ~5533–5570) makes no rebase. Moving launched work is refused by `runner.launched_refusal`, naming drop and add. The outcome holds, refused with nothing changed, but the scenario's words are of the removed path.

### 10. Lesser: what the runner's work reads (by reading; not reproduced)

- bolt-teams, "A submission's number is on its bolt's row from the submit" (284–296): `submission_rows` (`plan.py` ~9091) maps lines by `unit/<u>`, `chore/<c>` and `fix/…` branches. A Flume place submits from `change/<u>` (the `flume-0.3.6` fixtures), so a started bolt's lines may never show sluice's number.
- run-record, "A bolt's landing entry records its time by holder": `bolt_facts` (`plan.py` ~9300–9360) counts `stage.start`, `fix.start` and `fix.merge` entries and `unit/<u>` submissions. Flume's stage time goes to `nobody`. A `crew fix` launch's `fix.start`, with no end ever written, counts as `team` until the bolt ends.
- bolt-plan, scenario *The drop's host does not answer* (33–35): `op_bolt_drop`'s `after` sweeps only when `known_at` finds where the work runs. A bolt whose work no runner has taken asks sluice for no delete and says nothing.

### 11. Lesser: spec words left naming the old path

- card-sessions delta: "a conductor on the box runs `crew card session batch/3`" (`specs/card-sessions/spec.md` 11), and the scenario title "A landing's try off its team's host" (87).
- plan-proposals, "A proposal is read as the user would read it, waiting on the user alone": `crew plan proposed <n> --json` (`plan.py` 6792, `describe`) carries no `waits`, though the list's JSON (6794) and the page say "the user".

### 12. Lesser: docs and briefs left naming the old path

- `README.md` 208: batches "that span its teams". The review-batches delta has a batch span the partition's bolts.
- `CLAUDE.md` 35: "A landing that conflicts with main lands nothing: the team takes main into the bolt by a fix it submits to the bolt".
- `plugin/roles/operator.md` 66–68 (*Showing what is running*) promises each unit's dev-server URL from `crew sites`. `sites.py` now shows none for a started bolt, and every bolt in flight is a started one.
- `plan.py`'s module docstring (lines ~24–83) is printed by no command. It still says:
  - a drop is refused while a unit has a worktree;
  - an amendment's construct "runs again at once on its team's host, its conductor told";
  - a card session runs "on that unit's team's host";
  - a chore is built by code, verify and merge.
- `HEADER`'s Unit `%doc` (`plan.py` ~158), written into every new state branch, says "built on unit/<Unit> at <Repo>/places/<Unit>".

### 13. Lesser: other leftovers

- `tests/t-sites-live.sh` 30–37 still expects a started bolt's unit listed with its devurl address and place. It runs only under `CREW_TEST_LIVE=1`, outside the suite, and would fail.
- `plugin/lib/crew.py` 439: the board word's `KINDS` still takes `team`, routed to the operator, though no team has a dock.
- `plugin/lib/page.html` 478: `BUILDING` is `construct`, `code`, `verify` and `settle` only. A started bolt's units at `submitted`, `needs`, `waits`, `stalled` or `launching` draw as queued, against board-page's "merged, building or queued", where the text board (`board.pip`) shows them in flight.
- Suspected, no case: the fleet page's subscription list (`page.py` `agents_in`, 253) leaves out the reviewer, while the partition page's subscription dock lists it. A reviewer given a session of its own would show as "runs no crew agent" on the fleet page.

## Checks

| Check | Result |
|---|---|
| `tests/suite --affected` (task 9.2) | 26 passed (26 replayed), 0 failed: every task of the suite, the command core having changed; each replayed from a run that passed on this host with identical inputs |
| `tests/suite --force logic contract mod` | 3 passed (0 replayed), 0 failed |
| `tests/moon-tasks --check` (task 9.1) | in step; `tests/moon.yml` holds 26 `check-full` tasks |
| `openspec validate the-team-machinery-leaves` (tasks 1.2, 1.6) | valid, with 14 warnings of requirement text over 500 characters |
| `openspec validate the-team-machinery-leaves --strict` | not valid: the same 14 warnings, which strict mode counts |

The passing suite does not cover findings 1 to 9. Findings 2, 3 and 4 are pinned the wrong way by the cases named there, and findings 1 and 6 to 9 have no case.

## Tasks

All 34 tasks, 1.1 to 9.2, are ticked, and the check each names passes.

- Task 4.2's checks (`t-hold`, `t-session-hook`) do not reach finding 1.
- Task 8.2's words for main-level ops ("no conductor told") hold in the brief but not in `crew bolt submit`'s output (finding 2).
- Task 1.3's `_open.md` line is in, as the task asks, on the user's ruling of 2026-10-31.

## Requirements and scenarios

Read against the code and its cases. These hold:

- **The teams file and the commands that leave.**
  - `teams.json` version 5, partitions only.
  - Versions 2, 3 and 4, and a `teams` list, are refused naming `lib/crew-teams.nix`.
  - `roles.dispatcher` is refused.
  - Every removed command is gone, falling to argparse or the usage: `bolt give`, `plan agree`, `unit` and `chore run|wait|free`, `needs`, `list`, the team forms of `status|up|rebuild|close|restart|resume|clear|down`, `crew-role`'s team and slot forms, `fix --merge|--wait|--bolt`, and `main fix --team`.
- **The briefs.**
  - `conductor.md`, `ops.md`, `dispatcher.md`, `construct.md`, `coder.md` and `verify.md` are gone, and nothing in `plugin/`, `tests/` or README refers to them but the checks that they are gone.
  - The five staying briefs name none of the words task 8.2 rules out.
  - `cards_how` names the planner, main-level ops and the design agent.
- **The plan.**
  - `crew bolt start` starts a bolt's work whole, with no team, and only the user runs it outside a proposal.
  - A new branch's descriptor allows no `Team` or `Agreed`, and an old one still passes `recfix --check`.
  - A proposal waits on the user alone.
  - No write tells a conductor.
  - The planner, the design agent, main-level ops's `bolt land` and the user are the plan's writers.
- **The runner's work.**
  - A kit's launches, retries, drops and priorities name no host or stream.
  - Stages and where a bolt's work runs are read from the runner that took it.
  - Fix places on a bolt, `crew main fix` by kit, and the take-main fix are launched in the kit's repository.
  - Dependents launch after their After work lands.
  - Plan writes reach launched places.
  - What comes before a runner takes a kit's work is done in the main-level host's checkout.
  - A partition's kits come from its plan and landings (`tests/py/test_kits.py`).
- **The views and cards.**
  - `board.agent_views` gives the planner, design, ops and the operator their views and no other.
  - `crew board --json` carries no `teams`.
  - The cards, the page, the fleet page and the rail name no team, slot, conductor or dispatcher and no "a yes frees" line.
  - A started bolt's ledger and its `crew sites` entry show no dev server.
  - The landings card records a forecast conflict once and tells no one.
  - A send still standing lands only the ticked bolts not yet landed or gone.
  - `status.js` and its cases draw the planner's and ops's bands.
- **Holds, sends and batches.**
  - `crew hold`, `go` and `update` reach the main-level roles alone.
  - The branch hint is gone.
  - `crew send` takes a partition's label alone.
  - A batch spans the partition's bolts, reckoned on the main-level host, each unit named with its bolt.
  - Old acts on the branch still print as written in `crew trace`.

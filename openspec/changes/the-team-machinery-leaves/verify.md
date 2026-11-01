# Verify: the-team-machinery-leaves

Read 2026-11-01 on deneb, at `a09bfa5c` on `change/the-team-machinery-leaves`, cut from `bolt/crew-runs-its-work-through-flume` at `9913f249`. This is the second verify. The first, at `d2940c23` (commit `b6a4c929`), left the change unfinished with thirteen findings; the code stage answered them as tasks 10.1 to 10.13.

**Outcome: archived.** All 48 tasks are ticked, and every check they name passes. Each of the first verify's nine blocking findings is fixed, in the code or in the delta as the design has it, with a case that pins it. What still stands is lesser and listed below. None of it fails a requirement or scenario of the deltas.

## The first verify's findings, as they stand

| # | Finding | Task | Now |
|---|---|---|---|
| 1 | A team's agent from before got its name and identity back on resume | 10.1 | Fixed. `session-start` returns before the record, the env file and the rename for any agent `crew.main_named` does not model. `t-session-hook` checks resume, startup and compact of `swb-1-conductor`: no output, no env lines, no rename, record unchanged. |
| 2 | `crew bolt submit`'s refusals told ops to tell a conductor | 10.2 | Fixed. `plan.held_way` says what comes next: crew's take-main fix for a conflict with main, a queued submission waited out, ops's `crew fix <bolt>` for a failed check. `landing_head`'s diverged-copies words name ops's `crew fix`. bolt-teams' delta says the same, and `test_landing.py` is repinned. |
| 3 | A requeue of a started bolt was not refused | 10.3 | The delta now has what the code does, as Decision 14 says: `--requeue` drops each launch still standing. README follows, and `test_cross.py` pins the unit queued and its launch dropped. |
| 4 | An amended unit of a started bolt was not marked | 10.4 | Fixed. `op_unit_amend` marks `intent` or `proposal/<n>` when `amend_place` retries a launched place's construct, and leaves a unit unmarked when its held or unanswered launch is made anew. `test_amend.py` pins both. |
| 5 | The chores delta contradicted bolt-teams on `After` | 10.5 | The chores and bolt-plan deltas now hold a dependent `waiting` until its After work has landed on the bolt, as bolt-teams and the runner have it. |
| 6 | Nothing held a bolt's work while its landing was queued | 10.13 | Fixed, on the user's ruling (Decision 16; see below). |
| 7 | The queued-landing line was specified for ops's band and drawn in the planner's | 10.6 | The crew-board delta now names the planner's band, as `test_board.py` checks. |
| 8 | bolt-plan's stage ladder was no longer what crew reads | 10.7 | `place_stage` is gone with its cases. bolt-plan's "A unit's stage is read from the kits" is replaced by "A unit's stage is read from the runner, or from the plan before its bolt starts", and the design names the `plan.6` and `plan.13` clauses it retires. |
| 9 | A plan-proposals scenario described a rebase crew no longer makes | 10.8 | The scenario now says the approval is refused naming the launched place, with drop then add as the way on, and nothing rebased. |
| 10 | What the runner's work reads | 10.9 | Lines and gate time read sluice's submissions from Flume's branches, `change/<u>`, `chore/<c>` and `fix/<bolt>--<f>`, through `line_branches`. A drop of a started bolt no runner has taken asks sluice's delete in the main-level host's checkout (`drop_at`), or says why it cannot. The bolt-time holders stand: see lesser item 1. |
| 11 | Spec words naming the old path | 10.10 | card-sessions names no conductor or team's host. `crew plan proposed <n> --json` gives `waits: ["the user"]` for an open proposal. |
| 12 | Docs and briefs naming the old path | 10.11 | README's batches span the bolts, and CLAUDE.md's landing has crew's take-main fix and ops's fix. The operator's brief promises no dev server. `plan.py`'s usage and the Unit `%doc` name no worktree, team's host or conductor. |
| 13 | Other leftovers | 10.12 | Fixed: `tests/t-sites-live.sh` is deleted; the board word takes no `team` kind; `page.html` draws `needs`, `submitted`, `waits` and `stalled` as building, as `board.pip` does; the fleet page lists the reviewer. |

### Finding 6: a landing queued holds its bolt's work

The user ruled that `plan.8` stands, and that sluice's rejection and the state after it are kept apart from a queued landing. Decision 16 and the new bolt-teams requirement "A landing queued holds its bolt's work" give it four states. Read against the code:

- **The states.** `plan.landing_phase` reads queued, rejected, landing again or none from the run record, as a decision of facts alone (`code.7`).
  - A wait that sluice itself failed on leaves the landing queued.
  - crew's own refusal before anything was submitted names no head, so it leaves a rejection standing.
  - A landed or stopped landing holds no state.
  - `test_landing_state.py` covers each.
- **The hold.** `plan.landing_hold` refuses work while the landing is queued or landing again, naming the landing and its number.
  - It covers `crew unit add` and `crew chore add` into the bolt (`op_unit_add`), `crew unit move` and `crew chore move` into it (`op_unit_move`), and `crew fix <bolt> <name>` (`fix_flume`).
  - Each reads the run record at the tip its write is applied to (`Write.entries`), so a replay checks it again (`plan.1`).
  - A proposal is refused at its check (`Proposed`) and at its approval. A card is drawn with nothing read for it (`Drawn.landing`).
  - `crew fix --drop` and the take-main fix are not held.
  - Cases: `test_cross.py` `TestALandingQueuedHoldsTheBoltsWork`, `test_fix.py`, and `t-journey-land`, which refuses a `crew unit add` while the landing is queued.
- **What the views say.** `plan.phase_said` gives each state its own words:
  - in `crew bolts`, text and JSON (`landing_record`), and a run record that can't be read is named;
  - on the board's head line (`board.landing_of`, `head_said`);
  - on the rail's land line, which leaves a bolt queued or landing again out of those that can land (`test_rail.py`);
  - on the landings card's row for a rejected landing, which says the bolt is open for work (`landing_rows`, `landings_step`).

## Checks

| Check | Result |
|---|---|
| `tests/suite --affected` (task 9.2) | 26 passed (26 replayed), 0 failed. That is every task of the suite, since the command core changed. Each was replayed from a run that passed on this host with identical inputs, and covers every end-to-end test tasks 1.1 to 10.13 name. |
| `tests/suite --force logic contract mod` | 3 passed (0 replayed), 0 failed |
| `tests/moon-tasks --check` (task 9.1) | in step |
| `openspec validate the-team-machinery-leaves` (tasks 1.2, 1.6, 10.5, 10.7, 10.10) | valid, with 18 warnings of requirement text over 500 characters |
| `openspec validate the-team-machinery-leaves --strict` | not valid: strict mode counts the same 18 warnings. No task names strict. |

## Tasks

All 48 tasks, 1.1 to 10.13, are ticked, and the check each names passes:

- `tests/py/test_landing_state.py` exists, as 10.13 asks.
- `tests/py/test_kits.py` and `tests/py/test_runner.py` exist, as 5.1, 5.2, 5.5 and 5.6 ask.

## Lesser, still standing

None of these fails a requirement or scenario of the deltas. Each is worth a chore.

1. **A bolt's time still has a `team` holder.**
   - `plan.HOLDERS` is `team`, `kit`, `team_or_kit`, `user`, `hold` and `nobody`, and the bolt's time line and its landing entry's `Split` say `team` and `team or kit`.
   - `bolt_facts` counts `stage.start`, `fix.start` and `fix.merge` entries to the next `stage.end`. A `crew fix` launch records `fix.start` and nothing ever writes its end, so its minutes go to `team` until the bolt ends. A Flume place's stage time goes to `nobody`.
   - The design's Risk "Specs this change leaves to the crossed path" leaves the bolt-time requirements of crew-board, `plan.20`'s holders, as they stand. So this is accepted, not a failure, but the views still say "team" there.
2. **The rail can drop a rejection that `crew bolts` still shows.**
   - `plan.refusals` reads each bolt's last `bolt.submit` alone. Suppose sluice rejected the bolt at head H, and crew then refused a later submit before anything was submitted (no `Head`).
   - Then `held_at` finds no head, and the rail's land line and the landings card treat the bolt as not held.
   - `landing_phase`, as Decision 16 says, keeps it rejected for `crew bolts` and the board.
   - No scenario covers this case. Reading the rejection for the rail through `landing_phase` would make the views agree.
3. **Stale words and dead plumbing in `plan.py`.**
   - `Op`'s docstring (5176) and `apply_all`'s (6357) say they return "the bolts whose conductors hear the write". The `told` list they thread is collected by `write` as `touched` and used for nothing.
   - `take_main_launch` (4612) still says "nothing for a bolt given on today's path, whose conductor takes main in".
   - `after_met`'s docstring says "never waiting on a merge (plan.13)". Its `CONSTRUCTED` and `CODED` ladders now serve only a bolt not started, where every After work reads `ready` or `waiting`, so a dependent reads `waiting`, which the deltas want.
4. **One word in CLAUDE.md.** Line 24 has "whichever worktree or team runs it" of the host's test slots.

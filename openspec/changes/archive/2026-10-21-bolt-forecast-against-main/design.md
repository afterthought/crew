# Design

## Context

On each conductor's wait, `reach` forecasts every unmerged unit against the bolt and the units ahead of it with `git merge-tree` and tells the later unit once (`teams.12`). The bolt itself is forecast against nothing: `plan.8` has it meet main only at its landing, and since record 0032 no worktree holds the bolt's branch. sluice's forecast of a branch no worktree holds, `sluice submit main --check --head bolt/<bolt> --json`, forms the bolt on main and everything queued there in sluice's own order and writes nothing (sluice ADR 0039). It exits 0 with no conflict and 2 with one, printing `{"conflict": null | {"paths", "with"}, "head", "onto", "ahead"}`; a sluice without it refuses `--head` with exit 64.

Pages this change touches: `teams.md`, `plan.md`, `briefs.md` (`conductor.md`), `record.md` (the descriptor's comment), `tests.md`.

## Decisions

**The forecast is sluice's, run on the wait.** `reach` runs on the team's host at each conductor's wait, where `teams.12`'s forecasts already run; one more sluice command there costs one merge behind main's formed combinations, and a fetch of the bolt where it is on GitHub. crew dry-running the bolt against main itself would miss main's queue, which three of the box's twelve conflicts were with.

**A pure decision between two thin reads (`code.7`).** `sluice_check` runs the command and returns its exit, output and standard error; `bolt_forecast_read` reads that answer, checking every field it uses (`read.2`); `bolt_forecast` decides what the conductor is told, from the document and the Heads already recorded; `unread_said` decides when a forecast sluice can't give is named. `reach` says the words on the wait's standard error, as its other forecasts' notes, and records them.

**Once, by Heads.** A forecast's Heads are `bolt/<bolt>@<sha7> main@<sha7>` and `#<id>` for each submission queued on main it meets, so the same forecast is said once and a moved bolt, main or queue says it again. A forecast sluice can't give is keyed on `bolt/<bolt>@<sha7>` alone, from the kit's read of the bolt's head, so a host whose sluice has no `--head` names the gap once per bolt head rather than on every wait, which the brief would turn into a word to ops each time (`read.1` still holds: it is named).

**Landed or queued.** sluice names no submission when the head conflicts with main as it stands, and names the queued submissions it conflicts with otherwise. A conflict with what main has landed is taken in now by the take-main fix the brief already describes for a landing that conflicts (`plan.8`), the wait giving the command with a name from main's short sha so two such fixes on one bolt never share one; a conflict with a queued submission is waited out, since it may fail and leave the queue, as all three such submissions on the box did.

**Departures.** `plan.8` said a bolt meets main only at its landing; it is amended to meet it earlier on such a forecast (record 0036).

## Risks

- A take-main fix may now come while units are still in flight; it merges into the bolt like any fix, and units rebase onto the bolt as after any merge.
- Hosts without a sluice that has `--head` forecast nothing, saying so once per bolt head.

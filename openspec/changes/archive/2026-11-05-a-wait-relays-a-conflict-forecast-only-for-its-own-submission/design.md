# Design: a wait relays a conflict forecast only for its own submission

## Context

The proposal gives the box's timeline. Rules this change relies on: `teams.21`, which has the wait say each bolt's forecast against main once for the same bolt head; `read.1`, which says that what crew can't read is said and never guessed; `code.7`, which makes a decision a function of facts; `code.9`, which gives a wait a timeout of its own; and `plan.18` and `plan.19`, which have a decision of the moment read a bolt where it lives after a fetch. The change touches the areas of `plan.md` (`plugin/lib/plan.py`) and `briefs.md` (`plugin/roles/conductor.md`). It departs from no rule.

What crew reads of sluice was checked against sluice's statement and against crew's readers:

- **sluice's forecast.** Clause 64 forms, for a head not yet submitted, the candidate that head would form if submitted now, and "says the revision and the document it formed on". Clause 47a gives the conflicts that head would meet after every entry already submitted. `sluice submit main --check --head bolt/<bolt> --json` answers with `head` and `onto`. crew records both in the forecast's `Heads`, but its words named neither the head nor the time the forecast was made.
- **The overview and the waits on a submission.** `overview_look` relays a conflict or a blame only for a submission whose recorded path is the stage's place and only since the stage began. `wait_outcome`, `landing_due`, `answer_record` and `verdict_printed` read only the record whose id is the submission's own. None of them carried #1275's conflict to #1277. They relay by the submission's number, as clause 65's "names … every entry it is contested with" has sluice say it, and this change leaves them as they are.

The fault is in what the wait does with its own forecast. `stage_wait` runs `before_waiting`, and so `reach`, before it waits. `reach` writes each bolt's forecast on standard error at that moment. A conductor reads a wait's output when the wait answers, and that can be minutes later. In wldn's case it was ten minutes later, and by then the bolt had moved and been submitted again.

## Decisions

### Decision 1: a forecast's words name the bolt's head it is of

`bolt_forecast` puts `at <head7>` after the bolt's name in all three forms of its words: a conflict with what main has landed, one with a submission queued on main, and a bolt the user left. Its `Heads` are unchanged, so nothing is said twice that was said once. `main_told` builds the landings card's tell from the same function, so a tell names the head too. The take-main fix's command already names main's revision, `take-main-<main7>`, and the head was the half a reader lacked.

### Decision 2: the wait's answer judges each forecast it said against where the bolt stands then

`bolt_said` returns the head its forecast is of, or None when it said nothing. `reach` returns those as `[(bolt, head)]`, and `before_waiting` hands them to `stage_wait`. When the wait answers, at any of its ends, `forecasts_after` reads each such bolt's head where it lives, after a fetch (`forecast_heads_now`: `stages_for(..., fetch=True)`, the read a decision of the moment makes, `plan.18`). It then writes on standard error, before the answer's line, what the pure decision `forecasts_moved` gives:

- A bolt at another head: "bolt/<bolt> moved from <old> to <new> while this wait waited, so the forecast against main it said as it began is of <old>, not of the bolt now: take nothing in for it. Your next wait forecasts bolt/<bolt> at <new>."
- A bolt crew can't read, because the plan can't be read, the team no longer holds the bolt, or the kit can't be fetched: crew can't tell whether the bolt still stands at that head, with why, and the advice to read the head before taking anything in.
- A bolt still at the head forecast: nothing. Heads are compared by prefix, since sluice's head and git's are both full but either side may be short.

Nothing is read at the end when the wait said no forecast of a bolt, so a wait with no forecast costs nothing more.

Considered: holding the forecast's words until the answer and saying them only if the bolt has not moved. Rejected, because a wait cut off before it answers would leave a forecast recorded `Reached: wait` that nobody was told, and the next wait would not say it again for the same heads. Also considered: holding the record and the card's change until the answer. Rejected, because that would delay bolt-teams "A wait's forecast conflict with main changes the kit's landings card" by the whole length of the stage. Also considered: forecasting again through sluice at the answer. Rejected, because sluice's check is given up to a minute (`FORECAST_BOUND`) and fetches, which would push a nine-minute wait past an agent's ten-minute call (`code.9`). A fetch and a read of refs answers in seconds.

### Decision 3: what was recorded and the card stand

The forecast entry is a fact about the head it was made of, so it stays. `main_conflict`, which the landings card reads, takes a forecast only at the bolt's present head. The card's raise after a merge into the bolt (`landing_after_merge`) forecasts the bolt again at its new head. So no row is held for a head the bolt has left, and nothing here changes it.

### Decision 4: the conductor takes nothing in for a stale forecast

The conductor's brief says that a forecast is the bolt's at the head it names alone, so when the wait's answer says the bolt moved from that head, the conductor takes nothing in for it, and the next wait forecasts the bolt where it stands. `tests/t-briefs.sh` pins the phrase (`tests.6`).

## Risks

- A fetch at the answer adds a few seconds to a wait that said a forecast. That is rare, since a forecast is said once for the same heads.
- A bolt that moves and moves back within one wait reads as unmoved, and its forecast stands. The forecast is still true of that head, so this is no relay of another head's forecast.

## After deploy

None. Each behaviour is code proven in crew's tiers, and wldn's box gets it when the fleet moves its crew. That is swancloud's deploy and no step of this change.

## Task notes

**1.1** `plan.bolt_forecast`'s three word forms gain `at {doc['head'][:7]}` after `bolt/{bolt}`. Update `tests/py/test_forecast.py` (`TestBoltAgainstMain`, `TestALeftBolt`), `tests/py/test_landings.py` (`test_a_row_newly_taking_main_first_tells_its_conductor_the_fix_once_and_records_it`), `tests/t-journey-main-forecast.sh` and `tests/t-journey-land.sh`'s told words.

**1.2** `plan.forecasts_moved(said, now)`, pure. Cases in `tests/py/test_forecast.py` `TestAForecastIsOfItsHead`: moved, with wldn's heads; not moved, compared by prefix either way; unread, with its why and with no reading at all; only the bolts said are judged. `TestWaitChangesTheCard` adds that `bolt_said` gives the head, or None when it said nothing.

**1.3** `reach` returns `forecast`, `[]` when the plan can't be read. `before_waiting` returns it, `[]` on a refusal. `stage_wait` calls `forecasts_after` before `ended_said` and before the answer's `print`. `forecast_heads_now` reads the plan, the bolts the team holds among those said, and `stages_for(..., fetch=True)`, and gives `(head, None)` or `(None, why)`. `tests/t-journey-main-forecast.sh` gets one case: sluice's forecast names the bolt's parent, and `crew unit wait a --timeout 0` says it moved from that head to the bolt's own and says it once.

**1.4** The conductor's brief's forecast paragraph, README's wait paragraph, the crew skill's wait sentence and `crew unit wait`'s usage header. `tests/t-briefs.sh` pins the brief's phrase.

# Design

## Context

See proposal.md, *Why*. Today `landing_ended` (`plugin/lib/plan.py`) records every landing that did not land at the head submitted as a `bolt.submit` entry whose `Refused` holds crew's or sluice's last words; `refusals` reads those, and `landing_rows`, the rail's land line and `sent_left` treat each as the bolt's refusal at that head, so the row loses its box until the head moves. The words recorded are whatever sluice printed last, which for the two wldn bolts of 2026-10-23 was a notice of sluice's own round, "could not release …, whose worktree no longer exists" (`exec.rs` `tell_abandoned`), not the cause; and `wait_outcome` keeps only sluice's exit, so a failed submission whose checks never ran (exit 1) reads like one a test failed.

sluice 0.36.4's record of a submission says which it was (`crates/sluice-core/src/records.rs`, read 2026-10-24 at agentplot/sluice 4f2b506): `state` is `conflict` with `conflict.paths`, or `failed` with `failed[]`, each a `FailedTask` whose `hash` is empty "for a required check the run left without a result" and whose `not_run` holds why "the check could not run", and `result` is `"timed out"` when the run's time limit ended it. sluice's own words follow the same line (`crates/sluice/src/lib.rs` ~1672–1800): "the host could not run X: once it can, submit again" for checks with no result, "fix it in your worktree and submit again" only for a check that ran. `sluice wait <n> --json` prints that record (`wait_outcome`), and `sluice status main --all --json` lists every record (`submission_of`).

The one case that already holds nothing is a submission sluice answered with nothing crew can wait on (`landing_ended`'s `standing`), recorded with `Why` and `Head` and no `Refused`; this change records a stop the same way.

Rules relied on: `plan.16` as read 2026-10-24 (in `plan.18`'s details, for wldn signal 2026-10-24-wldn-ops-2dd52ecd/01), the rule this builds; record 0031 §1 and its amendments of 2026-10-23 and 2026-10-24 (a refused landing held for the team's fix; a landing's approval stands for the bolt's work); `roles.2` (the landing stays on the user's word, which a stop does not spend); `read.1` and `read.2` (judged from sluice's record by checked facts, an outcome crew can't read holding nothing it can't name); `code.7` (the judgment a function of facts); `state.4` (the row read from the run record, nothing written to make it); `tests.4` (each case in the lowest tier). Pages whose areas this touches: `plan.md` (`plugin/lib/plan.py`), `briefs.md` (`plugin/roles/main-ops.md`), `docs.md` (README, the skill), `tests.md` (`tests/`). `code.8`: the change adds no field the agents' views or the mod read; a row's words change and its box stays, both already drawn.

## Goals / Non-Goals

**Goals:**
- A landing's end is judged the bolt's or not from sluice's record of that submission alone.
- A stop keeps the bolt's row landable on the word it has, says what stopped it, and is submitted again by ops with no new word.

**Non-Goals:**
- crew submitting again by itself. A host or sluice that is down may stay down for hours, and the landing is ops's act (`plan.16`); crew's existing waits again on a submission sluice still has standing (`wait_again`) are unchanged.
- Telling ops when a stop is cleared. Ops reads that as it reads any finding outside a bolt.
- Re-reading entries recorded before this change. An old `Refused` is words only, which crew does not classify (`read.2`); see *Migration Plan*.
- crew's own refusals before anything is submitted (a split legacy bolt, words not the user's). They carry no head and hold no row today, and stay so.

## Decisions

**1. The bolt's is a conflict or a check that ran, read from sluice's record.** `landing_blame(record)` returns the bolt's when the record's `state` is `conflict`, or `failed` with any `failed[]` entry holding a `hash`, or with `result` `"timed out"`; anything else, a `failed` record whose every check has no result, `withdrawn`, a record still standing after crew's waits again, a `landed` record main does not hold, or no record crew can read, is a stop, with words saying what stopped it: the `not_run` reasons as sluice words them ("<task> could not run: <why>"), "every required check was left without a result" when none is given, sluice's last words for exit 3, or crew's existing words for what it can't tell. Alternatives: by exit code alone, which reads the Dagger engine not answering (exit 1, no result) as a failed test; by sluice's words, which are not a contract (`read.2`) and were a notice in the wldn case. A time-limit cut is kept the bolt's because sluice names a test that never ends as the bolt's to fix (`words.rs` `timed_out_way_on`) and only a run decides it; a host that was merely slow is the rarer case, and its team's conductor can see it from sluice's words.

**2. A stop is recorded stopped, not refused.** `landing_ended` records it as `bolt.submit` with `Head`, `Why` (the stop's words) and `Outcome: stopped`, no `Refused`, as the standing case already does; `stops(entries)` beside `refusals` gives `{bolt: (head, words)}` from each bolt's last `bolt.submit` when it is so marked. A later `bolt.submit` of the bolt, landed or refused, supersedes it, and a stop at another head holds nothing, as `held_at` reads a refusal. Alternative: keep `Refused` and add a mark; every reader of `Refused` (`refusals`, `sent_left`, the trace's "refused") would need it, and the run record's `Refused` means crew refused an act (run-record spec), which a sluice failure is not.

**3. The row keeps its box and says the stop.** `landing_rows` takes the stops and gives a boxed row whose facts carry `stopped` (head, words) when it is at that head; `cards.row_paragraph` and `row_counts` add "Its last landing at <head> was stopped, nothing of the bolt's: <words>. <ops> submits it again once that is cleared." The rail's land line says it beside "can land", and the row's tell names the bolt. `landings_step` needs no new act: a ticked bolt that is neither held nor moved is still landing on the send, so an answered card is left as it is and a card that follows does not ask for it again (`rows_unsent`, `sent_left`); its outcome's "Landing as you ticked" names each stopped bolt with its words. `card_read` prints a stopped bolt's words beside it, so ops sees why before it submits again. Alternative: change the answered card in place to show the stop; the spec leaves an answered landings card as it is until every ticked bolt lands or is held, and the user's word needs nothing more.

**4. crew bolt submit tells ops what to do.** For a stop, `landing_said`'s words to ops become: "bolt/<b> did not land, and nothing of the bolt's stopped it: <words>. Its row keeps its box and the user's word stands: report what stopped it, and once it is cleared crew bolt submit <b> submits it again, with no new word." The command still exits non-zero, as for any bolt not on main. The pull request is left a draft as for any landing that does not land (bolt-teams), and the next `crew bolt submit` readies it, which is how sluice tests the same commits again.

**5. Main-ops's brief carries the branch.** Step 2 of *Landing a bolt*: a stop is no conductor's; ops records it as a signal of a finding outside any bolt and tells the planner in one line, as *After landing* already has it, and submits the bolt again with the same command once what stopped it is cleared, on the send or pane words that still stand (`--excerpt` with the same words for a pane word, which crew reads again in ops's transcript), asking the user nothing.

**6. The stub sluice records what the real one does.** The stub's wait record gains `failed[]` (one entry with a `hash` for `sluice-fails`, entries with `not_run` and no hash for a new `sluice-could-not-run` file) and `conflict.paths` for a conflict, so the end-to-end cases judge by the record as crew does. A fixture of the two failed shapes, written to `records.rs`'s `Submission` and `FailedTask` and cited there, pins the logic tier's reading (`read.2`).

## Risks / Trade-offs

- [A cause that is the bolt's reads as a stop, e.g. a check that crashes the runner before it records a result] → ops submits it again, and the same stop says so again with sluice's words; ops reports it, and the planner or the team's conductor sees it. No landing happens without a passing run (`tests.5`), so the cost is a retry, not a bad landing.
- [A slow host's timeout is held for the team's fix] → sluice's own words say "if the host was slow, submit the same head again"; the conductor can answer that the fix is none, and a take-main or empty fix moves the head. Kept the bolt's by Decision 1.
- [Ops submits again before the cause is cleared] → it stops again, recorded again, nothing lands and nothing is held.

## Migration Plan

Old `Refused` entries keep holding their rows at their heads until the head moves. A bolt held today by a stop recorded before this change is landed again by ops on the user's word that stood for it, once its stop is cleared, as this change's rule says; no record is rewritten. Rollback is the revert: stops recorded meanwhile carry no `Refused` and hold nothing under the old code either.

## After deploy

None: every behaviour is code proved in the logic and end-to-end tiers, and nothing needs a step on a live host.

## Task notes

**1.1** `plugin/lib/plan.py`: `landing_blame(doc)` as Decision 1, a function of the record dict alone, returning `("bolt", None)` or `("stop", words)`; guard every field it reads (`state` a string, `failed` a list of dicts, `hash` and `not_run` strings, `result` a string), anything else a stop with words saying crew can't read the record. Fixture `tests/py/sluice-0.36.4/wait-failed-ran.json` and `wait-failed-not-run.json`, with a line in `tests/py/sluice-0.36.4/README` naming `records.rs` `Submission` (192–223) and `FailedTask` (129–150). Cases in `tests/py/test_landing.py`, class `TestTheBolts`: conflict; failed with a hash; failed timed out; failed with every check `not_run` (words name each task and why); failed with no `failed` list; withdrawn; landed; a record with a malformed `failed`.

**1.2** `wait_outcome` returns the exit and the record it read (or None); `submission_of` keeps the record's `failed`, `result` and `conflict` beside `id` and `state`; `landing_said` takes the blame, its recorded words for a stop the blame's words, for exit 3 sluice's last words, and its words to ops as Decision 4; the bolt's words unchanged. Cases in `tests/py/test_landing.py` on `landing_said`: exit 1 with a ran check (as today), exit 1 with not-run checks (stop words), exit 3 after `AGAIN` waits (stop), exit 2 with a conflict record (the bolt's), exit 2 at once with no record (stop).

**1.3** `landing_ended`: a stop recorded `bolt.submit` with `why`, `Head=p["TIP"]`, `Outcome="stopped"`, no `refused`; the at-once refusal (`p["refused"]` after an attempt) recorded the same when SUBMIT exited non-zero, with `Head` when the tip is known. `stops(entries)` and `stopped_at(stops, bolt, head)` beside `refusals` and `held_at`. Cases in `tests/py/test_landing.py`: `stops` reads the last entry per bolt, a later landed or refused entry supersedes it, an entry with no `Head` gives none.

**2.1** `landing_rows(order, rows, held, stopped)`: a row at a stopped head keeps `box: True`, its facts carrying `stopped` (head, words); `land_facts` and `land_read` pass `stops(entries).get(bolt)`; the rail's land line (`~10975`) adds the stop's words beside "can land" and keeps `can`. Cases in `tests/py/test_landings.py` (a stopped row has its box and its words; at a moved head none) and `tests/py/test_rail.py` (the line and the tell).

**2.2** `cards.py`: `row_paragraph` and `row_counts` say the stop as Decision 3, naming the owner's ops; `landings_card` and `landing_card` carry it unchanged otherwise. Cases in `tests/py/test_cards.py`: one row and three rows with a stopped one, its words on the face and in its box's detail.

**2.3** `landings_step`'s "Landing as you ticked" names each stopped bolt with its words (the step takes the stops); `card_read` prints a stopped bolt's words beside it in the bolts the send still lands. Cases in `tests/py/test_landings.py`: an answered card with a stopped ticked bolt is left; a follow names it as still landing with its words and the new card has no row for it.

**3.1** `tests/stubs/sluice` and `tests/stubs/wt-submit` as Decision 6; `tests/t-journey-land.sh`: a landing whose checks could not run keeps its row's box, the card left answered, `crew card read` naming it with its words, and a second `crew bolt submit` once the file is gone lands it; the existing conflict and failed-check cases still hold. Then `tests/moon-tasks` and `tests/moon.yml` if a test's reads change (`tests.10`).

**3.2** `plugin/roles/main-ops.md` step 2 as Decision 5. README's `crew bolt submit` paragraph, `plugin/skills/crew/SKILL.md`'s landing row and `plugin/bin/crew`'s `crew bolt submit` usage lines: one that did not land for its own content is held on its row; one sluice or its host stopped keeps its box and is submitted again once cleared (`docs.2`). `tests/t-docs.sh` stays green.

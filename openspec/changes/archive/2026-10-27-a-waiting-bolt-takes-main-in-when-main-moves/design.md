# Design

## Context

See proposal.md for why. What stands today, read on crew's main at 6159160:

- **The conductor's wait** forecasts each bolt its team holds against main through sluice (`reach`, `bolt_check`, `bolt_forecast`; `teams.21`, record 0036), but only when a wait runs (`stage_wait`), and a proven bolt waiting to land runs no stage. Its forecast entries go to the run record of the team's host, and the wait's once-only check reads that host's own entries (`local_entries`).
- **The landings card** (`raise_landings`, on the partition's main machine in main-level ops's name) forecasts its rows with `forecast_rows`: GitHub's main fetched in the kit's builder's main checkout, each bolt read where it lives (`gather.bolt_at`, `plan.19`), and `git merge-tree` of each bolt onto main and onto each row above it (`row_forecasts`). The result is only words on the row (`cards.forecast_said`): a row forecast to conflict with main keeps its box. And the card is raised only at events: a merge's end, a fix's start, a landing or a refused landing (`land_hand`), and the rail's sweep of a missing card.
- **A fix in flight** on a bolt already holds its row with no box, in the fix's words (`landing_rows`, `fixes_in_flight`, `fix_words`), and the rail's land row says the bolt lands once the fix has merged (`rail_rows`).
- **The rail's read with its sweep** (`rail_read(sweep=True)`) runs on every `crew rail` and on each refresh of the console's rail tab, every 30 seconds (`crew _rail` → `crew _views`). Its survey reads each kit at `origin/main` as the host last fetched it, with no fetch (`gather.now_ref`; `plan.18`, which rules a fetch per refresh out), and the fleet's timer fetches within minutes of a landing.
- **After the user's send**, `landings_step` counts a ticked bolt with a fix in flight as held: the card is closed saying it was held once nothing else is still to land.

Rules this design rests on: `teams.21` as read 2026-10-24 (the forecast as fresh as main; a conflict starts the take-main fix at once; the row says it takes main first and never that it can land; the card changed in place; the approval stands through the fix); `plan.8` (a bolt meets main before its landing only on a forecast conflict with what main has landed, by the team's take-main fix); `plan.16` (the landings card, one send for the ticked bolts); `plan.18` (every read of main is `origin/main` after a fetch; a refresh reads it as last fetched); `plan.19` (a bolt is read where it lives); `read.1`, `read.2`, `roles.4`, `code.3`, `code.7`, `code.9`, `state.1`. Pages whose area this touches: `plan.md` (`plan.py`, `gather.py`), `teams.md` (the wait), `briefs.md` (the conductor's and main-level ops's briefs), `docs.md` (README, the skill), `tests.md` (the tests).

## Goals / Non-Goals

**Goals:**

- A proven bolt waiting to land is forecast against main again whenever main moves, within one rail refresh of the main level's host reading the move.
- A row forecast to conflict with what main holds is never a box, on the card or on the rail's row, and its conductor is told the take-main fix once.
- A user's send keeps standing for a ticked bolt while it takes main in.

**Non-Goals:**

- Landing the bolt's new head on the same send once its take-main fix has merged, with no new word asked. That is `a-landings-approval-stands-through-taking-main-in`, built beside this in the same bolt: this change keeps the send standing up to the fix's merge, and that one decides what the send does with the head the fix made.
- Starting the fix by crew's own hand. The conductor starts it, as `teams.21` and record 0036 have it for a wait's forecast.
- A conflict with a submission only queued on main, which still holds nothing (`plan.8`).
- Any change to sluice or to the fleet's timer.

## Decisions

### 1. The landings card's own forecast is the instrument

The card's row forecast already reads main as `teams.21` asks, GitHub's main after a fetch, and each bolt where it lives, and it runs where the card is, on the main level's host. What it lacks is any consequence. So this change gives it one, rather than adding a second forecast: a row whose forecast against `main` names files takes main first.

Alternatives considered:
- **sluice's `submit main --check --head` for each waiting bolt**, as the wait runs it. It would also see main's queue, but a conflict with a queued submission holds nothing, so it adds nothing here. It runs on the team's host, reads the bolt by its name in the main checkout with no fetch, and refuses `--head` on an older sluice.
- **Run the conductor's wait for a waiting bolt**. No stage runs to wait on, and a wait is the conductor's call, not crew's.

`forecast_rows` also hands back the revision of main it forecast against (the commit `origin/main` names after its fetch, or `main` for a kit with no origin), for Decisions 2 and 3.

### 2. Main moving is read on the rail's sweep, with no fetch, and acted on by the card's raise

The trigger is the move itself. On the rail's read with its sweep on the partition's main machine, for each kit whose landings card is open, crew compares the revision of main the survey read for the kit at its builder's main checkout (`origin/main` as last fetched, no fetch, as `plan.18` has every refresh) with the revision the card's rows were last forecast against. When they differ, or when none was kept, it raises the card again (`raise_landings`), which fetches once and forecasts. When they match, nothing is fetched and nothing is raised.

- `gather.kit` names the revision it read main at (`main_at`), one `rev-parse` it already makes, guarded where an older gather leaves it out (`read.2`: a kit whose read lacks it is not judged moved; the sweep says so once per read).
- The revision the rows were last forecast against is kept on the main level's host beside the card's state, `~/.local/state/crew/cards/<label>/land/<kit>/main`, written by every raise that forecast against main. It is crew's own note of what it read, not the run record, so a raise that changes nothing on the card writes no entry and no commit (`state.1`), and a lost note costs one extra raise.
- The decision, which kits are due a raise, is a function of the open landings cards, the survey's revisions and the kept ones (`code.7`).
- A landing crew closes already raises the card (`landing_cards_closed` → `land_hand`), and that raise now forecasts again too, so a crew landing is acted on at once; a move of main by anything else (a record's submission, the user's own commit, a landing by hand) is read at the next sweep once the host's `origin/main` has it, which the fleet's timer brings within minutes.
- A move read with no raise in it (`step` "leave") changes no card: the raise passes no note of its own for a move, so the card is changed only when a row is, not on every landing on main.

This is the sweep's act, as its posting of a missing card is (record 0031 §1, §2); `crew board` still sweeps nothing (`state.4`). The rail's own rows are still made from what it reads, writing nothing.

Alternatives considered:
- **A fetch on every refresh** of each kit with an open card: one fetch per kit every 30 seconds, which `plan.18` rules out for refreshes.
- **Raise only at crew's own landings**: misses main moved by a record's or the user's submission, which `wt submit main` lands with no crew command (`state.3`), and every landing on a kit crew does not land.
- **`git ls-remote` per refresh**: still a network call per kit every 30 seconds.

### 3. A conflict with main holds the row as taking main first

`landing_rows` gains a third hold beside a fix in flight and sluice's refusal: a bolt **takes main first** when either

- the raise's forecast against `main` names files for it, or
- the run record holds a `forecast` on `bolt/<bolt>` at the bolt's present head naming a conflict with main and no queued submission (the wait's `teams.21` forecast, whose `Heads` carry no `#<n>`, or the raise's own), read by a new decision from the partition's entries and the bolt's head (`code.7`).

The record is read too so a known conflict does not turn back into a box when the card's own forecast could not be made, and so the rail, which forecasts nothing, can say it (Decision 5). The hold's words: "takes main first: forecast to conflict with main on <files> at <main's short sha>; <team>-conductor takes main in by a fix". A take-main fix in flight, a fix whose words begin "Take main into the bolt", holds the row as taking main first too, naming the fix and its words; any other fix holds it as today.

Rows held so drop out before the forecasts between rows are made, so a row is never forecast against a bolt that cannot land above it. The hold goes when the bolt's head moves and it reads proven with no conflict forecast: a forecast at an older head holds nothing.

The card's change follows from the existing step: a row held while the card waits is named in the change note and the card changed in place, or followed when its form must change (Pending You changes no card's questions), or withdrawn when no row can land (`rail-cards` "The landings card closes when nothing waits").

### 4. The conductor is told the fix once, and both forecasts share the once

When the raise's forecast finds a new conflict with main, crew tells the bolt's conductor the take-main fix with `crew tell` from the main level's host, which forwards to the team's host (`roles.4`, `code.3`), in the words `bolt_forecast` gives a wait, its fix named `take-main-<main's short sha>`, with `--bolt <bolt>` while the team holds two bolts (`teams.16`). It is recorded as a `forecast` on `bolt/<bolt>` with `Heads: bolt/<bolt>@<head> main@<main>`, the same form as the wait's, `Paths` and `Reached: told`, and only once the tell went through; a tell that fails records nothing and the next raise tries again.

Once-only reads the partition's run record from its branch (`read.5`), which holds the wait's forecasts too, so a conflict the wait already said is not said again by the raise. The wait's own once-only check keeps reading its host's entries; a raise's tell made on another host may be said once more by the next wait at the same heads, which names the same fix, and `crew fix` refuses a second fix of one name (`read.4`).

### 5. The rail's land row says it, and leaves it out of the tell

`rail_rows` reads the same recorded forecast (Decision 3) for each bolt otherwise ready to land, and for one taking main first says "takes main first: forecast to conflict with main on <files>, until its team's take-main fix moves its head", with `can` false, so the row's `crew tell <label>-ops "Land …"` leaves it out and main-level ops, which reads the rail's row for what can land (`main-ops.md` *Landing a bolt*, step 1), never submits it.

### 6. A wait's conflict with main raises the card at once

When `reach` records a bolt forecast to conflict with what main has landed (no queued submission), it hands the kit's card's raise to the main level's host (`land_hand`), so a waiting bolt's row is held as soon as the wait finds it, not at main's next move. A conflict with a queued submission hands nothing.

### 7. A send stands for a ticked bolt taking main in

In `landings_step`, after the user's send, a ticked bolt held only as taking main first, by Decision 3's forecast or by a take-main fix in flight, counts among the bolts still landing on the send, not among the held: the card is left while it takes main in, and is not closed counting it held. Any other hold, a fix of another kind or sluice's refusal, is held as today. What the send does once the fix has merged and the bolt reads proven at its new head is the sibling unit's (Non-Goals); until that lands, the step asks again at the new head as it does today.

### 8. The views

The rail's land row and the card's rows change in their words and their box, not in their shape: `board.agent_views` and the mod draw a held bolt's markers from the rail's rows, whose keys and `bolts` entries (`bolt`, `team`, `host`, `can`) stay as they are. So nothing the views draw changes, and `code.8` asks nothing of `plugin/hooks/status.js`.

## Risks / Trade-offs

- [Main moved by something other than a crew landing is read only once the main level's host's `origin/main` has the move, through the fleet's timer, and only while something reads the rail with its sweep there.] → The console's rail tab does every 30 seconds wherever the main level runs, and the conductor's wait still forecasts every bolt its team holds through sluice (`teams.21`). A landing crew closes raises at once.
- [A busy main, 53 landings in two days on switchboard-kit, raises the card at each move.] → A raise that changes no row changes no card and writes no entry; its cost is one fetch and a few `merge-tree`s on the builder's host, and each row's reading asked of its team's host as any raise asks it.
- [The take-main fix can be said twice, by the raise and then by the conductor's wait on another host.] → Both name the same fix, and `crew fix` refuses a second of one name.
- [Between the raise holding a row and the conductor starting the fix, the bolt waits on the conductor.] → The tell reaches its pane at once, and the row says who takes main in.
- [A `merge-tree` forecast is not sluice's formation on main.] → It is the same merge of the same two commits, `origin/main` after a fetch and the bolt where it lives, which is what sluice merges for a bolt's landing; sluice's queue holds nothing here (`plan.8`).

## After deploy

None: every behaviour here is code proven in crew's tiers, and nothing must be done on a live host. A host takes it when its crew moves to it, and its next raise forecasts at main as it stands.

## Task notes

**1.1** `plugin/lib/gather.py` `kit`: add `"main_at"`, the full sha `rev-parse --verify -q <now>^{commit}` already resolves (keep that call's answer rather than run a second). `gather.py` imports only the standard library (`code.1`). Contract case in `tests/contract/test_gather.py`: a kit with an origin reads `main_at` as `origin/main`'s commit, one with none as `main`'s.

**1.2** `plugin/lib/plan.py` `forecast_rows`: return the revision forecast against as a third value, `{"main": <sha>}` or None when the fetch or the read failed; update `raise_landings` (through `CardActs.forecast` and any test double of it in `tests/py/test_landings.py`) for the new shape. Logic cases in `tests/py/test_landings.py` beside `test_a_bolt_behind_main_names_main_first`.

**2.1** New decision `main_conflict(entries, bolt, head)` in `plan.py`: the latest `forecast` entry, not refused, whose `On` is `[bolt/<bolt>]`, whose `Heads` begins `bolt/<bolt>@<head[:7]> main@` and holds no `#` word, and has `Paths`: `(main's short sha, [paths])`, else None. Cases in `tests/py/test_forecast.py`: a wait's entry at the present head, a raise's entry, one at an older head, one with `#7`, one with no `Paths` (the unread form `unread_said` records).

**2.2** `landing_rows(order, rows, held, takes_main=None)`: `takes_main`, `{bolt: (main7, paths)}`, the raise's forecast conflicts with main merged with `main_conflict` for each row; a bolt in it, or with a fix in flight whose words begin "Take main into the bolt", is `box: False` with `why` beginning "takes main first:" and a `takes_main: True` mark; other holds as today. Keep the fix's hold words for any other fix. Cases in `tests/py/test_landings.py`: forecast conflict with main holds; a recorded conflict holds when the card's forecast was not made; a conflict only with a row above holds nothing; a take-main fix's words; another fix's words unchanged; a new head with no conflict has its box.

**2.3** `raise_landings`: forecast main for every row with a box first, hold those taking main first, then forecast the rest among themselves (`row_forecasts` with the held ones left out of `order`); write `CARDS/<label>/land/<kit>/main` with the revision whenever the forecast against main was made, what can't be written said on standard error and the raise going on. Logic-tier cases with the `CardActs` double.

**3.1** Tell and record (Decision 4): for each row newly taking main first by the raise's forecast, build the words with `bolt_forecast(team, label, bolt, {"conflict": {"paths": paths, "with": []}, "head": head, "onto": main}, done, two)`, `done` the `Heads` of the partition's `forecast` entries (`acts.entries(label)`), `two` from `held_by(plan, team)`; `crew.tell` the conductor; on success `record.emit(label, "forecast", [f"bolt/{bolt}"], why=f"bolt({bolt}): forecast to conflict with main", Heads=heads, Paths=" ".join(paths), Reached="told")`. Through `CardActs` (a `tell` act) so the logic tier holds a double. Cases in `tests/py/test_landings.py`: told once with the fix's command; not told again at the same heads; not told when the wait's entry has the heads; `--bolt` with two bolts; a failed tell records nothing.

**4.1** New decision `landings_moved(cards, mains, kept)` in `plan.py`: from each kit's open landings card (by label and kit), the survey's `main_at` for the kit at its builder's checkout, and the kept revision: the kits due a raise, a kit whose `main_at` is missing named as unread, not due. Cases in `tests/py/test_rail.py` or `tests/py/test_landings.py`: moved, not moved, no kept revision, no `main_at`, no open card.

**4.2** `rail_read(sweep=True)`: after `sweep_cards`, on the partition's main machine only, raise each kit `landings_moved` names (`raise_landings` with no note), what it did kept in the read beside `swept` (`read["moved"]`) and said by `rail_text` as the sweep's other acts are; a refusal said and the read going on. The builder's checkout path and host come from `builder(fleet, label, kit)`; its kit read is in `read["sv"]`. Logic case with the sweep's acts double; end-to-end in **7.1**.

**5.1** `rail_rows`: for each bolt otherwise ready to land, `main_conflict` from the partition's entries the rail already reads (`held`'s source in `rail_rows`) at the bolt's head; when it names one, `lands` is "takes main first: forecast to conflict with main on <files>, until its team's take-main fix moves its head", and `can` False. A fix in flight still reads as today. Cases in `tests/py/test_rail.py`: the line and the tell leaving it out; an older head holds nothing.

**5.2** `reach`: after recording a bolt's forecast conflict with main with no queued submission, `land_hand(fleet, label, kit)` for the bolt's kit; nothing for a queued one. Cases in `tests/py/test_forecast.py` with `land_hand` stubbed: handed for a landed-work conflict, not for `#7`.

**6.1** `landings_step`: after the send, a ticked bolt whose row is held with `takes_main` counts in `landing`, not in `held`; the outcome words unchanged for other holds. Cases in `tests/py/test_landings.py` beside `test_a_ticked_bolt_sluice_refused_is_held_and_the_rest_close_the_card`: ticked then taking main first leaves the card; ticked beside one that lands leaves it; a ticked bolt with another fix is still held.

**7.1** `tests/t-journey-land.sh`: a proven bolt as a row of its kit's landings card; a commit on the stub GitHub's main that conflicts with the bolt's file, fetched into the builder's `origin/main`; `crew rail --label <l>` on the main level's host raises the card again, holding the row taking main first, tells the conductor the take-main fix (read in the stub herdr's log), records the `forecast`; a second `crew rail` tells nothing and raises nothing. Add any file it newly reads to its `# Reads:` line and run `tests/moon-tasks`, committing `tests/moon.yml`.

**8.1** Words: `plugin/roles/conductor.md` *Forecasts and settling* gains that crew also tells it a waiting bolt's forecast conflict with main when main moves, which it acts on as the wait's, and *Fixes* that a take-main fix holds the row as taking main first; `plugin/roles/main-ops.md` step 1 names a row taking main first as one to leave out; README's landings card paragraph and `plugin/skills/crew/SKILL.md` say the card is forecast again when main moves and a row conflicting with main takes main first (`docs.2`). Checked by `tests/suite t-docs` and any brief case that reads those words.

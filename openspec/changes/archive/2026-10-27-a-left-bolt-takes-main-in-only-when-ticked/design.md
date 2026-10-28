# Design

## Context

See proposal.md for why. What stands on this bolt, which carries `a-waiting-bolt-takes-main-in-when-main-moves` (archived here 2026-10-27, not yet on main):

- **The landings card's raise** (`raise_landings`, on the partition's main machine in main-level ops's name) forecasts every row with a box against main first (`forecast_rows`, `row_forecasts`); a row forecast to conflict, or with a conflict the run record holds at its head (`main_conflict`), is held taking main first with no box (`landing_rows`' `takes_main`), and its conductor is told the take-main fix once (`main_told`, recording a `forecast` with `Reached: told`). The rail's sweep raises the card whenever main moves (`landings_moved`).
- **The conductor's wait** forecasts each bolt its team holds through sluice (`reach` → `bolt_check`, `bolt_forecast_read`, `bolt_said`), gives the fix's command for a conflict with what main has landed (`bolt_forecast`), records it with `Reached: wait` once per heads read from this host's entries (`local_entries`), and hands the kit's card a raise (`land_hand`).
- **What crew knows of "left"** is only on the card: a row the user cleared on their last send is shown unticked on the card that follows while its head stands, recorded as `<bolt>@<head>:left` in the post's or change's `Heads` (`cards.landings_card`, `card_heads`, `landings_step`'s `left`). On an answered card still open, the rows the user did not tick are known only from Pending You (`kit_card_state`'s `ticked`). Nothing records the user stopping a landing in ops's pane.
- **After the user's send**, ops runs `crew card read land/<kit>` (`card_read` → `landing_lines`), which prints a `crew bolt submit` of every ticked bolt; the card is raised again only at the next event or move of main.

So today a left bolt that conflicts is held with no box, its conductor told the fix, and the fix moves its head, which makes it a fresh row, no longer left (`landings_step`: "shown unticked … only while its head stands"). That is the churn the user named.

Rules this design rests on: `teams.21` as amended by record 0036 on 2026-10-24 and accepted 2026-10-26 (a left bolt forecast the same, its row saying what it finds, no fix until ticked, left on the card that follows); `plan.8` (a bolt meets main before its landing only by its team's take-main fix); `plan.16` (the landings card's send, or the user's words in ops's pane, is the word to land); record 0031 as amended 2026-10-24 (a send stands through taking main in; a card asked again says what changed); `signals.5` and `briefs.12` (the user's words read from the caller's transcript); `record.3` (no user words in the run record); `read.1`, `read.2`, `read.5`, `roles.2`, `roles.4`, `code.3`, `code.7`, `code.9`, `state.1`, `state.4`. Pages whose area this touches: `plan.md` (`plan.py`), `teams.md` (the wait, the command), `briefs.md` (the conductor's and ops's briefs), `docs.md` (README, the skill, the usage), `tests.md`.

## Goals / Non-Goals

**Goals:**

- A bolt the user left is forecast against main as any bolt is, its row keeping its box and saying whether it would take main first.
- No take-main fix is told for a left bolt, by the card's raise or by a conductor's wait, so crew moves no left bolt's head and it stays left.
- When the user ticks it, the fix is told then, its row taking main first and their send standing through it.
- A stop the user says in ops's pane is a fact crew holds, checked as their words.

**Non-Goals:**

- A ticked bolt landed on the user's words in ops's pane (`crew bolt submit --excerpt`) while it conflicts: it is submitted, sluice refuses it naming the conflict, and the team takes main in as `plan.8` has it today. This change only ends the stop there.
- A bolt not yet asked or ticked: it takes main in at once, unchanged.
- Any change to sluice, to the views' shape, or to how the card decides its form.

## Decisions

### 1. The raise decides which bolts are left, and records it

Only the raise sees everything "left" depends on: the card's rows and marks, the user's ticks on an answered card in Pending You, and the plan's heads. So the raise computes the kit's left bolts and records them, and the wait and the rail read that record.

A bolt is left, at a raise, when its head now is the head below and:

- it is marked `:left` on the card held while that card waits on the user; or
- the card held is answered and the user did not tick its row; or
- the kit's last recorded left set names it at that head and the card held has not ticked it (a left bolt stays left across the close of one card and the post of the next); or
- a `bolt.leave` of it is recorded after the kit's last recorded left set, at that head (Decision 4), and the card held has not ticked it since.

A bolt the user ticked on the card read now, a bolt landed or gone from the plan, and a bolt at another head are not left. The decision, `left_now`, is a function of the card state, the ticks, the heads and the entries (`code.7`).

When the set differs from the last recorded for the kit, the raise records it as one `landing.left` entry on the kit's landing row (`cards.row_object("land/<kit>")`) with `Key: land/<kit>` and `Left: <bolt>@<head7> …` (empty for none). A raise that changes nothing writes nothing (`state.1`). Its reader, `left_of(entries, key, heads)`, gives the last recorded set plus stops recorded after it, each at the bolt's present head, less any bolt with a later `bolt.submit` on the user's words (Decision 4); the wait and the rail use it. The card's own `left` facts, which mark rows unticked, become `left_now`'s set, so a stopped bolt shows unticked too.

Alternatives considered:
- **Read "left" from the card's `:left` marks alone.** Between the user's send and the answered card's close, a newly cleared bolt is unmarked, and a wait in that window would tell a fix. The marks are also gone once the card closes and none follows yet.
- **Parse the close's `Answer`** ("ticked y, left z"): crew's own words joined for a reader, not a field, and only written at the close.

### 2. A left row keeps its box and says it would take main first

`landing_rows` gains `left`, a set. A left bolt that `takes_main` names (by the card's forecast or by `main_conflict`) is not held: it keeps `box: True`, marked `would_main: (main7, paths)`. Its row's forecast words (`cards.forecast_said`, given the mark) say: "It would take main first if you tick it: forecast to conflict with main on <files> at <main7>. Ticked, its team takes main in by a fix, your send standing through it." A left bolt with a take-main fix already in flight, or with sluice's refusal, is held as today: those hold whatever the user chose.

A left row with a conflict against main is forecast against main alone and is not forecast against rows above it, as `row_forecasts` already does for any bolt forecast to conflict with main.

### 3. No tell for a left bolt, and the once is split by who it was said to

`main_told` skips each left bolt. Instead the raise records, once per heads, a `forecast` on `bolt/<bolt>` with the same `Heads`, `Paths` and `Reached: left`, and adds a sentence to the event's note it passes `landings_step`: "<bolt>, which you left, would take main first: forecast to conflict with main on <files> at <main7>". So a waiting card is changed in place the first time, and not again for the same heads, since nothing new is recorded then (rail-cards "A row the user left says whether it would take main first"). An answered card is left as it is, as for any change.

Once-only becomes a decision, `said_heads(entries, left)`: the `Heads` of `forecast` and `amendment` entries, counting a `Reached: left` entry only for a bolt still left. So a forecast said while left holds back nothing once the user ticks it, and `main_told` or the wait gives the fix at the same heads; a fix told once is told once, whichever said it. `main_conflict` reads `Reached: left` entries like any, so a ticked bolt whose card forecast cannot be made is still held taking main first.

### 4. A stop in ops's pane is `crew bolt leave`, checked as the user's words

`crew bolt leave <bolt>... --excerpt "<the user's words>" [--label L]` runs where ops runs, reads the words in the caller's own transcript exactly as `crew bolt submit --excerpt` does (`acts.heard`, `words_refusal`; `signals.5`), refusing in the same cases and recording nothing then. On the words, it records for each bolt a `bolt.leave` on `bolt/<bolt>` with `Head` (the bolt where it lives, `bolts_where`), `frm` and `Chars`, none of the words (`record.3`), and hands the kit's card a raise (`land_hand`) with the note "<bolt> was stopped on your words in <label>-ops's pane". A bolt no team holds, or not yet proven, is refused naming why: there is no landing to stop.

The stop ends when a later raise reads the bolt ticked on a send (it drops out of `left_now`, recorded), when a `bolt.submit` of it on the user's words is recorded after it (`left_of`), or when its head moves.

Alternatives considered:
- **Ops tells crew nothing and leaves the bolt out of its submissions.** The bolt's conductor's wait would still tell the fix, which is the churn.
- **Record the stop with no words read**, on ops's say: `roles.2` and `briefs.12` take only the user's own words as their word on a landing.

### 5. A conductor's wait says a left bolt's conflict and gives no fix

`reach` reads the partition's entries once (`partition_entries`, from the branch, `read.5`) for `left_of`, with each bolt's head from its stages. `bolt_said` passes `left` to `bolt_forecast`, which, for a left bolt and a conflict with what main has landed, gives: "bolt/<bolt>, which the user left on its kit's landings card, is forecast to conflict with main on <files>. Take nothing in while it is left: crew tells you the take-main fix once they tick it." It records the forecast with `Reached: left` and hands the card a raise, so the row says it at once. The wait's own once-only uses `said_heads` over its host's entries and the partition's, so a forecast said while left is said again, with the fix, once the bolt is ticked. A conflict with a queued submission reads as today.

### 6. Reading the send acts on it

`crew card read land/<kit>`, on an answered card, raises the card first, in this process, since it runs on the partition's main machine where the card is (`raise_landings`; `code.9`: the raise answers within a command's time, as every event's raise does). That raise reads the ticks: a bolt ticked that was left drops out of `left_now`, a conflict holds it taking main first, and `main_told` tells its conductor the fix, recorded `Reached: told`. `landing_lines` then leaves out of the `crew bolt submit` it prints each ticked bolt the run record holds forecast to conflict with main at its head (`main_conflict`, the heads from the card's rows), saying "<bolt> takes main first: its team takes main in by a fix, and your send stands for it". A raise that fails is said and the read goes on, printing what it would have.

### 7. The rail's land row

`rail_rows` reads `left_of` from the entries it already reads. A left bolt the record holds in conflict with main at its head reads "left by the user: takes main first once ticked, forecast to conflict with main on <files>", with `can` false, so the row's tell leaves it out. A left bolt with no conflict reads as today.

### 8. The views

The rows' words and boxes change, not their shape: `board.agent_views` and the mod read the rail's rows' keys and `bolts` entries (`bolt`, `team`, `host`, `can`), which stay. A new run-record act (`landing.left`, `bolt.leave`) is read by no view. So `code.8` asks nothing of `plugin/hooks/status.js`.

## Risks / Trade-offs

- [A left bolt's row says "would take main first" from a forecast as old as the last raise.] → The rail's sweep raises the card on every move of main, and reading the send raises it again before ops lands anything.
- [Between the user's send and ops's read, a conductor's wait still reads the last recorded left set, so a bolt ticked then waits for the read for its fix.] → Ops reads the send as soon as it is woken; the wait never tells a fix for a bolt the user has not ticked, which is the error that costs.
- [A stop recorded at one head lapses when the head moves, as a cleared row does.] → A head moves only by a fix someone started for the bolt; the card then asks for it again, saying what changed.
- [`crew card read` now raises a card.] → It writes only what any raise writes, and only on the main machine; a refused raise changes nothing and the read still prints.

## After deploy

None: every behaviour here is code proven in crew's tiers, and nothing must be done on a live host. A host takes it when its crew moves to it; builds-reach-the-phone, unticked on swancloud's landings card, reads as left at its next raise.

## Task notes

**1.1** `plugin/lib/plan.py`: new decision `left_now(card, ticked, heads, recorded, stops)`: `card` as `kit_card_state` gives it (or None), `ticked` its ticks, `heads` {bolt: head now} of the kit's rows, `recorded` the last `landing.left` set {bolt: head7}, `stops` [(bolt, head)] of `bolt.leave` entries after it. Returns {bolt: head7} per Decision 1. Reader `left_of(entries, key, heads)`: the last non-refused `landing.left` with `Key` key, parsed `<bolt>@<head7>`, plus `bolt.leave` entries after it (`On` `bolt/<b>`, `Head`), less a bolt with a later non-refused `bolt.submit` carrying `frm`, each kept only where its head prefixes `heads[b]`. Cases in `tests/py/test_landings.py`: marked on a waiting card; unticked on an answered card; carried across a close; a stop; ticked ends it; a moved head ends it; a submit on words ends a stop.

**1.2** `raise_landings`: compute `left_now` once the card state and rows are read; pass it as the card's `left` facts (in place of `landings_step`'s own for post, change and follow, unioned with it); record `landing.left` through `acts.emit` when it differs from `left_of`'s. Logic cases with the `CardActs` double: recorded once, not again unchanged.

**2.1** `landing_rows(order, rows, held, takes_main=None, left=())`: per Decision 2, `would_main` mark and box kept for a left bolt in `takes_main` with no fix in flight and no refusal. `cards.forecast_said(forecast, why=None, would=None)`: the would-words first when `would` is given; `cards.landings_card`'s row consequence passes `r.get("would_main")`. Cases in `tests/py/test_landings.py` and `tests/py/test_cards.py`.

**3.1** `said_heads(entries, left)` in `plan.py`; `main_told(…, left)` skips left bolts; the raise records `Reached: left` once per heads for each left bolt `found` names, and builds the note sentence, passed with the event's note to `landings_step`. Cases in `tests/py/test_landings.py`: left, told nothing, recorded `left`, the card changed with the sentence; raised again, nothing; ticked at the same heads, told and recorded `told`.

**4.1** `crew bolt leave`: parser beside `bolt submit` (`tests/py/test_parser.py`); `bolt_leave(fleet, a)` reusing `bolt_submit`'s excerpt check (factor it out if it is inline), its acts through a double for the logic tier; refusals for no words, words not the user's, no team, not proven; `bolt.leave` with `Head`, `frm`, `Chars`; `land_hand` with the note; the act in the entry-name table beside `bolt.submit`. Cases in `tests/py/test_pane_landing.py`.

**5.1** `bolt_forecast(team, label, bolt, doc, done, two=False, left=False)`: the left words of Decision 5 for a landed-work conflict; `reach` reads `partition_entries` once, `left_of` with each held bolt's head, `said_heads` over local and partition entries; `bolt_said` records `Reached: left` for a left bolt and still hands the raise. Cases in `tests/py/test_forecast.py`: left, no fix command, `Reached: left`; once; ticked at the same heads gives the fix; a queued submission unchanged.

**6.1** `card_read`: for an answered `land/<kit>` card, `land_hand(fleet, label, kit)` before reading the lines (it raises in process on the main machine); `landing_lines(…, main_first=…)`: leave out each ticked bolt `main_conflict` holds at its card head, with the sentence of Decision 6. Cases in `tests/py/test_card_commands.py`.

**7.1** `rail_rows`: `left_of(entries, f"land/{kit}", heads)` per kit; Decision 7's line and `can` False. Cases in `tests/py/test_rail.py`.

**8.1** `tests/t-journey-land.sh`: a proven bolt left on its kit's landings card by a send clearing it (stub Pending You answer); a commit on the stub GitHub's main conflicting with the bolt's file; `crew rail --label <l>` raises the card, the bolt kept unticked with its box and the would-words, the conductor told nothing (stub herdr's log), a `forecast` with `Reached: left` recorded; a send ticking it, then `crew card read land/<kit>` tells the conductor the take-main fix and prints no submit of it. Add anything it newly reads to its `# Reads:` line, run `tests/moon-tasks`, commit `tests/moon.yml`.

**9.1** Words (`docs.2`): `plugin/bin/crew`'s usage, README's landings paragraph and `plugin/skills/crew/SKILL.md` gain `crew bolt leave` and that a left bolt is forecast with no fix until ticked; `plugin/roles/main-ops.md`: the user's words stopping a landing are recorded with `crew bolt leave … --excerpt`, and a ticked bolt `card read` says takes main first is left out; `plugin/roles/conductor.md` *Forecasts and settling*: a left bolt's forecast says to take nothing in, and the fix comes once the user ticks it. Checked by `tests/suite t-docs`.

## Context

See proposal.md, *Why*. The bolt's earlier unit, `a-batchs-card-left-on-another-host-is-raised-again` (archived 2026-10-22, landed into the bolt at e723971d), built the mechanism for batches alone: `cards.stranded` names the owner's newest copy under a key that this host's sign-in can't reach, `sweep_judged` puts a batch row with one in `again`, `sweep_cards` raises it through `raise_batch` handed `dead`, which builds with `built_again`, and `stranded_said` words the report. That unit's design named proposal cards as stranded the same way and left them out, since its intent named batches; the design agent named them for the planner (signal 2026-10-22-swancloud-planner-968cd584/02). This unit takes the same path for every card crew raises.

Rules this change rests on: `briefs.11` (crew raises the rail's cards itself, each in the name of the role whose row it is: the planner's the proposals' and the batches', a conductor's its bolt's landing, main-level ops's the deploys and steps, the design agent's its records'), `briefs.13` (each of the six cards has one form built by crew; one card per thing), record 0031 §1 (six cards raised at fixed points, keyed by the thing; "no card waits on an agent remembering"), `briefs.15` and `briefs.16` (a record's card through `crew record`, in the design agent's name), `read.1` (crew does not guess what it can't read: a record's alternatives it doesn't hold), `read.5` (the run record read from the branch), `record.3` (no words in the run record), `state.4` (the views write nothing; the sweep is the act), `code.7` (decisions are functions of facts), `code.8` (what the agents' views draw). It touches the areas of `plan.md` (`plan.py`), `tests.md` (`tests/`) and `docs.md` (README, the skill), and `teams.md` for `plugin/bin/crew`'s usage header only. It edits nothing under `docs/` (`docs.7`), and moves nothing `board.agent_views` or `status.js` draw: a card raised again is a card posted, which every view already reads (`code.8`).

What crew does now, read on the bolt at bb1e74c7:

- **Only a batch row is judged stranded.** `sweep_judged` computes `cards.stranded` only for keys matching `batch/\d+`. A proposal's, landing's, deploy's or step's card posted on another host and never closed is open in the record, so the row is in neither `none` nor `again`, and nothing is raised. One recorded lost goes to `none` and is posted through its raise with no word that an older copy is dead.
- **Each kind's raise already posts when this host holds no card.** `raise_proposal` (event `sweep`, act `("change", SWEPT)`), `raise_land`, `ops.raise_deploy` (`deploy_move` gives `post` with no card held) and `ops.raise_step` (`step_point` over this host's entries) all reach `row_card_change`, which posts through `card_posted` when `cards.card_under` over this host's entries finds none. None of them reads `row["dead"]`.
- **A record's card has no row and no raise.** Record cards are listed apart (`rail_text`, "decision records waiting on you"), swept only to close at their status (`record_settled`), and `RAISES` has no `record`. A record card stranded on the host the main level left stays listed open until `CARD_DAYS`, and `crew record --accepted` on the new host closes nothing (`card_closed`: "holds none open on this host").
- **`crew record --proposed` reads the alternatives from a file it is handed** and keeps nothing of it; its `record.proposed` entry says nothing of whether the card offered alternatives.
- **The owners' hosts.** `row_owner` puts a proposal's and a batch's on the partition's main machine (the planner), a deploy's and a step's there too (main-level ops), and a landing's on the machine of the team holding the bolt (its conductor). A record's owner is `<label>-design` on the main machine, where `record_status` refuses to run anywhere else.

## Goals / Non-Goals

**Goals:**
- Every row's card that its owner's host can't reach gets one live card there at the rail's next read, saying the older copy is dead.
- A record's card stranded so is raised again too, from the record on the kit's main, or named with the command that raises it when crew can't build it.

**Non-Goals:**
- Reaching, asking after or closing the older copy, which no sign-in but its own reaches; the user dismisses it in the app.
- A card posted anew on the owner's host by its own event's command (a proposal rewritten, a deploy offered again, a merge moving a bolt's head) while a stranded copy stands: that command reads only this host's entries and posts as it does now. The rail's next read finds the newer post and raises nothing. Only `crew record --proposed` looks, since the read hands records back to it.
- A deploy offered or a step recorded on the host the main level left: the rail's operations rows are read only from the main level's host's own ops entries (`rail_record`, `ops.rows`, `plan.14`), so such an offer is no row on the new host, and its card is listed as an open card whose row is gone. That is the operations' design, named for the design agent in the change's report.
- Asking Pending You after a record's card held on this host, which the sweep does not do for records today.

## Decisions

### Every row kind is judged stranded, on its owner's host

In `sweep_judged`, drop the `batch/<n>` match: every row in `mine` (record 0031's key form, its owner running here, no post refused lately) has `cards.stranded(entries, key, owner, here)` computed, and goes to `again` when it names a card, and out of `none`. The rows' owners and hosts are `row_owner`'s, so a landing is judged on its team's host and every other row on the main level's host, as the rules put each card's owner (`briefs.11`). `sweep_cards` already drops an `again` row whose kind has no raise and raises the rest through `raised(l, dict(row, dead=older), owner)`, reporting `lost` with `stranded_said`'s words; those stay. The report for a raise that posts none becomes "its raise posted none", but a batch's, which keeps "its batch no longer waits to be read".

This also changes a card recorded lost to its owner on its own host while its row waits: it was in `none`, posted with no word of its older copy; it is now in `again`, posted saying the older copy is dead, as rail-cards' "A row's card lost to its owner is posted again" already asks.

### Each raise posts with the dead-copy summary when handed an older copy

`raise_batch` already builds with `built_again(cards.batch_card)` when `row.get("dead")`. The same goes into each other raise, at the builder it hands `row_card_change`:

- `raise_proposal` passes `dead=bool(row.get("dead"))` to `raise_proposal_at`, which gains a `dead=False` keyword and builds with `built_again(cards.proposal_card)` when set. Other callers pass nothing and are unchanged.
- `raise_land` builds with `built_again(cards.landing_card)` when `row.get("dead")`. Its `follows_of` reads this host's entries, where the stranded copy is not, so the new card follows nothing of it.
- `ops.raise_deploy` and `ops.raise_step` build with `plan.built_again(cards.deploy_card)` and `plan.built_again(cards.step_card)` when `row.get("dead")`. A deploy's `follows_of` reads the gathered record, where the stranded copy is open, so it is not a declined card and is not followed; a step's reads this host's entries.

`built_again` survives `card_built`'s second build with the reading's link, as it does for the batch. `row_card_change` finds no card held here, since the older copy is on another host or closed lost, so it posts once through `card_posted`, never adding the dead words twice.

### A record's stranded card is judged from the whole record

A record has no rail row, so `sweep_judged` takes the design agent's owner and host, `design=(owner, host)`, as it takes the planner's, and, where `design[1] == here`, judges each record key in record 0031's form (`record/<kit>/<4 digits>`) under which the entries hold a `card.post` of the design agent's: one whose last status `crew record` recorded is proposed (`record_settled` gives None and a `record.proposed` is there), whose last `record.proposed` is not `State: settled in the pane`, whose post was not refused lately (`refused_lately(..., key=)`), and for which `cards.stranded` names a card, goes into `again` as `(dict(label, key, group="records", alternatives=<its last record.proposed's Form is alternatives>), older)`. `sweep_cards` passes `design` (the partition's `<label>-design` and main machine) and reads that row's owner from it, as it reads `owners` for the rows. `RAISES` gains `"record": "raise_record_again"`.

### The record's raise reads the record as `crew record` does

`record_status`'s read of the record (the kit from the teams file, its checkout on this host, its main now by `MAIN` and `kit.main_now`, the one file `docs/adr/<nnnn>-*.md`, its last two commits, and `record_facts`) moves into a function `record_read(fleet, label, kit, number, status, alternatives=None)` returning the facts, `card_where` of the kit, the commit and its subject. `record_status` calls it unchanged in behaviour, and so does the new `raise_record_again(fleet, row, acts=None)`:

- with `row["alternatives"]`, it refuses, saying crew keeps no copy of record `<nnnn>`'s alternatives, so `<label>-design` raises it again with `crew record <kit> <n> --proposed --alternatives <file>`. `sweep_cards`' `raised` turns that refusal into a `left` report in those words (`read.1`).
- otherwise it reads the record with status `proposed`, and a record whose file no longer holds proposed on main, or that crew can't read, is refused in `record_read`'s words, reported `left` the same way;
- it posts through `raise_record(..., dead=True)`, which gains `dead=False` and builds with `built_again(cards.record_card)` when set.

### `crew record --proposed` records the card's form, and posts saying the older copy is dead when one is stranded

`record_status` adds `Form="alternatives"` to the `record.proposed` entry when `--alternatives` was given: a fact, no words of the file (`record.3`). An entry written before this change has no `Form` and reads as a record with none, which the risk below names. Before raising, `--proposed` gathers the partition's record (`record.gather(fleet, [label], since)`, as `ops.raise_deploy` already does) and hands `raise_record` `dead=True` when `cards.stranded` over it names the design agent's copy under the key. When the record did not answer whole, it posts as now and says the older copy could not be looked for.

## Risks / Trade-offs

- [The user answered the stranded copy and is asked again] → the cost of a card crew can't read, as for batches. A proposal answered on mac-studio's card that crew never saw is asked again on deneb.
- [A record raised with alternatives before this change reads as one with none] → the sweep raises it again as a plain approval of the record, without its alternatives. Alternatives cards are rare and the approval still holds the record whole; the design agent can raise it again with its file. Named in the report.
- [The older copy stays listed as an open card with no row, or as an old record card, naming a host crew left] → it ages out after `CARD_DAYS` (14 days), as the batch's design already accepts. `record_reading` takes the newer post under the key as the row's, so a record's newer card replaces the older in the record list.
- [A landing judged on a team's host only when the rail is read there] → as every landing card's sweep is today.

## After deploy

Nothing. crew is live on a host once its main is pulled, and every behaviour here is proved in the logic tier and in `tests/t-cards.sh` on the stub Pending You.

## Task notes

### 1.1

In `sweep_judged`, compute `older` for every row in `mine`, not only `batch/\d+`. Rewrite the docstring sentence that says "but a batch's row, batch/<n>" to say every row's, and add the record rows (task 2.1). In `tests/py/test_rail.py` `TestSweepJudged`: extend `MOVED` with `land/y` (its conductor on the box), `deploy/dev` and `op/dev/2` (wldn-ops on the box). Replace `test_a_proposals_card_held_or_lost_on_another_host_is_left_as_it_is` with a case where proposal 13's card held on mac-studio, or recorded lost there with no newer post, is in `again` and not in `none`; add the same for `land/y`, `deploy/dev` and `op/dev/2`; and one where the rows' owner runs on mac-studio and the read is on the box, which puts nothing in `again`. Run `tests/suite logic`.

### 1.2

In `sweep_cards`, the `again` loop's `left` words: "its batch no longer waits to be read" for a `batch/` key, else "its raise posted none". In `TestSweep`, with the `Acts` stand-in's raises for proposal, land, deploy and op each posting when handed `dead`: the sweep reports `lost` on the older card with `new` and `stranded_said`'s words; a raise returning None is reported `left`, "its raise posted none". Update `sweep_cards`' docstring: every row's card, not a batch's alone.

### 1.3

`raise_proposal` → `raise_proposal_at(..., dead=bool(row.get("dead")))`; `raise_proposal_at` takes `dead=False` and uses `built_again(cards.proposal_card)` for both `row_card_post` and `row_card_change` when set. `raise_land` uses `built_again(cards.landing_card)` when `row.get("dead")`. In `ops.py`, `raise_deploy` and `raise_step` use `plan.built_again(...)` of their builder when `row.get("dead")`. Each docstring says so in a clause. Cases in `tests/py/test_cards.py`, beside `test_the_sweeps_raise_of_a_batch_handed_an_older_copy_this_host_cant_reach_posts_it_saying_that_copy_is_dead`: `raise_proposal_at` with `dead=True` and no card held posts one card whose summary starts with `cards.DEAD`, and without it the plain summary; the same for `raise_land`, stubbing what the batch case stubs and `land_held`, `land_facts`, `landing_opened`, `landing_preview`. In `tests/py/test_ops.py`, `raise_deploy` and `raise_step` handed a row with `dead` post a summary starting with `cards.DEAD`. Run `tests/suite logic`.

### 2.1

`sweep_judged` takes `design=(None, None)`. Where `design[1] == here`, for each key matching `record/[a-z0-9][a-z0-9-]*/\d{4}` that a `card.post` by `design[0]` names in `entries`, apply *A record's stranded card is judged from the whole record*; a small helper reading the key's last `record.proposed` (its `State` and `Form`) keeps the loop thin. `sweep_cards` passes `design=(f"{l}-design", fleet["partitions"][l]["machine"])` and, in the `again` loop, takes the owner of a `group == "records"` row from it. Add `"record": "raise_record_again"` to `RAISES`. In `TestSweepJudged`: record 21's card posted on mac-studio, `record.proposed` before it, read on the box → in `again` with `alternatives` False; with `record.accepted` after → not; with `State="settled in the pane"` on its last proposed → not; with `Form="alternatives"` → in `again` with `alternatives` True; read on mac-studio → not. Run `tests/suite logic`.

### 2.2

Move `record_status`'s read into `record_read` as *The record's raise reads the record as `crew record` does* says; `record_status` keeps its argument checks and calls it. Add `raise_record_again` and `raise_record`'s `dead`. In `TestSweep`, the record row handed to the stand-in's raise with `dead`; one with `alternatives` whose raise refuses is reported `left` with words naming `crew record switchboard-kit 32 --proposed --alternatives <file>`. In `tests/py/test_cards.py`: `raise_record_again` with `record_read` stubbed posts one card whose summary starts with `cards.DEAD` in `wldn-design`'s name; with `alternatives` it refuses naming the command and posts nothing. Run `tests/suite logic`.

### 2.3

`record_status`: `Form="alternatives"` on `record.proposed` when `--alternatives`; before `raise_record`, gather the partition's record since `cards.DAYS` days ago and pass `dead=True` when `cards.stranded` over it names a card of `<label>-design` under the key; when `record.gather` names hosts missing, print that the older copy could not be looked for and post as now. In `tests/t-cards.sh`, beside the alternatives case at "design switchboard-kit 33 --proposed --alternatives": the `record.proposed` entry for 33 carries `Form: alternatives` and record 21's carries none; then a case where a `card.post` of `wldn-design` under `record/switchboard-kit/0034` from another host stands in the record (written to the branch's run record the way the file's other cross-host cases write one) and `crew record switchboard-kit 34 --proposed` posts a card whose summary starts with "An older copy of this card was lost". Run `tests/suite t-cards`.

### 3.1

README, in the rail's sweep sentence of the *Pending You* section: replace "a batch's card posted from a host other than the main level's … never asked after nor closed from there" with every row's card posted from a host other than its owner's, the main level's or, for a landing, its team's, or recorded lost to its owner, posted again there through its kind's raise, and a decision record's still proposed raised again from its record on the kit's main, one raised with alternatives named with the `crew record` command that raises it; and rewrite the sentence "A kind with no raise on a rail read, a record's, has its rows left as they are…" so it no longer names the record. In the `crew record` sentence: `--proposed` posts the card saying an older copy is dead when one is held on a host the main level left. The crew skill's `crew rail` row and `plugin/bin/crew`'s usage header for `crew rail` and `crew record` say the same in a clause each (`docs.2`). Take the bolt's other unit, `every-reading-cards-session-is-tried-every-time`, into the place first, as the code stage's prompt says, since it edits README too. Run `tests/suite t-docs`, then `tests/suite --affected` once, at the end.

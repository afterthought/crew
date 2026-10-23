## Context

Today a bolt's landing card is its own: crew raises it under `land/<bolt>`, in its conductor's name, on the host of the team holding it, once the bolt reads proven (`raise_land`, `land_facts`, `cards.landing_card`). The conductor adopts it, passes the user's yes to main-level ops with `crew tell`, and ops runs `crew bolt submit <bolt>`, which submits one bolt to sluice and waits for its outcome, then `crew bolt land <bolt>`. The bolt's reading session (plannotator) and its preview run on the team's host under the same key, and the conductor's `crew card wait land/<bolt>` returns the reading's notes. The rail has one landing row per bolt (`rail_rows`), owned by its conductor (`row_owner`), and the board marks each bolt from its row (`board.markers`).

Record 0031 as amended and accepted on 2026-10-23 makes the landing card one per kit's main, in main-level ops's name; `briefs.11`, `briefs.13` and `plan.16` already carry that, and the user's own word of 2026-10-23 settles that ops submits every approved bolt together, in order, each closed as it lands. The record leaves two things to this unit's reading of Pending You: whether a row is an approval of its own or the ticks of one list approve, and when a row's reading session starts. See proposal.md for why.

Rules this design relies on: `plan.16` (one landing procedure, ops's), `briefs.11` and `briefs.13` (crew's cards, their forms, one card per thing changed in place), `roles.2` (a landing only on the user's word), `state.3` (main moves only through sluice), `state.4` (no service), `read.1` (refuse, never guess), `read.5` (the run record from the branch; a host read over ssh only for its kits' stages), `code.3` (a command about a team or main level forwards to its host), `code.7` (decisions are functions of facts), `code.8` (the agents' views follow what crew models), `code.9` (a command answers within an agent's shell; long work is waited on), `teams.12` and `teams.21` (forecasts), `docs.2` (a command's change reaches README, the skill and the usage). Area pages this change touches: `plan.md` (`plan.py`), `teams.md` (`plugin/bin/crew`, `crew.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `tests.md` (`tests/`), `docs.md` (`README.md`).

## Goals / Non-Goals

**Goals:**
- One card per kit's main, its rows the proven bolts in the plan's order, each with what its bolt's card carried and the conflicts forecast against main and the bolts above it.
- One send lands every ticked bolt in that order, through one `crew bolt submit`, each closed as it lands, a refused one held on its row while the rest go on.
- Each bolt's reading and preview keep working as they do, now as its row's.

**Non-Goals:**
- Changing what makes a bolt proven (`landing_unready`, `landing_facts`, `briefs.12`).
- Ordering bolts by anything but the plan; the user's note is what moves one.
- Landing bolts of two kits in one command, or across partitions.
- A forecast of three or more bolts merged together: rows are forecast pairwise, as units are.

## Decisions

### 1. The card's key, owner and host

The card is `land/<kit>`, `<kit>` the kit's name as the teams file gives it (`t["kit"]["name"]`), posted in `<label>-ops`'s name on the partition's main machine, where ops's sign-in is, through `row_card_change` as every row's card is. A `land/<x>` key names a kit's landings card when `x` is the name of a kit a team of the partition builds, read from the teams file, and otherwise a bolt: its reading's and preview's key on its team's host, and the key of an old per-bolt card. So the decision that reads a `land/` key takes the partition's kit names as a fact. To keep the two apart, a bolt is refused a name that is a kit's of its partition, at the plan write that adds it.

Alternatives: a new key form such as `landings/<kit>`, which needs no kit list, but the record names `land/<kit>` and the older `land/<bolt>` cards are withdrawn either way; keeping the card on the conductor's host, which puts one kit's card under several conductors' names and breaks `follows` (`briefs.11`: a card follows only one in its own name).

### 2. Where each part runs

A row's reading and preview stay where they run now, on the team's host, under `land/<bolt>`, opened by the code that opens them now (`landing_opened`, `landing_preview`). The kit's card is raised on the main machine. The two are joined by two internal commands, each forwarded to its host (`code.3`):

- `crew _land-row <label> <bolt> --json`, run on the team's host: reads the bolt's landing facts there (`land_facts`), opens or keeps its reading and preview, ends them when the bolt does not read proven, and prints the row: its facts with its link or why it is unread, its preview, or why it is no row.
- `crew _land-card <label> <kit>`, run on the main machine: the raise of the kit's card (`raise_landings`), which asks `_land-row` of each candidate bolt's team host, forecasts the rows, builds the card and posts, changes, follows or closes it.

Every event that changes a row today, on the team's host, hands the raise to the main machine with `_land-card` in place of raising a card of its own: the merge's end (`landing_after_merge`, `team_freed`), a fix's start (`landing_held`), a preview's end, `crew card session land/<bolt>`, `crew card wait land/<bolt>` when it starts a reading, and `crew bolt land`'s close (`landing_cards_closed`). The rail's sweep on the main machine raises it for a kit row with no card open, as for any row.

Alternatives: writing each row's facts into the run record from the team's host for the main machine to read, which puts a second, staler copy of the facts on the branch and a new entry kind on every head move; reading the team's session files over ssh, which `read.5` rules out for anything but a kit's stages.

### 3. The card's form

Read in Pending You's `post_request` schema (pendingyou MCP, read 2026-10-23): an `approve` takes risk high and no `highStakes`; a `multi` list holds two to five options and takes `highStakes`, "the same test as risk high"; `questions` hold up to four lists, each up to five options, and need `about`; `update_request` changes a card's options but never its kind or its questions (`cards.CHANGED`).

- **One row that can land**: the card is today's `approve` of risk high, not reversible, its action "Land <bolt> on <kit>'s main", so the commonest case looks as it does now.
- **Two to five**: one `multi` list with `highStakes`, an option per row in order, id `land:<bolt>`, label `<n>. <bolt>`, its detail the row's counts, batches, verdict and conductor, its consequence the row's forecast, every option recommended (ticked), `multi` `{min: 0, max: n}`.
- **Six or more**: lists of five at most in order, each a question `rows-<k>`, `about` naming the kit's main, as the proposal card's lists are (`cards.proposal_card`).
- **Held rows** have no box: they are named on the face with why.

The face holds one inline Markdown artifact, "What lands on <kit>'s main, in order", a paragraph per row: its place, bolt and conductor, its units and chores one a line, its batches, sluice's verdict and when, how far main moved, what a yes frees, its forecast, and its reading, preview and pull request as links; then held rows. Links also go in the details, the readings first, then previews and pull requests as `ARTIFACTS` leaves room. Title: "Land on <kit>'s main: <n> bolts in order", or today's "Land the bolt <bolt> on <kit>'s main" for one. Summary: how many wait, that one send lands the ticked ones in the order shown, and that a note can move one or name a defect.

A change of form, one row to a list or a list to lists, is followed rather than changed (`cards.revision(kind_changed=True)`), and a card of lists is always followed (`questions=True`), as `briefs.13` has for proposals.

Alternatives: a row as an approval of its own, which needs `questions` of kind `approve`, at most four bolts a card and a hold per bolt, ten holds where the user asked for one send; one approval of the whole, which leaves no way to hold one back but a note.

### 4. When a row's reading starts

At the row's raise, as a bolt's reading starts now. Starting it at the user's tap would need something listening for the tap, a service crew does not run (`state.4`); Pending You opens a link and tells crew nothing.

### 5. Forecasts

sluice 0.36.4's forecast (`sluice submit main --check --head bolt/<bolt> --json`) forms the bolt on main and the submissions already queued there; its `--after` names submissions by number (`sluice-core/src/ops.rs` `forecast_onto`, read 2026-10-23), so it cannot stack a bolt on bolts not yet submitted. crew forecasts the rows itself, as it forecasts units (`teams.12`): on the host of the kit's first building team (`builder`), in its main checkout, after `git fetch -q origin`, `git merge-tree --write-tree --name-only` of each row's bolt onto `origin/main`, and onto each row above it from their merge base. A bolt's branch is read as `origin/bolt/<bolt>`, or the local `bolt/<bolt>` when that host holds it and GitHub does not; one crew can read neither way has its forecast said as not made, with why, and keeps its box (`read.1`: said, never guessed; a forecast holds nothing). The decision, which row conflicts with what on which paths, is a function of the order and each pair's paths (`code.7`); the git calls are the act. The conductors' own forecasts against main through sluice (`teams.21`) stand as they are.

Alternatives: merging the rows one onto another in sequence, which `git merge-tree` cannot do without commits to take merge bases from; asking sluice to forecast each after the ones before, which it cannot until they are queued.

### 6. Submitting several bolts

`crew bolt submit <bolt>...` takes one or more bolts of one kit, in the order given, refused before anything is submitted when they are of two kits, one is named twice, or one is held by no team. For each, on its team's host: the main checked (`main_held`), a worktree at `<kit>/places/land-<bolt>`, and `wt submit main --no-wait --json --no-remove` there, whose JSON gives the submission's number. The next bolt is submitted as soon as the one before is queued when both are on one host, so sluice tests them as one chain and lands them in submission order; on another host, only once the one before has ended, since each host's sluice keeps its own queue. crew does not pass `--after`: sluice keeps a submission waiting while one it is after is out of the queue (`sluice-core/src/order.rs`, "each only once every `after` is landed or ahead of it"), so a refused bolt would strand every bolt behind it, and submissions of equal priority land in the order submitted anyway.

Each submission is then waited on in order, `sluice wait <n> --timeout 9m --json` in the kit's main checkout, again while it exits 5. Once its outcome is in, the worktree is removed and the mains read as `LANDING` reads them now, and `landing_said` judges it. A landed bolt is marked (`LANDED_MARK`), recorded (`bolt.submit`), and closed at once by `crew bolt land`'s own code (`bolt_land`), in the same process, so it is closed as it lands; one `bolt_land` refuses is named with why and `crew bolt land <bolt>` as the act that closes it, and the command goes on. A bolt that did not land is recorded `bolt.submit` refused, with sluice's words and the head that was submitted (`Head`), which is what holds its row, and the command goes on. It prints each outcome as it comes and exits non-zero when any did not land. Like today's, it outlasts an agent's shell and is run in the background and waited on to its end (`code.9`).

Alternatives: ops running `crew bolt land` itself for each landed bolt, which leaves each closed only when ops next reads the output; `--after`, which strands the rest behind a refusal.

### 7. A refused landing holds its row

A bolt whose last `bolt.submit` entry was refused at its present head is held: its row shows sluice's words and that it waits for its team's fix, with no box. The fix that takes main into it moves its head, and it reads proven again with a box. A fix in flight holds a row the same way, its row naming the fix. Both are read where the row is read: the record from the branch (`read.5`), the head from the kit.

### 8. The answer, the close and what follows

Ops adopts the card with the line crew tells it, since the command that raises it is never ops's own (`cards.told_to`). `crew card read land/<kit>` prints, besides what it prints of any card, the bolts the user ticked in the card's order and the command that lands them, `crew bolt submit <a> <b> …`, and the note. Ops runs it, in the note's order when the note moves one, and passes a note naming a defect in a bolt to that bolt's conductor.

At each raise, the card held is judged by one decision of facts (`landings_step`): the rows, the card's state from Pending You, and the ticked bolts of its answer.

- No row can land and no card is held: nothing.
- No row can land and a waiting card is held: withdrawn, saying why (each row held, or none proven).
- Rows can land and no card is held: posted, following the kit's last landings card only when that one was answered and closed with rows left, else following nothing.
- A waiting card is held: changed in place, or followed when its form changed or it holds questions, with a change note naming what changed.
- An answered card is held: left as it is while any ticked bolt is still in the plan and not held; then closed with what landed and where GitHub's main holds it, what was held, what was left, and, when rows can land, a new card posted following it, a bolt the user cleared shown unticked with "Left on your last send". A send ticking none closes the card at once, landing nothing.

### 9. The rail and the board

`rail_rows` makes one row per kit, `land/<kit>`, with `bolts`, each bolt's name, team and what it waits on, in the plan's order, its `what` a line per bolt, and its answer `crew tell <label>-ops "Land <a>, <b>."` naming the bolts that can land, or none. `row_owner` gives it `<label>-ops` on the partition's machine. `row_gone` closes a kit's card whose row is gone as "nothing waits to land on <kit>'s main", and withdraws an old `land/<bolt>` card, swept on its own host, as "<bolt> is now a row of <kit>'s landings card". `blind_land` and `sweep_judged`'s blind set cover a kit row while a host holding one of its bolts does not answer. `board.markers` marks a bolt from the land row whose `bolts` hold it; the agents' views draw ops's card where the conductor's was (`code.8`).

### 10. The briefs

- `main-ops.md`, *Landing a bolt*: the word is the user's send on the kit's landings card, adopted and woken as its deploy cards are, or their words in the pane; step 1 checks each ticked bolt; step 2 is one `crew bolt submit` in the card's order, the note's when it moves one, as a background command, which closes each as it lands; a bolt that did not land is told to its conductor and the user in sluice's words; "Land one bolt at a time." goes; step 3 is `crew bolt land` only for a bolt the submission named as landed and not closed.
- `conductor.md`: its landing card goes. When its bolt reads proven it tells `{{MAIN_OPS}}` in one line that the bolt is proven and on the kit's landings card; it waits on the bolt's reading with `crew card wait land/<bolt>` as now, acting on notes from it and from ops; a fix holds the bolt's row, and the row comes back once the bolt reads proven again.
- `planner.md`: a bolt lands on the user's send on its kit's landings card, main-level ops's.
- `crew.py`'s card words (`cards_how`) name `land/<kit>` as main-level ops's card, and the skill and README the several bolts of `crew bolt submit` (`docs.2`).

## Risks / Trade-offs

- [A raise reaches each row's host over ssh, once per row] → rows are few, and the raise already reads each team's kit there; a host that does not answer leaves its rows off the card with why, and the rest are raised (`read.3`).
- [Pairwise forecasts miss a conflict that only three bolts together make] → sluice still tests the chain and refuses what conflicts; the refused bolt is held on its row while the rest land.
- [Bolts of one kit on two hosts land one host after the other, not as one chain] → their order holds; the second host's bolts wait for the first's outcome, a few minutes each.
- [An old per-bolt card open on a host the main level does not sweep] → every host of the partition is swept on the rail's read (`sweep_sessions`), and its card closes there.
- [A landed bolt `bolt_land` cannot close] → named with its command; the card waits for it as a ticked bolt still in the plan, and ops closes it by hand.

## Migration Plan

Nothing to run by hand. Once a host loads this crew, the next rail read withdraws each open `land/<bolt>` card on its own host and raises `land/<kit>` on the main machine; each running reading and preview stays, as its row's. An agent's brief reaches it at its next restart, which crew gives when the plugin changes (`teams.19`). Rolling back restores per-bolt cards the same way, the kit's card swept as a row gone.

## After deploy

None: the change is crew's code and briefs, proved by its tests, and what it changes on a host, the cards, happens at the next rail read with no step of anyone's.

## Task notes

**1.1** `plan.py`: `land_key(key, kits)` returning `("kit", name)`, `("bolt", name)` or None, `kits` the names of the kits the partition's teams build (`crew.kits_of` over `crew.partition_of(fleet, label)["teams"]`). `cards.row_object` takes the same kit names and gives `kit/<kit>` for a kit's key and `bolt/<bolt>` otherwise; thread the names to its callers (`record_keys`, `record_settled`, the `card.post`/`card.close` entries' `On`). The plan write that adds a bolt (`bolt add` in `may_write`'s path, or where `bolt add` is applied) refuses a name in `kits`. Cases in `tests/py/test_landings.py` (new): a kit's key, a bolt's key, an old `land/<bolt>/<head>` key, a bolt named as a kit refused.

**1.2** `plan.py`: `landing_rows(order, rows, held)` → the card's rows in the plan's order, each `{bolt, box: bool, facts | why}`; a bolt with a fix in flight or a `bolt.submit` refused at its present head (`refused_at(entries, bolt, head)`) is held, with no box. Cases: plan order kept; a fix in flight held; a refusal at the old head not held after the head moved; a refusal at this head held.

**1.3** `plan.py`: `row_forecasts(order, pairs)` → per row its conflicts `[(with, paths)]`, `with` "main" or a bolt above it, `pairs(ours, theirs)` the paths `[]`, or None when git can't tell, a row with a None pair saying its forecast was not made. The act: `forecast_rows(fleet, label, kit, bolts)` on `builder(fleet, label, kit)`'s host, `kit_git` fetch, then `merge-tree --write-tree --name-only --no-messages` with `ok=(0, 1)`, refs `origin/bolt/<b>` else `bolt/<b>` (`head_of`), parsed as `merge_tree` parses. Cases: two bolts on one file; one against main; an unreadable ref said, box kept.

**2.1** `cards.py`: `landings_card(f)` beside `landing_card`, which it reuses for one row (key `land/<kit>`). `f`: kit, rows (each the facts `landing_card` takes now, plus team, conductor, forecast, link or unread, preview), held (each bolt and why), left (bolts cleared on the last send), follows. Forms as Decision 3; `landings_form(n)` → "approve", "multi" or "lists". Cases in `tests/py/test_cards.py`: one row is the approve of risk high titled as today with no `highStakes`; three rows one `multi` with `highStakes`, three ticked options `1. y`…, details and consequences within Pending You's budgets (`LABEL`, `DETAIL`); seven rows two questions with `about`; a held row on the face with no option; a cleared bolt unticked with "Left on your last send"; the face's Markdown naming each row's reading, preview and pull request; at most `ARTIFACTS` artifacts.

**2.2** `cards.py`: `follows_of("land", {"kit": kit}, entries, by)` → the kit's last `land/<kit>` card in `by`'s name when it was answered and closed with rows left (its close's state and the entry the raise writes), else None; `ROWS` and `CREWS` words for the kit's card. Cases in `tests/py/test_cards.py`.

**2.3** `plan.py`: `landings_step(rows, card, ticked, in_plan)` → `("none",)`, `("withdraw", why)`, `("post", follows)`, `("change", note, kind_changed)`, `("leave",)`, `("close", outcome, then_post)`, as Decision 8. Cases in `tests/py/test_landings.py`, one per bullet of Decision 8.

**3.1** `plan.py`: `_land-row`, the act on the team's host: `land_held`, `land_facts`, `landing_opened`, `landing_preview` as `raise_land` calls them, its JSON the row; a bolt that does not read proven ends its reading and preview (as `sweep_sessions` and `preview_release` end them) and prints why. `raise_land` goes; its callers call `land_hand(fleet, label, kit)`, which runs `crew _land-card <label> <kit>` on the partition's machine through `crew.on_machine` and `crew.crew_argv`, saying a failure and refusing nothing of the event that called it. Register both in the parser and the dispatch tables (`("_land-row",)`, `("_land-card",)`), refused to any caller but crew's own forwarding as the other `_` commands are.

**3.2** `plan.py`: `raise_landings(fleet, label, kit, acts=None, note=None)` on the main machine (refused elsewhere, naming the machine, as `raise_land` refuses a wrong host): the plan's bolts of the kit held by a team, each with every unit merged, `_land-row` asked of each on its team's host (`read.3`: a host that does not answer named, its rows left off), `landing_rows`, `forecast_rows`, `landings_step`, then `row_card_change` or `row_card_close` in `<label>-ops`'s name with `card_where` of the kit. Cases: logic in `tests/py/test_landings.py` through a fake `CardActs` as `tests/py/test_card_commands.py` does; end to end in `tests/t-journey-land.sh`: two bolts proven, one card `land/<kit>` posted by `<label>-ops` on the stub, its two options; the second's head moved, the card changed in place.

**3.3** `plan.py`: the events hand the raise: `landing_after_merge` and `team_freed` (no longer `raise_land` per bolt; `frees_note` becomes the row's change note), `landing_held` (ends the row's reading and preview, then hands), the preview's end (`landing_preview`'s callers near `preview_change`), `card_session` and `card_wait` for `land/<bolt>` (`land_session`, `land_start`, `land_waited`: a bolt is a row when `_land-row` gives it one, refused as the specs say when not), `landing_cards_closed` (hands, the kit's card judged by `landings_step`). `session_refusal` keeps a bolt's reading on its team's host and refuses `land/<kit>` sessions. Cases in `tests/py/test_card_commands.py` and `tests/t-cards.sh`: `crew card wait land/y` with no row refused; with a row, a reading started and the kit's card carrying its link.

**4.1** `plan.py`: `crew bolt submit` takes `bolt` with `nargs="+"`; `submit_order(bolts, hosts)` → for each bolt whether it is submitted after the one before is queued or after it ended; `submit_refusal(bolts, kits, teams)` for two kits, a repeat, a bolt no team holds. The act splits `LANDING` into `SUBMIT` (the worktree, `wt submit main --no-wait --json --no-remove`, the submission's number, the tip, `OLD`) and `LANDED` (the worktree removed, `LEVEL`, `MAINS`, `HELD_*`, `RC` from the wait), with `sluice wait <n> --timeout 9m --json` looped while it exits 5 between them; `landing_said` reads `LANDED`'s report as it reads `LANDING`'s. A landed bolt: `LANDED_MARK`, `bolt.submit`, `bolt_land` called with an argparse namespace for it, its refusal printed with `crew bolt land <bolt>`. A bolt not landed: `bolt.submit` with `refused=` sluice's words and `Head=` the tip. Exit non-zero naming each not landed. Update `tests/stubs/wt-submit` to pass `--no-wait --json` to the stub sluice, which already queues and answers `wait` (`tests/stubs/sluice`). Cases: `tests/py/test_landing.py` for `submit_order`, `submit_refusal` and `landing_said` on `LANDED`'s report; `tests/t-journey-land.sh`: three bolts on one host submitted in order, the second's conflict refused and recorded, the first and third landed and out of the plan, exit non-zero.

**4.2** `cards.py` `answer_lines`, or `card_read` in `plan.py` for a `land/<kit>` key: the ticked bolts in the card's order, from `choiceIds`, each question's answers, or an approval of its one row, and `crew bolt submit <them> --label <label>`. Case in `tests/py/test_card_commands.py`.

**5.1** `plan.py`: `rail_rows` one row per kit as Decision 9; `row_owner` for `land/<kit>`; `row_gone`, `blind_land`, `sweep_judged`, `stray_cards`, `CARD_KEYS`, `card_of`'s words. Cases in `tests/py/test_rail.py`: two bolts one row, its tell naming both in order; a bolt waiting on a batch named on the row; a refused bolt held; an old `land/<bolt>` card withdrawn as a row of its kit's card; a kit row's card owned by `<label>-ops` on the partition's machine.

**5.2** `board.py` `markers` and whatever of `agent_views` reads a land row's key; `plugin/hooks/status.js` where it draws a landing card or row. Cases in `tests/py/test_board.py` (a bolt marked from its kit's row; the pinned keys case updated) and `plugin/tests/status.test.ts` when the views' shape moves.

**6.1** `plugin/roles/main-ops.md`, `conductor.md`, `planner.md` as Decision 10; `crew.py` `cards_how` and `needs_how` words that name a landing card; `plugin/skills/crew/SKILL.md` and `README.md` for `crew bolt submit`'s bolts and the kit's card; `plugin/bin/crew`'s usage header. Cases in `tests/t-briefs.sh`: main-ops's brief has no "Land one bolt at a time" and names `crew bolt submit` with several bolts; the conductor's brief raises and passes no landing card. `tests/t-docs.sh` stays green for the usage. After changing what a test reads, `tests/moon-tasks` and `tests/moon.yml`.

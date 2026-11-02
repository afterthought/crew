# Design

## Context

See proposal.md for why. A kit's landings card (`land/<kit>`, main-level ops's) is raised by `raise_landings` in `plugin/lib/plan.py`. Each post or change records its rows as `Heads`, `<bolt>@<head7>`. When the user has answered, `landings_step`'s answered branch compares each row's head now with the head the card showed. Any bolt whose head differs is `anew`: it is taken out of what the send lands, and the card closes or is followed by a new card that asks for it again. A ticked bolt sluice refused is held (`landing_rows`, `refusals`). Once nothing of the send is in flight, the card closes saying "Held: z", and the close's `Heads` keeps only the bolts still landing, so the yes for `z` is gone. After `z`'s take-main fix merges (`landing_after_merge` → `land_hand` → `raise_landings`), `z` reads proven at a new head and a new card asks for it. That is the path the user met four times in three hours.

What an earlier send still lands is read three ways. `landings_sent` reads it from the run record's closes, `{bolt: head}`. `rows_unsent` takes such bolts off the next card only while their head is the one sent. `sent_left` (used by `crew card read land/<kit>` through `landings_earlier`) lists them for ops, dropping one refused at the head sent. `card_read` refuses when ops holds no open card under the key (`card_held`).

The rules this rests on:
- `plan.16`: the user's send is the word to land, and ops submits what they ticked.
- `plan.19`'s details, read 2026-10-23: "The user's word on a landing card stands for the bolt's work (record 0031 as amended 2026-10-24, accepted)…".
- `plan.8`: a conflict is the bolt's, and its team takes main in by a fix.
- `roles.2`: a landing runs only on the user's word, and this change carries their word without making one.
- `read.1`: what crew can't read is named, never guessed.
- `state.2`: the approval is read from the run record crew already writes, with no new field in the plan.
- `code.7`: decisions are functions of facts.
- `code.9`: one fetch per read, within a command's time.
- `code.8`: nothing the views draw changes.
- `docs.2`: the docs change with the command.
- `docs.7`: no page of `docs/architecture/` or `docs/adr/` is edited.

Area pages touched: `plan.md` (`plugin/lib/plan.py`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `teams.md` (`plugin/bin/crew`'s usage header), `docs.md` (README) and `tests.md` (`tests/`).

## Goals / Non-Goals

**Goals:**
- One yes per bolt's work: a head moved by taking main in, or by a level of the host's copy, keeps the send.
- A bolt whose work changed is asked again with what changed, the card naming the commits.
- Ops can read and act on a standing send whether or not a landings card is open.

**Non-Goals:**
- What every follow-on card says about the earlier answer, its time and its words. That is `a-card-asked-again-says-what-changed`. This change only adds the bolt's own commits to the landings card's note.
- Deploy cards (`cards.head_anew` in `ops.py`) and the bolt's own legacy `land/<bolt>` card, which gives way to the kit's.
- Checking at `crew bolt submit` that the head submitted is the one crew read. Sluice proves whatever head it is given, as today.

## Decisions

### 1. A bolt's own work is its non-merge commits that main lacks

A bolt's own work at a head is the set `git rev-list --no-merges <head> ^<main>`, with main being GitHub's main after a fetch (`plan.18`). The send stands at the head now when that set is the same at the head sent and the head now. Crew reads this as two lists, each of which must be empty: `git log --no-merges --format='%h %s' <now> ^<sent> ^<main>` (gained) and `<sent> ^<now> ^<main>` (lost).

A take-main fix adds only merge commits. The coder brief's take-main fix merges `origin/main`, resolves conflicts in the merge commit and "change[s] nothing else". Sluice's landing of the fix on the bolt is a merge too, and main's own commits are excluded by `^main`. So taking main in, with or without conflicts, leaves the set alone, which is what the user asked for. A level of the host's copy to GitHub's leaves it alone when GitHub's copy holds the same commits, even when the two heads are different take-main merges with neither an ancestor of the other. That was the e104bcf/d64278b case in `plan.19`'s details.

Alternatives considered:
- **Ancestry with no non-merge commits added.** This fails the level case above, where neither head is an ancestor of the other.
- **Comparing the bolt's diff against main** (patch-id of `merge-base..head`). This changes whenever a conflict is resolved, so it would ask again exactly where the user said it must not.
- **Trusting the fix's name** (`take-main-…`). That is a name, not a fact about the work: a fix so named that also commits a test change would carry an approval for work the user never saw.

### 2. When the work can't be compared, the bolt is asked again, saying why

When the fetch fails, a head can't be resolved (an abbreviated sent head that is missing or ambiguous), or git fails, the work read returns why. The send does not carry, and the card asks again and names why (`read.1`). Holding the bolt instead was rejected: it would leave a proven bolt with no way on but a hand read. Carrying the send was rejected too: that guesses the work unchanged.

### 3. The read is made where forecasts are made

`bolt_work(fleet, label, kit, moves)` runs in the main checkout of the kit's first building team (`builder`), as `forecast_rows` does, through `kit_git`. It does one `fetch -q origin` for a kit with an origin. It reads main at `refs/remotes/origin/main`, or `refs/heads/main` for a kit with no origin. For each bolt it reads the head the same way `forecast_rows` resolves where the bolt lives (`gather.bolt_at`). `moves` is `{bolt: (sent, head)}`, where `head` is None when the caller doesn't have it yet and the read resolves it. The result is `{bolt: {head, gained, lost, why}}`, `why` set when it could not tell. Asking the bolt's team host through `crew _land-row` was rejected: a new flag on a command forwarded across hosts breaks on a host whose crew is older. `CardActs.work` wraps it so the logic tier can stand in for it, as `CardActs.forecast` does.

### 4. The decisions take the work as a fact

- `send_stands(sent, head, work)`: True when the heads match by prefix, or when `work` was read and both its lists are empty. False otherwise, including when it couldn't be read.
- `work_said(bolt, sent, head, work)`: the words for a bolt asked again. One form names what it gained, "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease; …". One form names what it lost, "…no longer holding: …". One form says crew can't tell, "crew could not tell whether z's own work changed since your send at abc1234: <why>". Each list gives five subjects at most, then "and N more".
- `rows_unsent(rows, sent, work)`: a row with a box whose sent head differs is removed when the send stands. It is returned as asked again, with its words, when the send does not stand.
- `landings_step(…, work=None)`, answered branch: a moved ticked bolt whose send stands is not `anew`. It counts as landing while it has its box, and as still held while it has none. Every ticked bolt that is held and whose send stands goes into the close's or the follow's `Heads` at the head they sent, and the outcome says "Held: z, <why>; your send stands for it: it lands once its team's fix has only taken main in and sluice has proven it, with nothing asked". An `anew` bolt's part of the outcome is `work_said`'s words.
- `sent_left(sent, now, in_plan, refused, work)`: `now` is `{bolt: head or None}` for the bolts sent. A bolt is listed when it is in the plan, its head now is read, its send stands, and sluice did not refuse it at its head now. It returns the bolts it can't tell of, with why, beside the list.

### 5. The raise reads the card before its rows

`raise_landings` reads the card's state and the ticked bolts first, then `landings_sent`. It builds `moves` for every bolt sent or ticked whose row's head differs from the head sent, and calls `acts.work` once for those (none when nothing moved). It then runs `rows_unsent` and `landings_step` with the work. The words for a bolt asked again are put before the post's note ("Raised as the bolts stand") or the change's note, so the card that asks again says what changed. The close path passes `Heads` when the step returns standing bolts, as the follow path does.

### 6. `crew card read land/<kit>` reads a send with no card open

`landings_earlier` gets each sent bolt's head now and its work from one `acts.work` call, with `head` None, and passes them to `sent_left`. `card_read` for a kit's key, when ops holds no open card, no longer refuses. It prints "no landings card of <kit> is open" and the lines `landing_lines` gives for the earlier sends, with an empty card. A bolt it can't tell of is printed as "can't tell whether the user's earlier send still lands z: <why>" and left out of the submit command. For any other key the refusal stands.

### 7. The briefs

Main-level ops's *Landing a bolt*:
- A bolt the user ticked whose head moved only by taking main in, or by its copy's level, still lands on that send once its conductor says it is proven again. Ops reads it with `crew card read land/<kit>`, which prints it with or without an open card, and asks nothing.
- A bolt whose own work changed is asked again by crew.
- The user's words in ops's pane stand the same way, quoted again with `--excerpt`.

The conductor's *Fixes*: once a take-main fix has merged and the bolt reads proven, a bolt the user's send ticked lands on that send, and is told to ops as proven as always. Otherwise its row has its box again.

## Risks / Trade-offs

- **A merge commit that changes more than main's side** (an "evil merge") carries the send. → The coder brief's take-main fix changes nothing beyond the merge. Sluice proves the merged head before anything lands, and the user's reading of the bolt shows it.
- **One more fetch on the builder's host per raise when a head moved.** → It runs only when a sent or ticked bolt moved. The same host already fetches once for the forecasts.
- **A sent head stored as seven characters can be ambiguous.** → It is said and asked again (Decision 2). Rare at crew's sizes.
- **A send stands for days if the bolt waits.** → That is the user's rule: the yes is for the work. Clearing the bolt on a later card is not possible while it stands, since it is no row, as with today's earlier sends.

## Migration Plan

None. The run record's closes already hold `Heads` in the form this reads. A held bolt's send that closed before this lands was never recorded, so that bolt is asked once more.

## After deploy

None. Each behaviour is proved in crew's tiers. A host takes the change by swancloud's timer or pin like any landing.

## Task notes

**1.1** In `plugin/lib/plan.py` beside `held_at`, add `send_stands(sent, head, work)` and `work_said(bolt, sent, head, work)` (Decision 4). `work` is `{head, gained: [(sha7, subject)], lost: [...], why}` or None. Cases in `tests/py/test_landings.py`: heads equal by prefix with no work; both lists empty; one gained; one lost; why set; six gained giving five and "and 1 more".

**1.2** `rows_unsent(rows, sent, work=None)` returns `(rows, landing_bolts, asked)`, with `asked` being `[(bolt, words)]`. Update its callers and `test_the_bolts_a_followed_send_still_lands_are_no_row_of_any_card_after_it_while_their_head_stands`. Add a case where a moved row whose send stands is no row, and one where a moved row whose work changed stays a row with `work_said`'s words.

**1.3** `landings_step(rows, card, ticked, in_plan, landed=None, note=None, here=False, work=None)`. In the answered branch:
- `anew` leaves out bolts where `send_stands(was[b], h, work.get(b))`.
- `standing` = ticked, in the plan, held, and not in `anew`.
- "close" becomes `("close", outcome, then, standing_heads)` and "follow" keeps its shape, with its landing list taking the standing held ones at their sent heads too.
- The "Held:" words say the send stands, as in Decision 4.
- The `anew` words are `work_said`'s.

Update `test_a_ticked_bolt_sluice_refused_is_held_and_the_rest_close_the_card` (its close now carries `z@abc1234` and the words) and `test_a_ticked_bolt_proven_again_at_a_new_head_is_asked_again_rather_than_waited_for` (work gained). Add cases:
- A moved ticked bolt with unchanged work is left, `("leave",)`.
- A held-only send closes keeping the bolt.
- Work that can't be read is asked again with why.

**1.4** `sent_left(sent, now, in_plan, refused, work=None)` returns `(bolts, unknown)`, with `unknown` being `[(bolt, why)]`. Held is now judged at the head now, `held_at(refused, b, now[b])`. Update `test_what_an_earlier_send_still_lands_leaves_out_the_landed_the_asked_again_and_the_refused_at_its_head`, and add:
- Refused at the sent head, now at a new head with unchanged work: listed.
- Now's head unread: unknown.
- Work changed: not listed.

**2.1** Add `bolt_work(fleet, label, kit, moves)` after `forecast_rows`, reusing its ref resolution: move that loop into a helper both call, so the forecasts and the work read the bolt at one ref. Use `kit_git(…, "log", "--no-merges", "--format=%h %s", now, f"^{sent}", f"^{main}")` both ways, after `rev-parse --verify -q <sent>^{commit}`, whose failure gives `why`. Add `CardActs.work`. Logic cases with `kit_git` monkeypatched, as `test_a_bolt_on_github_is_forecast_where_it_lives` does: a kit with no team building it; a fetch refused; an unresolvable sent head. In `tests/contract/test_git.py`, add one case per behaviour Decision 1 assumes, each naming `bolt_work`, in a scratch repo:
- Main moves and is merged into a bolt with a conflict resolved in the merge, then that branch is merged with `--no-ff`: both lists are empty.
- A fix commit merged: it is listed as gained.
- Two take-main merges from the same bolt tip, neither an ancestor of the other: both lists are empty.

**2.2** In `raise_landings`, read the card state before `rows_unsent`. Collect `moves` from `landings_sent` and from the answered card's `heads` for ticked bolts whose row head differs. Call `acts.work` once. Pass the work to `rows_unsent` and `landings_step`. Put `asked`'s words before the post or change note. Pass `Heads` on the close when `standing_heads` is set. Cases in the raise section of `tests/py/test_landings.py`, with a stand-in acts:
- The refused bolt's close keeps it, and on the next raise, at a new head with unchanged work, no card is posted.
- At a new head with a gained commit, a card is posted whose note names it.

**2.3** In `landings_earlier`, read `now` and `work` by one `acts.work(label, kit, {b: (h, None)})` for the sent bolts still in the plan. In `card_read`, for a kit's key with no card held, print "no landings card of <kit> is open" plus `landing_lines(label, {}, [], earlier)` and the unknown lines, and refuse nothing. `landing_lines` prints the unknown ones as Decision 6 says. Cases in `tests/py/test_landings.py`:
- `test_the_read_of_an_earlier_send_reads_the_plan_only_when_one_stands_and_refuses_when_it_cant`, updated.
- No card held, printing the submit.
- A head unread, left out of the command.

**3.1** `plugin/roles/main-ops.md`, *Landing a bolt*: the paragraph on reading the send and step 2's paragraph on a bolt that did not land, as Decision 7 says. Replace "crew … closes it … once every bolt the user ticked has landed or been held" with words saying a held bolt's send stands. `plugin/roles/conductor.md`, *Fixes*, the paragraph on taking main in: as Decision 7. `tests/t-briefs.sh` asserts the new phrases for both briefs with `has`, and `lacks` the conductor's "its row on the kit's landings card has its box again" as the only outcome.

**3.2** README's landing paragraph near the rail cards, `plugin/skills/crew/SKILL.md`'s `crew card read` row, and `plugin/bin/crew`'s usage line for `card read`: a kit's landings card read with no card open prints what an earlier send still lands. `tests/suite t-docs`.

**4.1** `tests/t-journey-land.sh`, after the three bolts where the second is refused:
- The second's take-main fix is started, delivered as a merge of main alone on the stub, and merged.
- Then: no landings card is posted for it; `crew card read land/<kit>` as ops, with no card open, prints it under the earlier send and its `crew bolt submit`; that command lands it, and `bolt.land` is recorded.

Update the opening comment to say so. Run `tests/moon-tasks` and commit `tests/moon.yml` if its reads changed.

**5.1** `tests/suite --affected`.

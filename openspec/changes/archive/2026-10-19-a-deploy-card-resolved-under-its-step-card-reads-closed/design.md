# Design

## Context

crew holds a card as open for as long as the run record has its `card.post` and no `card.close` that went through (`cards.card_under`, `plan.record_reading`). It learns that a card closed in only two ways. Either crew closes it itself, or crew asks Pending You about it while changing or closing it. The second way was added by 5eebfa74 on 2026-10-19: `cards.ended` reads `get_request`'s status, and `row_card_change` and `card_closed` then record a card already ended "ended in Pending You already" (`plan.ENDED_ELSEWHERE`) and send nothing more.

`cards.ENDED` lists `closed`, `cancelled` and `expired`. Pending You 0.35.1 has no `closed` status. Its statuses, read on 2026-10-19 from the fleet's install (`/nix/store/…-pendingyou-0.35.1`), are:

- `pending`, `snoozed` and `delegated` while a card waits (its wake mod's `OPEN`, `mod/hooks/wake.js` line 18, and `plan.OPEN`);
- `answered` once the user has answered;
- `resolved`, `cancelled` and `expired` once it is over (the wake mod's `CLOSED`, line 19; `dist/format.js` `isClosed`, where `resolved` reads "is already handled. Nothing to do.").

Pending You's guide (https://www.pendingyou.com/skill.md, read 2026-10-19, *Follow up with a new card*) says what makes a card `resolved` besides an `ack_answer`: "Posting it picks up the answered card it follows, as `ack_answer` would without an outcome". It also says "`follows` takes one of your own cards that they've answered or that's closed".

mac-studio's run record for 2026-10-19 shows the sequence. The user approved `deploy/mac-studio`'s card `req_3d1bf1e7cca848098393` (`ops.approve` at 13:17:07Z). The deploy recorded its step `a0e9c0f70891` waiting on the user at 14:02:04Z. crew posted `op/mac-studio/1`'s card following the deploy card at 14:02:09Z (`cards.follows_of("step")`), and Pending You resolved the deploy card. At 14:02:12Z the deploy's end (`crew ops record --act end`) read the card and saw `resolved`. Since that is not `answered`, `cards.close_call` chose `cancel_request`, which Pending You refused: "This request is already closed." The rail's sweep then tried 28 more times by 18:46:19Z. At 18:50:22Z the offer of d35fbf2 found the card held (`ops.deploy_move` "change"), `cards.revision` chose "change", and `update_request` was refused: "This was already answered; follow up with reply_in_thread." deneb's offer of d35fbf2 at 18:50:15Z found no card held, because its deploy card was closed at its end at 14:04:53Z, before any step followed it. So deneb's offer got a new card, which the user approved at 18:53:45Z.

The rules this change relies on:

- `briefs.16`: crew posts, changes, closes and reads its own cards, recording each act from Pending You's own reply.
- `briefs.11` and `plan.14`: a deploy's card is crew's, raised by `crew ops offer` and closed at the deploy's end. A step's card is raised by `crew ops step`.
- `read.1`: a status crew can't read is never taken as closed.
- `read.2`: Pending You's statuses are read as the tool gives them now.
- `state.2` and `state.4`: what is open is read from the run record alone.
- `record.1` and `record.3`: one entry per act, in crew's own words.
- `code.7`: which statuses are ended, and which open card a post follows, are decisions.
- `tests.4`, `tests.11` and `tests.12`: the reproducing case goes in the logic tier, and the stub pendingyou is made to behave as Pending You does.

The code this change touches is under the `plan.md` area (`plugin/lib/plan.py`). `cards.py` is named in no area page's paths, and the card rules it builds on are on `briefs.md`. The change edits no page in `docs/architecture/` (`docs.7`). It changes nothing the board's views or the mod draw, so `code.8` is not engaged.

## Goals / Non-Goals

**Goals:**

- A card Pending You has resolved, cancelled or expired reads closed to crew once crew has seen it so, and crew sends it nothing more.
- A card resolved by crew's own post that follows it reads closed from that post on, without waiting for a later act to find out.
- The deploy's end, the rail's sweep and the next offer act on the run record's answer: no refused close, no change sent to an ended card, a new card for the next offer.

**Non-Goals:**

- Carrying the deploy's outcome ("Deployed 97e54d5 to mac-studio: machine ok, suite ok.") onto a deploy card its step's card picked up first. The outcome stays in the run record's `ops.deploy` entries. Changing when the step's card is raised, or what it follows, is a design question named in *Risks*.
- Recording a card closed when an agent's own question is followed by its next question through Pending You's own tools. The card hook records the post alone. The question stays listed until its asker ends, and its withdrawal then reads it as ended (decision 4).
- Mending run records already written. mac-studio's card was recorded closed by hand at 20:06:55Z, and any other card a run record still holds open while Pending You has resolved it is read as ended the next time crew changes or closes it.

## Decisions

### 1. Pending You's ended statuses, and the state each is recorded as

`cards.ENDED` becomes `("resolved", "cancelled", "expired")`. `cards.ended(got)` gives the state crew records for an ended card: `"closed"` for `resolved`, since the card was answered and picked up; `"withdrawn"` for `cancelled` or `expired`; `None` for anything else, a reply that is not an object among them. Its truthiness is what `ended` gave before, so the callers' tests read the same. `row_card_change` and `card_closed` take their state from it in place of their own `"closed" if status == "closed"`. `row_card_change`'s new version follows the old card when that state is `"closed"`, as it does now, which Pending You allows for a resolved card.

*Alternative considered:* keep `closed` beside `resolved` in case Pending You ever gives it. Rejected under `read.2`: crew reads the statuses the tool gives, and a status it has never given is a guess written into a decision.

### 2. A post that follows an open card reads that card once the post is made

When `plan.card_posted` posts a card carrying `follows`, and the run record holds that card open under one of the same owner's keys (`cards.followed_open(entries, card, by)`, which gives that key or `None`), crew calls `get_request` on it in the same session, after the post and its upload. If `cards.ended` gives a state, crew records a `card.close` of it on its row's object, under its key, with that state. The outcome is `plan.FOLLOWED`, "picked up in Pending You by the card that follows it", when Pending You reports it `resolved`, and `ENDED_ELSEWHERE` otherwise. crew prints that it was picked up. Anything else leaves it as the record holds it: still `pending` or `answered`, "not found", a refusal, or a session that fails. The event that ends the card then closes it as it always has, or reads it as ended by decision 1.

The read never changes the post's outcome. The post is recorded as made whatever the read gives, and a failure of the read is said on standard error. A post given back as already recorded ("its post recorded already") reads nothing, since the command that recorded it first made the read.

`followed_open` is read from the same entries `card_posted` already takes for `post_key`. When `row_card_change` follows a card it closed itself, those entries already hold that close, so no read is made. In practice the read happens only when a step's card follows a deploy card still open, the case of 2026-10-19.

*Alternative considered:* record the followed card closed at the post without reading it, on the guide's word that a post picks up the answered card it follows. Rejected under `read.1`. The guide says a post picks up an *answered* card, crew does not know at the post whether the deploy card has been answered or is still waiting, and a card recorded closed while it waits would hide the user's question from the rail.

*Alternative considered:* rely on decision 1 alone, so the deploy's end reads the card as resolved and records it then. This gets each outcome right, but the run record holds the card open between the step's post and the deploy's end, which is the stretch the intent names ("from then on"). The rail's sweep asks Pending You about held cards under crew's own name, which Pending You answers for another assistant's card by refusing it, so the sweep never learns of the pickup itself. One read at the moment crew has just caused the pickup is cheaper than any later guess. Decision 1 stays as the guard for the cases a post does not cause: the user's own close in the app, an expiry, a read that failed.

### 3. The deploy's end and the next offer need no change of their own

With the deploy card recorded closed, `card_closed` finds no card under `deploy/<env>` and prints "holds none open on this host, so none is closed". `ops.word_stands` stops mattering for it, since no card is open. `ops.deploy_move` finds no card held and returns "post". `cards.post_key` counts the closed card and posts under the key's next revision. `cards.follows_of("deploy")` follows the environment's last card only when it was declined, else the landing card that left main at the head, as it does for deneb's. So the outcomes the intent names follow from decisions 1 and 2, and `ops.py` is not edited.

### 4. A question's withdrawal reads ended the same way

`plan.question_close` withdraws a question whose asker has ended. It reads the card with `get_request` and then calls `close_call`, so a question its asker followed up, or the user dismissed, is refused just as the deploy card was. It takes the state from `cards.ended` too, records the close with `ENDED_ELSEWHERE`, and calls nothing more. Every close crew makes then reads the status first and sends nothing to an ended card.

### 5. The stub pendingyou behaves as Pending You does here

`tests/stubs/pendingyou`'s `post_request` marks the card named by `follows` `resolved`, with its version moved on, when that card is `answered`. Its `cancel_request` refuses a card already `resolved`, `cancelled` or `expired` with Pending You's words, "This request is already closed." (`tests.4`). No end-to-end test changes: `t-journey-ops` records its deploy's end before its step, so its deploy card is acked before the step follows it. The stub's change is proved by the end-to-end tests staying green (`tests.12`).

## Risks / Trade-offs

- [The user never sees the deploy's outcome on a deploy card its step's card picked up, because the pickup acks it with no outcome.] → Not this change's to fix: it is in the run record. It is named for the design agent below.
- [A read after a post adds one `get_request` to a step's card post when it follows an open deploy card.] → One call, in the session already open, only on that path.
- [The stub's `cancel_request` now refuses an ended card, so an end-to-end test that closed one would fail.] → Every close crew sends is now preceded by a status read that sends nothing to an ended card (decisions 1 and 4). A test failing there shows a close path this change missed, and the coder reads it as such.

For the design agent (`swancloud-design`): the step's card is raised following the deploy's card while the deploy is still running (step recorded at 14:02:04Z, end at 14:02:09Z). Pending You's guide says that when there is something to tell the user about the answered card, the asker should ack it with that outcome first and then post the card that follows. Whether a deploy's card should be closed with its outcome before its first step's card is raised, or the step's card held until the deploy's end, is a decision `plan.14` and the step-card requirement in `rail-cards` don't make.

## Migration Plan

None. The run records already written stay as they are (*Non-Goals*), and crew's main is live on each host once the bolt lands (CLAUDE.md, *This checkout is live*). This change holds no proof list (`docs.6`). Every scenario in its delta is proved in the logic tier, and the stub's behaviour by the end-to-end tier the merge gate runs.

## Task notes

**1.1** In `cards.py`, set `ENDED = ("resolved", "cancelled", "expired")`. Make `ended(got)` give `"closed"`, `"withdrawn"` or `None` as decision 1 says. Keep its docstring's account of 2026-10-19, now naming `resolved` and the post that followed the card. In `plan.py`, take `state` from `cards.ended(got)` in `row_card_change` and `card_closed`. In `tests/py/test_cards.py`, change the case `test_a_card_pending_you_ended_already_is_recorded_closed_and_followed_never_changed_or_closed_again` to `resolved` where it used `closed`. Add a decision case: `ended` gives `"closed"` for `resolved`, `"withdrawn"` for `cancelled` and `expired`, and `None` for `pending`, `snoozed`, `delegated`, `answered`, `closed`, a missing status and a non-object.

**1.2** `cards.followed_open(entries, card, by)`: walk the entries in order, take the `Key` of the newest `card.post` of `card` by `by` that was not refused, and return it unless a later `card.close` of `card` that was not refused follows it; otherwise `None`. A `card.close` naming `card` with no `Key` still closes it. Logic cases: open under `deploy/srv` → `"deploy/srv"`; closed after → `None`; posted by another owner → `None`; a refused close → still the key.

**2.1** In `plan.card_posted`, after `post_request` and `card_uploaded` succeed inside the `with acts.bridge(...)` block, and only when `b["card"].get("follows")` names a card `followed_open` finds open for `owner` in the entries `post_key` was given, call `py.answer("get_request", {"requestId": follows, "name": owner})`. Catch a `Refusal` from that read in place, keeping its words, so it can't reach the `except Refusal` that records the post refused. After the post's own `card.post` entry and print (not on the "its post recorded already" path), when `cards.ended(got)` gives a state, emit `card.close` on `cards.row_object(key) or f"agent/{owner}"` with `Card=follows`, `Key=key`, `State=state`, `Outcome=FOLLOWED if got status is "resolved" else ENDED_ELSEWHERE`, and print `card <key>: <follows> picked up in Pending You by <new card>, which follows it`. On a read that failed, print to standard error `card <key>: whether <follows> was picked up can't be read: <why>`. Add `FOLLOWED` beside `ENDED_ELSEWHERE`. Logic cases in `tests/py/test_card_commands.py` with its `Acts`: a post following an open card that `get_request` reports `resolved` records the post and then that close; one reporting `answered` records the post alone; one whose read is refused records the post alone and says so; a post with no `follows`, or following a card the entries hold closed, calls no `get_request`.

**2.2** In `tests/py/test_cards.py`, the reproducing case runs mac-studio's 2026-10-19 sequence through the acts with `Acts`, its held entries growing with each act's emitted entries:

1. The entries hold `deploy/mac-studio`'s card `req_d1` posted by `swancloud-ops`.
2. `plan.row_card_change(..., cards.step_card, facts with follows="req_d1", ...)` for `op/mac-studio/1` posts `req_s1`, `get_request` reports `resolved`, and `req_d1` is recorded closed with `FOLLOWED`.
3. `plan.row_card_close(..., "deploy/mac-studio", outcome="Deployed 97e54d5 …")` makes no Pending You call and returns `None`.
4. `plan.row_card_change(..., cards.deploy_card, the d35fbf2 facts, ...)` posts a new card whose idempotency key is `deploy/mac-studio:2` and sends no `update_request`.
5. `cards.card_under(entries, "deploy/mac-studio", "swancloud-ops")` gives the new card.

The case is named after the requirement's first three scenarios.

**3.1** In `plan.question_close`, when `cards.ended(got)` gives a state, skip `close_call` and record the close with that state and `ENDED_ELSEWHERE`. Return the state. A logic case beside `test_a_question_whose_asker_herdr_no_longer_lists_is_withdrawn_naming_the_asker` in `tests/py/test_rail.py`, with that file's `Acts`, has `get_request` report `resolved` and asserts that no `cancel_request` is sent and that the close is recorded `closed` with `ENDED_ELSEWHERE`.

**4.1** In `tests/stubs/pendingyou`, `post_request` with `follows` naming a card in `cards.json` whose status is `answered` sets that card `resolved` and moves its version on, before it answers the post. `cancel_request` of a card whose status is `resolved`, `cancelled` or `expired` returns `refused("This request is already closed.")`. Nothing else in the stub changes.

**4.2** Run `tests/suite logic` while iterating. Once the change is done, run `tests/suite --affected` once. The stub is in every end-to-end task's inputs, so this runs them all. Both must end "0 failed". No test file is added or removed, so `tests/moon.yml` is unchanged.

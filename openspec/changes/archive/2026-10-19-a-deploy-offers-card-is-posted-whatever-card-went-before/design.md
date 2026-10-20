# Design

## Context

See proposal.md, *Why*. What crew does now, read on crew's main at 91e3a6a6:

- `cards.follows_of("deploy", {env, head}, entries)` returns the environment's last deploy card when the user declined it. Otherwise it returns the last landing card of the bolt whose `bolt.land` left main at the deployed head. That card is raised in the bolt's conductor's name (record 0031), and `ops.raise_deploy` posts the deploy card in `<label>-ops`'s name. Pending You refuses that post. `follows_of` for a landing and a step reads the same entries and never checks whose a card is.
- `plan.row_card_post` already records a refused post as `card.post` with `Refused:` holding Pending You's words, under the row's key, on the row's object. The run record shows it (below). `plan.rail_text` already prints, under a row with no card open, "none open; its last post was refused: <words>" (`last_refusal`).
- `board.marker` gives a row's marker `card: None` when no card is open, and `card_of` prints that as "no card open"; `page.html` prints "no card". Neither the board's text, nor the agents' views (main-level ops's deploy rows among them), nor the page says a post was refused.
- `ops.offer` returns at once when the commit offered is the open offer's and the files it was handed have not changed (`handed_changed` empty), so it never reaches `raise_deploy`. Only the rail's sweep posts a refused card again, once `CARD_RETRY` (600 s) has passed (`plan.sweep_judged`).

The case, read from `runs/mac-studio/2026-10-19.rec` and `2026-10-20.rec` on `swancloud/main` of afterthought/crew-state (crew's cache `refs/crew/swancloud/main` at 2026-10-20 01:59Z):

- 21:50:41Z `card.post`, By `swc-2-conductor`, Key `land/the-box-works-in-wldn-prod`, Card `req_5de89eb68b7c495fbb36`; closed `closed` at 23:57:19Z.
- 23:36:27Z `bolt.land`, On `bolt/the-box-works-in-wldn-prod`, Head `ddcf2cb4e5ad15281a11fe1e636d17dfed9c66b9`, Repo `swancloud`.
- 23:54:39Z to 00:00:17Z `ops.offer` by `swancloud-deployer` of `ddcf2cb…` to swancloud-srv, deneb, chuck-herdr-alpha, mac-studio and macbook-pro (Base `d46500a…`, chuck-herdr-alpha's `40f379c…`).
- From 23:54:45Z, every `card.post` by `swancloud-ops` under those `deploy/<env>` keys is `Refused: Pending You refused post_request: This is swc-2-conductor’s card; leave it. You’re “swancloud-ops”: act only on the cards you posted.` These are the offers' own posts and the sweep's at 00:05, 00:10, 00:16 and 00:20.
- 00:16:03Z `ops.offer` of swancloud-srv at `f358fdf…`, which no landing left main at; its post at 00:16:18Z went through as `req_bcd8896b56eb4d379d3f`.

Pending You: `post_request`'s schema takes `follows` as any `req_…` id and says nothing of whose card it may be. Its refusal above is the reading: a card follows only a card its asker posted. The refusals stop exactly where the followed card is another agent's, and srv's card, which followed nothing, went through.

Rules this rests on: `briefs.11` (crew raises each row's card in the name of the role whose row it is; its details, read 2026-10-20, name this fix: a card's `follows` held to a card in its own name, the environment's last deploy card or none, and a refused post said on the rail), `briefs.13` (the deploy's form, which already names the landings it carries), `briefs.16` (each act recorded from Pending You's own reply), `plan.14` (a deploy's row and card are main-level ops's), `read.1`, `read.2` (a missing value never becomes text), `code.7` (each decision a function of facts), `code.8` (what the board models reaches the agents' views and the mod), `state.4`, `docs.2` (README with the command's behaviour), `tests.4` (the reproducing case in the logic tier). Pages whose areas this touches: `plan.md` (`plan.py`), `tests.md` (`tests/`), `docs.md` (README, the specs).

Departure: record 0031 §5 says "a deploy follows its landing". Pending You refuses that whenever the landing card is a conductor's, which since record 0031 it always is. This change has a deploy card follow no landing card, as `briefs.11`'s details of 2026-10-20 already say it must. The record's line is the design agent's to amend (`docs.7`), and this change does not edit it.

## Goals / Non-Goals

**Goals:** a deploy card that Pending You takes whichever card went before; a refused post that the board, the views and the page show as owed; an offer again that posts what was refused.

**Non-Goals:**
- Telling main-level ops, or anyone, when a post is refused. The rail, the board and the views say it; the intent asks for no tell.
- Any change to the sweep's retry interval, to `post_key`'s keys, or to the deploy card's face. The keys are already `deploy/<env>` and its revisions, which only main-level ops posts under.
- `crew rail`'s card line, which already prints the refusal's words.

## Decisions

**1. `follows_of` takes the owner and counts only the owner's posts.** `follows_of(kind, thing, entries, by)` keeps, of `posted_cards(entries)`, only the cards whose `card.post` names `By == by`. `posted_cards` gains `by` on each card for this. The kinds then read:
- `deploy`: its environment's last deploy card when that card's state is `declined`, else None. The branch that looked up the landing card of the bolt landed at the head goes.
- `step` and `land`: as now, over the owner's cards only.

Callers pass the owner they post as: `ops.raise_deploy` and `ops.raise_step` `f"{label}-ops"`, `plan`'s two landing calls the conductor they post as. *Considered:* drop only the deploy's landing branch and leave the others unguarded. A bolt held by another team, or a step whose deploy card a person posted, would hit the same refusal. One guard where the follow is chosen covers every kind.

**2. An offer of the same commit posts a card main-level ops does not hold.** A new decision, `ops.offer_move(offers, env, to, changed, held)`, returns:
- `"offer"` when `to` is not the open offer's head; the offer is recorded and its card raised, as now.
- `"change"` when it is and the files changed.
- `"post"` when it is, nothing changed, and `held` (whether `cards.card_under(acts.entries(label), "deploy/<env>", f"{label}-ops")` names a card) is false.
- None when it is, nothing changed and a card is held.

`offer` keeps the files as now for `offer` and `change`, records `ops.offer` only for `offer`, and calls `raise_deploy` for `offer`, `change` and `post`. For `post`, `raise_deploy`'s own `deploy_move` already answers `"post"` when no card is held, so the card goes out with its facts built afresh, and the line that adopts it is told as on a first post. An approved deploy's card is left alone, as `deploy_move` already leaves it.

**3. A marker carries the refusal of its row's last post.** `board.marker(r, cards, label, logs)` adds `refused`: `plan.last_refusal(logs, r["key"])` when no card is open, else None, where `logs` is the rail read's `read["logs"][label]`, the same entries `rail_text` reads. `markers` and `keyed` pass it on, and the board's data hands them `read["logs"]`. `card_of` prints "no card open, its post refused" for such a marker, and "no card open" otherwise. Every view that draws markers, main-level ops's deploy and step rows among them, takes it through `row()`. `page.html`'s marker prints "no card, its post refused" with the words in the marker's title, after its key. The mod draws the views' segments as it is handed them, so `status.js` is unchanged. `tests/py/test_board.py`'s case pinning every key the mod reads still holds, since the mod reads no marker's fields.

## Risks / Trade-offs

- [A deploy card no longer threads under its landing card on the phone] → its face already lists the landings it carries, with each bolt; Pending You allows no other thread across owners.
- [A refusal of another kind, a rate limit or a sign-in, also reads "its post refused" on the board] → that is what happened, and the page and `crew rail` carry Pending You's words to tell them apart.
- [An offer repeated by a deployer that loops posts again each time while Pending You keeps refusing] → each attempt is one refused `card.post`, as the sweep's are now, and the deployer offers on its own schedule, not in a loop.

## Task notes

**1.1** In `cards.py`: `posted_cards` carries `by` from each post's `By`, and `follows_of` gains `by` as Decision 1 has it. Update its docstring, and the module's opening paragraph, which says each card follows "the card its thing follows". In `tests/py/test_cards.py`:
- Rewrite `TestDeploy.test_a_card_follows_the_card_its_thing_follows` so a deploy at a head a landing card put on main follows None.
- Give `TestFollows.E`'s posts their `By`, and pass the owner in each case.
- Add a case where the step's deploy card is another owner's and the step follows None, and a case where a landing raised by another conductor follows None.
- At the mac-studio sequence near line 1298, the `follows` asserted as `req_l48` becomes None, and the post's `follows` key is absent.

**1.2** The record's case, in `tests/py/test_cards.py` beside `TestFollows`, built from the entries in *Context*:
- swc-2-conductor's landing post and close of `req_5de89eb68b7c495fbb36`, the `bolt.land` at `ddcf2cb4e5ad15281a11fe1e636d17dfed9c66b9`, and swancloud-ops's earlier `deploy/deneb` posts closed `closed`.
- `follows_of("deploy", {"env": "deneb", "head": "ddcf2cb4e5ad15281a11fe1e636d17dfed9c66b9"}, entries, "swancloud-ops")` is None, as it is for the five environments.
- `plan.row_card_post` with the acts' stand-in, its `post_request` answering the refusal text verbatim, records one `card.post` on `env/deneb` under `deploy/deneb`, By `swancloud-ops`, its `Refused` holding Pending You's words, and returns None.
- With the stand-in answering a card, the post sends no `follows`.

**2.1** `ops.offer_move` as Decision 2, and `offer` acting on it. Cases in `tests/py/test_ops.py` `TestOfferedAgain`, one for each of the four answers. A case for `offer` itself, with `raise_deploy` and `emit` stood in (monkeypatched), shows that the same commit with the same files and no held card raises the card once and emits no `ops.offer`. Update `ops.py`'s usage header for `crew ops offer` to say it.

**3.1** `board.marker` and `card_of` as Decision 3, with `markers`, `keyed` and `environments` handed the label's logs from the read. Cases in `tests/py/test_board.py`:
- An Operation line and wldn-ops's view for a deploy offer whose only post was refused end "no card open, its post refused".
- The JSON's marker carries `refused` with the words.
- A row with no post at all still ends "no card open".

**3.2** `page.html`'s marker words and title, as Decision 3. A case in `tests/py/test_page.py` shows the page as written carries the words, as its other cases read the page's text.

**4.1** README (`docs.2`):
- *Operations*: "The same offer again writes nothing, unless …" becomes "writes nothing, and posts the deploy's card again when main-level ops holds none open, as when Pending You refused it; handed other notes or steps, it changes its card in place".
- The board paragraph: "each saying at the line's end whether its card is open and who asked it" gains "or that its post was refused".
- Where README says what the deploy card follows, it follows its environment's declined deploy card and no landing card.

`tests/t-docs.sh` stays green.

**5.1** Run `tests/suite logic`, then `tests/suite --affected`, from the worktree's root; both end "0 failed".

# Design

## Context

See proposal.md, *Why*. Here is what the bolt holds today, after `every-reading-cards-session-is-tried-every-time` and `a-landing-card-is-raised-with-its-session-every-time`:

- **What the sweep tries.** `sweep_judged` puts a held card into `out["unread"]` only when its key matches `(batch|proposal)/\d+` and `reading_unread(entries, key, card, now)` holds. `sweep_cards` then asks Pending You whether each such card still waits on the user (`card_waiting`) and calls `acts.reading_again(l, key)`. It lists the card `opened` with the link, or `left` with why. `tests/py/test_rail.py`'s `test_a_batchs_or_a_proposals_card_standing_without_its_reading_ten_minutes_is_tried_and_no_other_card` pins that a `land/y` card is not tried.
- **How a retry is tried.** `SweepActs.reading_again` calls `reading_again(fleet, label, key, acts)`. That reads a batch's or a proposal's facts (`reading_facts`), opens the reading, records `card.reading` in the planner's name, and relinks the card (`relink`). The relink happens when the session started anew or `reading_unread` shows the card standing without its reading. It handles no `land/` key.
- **How a landing's reading is started by hand.** `land_session` checks the bolt, its team and the host (`session_refusal`), reads `land_facts`, opens the reading through `acts.reading`, and prints the link. It relinks only when `started`. It records nothing in the run record. `land_start`, the landing's wait, calls it.
- **What the ten minutes count from.** `reading_unread` already reads a landing card's `card.post` and `card.update` with `Unread`, since those keys carry `Card`. It also already reads refused `card.reading` entries by `Key`. Because a landing's try records nothing, a failed sweep try would leave the clock at the card's post, and every later read would try again at the rail tab's pace.
- **What the card says.** `unopened` gives a landing card "the bolt's conductor starts it with crew card session land/<bolt>, and this card then carries its link". It does not say the rail tries again, which a batch's and a proposal's card do say.

Rules this rests on:

- `briefs.9`: every reading card carries its session's link, a landing's included.
- `briefs.13`: no command on a card for the user to run.
- `read.1`: why a try failed is named and kept.
- `record.1` and `record.3`: one entry per act, done or refused, in crew's own words; a pure read appends nothing.
- `code.7`: the sweep's judgment stays a function of facts. `code.9`: a rail read stays within an agent's shell's time.
- `docs.2`: README, the skill and the usage change together.

Pages whose areas this touches: `plan.md` (`plan.py`), `briefs.md` (`conductor.md`, the crew skill), `teams.md` (`plugin/bin/crew`'s usage), `tests.md`, `docs.md`. `code.8` is not engaged: no stage, object or field `board.agent_views` reads changes, and `card.reading` already exists as an act no view draws.

## Goals / Non-Goals

**Goals:**
- The rail's sweep tries a landing card's missing reading on the same terms as a batch's and a proposal's, and changes the card to carry the link.
- Every later try of a landing's reading is recorded, so the ten minutes count from it and its reason is kept.

**Non-Goals:**
- How a landing card is raised, its two tries and its wait's choice (`land_unstarted`), all unchanged.
- A landing card on a host the rail is not read on. The sweep reaches only the cards posted on its own host, as it does for every other card. A landing card is posted on its team's host.
- A landing card the user has answered. It is left as it is, as the batch's and the proposal's are.

## Decisions

**1. `land_session` records each try, as `reading_again` does.** The try is everything from reading the landing (`land_facts`) onward. The argument checks before it (no such bolt, no team, wrong host) are not tries, and they record nothing. `card` is the card the conductor holds under the key (`cards.card_under`), read before the try.

- **A `Refusal` from `land_facts`' unproven reason or from `acts.reading`:** append `card.reading` on `cards.row_object(key)` (`bolt/<bolt>`), by `<team>-conductor`, with `refused=` crew's message, `Key=key` and `Card=card` when one is held. Then raise it again.
- **Started anew:** append it done, with the same fields.
- **Given again:** append nothing (`record.1`).

The refusal for a bolt that does not read proven keeps its words. It is now raised from inside the recorded part, so the record keeps it too.

`land_start` goes through `land_session`, so the landing's wait records its tries with no change of its own.

**2. `land_session` relinks a card standing without its reading.** `relink`'s `due` becomes `started or reading_unread(acts.entries(label), key, card)`, as `reading_again` has it. Here `card` is the card held, and `now` is left out, so it answers only whether the card stands without its reading. A session given again on a card that carries its link changes nothing.

*Considered:* relinking only on a start anew, as now. A sweep try whose session started but whose card change was refused (Pending You down, say) would leave the session running with the card never carrying its link: every later try would give the link again and change nothing. That gap is why `reading_again` already has the second condition.

**3. `land_session` takes `say`.** It gains `say=None`, called as `say(url, decided)` in place of its two prints when given. With none given it prints as now, so `crew card session land/<bolt>`'s output is unchanged. It returns `(url, decided, started)`, as `reading_again` does. The sweep passes a `say` that prints nothing, since the rail lists the link itself (`opened`, "its reading opened at <link>").

**4. The sweep sends a landing key the landing's way.** `SweepActs.reading_again(label, key)` calls `land_session(self.fleet, label, key, self, say=lambda *_: None)` for a `land/` key and `reading_again` as now for the rest. The sweep's loop over `unread` is unchanged: it already reads the card in its owner's name (`c["by"]`, the conductor), checks `card_waiting`, and lists `opened` or `left`.

`land_session`'s own checks hold on the sweep's path. The sweep runs on the host the card was posted on, which for a landing card is its team's host (`raise_land` refuses elsewhere), so `session_refusal` passes. A bolt that no longer reads proven has no rail row, so its card is among the gone, not the held.

**5. `sweep_judged` takes landing keys.** The pattern becomes `(batch|proposal)/\d+|land/[a-z0-9][a-z0-9-]*`. Nothing else in `sweep_judged` changes: `reading_unread` already reads a landing card's entries, and with Decision 1 its refused tries. A landing card whose bolt is `blind` is never held here, since its host is this host. The docstring and `out["unread"]`'s description name the landing.

**6. The landing card's words.** `unopened` for a `land/` key says: "Its reading could not be opened on the tailnet: crew tries it again when the rail is read, and the bolt's conductor starts it with crew card session land/<bolt>; this card then carries its link." This mirrors the batch's sentence. The details still open with why, and the summary is cut to Pending You's budget as now. `card_built`'s printed line already names `crew card session <key>` and is unchanged.

**7. Briefs and docs.**

- **The conductor's brief:** in the landing card paragraph, the sentence on a card raised without its reading adds that crew's rail read tries it again too.
- **README:** the card-session paragraph's sentence "Each rail read tries the reading of each such card" names the landing card, and says a landing's is tried as `crew card session land/<bolt>` does on the team's host. The list of acts says `card.reading` is a try of a batch's, a long proposal's or a landing's reading.
- **The crew skill:** the rows for `crew rail` and `crew card session` say the same.
- **The usage:** `crew rail`'s entry in `plugin/bin/crew` and in `plan.py`'s usage text says the same.

## Risks / Trade-offs

- [A rail read on a team's host now may start plannotator for a landing card, up to `CARD_START`] → One try per card per ten minutes, only for a card the record shows without its reading. The batch and proposal tries already cost the same.
- [The landing's try reads the bolt's kit (`land_facts`) inside the rail read] → Only when a landing card is due a try, which should be rare. The raise reads the same.
- [A relink from the sweep asks for the bolt's preview again (`landing_preview`)] → It asks for the same head, which keeps the preview crew recorded. This is what `crew card session land/<bolt>` already does.
- [A crew on another host that does not know a landing's `card.reading`] → It reads it as an act it does not use. Every host takes crew's main in the same step.

## After deploy

Nothing. The logic tier proves every scenario. No check in crew's tiers reaches a real plannotator on a loaded host, and the batch's change already named watching for its first real `card.reading` entry. A landing's entry takes the same path.

## Task notes

**1.1** `land_session`, Decisions 1–3, in `plan.py`.

- Read `card = cards.card_under(acts.entries(label), key, owner)` once, before the try, and use it for both the entry and the relink. `relink` reads it again itself: that is fine, and it keeps its own signature.
- Move `owner` above the try.
- Wrap from `land_facts` to `acts.reading` in one `try`. The unproven `fail(...)` stays inside it.
- `say` defaults to the two prints now there.
- Return `(url, decided, started)`. `card_session`'s `return land_session(...)` then returns a tuple, which nothing reads. Check that `card_session`'s callers ignore its return value.

**1.2** Cases in `tests/py/test_cards.py`'s `TestLandingSession`, through its `run` and the stand-in acts. Check that the stand-in's `emit` records entries, and add a list for them if it does not.

- A start anew appends one done `card.reading` with `Key="land/b1"`, `Card="req_l1"` and `By="swb-1-conductor"`.
- A session given again appends nothing.
- A refusal from the reading appends one refused entry with the message and re-raises.
- The unproven refusal appends one refused entry.
- The wrong-host refusal (`team` on another machine) appends nothing.
- A session given again (`started=False`) on a card whose post holds `Unread` is changed with `RELINKED` while it waits.
- The same on a card whose post has no `Unread` is not changed (the existing `(False, {"status": "pending"}, False)` case).
- `say` given: nothing printed to standard output.

**2.1** `SweepActs.reading_again`, Decision 4. Its docstring names both paths.

**2.2** `sweep_judged`'s pattern and docstring, Decision 5. In `tests/py/test_rail.py`, rename and rewrite `test_a_batchs_or_a_proposals_card_standing_without_its_reading_ten_minutes_is_tried_and_no_other_card` so `land/y` is among the cards tried. Keep a card of another kind (a deploy's or a record's, whichever the file builds) as the one not tried. Keep the five-minute and other-host assertions.

**2.3** In `TestSweep`, beside `test_a_waiting_batch_card_posted_without_its_reading_long_ago_is_tried_and_listed_opened`, add three cases through the stand-in `Acts` (whose `reading_again` already takes any key):

- a waiting `land/y` card, posted by `swb-1-conductor` with `Unread` long ago, is tried and listed `opened` with its link;
- one whose try refuses is listed `left` with why;
- an answered one is not tried.

**3.1** `unopened`'s landing words, Decision 6. Update `test_a_landing_whose_reading_could_not_open_is_raised_all_the_same_an_approval_as_before`'s expected summary. Check that the summary still fits the budget there, as the batch's case checks it.

**4.1** `conductor.md`, Decision 7. Update `tests/t-briefs.sh`'s want at its line on "a card raised without its reading says so and why, and names" if the checked words move, and add a want for the rail's try.

**4.2** README, the crew skill, `plugin/bin/crew`'s usage and `plan.py`'s, Decision 7, together. `tests/t-docs.sh` stays green.

**5.1** Run `tests/suite logic`, then `tests/suite t-briefs t-docs` by name, then `tests/suite --affected` once at the end. No test's reads change, so `tests/moon.yml` stays as it is. If `tests/suite` says otherwise, run `tests/moon-tasks` and add `tests/moon.yml` to the touches.

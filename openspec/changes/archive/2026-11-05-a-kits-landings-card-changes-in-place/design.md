# Design: a kit's landings card changes in place, and is not raised again for a forecast that flips

## Context

The proposal gives the box's timeline. Rules this change relies on: `plan.8`, which says no landing card is raised and no row is marked able to land while it conflicts; `plan.16`, which has the landings card be the word to land; `roles.5`, which keeps Pending You's mechanisms in Pending You; `read.1`, which says what crew can't read is said and never guessed; and `code.7`, which makes a decision a function of facts. Record 0031 §3 says one card per thing, changed in place. Its amendment of 2026-10-24 says a landing's approval stands through taking main in. The change touches `plan.md`'s area (`plugin/lib/plan.py`, `plugin/lib/cards.py`). It departs from no rule.

What crew reads of Pending You was checked against `pendingyou mcp`'s own tool schemas on mac-studio (pendingyou 0.39.0, `tools/list`, read on 2026-11-06, nothing posted):

- `update_request` takes `options`, `multi`, `approve`, `recommendedIds`, `addQuestion` and `withdrawQuestion`, but no `kind`. So a card stays the kind it was posted as.
- `options`, on a post and on an update alike, holds two items at least and five at most. So a list of one box cannot be posted, and an approval of one row cannot become a list of two in place.

So crew cannot keep one card through a change from one row to two, or from two to one. The box's six re-posts were all such changes, each a bolt taking main in and coming back. The fix keeps the count steady through taking main in.

## Decisions

### Decision 1: a row taking main first is a row of the card while one can land

`card_rows(rows)` is a pure decision. From the rows `landing_rows` gives, after `rows_unsent`, it returns every row that can land and every row held only to take main first (`takes_main`: forecast to conflict with main at its head, or with only take-main fixes in flight), in the plan's order, while at least one row can land. It returns none otherwise, since no card is raised while none can land (`plan.8`). A row held for any other fix, or for sluice's refusal at its head, stays held with no box, as before. A row taking main first that an earlier send still lands is marked `sent` by `rows_unsent` and stays held with no box, since that send lands it once it reads proven, and showing it again would ask for it twice.

On the card such a row is a box left unticked. Its detail says why it takes main first, in `landing_rows`' words. Its consequence says that, ticked, it lands once its team has taken main in and sluice has proven it, the user's send standing through it. It is never among `recommendedIds`. So it is not marked able to land while it conflicts (`plan.8`), the same reading that lets a bolt the user left keep a box while it would conflict (rail-cards "A row the user left says whether it would take main first"). Its paragraph on the card's face is tagged *takes main first*, and its forecast sentence gives way to `taking_said`. A one-row card can't hold such a row, because `card_rows` returns one only beside a row that can land, so the hold-to-approve card is unchanged.

Considered: keeping the card's form sticky, so a list stays a list once posted. That would need a one-box list, which Pending You refuses, or a phantom second option ("leave every bolt waiting"), which would ask the user something that isn't a decision. Also considered: having every landings card be a list. That breaks on the same two-option minimum. Also considered: asking Pending You for `update_request` to change a card's kind. That is the most direct fix, but it is Pending You's to make (`roles.5`). It would still post the bolt's row as a box while it can't land and take it off while it takes main in, so the user would see the row come and go on one card instead of on six. This design holds the row in place, which is what record 0031's amendment of 2026-10-24 says of an approval through taking main in.

### Decision 2: the card's form and its change note read every row it shows

`landings_step`'s branch for a waiting card compares what the card showed with `card_rows` now, never with the rows that can land alone. `cards.landings_form` gets the count of shown rows, so a row taking main first or coming back from it keeps the form, and the step is a change in place. The change note says what moved:

- "`z` takes main first: …", in `landing_rows`' words, when a shown row comes to take main first;
- "`z` can land again", when it comes back, after "`z`'s head is now …" when its head moved;
- "`z` joins the card and takes main first: …", when a bolt not on the card joins it that way.

A row that stays taking main first, its words alone changing (a forecast's conflict becoming the take-main fix it started), changes nothing, as a held row's words changed nothing before. The card follows only when the shown count crosses a form, which is now only a bolt joining a card of one or leaving a card of two for good.

### Decision 3: the card marks such a row, and crew's unticking is not the user's leaving

`landings_card` records a row taking main first in its `Heads` as `<bolt>@<head>:main`, beside `:left`. `card_heads` reads `:main` and returns it as not left, and `heads_taking` gives the set. `kit_card_state` hands it to `landings_step` and `left_now` as the card's `taking`. On an answered card:

- An unticked row the card showed taking main first is not counted among the bolts the user cleared. So it is not in the close's "Left:", not in `landing.left`, and not in the close's `Answer`, and its conductor is still told the take-main fix.
- Once it can land, it is read as proven since the send (`anew`). The card that follows asks for it, ticked as crew proposes.
- A tick on it is a send that stands while it takes main in. `landings_step` already holds a ticked bolt taking main first in `landing` while `send_stands`, and leaves the card.

### Decision 4: the read judges a ticked bolt's take-main at its head now

`main_firsts` used to leave out of `crew card read`'s submit every ticked bolt with a conflict recorded at the head the card showed. A bolt whose take-main fix had since moved it, its work unchanged, was then left out for as long as the answered card stayed open, which made rail-cards "A send stands for a ticked bolt taking main in" unreachable through the read. That was true before this change for a bolt ticked and then forecast to conflict, and a tick on a row taking main first now reaches it too. `main_firsts` now reads each such bolt where it lives with one `acts.work`, the read `landings_earlier` already makes. It keeps a bolt out only while it still stands at that head, or while the record holds a conflict at its head now. A bolt whose head crew can't read stays out (`read.1`). The read costs nothing when no ticked bolt has a recorded conflict.

## Risks

- A row taking main first now sits on the card as an unticked box, so a user could tick it expecting it to land at once. Its detail and consequence say it takes main first and that a tick lands it only after its team has taken main in and sluice has proven it. Ops leaves it out of the submit meanwhile (main-ops.md, step 1).
- The first raise of a card posted before this change, with a row taking main first beside one that can land, finds that row joining. That may cross a form once and follow the card. It happens once for each such card.

## After deploy

None. Each behaviour is code proven in crew's tiers. wldn's box gets it when swancloud moves its crew pin.

## Task notes

**1.1** `plan.card_rows`, pure. `tests/py/test_landings.py` `test_a_row_taking_main_first_beside_one_that_can_land_is_a_row_of_the_card`.

**1.2** `landings_step`'s waiting branch reads `card_rows`, compares taking main first against the card's `taking`, and counts the shown rows for the form. The answered branch leaves the card's `taking` out of `cleared` and reads one that can land now as `anew`. `left_now` skips the card's `taking`. `rows_unsent` marks a taking row an earlier send lands `sent`. Cases: `test_a_row_coming_to_take_main_first_and_back_changes_the_card_in_place` and `test_a_row_shown_taking_main_first_and_left_unticked_is_no_bolt_the_user_left`. The helpers `waiting` and `answered` carry `taking`.

**1.3** `card_heads` reads `:main`, `heads_taking` gives the set, `kit_card_state` returns `taking`, and `landings_raised` builds the card's rows from `card_rows`, with `taking` set to the row's words. Its follow and close paths build the next card from those rows, less those the send lands. `offered` leaves the card's `taking` out. Cases: the raise's "One of two", "One of three", "A wait found it first" and "cannot be told", updated, and the wldn reproduction `test_a_forecast_that_flips_between_raises_holds_the_card_to_one_request_changed_in_place`.

**1.4** `cards.landings_card`: `:main` in the heads, the row's detail, consequence, paragraph and background, the summary's sentence, and no recommendation. `taking_said` and `row_said`. `tests/py/test_cards.py` `test_a_row_taking_main_first_is_an_unticked_box_saying_why_and_what_a_tick_does`.

**1.5** `main_firsts(…, kit, acts)` and `card_read` passing the kit. `tests/py/test_card_commands.py` `ReadSent` stubs `bolt_work`, and `test_a_ticked_bolt_whose_take_main_fix_moved_it_since_its_conflict_lands_on_the_send` covers it.

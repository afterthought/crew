# Design

## Context

This section records what was read on 2026-11-06, so the decisions below rest on it.

**Pending You's bounds.** Three sources were read: the fleet's `pendingyou` 0.41.0 bridge (`tools/list`, which posts nothing), the guide at `https://www.pendingyou.com/skill.md` (revision 2.60), and the refusal deneb met.
- `post_request`'s schema bounds a title at 140 characters, a summary at 400, and an option's or a question's label, detail, consequence and rationale at 80 and 200. A card's `about.title` is bounded at 120, and options at 5 a question. These are the budgets crew already keeps.
- `update_request` bounds its `changeNote` at 120.
- The schema bounds none of the action's fields: `where`, `done`, a step's `text` or its `command`. The guide gives no number for them either.
- Pending You's server refuses a step's words of 300 characters or more, in the words "Keep each step’s words under 300 characters." Those words are the only statement of that bound.

**The step deneb could not card.** swancloud's `the-fleets-pendingyou-is-0-41-0`, *After deploy*, step 1: "Sign Herdr in to Pending You again on this host, … Decline it on a host whose Herdr was never signed in." Its first sentence is 275 characters. Its words carry inline code marks and no `- command:` field. Its why is one sentence.

**Where crew builds a card's bounded fields** (`grep -n '"steps"' plugin/lib/*.py`, and every `cut` and `by_words` in `cards.py`):
- Action steps are built only by `step_card`: a gate's one step (its link), a user's commands, and a user's words.
- Options, labels, details, consequences and rationales are each held to `LABEL` or `DETAIL` already, in the landings, proposal, record and held-step cards.
- An `about.title` was cut to a bare 120 twice, and a change note to a bare 120 in `cards.change_args` and in `plan.row_card_change`.
- `page.py`'s `steps` are the page's, not a card's.

**The family.** No other tool of the Boomdrive family builds a Pending You card: Flume shows a stop-short through its caller (flume's requirements, "whoever shows the card"), and sluice, timber, weir and boom post none. crew is the one owner of its cards' budgets, so the fix is crew's alone. The step's words are swancloud's, written by its deployer from the change's *After deploy*. crew shows a kit's words as written (rail-cards "A card's words are the document's own"), so it asks no kit to keep a step short.

**Area pages this change touches:** `core.md` (`roles.5`, `read.1`, `code.7`, `code.8`), `tests.md` (`tests.4`, `tests.11`, `tests.12`) and `docs.md` (the spec). No rule changes, so no page is edited (`docs.7`).

## Goals / Non-Goals

**Goals:**

- A user's step of any length gets its card, and its words reach the user whole, never cut.
- Every action step crew builds holds to Pending You's budget for a step, and a command is never cut.
- Every budget crew holds a card to is in one table in `cards.py`.

**Non-Goals:**

- Bounds Pending You neither states nor refuses on: `where`, `done` and a command's length. crew keeps no guessed budget for them (`read.1`).
- Asking swancloud's deployer to write shorter steps.
- Retrying a refused card differently. The rail's sweep already posts a refused card again after `CARD_RETRY` (rail-cards "A row's card that Pending You refused is owed until it posts").

## Decisions

### 1. The long words ride the card's face whole, and the step is a short to-do

A user's step whose words do not fit a step keeps one action step. That step holds its first whole sentences that fit (`prose(words, STEP)`), or its first sentence cut at whole words, ending with "…". The card's face then carries the words whole, as inline Markdown titled "The step".

The other path was to split the words at sentence boundaries into several action steps, each within the bound. Not taken, for three reasons:
- A step that is one row on the rail would become several steps on the card. Pending You's progress then counts ticks and a failed step by numbers crew's model of the step does not have. "said step 2 did not work" would name half a sentence.
- Pending You's guide asks one action per step, each one click or one paste. Sentences are not actions: in deneb's step the second sentence is what the user sees once it worked, and the third is when to decline.
- A sentence longer than the bound would still be cut, so splitting alone cannot keep the words whole.

The face is where crew already puts a document's substance (rail-cards "A card's document is inline Markdown"). Markdown keeps the step's code marks, which the step's plain text and the summary drop. And it has no bound Pending You states.

### 2. The face appears only when nothing else holds the words whole

The words are whole on the card when any one of these holds them:
- the title, cut at whole words to the title's budget, cut nothing;
- the one action step is the words themselves;
- the summary is the words, and `prose` cut nothing of them.

Only when none does is the face added. So every card that showed its words whole before is unchanged, a short step with commands and a why among them, and a long step with no why shows them once, in its summary. deneb's step has a why, so its summary is the why, and its words are on the face.

### 3. One function builds every action step: `cards.step`

`step(words, command=None, short=None)` is the one place an action step is made. Its text is the words when they fit `STEP`, else `short`. Its command, when it has one, is carried whole: a command cut short does not run, and the guide asks for one whole command.
- A user's commands keep the command as their words when it fits, as before, and "Run this command." when it does not.
- A gate's one step is its link when that fits, else "Open the gate at this card's link and approve the deploy there." The card's *where* stays the link, which Pending You shows as a button.
- A user's words use `prose(words, STEP)` as the short words.

### 4. One budget table

The table beside `TITLE, SUMMARY, DETAIL, LABEL` and `OUTCOME` gains:
- `STEP = 299`: "under 300", read from Pending You's refusal;
- `ABOUT = 120`: a card's about title;
- `NOTE = 120`: `update_request`'s change note.

Every cut to a Pending You bound in `cards.py` and `plan.py` names one of them. `STEP` is the one budget no schema states. Its comment cites the refusal and the day it was read, so a later reader knows where it came from.

### 5. A title cut at whole words, and a held step's question kept

A user's step's title is "After <env>'s deploy: " and its words cut at whole words to `TITLE`, in place of `built`'s cut at any character.

A held step's title had its question, ", now or when the host is quiet?", appended after its words, and `built`'s cut then dropped the question from any title over 140. Now the words are cut first, to the room the head and the question leave, so the question always ends the title. When the title cut the words, the face carries them whole, as in Decision 2.

### 6. A change empties a face the card no longer carries

`update_request` keeps every field a change leaves out. So a step recorded again with short words would keep its old face, which shows the old words. `change_args` now always sends `artifacts`, empty when the card carries none. For a card that never had artifacts this changes nothing. For any card crew builds again, the face is what the builder says it is now.

### 7. A card still refused is seen on the rail

A post Pending You refuses for a bound crew does not know yet is recorded as a `card.post` refused in Pending You's words. The row stays on the rail, owing its card, with those words on its card line (`plan.last_refusal`, rail-cards "A row's card that Pending You refused is owed until it posts"). That already holds. This change adds a test that pins it for a step's card refused with deneb's words.

### Rules relied on

- `roles.5`: crew wraps Pending You and builds nothing of its own beside it. The budget is Pending You's, read and kept, not a bound of crew's.
- `read.1`: crew keeps no guessed budget for a field Pending You states none for and refuses none on.
- `code.7`: `step` and `step_card` are decisions on plain facts, tested in the logic tier.
- `code.8`: no bolt, unit, stage, card key or rail row changes shape, so the views and the mod are untouched.
- `tests.4`: the stub Pending You refuses a step of 300 characters or more in Pending You's words, as the server does.
- `tests.11`, `tests.12`: the cases are in the logic tier, on a fake that refuses as Pending You does.

### Departures

None.

## Risks / Trade-offs

- **[Pending You's step bound changes]** → `STEP` is read from a refusal, not a schema. A tighter bound is refused again, recorded in its words and shown on the rail, and the table's one number changes.
- **[The step's first sentences are not an action]** → The step names what to do only as far as the kit's first sentences do. The whole words are on the face beside it.
- **[A face sent empty on every change]** → `update_request` takes an empty array, as its schema allows. A card that never had a face is unchanged by it.

## Migration Plan

None. `op/deneb/20` stays owed on deneb's rail. The rail's sweep posts it again once crew at this change runs there, with nothing done by hand.

## After deploy

None: every outcome here is a logic-tier case, and nothing waits on a host or on the user.

## Task notes

**1.1** `plugin/lib/cards.py`: the budget table gains `STEP`, `ABOUT` and `NOTE`, each with its source. The two `cut(…, 120)` of an `about.title` (`landings_card`, `proposal_card`) and `change_args`'s change note name them, as does `plan.row_card_change`'s close outcome. Check: `tests/py/test_cards.py`, `tests/py/test_card_commands.py`.

**1.2** `cards.step(words, command=None, short=None)`. `step_card`'s gate step, its commands and its words are built by it. Cases in `TestStep`: a command longer than `STEP` is "Run this command." with the command whole, and a gate's link longer than `STEP` says to open the gate at the card's link, its *where* the link.

**1.3** `step_card`, the user's step:
- The title is "After <env>'s deploy: " and `by_words(words, TITLE - len(head))`.
- The steps are the commands through `step`, or `step(words, short=prose(words, STEP))`.
- The face is `markdown("The step", "op-<env>-<n>.md", words)`, added unless the title, the step or the summary holds the words whole (Decision 2).

Cases in `TestStep`:
- deneb's 370-character words with a why: the first sentence is the step, the words whole on the face, and the title within `TITLE` ending "…";
- the same words with no why: the summary holds them, so there is no face;
- a 600-character sentence: its step is cut at whole words, and the face holds it;
- a short step with commands and a why: no face.

**1.4** `step_card`, the held step: the words are cut at whole words to the room left by the head and ", now or when the host is quiet?", with the face when they were cut. Case in `TestStep`.

**1.5** `change_args` always sends `artifacts`, `[]` for a card that carries none. Case in `TestStep`: a step card built with short words sends `[]`, and one with a face sends it.

**2.1** `tests/py/test_card_commands.py`: `Py.answer` takes a function of the tool's arguments as an answer. `strict_post` refuses a post with a step of 300 characters or more in Pending You's words.
- A 370-character step with no commands, posted through `plan.row_card_post` on it, is posted and recorded, every step within `STEP`, the title within `TITLE`, and the words whole on the face.
- A step's card refused in those words is recorded refused, and `plan.last_refusal` gives the words for its row's card line.

**2.2** `tests/stubs/pendingyou`: `post_request` and `update_request` refuse an action with a step of 300 characters or more, "Keep each step’s words under 300 characters.", before anything else is judged.

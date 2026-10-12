# Design: a batch card's notes are its note and its sessions

## Context

A batch is posted today as one card per five units, keyed `batch/<n>-<k>` (`plan.py` `CARD_UNITS`, `rail_rows`, `batch_keys`), each a grouped card asking "which need notes?" as a pick-several and the notes as a question in words (`planner.md` *Batches* step 2). Pending You makes every question required, so the user could not send a card with nothing picked, and the reviewer's summary went on the card as a Markdown code artifact that scrolls sideways on the phone. The card hook (`plugin/hooks/cards`) checks a proposal's, a verify report's and a landing's card against its row's form (`FORMS`, `form_refusal`) and lets a batch's card through on its key alone, its comment saying so until this unit lands.

The ruling this change builds is `briefs.13` as amended 2026-10-11: "a batch's one card for the whole batch, never split, naming every unit, asking nothing and closed by one tap, its notes the annotations the user sends from each unit's reading session and the card's own note, both named on the card in plain words, and its summary readable on the phone as prose that wraps; ... never a required words question, and crew refuses a row's card in another form." Record 0005 says the same in its bullet "A batch is one card that asks nothing, and says where notes go", and adds that a monospace block is only for a table that needs its columns, within a phone's width, as record 0018's proposal text.

Sources read, on crew's main: `docs/architecture/briefs.md` (`briefs.9`, `briefs.11` to `briefs.13` and their details); `docs/adr/0018-a-proposals-card-shows-the-change-and-lets-new-units-be-left-out.md` (every question required; a note on any kind; "there is no text question ... the note is the place for words"); `docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md`; signals 2026-10-11-swancloud-planner-ab370c3e/01, /02, /04 and 7c9208ad/01 on swancloud's state branch; Pending You's guide 2.52 (`https://www.pendingyou.com/skill.md`, *Kinds*: `fyi` is "Nothing to answer; you're telling them", sent with "A title and summary"; *Intents*: `heads_up` "Nothing: you're letting them know"; *Hear the answer*: a `note` may come "on any kind, with or without an option"); the `post_request` and `update_request` schemas as the MCP server serves them (`summary` at most 400 characters; `context.background` a string; `context.links`); in this worktree, `plugin/hooks/cards`, `plugin/lib/plan.py` (`rail_rows`, `batch_keys`, `card_refusal`, `card_of`, `batch_team`, `card_units`, `card_end`), `plugin/lib/crew.py` `cards_how`, `plugin/roles/planner.md`, `plugin/roles/reviewer.md`, and the landed but unarchived `units-build-at-once-and-are-reviewed-in-batches` change's `review-batches`, `rail-cards` and `card-sessions` deltas; batch 5's summary file on mac-studio, for what the reviewer writes today (ten fence lines).

Rule pages this change touches: `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/lib/crew.py`), `briefs.md` (`plugin/roles/`), `docs.md` (`README.md`), `tests.md` (`tests/`). It relies on `briefs.9` ("annotations the user wrote that reach nobody" ruled out), `briefs.11` (the planner posts the batches' cards), `briefs.12` (notes go to the unit's conductor with no approval asked), `briefs.13`, `roles.3` (a brief-stated rule gets a check in crew), `read.1` (what crew cannot read, it refuses), `code.1`, `code.2` and `tests.6`. It departs from `briefs.12`'s "cards of at most five units, each asking which need notes and for the notes", which `briefs.13` as amended rules over; the design agent amends `briefs.12` (named in the final message).

## Goals / Non-Goals

**Goals:**
- One card per batch, naming every unit, that the user sends back with one tap and nothing picked or typed.
- A unit's notes read from where the user wrote them, its session's annotations and the card's own note, with no words of theirs reaching nobody.
- The summary as prose that wraps on a phone.
- crew refusing a batch card in any other form, and any crew card that asks a question in words.

**Non-Goals:**
- A reading session whose files do not open (signal ab370c3e/04): `a-cards-reading-session-opens-its-files`.
- The proposal card's form, the landing card's stakes, and cards outside the rail (`any-question-for-the-user-gets-a-card`).
- How batches fall due, how the reviewer reads a change, how a session starts and ends: unchanged.
- `docs/architecture/` and `docs/adr/` (`docs.7`).

## Decisions

### One row and one card per batch, keyed `batch/<n>`

The rail shows one row per batch, keyed `batch/<n>`, holding every unit of the batch, open until a `card.close` names that key. `CARD_UNITS` and the split by five go. The key is the batch's own number, as a proposal's is, so nothing in it reads as one of several cards; `batch/<n>` is already the batch's object in the run record (`review.batch`'s `On`), so the key and the object agree.

`batch_keys`, `card_refusal`, `card_of`, `batch_team`, `card_units` and `card_end` read `batch/<n>`, with the batch's whole unit list. A card's session state lives at `cards/<label>/batch/<n>/<unit>/`. The rail row's answer command becomes `crew tell <label>-planner "On batch <n>: "`, the user's notes in their words after it.

Considered: keeping `batch/<n>-<k>` with `k` always 1, which leaves every key reading as the first of several and still has to drop the split.

### A batch posted before this lands keeps its old keys until its cards close

A batch for which the run record holds a `card.post` under a `batch/<n>-<k>` key is read as it was posted: its rows are those old keys whose cards are not closed, each holding its five units as before, and the planner may not post `batch/<n>` for it. The hook's key patterns keep matching `batch/<n>-<k>`, so closing such a card is recorded and its sessions end; `card_of`, `card_units`, `batch_team` and `card_end` take an old key and read its five units as they do now. Once every old card of a batch has closed, its row is gone. A batch with no card posted reads only as `batch/<n>`. Nothing new is ever posted under an old key.

### The card is a notice, sent back with one tap

A batch card is `kind: "fyi"`, `intent: "heads_up"`: Pending You's kind for a card with nothing to answer. It has no `options`, `questions`, `text`, `approve`, `action` or `artifacts`, and is not high stakes. The user reads it, writes the card's note if they have one, and sends it back with the one control an `fyi` card shows. Units go on building whatever the user does with it (`briefs.12`: code is never held for a batch's answer).

Its title names the batch and its count: "Batch 3 of swancloud: 6 changes to read". Its summary, at most 400 characters, is the plain-words line the ruling asks for, naming where notes go:

> Nothing to answer. To leave notes on a change, annotate it in its reading session and send them there, or write them in this card's note, naming the change. Tap once when you're done; every change goes on building either way.

Its background is, for each unit in the reviewer's order, a line with the unit's name and team, the line "Read and annotate it: <its session's link>", then that unit's section of the reviewer's summary as written. Its links are each unit's session, labelled "Read and annotate <unit>". The background is where Pending You shows long words, and prose there wraps.

Considered: a `review` card, Pending You's "Something to look at", whose intent is `approve` and whose answer is a sign-off, where the card approves nothing; a pick-several of units sendable with none picked, which the user rejected as making them choose which units get notes, and which a batch of six cannot hold in five options.

### What the card checks for

`FORMS["batch"]` is kinds `("fyi",)`, not high stakes, no options, no steps. The batch row adds, on a post: an `approve`, `text` or `questions` field refused; an artifact refused ("attaches its summary"; the summary goes in the card's words); a fence (a line starting with three backticks or three tildes) in its summary or background refused ("puts its summary in a code block, which scrolls sideways on the phone"); and each unit of the batch, read from the run record by the key, must be named in its background, else "leaves out <units>". On an update: options, questions, steps, an `approve` or `text`, artifacts that are not empty or null, and a fence in a new summary or background are refused. A change that sets the background again is checked for every unit too.

The refusal's words follow the other rows': "a batch's card is one notice for the whole batch, kind \"fyi\", naming every unit, with each unit's summary as prose in its background and nothing to answer: no options, no question, no approval, no steps and no attachment".

Every row's card, whatever its form, is refused when it asks a question in words: `kind: "text"`, a `text` field, or a question of kind `text`, "asks a question in words, which Pending You makes required; the card's note is where the user's words go". Today `card_refusal` lets a crew agent post only under a row's key, so this covers every card of crew's.

What the hook cannot read for the unit check, the run record or a batch it does not hold, it refuses naming what failed (`read.1`), as the key check already does.

### Where a unit's notes come from

A unit's reading session is waited on as today, `crew card wait batch/<n> <unit>`. Annotations the user sends from it go to that unit's team's conductor at once, word for word, as "The user's notes on <unit>, from batch <n>'s reading session: <the annotations>". A session approved with no annotations means that unit is fine. Neither answers or withdraws the batch card: the card stays the user's until they send it. `cards_how`'s general rule, that a decision in a card's session is the card's answer and the card is then withdrawn, gains the batch card as its exception.

When the user sends the card, its note, if any, goes word for word to the conductor of each unit it speaks of, as the planner reads it: by name, or by what it says of a unit's summary. The message names every unit the note went to, so a construct reading a note that speaks of several knows the rest is another unit's. A note that speaks of no unit the planner can tell goes to every unit's conductor, saying the note named no unit, since words of the user's that reach nobody are ruled out (`briefs.9`). The planner never splits, rewords or summarizes a note.

The planner then closes the card with `ack_answer`, its outcome naming the units it sent notes to ("Sent your note to x1's and z1's teams; the rest are fine"), and crew's hook ends the card's sessions, as today. Annotations not yet sent from a session when the card closes end with the session; the card's line "Tap once when you're done" puts the tap after them.

### The summary is prose

The reviewer writes each unit's section as paragraphs and plain lists, with no code block and no table. A change's Touches is named in words ("the card hook, the planner's brief and their tests"), since no card carries a path. A section's text is posted as the reviewer wrote it, so the card and the file say the same.

### Where the words live

`planner.md` *Batches* steps 2 and 3 carry the card's form, its words and the reading of the notes; *Cards* names the batch card's form beside the proposal's. `reviewer.md` *The summary* says prose, no code block, Touches in words. `cards_how` gains one sentence on a batch card's sessions. README's batch and card paragraphs say one card per batch, asking nothing. `tests/t-briefs.sh` pins the new phrases and refuses the old ones.

## Risks / Trade-offs

- [Pending You's `fyi` card may close without reaching the planner, or may carry no `note`] → The guide says a note comes on any kind, but does not say an `fyi` card wakes its asker when sent back. Proof in dev reads it first; if it fails, the card's premise is wrong and the decision goes back to `swancloud-design` before the planner posts one.
- [A long background may be cut, or may not wrap] → Proof in dev reads a background the size of batch 5's on the phone.
- [The planner may read a note as speaking of a unit the user did not mean] → Every message names the units the note went to, and the closing outcome says so on the card, so the user sees where it went.
- [A note naming no unit makes every unit's construct run again] → The card's line asks the user to name the change; a construct reading a note that does not concern its unit leaves its change as it is.
- [Annotations sent after the card's tap are lost with the session] → The card says to tap once done; the closing outcome names what was sent for each unit.

## Migration Plan

Batches posted before this lands keep their `batch/<n>-<k>` cards until each closes, as above; no data moves. The planner's brief, once loaded fresh after landing, posts `batch/<n>` for any batch with no card.

## Proof in dev

What a coder cannot check locally, for the team's ops once the bolt is deployed. crew refuses a card ops posts, so items 1 and 2 are posted from a Claude session crew did not start, in the Getting started area (the `testAreaId` `report_setup` returns), not under a `batch/` key, and each is closed after.

1. A `post_request` of `kind: "fyi"`, `intent: "heads_up"`, the summary above and three `context.links`, shows one control on the user's phone, and the user sends it with one tap and a note. The asker is woken, and `get_request` returns the answer with the note. If the asker is not woken, or the note does not come back, stop: the decision goes back to `swancloud-design`.
2. The same card with a background of about 6,000 characters, batch 5's sections as prose with lists and no code block, reads on the phone whole, wrapping, with no sideways scroll; the user says so.
3. The first real batch after landing reaches the user as one card naming every unit, and the user sends it back with one tap; the planner closes it and no unit is constructed again unless the user left notes.

## Task notes

**1.1** In `plan.py`, drop `CARD_UNITS`. `rail_rows`: one row per batch, key `batch/{n}`, `units` every unit of the batch, `what` "batch {n} ({l}): " and every unit with its team, open until a close names the key; a batch whose run record holds a `card.post` under `batch/{n}-{k}` gives instead a row for each such key not closed, holding its five units (`units[(k-1)*5:k*5]`, the five kept as a literal for these old keys). The answer command is `crew tell {l}-planner "On batch {n}: "`. `batch_keys` returns the same keys. `CARD_KEYS` takes `batch/\d+` and `batch/\d+-\d+`. `card_refusal`'s words name `batch/<n>`. `card_of`'s "not a card key" words name `batch/<n>`. `batch_team` and `card_units` read `batch/<n>` as every unit of batch n, and `batch/<n>-<k>` as before. Update `rail_rows`' and `batch_keys`' docstrings.

**1.2** `tests/t-batch-cards.sh` runs its scenarios under `batch/1` and the state folder `batch/1/<unit>`, and adds one: a batch whose record holds a post under `batch/1-1` still starts, waits on and ends that key's sessions. `tests/t-batches.sh` line 79 to 91: a batch of seven is one row, `batch/2`; a batch with a `card.post` under `batch/3-1` and `batch/3-2` shows those rows until each closes, and refuses the planner's `batch/3`.

**2.1** In `plugin/hooks/cards`, add `"batch"` to `FORMS` with `kinds=("fyi",)`, `high=False`, `options=False`, `steps=False` and the `says` above. In `form_refusal`, for every row: `kind == "text"`, a `text` key, or any question of kind `text` adds "asks a question in words, which Pending You makes required". For the batch row: `approve` given adds "approves something"; `artifacts` a non-empty list adds "attaches its summary"; a summary or background holding a line that starts with ```` ``` ```` or `~~~` adds "puts its summary in a code block, which scrolls sideways on the phone". `KEYS`' batch pattern becomes `^batch/(\d+)(?:-\d+)?$`. Remove the comment that a batch card is checked for its key alone and the module docstring's "but a batch's, which has no form there yet".

**2.2** The unit check: on a post under `batch/<n>`, and on an update that gives a background to a card posted under one, the hook reads the batch's units with `plan.card_units(fleet, label, key)` and adds "leaves out <units>" for each not named in the background (a whole-word match on the unit's name). Its failure is a refusal naming what failed, as the key check's is. A post under an old `batch/<n>-<k>` key is refused by `card_refusal` already, so the form is not checked for it.

**2.3** In `tests/t-cards.sh`, turn line 286's grouped card into a refusal under `batch/1`, and add: an `fyi` naming every unit with prose in its background let through; a `multi`, an `approve`, a `text` and a grouped card refused; an `fyi` with an artifact refused; one with a fenced block in its background refused; one leaving out a unit refused, naming it; an update giving options, a `code` artifact or a fenced background refused. Add a `text` card under `proposal/1` and a verify key refused for asking in words. Line 83's record entry: a post under `batch/3` records `On batch/3` and `Key batch/3`; one under `batch/3-2` still records as before. Update the opening comment's sentence on a batch card's form.

**3.1** In `plugin/roles/planner.md` *Batches* step 2: one card per batch, keyed `batch/<n>`, naming every unit; kind `fyi`, intent `heads_up`; title, summary, background and links as the design says, the summary's words quoted; never a choice of units, a question or an attachment. Wait on each unit's session with `card wait batch/<n> <unit>`; annotations sent from one go to that unit's conductor at once, word for word; approved means that unit is fine; neither answers or withdraws the card. Step 3: when the user sends the card, send its note word for word to the conductor of each unit it speaks of, naming every unit it went to, or to every unit's conductor when it names none; close the card with `ack_answer` naming where notes went. Drop "of at most five units", "which need notes?", "one in words for the notes", "send each picked unit's notes" and "A unit not picked is fine". In *Cards*, the batch's card in one sentence beside the proposal's.

**3.2** In `plugin/roles/reviewer.md` *The summary*: each section is paragraphs and plain lists that wrap on a phone, with no code block and no table; Its Touches names what the change edits in words, never as paths.

**3.3** In `plugin/lib/crew.py` `cards_how`, after the sentence on withdrawing a card answered in its session: a batch card's sessions are its units', so a decision in one is that unit's and never the card's answer, and the card stays open until the user sends it, as the planner's brief says.

**3.4** In `README.md`, the rail-cards paragraph's "each card of a review batch" becomes each review batch's one card, and its forms sentence adds a batch's: one notice naming every unit, asking nothing, sent back with one tap, the notes being each unit's session's annotations and the card's note. The batches paragraph says the same where it names the batch's cards.

**3.5** In `tests/t-briefs.sh` around line 298, replace the batch wants with the new phrases: `card session batch/<n> <unit> --label wldn`, `card wait batch/<n> <unit> --label wldn`, `keyed \`batch/<n>\``, kind `fyi`, "Nothing to answer.", the note to each unit it speaks of, the note naming none to every unit, a session's annotations sent at once. Add `lacks` for "of at most five units", "which need notes?", "one in words for the notes" and "A unit not picked is fine". Pin the reviewer's "no code block" and `cards_how`'s new sentence.

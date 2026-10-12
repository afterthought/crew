# Design: a batch card's notes are its note and its session

## Context

On crew's main a batch is posted as one card per five units, keyed `batch/<n>-<k>`, each a grouped card asking "which need notes?" as a pick-several and the notes as a question in words (`planner.md` *Batches* step 2). Pending You makes every question required, so the user could not send a card with nothing picked, and the reviewer's summary went on the card as a Markdown code artifact that scrolls sideways on the phone. Each unit on a card links its own plannotator session, started on that unit's change folder on its team's host; the first batch's session listed the files but opened none when clicked (signal ab370c3e/04), and plannotator is given a folder there (`plan.py` `card_session`, the trailing slash).

This unit's branch already holds the first part of the change: one rail row and one card key per batch, `batch/<n>`, with a batch posted under the old keys read as it was (`plan.py` `rail_rows`, `batch_cards`, `batch_keys`, `card_part`, `card_units`); and the card hook's batch form, `fyi` with nothing to answer, no attachment, no code block and every unit named in its background, and no card of any row asking a question in words (`plugin/hooks/cards` `FORMS["batch"]`, `form_refusal`, `WORDS`, `FENCE`). Its sessions are still one per unit, under `batch/<n>/<unit>`.

The ruling this change builds, on crew's main:

- `briefs.13`: "a batch's one card for the whole batch, never split, saying first what it is, naming every unit, asking nothing and closed by one tap, its notes the annotations the user sends from the batch's one reading session and the card's own note, both named on the card in plain words, and its summary readable on the phone as prose that wraps; ... never a required words question, and crew refuses a row's card in another form."
- `briefs.9`: "a batch card carries the reviewer's summary cut to the card's budget and one such session's link, on the batch's folder holding the summary whole and every unit's whole change, and is answered in Pending You"; ruled out, "one session per unit on a batch card", and "annotations the user wrote that reach nobody".
- `briefs.12`: the batch is "posted by the planner as one card that says what it is, names every unit and links one reading session on the batch"; the planner sends each unit's notes from the session and the card to its team's conductor.
- Record 0005, the bullet "A batch card is a summary and one reading session, and says what it is": the card says first, in plain words, that it is "the partition's batch of the changes constructed or amended since the last batch, already being built, read for notes, approving nothing"; then the reviewer's summary cut to the card's budget, naming every unit and its team; then one link, to one session on the batch's own folder, "which holds the reviewer's summary whole and every unit's whole change as read at its commit"; the session "opens the summary and every change whole, as one review in that order with one decision, which is how plannotator opens several files (its usage, 0.28.6), never a folder whose listed files the user must click open"; nothing of plannotator's is patched, and `a-cards-reading-session-opens-its-files` folds into this unit. And the bullet "A batch is one card that asks nothing, and says where notes go": a monospace block only for a table that needs its columns, within a phone's width.
- Record 0018: every Pending You question is required, a note comes on any kind, and "there is no text question ... the note is the place for words".

Sources read, on crew's main: `docs/architecture/briefs.md` (`briefs.9`, `briefs.11` to `briefs.13` and their details); `docs/adr/0018-a-proposals-card-shows-the-change-and-lets-new-units-be-left-out.md`; `docs/adr/0005-the-rail-is-answered-through-pending-you-cards.md`, the two batch bullets; `docs/architecture/_open.md`, the batch item; on swancloud's state branch, signals 2026-10-11-swancloud-planner-ab370c3e/01, /02, /04, 7c9208ad/01, 2026-10-12-swancloud-planner-9ddc53be/01, e445bc04/01 and d111a426/01. Readings of the vendors:

- Pending You's `post_request` schema as the MCP server serves it (read 2026-10-11): `summary` at most 400 characters; `context.background` a string with no stated limit; `context.links` a list of label and url; kinds `choice`, `multi`, `approve`, `text`, `review`, `action`, `fyi`; intent `heads_up`. Its guide 2.52: `fyi` is "Nothing to answer; you're telling them"; a `note` may come "on any kind, with or without an option".
- plannotator 0.28.6 on mac-studio: `plannotator annotate --help` says "Several existing file paths (plannotator annotate spec.md mock.html notes.md) open as one review, in that order, with one decision for all of them"; a session started that way on three files with `--gate --json --result-file` lists in `plannotator sessions --json` with `target` the three paths joined by ", " and `label` "annotate-3 files: summary.md, proposal.md, proposal.md", the basenames only; its `--json` result is `decision` approved, annotated or dismissed with `feedback` text, as for one file. Not read: whether the feedback text names the file each annotation is on, which plannotator's page builds (*Proof in dev*, item 3).

In this worktree: `plugin/hooks/cards`, `plugin/lib/plan.py` (`card_of`, `card_session`, `change_folder`, `forward_card`, `batch_team`, `card_wait`, `end_session`, `card_end`, `card_folder`, `card_sweep`, `card_units`, `reading_command`, `reviews`, `batch_file`, `units_of_batch`), `plugin/lib/crew.py` `cards_how`, `plugin/roles/planner.md`, `plugin/roles/reviewer.md`, `plugin/bin/crew`'s usage, `plugin/skills/crew/SKILL.md`, README's rail-cards and batches paragraphs, and the landed but unarchived `units-build-at-once-and-are-reviewed-in-batches` change's deltas.

Rule pages this change touches: `plan.md` (`plugin/lib/plan.py`), `teams.md` (`plugin/lib/crew.py`, `plugin/bin/crew`), `briefs.md` (`plugin/roles/`, `plugin/skills/`), `docs.md` (`README.md`), `tests.md` (`tests/`). It relies on `briefs.9`, `briefs.11` (the planner posts the batches' cards), `briefs.12`, `briefs.13`, `roles.3` (a brief-stated rule gets a check in crew), `read.1` (what crew cannot read, it refuses), `code.1`, `code.2`, `code.3` (every ssh with `BatchMode=yes`), `docs.2` (a command's change in README, the skill and the usage together) and `tests.6`.

## Goals / Non-Goals

**Goals:**
- One card per batch, saying first what it is, naming every unit and its team, that the user sends back with one tap and nothing picked or typed.
- One reading session per batch that opens the reviewer's summary and every unit's whole change as one review, every file whole.
- The batch's notes read from where the user wrote them, the session's annotations and the card's own note, with no words of theirs reaching nobody.
- The card's words as prose that wraps on a phone.
- crew refusing a batch card in any other form, and any crew card that asks a question in words.

**Non-Goals:**
- Patching plannotator, or its folder mode (signal d111a426/01).
- The proposal card's form, the landing card's stakes, and cards outside the rail (`any-question-for-the-user-gets-a-card`).
- How batches fall due, how the reviewer reads a change, how a session starts and ends for any other row: unchanged.
- `docs/architecture/` and `docs/adr/` (`docs.7`).

## Decisions

### One row and one card per batch, keyed `batch/<n>`

The rail shows one row per batch, keyed `batch/<n>`, holding every unit of the batch, open until a `card.close` names that key. The key is the batch's own number, as a proposal's is, so nothing in it reads as one of several cards; `batch/<n>` is already the batch's object in the run record (`review.batch`'s `On`), so the key and the object agree. The rail row's answer command is `crew tell <label>-planner "On batch <n>: "`, the user's notes in their words after it.

Considered: keeping `batch/<n>-<k>` with `k` always 1, which leaves every key reading as the first of several and still has to drop the split.

### A batch posted before this lands keeps its old keys and sessions until its cards close

A batch for which the run record holds a `card.post` under a `batch/<n>-<k>` key is read as it was posted: its rows are those old keys whose cards are not closed, each holding its five units, and the planner may not post `batch/<n>` for it. Such a card keeps its one session per unit, `crew card session|wait|end batch/<n>-<k> <unit>` on the unit's team's host, as today, and its close ends them as today. Once every old card of a batch has closed, its row is gone. A batch with no card posted reads only as `batch/<n>`. Nothing new is ever posted under an old key.

### The batch's folder holds the summary and every change

The batch's own folder is `~/.local/state/crew/<label>-main/reports/batch-<label>-<n>/`, on the main level's host, beside the reviewer's summary file. crew writes it when the session is started, from the batch in the run record (`review.batch`, each unit at the commit its change was read at):

- `00-summary.md`, the reviewer's summary file as written.
- For the k-th unit in the batch's order (two digits, from `01`), each Markdown file of `openspec/changes/<unit>/` at that unit's commit, read from its kit's main checkout on its team's host with `git ls-tree` and `git show`, over `ssh -o BatchMode=yes` when the team's host is another (`code.3`), as the reviewer's prompt reads it (`reading_command`). Each is named `<kk>-<unit>-<its path under the change, with / as ->`: `01-x1-proposal.md`, `01-x1-design.md`, `01-x1-specs-card-sessions-spec.md`, `01-x1-tasks.md`.

Every name carries its unit, since plannotator shows a file of several by its basename alone, so the user sees which unit each file is, and so does any feedback that names its file. A change's files that are not Markdown (`.openspec.yaml`) are left out: they say nothing to the reader and plannotator opens Markdown, text and HTML. The files are the change as read at its commit, not as its branch stands now, so the session shows what the summary speaks of.

What crew cannot read for the folder, a host that does not answer, a commit not in the kit, the summary not written, refuses the session naming the unit, the host and what failed, and starts nothing (`read.1`); a session never opens on part of a batch.

Considered: a session on each unit's folder in place on its team's host, which is today's form, needs a session per host and per unit, and is what record 0005 ruled out; plannotator's folder mode on the batch's folder, whose listed files the first batch's user could not open over the tailnet.

### One session per batch, opened as one review

`crew card session batch/<n>` takes no unit. It runs on the partition's main level's host, where the summary and the planner are, and refuses elsewhere, naming that host. It writes the batch's folder, then starts `plannotator annotate <file> <file>... --gate --json --result-file <result>`, every file of the folder as its own path in the order above, the summary first, then each unit's proposal, design, specs in path order, tasks, and any other Markdown in path order. That is one review with one decision, which opens each file whole. The session is kept, like a proposal's, in `~/.local/state/crew/cards/<label>/batch/<n>/`, its `document` the files as plannotator lists them, joined by ", ", and crew judges it serving when plannotator lists that pid with that target, path by path. While it runs, `crew card session batch/<n>` prints its link again and starts nothing, and the folder is not written again.

`crew card session batch/<n> <unit>`, `wait` and `end` with a unit are refused for a `batch/<n>` key: "a batch has one reading session, on the whole batch: crew card session batch/<n>". `crew card wait batch/<n>` and `crew card end batch/<n>` act on that one session on the host they run on. When a crew agent closes or withdraws a `batch/<n>` card, crew's hook ends its session in the hook, as for a proposal's; an old `batch/<n>-<k>` card's close still runs `crew card end` apart, since its sessions are on its units' hosts. The rail's sweep reads `batch/<n>/session.json` as a key's own session, as it reads a proposal's.

### The card says what it is, and is a notice sent back with one tap

A batch card is `kind: "fyi"`, `intent: "heads_up"`: Pending You's kind for a card with nothing to answer. It has no `options`, `questions`, `text`, `approve`, `action` or `artifacts`, and is not high stakes. Units go on building whatever the user does with it (`briefs.12`).

- **Title**: the batch and its count, "Batch 3 of swancloud: 6 changes to read".
- **Summary** (at most 400 characters): what the card is, then where notes go, in these words, with the batch's number, partition and count filled in:

  > This is batch 3 of swancloud: the 6 changes written or rewritten since the last batch, already being built. Nothing to answer and nothing to approve. To leave notes, annotate the changes in the reading session and send them there, or write them in this card's note, naming the change. Tap once when you're done; every change goes on building either way.

- **Background**: first the line "Read and annotate the whole batch, its summary and every change: <the session's link>"; then, for each unit in the reviewer's order, a line with the unit's name and its team, and the opening paragraph the reviewer wrote for it. This is the reviewer's summary cut to the card's budget: each unit's few sentences, the rest in the session.
- **Links**: the one session, labelled "Read and annotate batch 3".

The card's own words open with what it is, as `briefs.13` and record 0005 order it; the link opens the background and is the card's one link, as `briefs.9` has a session's link.

Considered: a `review` card, Pending You's "Something to look at", whose intent is `approve` and whose answer is a sign-off, where the card approves nothing; a pick-several of units sendable with none picked, which the user rejected as making them choose which units get notes, and which a batch of six cannot hold in five options; each unit's whole section in the background, which makes a batch of six a long scroll that the session already holds.

### What the card hook checks

`FORMS["batch"]` is kinds `("fyi",)`, not high stakes, no options, no steps. The batch row adds, on a post: an `approve`, `text` or `questions` field refused; an artifact refused ("attaches its summary"); a fence, a line starting with three backticks or three tildes, in its summary or background refused ("puts its summary in a code block, which scrolls sideways on the phone"); more than one entry in `context.links` refused ("links more than one session; a batch has one reading session"); and each unit of the batch, read from the run record by the key, must be named in its background, else "leaves out <units>". On an update: options, questions, steps, an `approve` or `text`, artifacts that are not empty or null, a fence in a new summary or background, and more than one link are refused, and a change that sets the background again is checked for every unit.

The refusal's words follow the other rows': "a batch's card is one notice for the whole batch, kind \"fyi\", saying what it is, naming every unit, with each unit's summary as prose in its background, one link to the batch's reading session and nothing to answer: no options, no question, no approval, no steps and no attachment".

Every row's card, whatever its form, is refused when it asks a question in words: `kind: "text"`, a `text` field, or a question of kind `text`, "asks a question in words, which Pending You makes required; the card's note is where the user's words go". `card_refusal` lets a crew agent post only under a row's key, so this covers every card of crew's.

What the hook cannot read for the unit check, the run record or a batch it does not hold, it refuses naming what failed (`read.1`). Whether the summary says what the card is, in the planner's words, is the brief's and pinned by `tests/t-briefs.sh`; the hook reads no prose.

### Where the batch's notes come from

The planner waits on the session with `crew card wait batch/<n>` as a background command. When the user sends annotations from it, the planner sends them at once, word for word, to the conductor of each unit they speak of, as "The user's notes on <unit>, from batch <n>'s reading session: <the annotations>". It reads which unit an annotation speaks of from the file it names, when the feedback names one, every file being named for its unit, else from what it quotes and says. An annotation it cannot place goes to every unit's conductor, saying it named no unit it could tell. A message carrying annotations for several units names every unit they went to. A session approved with no annotations means every unit is fine as far as the session goes. Neither answers or withdraws the card: it stays the user's until they send it. `cards_how`'s general rule, that a decision in a card's session is the card's answer and the card is then withdrawn, gains the batch card as its exception.

When the user sends the card, its note, if any, goes the same way: word for word to the conductor of each unit it speaks of, by name or by what it says of a unit's summary, naming every unit it went to, or to every unit's conductor when it names none, saying so (`briefs.9`: no words reaching nobody). The planner never splits, rewords or summarizes the user's words. A unit no annotation and no note speaks of is fine.

The planner then closes the card with `ack_answer`, its outcome naming the units it sent notes to ("Sent your notes to x1's and z1's teams; the rest are fine"), and crew's hook ends the session. Annotations not yet sent from the session when the card closes end with it; the card's line "Tap once when you're done" puts the tap after them.

### The summary is prose, and opens each unit with what the card carries

The reviewer's section for each unit opens with a paragraph of a few sentences saying what the change does and what the user would most care about in it: the paragraph the card carries. The rest of the section, the decisions, the risks, what it touches and what is left open, follows as paragraphs and plain lists, with no code block and no table. What a change touches is named in words ("the card hook, the planner's brief and their tests"), since no card and no summary carries a path. The planner posts each opening paragraph as the reviewer wrote it, so the card and the session say the same.

### Where the words live

`planner.md` *Batches* steps 2 and 3 carry the card's form, its words, the one session and the reading of the notes; *Cards* names the batch card's form beside the proposal's. `reviewer.md` *The summary* says the opening paragraph, prose, no code block, Touches in words. `cards_how` gains one sentence on a batch card's session. README's rail-cards and batches paragraphs, `plugin/skills/crew/SKILL.md`'s card rows and `plugin/bin/crew`'s usage for `crew card` say one card per batch, asking nothing, with one session on the batch (`docs.2`). `tests/t-briefs.sh` pins the new phrases and refuses the old ones.

## Risks / Trade-offs

- [Pending You's `fyi` card may close without reaching the planner, or may carry no `note`] → The guide says a note comes on any kind, but does not say an `fyi` card wakes its asker when sent back. *Proof in dev* reads it first; if it fails, the card's premise is wrong and the decision goes back to `swancloud-design` before the planner posts one.
- [plannotator's feedback may not name the file each annotation is on] → Every file's name carries its unit, and the planner places an annotation by what it quotes when the file is not named; one it cannot place goes to every unit's team, saying so. *Proof in dev* reads which it is.
- [A session of thirty files is long to page through on a phone] → The summary comes first and each file is named for its unit; the user reads the card's paragraphs to choose what to open.
- [Once the user sends from the session, its link no longer opens a review] → The card's note still takes words; the planner's outcome on closing names what reached each team.
- [The planner may read a note or an annotation as speaking of a unit the user did not mean] → Every message names the units it went to, and the closing outcome says so on the card, so the user sees where it went.
- [Words naming no unit make every unit's construct run again] → The card's line asks the user to name the change; a construct reading notes that do not concern its unit leaves its change as it is.

## Migration Plan

Batches posted before this lands keep their `batch/<n>-<k>` cards and per-unit sessions until each closes, as above; no data moves. The planner's brief, once loaded fresh after landing, posts `batch/<n>` with its one session for any batch with no card.

## Proof in dev

What a coder cannot check locally, for the team's ops once the bolt is deployed. crew refuses a card ops posts, so items 1 and 2 are posted from a Claude session crew did not start, in the Getting started area (the `testAreaId` `report_setup` returns), not under a `batch/` key, and each is closed after.

1. A `post_request` of `kind: "fyi"`, `intent: "heads_up"`, the summary above and one `context.links` entry, shows one control on the user's phone, and the user sends it with one tap and a note. The asker is woken, and `get_request` returns the answer with the note. If the asker is not woken, or the note does not come back, stop: the decision goes back to `swancloud-design`.
2. The same card with a background of six units' opening paragraphs, about 3,000 characters of prose, reads on the phone whole, wrapping, with no sideways scroll; the user says so.
3. `crew card session batch/<n>` on a real batch of at least two units from two teams' hosts opens, from the user's phone over the tailnet, the summary and then every file of each change, each whole, in order. The user annotates one passage in two units' files and sends them; the feedback `crew card wait` prints is read for whether it names each annotation's file, and the reading is said to `swancloud-design`.
4. The first real batch after landing reaches the user as one card that says what it is, names every unit and links one session, and the user sends it back with one tap; the planner closes it and no unit is constructed again unless the user left notes.

## Task notes

**1.1** In `plan.py`, drop `CARD_UNITS`. `rail_rows`: one row per batch, key `batch/{n}`, `units` every unit of the batch, `what` "batch {n} ({l}): " and every unit with its team, open until a close names the key; a batch whose run record holds a `card.post` under `batch/{n}-{k}` gives instead a row for each such key not closed, holding its five units. The answer command is `crew tell {l}-planner "On batch {n}: "`. `batch_keys` returns the same keys. `CARD_KEYS` takes `batch/\d+` and `batch/\d+-\d+`. `card_refusal`'s and `card_of`'s words name `batch/<n>`. `batch_team` and `card_units` read `batch/<n>` as every unit of batch n, and `batch/<n>-<k>` as before.

**1.2** `tests/t-batches.sh`: a batch of seven is one row, `batch/2`; a batch with a `card.post` under `batch/3-1` and `batch/3-2` shows those rows until each closes, and refuses the planner's `batch/3`.

**2.1** In `plugin/hooks/cards`, `FORMS["batch"]` with `kinds=("fyi",)`, `high=False`, `options=False`, `steps=False`. In `form_refusal`, for every row: `kind == "text"`, a `text` key, or any question of kind `text` adds `WORDS`. For the batch row: `approve` given, a non-empty `artifacts`, and a fence in the summary or background each refused. `KEYS`' batch pattern `^batch/(\d+)(?:-\d+)?$`.

**2.2** The unit check: on a post under `batch/<n>`, and on an update that gives a background to a card posted under one, the hook reads the batch's units with `plan.card_units` and adds "leaves out <units>" for each not named in the background, as a whole word. Its failure is a refusal naming what failed. An old `batch/<n>-<k>` key is refused by `card_refusal` for a new post, and its card is not checked.

**2.3** In `tests/t-cards.sh`: an `fyi` under `batch/1` naming every unit with prose in its background and one link let through; a `multi`, an `approve`, a `text` and a grouped card refused; an `fyi` with an artifact refused; one with a fenced block in its background refused; one with two links refused; one leaving out a unit refused, naming it; an update giving options, a `code` artifact, a fenced background or a second link refused. A `text` card under `proposal/1` and a verify key refused for asking in words. A post under `batch/3` records `On batch/3` and `Key batch/3`; one under `batch/3-2` still records as before. Update the opening comment's sentence on a batch card's form.

**2.4** In `form_refusal`, for the batch row: `context.links` a list of more than one entry adds "links more than one session; a batch has one reading session", on a post and on an update that gives links. Add "saying what it is" and "one link to the batch's reading session" to `FORMS["batch"]["says"]`, and the link check to the module docstring's list of what a change is checked for.

**3.1** In `plan.py`: `batch_folder(label, n)`, `reviews(label) / f"batch-{label}-{n}"`. `card_of`: a `batch/<n>` key refuses a unit, in the words of *One session per batch*, and needs none; a `batch/<n>-<k>` key needs one, as today. `card_session` for `batch/<n>`: refused on any host but the partition's main level's (`fleet["partitions"][label]["machine"]`), naming it; under the key folder's lock, while no session serves, write the folder afresh (remove the files crew wrote there before, then `00-summary.md` from `batch_file`, then each unit's Markdown files as *The batch's folder* names them, read at the batch's commit from `t["kit"]["main"]` on its team's host, through ssh with `BatchMode=yes` when that host is another); a file, a host or the summary crew cannot read refuses, naming the unit, the host and what failed, with no session started. Then start plannotator on the files in order, as one argument each, and record `document` as the realpaths joined by ", ". `serving` compares a listed target split on ", " path by path with the recorded document split the same way, so one file's session is judged as before. The row's `doc` for a batch becomes the batch's number, read by `card_session`. `batch/<n>-<k> <unit>` keeps today's path through `change_folder` and `forward_card`.

**3.2** `card_wait` and `card_end` for `batch/<n>` act on the key's own folder on this host, with no unit and no forward; for `batch/<n>-<k>` as today. In `plugin/hooks/cards` `main`, a close of `batch/<n>` ends its session in the hook through `plan.end_session(label, key)`, as for a proposal's, saying so as additional context when it keeps one; a close of `batch/<n>-<k>` still starts `crew card end` apart. `card_folder` already reads `batch/<n>` as a key's own folder and `batch/<n>-<k>/<unit>` as a unit's; update `card_session`'s, `card_of`'s, `card_wait`'s, `card_end`'s and `end_session`'s docstrings and the hook docstring's sentence on a batch card's sessions.

**3.3** `tests/t-batch-cards.sh`: `crew card session batch/1` on the main level's host writes the batch's folder with `00-summary.md` first and each unit's files named `<kk>-<unit>-…`, read at the batch's commits from two teams' hosts, and starts one session whose stub-plannotator arguments are those files in that order; run again, it prints the same link and starts nothing; `batch/1 x1` refused as a batch with one session; on another host refused, naming the main level's host; a team's host that does not answer refuses, naming it, with no session; `card wait batch/1` and `card end batch/1` act on it; the card's close through the hook ends it. A batch whose record holds a post under `batch/1-1` still starts, waits on and ends that key's per-unit sessions. `tests/t-card-sweep.sh`: the batch card's session is one, `batch/1`, on the main level's host, ended by the sweep once its card is closed. Run `tests/moon-tasks` and commit `tests/moon.yml` if a test's `# Reads:` line changes.

**4.1** In `plugin/roles/planner.md` *Batches* step 2: one card per batch, keyed `batch/<n>`, naming every unit with its team; kind `fyi`, intent `heads_up`; title, summary, background and links as the design says, the summary's words quoted; never a choice of units, a question, an approval or an attachment. Start the one session with `card session batch/<n> --label {{LABEL}}` and wait on it with `card wait batch/<n> --label {{LABEL}}` as a background command; the annotations sent from it go at once, word for word, to the conductor of each unit they speak of, by the file each names or what it says, to every unit's when one names none, saying so; approved with none means fine; neither answers or withdraws the card. Step 3: when the user sends the card, its note goes the same way; close the card with `ack_answer` naming where notes went. Drop "of at most five units", "which need notes?", "one in words for the notes", "send each picked unit's notes", "A unit not picked is fine", and every per-unit `card session` and `card wait`. In *Cards*, the batch's card in one sentence beside the proposal's. The worktree holds an uncommitted edit of this file from an earlier code stage, with one session per unit: write the brief from this note, not from that edit.

**4.2** In `plugin/roles/reviewer.md` *The summary*: each unit's section opens with a paragraph of a few sentences saying what the change does and what the user would most care about, which the planner puts on the card; the rest follows as paragraphs and plain lists that wrap on a phone, with no code block and no table; its Touches names what the change edits in words, never as paths; "the planner posts the batch's cards" becomes its one card.

**4.3** In `plugin/lib/crew.py` `cards_how`: the sentence that a batch card's session is started "once for each of its units" becomes one session on the batch, `card session batch/<n>`; after the sentence on withdrawing a card answered in its session, add that a batch card's session holds the batch's notes, so a decision in it is never the card's answer and the card stays open until the user sends it, as the planner's brief says.

**4.4** In `README.md`: the rail-cards paragraph's "each card of a review batch" becomes each review batch's one card; its forms sentence adds a batch's, one notice that says what it is, names every unit, asks nothing and links one session, sent back with one tap, its notes the session's annotations and the card's note; "A batch's card is checked for its key alone, not yet for its form" goes; its `batch/<n>-<k>` key becomes `batch/<n>`. The card-sessions paragraph's last sentence says a batch card has one session, `crew card session batch/<n>`, on the batch's folder on the main level's host, the summary and every unit's Markdown files at its commit, opened as one review; a batch posted under `batch/<n>-<k>` keeps its per-unit sessions. The batches paragraph says the planner posts the batch as one card. In `plugin/skills/crew/SKILL.md`, the card session row's "a batch card's for each of its units" becomes a batch card's one, on the whole batch, and the `[<unit>]` is for an old batch card. In `plugin/bin/crew`'s usage for `crew card`, the same.

**4.5** In `tests/t-briefs.sh`, replace the batch wants with the new phrases: `card session batch/<n> --label wldn`, `card wait batch/<n> --label wldn`, `keyed \`batch/<n>\``, kind `fyi`, "This is batch", "Nothing to answer and nothing to approve.", the notes to each unit they speak of, the words naming none to every unit, the reviewer's opening paragraph and "no code block", and `cards_how`'s new sentence. Add `lacks` for "of at most five units", "which need notes?", "one in words for the notes", "A unit not picked is fine" and `card session batch/<n> <unit>`. Then run `tests/suite --affected` and see it green.

# Design: a proposal's card shows the change and lets new units be left out

## Context

Record 0018 settles a proposal's card and what crew does with each answer; `plan.3`, `briefs.9` and `briefs.13` are already amended to it, and `_open.md` lists this unit as what builds them. The card the user approved is in the Flywheel site spike's exploration (`agentplot/flywheel-next:openspec/explorations/bolt-plan-change-diagram/proposal-card.md` at 3bf57919, with `examples/measurement-pages.card-request.json`, the card as sent, and `gen.ts`, its generator). `gen.ts` is the reading of what the picture, the text and the card's words are, not code crew ships: it is Bun with a headless Chromium, and crew is Python with the standard library (`code.1`).

Today the planner posts a proposal's card itself, an `approve` card whose words are the case and a line per change with the plannotator session's link first (`planner.md` *Cards*; `crew.py` `cards_how`), and crew's card hook refuses a proposal's card that is a grouped card of questions or has options (`plugin/hooks/cards` `FORMS`). An approval applies every `Do` (`plan.py` `plan_approve`, `apply_all`).

Pending You, as its `post_request` tool schema read on 2026-10-11 says, and as the exploration found by trying: a grouped card leaves out the card's `kind`, carries `intent`, an `about` and two to four `questions`, each with its own `id` (`^[A-Za-z0-9_-]{1,40}$`), `kind` (`choice`, `multi`, `approve`, `text`), `title` (8 to 140 characters), `detail` and `rationale` (200 each), and two to five `options`; a card's `summary` holds 400 characters and its `title` 140; an artifact needs `kind`, `title` and `ref`, an `image` with `upload: true` gets an upload URL, and a `code` artifact carries `lang` (`text` among them) and `lines`. Every question is required, so a words question blocks the card; every card has a note in its ⋯ menu. The user can split a card: each question becomes a card of its own, listed under the original's `splits`, and the answers come back on those.

## Goals / Non-Goals

**Goals:**

- crew prints every part of a proposal's card and draws its picture, from the plan and the proposal alone, with nothing installed.
- The user can leave out any unit new to a bolt while approving the rest, and the approval stays one commit or nothing (`plan.3`).
- crew holds an approval until it has every answer of a split card.
- crew refuses a proposal's card in any other form (`roles.3`, `briefs.13`).

**Non-Goals:**

- The animated change, a step at a time, which belongs to crew's page once `the-board-is-a-page` exists (record 0018).
- How an image reaches Pending You, which `an-image-on-a-card-is-uploaded`, merged into this bolt before this unit, puts in the card discipline; this change follows it.
- A batch's card (`a-batch-cards-notes-are-its-note-and-its-sessions`).
- Leaving out a drop, an amendment, an order or a split: those take words, so the user does not approve and says why in the card's note, and the planner writes the proposal again (record 0018).

## Decisions

### The card is drawn from the proposal applied to a copy of the plan

`crew plan card <n>` reads the plan and `proposals.rec` at the branch's tip, as `crew plan proposed <n>` does, and applies the proposal's `Do` lines in order to a scratch copy, as `check_ops` does, to get each bolt's units before and after. It reads no kit (`plan.12`), so the picture shows no stage. A proposal that no longer applies is refused with the command that fails, as the approval would refuse it. A closed proposal is refused.

**What is new to a bolt** is every unit a `unit add` names, to a bolt or to the queue, and every unit a `unit move` puts into a bolt. A split's new parts, a reorder and a move to the queue are not: leaving those out takes words. A unit added to the queue counts because the proposal is the first the user hears of it.

**The counts** are: dropped (`unit drop`, and each unit of a `bolt drop` without `--requeue`), amended (`unit amend`), new (as above), moved (`unit order`, `unit after`, `bolt order`, a `unit move` out of a bolt), split (`unit split`); a count of zero is left out.

### crew draws the PNG itself

Pending You shows a PNG and refuses an SVG. Record 0018 lets the picture come from a renderer the kit puts on the host's path, or from crew itself. crew draws it: `code.1` keeps devenv to jq, moon, python3 and recutils, neither mac-studio nor the box has an SVG renderer, and the picture is only rectangles, lines and monospace text, so a raster canvas is enough. `plugin/lib/picture.py` keeps an RGB canvas, draws filled and outlined rectangles, solid and dashed lines and text, and writes the PNG with `zlib` and `struct` (signature, `IHDR` 8-bit truecolour, one `IDAT` of filter-0 scanlines, `IEND`, each chunk with its CRC from `zlib.crc32`). `plugin/lib/font.py` holds a bitmap font: the X11 misc-fixed 6×13 face, which is public domain, drawn at two times (12×26 a character), its glyphs for ASCII, Latin-1 and the few symbols the card uses (`→ … · – ↕ ’ “ ”`), each a hex string of its thirteen rows. A character the font lacks is drawn as `?`.

The picture is 780 pixels wide, twice a phone's width, as tall as its rows need, in the exploration's palette: background `#102b2f`, row `#163a3e`, rule `#2b4a4d`, text `#ede7da`, muted `#a3b4ae`, amended and moved `#c9a227`, new `#8fb9ae`, dropped `#e07b4f`. From the top, with a 28-pixel margin:

- the bolt's name at three times, made bold by drawing it twice a pixel apart, wrapped at its hyphens;
- the counts, each in its colour, joined by ` · `, and under them `<before> units now; <after> once approved` in muted (`A new bolt; <after> once approved` for a `bolt new`);
- one row per unit, in the order once approved, with each dropped unit put back where it stood (after the unit it followed). A row is a filled rectangle with its order number in a left column (`–` for a dropped or moved-out unit), its name, its intent in muted wrapped to at most two lines of 52 characters, and a tag at the right: `drop`, `amend`, `new`, `moved`, `out`. A dropped row has a dashed outline in its colour, its name struck through and `Why: <reason>` under it; an amended row shows its old intent on one line struck through in the amended colour above its new intent in the text colour; a new row has an outline in the new colour; a moved-out row is struck like a dropped one, with `to <bolt>` or `to the queue` under it.

A proposal that touches several bolts, or the queue, draws one such section per bolt, in the order its commands first name them, each under its own heading, and one for each kit's queue a unit goes to.

### The change as text

The text artifact is the exploration's `.txt`: the bolt and `<before> units → <after>` (`a new bolt → <after>`), a blank line, one block per command in the proposal's order, a blank line, `ONCE APPROVED` and the numbered order with `+` for new, `~` for amended and `↕` for moved. A block is its heading padded to seven characters and the unit or bolt, then what it says on lines indented seven, wrapped at 33 characters: a drop's reason, an amendment's new intent (three lines), an add's intent (two), a move's `from <bolt> to <bolt>`, an order's `before <unit>`, `first` or `last`, an after's `after <units>` or `after nothing`, a split's narrowed intent and `into <unit>`, a new bolt's goal. A heading longer than six characters (`NEW BOLT`, `ORDER BOLT`, `DROP BOLT`) stands on its own line with the name under it. A name longer than its line wraps at its hyphens. Text cut short ends with `…`. A proposal of several bolts gives one header and `ONCE APPROVED` list per bolt.

### The card's fields

`crew plan card <n>` prints one JSON object: `card`, the `post_request` fields the planner sends as they are; `picture`, where it wrote the PNG; and `session`, true only for a proposal of more than fifteen new units. The planner adds what is its own: `idempotencyKey` (`proposal/<n>`), `areaId`, `session`, `blocking` false and `urgency`. The fields:

- `title`: `Approve the change to <bolt>: <counts>?`, or for several bolts `Approve proposal <n> to <bolt> and <bolt>: <counts>?`, cut by whole bolt names to 140 with `and <k> more`.
- `summary`, three lines in 400 characters: `Proposal <n>, by <planner>` with `, replacing proposal <m>` where it does; `<before> units → <after> once approved: <counts>.`; `Goal: <goal>` of the first bolt, cut by whole words.
- `context.background`: the case whole, then `Changes:` and a line per change as `crew plan proposed <n>` heads it, without its markdown, then, while conductors have yet to agree, who; `trace`, `filesTouched`, `tried` and `links` empty.
- `artifacts`: the picture, `{kind: image, title: "The change, once approved", ref: "proposal-<n>.png", upload: true, caption: "Struck and dashed: dropped, with its reason. Gold: amended, old intent struck above the new. Mint: new."}`, and the text, `{kind: code, lang: text, title: "The change, in text", ref: "proposal-<n>.txt", lines: [...]}`. Neither `ref` is a path (`briefs.9`).
- `intent`: `approve`.

With no new unit, or more than fifteen, the card is a plain approval: `kind: approve`, `approve: {action: "Apply proposal <n>", risk: low, reversible: true}`, `recommendedIds: ["approve"]`.

With one to fifteen it is grouped: `about: {kind: other, title: "Proposal <n>: <bolt>"}` and `questions`:

- `plan`, kind `approve`: title `Approve the change to <bolt>?`; detail the case as bullets, one `• ` per sentence, as many whole ones as fit in 200 characters; rationale `To keep the dropped unit or change the amendment, don't approve: say why in a note from ⋯, and the planner writes the proposal again. A note beside an approval changes nothing applied.`, naming only what the proposal does, or `To change it, don't approve: say how in a note from ⋯. A note beside an approval changes nothing applied.` when it drops and amends nothing (record 0018 item 6: approving with a note never holds back a drop or an amendment, so the rationale never says a note objects); `approve: {action: "Apply proposal <n>, with the new units you keep", risk: low, reversible: true}`; `recommendedIds: ["approve"]`.
- `units-1` to `units-<g>`, `g` being the new units divided by five rounded up, the units in the proposal's order shared out as evenly as can be (seven make four and three, eleven four, four and three), so every question has two to five options. Kind `multi`; title `Which new units go in? Clear one to leave it out.`, with ` (<k> of <g>)` when `g` is more than one; rationale `A cleared unit is not added; the rest of the proposal still applies.`; one option per unit, `id` and `label` its name (the label cut to 80), `detail` its intent cut to 200, `consequence` `Cleared: not added; the rest still applies`, or for a unit moved in `Cleared: stays in <the queue|bolt x>; the rest still applies`; `multi: {min: 0, max: <its units>}`; `recommendedIds` every unit.
- A lone new unit is `units-1` of kind `choice`, titled `Does <unit> go in?`, its options the unit (labelled `Add it` or `Move it in`, its intent as detail) and `leave-out` (`Leave it out`, with the consequence above), recommending the unit.

No question is of kind `text` (`briefs.13`). The card carries no link: its owner starts no session for it, but for the card of more than fifteen new units, which links the session on the proposal's page as `briefs.9` says, its link first in summary and background.

### An approval leaves out what only the cleared units concern

`crew plan approve <n> --clear <unit>...` checks each cleared unit is new to a bolt in proposal `n` (as above), else refuses naming the units it may clear. Each `Do` names a set of units: its subject unit and every unit it refers to, `--after`, `--before`, `unit after`'s units, `unit order`'s `--before`, `unit split`'s `--into`; a bolt command names none. A `Do` whose units are all cleared is left out. A `Do` left in that names a cleared unit refuses the whole approval: `` `<do>` names <unit>, which the user left out: write the proposal again without it `` (`plan.3`). The rest are applied in order by `apply_all`, under the same checks and in the same one commit, and a refusal changes nothing. So a cleared `unit add` makes no unit, and a cleared `unit move` leaves the unit where it was.

The approved proposal holds one `Cleared: <unit>` per cleared unit, after `Closed`. `proposals.rec`'s `%allowed` gains `Cleared`, and since a branch's file carries the header it was created with, the approval brings the `Proposal` descriptor in step with crew's own before it writes, as `in_step` does for `plan.rec`. The commit's subject is `plan(proposal <n>): approve: <summary of what applied>`, its body `Left out: <units>`, and the `plan.approve` entry names every object the proposal names, the cleared units among them, so `crew trace unit/<cleared>` shows the approval that left it out; who left it out is the approval's agent and session, as for any approval (`roles.2`).

### crew gathers a card's answers on the planner's host

A card can come back in pieces: split, each question is a card with its own answer, and the planner is woken for each. `crew plan answer <n> <question> <answer>... [--note "<text>"]` records one answer:

- `plan approve` or `plan decline`;
- `units-<k> <unit>...`, the units the user left ticked, none when every one is cleared; for a lone unit's choice, `units-1 <unit>` or `units-1 leave-out`.

It checks the question against the card `crew plan card <n>` would print now (its questions and their units, computed, not stored) and refuses a question it does not ask, a unit its question does not hold, a second answer to a question that differs from the first (the same answer again is fine), and a closed proposal. It keeps what it holds in `~/.local/state/crew/cards/<label>/proposal/<n>/answers.json` on the host it runs on, beside the card's session files: the planner's host, which is where the planner reads its cards. This file is a card's working state, like the session files, not the plan's (`state.2`): it is never on the branch, and if it is lost the planner records the answers again from the card, which Pending You still holds.

Once it holds `plan approve` and an answer for every `units-<k>`, it runs the approval as `crew plan approve <n> --clear <the units not ticked>` and removes the file. On `plan decline` it applies nothing, removes the file and prints that the decline and its note are the user's word for the planner to act on, writing the proposal again with `--replaces` or dropping it. Until then it prints the questions it waits on and applies nothing. `plan answer` runs the approval's `may_write` check as `plan approve` does: any caller, by design (`roles.2`), on the user's word.

### A note beside an approval follows it

A note never holds an approval: the user chose to approve (record 0018). `--note` is kept with the answers and, once the approval is applied, printed: `The user's note beside the approval of proposal <n>: "<note>". Propose what it asks as a new proposal.` A note beside a decline is printed the same way with the decline. Nothing of the note reaches the run record (record 0005: no card's words are recorded).

### The hook checks a proposal's card against the proposal

`FORMS` gives way, for `proposal/<n>`, to a check of its own in `plugin/hooks/cards`, called by `form_check` before `post_request`. It computes the card's questions as `crew plan card <n>` does (one fetch of the branch, `plan.12`) and refuses, naming what is wrong and the form to use:

- a proposal with no new unit, or more than fifteen: anything but an `approve` card with no options, steps or questions;
- one with one to fifteen: a card with no `questions`; a first question not `plan` of kind `approve`; any other question not `units-<k>` of kind `multi`, or `choice` for a lone unit; any question of kind `text`; and unit questions whose option ids, `leave-out` aside, are not the proposal's new units, each exactly once, naming each missing or extra unit;
- in either form, steps for the user.

A proposal crew cannot read is refused, saying to post again later, as every check the hook cannot make is (`read.1`). An update to a proposal's card is checked as today: no questions, options or steps given by a change. The conductor-agreed update changes only words.

### The briefs

`planner.md` *Cards*: a proposal's card is what `crew plan card <n> --label <label>` prints; post `card` as it is with the row's key and your own fields, upload the picture from `picture` as the card discipline says for an image, and start a session only when `session` is true. When the user answers, from the card or a card split off it, run `crew plan answer <n> <question> <answer>` for each question answered, with `--note` for the note, and act on what it prints; close the card and each split with `ack_answer` once crew has applied or declined. Step 3 of *Proposals* says the same for an answer in the pane: `crew plan approve <n>`, with `--clear` for each unit the user leaves out. The sentence "An approval applies the commands exactly as the user read them" becomes "the commands the user read and kept". `cards_how` in `crew.py`: a proposal's card carries no session link unless `crew plan card` says it needs one; the paragraph that has every card that asks the user to read link a session names the proposal's exception; and the paragraph `an-image-on-a-card-is-uploaded` added, which has a card carry an artifact only for a picture or a document's substance as Markdown, names a proposal's card's picture and text, as `crew plan card` gives them.

That unit's `rail-cards` delta adds the requirement that a card carries no artifact but such a picture or such Markdown, which the proposal's text block, a `code` artifact of lang `text`, would break. The text is plain text on purpose: it is the monospace block of at most forty characters a line that record 0018 item 4 names and the user approved on the phone (the exploration's `measurement-pages.card-request.json`), where Markdown would wrap it and set it in proportional type. So this change's `rail-cards` delta modifies that requirement to name the proposal's text as the one other artifact a card carries, and the whole-document link as not a proposal's.

### Docs

README's *Proposals* gains `crew plan card` and `crew plan answer`, and `crew plan approve <n> [--clear <unit>...]`; its card paragraph says a proposal's card is drawn by crew and links no session. The crew skill's sentence on proposals and `crew`'s usage header name the same (`docs.2`). Nothing under `docs/` is edited (`docs.7`).

## Risks / Trade-offs

- **The split's answers.** That each split keeps its question's `id`, and that the planner can tell which question a split answers, is read from the exploration's one accidental split, not from Pending You's reference. If a split loses the id, the planner still knows the question by its title and options, and `crew plan answer` checks what it is given against the card. → *Proof in dev* reads it on a real split.
- **A bitmap font at two times** is coarser than the exploration's vector text. It is legible at a phone's width, and it needs nothing installed. → *Proof in dev*: the user reads it on the phone.
- **Answers on one host.** The planner runs on one host and reads its cards there; a planner moved mid-card loses the gathered answers and records them again.
- **The archive's order.** The `rail-cards` delta modifies a requirement `an-image-on-a-card-is-uploaded` adds, so that change is archived first; `openspec validate` says the archive would refuse this delta until then. → Whoever archives this bolt's changes takes the image unit's before this one.
- **A card posted before this lands** is in the old form; the hook checks only new posts, so it stays until it is answered.

## Proof in dev

These need a live Pending You and the user's phone; the team's ops works them once the bolt is deployed, with the planner posting a real proposal's card:

- A proposal that adds two units and drops one: its card shows the picture legibly at the phone's width, the text block without wrapping, the case under the approval, and two units ticked; the user clears one and approves; the plan holds the other and the drop, and the cleared unit is nowhere.
- The same card split by the user: the planner records each split's answer with `crew plan answer`, crew waits for the second, then applies; read on the splits whether each keeps its question's `id`, and write what Pending You returned into the bolt's proof file.
- A note beside an approval reaches the planner's pane after the approval is applied.

## Task notes

### 1.1

`plugin/lib/font.py`: generate it once from `6x13.bdf` in the xorg `font-misc-misc` source (public domain, "Public domain font. Share and enjoy."), with a throwaway converter that is not committed; the file says where the glyphs came from and their licence. One dict from character to a 26-hex-digit string, thirteen rows of six bits held in the high bits of a byte. `plugin/lib/picture.py`: the canvas and PNG writer, standard library only (`code.1`), with a `draw(sections, counts, …) -> bytes` entry the card's code calls; no I/O but the bytes it returns.

### 1.2

In `plan.py`, beside `describe`: one function that turns proposal `n` at the tip into the card's model (each touched bolt's units before and after, each command's kind and words, the new units, the counts), applying the `Do` lines to a scratch `Write` as `check_ops` does, and from it the text lines, the `card` fields and the picture. `crew plan card <n> [--label L]` (parser, `COMMANDS`; no `ACTS` entry, it records nothing) writes `proposal-<n>.png` under `CARDS / label / "proposal" / str(n)` and prints the JSON. Refuse a closed proposal in `fail()`'s words (`code.2`). Check every length against the limits in *Context* in the code, so a long intent is cut, never sent too long.

### 1.3

`--clear` on `plan approve` (`nargs="+"`, repeatable). Compute the kept `argvs` once from the proposal, check the cleared names, then hand the kept list to the existing `change` and its `prepare` loop, so a kept move still rebases and a refused approval undoes it. `Cleared` in `PROPOSALS`' `%allowed`; bring the file's `Proposal` descriptor in step in the approval's write. `crew plan approve` with no `--clear` is byte-for-byte today's.

### 1.4

`crew plan answer` (parser, `COMMANDS`, `ACTS` `plan.approve` only when it applies; a recording that applies nothing writes no entry). The answers file is JSON `{"plan": "approve", "units-1": ["b"], "note": "…"}`. Remove it on apply or decline; `card end` and the hook's session ending leave it alone, since they remove only empty directories.

### 2.1

Replace `FORMS["proposal"]` with the proposal check in *The hook checks a proposal's card against the proposal*, reading the card model through `plan` as `key_refusal` already imports it. Keep the update path as it is.

### 3.1

`planner.md` and `crew.py` `cards_how` as *The briefs* says. `tests/t-briefs.sh` pins "crew plan card", "crew plan answer", "--clear" and "links no session" in the planner's brief (`tests.6`); drop any pinned phrase the change removes.

### 4.1

`tests/t-proposal-card.sh`, new, its opening comment saying what it proves, sourcing `lib.sh` through `${TESTS:?…}` (`tests.2`). Build a plan with a bolt of four units and proposals for each case. Assert from `crew plan card`'s JSON: the title and counts; the summary's lines; the text lines, each at most forty characters, the `DROP`, `AMEND`, `ADD` blocks and `ONCE APPROVED` marks; the questions for none, one, two, seven and sixteen new units; the `plan` question's rationale, word for word, for a proposal that drops a unit and one that drops and amends nothing; no `text` question; no path in any field. Assert the PNG by reading it with Python in the test: its signature, a width of 780, a height that grows with the rows, and pixels of the dropped and new colours present. Run with no browser and nothing but devenv on the path.

### 4.2

`tests/t-proposals.sh`: approve with `--clear` (a new unit left out, a queued unit moved in left out and still queued, `Cleared` on the record, one commit), refused for a kept `--after` naming a cleared unit and for a unit that is not new, nothing changed; `crew plan answer` waiting on a unit question, then applying, a decline, a different second answer refused, and the note printed after the approval.

### 4.3

`tests/t-cards.sh`: a proposal card posted as `crew plan card` prints it passes; one missing a new unit, one with a `text` question, and a plain approval for a proposal with new units are refused with the form named; a plain approval for a proposal with no new unit passes, as before. Then `tests/moon-tasks`, commit `tests/moon.yml`, and `tests/suite --affected` ends with "0 failed".

### 5.1

README, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew`, as *Docs* says; `tests/t-docs.sh` holds every command README names in the usage.

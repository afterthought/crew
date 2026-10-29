# Design

## Context

See proposal.md for why. The design rests on record 0043 (accepted 2026-10-28) and `briefs.13` as it amends it, on flume record 0007 and clause 129 of Flume's requirements (agentplot/blueprints `design/flume/requirements.md`, with 43, 123, 128 and C.7), and on sluice record 0045 for what a preview is.

What crew does today:

- A landings row is read on its team's host (`plan.land_row`), which asks sluice for a preview of the bolt's head when the kit's policy there declares `[preview]` (`landing_preview`, `preview_ask`, `preview_step`), hands `crew _preview <label> <bolt> <head>` to a process of its own, waits up to twenty seconds for sluice to name the addresses, and records its ask at `~/.local/state/crew/previews/<label>/<bolt>.json`. The preview stays up until the bolt leaves the card (`land_end`, `landing_held`, `crew bolt land`) or the rail sweep finds its card closed (`card_sweep`). A moved head releases the old one and asks a new one.
- `cards.preview_said` turns a preview into the row's words and links; `landing_card`, `row_paragraph` and `landings_card` carry them.
- The batch card (`cards.batch_card`) is raised on the partition's main machine from the run record and the reviewer's summary (`batch_facts`, `raise_batch`). It carries nothing a stage made.
- The conductor's wait (`plan.stage_wait`) runs on the team's host and looks at the stage's place every few seconds until the stage ends.

sluice 0.51.3, read on mac-studio on 2026-10-28 (`sluice preview --help`, `sluice release --help`, `crates/sluice/src/preview.rs`): `sluice preview <branch> <revision> [--wait] [--json]` brings up a running copy of a revision a branch has landed and holds it until `sluice release <name or revision>`. It refuses a branch no `[branches]` table names ("no [branches] table in .config/sluice.toml on <branch> names it"), a revision the branch has not landed, and a revision whose policy has no `[preview]`. One revision has one preview on the host; asking again gives it back. `sluice previews --json` lists every preview with its branch, revision, name, addresses and state.

Area pages this change touches: `plan.md` (`plan.py`), `teams.md` (`plugin/bin/crew`), `briefs.md` (`plugin/roles/`), `tests.md` (`tests/`), `docs.md` (`README.md`).

## Goals / Non-Goals

**Goals:**

- Every card about a stage's work carries what the stage's run recorded as made, as written (`briefs.13`, record 0043).
- No preview is held while a card sits: it comes up on the user's ask and goes on their done or the card's end.
- Each card's facts proved by a test.

**Non-Goals:**

- Telling a stage's agent to write `made.jsonl`. No stage of crew's declares what it makes, and Flume renders the path into the prompt as `{{made}}` once crew runs stages through it. Until a brief or Flume tells a run where, a crew stage writes no line, and its card carries none (record 0043: "a stage that writes none gives its card no link").
- Reading Flume's `made` from `flume status` or a stage's end. That replaces the reading of `made.jsonl` when crew runs stages through Flume.
- Made lines on the landings card. Record 0043 gives a landings row the bolt branch and head; a unit's made lines are on its batch's card.
- Any change to the run record. An entry holds no text anyone typed (run-record spec), and a made line is the run's text.

## Decisions

### Decision 1: `made.jsonl` is read in the place's own git directory

Until crew runs stages through Flume, crew reads `made.jsonl` at `$(git -C <place> rev-parse --git-dir)/made.jsonl`. Flume's clause 128 puts it in "the place's own folder beside its held state", which crew has no equivalent of. The git directory is the place's own, and it goes when the worktree is removed, as Flume's C.7 keeps what readiness makes for a place. It is also out of `git status`.

Alternatives: the place's root, which is the most literal reading of "in the stage's place", but an untracked file there makes `git status --porcelain` dirty, so the tidy keeps the place (plan.py `tidy`, `plan.9`) and a dependent's rebase refuses it (`clean`); a folder under `~/.local/state/crew/`, which outlives the place, against clause 129's "the lines go with the folder".

### Decision 2: a line is read as written, and shown as written

A line is one line of the file. crew reads it as a JSON object holding `name` and `kind`, with `address` for a durable thing, or `branch` and `revision` for a thing that must run, the field names flume record 0007 gives `made` ("each a name and kind with … its address, and … the branch and revision that bring it up"). crew shows each field's text as it is, cut by `cards.by_words` only where a card's budget demands, and checks nothing about an address: no URL check, no reachability check (`read.2` guards an absent field so it never becomes text; it asks no check of a present one). A line that is not such an object is carried as its text, saying crew could not read it as a made thing, and refuses nothing. A line holding both an address and a branch is a durable thing with its address shown, and its branch and revision shown beside it.

The made lines go into the card's words: the batch card's face Markdown, under each unit's paragraph, and its details. They do not become link artifacts: a card has at most eight (`cards.ARTIFACTS`), and a link artifact Pending You refused for an address crew did not check would refuse the card.

### Decision 3: the conductor's wait keeps a copy, on the team's host

The place goes at the tidy after the unit merges, often before its batch's card is answered. Flume's answer is that "a caller that wants them after keeps them, as it keeps a report" (clause 129). The conductor's wait is the caller: at each look, and once more at the stage's end, it reads the place's `made.jsonl` (`made_read`) and appends each line it has not kept to `~/.local/state/crew/made/<label>/<unit>/<stage>.jsonl` on the team's host, byte for byte, under the stage that is running when it first sees it (`made_new`, a decision on plain facts, `code.7`). A line already kept under any stage of the unit is not kept again. The copies are files read by any process, no service (`state.4`), and go at `land_end` for each unit of a bolt that lands or is dropped.

Alternatives: the run record, which reaches the main machine with no ssh, but an entry holds no text anyone typed; reading the place directly at each batch raise, which loses everything once the place is tidied.

### Decision 4: the batch's raise reads the copies from each team's host

`batch_read` on the main machine asks each unit's team's host for its copies, `crew _made <label> <unit>... --json` run through `crew.on_machine` (`code.3`), one call per host, as `CardActs.land_row` reads a landings row on its team's host. A host that does not answer is named on standard error and its units carry no lines this raise (`read.3`); nothing is refused, since the batch stands. A host is read only for its kits' places' facts (`read.5`).

When the wait keeps a new line for a unit in a batch whose card is open (`batch_open`, from the branch's entries), it hands `crew _batch-card <label> <n> --note "<unit> recorded <name>"` to the partition's main machine, as `land_hand` hands the landings card. `raise_batch` then changes the card in place through `row_card_change`, which leaves a card the user answered as it is.

### Decision 5: the landings row carries the branch and head; nothing is asked at its post

`landing_preview` stops asking sluice. It reads only whether the kit's policy at the head declares `[preview]` (`head_previewed`, as today) and gives the row one of: `{branch, head, state: "ask"}`, the preview's branch and head with no addresses; `{head, none: True}`, which the row says as "no preview"; `{head, why}` when the policy can't be read (`read.1`); or, when crew's record holds a preview brought up from this card at this head, that preview as sluice lists it. `preview_step` loses `ask` at the raise: it keeps a recorded preview at this head, releases one at another head (`replace` becomes `release`) or with no `[preview]` now, and asks nothing.

### Decision 6: the user's ask is their words on the card, and the owner runs `crew card preview`

Pending You lets the user write on a card that still waits on them, and wakes its owner's Claude Code session when they do (Pending You guide 2.59, "Hear the answer": "When they answer, write to you, … a turn starts that names the card"; "They asked you something on a card that still waits on them … answer with `reply_in_thread`"). A card's options are its answer, so a box or a choice cannot ask for a preview without answering the card. The user's ask is therefore their own words on the card, and the card says so: "To try it running, write on this card naming it; it is put away when you write that you are done, or when this card closes." This is a word of the user's that the owner acts on (`roles.2`); no card asks the user to run a command (`briefs.13`).

The owner, main-level ops for `land/<kit>` and the planner for `batch/<n>`, replies in the thread first, as Pending You asks, then runs `crew card preview <key> <thing>` or `crew card preview <key> <thing> --done`. The command:

1. Reads the card's thing from crew's own facts (`preview_target`, a decision on plain facts): a landings row's bolt branch and current head, or a batch line's branch and revision from the unit's copy. It refuses a thing the card does not carry, naming those it does, and a caller other than the card's owner, naming the owner (`code.2`).
2. Forwards to the team's host (`code.3`) and, there, under the partition's previews lock, asks sluice as `preview_ask` does today: `crew _preview <label> <key> <thing> <branch> <revision>` handed to a process of its own (`code.9`), sluice's previews read up to twenty seconds for the addresses, crew's ask recorded at `~/.local/state/crew/previews/<label>/<key with / as ->/<thing with / as ->.json`. Asked again at the same revision, it keeps the one it has.
3. Changes the card in place on the main machine (`land_hand`, or the batch's hand of Decision 4) with a note naming the thing and whether it is up, coming up or failed.

`--done` releases the recorded preview (`preview_release`, which runs `sluice release <name> --json` in the kit's main checkout and removes crew's record), then changes the card in place to carry what brings it up again. A preview's end changes the card as today (`preview_change`).

`sluice preview` refuses a branch no `[branches]` table names, so a line naming a unit branch is refused and the card says so in sluice's words. crew does not check for it first: the run wrote the branch, and sluice owns what it previews.

### Decision 7: releases

A preview crew brought up from a card is released by `--done`; by `land_end` (landing, drop) and `landing_held` (fix), as today; when a batch card closes, by the close's own act on the main machine handing `crew _preview-release <label> batch/<n>` to each host holding one; when a merge moves a landings row's head, by `land_row`'s `preview_step`, which now releases and asks nothing; and by the rail sweep (`card_sweep`) for a recorded preview whose card is closed or whose row is gone, as today, now over every key's records, not only `land/`. One revision has one preview on a host, so crew releases a preview only when no other record of crew's on that host names the same revision; the last record to go releases it. crew releases only previews it recorded (`read.4`).

### Decision 8: the briefs

`main-ops.md` and `planner.md` gain one paragraph each: when the user writes on a card of theirs asking to bring a named thing up or saying they are done with it, reply in the thread, then run `crew card preview <key> <thing>` (or with `--done`), and tell the user what crew said if it refused; a word for a preview answers nothing on the card. `conductor.md`'s landings paragraph says the row carries the bolt branch and head, the preview comes up only on the user's ask and goes on their done or at the landing, and a moved head releases one up at the old head.

### Decision 9: a landed revision's card

The deploy card names its commit already (`deploy_card`), and the landing's close names the commit GitHub's main holds (`landed_words`). Neither gains a preview; tests pin both, as record 0043 asks ("a card about a landed revision carries the commit it landed as and no preview of its own").

### The agents' views

`board.agent_views` and `plugin/hooks/status.js` draw rail rows and cards by key and state, not a card's words, and draw no preview today; nothing they draw moves (`code.8`, "not ruled out: a change that moves nothing the views draw").

### Rules relied on

`briefs.13` (as amended by record 0043), `roles.2`, `roles.5` (reading `made.jsonl` is the stopgap record 0043 names, retired when crew runs stages through Flume), `state.4`, `read.1`, `read.2`, `read.3`, `read.4`, `read.5`, `code.2`, `code.3`, `code.7`, `code.8`, `code.9`, `plan.9`, `docs.2`. No rule is departed from.

## Risks / Trade-offs

- [No crew stage writes `made.jsonl` yet] → The batch card carries made lines only once a run writes them; this change is the reader, named as such in the Non-Goals and for the design agent.
- [A landing row's preview takes up to twenty seconds after the user asks, and longer to come up] → The card changes in place as it comes up, as today's preview does; the landing waits on nothing.
- [Two cards asking one revision share sluice's one preview] → crew releases it only when its last record of that revision goes.
- [The batch raise reads every team host] → One call per host, a silent host named and its units carried without lines.
- [The user's words may name a thing loosely] → The owner names the thing to crew; crew refuses one the card does not carry and lists those it does, which the owner can say back in the thread.

## Migration Plan

A landings card open when this lands still lists the addresses of a preview crew asked for at its post. The first `land_row` after the landing finds crew's record of it under the old path (`previews/<label>/<bolt>.json`), releases it (`preview_step`'s `release`, since nothing asked it from the card), and changes the row to carry what brings it up. No preview is left held.

## After deploy

None: every behaviour is proved by the logic tier and the land journey in the worktree, and the migration runs itself at the first rail read.

## Task notes

**1.1** `cards.py`: `made_line(text)` parses one line into `{name, kind, address?, branch?, revision?}` or `{text, unread: True}`; `made_said(unit, stages)` gives the Markdown lines under a unit, `stages` `[(stage, [line])]`, a durable thing as "`<stage>`: <name>, <kind>, at <address>", a running one as "… brought up from <branch> at <revision>; write on this card to bring it up", one up with its addresses, one unread as its text. Cases in `tests/py/test_made.py`: a page, a preview, both fields, a non-object, an object missing `kind`, a line with an empty address (shown empty, never "None").

**1.2** `plan.py`: `made_read(place)` reads `<git dir>/made.jsonl` (git's `rev-parse --git-dir` in the place) as a list of lines, `[]` when absent, a `Refusal` naming the file when unreadable; `made_new(kept, lines, stage)` returns the lines to keep under `stage` given every line kept for the unit (Decision 3); `made_keep(label, unit, stage, lines)` appends. `stage_wait` calls them each look and at the end, saying a refusal on standard error. Cases in `tests/py/test_made.py`: once per line across looks, the stage first seen, a duplicate line under two stages kept once, nothing for a place with none; the contract tier is not needed, `rev-parse --git-dir` already being read in `plan.py`'s `kit_git` paths.

**1.3** `plan.py`: `crew _made <label> <unit>... --json` prints `{unit: [[stage, [line]]]}` from the copies; `batch_read` gathers them per host (Decision 4) into `facts["units"][i]["made"]`; `cards.batch_card` puts `made_said` under each unit's paragraph on the face and in the details. `land_end` removes the copies of the bolt's units. Cases in `tests/py/test_cards.py` (`batch_card` with and without made lines, a silent host) and `tests/py/test_made.py` (the copies removed at `land_end`).

**1.4** `plan.py`: when `made_keep` keeps a line for a unit in a batch whose card is open, the wait hands `_batch-card <label> <n> --note` to the main machine (`batch_hand`, modelled on `land_hand`); `_batch-card` runs `raise_batch` with the note. Cases in `tests/py/test_made.py` with a stand-in `CardActs`: changed in place while waiting, left as it is once answered (`row_card_change`'s own rule).

**2.1** `plan.py`: `landing_preview` and `preview_step` as Decision 5; `cards.preview_said` gains the `ask` and `none` shapes ("Try it running from bolt/y at abc1234: write on this card to bring it up, and that you are done to put it away. It is not held while the card waits." and "No preview."). `landing_card`, `row_paragraph`, `landings_card` carry them. Cases in `tests/py/test_landing.py`, `test_landings.py`, `test_cards.py`: declared, none, unreadable policy, a recorded preview up at this head listed, the old head released.

**2.2** `plan.py`: `crew card preview <key> <thing> [--done] [--label L]`, its parser beside `card session`, `preview_target` (Decision 6, step 1), the forward to the team's host, `preview_ask` and `preview_release` keyed by card key and thing, the handed `_preview <label> <key> <thing> <branch> <revision>`, `handed_named` matching it. Cases in `tests/py/test_card_commands.py`: the owner brings a row's preview up, a non-owner refused naming the owner, an unknown thing refused naming the rows, `--done` releases and the row asks again, asked twice keeps one.

**2.3** `plan.py`: releases as Decision 7: `land_row` on a moved head, `card_sweep` over every key's records, a batch card's close handing `_preview-release`, the shared revision kept while another record names it, and the migration of an old `previews/<label>/<bolt>.json`. Cases in `tests/py/test_rail.py` and `test_card_commands.py`.

**2.4** `tests/t-journey-land.sh`: the row is posted with sluice's stub asked for nothing; ops's `crew card preview land/<kit> <bolt>` brings it up and the card lists the stub's address; `--done` releases it and `sluice previews` lists none; asked again, then `crew bolt land` releases it. The comment block at the test's head says the new story; run `tests/moon-tasks` if what it reads changes.

**3.1** `cards.deploy_card` and `plan.landed_words`: cases in `tests/py/test_cards.py` and `test_landing.py` that the deploy card names its commit and carries no preview word or link, and that a landing's close names the landed commit and no preview.

**4.1** `plugin/roles/main-ops.md`, `planner.md`, `conductor.md` as Decision 8; `tests/t-briefs.sh` checks each brief names `crew card preview` (main-ops, planner) and that the conductor's no longer says crew asks sluice for a preview when the row is posted.

**4.2** `plugin/bin/crew`'s usage header, `README.md` and `plugin/skills/crew/SKILL.md` name `crew card preview <key> <thing> [--done]` together (`docs.2`); `tests/t-docs.sh` proves it.

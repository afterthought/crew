# Design

## Context

A bolt lands by main-level ops's procedure: `crew bolt submit <bolt>` hands sluice the bolt's branch from a short-lived worktree on the team's host, and `crew bolt land <bolt>` takes the bolt out of the plan and has `crew _tidy` on the team's host close the conductor's landing card with `landed_words` (`plan.py` `bolt_submit`, `bolt_land`, `tidy_after`, `team_tidy`, `landing_cards_closed`, `row_card_close`). The word to land is the card's approval, which the conductor passes on with `crew tell`, or the user's words in ops's pane (`plan.16`). crew checks neither today: `bolt_submit` takes no words, and `bolt_land` closes the card the same way whatever the word was. A card the user never tapped is withdrawn with "landed on GitHub's main at …", which Pending You shows as withdrawn, not answered.

The batch already has the pattern this change follows. `crew card answer batch/<n> --excerpt "<words>"` (`batch_answer`) reads the words in the caller's own transcript with `transcript.check(sid, words, want="user")`, refuses anything crew does not read as the user's (`pane_answer_refusal`), records `batch.answer` with the transcript record in `From` and the length in `Chars` and no words, and closes the card with the words through `row_card_close(..., said=...)`, recording the outcome without them. Record 0031's amendment of 2026-10-22 says the user's words in a main-level pane land a bolt as they answer a batch, "recorded by crew from that session's transcript as theirs (`signals.5`) and never from an agent's words" (`briefs.12`'s details, as amended that day).

What differs for a landing:
- The words are checked by `crew bolt submit`, which runs where ops runs, but the card is closed later, by `crew bolt land`, on the team's host. The run record can't carry the words between them (`record.3`), so ops's host keeps them for that one step.
- `bolt_submit` runs locally and reaches the team's host only for the submission script, so the transcript is on the host where the check runs, as it is for `batch_answer`.

Rules relied on: `plan.16` (the user's words in ops's pane are a word to land; the card closes at `crew bolt land`); `briefs.11` (crew closes a row's card, never an agent); `briefs.12` as amended 2026-10-22 (a landing in a main-level pane is recorded from that session's transcript as the user's); `signals.5` (who asserted a record, `transcript.asserter`); `record.3` (no entry holds the words); `read.1` (a transcript crew can't read refuses; a word it can't read back is said, never guessed); `roles.2` (a landing is run only on the user's word; crew records who ran it and refuses it by no caller); `roles.4` (a `[crew tell from <agent>]` line is that agent's); `code.2`, `code.7` (refusals through `fail()`, decided by functions of facts tested in the logic tier); `code.9` (the check adds a transcript read to a command already run in the background). `code.8`: nothing the board or the bands draw changes; a `bolt.submit` entry gains `From` and `Chars`, which no view reads.

Pages whose areas this touches: `plan.md` (`plan.py`), `briefs.md` (`plugin/roles/main-ops.md`), `tests.md` (`tests/`), `docs.md` (README, SKILL.md, `plugin/bin/crew`'s usage). `signals.md`'s area is read, not changed: `transcript.check` is used as the batch's change left it. `record.md` is not touched: `From` and `Chars` are already in the descriptor's `%allowed`.

## Goals / Non-Goals

**Goals:**
- `crew bolt submit` takes the user's words from ops's pane, submits only once it reads them as the user's in ops's own transcript, and records that it did without the words.
- The landing card closes naming those words, as answered, so a landing said in the pane reads on the card as one approved there.

**Non-Goals:**
- Checking the card's approval when `crew bolt submit` runs without `--excerpt`. The conductor's tell carries it, as today.
- A landing said in the operator's or the planner's pane. `plan.16` names ops's pane alone; words another agent passes on are refused, naming it.
- `crew bolt land` of a bolt no team holds, on the user's word. It submits nothing, and `plan.16` asks no check of its word here.
- `crew record --settled-in-pane` reading the user's words. It stays as it is.

## Decisions

### 1. `crew bolt submit <bolt> --excerpt "<words>"`, checked before anything is submitted

`--excerpt` is optional: without it the word is the card's, and nothing changes. With it, `bolt_submit` reads the verdict on the words in the caller's own session on this host, as `CardActs.heard` does, before it runs `LANDING` on the team's host. Every refusal comes before the submission, so a refused word moves nothing. crew refuses no caller (`roles.2`). The words must be in the caller's own transcript as the user's, and only ops's brief tells it to pass them.

Considered: a command of its own, as the batch has `crew card answer`. A landing's word and its submission are one act, and a word recorded apart from it could be left with nothing landed. Also considered: refusing callers other than main-level ops. `roles.2` rules out refusing a landing by caller.

### 2. One verdict refusal for a batch and a landing

`pane_answer_refusal`'s verdict branch moves into `heard_refusal(head, v, answers)`, where `head` begins the refusal and `answers` says where the user gives this word. A batch's is "on its card or in one of those two panes"; a landing's is "on its landing card or in main-level ops's pane". `pane_answer_refusal` calls it with its own words, so its refusals are unchanged. `submit_word_refusal(bolt, v)` calls it with `head` "crew submits nothing of bolt <bolt>". It returns `None` only for a verdict `verified` asserted by `user`. No refusal holds the words, since a refused `bolt.submit` records its message (`record.3`).

### 3. The `bolt.submit` entry points at the words

A landing on the user's words records its `bolt.submit` with `From: session/<sid>/<record>` and `Chars: <length>`. The record is the transcript record's uuid, or `line-<hash>` when it has none, as `batch_answer` names it. `By` and `Session` come from `record.emit`. A landing on the card's approval records no `From`, so "landed on the user's words in a pane" is read from the entry alone: `pane_word_of(entries, bolt)` gives `(by, at, frm)` for the last `bolt.submit` on `bolt/<bolt>` that was not refused, when it carries a `session/` `From`, and `None` otherwise.

### 4. Ops's host keeps the words until `crew bolt land`

Once `landing_said` reads the bolt landed, `bolt_submit` writes `~/.local/state/crew/landings/<label>/<bolt>.json` on its own host: `{words, by, at, from}`, the same `from` as the entry's. This is host state, like a preview's record (`PREVIEWS`), and never the run record. `bolt_land` reads it when `pane_word_of` gives a pane word whose `from` matches. It removes the file once the landing is written, whatever became of the card. A file whose `from` is not the last pane landing's is stale and ignored. A missing file on a pane landing means `bolt land` runs on another host than the submission. The card then closes without the words, and the command says the words were kept on the entry's `Host`.

Considered: a second `--excerpt` on `crew bolt land`, checked again. That gives ops two chances to quote differently, and needs a rule for a landing on the card that is passed words. Also considered: closing the card at `crew bolt submit`. `plan.16` closes it at `crew bolt land`, naming the timer.

### 5. The card closes with the words, answered here

`pane_landed(landed, by, at, words)` gives the close's two texts:
- **Recorded outcome:** `Landed on the user's word in <by>'s pane; <landed_words>`.
- **Sent to Pending You:** `Landed on the user's word in <by>'s pane, "<words>"; <landed_words>`. With no words, it is `Landed on the user's word in <by>'s pane at <HH:MM>Z; <landed_words>`.

The word comes first, because `cards.close_call` cuts what it sends to Pending You's 200 characters, and the timer's tail is what should go. `tidy_after` passes both texts, and a flag that the card was answered in a conversation, to the team's host as `_tidy --landed <bolt> --outcome <recorded> --said <sent> --here`. `team_tidy` passes them to `landing_cards_closed`, which passes them to `row_card_close(..., said=, here=)`. `card_closed` passes `here` on to `cards.close_call`. With `here`, a card still waiting is cancelled with Pending You's `answeredHere: true` and recorded `closed`, not `withdrawn`. A card the user also tapped is acked as before.

Vendor read: Pending You's `cancel_request` takes `answeredHere` ("They answered or read it in your conversation"), boolean, beside `reason` (at most 200 characters) and `requestId`. That is from its MCP schema as this session loaded it on 2026-10-22.

### 6. Main-level ops's brief

In *Landing a bolt*, after the two ways the word comes: when the user says it in this pane, step 2 is `crew bolt submit <bolt> --excerpt "<their words, as they wrote them>"`, quoting everything they said of the landing in one message. A refusal is no word to land: say what crew said, and land nothing. Words an agent tells you the user said are never the word. One command per bolt when one sentence lands several.

## Risks / Trade-offs

- [Ops quotes words from an older message than the one that said land] → The check finds the words wherever the user wrote them in the live session. The brief says to quote the message that gave the word, and the card shows the words, so the user sees what was taken.
- [The words file is left when `crew bolt land` never runs] → It holds one landing's words on ops's host, under ops's own state, and the next pane landing of the same bolt name replaces it. Nothing reads it but `bolt land`, which checks its `from` against the record.
- [The team's host runs an older crew that doesn't know `--said` or `--here`] → `_tidy` refuses the arguments, the landing stands, and the card is closed by the next sweep once the plan no longer holds the bolt, as when the host does not answer (`tidied`). Hosts take crew's main together.
- [Pending You treats `answeredHere` differently from its description] → The close still withdraws the card with the words. What the user sees is checked after the first pane landing (*After deploy*).

## Migration Plan

None. Landings before this change have no `From` on their `bolt.submit`, and close as before.

## After deploy

- At the first landing said in ops's pane after this lands, main-level ops reads the closed card in Pending You (`get_request`) and says whether it reads answered, with the words. Pending You's display of `answeredHere` can't be reached by crew's tests. Environment: the main level's host. Doer: main-level ops, once `crew bolt land` of that bolt has run.

## Task notes

**1.1** `heard_refusal(head, v, answers)` holds today's verdict branch of `pane_answer_refusal` (`unverified`, `refused`, `found`, `agent:<name>`, `crew`, `tool`), with `answers` in place of the batch's "on its card or in your pane". `pane_answer_refusal` calls it. Every case in `tests/py/test_batch_answer.py` passes unchanged.

**1.2** `submit_word_refusal(bolt, v)` is `heard_refusal(f"crew submits nothing of bolt {bolt}", v, "on its landing card or in main-level ops's pane")`. Cases in a new `tests/py/test_pane_landing.py`, on `transcript.Verdict`s built directly:
- verified, user: `None`;
- `agent:swancloud-operator`: names swancloud-operator and the two ways;
- refused: "not in a record your session received";
- `tool`, `crew`, `found`, `unverified` with its reason;
- no refusal holds the words.

**2.1** `bolt_submit(fleet, a)`:
1. With `a.excerpt` set, after `locate` and before `crew.on_machine`, get the verdict and session as `CardActs.heard` does (`session_here`, then `transcript.check(sid, words, want="user")`), and `fail()` on `submit_word_refusal`. Blank words are refused, asking for the user's words.
2. On a landing, `record.emit(..., frm=[f"session/{sid}/{rid}"], Chars=len(words))`, with `rid` as `batch_answer` makes it.
3. Then `landing_word_keep(label, bolt, words, who, at, frm)` writes the file of decision 4, under a module path `LANDINGS` beside `PREVIEWS`.

Add `--excerpt` to the `submit` subparser. Cases in `tests/py/test_parser.py` (the flag parses, and is absent by default).

**2.2** `pane_word_of(entries, bolt)` (decision 3) and `landing_word_read(label, bolt, frm)` (words or `None`; refused when the file is there but can't be read, `read.1`). Cases in `tests/py/test_pane_landing.py`:
- a card landing: `None`;
- a pane landing: its `By`, `At` and `From`;
- a refused pane `bolt.submit` after a card one: `None`;
- the file read back in a temp `LANDINGS`, and a stale `from` giving `None`.

**3.1** `pane_landed(landed, by, at, words)` (decision 5). Cases in `tests/py/test_landing.py` `TestTheCardsClose`:
- with words: the recorded outcome holds none of them, and the sent text begins with the word and the quoted words;
- without words: the time, `HH:MMZ`.

**3.2** `cards.close_call(got, card, name, outcome=None, reason=None, here=False)`: with `here` and a pending card, the `cancel_request` arguments carry `"answeredHere": True` and the state is `"closed"`. Cases in `tests/py/test_cards.py` beside the existing `close_call` cases, an answered card unchanged by `here`.

**3.3** Plumbing, in order:
- `card_closed(..., here=False)` and `row_card_close(..., here=False)` pass `here` on.
- `landing_cards_closed(fleet, t, bolt, outcome, said=None, here=False)`.
- `team_tidy` reads `--said` and `--here` (added to the `_tidy` subparser).
- `tidy_after`'s `landed` becomes `(bolt, outcome, said, here)`, with `--said`/`--here` added only when given.
- `bolt_land`, once `pane_word_of` gives a word, builds the texts with `pane_landed` from `landing_word_read`. With no words, it prints that the words were kept on the entry's `Host`. It removes the file after `tidy_after`.

Cases in `tests/py/test_card_commands.py`, with its stand-in `CardActs`: `row_card_close` with `said` and `here` sends the words and `answeredHere`, and records the outcome without them.

**4.1** `main-ops.md` *Landing a bolt*: the words of decision 6. `tests/t-briefs.sh` checks with `has` for `bolt submit <bolt> --excerpt "<their words, as they wrote them>"` and "A refusal is no word to land" in the main-ops brief. Also:
- `plan.py`'s usage docstring and `plugin/bin/crew`'s header: `crew bolt submit <bolt> [--excerpt "<the user's words>"] [--label L]`.
- README's landing paragraph and SKILL.md's command table name the flag (`docs.2`).

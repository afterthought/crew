# Design

## Context

This change builds on `the-board-opens-a-dock-on-each-item`, ahead of it in the bolt: `page.py`'s `docks(d, fleet, label)` makes one dock page per item, keyed `<kind>:<name>` (`signal:`, `proposal:`, `bolt:`, `unit:`, `fix:<bolt>/<fix>`, `landing:`, `deploy:<env>/<to>/<when>`, `operation:<env>/<key>`, `team:`, `subscription:`), and `page.html` draws `D.docks[key]` in a dock with no foot, holding nothing that answers or sends. That change's own case asserts the page holds no `fetch`; this change replaces that assertion with its own (Task notes 2.1).

`crew tell <agent> "<text>"` is `crew.py`'s `tell(fleet, name, text, sender=record.who())`: it finds the agent's host and session, refuses with nothing typed when the agent is not up, waits on a question or cannot be read (`tell_refusal`, `teams.11`), types `[crew tell from <sender>] <text>` with `herdr agent prompt` on that host, and records a `tell` entry with the text's length, never its text (`record.3`). `record.who()` is `CREW_AGENT`, else `<user>@<host>`. `transcript.asserter` reads a tell whose sender holds `@` as the user's (`signals.5`), and `plan.words_refusal`, which a landing on the user's words (`submit_word_refusal`), a batch answered in a pane (`pane_answer_refusal`) and a record settled in a pane (`settled_refusal`) all rest on, takes a verified excerpt asserted by the user. So today a tell from the user at any host answers: the main-level and review-batches specs say so in their scenarios "Through the rail's answer command".

Record 0038 §3 rules that the dock's word reaches the item's agent as crew's tell in the user's name from the board, naming the item (`[crew tell from <user>@board]`), that the board still answers nothing (record 0010), a card being answered on the rail, and that a word not delivered is said in the dock in crew's refusal words. §4 rules that the listener taking the word is swancloud's, on the board's host, the page posting to its own address and srv's Caddy carrying it there over the tailnet, so crew runs no service (`state.4`). swancloud's unit for it, `the-boards-word-reaches-crew-tell`, is not written yet; this design fixes the one thing it must agree with, what the page posts and what crew's command takes and answers (Decision 2).

Rules this design rests on: `state.4` (no service of crew's; the page writes nothing), `roles.2` and `roles.3` (an answer runs only on the user's word, and the board's not being one is a check, not a brief's wording), `roles.4` (the word is marked as crew's tell), `read.1` and `read.2` (a field missing from the post is refused, never defaulted), `code.1` (standard library; the page's script plain), `code.2` (a refusal through `fail()` or tell's own words, never a traceback), `code.3` (the tell reaches the agent's host as every tell does), `code.4` (the key's kind and the agent are names), `code.7` (routing and the word's check are decisions on plain facts), `code.8` (nothing the agents' views draw moves), `code.9` (the command answers within one tell's time), `signals.5` (who asserted an excerpt), `teams.10` and `teams.11` (every brief carries how to read crew's marks; a tell reaches its agent or nothing is typed), `record.3` (no word's text in the record), `docs.2`, `tests.10` and `tests.11`. The change touches the areas of `teams.md` (`plugin/bin/crew`, `plugin/lib/crew.py`), `signals.md` (`plugin/lib/transcript.py`), `plan.md` (`plugin/lib/plan.py`), `tests.md` (`tests/`) and `docs.md` (`README.md`); `page.py` and `page.html` are under no area page. It departs from no rule.

## Goals / Non-Goals

**Goals:**

- A word typed in any dock reaches the item's agent marked as the user's word from the board, naming the item, or the dock says why not in crew's words.
- Whom each item's word goes to is decided once, in Python, and shown before it is sent.
- A word from the board answers no card, landing, batch or record, by a check in crew.

**Non-Goals:**

- The listener and Caddy's path to it: swancloud's `the-boards-word-reaches-crew-tell`.
- A reply from the agent in the dock: the board answers nothing; the agent answers in its own pane or on the rail as it does today.
- Any change to what an agent does with a word, beyond the briefs' line on who is speaking.
- The fleet page and subscriptions' use: their own units.

## Decisions

### 1. The page decides whom a word goes to; crew checks it by kind

`page.py` gains `word_to(key, d, label)`, a decision on the page's data: the key's kind picks the role (`bolt`, `unit`, `fix` the conductor; `proposal`, `batch` the planner; `signal`, `record` the design agent; `landing`, `deploy`, `operation` main-level ops; any other kind the operator), and for the conductor's kinds the team holding the item's bolt (`<team>-conductor`), else the operator. `docks` sets each page's `to`, which the dock names. Agents' names are crew's own: `<team>-conductor`, `<label>-planner`, `<label>-design`, `<label>-ops`, `<label>-operator` (`crew.py` `main_tokens`).

`crew tell --board` checks the posted `to` against the key's kind by the same table in `crew.py`, on the teams file alone: exactly the role's agent of the posted partition, and for the conductor's kinds any conductor of one of the partition's teams or its operator, since which team holds a bolt is the page's read and not the command's.

Why: the user sees whom the word reaches before sending, and the dock's line is the routing itself, not a guess of it. Re-reading the board in the command to find a unit's team would take seconds of kit reads for each word (`crew rail`'s 2.4 to 4.7 s, record 0010) and decide routing in a second place. The kind check keeps a post from reaching an agent its item's kind does not go to (`roles.3`).

### 2. The listener pipes the post to `crew tell --board`

The page posts `{"label", "key", "to", "text"}` as JSON to `word` relative to its own address (`board.swancloud.net/word` for a page served at `/<label>.html`). The listener passes the request's body, unread, to `crew tell --board` on its standard input, and answers 200 with the command's standard output when it exits zero, and 422 with its standard error otherwise. `crew tell --board` takes no other argument; it reads one JSON object, refuses anything else (`read.2`), checks it (`board_word`, Decision 1 and Task notes 1.2), and calls `tell` with sender `<user>@board` and text `(on <kind> <name>) <text>`, printing `sent to <agent>` on delivery and exiting 1 with tell's words otherwise.

Why: everything about the word, its form, its routing check, its marking, is crew's and proved in crew's tiers; the listener parses nothing and builds no argument list, so swancloud's job stays as thin as the maker that runs `crew page`. It is `crew tell`, as record 0038 §4 names it, with the board as its sender. Considered: the listener building `crew tell <to> "<text>"` with a flag naming the item; it puts the item's naming and the word's checks in swancloud's job, where crew's tiers cannot reach them.

This contract is what swancloud's unit must match; it is named for swancloud's planner and design agent in the commit's message.

### 3. The sender is `<user>@board`

`<user>` is the user the command runs as (`getpass.getuser()`, as `record.who()` takes it), so the listener running as chuck sends `[crew tell from chuck@board]`. `board` names no host: the word comes from the board, wherever the listener runs. `transcript.TELL` already reads such a sender, and `asserter` reads it as the user's (`signals.5`), so a signal an agent captures from the word is the user's, as it should be. The item is named after the mark as `(on <kind> <name>)`, the key's two parts, the same form as crew send's `(sent to <name>)`.

The tell's run-record entry is tell's own, `tell` on `agent/<to>` with the text's length (`record.3`); its `By` is who ran the command, the listener's user at its host.

### 4. A word from the board answers nothing

`transcript.Verdict` gains `board`, true when its source record is a tell whose sender ends `@board`; `check(..., want="user")` takes the last record the user asserted that is not from the board, and a word from the board only when there is no other. `words_refusal` refuses a verified excerpt from the board: `<head>: the words came from the board, which answers nothing; <advice>`, the advice each caller already gives (the landing card or ops's pane; the batch's card or the pane; the record's card or the pane). The three callers and the landing's, batch's and record's refusals are otherwise unchanged.

Why: record 0038 §3 and record 0010 rule that the board answers nothing, and a tell from the user would otherwise land a bolt or answer a batch (the scenarios "Through the rail's answer command"). A rule an agent would have to remember is a check in crew (`roles.3`). Considered: `asserter` returning a new `board` asserter; it would change who every capture says asserted a word and `signals.5`'s reading, where the word is the user's and only its being an answer is ruled out.

### 5. A word is one line of at most 1000 characters

The dock's field is a one-line input with `maxlength` 1000, and `crew tell --board` refuses an empty text, one over 1000 characters, or one holding a line break. Why: record 0038 asks for a short message; a one-line input holds no line break, and crew checks what any post could send rather than trusting the page. How `herdr agent prompt` and Claude Code take a prompt holding line breaks is not read, and one line needs no such reading.

### 6. The dock's word section and what it says back

The word is the last section of the dock's body, not a foot: the dock still has no foot and nothing in it answers (the dock's own requirement). The section names `to` and says a card is answered on the rail. Send posts with `fetch`, disables itself until the answer, and shows the answer's text with `textContent`: on `ok`, the text, the field emptied; otherwise the text with the word left in place; with no answer or an empty one, `the board's listener did not answer: nothing was sent`. On `location.protocol === "file:"` the field and Send are disabled and the section says a word is sent only from the served board. The `fetch` is the page's one request, made only on Send, to its own origin.

### 7. The briefs say what a tell from the board is

`crew.py`'s `SENDERS`, in every brief's roster (`teams.10`), adds that a message beginning `[crew tell from <user>@board]` is the user's word sent from the board about the item it names, and answers no card. Changing the briefs makes each standing agent due a restart once the change reaches its host, as any brief change does (CLAUDE.md, *Proving and landing a bolt*).

## Risks / Trade-offs

- [The word works only once swancloud's listener is served] → Until then the post finds no listener and the dock says the board's listener did not answer and nothing was sent; nothing is lost or half-sent.
- [Anyone on the tailnet can post a word] → Record 0038 §4 keeps the word on the tailnet, as the board itself is; crew's check holds a word to the agent its kind goes to, and a word from the board answers nothing, so a forged word can only say something to an agent.
- [A unit moves to another team's bolt in the thirty seconds before the page is written again] → The word goes to the conductor the dock named, which crew's check accepts; that conductor carries it on, as any agent does a word not its own.
- [The template's script is proved by its marks, not run] → As the page's forms and the dock are; the routing and the word's checks, most of the change, are logic cases.

## Migration Plan

None: the page is written whole every thirty seconds by swancloud's maker, and `crew tell --board` is new. Rolling back is the next write from an older crew; a word posted to it then is refused as a `crew tell` with too few arguments, which the dock shows.

## After deploy

None: every scenario is proved in crew's tiers. The listener and its path through Caddy are swancloud's unit, built and proved there, not a step of this change.

## Task notes

**1.1** `plugin/lib/page.py`: `ROLE_OF` (kind to role: `bolt`, `unit`, `fix` `conductor`; `proposal`, `batch` `planner`; `signal`, `record` `design`; `landing`, `deploy`, `operation` `ops`) and `word_to(key, d, label)`: the role's agent; for `conductor`, the team of the held or planned bolt the item is or belongs to as `d["board"]` gives it (a unit's bolt, a fix's bolt), `<team>-conductor`, else `<label>-operator`; any other kind `<label>-operator`. `docks` sets `to` on every page. Cases in `tests/py/test_page.py`, a class `TestWord` on the fixture `TestDocks` uses: a held bolt of swb-1, its unit and its fix go to `swb-1-conductor`; a planned bolt with no team and its unit to `wldn-operator`; a proposal to `wldn-planner`; a signal to `wldn-design`; a landing, a deploy and an operation to `wldn-ops`; a team and a subscription to `wldn-operator`; every page in `docks` has `to`.

**1.2** `plugin/lib/crew.py`: `ROLE_OF` as in 1.1 (one table; `page.py` imports it from `crew`, which it already loads for the fleet); `KINDS`, the dock's kinds and `batch`, `record`, `partition`; `board_word(fleet, raw)`, a decision returning `(to, text)` or raising `Refusal` through `fail()`: `raw` parses as one JSON object whose `label`, `key`, `to` and `text` are strings, else `a word from the board is one JSON object holding label, key, to and text`; `label` in `fleet["partitions"]`; `key` matches `^([a-z]+):([A-Za-z0-9._:/+-]{1,200})$` with its kind in `KINDS`; `to` is the kind's agent in the label (`a word on a proposal goes to wldn-planner, not swb-1-conductor`), for the conductor's kinds one of the label's teams' conductors or its operator; `text.strip()` not empty, at most 1000 characters, no `\n` or `\r` (`a word from the board is one line`); the text is `(on <kind> <name>) <text>`. `board_tell(fleet, raw)`: `board_word`, then `tell(fleet, to, text, sender=f"{getpass.getuser()}@board")`, printing `sent to <to>` when it returns true. `main`: `a == ["tell", "--board"]` reads `sys.stdin` and exits 0 or 1 by `board_tell`. `SENDERS` gains the sentence of Decision 7. `plugin/bin/crew`: `tell) [[ ${2:-} == --board && $# == 2 ]] && { py tell --board; exit; }` before the existing line, and the usage header's `crew tell` gains `crew tell --board < word.json`. Cases in `tests/py/test_board_word.py` (new), `crew.tell` monkeypatched as `tests/py/test_send.py` does: a word on `unit:a` for `swb-1-conductor` tells it `(on unit a) Keep the zone check` with sender `<user>@board` and prints `sent to swb-1-conductor`; one each for not JSON, a missing field, a field not a string, an unknown label, an unknown kind, a key with a space, the wrong agent for a proposal, a conductor of another partition's team, an empty text, 1001 characters, a line break, each refused with its words and `tell` never called; a tell that returns false prints nothing and the command exits 1.

**1.3** `plugin/lib/transcript.py`: `BOARD = "@board"`; `Verdict(..., board=False)`; in `check`, `received_user` kept apart for records not from the board (a tell whose `TELL` sender ends `@board`), `want="user"` taking the last such, else the last from the board; the verdict's `board` set from its source record. `plugin/lib/plan.py` `words_refusal`: after the verified-and-user test, `if v.grade == "verified" and v.asserted_by == "user" and v.board` returns `f"{head}: the words came from the board, which answers nothing; {advice}"`, the check placed before the `None` return. Cases in `tests/py/test_transcript.py`: `asserter` reads `[crew tell from chuck@board] (on unit a) x` as `user`; `check` on a transcript holding the words only in such a tell is verified, `board` true; with the same words typed afterwards, and with them typed before, `want="user"` gives the typed record, `board` false. Cases in `tests/py/test_board_word.py`: `submit_word_refusal`, `pane_answer_refusal` (with a batch the entries hold) and `settled_refusal` on a board verdict each refuse with `the words came from the board, which answers nothing` and their advice; on the same verdict with `board` false each passes.

**2.1** `plugin/lib/page.html`: in the dock's drawing, a last section `.word`: a line `to <to>; a card is answered on the rail`, an `<input type="text" maxlength="1000">` and a Send button; `sendWord(key, page)` posting `JSON.stringify({label: D.label, key, to: page.to, text})` with `fetch(new URL("word", location.href), {method: "POST", headers: {"Content-Type": "application/json"}, body})`, the button disabled until it settles, the answer's `text()` shown by `textContent` as Decision 6 says, the field emptied on `ok`; on `location.protocol === "file:"` the input and button disabled and the line `a word is sent only from the served board`. Cases in `tests/py/test_page.py` on `page.render` with the data block removed, as the page's form cases are: `class="word"`, `maxlength="1000"`, `fetch(` once, `new URL("word"`, `"POST"`, `file:`, `a card is answered on the rail`, `the board's listener did not answer: nothing was sent`, `a word is sent only from the served board`; no `XMLHttpRequest`, `WebSocket`, `innerHTML` or `.dk-f`; the case "nothing loads from outside the file" still passes, and the dock unit's assertion that the page holds no `fetch` is replaced by the `fetch(` once case.

**3.1** `tests/t-journey-main.sh`, after its crew send cases: `printf '%s' '{"label":"wldn","key":"proposal:4","to":"wldn-planner","text":"Words BRDW from the board"}' | crew tell --board` succeeds, prints `sent to wldn-planner`, the stub log holds `agent prompt wldn-planner '[crew tell from <user>@board] (on proposal 4) Words BRDW from the board'`, and the run record holds a tell of 41 characters, the item's naming counted, and not `BRDW`; the same word for `swb-1-conductor` fails with `a word on a proposal goes to wldn-planner`, typing nothing. The opening comment names the board's word. No new `# Reads:` path; run `tests/moon-tasks` and commit `tests/moon.yml` if it changes (`tests.10`).

**3.2** README: the `crew tell` paragraph (the mark of a tell from the board, what it answers) and its usage line; the `crew page` paragraph (each dock's word to the item's agent, the agents by kind, the post to the page's own address served by swancloud). `plugin/skills/crew/SKILL.md`: a row for `crew tell --board`, and `crew page`'s row. `plugin/bin/crew`'s usage header as 1.2 says. `tests/t-docs.sh` passes.

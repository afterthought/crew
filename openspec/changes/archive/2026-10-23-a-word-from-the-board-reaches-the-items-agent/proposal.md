# Proposal

## Why

Once the board opens a dock on each item (`the-board-opens-a-dock-on-each-item`), the user can read an item there but can say nothing about it: to give a unit's conductor or the planner a word on what they see, they go to a terminal and find the right agent. The user asked to send feedback on board items to the right agent from the board itself (signal 2026-10-23-swancloud-design-40a8b1a4/01), and record 0038, accepted on 2026-10-23, rules how: the dock takes a short message and it reaches the item's agent as crew's tell in the user's name from the board, naming the item; the board still answers nothing, a card being answered on the rail; and a word that cannot be delivered is said in the dock in crew's own refusal words (its §3, extending record 0010). This is the record's second crew unit, after the dock.

## What Changes

- Every dock ends with **a word to the item's agent**: a one-line field, a Send button, and a line naming who it goes to. The agent is the item's, as record 0038 §3 lists them: a bolt's, unit's or fix's team conductor; a proposal's or batch's planner; a signal's or record's design agent; a landing's, deploy's or operation's main-level ops; and the partition's operator for anything else, a team, a subscription, or a bolt or unit no team holds yet.
- Sending posts the word to the board's own address, where swancloud's listener (its unit `the-boards-word-reaches-crew-tell`, record 0038 §4) hands it to one crew command, **`crew tell --board`**, which reads the word on its standard input, checks it and tells the agent. The agent receives `[crew tell from <user>@board] (on <kind> <name>) <text>`: crew's tell in the user's name, from the board, naming the item, so no agent takes it for typing.
- The dock says what came back: "sent to crw-6-conductor", or, when nothing was delivered, crew's own words for why (the agent is waiting on a question in its pane, is not up, its host did not answer, the word was empty or too long). When the listener does not answer, the dock says that nothing was sent; opened from disk, the dock says a word is sent only from the served board.
- **The board still answers nothing.** The dock's line says a card is answered on the rail, and crew holds to it: words that reached an agent only in a word from the board are never taken as the user's words for landing a bolt, answering a batch or settling a record in a pane; crew refuses, saying the words came from the board and where the user answers instead. Signals the agents capture from such a word are still the user's.
- Every brief's line on who is speaking in its pane names a tell from `<user>@board` as the user's word sent from the board about the item it names, answering no card.
- The page still loads nothing: the word's post, on the user's Send, to the page's own address, is the only request it ever makes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `board-page`: each dock takes a word to its item's agent, routed by the item's kind, delivered by `crew tell --board` and answered in the dock; a word from the board answers no card; the page's one request is that word's post to its own address.

## Impact

- `plugin/lib/page.py`: each dock page names the agent its word goes to.
- `plugin/lib/page.html`: the word's field, its post and what the dock says back.
- `plugin/lib/crew.py`, `plugin/bin/crew`: `crew tell --board`, its check of the posted word, the item named in the tell, and the briefs' line on who is speaking.
- `plugin/lib/transcript.py`, `plugin/lib/plan.py`: a word from the board is read as the user's but refused as the words of a landing, a batch's answer or a record settled in a pane.
- `tests/py/test_page.py`, `tests/py/test_board_word.py` (new), `tests/py/test_transcript.py`, `tests/t-journey-main.sh`, `tests/moon.yml`.
- README, the crew skill's rows for `crew tell` and `crew page` (`docs.2`).
- swancloud: its listener, `the-boards-word-reaches-crew-tell`, posts to and reads from the command this change adds; nothing of swancloud's is edited here. No service of crew's (`state.4`). No change to `crew board`, its JSON or the agents' views (`code.8`).

## Touches

```
plugin/lib/page.py
plugin/lib/page.html
plugin/lib/crew.py
plugin/bin/crew
plugin/lib/transcript.py
plugin/lib/plan.py
tests/py/test_page.py
tests/py/test_board_word.py
tests/py/test_transcript.py
tests/t-journey-main.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
```

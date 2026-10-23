# Proposal

## Why

The rules say the user lands a bolt in one of two ways: by approving its landing card, or by saying so in their own words in main-level ops's pane (`plan.16`). crew records the first, since the card's answer is Pending You's. It records nothing of the second. When the user says "land it" in ops's pane, ops runs `crew bolt submit` on its own say-so, crew never checks that the user said it, and the landing card, still waiting, is withdrawn at `crew bolt land` as if nobody had answered it. A batch answered in a main-level pane is now read from the session's transcript and recorded as the user's (`briefs.12`, record 0031 as amended 2026-10-22), and the design agent left the landing's pane answer for a unit of its own (signal 2026-10-23-swancloud-planner-06710fc5/01). This is that unit.

## What Changes

- When the user tells ops to land a bolt in their own words in ops's pane, ops runs `crew bolt submit <bolt> --excerpt "<the user's words>"`. Before anything is submitted, crew looks for the words in ops's own session transcript on its host, and goes on only when it reads them as the user's (`signals.5`): typed in the pane, or a `crew tell` from `<user>@<host>`, such as the rail's `crew tell <label>-ops "Land bolt <bolt>."`.
- Words crew does not read as the user's are refused, and nothing is submitted: ops's own words, words another agent passed on with `crew tell` (named), crew's own message, a tool's output, words not in the transcript, or a transcript crew can't read or can't tell is the live session's. Ops's say-so is never the word to land.
- A landing on the user's words is recorded on the `bolt.submit` entry: the session and the transcript record the words were read from, and their length, but none of the words (`record.3`). A landing on the card's approval, with no `--excerpt`, is recorded as today.
- At `crew bolt land`, the bolt's landing card closes saying where GitHub's main holds the landing, as today, and then that it landed on the user's word in ops's pane, with their words. The card is closed as answered in the conversation, so Pending You shows it answered, not just withdrawn. A landing said in the pane counts as one approved on its card.
- When `crew bolt land` runs where the words can't be read back, on another host than the submission's, the card still closes naming the pane and the time, without the words, and the command says why.
- Main-level ops's brief says to pass the user's words with `--excerpt` when the word to land came in its pane, and that a refusal means no landing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `main-level`: a landing said in ops's pane is checked against ops's own transcript as the user's words before anything is submitted, is recorded without the words, and closes the bolt's landing card naming them.

## Impact

- `plugin/lib/plan.py`: `bolt_submit` takes `--excerpt`, checks it before the submission, records the pointer on `bolt.submit` and keeps the words on ops's host until `bolt land`; `bolt_land`, `tidy_after`, `tidy` and `landing_cards_closed` carry the words to the card's close apart from the outcome they record; `card_closed` passes Pending You's "answered here" on such a close; the parser and the module's usage text.
- `plugin/lib/cards.py`: `close_call` takes whether the card was answered in a conversation.
- `plugin/roles/main-ops.md`: *Landing a bolt*.
- Tests: `tests/py/test_landing.py`, a new `tests/py/test_pane_landing.py`, `tests/py/test_cards.py`, `tests/py/test_card_commands.py`, `tests/py/test_parser.py`, `tests/t-briefs.sh`.
- `README.md`, `plugin/skills/crew/SKILL.md` and the usage header of `plugin/bin/crew` (`docs.2`).

## Touches

```
plugin/lib/plan.py
plugin/lib/cards.py
plugin/roles/main-ops.md
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/py/test_landing.py
tests/py/test_pane_landing.py
tests/py/test_cards.py
tests/py/test_card_commands.py
tests/py/test_parser.py
tests/t-briefs.sh
```

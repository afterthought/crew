# A landing sluice sent back reads as its team's fix, not a stop

## Why

On the Willdan box (wldn, chuck-herdr-alpha), switchboard-kit's bolt `mains-gate-passes-the-dispatch-supersede-test` was submitted again at `977138a` at 21:28Z on 2026-11-06 as pull request #268. sluice took it in on another host, tested it and sent it back for a failed check. It stays a draft. At 22:28Z main-level ops ran `crew bolt submit` again at the same head. sluice's worktrunk driver read the failed request as one whose standing it could not read and submitted nothing: "wt submit: could not read whether a submission stands, so nothing was submitted" (22:31:11Z). crew 0.38.10 read that exit 3 as sluice itself failing. It recorded the landing stopped, nothing of the bolt's, gave the row its box back, and told ops that the next `crew bolt submit` submits it again. That command cannot run while the head is the one sluice sent back. A landing that needs its team's fix read as a stop of sluice's (signal `WilldanGroup/crew-state:wldn/main signals/2026-11-06-wldn-ops-ea539623/01`). The user ruled that the box's crew faults are fixed on crew main ("Yes: fix them on crew main, for the box").

sluice's statement says what moves a sent-back request on (agentplot/blueprints `design/sluice/requirements.md`). A request whose landing failed stays a draft (C.5, pull request). Its entry is submitted again only by a new submit or by the operator, never because its head moved (clauses 5, 67, 120). crew's way on for a bolt whose landing failed is a fix it launches on the bolt's branch, which merges into the bolt through sluice; the landing is then submitted again (C.5, crew).

## What Changes

- **A sent-back landing is its team's fix until the head moves.** A refusal sluice made for the bolt's own content, recorded at the head submitted, stands through every later `bolt.submit` that submitted nothing at that head: crew's own refusal before submitting, and a stop that names no submission of sluice's. The bolt's row stays held for its team's fix and says no stop. A submission sluice queued, left standing or landed, a stop naming a submission of its own, or a stop at another head lifts it.
- **`crew bolt submit` refuses a landing sluice sent back at the head it would submit.** It reads sluice's record of that submission, `sluice status <n> --json`, on the team's host. It submits nothing, runs no `wt submit` and leaves the pull request a draft. It says what failed from the record: the checks that ran and failed, the paths in conflict and the submissions it meets, and main's revision it was tested on (`failed`, `conflict.paths`, `conflict.with`, `tested.on`), never a check's own words. It offers the team's fix with the `crew fix` that starts it, and the `crew bolt submit` that lands it once that fix has merged. A record that can't be read is said with why, and the fix offered with no command.
- **A refused landing tells ops the fix.** When sluice sends a landing back, crew's words to ops name what failed from the record, the team's `crew fix` (a failed check mended, or main taken in for a conflict), and the submit once that fix has merged, in place of "then you submit again".
- **Each reader says it.** The kit's landings card's row and the rail's land line say ops submits the bolt again once its team's fix has merged. `crew bolts` shows the sent-back landing on the bolt, `landing: sent back at <head>, its team's fix: <sluice's words>`, and in its JSON as `sent_back`. A run record it can't read is named.
- README, the crew skill and `crew`'s usage header say this (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a requirement of its own, "A landing sluice sent back is its team's fix".
- `rail-cards`: "A refused landing is held on its row" holds through a later submit that submitted nothing at that head, and says ops submits it again once the fix has merged.

## Impact

- `plugin/lib/plan.py`: the decisions `sent_back`, `sent_back_of`, `sent_back_said`, `team_fix`, `team_fix_said` and `sent_back_refusal`; the act `landing_sent_back`, run by `landing_submitted` before the queue is read; `refusals` and `stops` read through `sent_back`; `landing_end` and `landing_said` take the bolt's team; `submission_of` keeps the record's `tested`; `landing_rows`, the rail's land line, `bolts_sent_back`, `bolts_data` and `bolts_text`.
- `plugin/bin/crew` (usage header), `README.md`, `plugin/skills/crew/SKILL.md`.
- Tests: `tests/py/test_landing.py`, `tests/py/test_landings.py`, `tests/py/test_rail.py`, `tests/py/test_bolt_submissions.py`, `tests/py/test_bolt_commands.py`, `tests/t-journey-land.sh`.
- `crew bolts --json` gains `sent_back` on each bolt and `sent_back_unread` at the top. The board and the mod read neither, so nothing they draw changes (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_landing.py
tests/py/test_landings.py
tests/py/test_rail.py
tests/py/test_bolt_submissions.py
tests/py/test_bolt_commands.py
tests/t-journey-land.sh
```

---
paths:
  - "plugin/lib/record.py"
---

# Run record rules

The rules for the run record: what an entry is, when it is written, what it never holds. `core.md` binds here too; the how-to is README's Seeing what happened section.

## Rules

- **[record.1]** Every command that moves work appends one entry per act, after the act, done or refused; a pure read appends nothing.
- **[record.2]** A failed append is said once on standard error and never changes what the command does or how it exits.
- **[record.3]** No entry holds text anyone typed: not a tell's text, a stage's words, an intent, a goal, a reason, an excerpt or a proposal's `Do` line; `Why` is composed from names, a tell records its length, a refusal records crew's own message.
- **[record.4]** A host appends only to its own `runs/<host>/<UTC day>.rec`, each entry in one write after the descriptor, never rewritten or removed; the branch's copy of a day is the union of both by `Id`, so carrying twice changes nothing.
- **[record.5]** Each `stage.start` is followed by exactly one `stage.end`; an end nobody waited for is recorded once, marked late, by the next command that reads the team.
- **[record.6]** A fix's object is `fix/<bolt>/<name>`, and its `Why` names the fix by the part after the last slash, for fixes under either naming.

## Details

**[record.1]** Rules out: an entry before the act; an entry from `crew bolts`. Not ruled out: one `card.post` for two posts Pending You answers with one card: a post answered with the card this host's record already holds open under the same key and owner, another command's post of it recorded while this one's was asked, is that card's act, made once, and is not recorded again (two rail reads swept at once on mac-studio on 2026-10-18, from swancloud-ops's start and the design agent's, and recorded `req_2a16bbe95cd841c58611` under `op/swancloud-srv/1` twice, at 15:24:51Z and 15:24:52Z; `plan.py` `card_posted`, `tests/py/test_card_commands.py`). Source: `run-record` spec; `record.py` 4–8; `plan.py` `ACTS`, `named`; `tests/py/test_record.py`, `tests/t-journey-state.sh`.

**[record.2]** Rules out: `set -e` tripping on `entry`; a command failing for want of a record. Source: `record.py` 7–8, `emit`; `tests/py/test_record.py`, `tests/t-journey-state.sh`. Read 2026-10-27, for madswan's signals 2026-10-27-swancloud-operator-cbefe4ba/01 and /02 (madswan-planner's `crew plan answer 170 plan approve` on deneb, 17:32:58Z): the run's last entry, its card.close of proposal/170, was refused six times by madswan/main, which took nineteen commits from deneb's writers in two minutes, and was kept, as this rule says; the next command on deneb pushed it nine seconds later (d1ae319d2 on madswan/main), since `record.reach` pushes every entry the branch lacks, oldest first, before the command's own, and `record.4`'s union makes a second push harmless. The card's close read deneb's own file (`cards.host_entries`, `card_under`), not the branch, found the card.post of 16:59:32Z, acked the card on Pending You and recorded the close at 17:33:38Z, State closed, with no refusal; the later line "madswan-planner holds none open on this host" is a lookup after that close, and right. A kept entry delays no close and loses no card; what it delays is the branch's view of it (`read.5`), until the host's next entry. No crew unit or chore from this rule.

**[record.3]** Rules out: `Refused: \`unit add x "the whole intent"\``. Source: `run-record` spec "An entry holds no text anyone typed"; `record.py` 6–7; `tests/py/test_record.py`, `tests/t-journey-signals.sh`.

**[record.4]** Rules out: a host writing another's file; an entry edited in place. Source: `record.py` `emit`, `carry`; state-repository design; `tests/py/test_record.py`, `tests/contract/test_record.py`, `tests/t-journey-state.sh`.

**[record.5]** Rules out: two ends for one start; an end never recorded. Source: `run-record` spec "A stage's end is recorded when crew sees it".

**[record.6]** Rules out: a fix's `Why` naming its bolt as the fix. Source: fix 147075d.

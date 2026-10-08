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

**[record.1]** Rules out: an entry before the act; an entry from `crew bolts`. Source: `run-record` spec; `record.py` 4–8; `plan.py` `ACTS`.

**[record.2]** Rules out: `set -e` tripping on `entry`; a command failing for want of a record. Source: `record.py` 7–8, 151–153; `plugin/bin/crew` 123.

**[record.3]** Rules out: `Refused: \`unit add x "the whole intent"\``. Source: `run-record` spec "An entry holds no text anyone typed"; `record.py` 6–7.

**[record.4]** Rules out: a host writing another's file; an entry edited in place. Source: `record.py` 112–205; state-repository design.

**[record.5]** Rules out: two ends for one start; an end never recorded. Source: `run-record` spec "A stage's end is recorded when crew sees it".

**[record.6]** Rules out: a fix's `Why` naming its bolt as the fix. Source: fix 147075d.

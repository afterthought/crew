---
paths:
  - "plugin/lib/transcript.py"
  - "plugin/lib/plan.py"
---

# Signal rules

The rules for captures, signals and moves. `core.md` binds here too; the how-to is README's Signals section and the blueprints' `signals/README.md`.

## Rules

- **[signals.1]** An agent's captures and signals are written to `signals/` on the flywheel's branch; meeting and channel signals stay in the partition's first blueprints repo; an id is unique across both and every lookup tries the branch first.
- **[signals.2]** `crew signal` runs on the host it is invoked on, never forwarded, and requires a verbatim excerpt; it refuses only a paraphrase in a live transcript (written within fifteen minutes), and anything crew cannot read lowers the grade and never stops a capture; no command refuses anything for a grade.
- **[signals.3]** Of a capture's source only the excerpt enters git; the raw record is banked outside git on the capturing host and the capture points to it.
- **[signals.4]** A signal has one move, appended to `moves.rec` on the branch and refused when one exists; a signal becomes work only through `route`, written with the unit that takes it; signals, captures, moves and proposals are append-only, and a capture names who recorded it.
- **[signals.5]** Who asserted an excerpt is read from the mark on the record: `[crew tell from <name>]` is that agent, `[crew]` is crew, a stage's own prompt is the conductor that ran it, a tool's output is the tool, and anything else is the user.
- **[signals.6]** A capture a program records, a kit's release adapter or its deployer, lands through `crew signal land` on the flywheel's branch of the partition the kit belongs to, with `source` naming the program and the raw record banked on the host that ran it; a program never writes a blueprints repo, and a capture that is its own excerpt gets its one signal mechanically, with no model in between.
- **[signals.7]** Curation runs on the partition's cadence over the signals with no move, and on the user's word; a batch of chores it routes is proposed as one bolt the user accepts or declines row by row, each row still its own decision.

## Details

**[signals.1]** Rules out: an agent's signal committed in a blueprints repo; a capture name the blueprints already has. Source: checked-capture; `plan.py` 52–53, 2068–2085, 2247–2251.

**[signals.2]** Rules out: a reworded excerpt accepted; a capture blocked by an unreadable transcript; forwarding `crew signal`. Source: fix e1ed1df; checked-capture design "The check, and how it degrades"; `plan.py` `signal`, `capture_named`; `tests/py/test_signals.py`, `tests/py/test_transcript.py`, `tests/t-journey-signals.sh`.

**[signals.3]** Rules out: a transcript line in a commit. Source: checked-capture design "The raw record".

**[signals.4]** Rules out: a second move; a hand edit of `moves.rec`; a route without a unit. Source: `main-level` spec; `plan.py` `move`, `curation_move`, `route_move`; fix 2d95e12; `tests/py/test_signals.py`, `tests/contract/test_recfix.py`, `tests/t-journey-signals.sh`.

**[signals.5]** Rules out: a conductor's `Fix:` words graded as the user's. Source: checked-capture design; `transcript.py` `asserter`; `roles.4`; `tests/py/test_transcript.py`.

**[signals.6]** Rules out: a release or a deploy failure captured into a blueprints repo; a program summarising a release before curation; a machine capture with no raw record. Source: swancloud ADR 0019, 0020; the blueprints' `signals/README.md` (two homes); Flywheel Next on enumerators, per the exploration of 2026-10-08. Not built: `_open.md`.

**[signals.7]** Rules out: curation only when someone asks; a bolt of chores approved as one yes with no row declinable. Source: Flywheel Next requirements 60 and 110, per the exploration of 2026-10-08; ADR 0001. Not built: `_open.md`.

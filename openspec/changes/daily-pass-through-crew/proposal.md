# Proposal

## Why

Signals from meetings and channels are written by the daily pass in the blueprints repo (`signals/bin/sweep` and the `signal-capture` skill in `WilldanGroup/willdan-blueprints`): two headless Claude runs each morning that write capture and signal files in a checkout and commit them there. It is the one writer of shared records that does not go through crew. So a meeting signal has no entry in the run record, and `crew trace` of one begins at its move, with nothing saying when it was captured or by what; its files are not checked against the shape crew and the curator rely on; and its commits arrive by a checkout's push, the path that every other record left because checkouts lag and collide.

This change gives the daily pass crew's path. It is the last step of the findings-to-design work (`openspec/explorations/findings-to-design/proposal.md`, the constraint that shared records are written only through crew, and invariant 16; `roadmap.md`). Most of the work is in the blueprints repo, outside crew.

## What Changes

- **`crew signal land <capture-dir>`** takes a capture directory written anywhere on disk (a `capture.md` and its signal files, in the shape the blueprints' `signals/README.md` gives), checks it, and writes it to `signals/` on main of the partition's first blueprints repo by crew's path: fetched, applied to the tip, pushed without force, applied again when someone pushed first. Landing the same directory again writes nothing.
- **It checks what it lands**: the capture names its source and event date; each signal has a kind, an asserter, an assertion and a quoted excerpt; ids match their paths; nothing that looks like raw material is among the files.
- **A landed signal is never changed.** A signal file that differs from one already on main is refused. A capture may change only from unread to read, with its count.
- **Each landed capture and signal leaves a `capture` entry**, so a meeting signal's trace begins where an agent's does.
- **Outside crew**, in each blueprints repo that runs a daily pass: the pass writes its captures in a scratch directory that git ignores, lands them with `crew signal land`, and pulls; it no longer commits `signals/` itself.

Where meeting signals live is unchanged by this change: the blueprints. The user has an open question on whether they should follow an agent's signals into the flywheel's state; if so, the one thing that changes here is where `crew signal land` writes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `signal-capture`: a capture written outside crew is landed through crew, checked, immutable once landed, and recorded.

## Impact

- `plugin/lib/plan.py`: `signal land` (the checks, the write by paths to the blueprints repo's main, the entries).
- `plugin/bin/crew`, `README.md`, `plugin/skills/crew/SKILL.md`, the usage header, `tests/`.
- The blueprints repos with a daily pass (willdan-blueprints today): `signals/bin/sweep`, `.claude/skills/signal-capture/SKILL.md`, `.gitignore`, `signals/README.md`.
- The Mac that runs the daily pass needs crew on its `PATH` for the job, and the partition's label.
- Depends on `run-record` and `checked-capture` (the one lookup of signals across both homes).

## Touches

`plugin/lib/plan.py`, `plugin/bin/crew`, `plugin/skills/crew/SKILL.md`, `README.md`, `tests/`; in each blueprints repo `signals/bin/sweep`, `.claude/skills/signal-capture/SKILL.md`, `.gitignore`, `signals/README.md`.

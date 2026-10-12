# Proposal

## Why

A program records captures too: swancloud's release adapter one per release newer than the fleet's pin, its deployer one per failed deploy (swancloud ADRs 0019, 0020). `signals.6` has each land through `crew signal land` on the flywheel's branch of its kit's partition, `source` naming the program, its raw record banked on the host that ran it, and its one signal made mechanically. Until crew has the command both programs keep their captures on mac-studio and retry them every night, and the doctor says they wait on crew.

## What Changes

- **`crew signal land <capture-dir> --label L`**, run as the program (`CREW_AGENT`) on the host that ran it, never forwarded (`signals.2`). It checks the folder whole: `capture.md` and its signals, `NN-<slug>.md`, and nothing else; the capture names itself, its `source`, who captured it, its event's date and its raw record on this host; it is read and counts its signals, at least one; each signal names itself, its kind and who asserted it, says what it asserts, quotes its excerpt and is no larger than 8 KiB. A refusal names the file.
- It writes the folder to `signals/<capture>/` on the flywheel's branch in one commit with a `capture` entry naming each signal, passing over the files the branch holds the same and refusing one that differs; the same capture again writes nothing and says it is already landed, exiting 0.
- `crew signal land --help` begins `usage: crew signal land`, which the programs read before handing a capture over; a signal's slug can no longer be `land`.

## Capabilities

### Modified Capabilities

- `signal-capture`: a program's capture lands on the flywheel's branch through `crew signal land`.

## Impact

- `plugin/lib/plan.py` (`signal_land`, `capture_refusal`, `capture_landing`), `plugin/bin/crew`'s usage, README, `plugin/skills/crew/SKILL.md`.
- `tests/py/test_signals.py`, `tests/t-journey-signals.sh`.
- swancloud's release adapter and deployer land their captures with no change of theirs, once the release adapter dashes the versions in its capture names, which `code.4` refuses with dots (the user, 2026-10-12).

## Touches

```
plugin/lib/plan.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/**
```

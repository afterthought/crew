# Design

Relies on `signals.1` (an id is unique across both homes), `signals.2` (`crew signal` runs where it is invoked), `signals.3` (only the excerpt enters git; the raw record stays on its host), `signals.4` (captures and signals are append-only, and a capture names who recorded it), `signals.6` (this command), `state.1` and `plan.1` (one checked commit through crew's cache), `code.4` (the names crew accepts) and `code.7` (the checks are functions of the folder's files). Touches `signals.md`'s and `plan.md`'s area (`plugin/lib/plan.py`).

## What the programs send

Both of swancloud's programs write a folder per capture: `capture.md` with `capture`, `source` (`release`, `swancloud-deployer`), `key`, `event_date`, `captured_by`, `host`, `at`, `raw: <host>:<path>`, `imported`, `status: read` and `signals: 1`, then a title and a sentence; and one signal, `01-released.md` or `01-failed.md`, with `signal`, `kind`, `who` and `subject` (the release adapter adds `claims`), one fixed sentence, the excerpt quoted, and where it came from. The deployer's excerpt is the failed step's last 40 lines, the release adapter's the release's notes cut at a line under 8 KiB; each keeps the whole in its raw record. Each asks `crew signal land --help` first and reads exit 2 as a crew without the command.

## The checks, before any write

`capture_refusal` judges the folder's files, this host and whether the raw record is there: the capture's name is one `code.4` takes; `capture.md` is there and every other file is a signal's; the capture names itself, a `source`, a `captured_by` and an `event_date` that is a date; its raw record names this host and is there; it is read and counts as many signals as it holds, at least one, since a program's capture is its own excerpt and its one signal is made with it; each signal names itself in the capture, a kind of the five, who asserted it, says something and quotes something, and is at most 8 KiB. The first refusal found is said, naming the file, and exits 1, never 2. The name must also be free in the partition's first blueprints repo (`signals.1`).

## The write

One `write` on the flywheel's branch: at each tip, `capture_landing` adds each file the branch lacks, passes over one it holds the same, and refuses one it holds otherwise; with nothing to add, nothing is committed and the command says the capture is already landed, so a program that lost its own record of what landed recovers by offering again. The commit's subject is `signals(<capture>): land <n> signals (<who>)` and its entry a `capture` naming each signal added. `By` is the program's `CREW_AGENT`. A refused landing is recorded refused, naming the capture when its name is one crew takes.

## Not here

The daily pass's meeting captures, which land in the blueprints repo and may be unread stubs, are `daily-pass-through-crew`'s. A capture name with a version's dots is refused by `code.4`, which stands: swancloud's release adapter dashes its versions (the user, 2026-10-12), a change of swancloud's.

## Proof in dev

The logic cases and the signal journey prove it; crew has nothing to deploy. Once landed and every host has pulled, the deployer's next failed deploy lands from mac-studio, and `crew signal show <capture>/01-failed` reads it.

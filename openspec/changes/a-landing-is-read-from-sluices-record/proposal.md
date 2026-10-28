# A landing is read from sluice's record

## Why

Today a bolt's landing is recorded and closed only by the one `crew bolt submit` process that submitted it, at the end of its own wait. When that process is gone before sluice decides (ops's session restarted, its background task cut), nothing records the landing; when the close is refused, the refusal is printed on that process's standard error and nowhere else, and the bolt stays held until someone runs `crew bolt land` by hand. wldn's swb-3 lost a day to exactly that on 2026-10-26: its bolt had landed, its close was refused for a chore still at ready, and nobody read the refusal (record 0044, outcome 4; `plan.8`'s reading of 2026-10-27). Record 0044, accepted by the user on 2026-10-27, makes it a rule (`plan.21`): landed is read, never remembered.

## What Changes

- When sluice queues a landing's submission, crew records it at once in the run record: the bolt, the submission's number, the head submitted and main before. From then on any host knows which submission to read.
- The landing's waiter on the team's host, the background process `crew bolt submit` already leaves running there, waits as `teams.5` has an agent wait: `sluice wait <n> --timeout 9m --json`, again while it exits 5, rather than one call of a day. When it ends, it runs crew's read of the landing.
- One read of a landing, `crew _landing-read <label> <bolt>`, on the team's host and one at a time there, reads sluice's own record of the recorded submission (`sluice status <n> --json`). While sluice has it standing, the read records nothing. Once sluice has it out, the read records its outcome as `crew bolt submit` records it today (landed, refused for the bolt's content, or stopped), and closes a landed bolt with `crew bolt land`'s own code.
- Every crew act that reads the bolt after its landing runs that read: the waiter as it ends, `crew bolt submit`'s own end, the team's read on its host (every team command and the conductor's wait), and `crew bolt land`. `crew bolt land` by hand still closes a bolt, but it is never the only way.
- A close crew refuses is recorded as a refused `bolt.land` entry with crew's words, recorded again only when the words change. The bolt's head line on the board, and its conductor's and ops's bands, say the bolt landed on main and was not closed, with those words. This lasts until a later read closes the bolt.
- While a landing is queued, the bolt's head line says so, with sluice's submission number.
- Main-level ops's brief stops telling ops to run `crew bolt land` once a refused close is mended. crew's next read closes it, and ops may still run it.
- sluice changes nothing. Every submission's state is readable from every host that submits to its branch (sluice statement 26), which is madswan-design's reading of 2026-10-27.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a landing's submission is recorded when sluice queues it, and its outcome comes from sluice's record, read by whichever crew act reads the bolt first after it. A landed bolt is closed by that read. A refused close is recorded and said until it is lifted. The landing's background waiter waits a call at a time.
- `crew-board`: a held bolt's head line says when its landing is queued, and says when it landed on main and its close was refused, in crew's words.

## Impact

- `plugin/lib/plan.py`: `SUBMIT`'s background waiter; `landing_submitted` and `landing_ended` (the queued entry, and the end handed to the read); a new `landing_read` and its command `crew _landing-read`; `reap`, the team's read; `bolt_land`; and pure decisions for each, `code.7`.
- `plugin/lib/record.py`: a `Submission` field on run-record entries.
- `plugin/lib/board.py` and `plugin/hooks/status.js`: the bolt's head line and the agents' views (`code.8`).
- `plugin/bin/crew`: the `_landing-read` command's route to the team's host.
- `plugin/roles/main-ops.md`: what ops does when a bolt landed and was not closed.
- Tests: logic (`tests/py/test_landing.py`, `tests/py/test_board.py`), the mod's cases (`plugin/tests/status.test.ts`), and the end-to-end landing journey (`tests/t-journey-land.sh`) on the stub sluice (`tests/stubs/sluice`).

## Touches

```
plugin/lib/plan.py
plugin/lib/record.py
plugin/lib/board.py
plugin/hooks/status.js
plugin/bin/crew
plugin/roles/main-ops.md
plugin/tests/**
tests/py/**
tests/stubs/sluice
tests/t-journey-land.sh
tests/t-briefs.sh
tests/moon.yml
```

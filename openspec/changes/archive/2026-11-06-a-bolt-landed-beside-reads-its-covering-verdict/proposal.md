# A bolt whose last landing went beside the queue reads the verdict that covers it

## Why

On the Willdan box (wldn, chuck-herdr-alpha), switchboard-kit's bolt `the-shared-applications-landing-sends-a-person-where-they-were-invited` took main in by a fix, `take-main-f1e3610`, that changed nothing a required check reads. sluice landed it beside its queue with nothing run, as #1319 at `b01e966` on 2026-11-05 (sluice clause 140, rule core.39). Its commit's `Sluice-Result` reads `landed beside the queue (no required check reads its changes)` and names no `Sluice-Tested`. crew reads a bolt's verification from that trailer and calls it green only when it starts `passed`, so it read the bolt's verification as unknown. The bolt was never proven and never reached switchboard-kit's landings card (signal `afterthought/crew-state:swancloud/main signals/2026-11-05-swancloud-operator-1471e382/01`, from `WilldanGroup/crew-state:wldn/main signals/2026-11-05-wldn-ops-8164854f/01`). The user ruled that the box's crew faults are fixed on crew main ("Yes: fix them on crew main, for the box").

sluice 0.69.0 names the verdict that covers a landing beside (sluice record 0083; statement clauses 23, 140 and S68 as amended on agentplot/blueprints at eb0d3eb). The landing's `Sluice-Result` opens `passed (0 run, 0 replayed)` and names the covering verdict and the revision it landed as. sluice's record of the submission carries the same as `covered_by`, `{at, result, ran, replayed}`. crew v0.41.3 reads neither. With 0.69.0's trailer it would read green from the trailer's words alone, with the landing's own counts, nothing run.

## What Changes

- **A landing beside reads as the verdict that covers it.** A bolt whose head names a submission and no `Sluice-Tested`, which is how sluice writes a landing beside its queue, has its verification read from sluice's record of that submission, `sluice status <n> --json`. It is green only when the record has the submission landed beside the queue as the head and names a covering verdict that passed. The verification then names that verdict's run and replay counts and the revision it landed as, never the landing's nothing run. It is never green from the trailer's words.
- **An older sluice's landing beside stays unknown, saying why.** sluice before 0.69.0 records no covering verdict. Such a landing reads unknown, saying that sluice's record names none and that the bolt reads proven once a landing on it carries a verdict of its own or names the one that covers it. A record crew can't read, one that has the submission landed as another commit, or a covering verdict that did not pass or that crew can't read, reads unknown too, naming which (`read.1`).
- **The gather reads that one record.** A kit's gather runs one `sluice status <n> --json` in the kit's main checkout for each bolt whose head is a landing beside, and none for any other head.
- README and the crew skill say this (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `merge-gate`: a bolt's verification, for a head sluice landed beside its queue, is the verdict sluice's record of that landing names as covering it, a requirement of its own, "A landing beside reads as the verdict that covers it".
- `crew-board`: a kit's gather runs one `sluice status <n> --json` for each held bolt whose head is a landing beside, the record of that landing's submission.

## Impact

- `plugin/lib/gather.py`: the new read `landing_read`, its trailers and fields, giving each bolt `beside` beside its `verdict`.
- `plugin/lib/kit.py`: `verification` takes `beside`; the new decision `covering`.
- `plugin/lib/plan.py`: every read of a bolt's verification passes `beside`: `Stages.bolt_state`, `proven_facts` and `give_refusal`, `landing_unready` and `land_facts`, `bolts_data`, and the rail's landing rows.
- `README.md`, `plugin/skills/crew/SKILL.md`.
- Tests: `tests/py/test_kit.py`, `tests/py/test_rail.py`, `tests/py/test_landing.py`, `tests/py/test_bolt_commands.py`, `tests/py/test_chores.py`, `tests/py/facts.py`, `tests/contract/test_gather.py`; sluice's records in `tests/py/sluice-0.68.1/` and `tests/py/sluice-0.69.0/`.
- The shape of a bolt's verification, `{state, said}`, is unchanged, and nothing the board or the mod draws changes (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/plan.py
README.md
plugin/skills/crew/SKILL.md
tests/py/test_kit.py
tests/py/test_rail.py
tests/py/test_landing.py
tests/py/test_bolt_commands.py
tests/py/test_chores.py
tests/py/facts.py
tests/py/sluice-0.68.1/**
tests/py/sluice-0.69.0/**
tests/contract/test_gather.py
```

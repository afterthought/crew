# Proposal

## Why

On 2026-10-27 the user asked why bolts take so long, then corrected the aim: bolts coded for hours are welcome, but no team may sit idle and nothing may slow down in a gate (signal 2026-10-27-swancloud-operator-694a2442/01). wldn's swb-2 sat seventeen hours on a hold nobody could see, and swb-3's landing waited overnight on cards, and nothing on the rail or the board said where any bolt's time had gone. Record 0044, accepted by the user on 2026-10-27, settles it in its fifth outcome, now rule `plan.20`: a bolt's row shows its age since its give and who held that time, and its landing's entry keeps the split, so an idle team, a hold or a slow gate is read in minutes.

## What Changes

- Every held bolt's head line on the board, in the board tab, the board's JSON and every agent's band that draws it, says how old the bolt is since it was given and where that time went, in minutes per holder: the team, the kit, the user, a hold and nobody. It also says who holds the bolt now and since when, and for a hold, what it is for.
- A bolt's line on its kit's landings row on the rail, the one row the rail gives a bolt, says the same.
- Each minute of a bolt's life goes to one holder, the first of these that applies:
  - the team, while a stage of the bolt's work runs other than a merge;
  - the kit, while one of the bolt's submissions is under test in sluice;
  - the team, while a merge stage runs or one of the bolt's submissions stands in sluice not under test;
  - the user, while a card of the bolt's is open;
  - a hold, while one is recorded on the bolt;
  - nobody, otherwise.

  A bolt nobody has held for five minutes is said to be stalled (`teams.23`'s measure).
- Every bit of this is read from what crew already keeps: the run record, which holds the give, each stage's start and end, each card's post and close, and a host's hold; and sluice's own record of the bolt's submissions. Nothing new is recorded to make it, and crew builds no hold and no stall of its own. Those are Flume's (record 0044 as the user accepted it; record 0047).
- The bolt's landing entry (`bolt.land`) records the bolt's age at its landing and the split, as two new fields, `Age` and `Split`.
- When a host's follower gathers a kit, it now also reads sluice's record of each held bolt's submissions with `sluice status <branch> --all --json`. That is how a decided merge's time in the gate is counted. The queue itself is still read from the overview's watch.
- No bolt is given a clock or a size limit, and no card asks the user about a bolt's age (the user's correction of 2026-10-27; `plan.20`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `crew-board`: a held bolt's head line, in the lane, the JSON and the bands, carries its age and who held its time. The follower's gather of a kit reads sluice's record of the kit's held bolts' submissions as well as the overview's watch.
- `crew-rail`: a bolt's line on its kit's landings row carries its age and who held its time.
- `run-record`: a bolt's landing entry records its age and its split by holder.

## Impact

- `plugin/lib/plan.py`: the decision that splits a bolt's time (`bolt_time`, a function of facts), the reads that feed it from the run record, the rail's land line, and `bolt_land`'s entry.
- `plugin/lib/gather.py`: sluice's record of each asked bolt's submissions, and of main's, read with `sluice status --all --json`, guarded field by field. A standing submission's checks' start is read from the overview's candidates.
- `plugin/lib/board.py`: the ledger's `time`, `bolt_row`'s words, and every view that draws a head line (`code.8`). `plugin/hooks/status.js` draws segments and changes only if a case shows it must. `plugin/tests/status.test.ts` gains a case.
- `plugin/lib/record.py`: `Age` and `Split` among the fields.
- `README.md` and `plugin/skills/crew/SKILL.md`, for the board's and the rail's words (`docs.2`). No command or usage changes.
- Tests in the logic and contract tiers, a recorded sluice 0.51.3 `status --all` document beside the overview one, and `tests/moon.yml` if a test's reads change.
- The sibling unit `a-landing-is-read-from-sluices-record` changes which act writes `bolt.land`. Whatever writes it carries the split.

## Touches

```
plugin/lib/plan.py
plugin/lib/gather.py
plugin/lib/board.py
plugin/lib/record.py
plugin/hooks/status.js
plugin/tests/**
README.md
plugin/skills/crew/SKILL.md
tests/py/**
tests/contract/**
tests/t-journey-land.sh
tests/moon.yml
```

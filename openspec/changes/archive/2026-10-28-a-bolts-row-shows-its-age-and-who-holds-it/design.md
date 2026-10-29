# Design

## Context

Record 0044's fifth outcome, rule `plan.20`: a bolt's row on the rail and the board shows its age since its give and where the time went by holder (the team, the kit, the user, a hold, nobody), and its landing's entry records the split. The user accepted the record with the note that holds and stalls are built in Flume, sluice and Tailrace, not added to crew. Record 0047 lists "the rows' time by holder" among the readings crew keeps for good. So this change is a reading: it adds no wait, no hold, no stall detector and no record of its own.

What crew reads today, on main at e20636f:

- The run record (read from the branch alone, `read.5`) holds every `bolt.give`, every `stage.start` and `stage.end` of a unit or chore, every `fix.start`, `fix.merge` and their `stage.end`, every `card.post` and `card.close` with its key and object, and every `host.hold` and `host.go`. `rail_record` already reads sixty days of it for the rail and the board.
- Each kit's gather (`gather.py`) reads the submissions standing in sluice from `sluice overview --json`, or from the follower's overview watch (`submissions_of`), and `submission_rows` gives each to its bolt's line. A standing submission carries its `submitted` time and state. A candidate under test carries the time its checks `started`.
- sluice 0.51.3's record of a decided submission, `sluice status <branch> --all --json`, gives `submitted`, `told` and `state` for every submission the branch ever had, and stays readable after `branch delete` (read on deneb 2026-10-28 for `bolt/crew-costs-an-idle-host-nothing`). It does not give when a decided submission's checks began. sluice's own log under the git folder has that, but crew reads no folder of sluice's (the follower's spec). The overview's `recent` holds only the last few landings and blames.

Area pages touched: `plan.md` (`plan.py`, `gather.py`), `record.md` (`record.py`), `docs.md` (README, the specs), `briefs.md` (the crew skill) and `tests.md`.

## Goals / Non-Goals

**Goals**

- Every held bolt's head line, on the board, in its JSON and in the bands, and its line on its kit's landings row on the rail, says its age, its minutes by holder, and who holds it now and since when.
- `bolt.land` records the age and the split.
- Every holder's reading, and the split, are pinned by logic-tier cases.

**Non-Goals**

- No hold or stall of crew's own: no wait, no notice to a conductor or the operator, no card (`teams.23`'s tells are Flume's, record 0044 as accepted, `roles.5`).
- No clock, size or bound on a bolt (`plan.20`, the user's correction of 2026-10-27).
- No row on the rail for a bolt still being built: the rail lists what waits on the user, and a building bolt is read on the board.
- No change to `crew bolts`, the board page (`page.html`) or the fleet page beyond the JSON key they ignore.

## Decisions

### 1. One holder per minute, in a fixed order

A bolt's time from its newest give to now (or to its landing) is cut at every start and end the facts hold. Each piece goes to the first holder that applies:

1. **team**, while a stage of the bolt's work runs other than a merge (construct, code, verify, settle, a fix's code);
2. **kit**, while one of the bolt's submissions is under test, from the start of its checks to its decision;
3. **team**, while a merge stage runs, or one of the bolt's submissions stands in sluice not under test (queued, waiting, passed, landing);
4. **user**, while a card of the bolt's is open;
5. **hold**, while a hold is recorded on the bolt;
6. **nobody**.

A team at work is not idle, whatever else is happening, so its stages come first. A gate's checks are the gate's even while the merge agent waits on them, so the kit beats the merge stage. A submission standing with nothing testing it is the team's (`plan.20`'s words): before sluice's driver runs on a host, a standing submission moves only while its submitter waits on it. Waiting on people counts only when nothing is moving, and a hold only when no one else holds the bolt. The shares then sum to the age, and an idle team, a hold or a slow gate each shows as its own minutes.

The decision is `bolt_time(start, end, stages, submissions, cards, holds)` in `plan.py`, a function of plain facts that starts no process (`code.7`). It returns the age in minutes, the share of each holder, and who holds the bolt at `end` with since when and what for. It is called at draw time with the time now, so the follower's redraw from a kept read (`plan.12`, the follower's spec) ages the line without reading anything again.

*Alternatives:* shares that overlap (a stage and a gate both counted) would not add up to the age, and would hide which of them the bolt waited on. A share by unit would not answer the user's question about the team.

### 2. Each holder from what crew already keeps

- **Give**: the newest `bolt.give` on `bolt/<b>` not refused. A bolt given before the sixty days the rail reads, or a run record that can't be read, gives no start, and the line says the age can't be told and why (`read.1`).
- **Stages**: each `stage.start` naming `unit/<u>` or `chore/<c>` of the bolt, or `fix.start`/`fix.merge` naming `fix/<b>/<f>`, not refused, paired with the next `stage.end` naming the same stage object and agent. With none yet, it runs to now. A merge is told by its `stage/<u>/merge` object or its act, `fix.merge`.
- **Submissions**: the bolt's lines' submissions on `bolt/<b>`, and its landings on main, by `submission_rows`' rule (from `unit/<u>`, `chore/<c>`, the fix's branch, `bolt/<b>`, or a pull request opened from it). Standing ones come from the overview the gather or the watch read, decided ones from `sluice status --all`. Each has `submitted`, `started` and `decided`:
  - A standing submission under test takes `started` from the testing candidate that holds it.
  - A decided submission takes `decided` from `told`, and has no `started` in sluice 0.51.3's record, so it counts as under test from `submitted` to `told` (Decision 3).
  - A record the gather could not read leaves the split unknown, said with sluice's words.
- **Cards**: `card.post` to the `card.close` of the same card (or now). A card is the bolt's when:
  - its key is `land/<b>`;
  - it is a `batch/<n>` whose batch holds a unit or chore of the bolt;
  - it is a `proposal/<n>` whose changes, in the plan's proposals file, name the bolt or its work;
  - it is `land/<kit>` of the bolt's kit, from the end of the bolt's last merge stage on;
  - it is a question (`plan.card_kind`) posted by an agent of the team holding the bolt, `<team>-conductor`, `<team>-ops` or `<team>-unit-<n>`, while the team held it;
  - or its post's `On` names `bolt/<b>` or the bolt's work.

  A card lost to its owner and posted again counts as one open card.
- **Holds**: the team's host's `host.hold` to its `host.go`, read from the same entries, what for being "its host <h> is held by <by>". That is the one hold crew records today.

### 3. A decided submission's stay is the kit's whole

sluice's reader contract (`status --json`, the overview) gives no start of checks for a decided submission. Counting its time queued as the team's would need a time crew cannot read, and `read.1` forbids a guess. So its whole stay, `submitted` to `told`, is the kit's. On a bolt's branch a submission queues only behind another of the bolt's own merges under test, which is the kit's too, so the over-count is the queue's wait for a round with no waiter. A standing submission is split exactly, and its queued minutes move from the team to the kit once it is decided. This is said in the code where the rule lives, and it goes when sluice's record gives each submission its checks' start (named in this unit's final message as a reading for sluice).

### 4. Holds come from records, not from a conductor's waits

`teams.22`'s details of 2026-10-27 named a conductor's `crew card wait` or `crew unit wait` as the hold to say on the row until Flume holds. `crew card wait` is gone on main since record 0046 (`teams.24`, landed in e20636f): a card's answer is Pending You's record, and a bolt waiting on one is the user's time by Decision 1. A `crew unit wait` waits on a stage that runs, which is the team's. Neither leaves a minute a hold would take. Reading them would also mean reading every conductor's transcript at every refresh, against record 0047's direction that crew stops reading transcripts for stages. So the hold share is read from holds crew records, a host's hold. The read of Flume's holds (flume record 0008) belongs to move 5, when crew's kits run under Flume, and is not built here. `bolt_time` takes holds as plain facts, so that read only feeds it.

### 5. Where the line is drawn

- **Board**: `board_data` gives each ledger a `time`: `{age, shares: {team, kit, user, hold, nobody}, now: {holder, what, since}, stalled}`, or `{unknown: why}`. `bolt_row` draws it after the merged count, `3h 05m: team 2h 10m, kit 12m, user 40m; user since 14:02, batch/12`. With a hold the words name it, `held since 14:02: its host deneb is held by chuck`. Once nobody has held the bolt five minutes (`teams.23`'s measure), it says `stalled since 14:02`. A zero share is left out, and minutes use `plan.age`'s form.
- Every view that draws `bolt_row` (`ledger_rows` for the conductor, `team_rows` for the planner and the operator) and the board text get it with no other change. The views stay lists of segments, so `status.js` draws them as it is (`code.8`). The mod's cases gain one drawing a head line with its time, and `test_board.py`'s key-pinning case gains `time` if the mod is made to read it.
- **Rail**: `rail_rows`' land line ends with the same words, from the same facts the read holds, so the rail and the board agree (`crew-board`'s "one read").

### 6. The landing entry

`bolt_land` reads the bolt's facts at its landing. It already has the partition's entries. It reads sluice's records of `bolt/<b>` and main on the team's host through the host run it already makes. It computes `bolt_time` up to the landing submission's `told`, or the entry's own time when none landed, and writes `Age` (minutes) and `Split` (`team 200, kit 25, user 125, hold 0, nobody 20`) on `bolt.land`. Both are new fields in `record.EXTRA` and the descriptor's `%allowed`, added as `Answer` was. They hold no typed text (`record.3`). A fact it can't read leaves both fields off and the landing goes on (`record.2`'s spirit: a reading never changes what the command does). The sibling unit `a-landing-is-read-from-sluices-record` (`plan.21`) moves where `bolt.land` is written. The fields go on that write, wherever it lands, by the same helper.

### 7. The gather reads decided submissions

For each bolt it is asked about, `gather.kit` runs `sluice status bolt/<b> --all --json`, and once per kit `sluice status main --all --json`, in the kit's main checkout. Every field is guarded as `submissions_of` guards it (`read.2`), and failures are said in sluice's words (`sluice_said`). It returns them with the kit as `history`, or `history_error`. A follower's refresh on a queue's move gathers nothing (the follower's spec): the history then stays as the last gather read it. A submission no longer standing and not yet in the history counts as it last stood up to the new line's time. `gather.py` stays standard-library only (`code.1`).

## Risks / Trade-offs

- [A decided merge's queued minutes are counted to the kit] → Decision 3. Small on a bolt's branch, and gone when sluice gives the start.
- [`sluice status main --all` grows with main's history] → One process per kit gather, which runs only when a kit moved. The gather filters to the asked bolts and parses nothing else.
- [A bolt given more than sixty days ago] → Its age can't be told and it says so. No bolt of the fleet's is that old.
- [Card ownership rules miss a card] → Its minutes read as nobody's, which shows as idle and is visible to the user. The rule's list is in one function with its cases.
- [The sibling unit's landing write and this unit's fields meet in `plan.py`] → Same bolt. The conductor orders them, and the field helper is one call.

## Migration Plan

None. The bolt's branch was cut at c5b086a, before `crew-costs-an-idle-host-nothing` landed the submission rows and the follower's watch this design builds on. The bolt takes main in before code, as `teams.21` has it.

## After deploy

None: every behaviour here is read from records and proved in the logic and contract tiers. Nothing waits on a live host.

## Open Questions

- sluice: give each submission's record the time its checks began. This is a reading for sluice's side, named to the team. Decision 3 stands until then.

## Task notes

**1.1** `plan.py`: `bolt_time(start, end, stages, submissions, cards, holds)` per Decision 1:
- `stages`: `[{start, end|None, merge: bool}]`.
- `submissions`: `[{submitted, started|None, decided|None, state}]`.
- `cards`: `[{at, until|None, key}]`.
- `holds`: `[{at, until|None, what}]`.

It returns `{age, shares, now: {holder, what, since}, stalled}`, minutes as ints, stalled once nobody has held five minutes (`STALLED = 5`). Cases in a new `tests/py/test_bolt_time.py`, one per scenario of the `crew-board` delta's head-line requirement, plus:
- the shares sum to the age;
- a stage with no end runs to `end`;
- a card closed before the give is left out;
- a standing submission with state `testing` and no `started` counts from `submitted`.

**1.2** `plan.py`: `bolt_facts(entries, plan, bolt, team, kit_name, submissions, history)` turns run-record entries and sluice's submissions into `bolt_time`'s facts, per Decision 2: the give, the stage pairs, card ownership (the batches by `batches()`, proposals by the plan's proposals file, `land/<kit>` from the last merge's end, team questions by `card_kind` and the agent's team) and host holds. It returns `{unknown: why}` when the give or the history can't be read. Cases in `tests/py/test_bolt_time.py` from entries built as `tests/py/facts.py` builds them.

**2.1** `gather.py`: `history(main, bolts)` runs `sluice status <branch> --all --json` for each `bolt/<b>` and main, parsed by a guarded `decided_of(doc)` returning `[{id, branch, head, state, submitted, told, worktree, pull_head}]`. `submissions_of` also gives each standing submission's `submitted`, and `started` from the testing candidate holding it. `kit()` returns `history`/`history_error` for a kit asked bolts of. Record sluice 0.51.3's `status bolt/<b> --all --json` and `status main --all --json` (trimmed, as `tests/py/sluice-0.51.3/README` describes its overview) beside `overview-standing.json`, with a README line. Logic cases for `decided_of` in `tests/py/test_bolt_submissions.py`, and a contract case in `tests/contract/test_gather.py` running the gather against a scratch kit with the stub or real sluice as that file does.

**2.2** `board.py` follower (`Follower`, `queue_of`): a queue move keeps the last gather's `history`. A submission that left the standing list and is absent from the history is kept as it last stood, decided at the line's time. Cases in `tests/py/test_board.py` beside the follower's queue cases.

**3.1** `board.py`: `board_data` puts `time` on each ledger from `bolt_facts` and `bolt_time` at `now`. `bolt_row` draws it (Decision 5). Cases in `tests/py/test_board.py`: a head line per holder, stalled, unknown, and `agent_views` for a conductor and the planner showing it. `plugin/tests/status.test.ts`: a band drawing a head line with its time.

**3.2** `plan.py`: `rail_rows` ends each land line with the same words, from the read's entries and the kit's submissions. A case in `tests/py/test_rail.py`: a land line's time equals the board's for the same read.

**4.1** `record.py`: `Age` and `Split` in `EXTRA`, the descriptor's `%allowed` and the fields comment. `plan.py` `bolt_land`: reads history on the team's host (`host_run`, a script beside `SUBMISSIONS` taking the bolt), computes the split to the landing's `told`, and writes both fields, or neither when a fact can't be read. Cases in `tests/py/test_landing.py` for the fields' words and for neither on an unread history. `tests/t-journey-land.sh` asserts the entry holds `Age` and `Split` if that test's stub sluice can answer `status --all`; else the logic case stands alone.

**5.1** README's board and rail sections, and `plugin/skills/crew/SKILL.md` where it describes the board's head line, say the age, the shares and the holder (`docs.2`). `tests/t-docs.sh` passes.

**5.2** `tests/moon-tasks` run and `tests/moon.yml` committed if a test's reads changed (`tests.10`). `tests/suite --affected` ends with "0 failed".

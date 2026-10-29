# Design

## Context

This bolt, `crew-reads-a-bolts-time-and-its-landing`, already holds the merged unit `a-bolts-row-shows-its-age-and-who-holds-it`. That unit gives each held bolt's row its age and who held its time (`plan.20`, record 0044 outcome 5). Its gather (`gather.kit`) calls `history(main, bolts)`, which runs `sluice status bolt/<b> --all --json` for every bolt asked and `sluice status main --all --json` once more, at every gather of every kit. The follower's `requeue` then patches that history between gathers with `board.kept_gone`. That is the call this unit removes.

What the sources say:

- **sluice ADR 0023**: `sluice overview --json [--watch]` is a reader's one contract. A reader finds what happened by comparing each branch's `recent`, the last ten `landed`, `blamed` and `conflict` events of its log.
- **sluice clause 129**: on one host, one process reads a repository's records for everyone watching.
- **The crew-board spec** (as this bolt holds it): the follower keeps one overview watch per kit (`The follower follows each kit's queue through sluice's overview`).
- **`read.1`**: what crew can't read is said, never guessed.
- **`plan.20`**: the team holds "a stage running or a submission in a gate", and the kit holds "a gate's checks running".
- **`plan.21` and record 0046 part 2**: a landing's number is recorded from its submit (`bolt.submit`, `Outcome: queued`, `Submission`). Every submission's number is on its row from the submit.
- **sluice record 0067** (accepted, not built in sluice v0.57.1): a run's record will carry each step's time. Until it does, nothing of sluice's records gives a decided submission's checks' start.

What the overview carries, read on deneb on 2026-10-29 with sluice 0.56.0 in crew's own checkout:

- Each branch's standing `submissions` have `id`, `branch`, `from` (`worktree`, `head` for a pull request's branch, `path`), `state` and `submitted`.
- Each branch's `candidates` have `state`, `started` (for a testing candidate) and `submissions`.
- Each branch's `recent` events have `event`, `at`, and `ids`, a list of numbers. sluice 0.51.3 printed a single `id` instead (`tests/py/sluice-0.51.3/overview-standing.json`).
- `recent_from` maps each event's number to the branch it came from, such as `unit/<u>` or `pull/<n>`.

So a decision's time is in the overview the watch already prints, on the line where the submission leaves the queue. A submit's time and a checks' start are in the lines while it stands.

Area pages touched:

- `plan.md` (`plan.py`, `gather.py`): `plan.20`, `plan.21`, `plan.12`'s follower reading.
- `record.md` (`record.py`'s comment).
- `docs.md` (README, the specs, `docs.2`, `docs.4`, `docs.6`).
- `briefs.md` (the crew skill).
- `tests.md` (`tests.10`, `tests.11`).

Core rules relied on: `read.1`, `read.2`, `code.1`, `code.7`, `code.8`, `state.4` (and its reading of 2026-10-28: the follower's kept read is a derived cache) and `roles.5` (crew reads sluice, it builds nothing sluice holds).

## Goals / Non-Goals

**Goals**

- A kit's gather starts no `sluice status`, ever. It starts no sluice process at all when the follower hands in its watch's queue.
- The follower keeps each held bolt's submissions from their submit to their decision, taking every fact from the overview lines it already reads.
- A decided merge's stay is split at its checks' start where crew holds it. Where crew doesn't hold it, the stay is shown as team-or-kit, never the team's under the merge stage and never the kit's whole.
- The landing entry's `Split` follows the same rule.

**Non-Goals**

- No change to the landing's one read of sluice's record on the team's host (`landing_time`, `HISTORY`), or to the landing read of its submission (`plan.21`). Those are reads made once at an act.
- No read of sluice's run record for checks' start. That waits on sluice record 0067 being built, and then it is a unit of its own.
- No file kept by the follower across its restarts. Its kept submissions are a derived cache in memory (`state.4`), and what a restart loses is said as team-or-kit.
- No change to `crew bolts`' text, the rail's rule or which bolts are asked about.

## Decisions

### 1. The gather reads sluice only through the overview

- `gather.kit` drops its `history(...)` call and its `history`/`history_error` keys. `history` and `status_all` go from `gather.py`. `status_read` and `decided_of` stay, since `plan.history_read` uses them for the landing's one read.
- When the follower hands in `queued`, the gather starts no sluice process. Otherwise it runs its one `sluice overview --json`, as now.
- The gather's answer gains `decided`: the decided submissions the overview's `recent` names. For each, its number, the branch it was decided on, where it came from (`recent_from`), the event, and the event's time as `decided`. It has no `submitted` and no `started`.
- A new guarded reader, `gather.decided_in(doc)`, reads `ids` or `id`, guarding every field as `submissions_of` does (`read.2`).
- When the follower hands in `queued`, it hands in its kept `decided` too (Decision 2), and the gather returns that.

### 2. The follower keeps each submission from its submit to its decision

`board.Follower` keeps, per kit `(host, main)`, a map from submission number to its facts: `{id, branch, worktree, pull_head, submitted, started, decided, event}`. A new decision of facts, `board.kept_submissions(kept, doc, bolts)`, updates the map from each document the watch or the clock's ask reads, and from the overview a gather gives back:

- Each standing submission of a bolt the read asks about, or on main from one, is added. Its `submitted` comes from the document. Its `started` comes from the testing candidate that holds it, once one does, and is never cleared afterwards.
- Each kept submission the document no longer holds standing is decided:
  - at the `at` of the branch's `recent` event that names it, its event kept;
  - else at the document's own `at`, with event `gone`, which is a withdrawal or a decision the ten-event window missed.
  - A document with no time decides nothing (`read.1`, as `kept_gone` held).
- A decided submission the document's `recent` names and the map lacks is added with `decided` alone. These are the ones decided before the follower saw them.
- A submission of a bolt no longer asked about is dropped.

The map replaces `kept_gone` and the kept `history`. `requeue` gives each moved kit's answer `decided` from the map, and a gather's answer is given the map's too, so a gather never throws away what was kept. On a follower restart the map starts from the first document's standing submissions and its `recent`.

*Alternatives:*

- A `sluice status <n> --json` read once at each decision. It is one process per decision. The overview line that shows the decision already names its time in sluice's own log, so it adds nothing but a process.
- Keeping the map in a file across restarts. That would be state crew can't remake from the files (`state.4`), and a restart is rare.

### 3. The holder rule follows `plan.20`, with an unsplit share

`plan.bolt_time` gains a holder `team-or-kit` (`team_or_kit` in the JSON) between kit and the merge stage. Its order, first match wins:

1. **team**: a stage other than a merge runs.
2. **kit**: a submission under test, from its `started` to its `decided` (or now).
3. **team-or-kit**:
   - a submission with no `started`, from its `submitted` to its `decided` (or now, while it stands `testing`);
   - and, for a merge stage that ended, its whole run when crew holds no `submitted` of that stage's work between its start and its end.
4. **team**: a merge stage runs; a submission stands queued; or a decided submission's stretch from `submitted` to `started`.
5. **user**.
6. **hold**.
7. **nobody**.

`plan.20` names the team as holding "a submission in a gate" and the kit "a gate's checks running". So a known queued stretch stays the team's. The kit holds checks with a known start, and a stay crew can't divide goes to neither. That keeps `read.1`: the line does not guess and does not count those minutes under the merge stage as the team's. It replaces the merged unit's Decision 3, which counted the whole decided stay as the kit's.

A merge stage's work is the `unit/<u>`, `chore/<c>` or fix branch its entry names. A submission is that work's when its `worktree` is that branch. `bolt_facts` hands each stage its `work`, and each submission its `worktree`.

A decided submission with only `decided`, and no `submitted`, places no minutes itself. It only marks that the merge it ended was submitted at a time crew doesn't hold. The merge stage rule above covers that run.

The shares still sum to the age. `HOLDERS` becomes `("team", "kit", "team_or_kit", "user", "hold", "nobody")`. `time_said` names the share `team or kit` and the holder now `team or kit since 14:05, #41`. Where any team-or-kit minutes show, it adds once: `team or kit: sluice keeps no start of its checks`.

### 4. Submissions are matched to the bolt from the overview and the run record

`bolt_facts(entries, plan, bolt, team, host, kit_name, submissions, decided, unread=None)` takes the kept or overview `decided` in place of `history`. It matches a submission to the bolt as it does now, by `worktree` or `pull_head`. It also matches a main submission whose number is the `Submission` of the bolt's queued `bolt.submit` in `entries`, because `recent_from` gives `pull/<n>` alone for a landing by pull request.

When neither the queue nor `decided` can be read, it says so (`unknown`), as today. A decided submission with no `decided` time can't be placed, and is said as today.

### 5. The landing's split follows the same rule

`landing_split` keeps its one read (`landing_time`, `HISTORY`, `history_read`) and maps `told` to `decided`. sluice 0.51.3's record gives no `started`, so a landed bolt's decided merges are team-or-kit there. `Split` is written `team 200, kit 0, team-or-kit 25, user 125, hold 0, nobody 20`.

`record.py`'s comment on `Split` names the new share. `Age` is unchanged.

### 6. Views

`board_data`'s ledger `time` carries the new `shares` key. `bolt_row` draws `time_said` as now. The bands get the same words through `ledger_rows` and `team_rows`. `status.js` draws segments and reads no share key, so it is unchanged unless the mod's case for a head line with its time shows otherwise. `test_board.py`'s JSON case pins the new key (`code.8`).

## Risks / Trade-offs

- **The follower restarts, and a bolt's earlier merges read team-or-kit.** That is honest (`read.1`). The landing entry still reads sluice's record once, and a restart is rare.
- **A decision missed by the ten-event window.** It is decided at the line's own time, at most one watch line late, which is seconds.
- **The overview's `recent` shape differs between sluice versions** (`id` against `ids`). Both are read and guarded, and a new recorded document pins the current one.
- **Most landed bolts' `Split` will show team-or-kit for their merges** until sluice keeps checks' start (record 0067). That is the truth crew can read, not a regression in what is known.

## Migration Plan

None. The kept `history` key leaves the gather's answer and the follower's kept answers in the same change. A follower running the older crew restarts on deploy.

## After deploy

None. Every behaviour here is a decision on facts or a gather's call, each proved in the logic or contract tier. Nothing waits on a live host.

## Open Questions

- sluice: record 0067's run record, or the submission's own record, to carry when a submission's checks began, so a decided merge's stay can be split after the follower restarts and at the landing. Already accepted on sluice's side. Reading it is a later crew unit.

## Task notes

**1.1** `gather.py`:
- Remove `history` and `status_all`, the gather's `history(...)` call, and the `history`/`history_error` keys. Keep `status_read`, `decided_of` and `sluice_ran` for `plan.history_read`.
- Add `decided_in(doc)`: for a `sluice/overview@1` document, `([{id, branch, worktree, pull_head: None, event, decided, submitted: None, started: None}], None)` from each branch's `recent` (the `ids` list or a single `id`) and `recent_from`, every field guarded; `(None, why)` as `submissions_of` says it for another schema.
- `kit()` puts `decided` from `req["decided"]` when the follower hands it in (with `queued`), else from `decided_in` of the overview it read.
- Update the module docstring.

Logic cases in `tests/py/test_bolt_submissions.py`: `decided_in` over the recorded documents, the `id` and `ids` forms, a mistyped field left None, another schema refused.

Record the host's current sluice overview, trimmed to a branch with recent events, as `tests/py/sluice-<version>/overview-recent.json`, with a README line as `tests/py/sluice-0.51.3/README` has it.

**1.2** `tests/contract/test_gather.py`:
- Replace `test_a_kits_gather_reads_sluices_record_of_each_asked_bolt_and_of_main_once_each_in_its_main_checkout` with a case where sluice is a script on the path that logs every call. A gather with `queued` handed in starts no sluice process. One without it runs `overview --json` once and no `status`, for two asked bolts and main.
- Extend `test_a_kits_queue_handed_in_is_its_submissions_and_sluice_is_not_run` with `decided` handed in and returned.
- In `tests/t-journey-board.sh`, after the follower's first read of the box's kit, assert that the test log holds no `sluice status` call. That is the end-to-end proof that a gather on a host starts none.

**2.1** `board.py`:
- Add `kept_submissions(kept, doc, bolts)` per Decision 2, a decision on facts (`code.7`).
- The follower keeps the map per kit, updated in `requeue` and after a read's gathers seed the watches.
- Each kept answer's `decided` comes from it, and `queued` hands go with a `decided` hand.
- Remove `kept_gone` and its cases.

Cases in `tests/py/test_board.py`, one per scenario of the delta's follower requirement:
- a merge decided between gathers, taken at its recent event's time and kept after a gather;
- a withdrawn merge, taken at the line's time;
- one decided before the follower saw it, added with `decided` alone;
- a bolt no longer asked about, dropped;
- a line with no time, which decides nothing;
- `started` kept once seen.

**3.1** `plan.py` `bolt_time`, `HOLDERS`, `time_said`, per Decision 3: stages carry `work`, submissions `worktree`, the new rank and the merge stage rule. Cases in `tests/py/test_bolt_time.py`:
- Replace `test_a_decided_merge_whose_checks_start_is_not_kept_is_the_kits_whole_stay` and `test_a_standing_submission_testing_with_no_start_of_checks_counts_from_its_submit` with the delta's scenarios: a decided merge with its checks' start, one without, and a merge that ended before the follower saw it.
- Add a merge stage still running with no submission held, which is the team's.
- Add the words `team or kit 12m` and the holder now.
- The shares-sum case covers the new share.

**3.2** `plan.py` `bolt_facts` per Decision 4: `decided` in place of `history`, each stage's `work`, and the landing matched by the queued `bolt.submit`'s `Submission`. `held_time` reads `decided`, with `decided_error` when it can't be read. Cases in `tests/py/test_bolt_time.py`:
- the landing by pull request matched by its number;
- `test_the_bolts_submissions_standing_over_its_record_and_none_of_another_bolts` over `decided`;
- the unread cases renamed.

`tests/py/test_rail.py`'s cases that set `history` set `decided`.

**4.1** `plan.py` `landing_split` per Decision 5, and `record.py`'s comment on `Split`. Cases in `tests/py/test_landing.py`: the delta's run-record scenarios, `Split` naming team-or-kit and summing to `Age`. `tests/t-journey-land.sh` is left as it is unless it asserts `Split`'s words.

**5.1** `board_data`'s `time` per Decision 6. `test_board.py`'s `test_the_json_carries_the_age_the_shares_and_the_holder_now` holds `team_or_kit`. A band case in `plugin/tests/status.test.ts` draws a head line with a team-or-kit share, and `status.js` changes only if that case fails.

**6.1** README's Construction paragraph and `plugin/skills/crew/SKILL.md`'s description of the head line say the follower reads sluice only through the overview, and that a stay crew can't split is shown as team or kit (`docs.2`). `tests/t-docs.sh` passes.

**6.2** Run `tests/moon-tasks` and commit `tests/moon.yml` if a test's reads changed (`tests.10`). Run `tests/suite --affected`, which must end with "0 failed".

# Design

## Context

See proposal.md for why. The user's word, 2026-11-03, Pending You req_6b236a29: "Deneb only now; the box later." This is the further word swancloud record 0044 waits on, as amended 2026-11-02: "crew without teams (record 0047 move 5, landed in crew at 9d590e9f) reaches a host on a further word of the user's, once every team there has crossed and its bolts landed".

How crew without teams came and went on main, each landing reachable from main's history:

| Landing | Commit | What it did |
|---|---|---|
| #416 `change/the-team-machinery-leaves` | a2aa2c9d, on `bolt/crew-runs-its-work-through-flume` after 9913f249 (#415, `roles-run-as-flume-kinds`) | The team machinery leaves crew; `teams.json` at version 5 alone; the change archived and its deltas synced into `openspec/specs/` |
| #417 the bolt | 9d590e9f | The bolt merged onto main beside main's #410 to #413 |
| #418 `design/teams-leave-the-pages` | ab7f9006 | The design agent's amendments of `docs/architecture/` and record 0052 for #417 |
| #419 Opus | ccb5f9a9 | The design agent and the planner on Opus 5.5 |
| #420 version 2 again | 68d23639 | All of the above taken off main, after #417's deploy refused every host's teams file |
| #421 Opus again | 3fd28002 | #419's fix on the team crew |
| #423 `change/teams-cross-to-flume-on-main` | 09b2cf4d | The bolt's `roles-run-as-flume-kinds` and `teams-cross-to-flume-as-their-bolts-land` brought onto main: the crossing step and roles as Flume kinds |
| #425 to #428 | a3b88c1f, b7a3614c, 808202bd, 2c8b9786 | Design records: the user's words as theirs, record 0052's amendment accepted, `briefs.15`, two lines of `plan.md` |
| #430 `bolt/a-quiet-agent-that-committed-is-not-stuck` | b9ca0eaf | A stuck report carries the agent's last words and the branch's commits; the conductor reads it before it asks |
| #435 `bolt/crews-chores-of-the-24th-night` | f3c5abd4 | A proven bolt's batch is reckoned at once wherever it lives; a stage drives a browser only the kit's way |

So ccb5f9a9's tree is the teamless crew as main last held it, and 09b2cf4d's tree is #415's bolt plus main's #410 to #413 and Opus: the crew #416 was cut from, as main holds it again. The difference between the two trees touches exactly the files #416, #418 and #419 touch (read 2026-11-03: no file outside them, and none of theirs left out). Applied three-way onto main's tip f3c5abd4, it conflicts in 21 files, each one #425 to #435 touched (*Decision 2*).

Area pages this change touches: every one. `core.md` (`roles.1`, `roles.4`, `roles.8`, `code.3`, `code.5`, `code.8`); `teams.md`, `plan.md`, `record.md`, `signals.md`, `briefs.md` through the code and briefs #416 changes and the pages #418 amends; `tests.md` (`tests/`); `docs.md` (README, the specs, `docs/architecture/`).

## Goals / Non-Goals

**Goals:**

- A commit on `teamless/deneb`, cut from main at f3c5abd4, holding the teamless crew exactly as #416, #418 and #419 built it, reconciled with what main has landed since.
- crew there reads `teams.json` at version 5 alone and refuses any other version, or a `teams` key, as #416 had it.
- Every check crew's gate requires of main passes on it under `sluice exec main`.

**Non-Goals:**

- Landing anything on main, or touching the box. Main keeps the team machinery, its specs and its pages for chuck-herdr-alpha until the user's word for the box.
- Changing what the teamless crew does. No decision of #416's is reopened, and nothing new is designed beyond what a conflict needs to resolve.
- swancloud's pin of deneb's crew, deneb's teams file, and swancloud record 0044's amendment for them. These are swancloud's.
- Rewriting a record in `docs/adr/`. Main's records stand as written.
- Archiving this change. That is the flow's, after its code and verify.

## What this change rests on

1. **The landings above, as committed.** a2aa2c9d, ab7f9006, ccb5f9a9 and 09b2cf4d are all in main's history, so the application reads them from crew's own clone.
2. **The runner on deneb.** The teamless crew launches a kit's work through the flywheel runner on the kit's host and reads where it runs from that runner's report (`roles.9`; #416, Decision 4). deneb runs the runner under swancloud record 0044's `runner` flag.
3. **swancloud, in one deploy on the user's word.** deneb's crew is pinned to the commit this change pushes, and deneb's `~/.config/crew/teams.json` is written at version 5, the partitions whose main level runs on deneb, madswan and swancloud, each with `flume` naming its five roles `false`. The box keeps the fleet's pin and its own file. Record 0044 first had this shape as `teams = false`, and its amendment of 2026-11-02 withdrew it. Writing it again is swancloud's: its planner's unit, and its design agent's amendment of record 0044 on the user's word of 2026-11-03.
4. **deneb is drained.** Every team there has landed its bolt and is closed, and its main levels are down (the brief of 2026-11-03), so no agent on deneb runs a brief the teamless crew does not know (`read.4`).

## Decisions

### 1. The teamless crew comes back by one three-way application

The branch takes the change from 09b2cf4d's tree to ccb5f9a9's, applied three-way onto f3c5abd4. The mechanism is a cherry-pick of a commit made for it, ccb5f9a9's tree with 09b2cf4d as its parent, and that commit is never pushed. Everything #416, #418 and #419 changed comes back in one go: the code, the briefs, the tests, the end-to-end world, README, CLAUDE.md, the pages, the archived change `2026-11-01-the-team-machinery-leaves` with its verify, and the specs synced from it. The 21 conflicts are resolved by Decisions 2 to 6, and the result is committed as one Conventional Commit marked breaking (`code.6`).

Why this base: 09b2cf4d is the crew #416 was cut from, with main's #410 to #413 and Opus as #417's and #419's landings already resolved them. So the conflicts left are exactly where main moved after it.

Alternatives considered:

- Cherry-picking #416's landing against 9913f249 and #418's against 9d590e9f. This conflicts in 22 files and 4 pages, and has to resolve again what #417's merge already resolved.
- Writing #416's deltas again in this change instead of restoring its archive. That duplicates some 3,000 lines of deltas, and leaves the archive #420 removed missing from the record of why the specs say what they say.

### 2. A later landing that touched team machinery goes with it, and one that changed what stays keeps main's

This is the brief's rule, held to `the-team-machinery-leaves`'s own two rules (its Task notes). **Reachability decides**: a function, constant, case or line that the teamless crew still calls stays, however team-shaped its name. One only the old path calls goes, with its cases (`tests.4`). **A test of a staying feature is kept, never deleted for its setup.**

Each conflict, with ours meaning f3c5abd4 and theirs meaning ccb5f9a9:

| File | Main since #423 | Resolution |
|---|---|---|
| `README.md` | #430: a code stage ends at its commit alone | Theirs. The paragraph leaves with §Teams. |
| `docs/adr/0052-…` | #425: the amendment accepted on the user's words | Ours. A record keeps main's text. |
| `docs/architecture/_open.md` | #425: the runner's item accepted, deneb under v0.40.0 | Decision 6 |
| `docs/architecture/briefs.md` | #425, #426: `briefs.15`, records of the user's words | Decision 6 |
| `docs/architecture/core.md` | #425: `roles.9` and its details as accepted | Decision 6 |
| `openspec/specs/bolt-teams/spec.md` | #430: two requirements reworded and "A conductor reads a stuck report before it asks" added | Theirs. #430's added requirement is kept, and this change's delta removes it. The two reworded requirements go, since `the-team-machinery-leaves` removes them. |
| `plugin/bin/crew` | #430: `unit wait`'s stuck answer in the usage | Theirs |
| `plugin/lib/gather.py` | #430: `since` | Theirs (Decision 3) |
| `plugin/lib/plan.py` | #430: the stuck report in `stage_wait`; #435: `before_waiting`, `after_answer`, `after_delivery`'s order, `batch_reckoners` over every team, `batch_check`'s `fetch` | Theirs in every conflict, then Decisions 3 and 4 |
| `plugin/lib/transcript.py` | #430: `last_words` and its docstring paragraph | Theirs (Decision 3) |
| `plugin/roles/coder.md`, `verify.md` | #435: the browser words | Deleted, as theirs (Decision 4) |
| `plugin/roles/conductor.md` | #430: reading a stuck report | Deleted |
| `plugin/skills/crew/SKILL.md` | #430: a stuck stage's report | Theirs |
| `tests/contract/test_gather.py` | #430: `since`'s case | Theirs |
| `tests/py/test_batches.py` | #435: `TestReckonedAtOnce`, the every-team reckoner | Theirs |
| `tests/py/test_stage_ends.py`, `test_wait.py` | #430 | Deleted |
| `tests/py/test_transcript.py` | #430: `last_words`'s cases | Theirs |
| `tests/t-briefs.sh` | #425, #426: the design brief's record words; #430: the conductor's stuck words; #435: the browser words | Ours for #425's and #426's pins, built as theirs build a brief. Theirs everywhere else. #430's and #435's pins go. |
| `tests/t-journey-units.sh` | #430 | Deleted |

Every other file main changed since #423 merges cleanly and is kept as merged. Among them are `plugin/roles/design.md`, which carries #416's teamless words with #421's Opus and #425's and #426's record words, and `tests/py/test_rail.py`, which keeps #435's fixed clock (Decision 4).

### 3. #430's stuck report goes whole

A stuck report is the answer of a conductor's stage wait, and `the-team-machinery-leaves` removes the wait, the stage and the conductor. So everything #430 added goes:

- `plan.py`: `stuck_report`, `stuck_said`, `report_time` and the `look` and `stage_wait` they serve.
- `gather.since`.
- `transcript.last_words` and the docstring paragraph that reads Claude Code's message ids for it.
- The usage lines, README's line, the skill's bullet and the conductor's brief.
- The cases in `test_wait.py`, `test_stage_ends.py`, `test_transcript.py`, `tests/contract/test_gather.py`, `t-journey-units` and `t-briefs`.

`background` stays as ccb5f9a9 has it, since `hold.own_work` reads it (#416's Task notes 2.1), and `session_transcript`, which #430 drew out of it, stays only if that `background` calls it. Its archived change, `2026-10-29-a-stuck-report-carries-what-the-agent-said-and-did`, stays as history.

### 4. #435's batch reckoning goes with the wait, and the browser words with the stage briefs

#435 reckons a batch from a conductor's wait before it waits and at a merge's end, ahead of the landing card's hand (`before_waiting`, `after_answer`, `after_delivery`'s order), and from the rail's sweep over every team of the teams file (`batch_reckoners(found, teams)`). Both go. The teamless crew has no wait and no team: `the-team-machinery-leaves` reckons each partition's batch at every rail sweep and follower refresh on its main level's host, over every started bolt (its Task notes 5.3; review-batches). So awb-1's case of 2026-10-27, a bolt proven ten hours with no batch reckoned because no later wait came, cannot arise here: the sweep comes again at every refresh. `batch_check` keeps ccb5f9a9's signature, `(fleet, label, read=None)`, and its `fetch` parameter goes, since no caller would pass it. #435's fixed clock for `test_rail.py`'s branch-alone cases stays: it fixes a staying test.

The browser words #435 gave `coder.md` and `verify.md` leave with those briefs (#416, Decision 7). A Flume place is briefed by its kind and by the kit's own files, so crew has nowhere left to carry them. `_open.md` names them as left, for Flume's kinds or each kit's CLAUDE.md (Decision 6).

### 5. #421 and #423 need nothing of their own

ccb5f9a9 already holds #419's Opus, the same lines #421 wrote, so `agent-models`, the role definitions, `t-roles` and `t-journey-main` merge cleanly. #423 brought back the crossing as 09b2cf4d holds it, the base of the application, so #416's removal of the team path, the crossing and the `team.cross` entry applies as #416 made it. What #423 holds that stays is kept: roles as Flume kinds, the runner's records, and the launch digest that reads crew's own path as one word (#413).

### 6. The pages are #418's, around main's later records, and say where this crew runs

`docs/architecture/` and `_open.md` take #418's amendments: the rules the teams retire, and `roles.1`, `roles.4`, `code.3`, `code.5` and `code.8` as amended. The exceptions:

- Main's later records and the rules they amended stand as main has them: `roles.9` and its details as accepted (#425), `briefs.15` (#425, #426), and `plan.md`'s lines (#427, #428).
- The pages' citations of the reverted landing are rewritten. "With the landing of `the-team-machinery-leaves` (9d590e9f)", "(9d590e9f, #417)" and "since 9d590e9f" each name `the-team-machinery-leaves` as this change built it on `teamless/deneb`, dated 2026-11-03, for deneb alone on the user's word, with main keeping the rule for the other hosts. `roles.8` on this branch reads retired on those terms.
- `docs/adr/` keeps main's text whole, the citations in record 0052's accepted amendment among them. A record is history, and its amendment is the design agent's (`docs.7`).

`_open.md` keeps main's runner item, and drops what #418 drops: move 5's line, the stopgaps until move 5, and the team items under *Code against a rule*. It keeps #418's dev-server item, and gains two items:

- **crew without teams on deneb alone.** The user's word above, quoted. This crew is `teamless/deneb`, a branch of main that is never landed, pinned by swancloud for deneb. Main keeps the team machinery, its rules and teams file versions 2 to 4 for chuck-herdr-alpha's wldn teams until the user's word for the box. It names `plan.19`, `code.10` and main's `roles.8` as what it stands against until then.
- **The browser words of the stage briefs.** #435's words, on wldn's signal 2026-10-24-swb-2-conductor-1668df99/01, left with `coder.md` and `verify.md` and carried by neither crew nor a Flume place's brief, for Flume's kinds or the kits.

### 7. The checks are the gate's, run on the branch, and the branch is pushed, not submitted

Once committed, `sluice exec main` runs in the worktree the `check-full` tasks crew's policy requires of main that the head affects, open and under the host's bound (`.config/sluice.toml`; `tests.5`, `tests.10`). Every check passes, and `tests/moon-tasks` leaves `tests/moon.yml` in step first. The branch is then pushed to GitHub as `teamless/deneb`, without force (`state.5`), and nothing is submitted to main (`state.3`). Any later commit of the change's own stages on the branch is pushed there the same way. swancloud pins the branch's last commit, which `git rev-parse HEAD` reports in full.

### Rules relied on

`state.3` (nothing reaches main), `state.5` (no force), `code.5` (version 5 alone, as #418 amended it), `code.6` (a Conventional Commit, staged by path), `code.7`, `code.8` (the views and the mod follow, as #416 built them), `read.4`, `roles.2`, `docs.2` (README, the skill and the usage together), `docs.4` (the specs change through the restored archive and this change's delta), `tests.4`, `tests.5`, `tests.10`, `tests.11`, and every rule `the-team-machinery-leaves` relied on (its *Rules relied on*).

### Departures

- **`roles.8` (main's).** Main's `roles.8` has the old path leave crew "in a landing of its own once no team uses it". Here it leaves on a branch for one host while the box's teams still use it, on the user's word "Deneb only now; the box later." Main keeps `roles.8`, and with it every team's path, since nothing of this reaches main.
- **`plan.19` and `code.10`.** A host loads crew released at a tag of main that swancloud pins. deneb will load a commit of `teamless/deneb`, which no release tag carries, since CI tags main's pushes alone. Why: the user's word, and a release from main would reach every host, refusing the box's teams as #417's did. Until the box's word, `_open.md` says so (Decision 6).
- **`docs.7`.** A change's construct and code never edit `docs/architecture/` or `docs/adr/`. This change brings back #418, the design agent's own amendments, rewriting only their citations of the reverted landing, and resolves the pages' conflicts in favour of main's records. The brief asks for #418 to come back, and nothing of it reaches main, where the design agent remains the pages' one writer.
- **crew's last-task convention** (`openspec/config.yaml`: the last task runs `tests/suite --affected` and leaves the whole suite to sluice at the merge). There is no merge here, so the last check is the gate's own, `sluice exec main`, run by the coder (the brief), and the push follows it. A task proving the pages and the specs by `git grep` and `openspec validate` does so because no tier reads those files.

## Risks / Trade-offs

- **Two crews in one fleet.** deneb runs this crew on a version-5 file, and every other host runs main's release on its own file. A command one crew forwards to another host runs under that host's crew (`code.3`). The box's crew forwarding a team's command for a team that ran on deneb reaches deneb's crew, which has no such command and prints its usage. deneb's crew forwarding a main-level command to the box reaches the box's crew, which reads its own file. A partition's state branch is written by the crew of the host its main level runs on. So deneb's file naming deneb's partitions alone (*What this change rests on*, 3) keeps each partition with one crew. What the box's crew still reads of deneb's partitions is today's crew's and unchanged here. Accepted until the box's word. The swancloud unit that writes deneb's file is where it is read whole.
- **The branch drifts from main.** Main's later landings do not reach deneb until they are brought to `teamless/deneb`, and a fix landed on main for the team crew may not apply to it. Accepted: the user's "the box later" bounds the time. A later change brings the branch and main together.
- **History that cites the reverted landing.** The restored archive of `the-team-machinery-leaves`, its verify and main's records cite 9d590e9f and #417 as the landing. Accepted: they are records of what happened. The rule pages, which bind, cite this change (Decision 6).
- **A requirement of #430's stands in the specs until this change is archived.** The restored `bolt-teams` spec keeps "A conductor reads a stuck report before it asks" until this change's delta removes it at the archive. Accepted: that is how a spec changes (`docs.4`). The flow archives the change after verify.
- **The risks `the-team-machinery-leaves` named come back with it.** The teams file and the crew that reads it change together. A host with the new file and the old crew, or the reverse, refuses every command. A landing's hold is read from the run record, so it is unheld for the seconds a push takes. Each is mitigated as that design says, the first by swancloud's one deploy.

## Migration Plan

1. This change is built on `change/crew-runs-without-teams-on-deneb`, its checks pass under `sluice exec main`, and it is pushed as `teamless/deneb`.
2. swancloud pins deneb's crew to the pushed commit and writes deneb's teams file at version 5, in one deploy, on the user's word (*What this change rests on*, 3).
3. The user brings deneb's main levels up (*After deploy*).
4. On main, the design agent records the user's word of 2026-11-03 and where deneb's crew comes from. This change lands nothing on main, so main's pages cannot learn it from here.

Rollback is swancloud's: deneb's pin goes back to the fleet's release, and its file back to the version that release reads. Main never held this change.

## After deploy

- **deneb: bring the main levels up.** `crew main up madswan` and `crew main up swancloud`, run by the user once swancloud's deploy has pinned this commit and written deneb's version-5 file. Why no check can be code: a start of agents on a live host is the user's act (`roles.2`; swancloud record 0044, "The main level comes back by the user's hand"). No test in the coder's worktree can hold what runs on deneb after a deploy.

Nothing else: deneb's teams are closed and its main levels down before the deploy (*What this change rests on*, 4), so no agent of the team crew is left standing there to close.

## Task notes

Two rules hold for every task, `the-team-machinery-leaves`'s own: reachability decides what goes, and a task that deletes or adds a test, or changes what one reads, runs `tests/moon-tasks` and commits `tests/moon.yml` in the same commit (`tests.10`). Never run `wt submit --help` (CLAUDE.md), and submit nothing.

**1.1** Make the commit to apply, and cherry-pick it with no commit:

```
c=$(git commit-tree 'ccb5f9a9^{tree}' -p 09b2cf4d -m 'the teamless crew as ccb5f9a9 held it')
git -c merge.conflictStyle=diff3 cherry-pick --no-commit "$c"
```

Expect exactly the 21 conflicts of Decision 2's table, six of them modify/delete. A conflict anywhere else means main moved past f3c5abd4. Resolve it by the same rule and name it in the summary. Resolve each file as the table says. Take a deletion with `git rm` of that path alone, and stage every resolution by its path (`code.6`). No conflict marker is left (`git diff --check`), and `git status` shows no unmerged path. Commit once, as `feat!: crew runs without teams, as the-team-machinery-leaves built it, for deneb alone`, with a body naming ccb5f9a9, 09b2cf4d, the user's word and that nothing of it reaches main, plus a `BREAKING CHANGE:` footer saying `teams.json` is read at version 5 alone. Verify `tests/suite logic contract`.

**1.2** Run `git grep -n -e 'since(' -e 'last_words' -e 'stuck_report' -e 'stuck_said' -e 'report_time' -e 'before_waiting' -e 'after_answer' -- plugin tests`. Every hit is gone, or is a caller the teamless crew reaches, named in the summary. `gather.since` and `transcript.last_words` go with their docstrings and cases unless something staying calls them. `background` is ccb5f9a9's, and `session_transcript` stays only if it calls it. Tests: `test_transcript.py` and `tests/contract/test_gather.py` lose #430's cases. `test_wait.py`, `test_stage_ends.py` and `t-journey-units.sh` stay deleted.

**1.3** `plan.batch_reckoners`, `reckon_batches` and `batch_check` are ccb5f9a9's: `batch_check(fleet, label, read=None)`, reckoned for each partition whose main level runs on this host. No `fetch`, `ripe`, `before_waiting`, `after_answer` or team reckoner is left. `test_batches.py` is ccb5f9a9's, with no `TestReckonedAtOnce` and no every-team reckoner case. `test_rail.py` keeps #435's `AtNow` clock in `TestTheBranchAlone`.

**1.4** `plugin/roles/design.md` has ccb5f9a9's teamless words (the description, *Answering a design question*, `crew answer` to a waiting place), the Opus model, and #425's and #426's words on records: what the user settled in their own words is theirs, a record is proposed until seen, and a card asks only for a choice that is theirs alone. In `tests/t-briefs.sh`, #425's and #426's pins on the design brief build it as ccb5f9a9's t-briefs builds a main-level brief, by its partition. Pins on the conductor's stuck report and on the coder's and verify's browser words are gone, since neither brief is built. ccb5f9a9's check that no main-level brief names a conductor, team ops, a dispatcher, a slot, a give, `crew fix <team>`, `crew unit run|wait`, `crew needs` or `crew status <team>` stands.

**1.5** README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage are ccb5f9a9's, with nothing of #430's stuck answer or a code stage's end (`docs.2`). `t-docs`' README count holds as ccb5f9a9 set it.

**1.6** Run `tests/moon-tasks`. `tests/moon.yml` holds no task for a deleted test and no `# Reads:` path that is gone, and `tests/journeys.sh` is read where ccb5f9a9 reads it. Commit it if it changed.

**2.1** `openspec/specs/` is ccb5f9a9's, with two exceptions. `bolt-teams` keeps main's "A conductor reads a stuck report before it asks", which this change's delta removes. `agent-models` reads Opus 5.5 for the design agent and the planner, as ccb5f9a9 and main both have it. Both `openspec validate crew-runs-without-teams-on-deneb` and `openspec validate --specs` pass. The archives `2026-11-01-the-team-machinery-leaves`, `2026-10-31-roles-run-as-flume-kinds`, `2026-10-31-teams-cross-to-flume-as-their-bolts-land` and `2026-10-29-a-stuck-report-carries-what-the-agent-said-and-did` are all present.

**2.2** In `tests/py/test_teams.py`, `TestLoad` keeps ccb5f9a9's cases: another version refused naming 5 and `lib/crew-teams.nix`, 2 among them, and a file that lists teams refused at version 4 or 5. It gains one case for main-level's "The box's file at version 2": a version-2 file holding `partitions` and a `teams` list, shaped as `tests/lib.sh`'s `teams_old` writes it, refused with the version's words, crew having read nothing further.

**2.3** Apply Decision 6 to `core.md`, `teams.md`, `plan.md`, `briefs.md`, `record.md`, `signals.md` and `_open.md`. `git grep -n 9d590e9f -- docs/architecture` prints nothing, and `git diff f3c5abd4 -- docs/adr` shows only what the application brought cleanly. Where #418's record 0052 conflicted, the result is main's text.

**3.1** Run `sluice exec main` from the worktree's root once 1.1 to 2.3 are committed. It runs the `check-full` tasks the head affects against main's policy, and every one passes. A check that fails is fixed by the rule of Decision 2 and run again. The same check failing twice is a stop short (`flume needs`), naming it.

**3.2** Run `git push origin HEAD:refs/heads/teamless/deneb`, with no `--force` or `+`. A refusal by GitHub's rules is a stop short (`flume needs --found`), naming its words. `git ls-remote origin refs/heads/teamless/deneb` names `git rev-parse HEAD`, and `refs/heads/main` is still main's. The summary gives the full SHA, what was reconciled and how, and anything left out.

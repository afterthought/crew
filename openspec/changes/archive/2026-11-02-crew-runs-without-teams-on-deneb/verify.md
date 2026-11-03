# Verify: crew-runs-without-teams-on-deneb

Read 2026-11-03 on deneb, at `989e4280` on `change/crew-runs-without-teams-on-deneb`, cut from main at `f3c5abd4`, which is still main on GitHub.

**Outcome: archived.** All 15 tasks are ticked, and every check they name passes. Both deltas' requirements and scenarios are met, each refusal by a case. The tree holds exactly what the design says, and nothing else: it is ccb5f9a9's, apart from main's later words and records and this change's own case. One point is lesser, and a push from outside the place closes it. GitHub's `teamless/deneb` stands at `9c877969`. That is behind the branch by the tick of 3.2 and by this stage's report and archive, which change only `openspec/`. Nothing fails a requirement.

## The tree against the design

The three-way application was read back from its two sides.

| Set | What it holds | Read |
|---|---|---|
| Files the application touched (09b2cf4d to ccb5f9a9) | 180 | Every one differs from main at HEAD except record 0052, which keeps main's text (Decision 2) |
| Files main touched since 09b2cf4d | 29 | 24 meet the application: Decision 2's 21 conflicts plus `plugin/roles/design.md`, `tests/py/test_rail.py` and `docs/architecture/plan.md`, which merged cleanly. The other 5 are #430's archive, kept at main's text |
| Files only the application touched | 156 | Each is ccb5f9a9's at HEAD, apart from the four that later tasks amend: `teams.md`, `record.md`, `signals.md` (2.3) and `tests/py/test_teams.py` (2.2) |
| Files HEAD changes outside both | 6 | This change's own directory alone |

Outside `openspec/changes/`, HEAD differs from ccb5f9a9 in 13 files, each as the design has it:

- **The pages.** The 7 pages carry #418's amendments around main's records (Decision 6). Record 0052 is main's text (`git diff f3c5abd4 HEAD -- docs/adr` is empty).
- **The specs.** `bolt-teams/spec.md` keeps #430's "A conductor reads a stuck report before it asks" for this change's delta to remove.
- **The design brief.** `plugin/roles/design.md` carries #425's and #426's words on records.
- **The tests.** `test_rail.py` keeps #435's `AtNow` clock in `TestTheBranchAlone`. `test_teams.py` gains the version-2 case. `t-briefs.sh` pins #425's and #426's design words.

Every other file of `plugin/` and `tests/` is ccb5f9a9's byte for byte.

Decision 2's table, file by file:

- **Theirs**, identical to ccb5f9a9: `README.md`, `plugin/bin/crew`, `plugin/lib/gather.py`, `plugin/lib/plan.py`, `plugin/lib/transcript.py`, `plugin/skills/crew/SKILL.md`, `tests/contract/test_gather.py`, `tests/py/test_batches.py` and `tests/py/test_transcript.py`.
- **Deleted**: `plugin/roles/coder.md`, `verify.md` and `conductor.md`, and `tests/py/test_stage_ends.py`, `tests/py/test_wait.py` and `tests/t-journey-units.sh`.
- **Ours where the table says**:
  - `roles.9` and its details are main's, line for line, and so is `briefs.15`.
  - Every sentence #427 (a041654a) and #428 (62c8ff71) added to `plan.md`'s `plan.2` details stands.
  - `t-briefs.sh` builds #425's and #426's design pins by the partition, as ccb5f9a9's builds a main-level brief. It drops the old card words with `lacks`.
- **No conflict residue.** No conflict marker is left. `git diff --check f3c5abd4 HEAD` names four whitespace points, and each is in ccb5f9a9's tree as committed (`git diff --check 09b2cf4d ccb5f9a9` names the same four), so none is a resolution's leftover:
  - a blank last line in `docs/architecture/record.md`;
  - a blank last line in `tests/contract/test_wt.py`;
  - one trailing space in the crew-board spec and its archived delta.

## Tasks

| Task | Read |
|---|---|
| 1.1 | `b0fc5f32` is the one application commit, `feat!:` with the body and `BREAKING CHANGE:` footer Task notes 1.1 asks for, on `d5ed1e5e` (the proposal) above `f3c5abd4`. The tree is as above. |
| 1.2 | Task notes 1.2's grep finds no `stuck_report`, `stuck_said`, `report_time`, `before_waiting`, `after_answer`, `gather.since` or `transcript.last_words`. Its other hits are not #430's: `proposal_since`, `deploy_since`, `step_since`, `landings_since`, `landed_since`, `acts_since`, and `last_words` as a field of Flume 0.3.6's JSON in `tests/py/flume-0.3.6/`. `background` is ccb5f9a9's (`plan.py` 8536), and no `session_transcript` is left. |
| 1.3 | `batch_check(fleet, label, read=None)`, `batch_reckoners(fleet, found, here)` and `reckon_batches` are ccb5f9a9's. No `fetch`, `ripe`, `TestReckonedAtOnce` or team reckoner is left. `test_rail.py` keeps `AtNow`. |
| 1.4 | `design.md` carries ccb5f9a9's description and *Answering a design question*, `crew answer` to a waiting place, `model: claude-opus-5-5[1m]` at `xhigh`, and #425's and #426's words on whose each decision is. No main-level brief (design, planner, main-ops, reviewer, operator) names a conductor, a dispatcher, `crew fix <team>`, `crew unit run` or `wait`, `crew needs` or `crew status <team>`. `t-briefs` passes. |
| 1.5 | README, the skill and the usage are ccb5f9a9's. `t-docs` passes. |
| 1.6 | `tests/moon-tasks` leaves `tests/moon.yml` unchanged, and `tests/journeys.sh` is read by the journeys that source it. `tests/suite` ran, which it refuses to do while the tasks are out of step. |
| 2.1 | `openspec/specs/` is ccb5f9a9's apart from `bolt-teams`' kept requirement. `agent-models` reads Opus 5.5 at xhigh for the design agent and the planner. The four archives Task notes 2.1 names are present. Both validations pass. |
| 2.2 | `TestLoad` keeps ccb5f9a9's cases. It refuses versions 1, 2, 3, 4, 6, `"5"`, `true` and `null` naming 5 and `lib/crew-teams.nix`, a version-4 file with teams by its version, and a version-5 file with a `teams` list, empty or not, saying version 5 has no place for teams. It gains `test_the_boxs_file_at_version_2_is_refused_by_its_version_with_nothing_further_read`, which refuses `teams_old`'s shape before the hosts file is read. `crew.load` refuses by version before it looks for `teams`, and both refusals end "crew has done nothing." |
| 2.3 | `git grep -n 9d590e9f -- docs/architecture` prints nothing. The pages name `the-team-machinery-leaves` on `teamless/deneb`, dated 2026-11-03, for deneb alone. `core.md` opens by saying whose these pages are. `roles.8` reads retired on those terms, its details naming the departure from main's `roles.8`. `_open.md` keeps main's runner item and gains two items: *Move 5 on deneb alone, crew from `teamless/deneb`*, quoting the user's word, and *The stage briefs' browser words*. |
| 3.1 | `sluice exec main` passes, as *Checks* below shows. |
| 3.2 | GitHub's `refs/heads/main` is `f3c5abd4`, untouched. `refs/heads/teamless/deneb` is `9c877969`, the tick of 3.1, pushed from outside the place. Flume's hook refuses an agent's `git push` in its place: it refused the code stage's push, which then stopped short, and it refused this stage's. So the check names `rev-parse HEAD` only at the commit the push was made at. Each commit after it moves HEAD, the tick of 3.2 (`989e4280`) first. Those commits change only `openspec/`, so the crew a pin of `9c877969` loads is the crew of the branch's head. Decision 7 has each later commit of the change's own stages pushed the same way. That push is a fast-forward of `teamless/deneb` to the branch's head, without force, made from outside the place as `9c877969`'s was. Flume holds this place's submission ("Never submit to crew main: it deploys to every host and the box still runs teams."), so nothing reaches main. |

## The deltas

**main-level, "Partitions are declared in the teams file"** (MODIFIED). The requirement's text is unchanged from the restored spec. The delta adds two scenarios, and each is met:

- **"The box's file at version 2"**: the new `TestLoad` case, with the message naming version 2, version 5 and `lib/crew-teams.nix` and ending "crew has done nothing".
- **"A version-5 file that lists teams"**: `test_a_file_that_still_lists_teams_is_refused_at_version_4_or_5`, its message "lists teams, which version 5 has no place for: crew runs no team", naming `lib/crew-teams.nix`.

The restored scenarios, versions 3 and 4 among them, are the parametrized refusal and the version-4 case. `t-teams` runs the refusals through the command.

**bolt-teams, "A conductor reads a stuck report before it asks"** (REMOVED). The requirement stands in `openspec/specs/bolt-teams/spec.md` for the archive to remove. Nothing in `plugin/` reads a stuck report, and no conductor brief is left.

## Checks

| Check | Result |
|---|---|
| `tests/suite logic contract t-briefs t-docs` | 4 passed (4 replayed), 0 failed |
| `tests/suite --force logic contract t-briefs t-docs` | 4 passed (0 replayed), 0 failed |
| `sluice exec main` at `989e4280` | exit 0. 27 tasks completed, the 26 checks every one passed: `logic` (3080 passed), `contract` (107 passed), `mod`, and all 23 end-to-end tests. That is every `check-full` task in `tests/moon.yml`, since the command core changed. Results recorded under their keys for `989e428`. |
| `openspec validate crew-runs-without-teams-on-deneb` | valid |
| `openspec validate --specs` | 24 passed, 0 failed, with only the long-requirement warnings the restored specs already carry |
| `git grep -n 9d590e9f -- docs/architecture` | nothing |
| `git ls-remote origin refs/heads/main` | `f3c5abd4`, main's |
| `git ls-remote origin refs/heads/teamless/deneb` | `9c877969`, an ancestor of the branch's head, so a fast-forward reaches it |
| Flume's submission of the place | held, with the words "Never submit to crew main: it deploys to every host and the box still runs teams. The branch is pushed as teamless/deneb and pinned by swancloud for deneb alone." |

No test task reads `openspec/specs/`, so the archive's merge of the deltas changes no check's outcome. `openspec validate --specs` is run again on the archived tree.

## What stays outside this change

- **The push of the branch's head.** `teamless/deneb` is brought to `change/crew-runs-without-teams-on-deneb`'s head by a fast-forward without force, from outside the place, before swancloud pins it.
- **swancloud's deploy.** swancloud pins deneb's crew to `teamless/deneb`'s head and writes deneb's teams file at version 5, in one deploy on the user's word. That work is swancloud's (*What this change rests on*, 3).
- **deneb's main levels.** `crew main up madswan` and `crew main up swancloud` come after that deploy, by the user's hand (*After deploy*).
- **Main's pages.** On main, the design agent records the user's word of 2026-11-03 and where deneb's crew comes from (Migration Plan, 4). This change lands nothing on main, so main's pages cannot learn it from here.

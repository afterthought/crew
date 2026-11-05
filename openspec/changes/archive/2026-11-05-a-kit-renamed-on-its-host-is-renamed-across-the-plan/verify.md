# Verify: a-kit-renamed-on-its-host-is-renamed-across-the-plan

Read 2026-11-05 on deneb, at `dc78fcf5` on `change/a-kit-renamed-on-its-host-is-renamed-across-the-plan`, cut from `teamless/deneb` at `b57c709d`.

**Outcome: archived.** All 21 tasks are ticked, and every check they name passes. Each requirement and scenario of the five deltas is met by the code and proved by a case. `teamless/deneb` has since moved to `9d854501` with two commits, #439's CLAUDE.md words. The branch merges onto it cleanly (`git merge-tree`), so sluice's submission meets no conflict. Nothing fails.

## Checks

| Check | Result |
|---|---|
| `tests/suite logic contract` | 2 passed, 0 failed |
| `tests/suite --affected` | 26 passed, 0 failed: `contract`, `logic`, `mod`, `t-briefs`, `t-cards`, `t-docs`, `t-hold`, `t-journey-board`, `-cross`, `-land`, `-main`, `-main-fix`, `-ops`, `-plan`, `-review`, `-roles`, `-signals`, `-state`, `t-roles`, `t-runner`, `t-session-hook`, `t-slot`, `t-sluice`, `t-stage-facts`, `t-suite`, `t-teams` |
| `openspec validate` | Valid. `--strict` fails on four "requirement text is very long" warnings alone, a warning crew's own specs raise 108 times |

Every test was replayed: moon replays a test only when its inputs are identical to a run that passed on this host (`tests.9`, `tests.10`). `tests/suite` ran, so `tests/moon.yml` is in step with the tests.

## Tasks

| Task | Read |
|---|---|
| 1.1 | `kit_now(kit, renames)` sits beside `kit_in`. It reads each rename in order by name or forge address, and reads a name no rename names as written. `TestKitNow` covers all six cases of Task notes 1.1. |
| 1.2 | `runs_at` makes one pass over `runs/` per tip, kept in `READ` as `runs-<tip>`, and gives both `landings` and `renames`. `landings_at` and `renames_at` read from it. `renames_in` keeps the renames not refused, sorted by `At` then `Id`. `partition_kits(plan, landings, renames=())` reads every name through `kit_now`. `TestRunsRead` pins the single read, and `TestPartitionKits` gains the three cases. |
| 1.3 | Every row of Decision 3's table reads through `kit_now`. Launches go through `launches_now`, in `runner_facts`, `rail_runs` and a write's card raise (`raise_proposal_at`). A fix of main reads its kit from its launch's `Repo` (`main_fixes_waiting`), and a send or drop finds its launch (`main_fix_work`). `ops.landings` and `page.fleet_kits` read through the entries' renames. `record_items` takes the renames. The cases named in Task notes 1.3 are in `test_kits.py`, `test_main_fix.py`, `test_ops.py`, `test_page.py` and `test_proposals.py`. |
| 1.4 | `TestRenamedKit` in `test_board.py` names `timber` alone and keeps the views' keys. `plugin/hooks/status.js` is untouched (`code.8`). |
| 2.1 | The parser gains `kit rename <old> <new> [--label]`, with each name checked by `kit_name` (`KIT`, `code.4`). `("kit", "rename")` is in `PLAN_WRITES`, `OPS`, `COMMANDS` and `ACTS`. `named` adds `kit/<old>` to a refusal's entry. `test_parser.py` covers the command, its `Do`, and the names it refuses. |
| 2.2 | `op_kit_rename` checks `rename_refusal` inside its change, at the tip it is applied to (`plan.1`). It rewrites `Repo` alone on the records `renamed_in` finds, and appends no request. `TestTheRename`, `TestRefused` (old and new the same, no such kit, still kept, no new kept, two kept by the new name, a bolt's name, the host the hosts file does not list) and `TestTheStartedBolt` compare each record field by field. |
| 2.3 | `test_plan_roles.py` refuses the planner naming `crew plan propose` and the design agent and ops naming the planner. It allows the user and a proposal's approval. |
| 2.4 | The subject is `plan(kit): rename <old> <new>`. The entry is `kit.rename`, with `On: kit/<new>`, `From: kit/<old>`, `Repo` and `Count`, passed through `Op.fields` on both a direct write and an approval. `record.py`'s descriptor comment and `line` read `Count` as "renamed". `test_recfix.py` runs a real `recfix --check` on madswan's shape, which passes, and on a plan that breaks `%unique: Repo Goal`, which is refused before any commit. |
| 2.5 | `kit_given` writes the name now in `bolt new`, `unit add` and `chore add`, and `former_said` says so after the write. `former_kept_said` refuses a former name the host keeps again. A command later in the same proposal reads the rename through `Write.renamed`. `TestAFormerName` covers each, the `Do` left unchanged. |
| 2.6 | `cards.renamed_drawn` draws the `RENAME KIT` block: old → new, the bolts with `(started)`, and the units. It files each bolt section under the new kit and adds no question. `describe` gives the proposals page its lines. Both are in `test_proposal_card.py`. |
| 2.7 | `row_gone` closes `land/<old>` with "<old> is renamed <new>: its landings are rows of land/<new>", ahead of any gone-bolt reading. `record_now` reads `record/<old>/<n>` as `record/<new>/<n>` in `record_settled` and `record_proposed`. The sweep passes the partition's renames (`rail_read`'s `renames`). Both cases are in `test_rail.py`. |
| 2.8 | `main_kit_said` ends "if it was renamed on its host, crew kit rename <kit> <new> names it so in the plan". `TestBeforeARunnerTookIt` pins it. |
| 3.1 | `REPOSITORIES` and `"repositories.rec": "Repository"` are in `runner.FILES`. `host_read` gives `repositories` as `{address: folder}`, or `None` where the file is absent. A record with no address, one address twice, or no folder makes the host unreadable, naming the file, as does a file recfix refuses. All of these are in `test_runner.py`. |
| 3.2 | `runner.where(reads, launches, what, kit)` takes the folder from `kept_folder` ahead of a place's Status. A runner reporting repositories without the kit leaves it unread, naming the host, what it keeps and `crew kit rename`. Two repositories by one name are told apart by forge address, or refused. A runner that reports none is read from Status. `kit_at`, `bolt_taken` and `launched_at` pass the kit. |
| 3.3 | `TestTheStartedBoltLands` runs on madswan's facts: request 1 under `flywheel-cloud`, a Flume 0.3.6 status tidied and landed, and `repositories.rec` at the renamed folder. After the rename, one-seam reads merged, the bolt is read in the renamed clone, its key is `land/boomdrive-cloud`, and no request is appended. Before the rename, it is refused naming the rename. |
| 4.1 | `t-journey-plan` passes. The user's `crew kit rename atlas-kit atlas` writes one commit touching only `plan.rec` and `runs/`, with its entry (`From kit/atlas-kit`, `Repo atlas`, `Count 2`). The planner's direct run is refused naming `crew plan propose`. The planner's proposal draws `RENAME KIT` on its card, and the approval's one commit renames `boards`, its entry's `From` naming the proposal. |
| 4.2 | README's plan section, `SKILL.md` and `plugin/bin/crew`'s usage header each name the command, what it rewrites and does not, and who runs it. The crew command routes `kit` to `plan.py`. `t-docs` passes. |
| 4.3 | `planner.md` gains the table row and the sentence. `t-briefs` pins both. |
| 4.4 | As *Checks* above. |

## The deltas

**bolt-plan, "A kit renamed on its host is renamed across the plan in one act"** (ADDED). Every refusal the requirement lists is in `rename_refusal`, checked at the tip. A main-level host the hosts file does not list is refused by name, and two repositories kept by the new name are refused through `crew.kit_kept` (`read.1`). The scenarios are proved as follows:
- "The user renames tailrace": `TestTheRename`.
- "Not renamed on its host", "A new name the host does not keep" and "The new name is a bolt's": `TestRefused`.
- "A kit only its landings name": `test_a_kit_only_the_landings_name_renames_no_record_and_still_writes_its_entry`.
- "The planner proposes it" and "Another agent runs it": `test_plan_roles.py`.
- "A started bolt's kit": `TestTheStartedBolt`.
- "The command at a shell": `t-journey-plan`.

**bolt-plan, "What crew recorded under a kit's former name is read under its name now"** (ADDED). Every read in the requirement's list goes through `kit_now`, and nothing writes `requests.rec`, `runs/`, `proposals.rec`, signals or `moves.rec` for a rename (`t-journey-plan` checks the commit touches only `plan.rec` and `runs/`). The scenarios:
- landings under the old name, a rename undone and a chain of renames: `TestKitNow` and `TestPartitionKits`;
- a launch made before the rename: `TestWhereABoltRuns`;
- a fix of main under the old name: `test_main_fix.py`'s `TestRenamed`;
- a deploy's landings: `test_ops.py` and `test_page.py`;
- a source in a renamed repository: `test_proposals.py`;
- the board after a rename: `test_board.py`'s `TestRenamedKit`.

**bolt-plan, "A command given a kit's former name writes its name now"** (ADDED). Both scenarios are in `TestAFormerName`.

**drive-state, the three MODIFIED requirements.** Each one's header matches `openspec/specs/drive-state/spec.md`.
- The runner's four files: `test_runner.py`.
- `where`'s folder from `repositories.rec`, and the two new unread cases: `test_runner.py` and `TestWhereABoltRuns`. "The runner that took the work" now says "reports no repositories", as Task notes 3.2 asks.
- The main-level host's refusal naming the rename: `TestBeforeARunnerTookIt`.

**run-record, "A kit's rename is one entry naming both its names"** (ADDED). A done rename's entry is shown by `test_recfix.py` and `t-journey-plan`. A refused rename's entry comes from the entry point's refusal through `ACTS` and `named` (`kit/<old>`), and `renames_in` drops refused entries, so a refused rename renames nothing (`TestRenamesIn`).

**rail-cards, "A kit's landings card follows its rename"** (ADDED), and **plan-proposals, "A proposal's card draws a kit's rename"** (ADDED). Proved by `test_rail.py` and `test_proposal_card.py`, as in tasks 2.7 and 2.6.

## Observations

Neither fails a requirement.

- **A source in another renamed repository.** A source naming a former address of a repository that is not the work's own kit is still fetched and named by that address. GitHub's redirect answers it, as the design's *Risks* accepts. The scenario's case is the work's own kit, which is read in the kit's checkout.
- **What the started bolt's landing still waits on.** It needs the runner's R1 and R2, swancloud's S1 and the renamed clones (*What this change rests on*), then madswan-planner's proposal after deploy. All of that is other repositories' work and the design's *After deploy*, not this change's.

## Decisions

This stage made none of the user's or the rules'. It accepted the non-strict `openspec validate` as the spec check, since `--strict` fails only on a length warning that crew's own specs raise throughout. That choice is recorded here.

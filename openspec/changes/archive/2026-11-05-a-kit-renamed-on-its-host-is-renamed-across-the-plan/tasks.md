# Tasks

Each check is a moon task of the `tests` project, run through `tests/suite`: `logic` is `tests:logic`, `contract` is `tests:contract`, and an end-to-end test `t-<name>` is `tests:t-<name>`. Build the groups in order. Submit nothing, and never run `wt submit --help`.

## 1. A kit read under its name now

- [x] 1.1 `plan.kit_now` reads a kit's name through the partition's renames in the order they were written, by name or forge address. A name no rename names reads as written, and a rename and its undoing read back (design Decision 3; Task notes 1.1). Passes `tests/py/test_kits.py` (`tests/suite logic`).
- [x] 1.2 A partition's renames are read from its run record in the same read of `runs/` as its landings, once per tip, and `partition_kits` names each kit once, by its name now (design Decision 3; `plan.12`; Task notes 1.2). Passes `tests/py/test_kits.py` (`tests/suite logic`).
- [x] 1.3 Every read in Decision 3's table, of what crew never rewrites, reads a kit through `kit_now`: a kit's launches, a bolt's kit from its launches, a fix of main's kit, a kit's landings and deploys, and a source's repository (design Decision 3; Task notes 1.3). Passes `tests/py/test_kits.py`, `test_main_fix.py`, `test_ops.py`, `test_page.py` and `test_proposals.py` (`tests/suite logic`).
- [x] 1.4 The board and the agents' views name a kit whose landings were recorded under a former name by its name now, and leave the views' keys unchanged, so the mod is untouched (design Decision 3; `code.8`; Task notes 1.4). Passes `tests/py/test_board.py` (`tests/suite logic`).

## 2. The rename

- [x] 2.1 `crew kit rename <old> <new>` is a plan command a proposal may hold, parsed by the command line's own grammar, with its act `kit.rename` (design Decision 2; Task notes 2.1). Passes `tests/py/test_parser.py` (`tests/suite logic`).
- [x] 2.2 The rename does three things (design Decision 2; Task notes 2.2). Passes `tests/py/test_kit_rename.py` (`tests/suite logic`).
  - It rewrites the `Repo` of every Bolt and Unit record naming `<old>` to `<new>`, and nothing else.
  - It is refused, with nothing written, where the old name is no kit of the partition, where the main-level host still keeps the old name or keeps no repository by the new one, where the new name is a bolt's, or where the hosts file can't be read.
  - It appends no request and leaves a started bolt as it was.
- [x] 2.3 The user runs the rename at a shell, and a proposal holding it applies on the user's approval. The planner's direct run is refused naming `crew plan propose`, and any other agent's naming the planner (design Decision 2; `roles.1`; Task notes 2.3). Passes `tests/py/test_plan_roles.py` (`tests/suite logic`).
- [x] 2.4 The rename is one commit. Its run-record entry is `kit.rename`, naming `kit/<new>`, `kit/<old>`, `Repo` and `Count`, and the plan it leaves passes a real `recfix --check`, while one breaking `%unique: Repo Goal` is refused before any commit (design Decision 2; Task notes 2.4). Passes `tests/contract/test_recfix.py` (`tests/suite contract`).
- [x] 2.5 A plan command given a kit's former name writes the name now and says so, a proposal approved after a rename among them, its `Do` unchanged. A repository kept again under a former name is refused, naming the rename (design Decision 4; Task notes 2.5). Passes `tests/py/test_kit_rename.py` (`tests/suite logic`).
- [x] 2.6 A proposal's card draws a rename as its own block, the old name, the new, the bolts and units it renames and which bolts are started, and is a plain approval when it adds no unit (design Decision 2; Task notes 2.6). Passes `tests/py/test_proposal_card.py` (`tests/suite logic`).
- [x] 2.7 A card open under `land/<old>` closes saying the kit is renamed, and `land/<new>` is raised for its rows. A decision record's card under `record/<old>/<n>` is settled by the record under its new kit (design Decision 5; Task notes 2.7). Passes `tests/py/test_rail.py` (`tests/suite logic`).
- [x] 2.8 The refusal for a kit the main-level host does not keep names `crew kit rename` as the way on (design Decision 2; Task notes 2.8). Passes `tests/py/test_kits.py` (`tests/suite logic`).

## 3. Where a runner keeps a kit

- [x] 3.1 crew reads `repositories.rec` on a runner's branch, each repository the runner keeps by its forge address with its folder. A file it can't read makes that host's runner unreadable, and a missing file is no report (design Decision 6; Task notes 3.1). Passes `tests/py/test_runner.py` (`tests/suite logic`).
- [x] 3.2 A started bolt's and a kit's folder are read from the reporting runner's `repositories.rec`, by the kit's name now, over a place's stale status. A runner that reports repositories but not the kit leaves it unread, naming what it keeps and the rename. A runner that reports none is read from Flume's status as before (design Decision 6; Task notes 3.2). Passes `tests/py/test_runner.py` and `tests/py/test_kits.py` (`tests/suite logic`).
- [x] 3.3 With madswan's facts and the rename to `boomdrive-cloud`, `you-sign-in-to-staging` reads one-seam merged, is read and landed in the renamed clone's folder, and sits on `land/boomdrive-cloud`, and no request was appended (design Decision 7; Task notes 3.3). Passes `tests/py/test_kit_rename.py` (`tests/suite logic`).

## 4. The command, its docs and its brief

- [x] 4.1 `crew kit rename` runs through the crew command on the stubs (Task notes 4.1). Verify `tests/suite t-journey-plan` ends with "0 failed".
  - The user's run writes one commit and its entry.
  - The planner's direct run is refused.
  - A proposal holding a rename is checked, carded and applied on approval.
- [x] 4.2 README, `plugin/skills/crew/SKILL.md` and `plugin/bin/crew`'s usage header name `crew kit rename`, what it rewrites and who runs it, together (`docs.2`; Task notes 4.2). Verify `tests/suite t-docs` ends with "0 failed".
- [x] 4.3 The planner's brief names the rename among its commands, and says a renamed kit is renamed by proposing it, never by dropping and adding its work again (design Decision 2; Task notes 4.3). Verify `tests/suite t-briefs` ends with "0 failed".
- [x] 4.4 Every test the change affects passes (Task notes 4.4). Verify `tests/suite --affected` ends with "0 failed".

# Design: a bolt never carries another bolt's work to main

## Context

The proposal gives the box's case. Rules this change relies on:

- `plan.19`: crew cuts every place from `origin/bolt/<bolt>`, and reads a bolt that lives on GitHub there and never from the host's copy.
- `plan.8`: a bolt meets main alone, and no landing card is raised nor row marked able to land while it conflicts.
- `teams.22` with record 0044 point 2: a bolt ships alone.
- `teams.17`: a merge carries no other unit's open change. This change holds bolts to the same rule.
- `read.1`: what crew can't read is said and refuses.
- `code.7`: a decision is a function of facts.
- `roles.3`: an agent's breach of a rule its brief states is met by a check in crew.
- `state.5`: crew moves no branch.

It touches the areas of:

- `plan.md` (`plugin/lib/plan.py`, `plugin/lib/gather.py`, `plugin/lib/kit.py`)
- `teams.md` (`plugin/bin/crew`)
- `briefs.md` (`plugin/roles/coder.md`, `plugin/skills/`)
- `tests.md` (`tests/`)
- `docs.md` (`README.md`, `openspec/`)

It departs from no rule.

### Where the carried work came from

The ruling asked where a slot's worktree or branch is cut or reused between units. It names a unit's run, its construct, a fix's start, and a slot's freeing and tidying. Each was read:

- **A unit's construct and code, a chore's code, a unit's merge whose place is gone, a fix's start.** All go through `make_place`. `PLACE` fetches `+refs/heads/bolt/<bolt>:refs/remotes/origin/bolt/<bolt>` and cuts a new branch from `origin/bolt/<bolt>`, tracking it. The place's path and branch are the unit's own (`places/<unit>`, `unit/<unit>`), never the slot's.
- **A slot's freeing.** It ends the agent and closes the pane. The next stage opens a fresh pane in the place of the work it holds (`crew.launch`, `held["place"]`). Nothing of a slot carries from one unit to the next.
- **A kept branch.** A branch an earlier drop kept is taken as it stands (record 0003). That is the unit's own earlier work, by design.

The box's run record and the coder's session confirm the cut. The popover unit's construct at 19:01:23Z delivered `0a3071e0`, on `853cb325`, the bolt's own head. The carried work came in at 19:51:12Z, when the code stage's coder ran `git rebase` onto `f5e67f35`. Its brief told it the branch was made from "the team's bolt, `bolt/<bolt>`", and its code prompt, `/opsx:apply <unit>`, names no bolt. Its team held two (`teams.16`), and it took the first `bolt/*` branch holding its base.

One path of crew's own does carry another bolt's work. `crew unit move` rebased a moved place with `git rebase --onto bolt/<to> bolt/<from>`. Those are the host's copies, which `plan.19` rules out reading. A lagging copy of the bolt the unit left replays that bolt's landings onto the bolt it joins.

### The family

- **Flume.** `flume launch --base` cuts a place from `origin/<base>` after its own fetch of that one branch. It asks sluice for the base's revision where the branch's policy names a remote, else reads `GitHistory::origin_branch`, which never reads an earlier tracking ref. A fetch that fails refuses the launch. A branch or place that exists is refused, never reused (agentplot/flume main, `crates/flume-core/src/launch.rs` `base_now`, `crates/flume/src/git.rs` 200–209, `crates/flume/src/profiles/place/git_worktree/mod.rs` 355–373).
- **Boomdrive's runner.** It passes a launch's `Base`, `bolt/<bolt>`, to `flume launch --base` unchanged, and each place is one request's (agentplot/boomdrive main, `crates/flywheel/src/carry.rs` 1104, `crates/flywheel/src/flume.rs` 177–178).

Neither cuts from anything but the bolt as its remote holds it, so neither has the fault. An agent in a Flume place could still rebase onto another bolt, which the merge and landing refusals below meet.

## Decisions

### Decision 1: another bolt's work is a commit on that bolt's first-parent line beyond main

`gather.carried_bolts(holds, lines, own)` is the one decision. It takes:

- the commits a tip holds beyond main;
- each bolt's first-parent line beyond main;
- the bolt the tip is of.

It returns each other bolt whose line holds a commit the tip holds that is not on its own bolt's line.

A bolt's first-parent line beyond main is the landings sluice made on it, so a commit there is that bolt's work, whichever branch it reached by a merge. In the box's case:

- The popover bolt holds landing 214, which is on the deleting bolt's line and not on its own. It carries the deleting bolt's work.
- The deleting bolt holds nothing on the popover bolt's line. It is free to land, and its landing takes 214 to main.
- Once main holds 214, the popover bolt holds nothing beyond main of another bolt's, and it lands.

Every fact is read from refs, never from a commit's words.

Considered: refusing a bolt that holds any commit main lacks and another bolt's branch holds, the ruling's words taken whole. It would hold the deleting bolt too, since it shares 214 and its unit's commits with the popover bolt. That would leave no way on but the user's hand, since the popover bolt can't land until main holds 214. First-parent ownership holds only the bolt that took the work. Not covered: a bolt whose branch was made at another bolt's tip, the two sharing a first-parent segment. sluice's give makes every bolt from main, so it does not arise.

### Decision 2: the kit's read says what each bolt carries

`gather.kit` lists each bolt's first-parent line beyond main (`bolt_lines`). It covers every bolt GitHub holds, as the host last fetched it, and a bolt kept on its host. It then gives each bolt it reads `carries`, `{bolt: [landings]}`. When git can't list a line, it gives `carries_error` instead (`read.1`). It fetches nothing of its own (`plan.18`), as every stage read. The readers use it:

- `land_facts` passes it to the row's facts.
- `landing_rows` holds the row with no box, whatever else holds it, saying `held: <carries_said>`. A row with no box raises no card (`card_rows`, `plan.8`).
- The rail's land line in `rail_rows` says the same and can't land.
- `bolts_data` and `bolts_text` give it as `carries` and a `landing: held: …` line.

### Decision 3: crew bolt submit reads what the head carries after one fetch

`landing_submitted` runs `landing_carries` after `landing_sent_back` and before sluice's queue is read. It judges the head the landing would submit, or the host's `bolt/<bolt>` for a bolt kept there. `CARRIES` runs on the team's host. It fetches main and every bolt from origin with `--prune`, so a branch GitHub deleted is no other bolt. It prints what the tip holds beyond main, its own first-parent line and each bolt's line. `kit.carries_of` reads the output, and `carries_refusal` words the refusal.

A bolt that carries another's work returns crew's own refusal. Nothing is submitted, no worktree is cut and sluice is asked for nothing. The refusal is recorded with no head, so it holds no row of its own (`landing_ended`). The row is held by what the kit's read says, and is never read as sluice sending the landing back. A fetch or a listing git refuses refuses the submission, naming git's words (`read.1`).

### Decision 4: a merge into a bolt is refused while its branch carries another bolt's work

`merge_bolts` runs in the merge stage of units, chores and fixes, beside `merge_carries` (`teams.17`) and the split check (`plan.19`). It runs `CARRIES` for the branch against the bolt where it lives (`bolt_upstream`), so `HOLDS` leaves out what the bolt already holds. `merge_carried_refusal` names each bolt and its landings, and gives the way on:

- take that work out of the branch, building it on the bolt where it lives alone; or
- merge once main holds that work, by that bolt's own landing.

This is crew's check on the agent's act (`roles.3`). The coder's brief now states the rule (Decision 5), and the check refuses the act whatever the agent was told.

### Decision 5: the coder's bolt is the one its branch tracks

`PLACE` sets every unit's, chore's and fix's branch to track its bolt where it lives. So the brief names the bolt by `git rev-parse --abbrev-ref @{upstream}`, with no new token and no new prompt words. The brief says that bolt is the only one the coder builds on. The team may hold another, and no other `bolt/*` branch is the coder's to rebase onto, merge, test against or take work from. Both places that took the bolt in with `git rebase bolt/<bolt>`, a forecast conflict and a merge refused for a conflict, now say `git fetch -q origin`, then `git rebase @{upstream}`. `tests/t-briefs.sh` pins the phrase (`tests.6`).

Considered: naming the bolt in every stage's prompt. The prompt is a slash command whose form crew recognises (`roles.4`). The upstream already names the bolt in every place crew cuts.

### Decision 6: a moved unit is rebased between its bolts where they live

`REBASE` takes the bolt the unit leaves where it lives as its seventh word, beside the bolt it joins (the sixth). It fetches each that lives on GitHub first, and runs `git rebase --onto <joins> <leaves>`. A fetch that fails exits 4, which `op_unit_move` refuses with git's words.

## After deploy

None. Every case is held by the logic tier on plain facts, by the contract tier on real git in scratch repositories, and by `t-briefs` and the journeys that land bolts on the stubs. What the box runs is swancloud's pin, not a step of this change.

## Task notes

**1.1** `plugin/lib/gather.py`: `carried_bolts`, `bolt_lines`, and `carries`/`carries_error` in `kit`. Logic: `tests/py/test_landings.py` (`test_a_bolt_holding_another_bolts_landing_carries_that_bolts_work_and_the_other_carries_nothing`, `test_a_commit_on_the_bolts_own_line_or_one_main_holds_is_carried_from_no_one`). Contract: `tests/contract/test_gather.py` (`test_a_bolt_on_github_that_merged_another_bolts_landing_carries_that_bolts_work`).

**1.2** `plugin/lib/plan.py`: `carries_said`, `carried_named`, `landing_rows`, `land_facts`, the rail's land line in `rail_rows`, `bolts_data`, `bolts_text`. Logic: `tests/py/test_landings.py` (`test_a_bolt_carrying_another_bolts_work_is_held_with_no_box_naming_that_bolt_and_its_landing`, `test_a_bolt_whose_carried_work_cant_be_read_is_held_saying_why`), `tests/py/test_rail.py` (`test_a_bolt_carrying_another_bolts_work_is_held_on_its_land_line_and_left_out_of_the_tell`), `tests/py/test_bolt_submissions.py` (`test_crew_bolts_says_a_bolt_carrying_another_bolts_work_is_held_naming_it`).

**1.3** `plugin/lib/plan.py`: `CARRIES`, `bolts_carried`, `carries_refusal`, `landing_carries` and its call in `landing_submitted`; `plugin/lib/kit.py`: `carries_of`. Logic: `tests/py/test_landing.py` `TestTheSubmission` (`test_a_bolt_carrying_another_bolts_unlanded_work_submits_nothing_and_names_that_bolt_and_its_landing`, `test_a_bolt_whose_carried_work_cant_be_read_submits_nothing_naming_why`), its fake and `tests/py/test_pane_landing.py`'s answering `CARRIES`; `tests/py/test_kit.py` (the `carries_of` cases). Contract: `tests/contract/test_git.py` (`test_a_bolt_holding_another_bolts_landing_carries_it_until_main_holds_it_and_the_other_carries_nothing`).

**1.4** `plugin/lib/plan.py`: `merge_carried_refusal`, `merge_bolts`, called in `run_check`'s merge, `chore_check`'s merge and `fix_cmd`'s merge. Logic: `tests/py/test_stage_rules.py` `TestAMergeCarriesNoOtherBoltsWork`. Contract: `tests/contract/test_git.py` (`test_a_unit_built_on_another_bolts_landing_carries_that_bolts_work_into_its_own`).

**1.5** `plugin/roles/coder.md`, `tests/t-briefs.sh`.

**1.6** `plugin/lib/plan.py`: `REBASE`, `op_unit_move`. Contract: `tests/contract/test_git.py` (`rebase` takes the bolt it leaves; `test_a_unit_moved_from_a_bolt_whose_host_copy_lags_carries_none_of_that_bolts_work`).

**1.7** Contract: `tests/contract/test_git.py` (`two_bolts`, `test_a_slot_that_built_one_bolts_unit_cuts_the_next_bolts_unit_from_that_bolt_with_nothing_of_the_first`).

**2.1** README's landings card paragraph, the crew skill's landing row and `crew`'s usage header for `crew bolt submit`.

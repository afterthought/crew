# Design: a bolt never carries another bolt's work to main

## Context

The proposal gives the box's case and what this line takes of crew main's fix (b79d1d86, d44832bc). Rules this change relies on:

- `plan.19`: a bolt that lives on GitHub is read there, never from the host's copy.
- `plan.8`: a bolt meets main alone, and no landing card is raised nor row marked able to land while it conflicts. Record 0056 changes how a bolt lands once the base-place retrofit ships; until then crew lands through sluice, and this change guards that landing.
- `read.1`: what crew can't read is said and refuses.
- `code.7`: a decision is a function of facts.
- `roles.5`: crew builds no mechanism of Flume's; this is crew's own landing, which it runs until record 0056's unit retires it.
- `state.5`: crew moves no branch.

It touches the areas of:

- `plan.md` (`plugin/lib/plan.py`, `plugin/lib/gather.py`, `plugin/lib/kit.py`)
- `teams.md` (`plugin/bin/crew`)
- `briefs.md` (`plugin/skills/`)
- `tests.md` (`tests/`)
- `docs.md` (`README.md`, `openspec/`)

It departs from no rule.

### What of main's fix this line has no code for

- **A merge into a bolt.** main refuses a unit's, chore's or fix's merge while its branch carries another bolt's work (`merge_bolts`). Here a place is Flume's, and Flume submits it to its bolt: crew runs no merge to refuse. A place carrying another bolt's work reaches its bolt, and this change holds that bolt at its landing.
- **The coder's brief.** Here crew starts no coder; a place's agent is Flume's.
- **`crew unit move`'s rebase.** Here a move of launched work is refused, naming drop and add, and `REBASE` is gone.

## Decisions

### Decision 1: another bolt's work is a commit on that bolt's first-parent line beyond main

`gather.carried_bolts(holds, lines, own)` is the one decision. It takes the commits a tip holds beyond main, each bolt's first-parent line beyond main, and the bolt the tip is of. It returns each other bolt whose line holds a commit the tip holds that is not on its own bolt's line.

A bolt's first-parent line beyond main is the landings sluice made on it, so a commit there is that bolt's work, whichever branch it reached by a merge. In the box's case the popover bolt holds landing 214, on the deleting bolt's line and not its own, so it carries the deleting bolt's work; the deleting bolt holds nothing on the popover bolt's line and is free to land; once main holds 214, the popover bolt lands. Every fact is read from refs, never from a commit's words.

Considered, as main did: refusing a bolt that holds any commit main lacks and another bolt's branch holds. It would hold the deleting bolt too, leaving no way on but the user's hand.

### Decision 2: the kit's read says what each bolt carries

`gather.kit` lists each bolt's first-parent line beyond main (`bolt_lines`), every bolt GitHub holds as the host last fetched it and a bolt kept on its host, and gives each bolt it reads `carries`, `{bolt: [landings]}`, or `carries_error` when git can't list a line (`read.1`). It fetches nothing of its own (`plan.18`). A ref another command removed while the read ran is left out as gone. The readers:

- `land_facts` passes it to the row's facts.
- `landing_rows` holds the row with no box, whatever else holds it, saying `held: <carries_said>`; a row with no box raises no card (`plan.8`).
- The rail's land line in `rail_rows` says the same and can't land.
- `bolts_data` and `bolts_text` give it as `carries` and a `landing: held: …` line.

### Decision 3: crew bolt submit reads what the head carries after one fetch

`landing_submitted` runs `landing_carries` once the head it would submit is decided (`landing_head`) and before sluice's queue is read. It judges that head, or the host's `bolt/<bolt>` for a bolt kept there. `CARRIES` runs on the bolt's host, where the runner that took its work reported it. It fetches main and every bolt from origin and prunes nothing: a branch GitHub deleted was in main, so its line beyond main is empty, and pruning removed a landed bolt's tracking ref while another read listed it (crew main's d44832bc). `kit.carries_of` reads the output, and `carries_refusal` words the refusal.

A bolt that carries another's work returns crew's own refusal: nothing is submitted, no worktree is cut and sluice is asked for nothing. The refusal is recorded with no head, so it holds no row of its own (`held_at`); the row is held by what the kit's read says. A fetch or a listing git refuses refuses the submission, naming git's words (`read.1`).

`CARRIES` keeps main's fourth word, a branch the tip is judged beyond, so the script is main's; nothing on this line passes it.

## After deploy

None. Every case is held by the logic tier on plain facts and by the contract tier on real git in scratch repositories. What deneb runs is swancloud's pin of `teamless/deneb`, not a step of this change.

## Task notes

**1.1** `plugin/lib/gather.py`: `carried_bolts`, `bolt_lines`, and `carries`/`carries_error` in `kit`. Logic: `tests/py/test_landings.py` (`test_a_bolt_holding_another_bolts_landing_carries_that_bolts_work_and_the_other_carries_nothing`, `test_a_commit_on_the_bolts_own_line_or_one_main_holds_is_carried_from_no_one`). Contract: `tests/contract/test_gather.py` (`test_a_bolt_on_github_that_merged_another_bolts_landing_carries_that_bolts_work`, `test_a_bolts_ref_gone_while_the_lines_are_read_is_left_out_and_one_git_cant_list_is_named`).

**1.2** `plugin/lib/plan.py`: `carries_said`, `carried_named`, `landing_rows`, `land_facts`, the rail's land line in `rail_rows`, `bolts_data`, `bolts_text`. Logic: `tests/py/test_landings.py` (`test_a_bolt_carrying_another_bolts_work_is_held_with_no_box_naming_that_bolt_and_its_landing`, `test_a_bolt_whose_carried_work_cant_be_read_is_held_saying_why`), `tests/py/test_rail.py` (`test_a_bolt_carrying_another_bolts_work_is_held_on_its_land_line_and_left_out_of_the_tell`), `tests/py/test_bolt_submissions.py` (`test_crew_bolts_says_a_bolt_carrying_another_bolts_work_is_held_naming_it`).

**1.3** `plugin/lib/plan.py`: `CARRIES`, `bolts_carried`, `carries_refusal`, `landing_carries` and its call in `landing_submitted`; `plugin/lib/kit.py`: `carries_of`. Logic: `tests/py/test_landing.py` `TestTheSubmission` (`test_a_bolt_carrying_another_bolts_unlanded_work_submits_nothing_and_names_that_bolt_and_its_landing`, `test_a_bolt_whose_carried_work_cant_be_read_submits_nothing_naming_why`), its fake and `tests/py/test_pane_landing.py`'s answering `CARRIES`; `tests/py/test_kit.py` (the `carries_of` cases). Contract: `tests/contract/test_git.py` (`test_a_bolt_holding_another_bolts_landing_carries_it_until_main_holds_it_and_the_other_carries_nothing`, `test_a_bolt_github_deleted_after_it_landed_is_read_as_carrying_nothing_and_its_tracking_ref_kept`).

**2.1** README's landings card paragraph, the crew skill's landing row and `crew`'s usage header for `crew bolt submit`.

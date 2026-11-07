# A bolt never carries another bolt's work to main

## Why

On the Willdan box, in WilldanGroup/breadboard-kit, the bolt `breadboards-access-choice-is-one-popover` landed on main at `99c0e88` on 2026-11-06 carrying the bolt `breadboard-shows-a-deleted-app-as-deleting`, which was held (signal `WilldanGroup/crew-state:wldn/main signals/2026-11-07-wldn-ops-052d0a47/01`). A coder in the popover bolt's unit rebased its branch onto the deleting bolt's landing 214, `f5e67f35`, and landing 216 merged that into the popover bolt. Nothing of crew's saw the carried work, not the landings card nor `crew bolt submit`. crew main fixed it on 2026-11-07, b79d1d86 and d44832bc, released in v0.41.9.

agentplot-design ruled that `teamless/deneb` takes the fix's behavior: "deneb's crew lands bolts through sluice until the base-place retrofit ships, so the defect is live there." On this line a bolt's work is Flume's places, launched through the host's runner and merged into the bolt by Flume, so an agent in a place can carry another bolt's work into its bolt as the box's coder did, and only crew's landing stands between that bolt and main.

That breaks `plan.19` (every place's work is its own bolt's, as GitHub holds it) and `plan.8` (a bolt meets main alone, and nothing lands while it is held).

## What Changes

- **A bolt carrying another bolt's work does not land.** A commit of another bolt's own is one on that bolt's first-parent line beyond main: the landings sluice made on it. While a bolt holds such a commit and main lacks it, `crew bolt submit` submits nothing, naming that bolt and its landings. Its row on the kit's landings card is held with no box, as a conflict holds one (`plan.8`), so no landing card is raised for it. The rail's land line says it can't land, and `crew bolts` says it is held. Everything is read from the branches as GitHub holds them, never from a commit's words. The bolt whose work was carried is not held, and its own landing takes that work to main, after which the carrying bolt lands.
- **The read prunes nothing.** `crew bolt submit`'s read fetches every bolt from GitHub without pruning, since a branch GitHub deleted was in main and its line beyond main is empty, and a ref another command removes mid-read is left out as gone (`read.1`).
- README, the crew skill and `crew`'s usage header say this (`docs.2`).

main's fix has three parts this line has no code for, so they are not carried: the refusal of a unit's, chore's or fix's merge into its bolt (`run_check`, `chore_check`, `fix_cmd`), since crew runs no merge here and Flume submits a place to its bolt; the coder's brief (`plugin/roles/coder.md`), since crew starts no coder here; and `crew unit move`'s rebase between bolts (`REBASE`), since a move of launched work is refused here, naming drop and add.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: "A bolt carrying another bolt's work does not land" and "crew bolts says a bolt carries another bolt's work".
- `rail-cards`: "A row carrying another bolt's work is held".
- `crew-rail`: "A bolt carrying another bolt's work is held on its land line".

## Impact

- `plugin/lib/gather.py`: the decision `carried_bolts`, the read `bolt_lines`, and each bolt's `carries` or `carries_error` in a kit's read.
- `plugin/lib/kit.py`: `carries_of`, reading `CARRIES`.
- `plugin/lib/plan.py`: the script `CARRIES`; `bolts_carried`, `carries_said`, `carried_named`, `carries_refusal` and `landing_carries`; `landing_submitted`; `landing_rows` and `land_facts`; the rail's land line in `rail_rows`; `bolts_data` and `bolts_text`.
- `plugin/bin/crew` (usage header), `README.md`, `plugin/skills/crew/SKILL.md`.
- `crew bolts --json` gains `carries` and `carries_error` on each bolt. The board and the mod read neither, and the rail's rows keep their shape, so nothing they draw changes (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/plan.py
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_landings.py
tests/py/test_landing.py
tests/py/test_pane_landing.py
tests/py/test_rail.py
tests/py/test_bolt_submissions.py
tests/py/test_kit.py
tests/contract/test_git.py
tests/contract/test_gather.py
```

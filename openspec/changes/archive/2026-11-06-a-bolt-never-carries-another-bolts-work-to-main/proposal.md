# A bolt never carries another bolt's work to main

## Why

On the Willdan box (wldn, chuck-herdr-alpha), in WilldanGroup/breadboard-kit, the bolt `breadboards-access-choice-is-one-popover` landed on main at `99c0e88` on 2026-11-06 carrying the bolt `breadboard-shows-a-deleted-app-as-deleting`, which was held, and crew read the held bolt as landed (signal `WilldanGroup/crew-state:wldn/main signals/2026-11-07-wldn-ops-052d0a47/01`: "popover bolt b0fdcee held it"). The deleting bolt's landing 214, `f5e67f35`, merged its unit `a-deleted-app-reads-deleting-until-switchboard-retires-it` from slot `brd-2-unit-1`. The popover bolt was given at 19:00:38Z, and its unit's construct in the same slot at 19:01:23Z cut the place right: its first commit `0a3071e0` sits on `853cb325`, main's tip, where the bolt was made. At 19:51:12Z the unit's code-stage coder rebased its branch onto `f5e67f35`, and landing 216, `b0fdceeb`, merged that into the popover bolt. The coder's session (`ec87649b`, read on the box) shows why. Its smoke run against its own branch failed. It then listed the host's `bolt/*` branches that held its base, took the first, `bolt/breadboard-shows-a-deleted-app-as-deleting`, as its bolt, ran `sluice exec bolt/breadboard-shows-a-deleted-app-as-deleting -- moon run brd-console:smoke`, and rebased onto it. The coder's brief names its bolt only as `bolt/<bolt>` and the code prompt names none, and the team held both bolts (`teams.16`). Nothing of crew's then saw the carried work: not the unit's merge into its bolt, not the landings card, not `crew bolt submit`.

That breaks `plan.19` (every place's work is its own bolt's, as GitHub holds it), `plan.8` (a bolt meets main alone, and nothing lands while it is held) and `teams.22` with record 0044's point 2 (a bolt ships alone). The user ruled that the box's crew faults are fixed on crew main ("Yes: fix them on crew main, for the box").

## What Changes

- **A bolt carrying another bolt's work does not land.** A commit of another bolt's own is one on that bolt's first-parent line beyond main: the landings sluice made on it. While a bolt holds such a commit and main lacks it, `crew bolt submit` submits nothing, naming that bolt and its landings. Its row on the kit's landings card is held with no box, as a conflict holds one (`plan.8`), so no landing card is raised for it. The rail's land line says it can't land, and `crew bolts` says it is held. Everything is read from the branches as GitHub holds them, never from a commit's words. The bolt whose work was carried is not held, and its own landing takes that work to main, after which the carrying bolt lands.
- **A merge into a bolt carries no other bolt's work.** A unit's, chore's or fix's merge is refused before its submission while its branch holds another bolt's landing that main and its own bolt lack. The refusal names that bolt and its landings, and says to take that work out or to merge once main holds it.
- **The coder builds on its own bolt alone.** The coder's brief names its bolt as the one its branch tracks, `git rev-parse --abbrev-ref @{upstream}`, its bolt as GitHub holds it. No other `bolt/*` branch is its to rebase onto, merge, test against or take work from. It takes its bolt in with `git fetch -q origin` and `git rebase @{upstream}`, never the host's lagging copy.
- **A moved unit carries nothing of the bolt it leaves.** `crew unit move` rebases a unit's place from the bolt it leaves onto the bolt it joins, each read where it lives after a fetch. It used the host's copies, and a lagging copy of the bolt it left replayed that bolt's landings onto the bolt it joined.
- A slot holds no place of its own: each unit's place is cut from `origin/bolt/<bolt>` after a fetch, whatever the slot last built. Today's cut is right, and a contract test now pins it across two bolts.
- README, the crew skill and `crew`'s usage header say this (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: four requirements of their own: "A bolt carrying another bolt's work does not land", "A merge carries no other bolt's work", "A place's work starts at its own bolt alone" and "crew bolts says a bolt carries another bolt's work".
- `rail-cards`: a requirement of its own, "A row carrying another bolt's work is held".
- `crew-rail`: a requirement of its own, "A bolt carrying another bolt's work is held on its land line".

## Impact

- `plugin/lib/gather.py`: the decision `carried_bolts`, the read `bolt_lines`, and each bolt's `carries` or `carries_error` in a kit's read.
- `plugin/lib/kit.py`: `carries_of`, reading `CARRIES`.
- `plugin/lib/plan.py`: the script `CARRIES`; `bolts_carried`, `merge_bolts`, `merge_carried_refusal`, `carries_said`, `carried_named`, `carries_refusal` and `landing_carries`; the merge stages of units (`run_check`), chores (`chore_check`) and fixes (`fix_cmd`); `landing_submitted`; `landing_rows` and `land_facts`; the rail's land line in `rail_rows`; `bolts_data` and `bolts_text`; `REBASE` and `op_unit_move`.
- `plugin/roles/coder.md`; `plugin/bin/crew` (usage header), `README.md`, `plugin/skills/crew/SKILL.md`.
- Tests: `tests/py/test_landings.py`, `tests/py/test_landing.py`, `tests/py/test_pane_landing.py`, `tests/py/test_rail.py`, `tests/py/test_bolt_submissions.py`, `tests/py/test_kit.py`, `tests/py/test_stage_rules.py`, `tests/contract/test_git.py`, `tests/contract/test_gather.py`, `tests/t-briefs.sh`.
- `crew bolts --json` gains `carries` and `carries_error` on each bolt. The board and the mod read neither, and the rail's rows keep their shape, so nothing they draw changes (`code.8` not reached). Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/plan.py
plugin/roles/coder.md
plugin/bin/crew
README.md
plugin/skills/crew/SKILL.md
tests/py/test_landings.py
tests/py/test_landing.py
tests/py/test_pane_landing.py
tests/py/test_rail.py
tests/py/test_bolt_submissions.py
tests/py/test_kit.py
tests/py/test_stage_rules.py
tests/contract/test_git.py
tests/contract/test_gather.py
tests/t-briefs.sh
```

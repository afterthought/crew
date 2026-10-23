# A landing's pull request is live only on the user's word

## Why

A bolt lands only on the user's word (`plan.16`, `roles.2`), but a landing that sluice refuses leaves its GitHub pull request open and ready, and sluice takes an open, ready pull request back into main's queue on its own whenever its branch moves. The pull request's branch is the bolt's own, `bolt/<bolt>`, so the team's fix for the refusal moves it, and the bolt lands with nobody's word. That is how `bolts-live-on-github` landed on crew's main as 1c75a9f6 on 2026-10-23, its landing card never answered (signal 2026-10-23-swancloud-ops-31c1ea3d/01); swancloud-ops then marked crew's #99 a draft by hand to keep `crews-small-leftovers-of-late-october` from landing the same way (signal 2026-10-23-crw-6-conductor-888a3e7c/01). The landing card already follows the user's word: crew holds it when a fix starts and raises it again once the bolt is proven (record 0031 §1, §3). The pull request has to follow the same word.

## What Changes

- **A landing that does not land leaves its pull request a draft.** When `crew bolt submit` ends with the bolt not on main (refused, failed, withdrawn, stopped, or crew can't tell), crew marks the bolt's open pull request into main a draft before it answers, and says so, with the link and what makes it live again. A draft is one sluice never takes into the queue, however the branch moves.
- **A fix on the bolt holds the pull request as it holds the card.** When a fix starts on a bolt, crew marks the bolt's live landing pull request a draft as it withdraws the landing card "held for a fix".
- **No merge into a bolt runs past a live landing pull request.** Before a unit's, chore's or fix's merge into a bolt starts, crew marks the bolt's live landing pull request a draft; when it can't, the merge does not start, and crew names the pull request and why.
- **The next landing on the user's word readies it.** `crew bolt submit` marks the bolt's draft pull request ready for review before it submits, so sluice takes it for the head it now has, and tests the same commits again when the head has not moved.
- crew reads and marks pull requests through GitHub's own CLI, `gh`, on the team's host, only in a kit whose sluice policy at main takes pull requests into main; a kit that takes none is asked nothing.
- The tests' `gh` is a stub, guarded like the other stubs, so no test reaches GitHub.
- README, the crew skill and `crew`'s usage header say what a landing that does not land leaves, and what readies it (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a landing's pull request is live only while the user's word stands for its head: a draft after a landing that does not land, after a fix starts and before any merge into the bolt; readied by the next landing.

## Impact

- `plugin/lib/plan.py`: `bolt_submit`, `landing_said`, `landing_held`, the unit's and chore's merge checks (`run_check`, the chore's check) and `fix_cmd`'s merge, and new scripts that read and mark the pull request on the team's host.
- `plugin/lib/kit.py`: whether a kit's policy takes pull requests into main, and what `gh` said of the bolt's pull request.
- README, `plugin/skills/crew/SKILL.md`, `plugin/bin/crew`'s usage header.
- `tests/stubs/gh` (new), `tests/run`'s stub guard, `tests/py/test_landing.py`, `tests/py/test_kit.py`, `tests/t-journey-land.sh`, `tests/moon.yml`.
- Each team's host needs `gh` on its path, signed in with write access to each kit's repository that takes pull requests (on deneb, `afterthought`, read 2026-10-22).
- Nothing outside the standard library is imported (`code.1`); nothing is pushed (`state.5`).

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/stubs/gh
tests/run
tests/lib.sh
tests/py/test_landing.py
tests/py/test_kit.py
tests/py/test_bolt_commands.py
tests/t-journey-land.sh
tests/t-journey-units.sh
tests/t-docs.sh
tests/moon.yml
```

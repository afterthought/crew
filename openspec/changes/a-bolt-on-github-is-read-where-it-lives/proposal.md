# A bolt on GitHub is read where it lives

## Why

A bolt given since bolts moved to GitHub lives on GitHub's `bolt/<bolt>`, and sluice lands every merge into it there. crew still reads the bolt from the host's own `refs/heads/bolt/<bolt>`, which sluice's statement makes its private copy, levelled only at a landing it reads and read by nobody (sluice clause 124); sluice 0.36.4 does not level it at all. So on deneb on 2026-10-23 `a-verify-ends-at-its-report`'s two chores landed on GitHub (#152, #157, head d0546507) while the host's copy stayed at 6a929a44: `crew bolts` and `crew chore wait` called both chores unmerged, and the bolt never read proven (signal 2026-10-23-crw-6-ops-f46cd335/01). plan.19's reading of the same day rules it: a bolt on GitHub is read where it lives, `origin/bolt/<bolt>` after a fetch, as main is read, and the host's copy is sluice's alone.

## What Changes

- **One answer to "where is this bolt read".** A bolt is read at GitHub's copy, `origin/bolt/<bolt>`, when the host holds that copy and the policy in it names a remote for the bolt. Otherwise it is read at the host's `bolt/<bolt>`, which is then the bolt itself: a bolt made before gives went through sluice, kept on its host until it lands, or one in a kit whose policy names no remote. The host's copy of a bolt on GitHub is never read for anything about the bolt.
- **Every read of a bolt goes there.** Its head and when it was made, its verification (the `Sluice-Result` trailer at that head), the changes and chores it holds, open and archived, a chore's place's own commits beyond it, whether a fix has merged into it, the merge stage's "the bolt holds it", the landing card's base, the verify's undeclared paths, a forecast's words, a dependent's rebase onto it and its take of what it comes after, and the commit that brought a unit's change to it.
- **Fetched as main is fetched (plan.18).** The read on every team read and every refresh of the rail and the board fetches nothing; it reads GitHub's copy as the host last fetched it. A read a decision of the moment rests on fetches the kit's origin first: `crew bolts`, a give's check that the team's bolt reads proven, every look a wait takes at a merge stage, and a give, which fetches the branch it had sluice make. A fetch that fails is said: the read refuses or the look delivers nothing, naming git's words, never falling back to the host's copy.
- **sluice levelling the copy or not changes nothing crew reads.** crew's stub sluice can land a bolt's merge on GitHub and leave the host's copy and its tracking ref where they were, as sluice 0.36.4 under its app's identity does, and the journeys prove crew sees the merge.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: a bolt on GitHub is read at GitHub's copy after a fetch where a decision rests on it, never at the host's copy; the stages, `crew bolts`, waits and gives follow.

## Impact

- `plugin/lib/gather.py`: the bolt's read ref decided once (`bolt_at`) from what the host holds of GitHub's copy and the policy in it, with the policy matching moved here from `kit.py` so the file sent to hosts stays standard library only (`code.1`); `kit()`'s per-bolt facts, `chore_place`, `own_head` and `fix_merged` read there; a request may ask for a fetch first.
- `plugin/lib/kit.py`: `branch_table` and `bolt_remote` use gather's policy matching; what they decide does not change.
- `plugin/lib/plan.py`: `survey` and `stages_for` take a fetch; `bolts_view`, `bolt_give`'s proven check, `deliverable_facts`'s merge look and `BOLT_CREATE` fetch; `land_facts`, `chore_commits`, `undeclared`, `change_words`, `forecast_words`, `rebase_words`, `ONTO`, `TAKE` and `landed_at` read the bolt at its read ref.
- `tests/stubs/wt-submit` and `tests/stubs/sluice`: a switch that lands on GitHub and leaves the host's copy and tracking ref behind.
- `README.md` and `plugin/skills/crew/SKILL.md` say where a bolt on GitHub is read and when crew fetches it (`docs.2`).
- Shares `gather.py`, `plan.py` and `kit.py` with `no-worktree-holds-main-or-a-bolt-branch`, still open on main.
- Until this lands, ops levels a lagging copy by hand on the user's word (plan.19's reading); once it lands no hand is needed. The landing's own submission still checks out the host's copy; that is outside this change.

## Touches

```
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/plan.py
tests/stubs/wt-submit
tests/stubs/sluice
tests/py/test_bolt_commands.py
tests/py/test_stage_ends.py
tests/py/test_kit.py
tests/py/test_stages.py
tests/py/test_forecast.py
tests/contract/test_gather.py
tests/contract/test_git.py
tests/t-journey-units.sh
tests/t-journey-plan.sh
tests/t-journey-merge.sh
tests/t-journey-prompts.sh
tests/moon.yml
README.md
plugin/skills/crew/SKILL.md
```

# Proposal

## Why

On 2026-10-23 a chore's merge into crw-6's bolt `crews-small-leftovers-of-late-october` dropped two merges that had already landed on it. The bolt was made on its host before bolts lived on GitHub, and a refused landing had pushed an older copy of it to GitHub. When a later merge brought the bolt a sluice policy naming `origin`, sluice began sending the bolt's merges to GitHub, formed the next one on that older copy, and the docs chore and the take-main fix were lost from the bolt (signal 2026-10-23-crw-6-conductor-906b7fc5/01). Record 0032, as amended on 2026-10-22, asked the planner and main-level ops to keep that policy merge last in such a bolt, and nobody did. `plan.19` now rules that a bolt split this way takes no merge, and that crew refuses one; `roles.3` says a rule broken once is held by a check in crew, not firmer words.

## What Changes

- A unit's, chore's or fix's merge into its bolt is refused before anything is submitted when the bolt is split: the host's own `bolt/<bolt>` has a tip whose policy names a remote for the bolt, and the bolt's branch on that remote, read after a fetch, does not hold that tip. The refusal names the split (both commits and how many merges GitHub's copy lacks) and the bolt's landing as the way on, since the landing's own push puts the host's tip on GitHub and makes the two one.
- A bolt whose tip names no remote, a bolt whose copy on GitHub holds the host's tip, a bolt with no branch on its host, and a bolt GitHub has no copy of (which sluice refuses itself, dropping nothing) take their merges as today.
- When crew cannot read GitHub's copy, the merge is refused naming git's words, never let through on a guess.
- The landing, `crew bolt submit`, is not checked: it is the way on.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a merge into a bolt split between its host's tip and an older copy on GitHub is refused, naming the split and the landing.

## Impact

- `plugin/lib/plan.py`: a read of the bolt's copy on its remote (one script, run on the team's host), a decision on it, and a refusal at the start of a unit's and a chore's merge stage and of `crew fix merge`.
- `plugin/lib/kit.py`: the reading of that script's output.
- `tests/py/test_bolt_commands.py`: the decision's cases; `tests/py/test_kit.py`: the reading's; `tests/contract/test_git.py`: the script run on real git against a scratch remote.
- `docs/architecture/plan.md` is not edited: `plan.19` already rules the refusal, and its details are the design agent's to mark built after the landing (`docs.7`).
- No push, no new command, nothing of sluice's. What crew models and the agents' bands are unchanged.

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
tests/py/test_bolt_commands.py
tests/py/test_kit.py
tests/contract/test_git.py
```

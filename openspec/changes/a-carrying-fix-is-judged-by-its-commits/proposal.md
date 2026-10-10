# A carrying fix is judged by its commits

## Why

When a bolt's landing conflicts with main, the team's fix replays the bolt's commits onto main, and `crew fix <team> <name> --merge` is meant to make that fix the bolt's head. Today crew decides whether the fix is such a replay by asking `git range-diff` to pair the commits, and range-diff pairs by how alike two patches look. When main has rewritten the lines around what one of the bolt's commits edits, the faithful replay of that commit no longer looks alike enough at range-diff's default, so crew finds it unpaired and merges the fix as an ordinary fix, which is the very failure the carry exists to prevent. crw-1's fix agent hit this on 2026-10-10: "1 of 13 bolt commits unpaired: b515c00 … pairs with no commit of the fix" (signal 2026-10-10-crw-1-conductor-69720a11/01). Record 0015, restated that day, and `plan.8` now say the commits themselves are the judge.

## What Changes

- crew decides that a fix carries the bolt when the fix holds exactly as many commits beyond main as the bolt does, and, in order, each of the fix's commits is the bolt's commit in the same place replayed: the same message and the same author, its patch the same or changed. A commit whose surroundings main rewrote therefore still counts, however different its patch now looks.
- A fix that adds a commit, drops one, reorders them, or rewords or re-authors one does not carry the bolt; it merges as every fix does, and crew says which commits are not the bolt's, as it does today.
- crew still prints `git range-diff`'s view of the two, beside its judgment, as the reading the conductor can look at; it no longer decides anything, and crew no longer parses it.
- How many commits the resolution changed, which crew reports when it moves the bolt, is counted by comparing each pair's patch.
- README, the crew skill and `crew`'s usage header say how the fix is judged (`docs.2`); `_open.md` no longer lists the item, and the `plan.8` and `teams.5` details name what builds it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: the requirement "A fix that carries the bolt onto main becomes its head" judges the fix by its commits' count, order, message and author instead of by `git range-diff`'s pairing, and prints range-diff as the reading.

## Impact

- `crew fix <team> <name> --merge` moves the bolt for a replay it used to merge; every other outcome is as before. Its output gains the range-diff reading, and the words for a fix that does not carry change from range-diff's "pairs" to which commits are or are not the bolt's.
- `plan _carry`'s shell assignments (`CARRIES`, `OLD`, `NEW`, `COMMITS`, `CHANGED`, `WHY`) stay as they are, so the bash side of `--merge` does not change.
- Every kit's bolts are judged the same way; nothing a kit configures is involved.

## Touches

```
plugin/lib/plan.py
plugin/bin/crew            (usage header only)
plugin/skills/crew/SKILL.md
README.md
tests/t-fix.sh
docs/architecture/plan.md  (plan.8 details)
docs/architecture/teams.md (teams.5 details)
docs/architecture/_open.md
```

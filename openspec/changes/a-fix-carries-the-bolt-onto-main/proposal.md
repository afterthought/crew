# A fix carries the bolt onto main

## Why

A bolt is built while main moves, so it usually lands behind main, and the landing's rebase is where the two meet. When that rebase conflicts, the main-ops brief sends the conflict to the team as a fix, but a fix can only merge into the bolt, which replays main's commits over the bolt's tip, conflicts on the same lines again, and would leave the bolt holding its old commits under copies of main's. The only way through today is the user moving the bolt's branch by hand, which is what happened to `a-teams-cards-are-its-conductors` on 2026-10-09 (signal 2026-10-09-crw-1-conductor-47d11d45/01). Record 0015 decides that the team's fix carries the bolt onto main and crew makes it the bolt's head; this change builds that.

## What Changes

- When a landing's rebase conflicts, main-ops aborts it, nothing lands, and main-ops tells the conductor (and the user) the commit that conflicted and the files.
- The conductor starts a fix for it as for any defect. The fix's agent replays the fix branch's commits, which are the bolt's own, onto the kit's main, resolves each conflict keeping both intents, adds no commit of its own, runs the tests the resolved files affect, and stops.
- `crew fix <team> <name> --merge` first asks whether the fix carries the bolt: its branch no longer holds the bolt's head but sits on a commit the kit's main holds, and `git range-diff` pairs each of the bolt's commits beyond main with exactly one of the fix's, in order, equal or changed, with none of the fix's left unpaired. When it does, crew itself moves `bolt/<bolt>` to the fix's head in the bolt's worktree, ends the fix's agent, runs the kit's post-merge checks on the new head as a merge would, records the move, and says so. When it does not, the fix merges as every fix does, and crew names the commits that did not pair.
- After a carry the bolt must be proven again before it lands: crew says so when it moves the bolt, and the conductor asks ops for a new proof and posts the landing card again only once that proof is clean.
- The main-ops, conductor, coder and ops briefs say all of this; README, the crew skill and `crew`'s usage header say what `--merge` now does.
- `plan.8` and `teams.5` stop being open items: the `_open.md` line goes, and `teams.5`'s details name what builds it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a fix whose branch is the bolt's own commits replayed on main becomes the bolt's head by crew's move, with the bolt's checks run and its proof owed again; a landing whose rebase conflicts lands nothing and goes back to the team as such a fix.

## Impact

- `crew fix <team> <name> --merge` does one of two things now; its output says which. Nothing else on the command line changes.
- A new run-record act, `fix.carry`, on the fix and the bolt.
- The main-ops, conductor, coder and ops briefs change; each agent takes them at its next fresh start once the bolt lands and every host has pulled.
- Every kit's bolts benefit, not only crew's: the move and the checks go through git and the kit's own worktrunk hooks.

## Touches

```
plugin/bin/crew
plugin/lib/plan.py
plugin/roles/main-ops.md
plugin/roles/conductor.md
plugin/roles/coder.md
plugin/roles/ops.md
plugin/skills/crew/SKILL.md
README.md
tests/t-fix.sh
tests/t-briefs.sh
tests/moon.yml
docs/architecture/teams.md
docs/architecture/_open.md
```

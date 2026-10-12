# No worktree holds a bolt's branch

## Why

A kit that merges through sluice has its bolt branches moved by sluice, through gix, and protected by sluice's reference-transaction hook, which refuses every other move: `git merge`, `git reset`, `git rebase`, `git branch -f`. crew keeps each bolt's branch checked out in `<kit>/bolts/<bolt>`, so every landing sluice makes leaves that worktree's index and files behind its HEAD; crew's landing rebases the bolt's branch onto main, and a carrying fix resets it, both of which sluice's hook refuses. The user: "we should try to move CREW outside of SLUICE's control to a design where we don't check out the bolt branch as a work tree." Record 0023, point 7.

## What Changes

- **`bolt/<bolt>` is never checked out.** Units and fixes merge into it as now, by `wt merge` or `wt submit`.
- **The bolt's checkout is on `land/<bolt>`**, a branch crew makes beside the bolt's and that tracks it. crew brings it level with `git merge --ff-only bolt/<bolt>` whenever it reads that the bolt moved, and before a proof; a local change git would overwrite keeps it where it is, recorded and told to the conductor.
- **`land/<bolt>` is what lands.** main-level ops merges it onto main from the bolt's checkout, through the kit's hooks, rebasing `land/<bolt>`; a carrying fix becomes `land/<bolt>`'s head by crew's move. `bolt/<bolt>` is never rebased or reset. After a carry, later units and fixes branch from and merge into `land/<bolt>`.
- **crew verifies a bolt's head through the kit's test adapter**: after each move of `land/<bolt>`, in a place of its own for that revision, on the checks the kit's declaration requires of bolt branches; in a kit on sluice, a head sluice landed with a passing verdict needs no run. `crew bolt verify <bolt>` prints the verification of the head, and with `--again` runs it again. **BREAKING** for crew's own repository: its `[post-merge]` verification, `bolt-verify.sh` and `bolt-status.sh` go.
- **The tidy** knows a bolt's checkout by `<kit>/bolts/<bolt>` on `land/<bolt>`, and removes `bolt/<bolt>` once the bolt is gone and main holds it; a bolt given before this change keeps its old shape until it lands.
- The conductor's, ops's and main-ops's briefs say so.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: giving a bolt makes `bolt/<bolt>`, `land/<bolt>` and the checkout on `land/<bolt>`.
- `bolt-teams`: where a bolt is built, deployed from and landed; what a carrying fix moves; the bolt's line for fixes after a carry; which worktrees crew removes; a requirement is added for the checkout following its bolt.
- `kit-toolchain`: requirements are added for verifying a bolt's head through the kit's test adapter, and for reading and running that verification again.
- `merge-gate`: the bolt's verification by crew's own post-merge hook is removed, replaced by `kit-toolchain`'s.

## Impact

- `plugin/lib/plan.py` (`bolt give`, `make_place`, `carry_move`, `carry_judgment`, the merge stage's end, `merge_how`, `tidy`, `tidy_over`, `bolt land`), `plugin/lib/kit.py` (the test adapter's run and read), `plugin/bin/crew` (`crew prove`, `crew bolt verify`, the usage header), `plugin/roles/conductor.md`, `ops.md`, `main-ops.md`, crew's `.config/wt.toml`, `.config/hooks/`, `.config/sluice.toml`, README, CLAUDE.md, the crew skill, and the tests named in the tasks.
- Built after the one-process refactor lands, since both rework these commands, and after `a-kit-declares-its-toolchain-and-tests` and `a-carrying-fix-is-judged-by-its-commits`, whose requirements this one modifies.
- Each kit whose post-merge hook verifies the branch of the worktree it runs in (swancloud's `flake-gate verify`, switchboard's `post-merge-verify`) changes it, in its own repository, to verify main only, and declares its bolt branches' required checks, before this reaches a host it uses: worktrunk runs a merge into a bolt's post-merge hooks in the kit's main checkout once no worktree holds the bolt.

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
plugin/bin/crew
plugin/roles/conductor.md
plugin/roles/ops.md
plugin/roles/main-ops.md
plugin/skills/crew/SKILL.md
.config/wt.toml
.config/hooks/bolt-verify.sh     (removed)
.config/hooks/bolt-status.sh     (removed)
.config/sluice.toml
README.md
CLAUDE.md
tests/py/test_follow.py
tests/py/test_tidy.py
tests/py/test_kit.py
tests/contract/test_git.py
tests/contract/test_wt.py
tests/t-journey-units.sh
tests/t-journey-land.sh
tests/t-journey-fix.sh
tests/t-merge-gate.sh
tests/t-briefs.sh
tests/moon.yml
```

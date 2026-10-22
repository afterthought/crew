# Tasks

## 1. A give makes the bolt on GitHub, and every place is cut from it

- [x] 1.1 crew reads the remote a kit's policy names for a bolt branch, and `crew bolt give` refuses a kit whose policy at `origin/main` names none, naming the file and the key (design, Decision 1 and 2, Task notes 1.1). Logic: `tests/py/test_kit.py`. Contract: `tests/contract/test_kit.py`.
- [x] 1.2 crew reads the host's sluice version and sluice's `branch create` and `branch delete` documents by facts recorded from sluice 0.36.4 (Decision 2, Task notes 1.2). Logic: `tests/py/test_kit.py` on `tests/py/sluice-0.36.4/`.
- [x] 1.3 `crew bolt give` refuses a host's sluice below 0.20.0 or one it can't read, has sluice make `bolt/<bolt>` from main before the plan write, refuses in sluice's words with the plan unchanged, marks the local branch as crew's, and deletes the new branch again when the write is refused (Decision 2, Task notes 1.3). Logic: `tests/py/test_bolt_commands.py`.
- [x] 1.4 Every unit, chore and fix place of a bolt on GitHub is cut from `origin/bolt/<bolt>` after a fetch, tracking it, a bolt made before is cut from its local branch, and a moved unit tracks its new bolt the same way (Decision 3, Task notes 1.4). Contract: `tests/contract/test_git.py`.
- [x] 1.5 A place tracking `origin/bolt/<bolt>` is read as a place of that bolt wherever crew reads a place's upstream (Decision 4, Task notes 1.5). Logic: `tests/py/test_tidy.py` and the stage reads' cases.
- [x] 1.6 The test kits stand on a bare remote with a policy naming `origin` for bolts and main, the stub sluice answers `--version`, `branch create` and `branch delete`, and the stubs land on the remote a branch's policy names (Decision 7, Task notes 1.6). Journey: `tests/suite t-journey-teams t-journey-units` ends with "0 failed".

## 2. A land deletes the bolt on GitHub

- [x] 2.1 `crew bolt land` has sluice delete `bolt/<bolt>` after the plan write, names a refusal in sluice's words with the bolt out of the plan, deletes a bolt made before wherever its tip's policy routes it, and the tidy unsets the mark of a bolt branch already gone (Decision 5, Task notes 2.1). Logic: `tests/py/test_landing.py`, `tests/py/test_tidy.py`. Journey: `tests/suite t-journey-land` ends with "0 failed".

## 3. A bolt made before stays local

- [x] 3.1 Each read of a team that holds a bolt on its host only, while the kit's main names a remote for bolts, says once that the bolt is local until it lands and runs no create (Decision 6, Task notes 3.1). Logic: `tests/py/test_tidy.py`. Journey: `tests/suite t-journey-teams` ends with "0 failed".

## 4. The docs say it

- [x] 4.1 README, the crew skill and `crew`'s usage header say a give and a land go through sluice on GitHub (Task notes 4.1, `docs.2`). Journey: `tests/suite t-docs` ends with "0 failed".

## 5. The parent change says the same

- [x] 5.1 `no-worktree-holds-main-or-a-bolt-branch` has its part 1 tasks ticked as built by this change, and its words for a bolt made before and its two matching requirement blocks read as this change's (Decision 8, Task notes 5.1). Check: `openspec validate no-worktree-holds-main-or-a-bolt-branch` passes.

## 6. The place holds what the bolt merged

- [x] 6.1 The unit's branch is rebased onto `bolt/bolts-live-on-github`, each conflict resolved keeping both changes' intents, and tasks 1 to 5 still hold on it (design, Decision 11, Task notes 6.1). Logic: `tests/suite logic`. Journey: `tests/suite t-journey-teams t-journey-units t-journey-land t-docs` ends with "0 failed".

## 7. A drop ends the bolt's branch through sluice

- [ ] 7.1 `crew bolt drop` of a bolt a team holds has sluice delete its branch after the plan write, says it deleted or gone, and when sluice refuses keeps it where it lives, marked `dropped`, named as the drop's unmerged work in sluice's words and recorded once as `branch.kept` (Decision 9, Task notes 7.1). Logic: `tests/py/test_bolt_commands.py`.
- [ ] 7.2 The team's reads ask sluice's delete again for a dropped bolt's kept branch once main holds its tip, saying nothing while it does not, and ask it for a bolt branch marked `given` that no plan has in place of git's delete (Decision 10, Task notes 7.2). Logic: `tests/py/test_tidy.py`.
- [ ] 7.3 A dropped bolt with no merge is deleted from the kit's remote, one holding a merge is kept there and on the host and named, and a landing that brings its tip into main has the next read delete it (Task notes 7.3). Journey: `tests/suite t-journey-land` ends with "0 failed".
- [ ] 7.4 README, the crew skill, `crew`'s usage header and the planner's role say a drop has sluice delete the bolt's branch, kept and named while main lacks its tip (Task notes 7.4, `docs.2`). Journey: `tests/suite t-docs t-briefs` ends with "0 failed".
- [ ] 7.5 `no-worktree-holds-main-or-a-bolt-branch`'s `bolt-plan` block reads as this change's again (Decision 8, Task notes 7.5). Check: `openspec validate no-worktree-holds-main-or-a-bolt-branch` passes.

## 8. The suite

- [ ] 8.1 `tests/moon.yml` is regenerated by `tests/moon-tasks` and committed, and `tests/suite --affected` ends with "0 failed" (Task notes 8.1).

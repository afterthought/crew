# Tasks

## 1. A bolt is a branch, given only with a policy

- [x] 1.1 `kit.bolt_checks` reads the checks a kit's policy requires of a bolt branch, the most specific pattern first, and refuses, naming the file, a missing policy, one that is not TOML and one with no checks for bolt branches; `kit.policy_said` reads `POLICY`'s output: `tests/py/test_kit.py` (`TestBoltChecks`) (design: *The give reads the policy from main's commit*; `teams.5`, `read.1`, `code.7`).
- [x] 1.2 `crew bolt give` makes `bolt/<bolt>` from the kit's main with no worktree, marked `branch.bolt/<bolt>.crew`, after `kit_policy` reads main's commit on the team's host: `tests/contract/test_git.py` (`test_a_bolt_is_a_branch_from_main_as_it_stands_marked_as_crews_and_no_worktree`, `test_a_kits_policy_is_read_from_mains_commit`), `tests/t-sluice.sh` (the refusals and the give), `tests/t-journey-units.sh`, `tests/t-journey-teams.sh` (design: *A bolt is a branch crew marks as its own*; `plan.8`, `read.4`).
- [x] 1.3 `bolt_place` starts the conductor and ops in the kit's main checkout for a bolt with no worktree, and in the worktree an older bolt still has: `tests/t-journey-teams.sh`, where a team up when its bolt is given starts again in the kit's main checkout and resumes there (`teams.6`, `plan.9`).

## 2. Every merge into a bolt is a submission

- [x] 2.1 `merge_command` is `wt submit bolt/<bolt> --no-remove` for a unit, a chore and a fix; the `sluice = true` flag and `gather.sluice` go; the merge prompt is read as the conductor's in a transcript, as the `wt merge` prompt still is: `tests/py/test_prompts.py`, `tests/py/test_chores.py`, `tests/py/test_transcript.py`, `tests/t-sluice.sh`, `tests/t-journey-merge.sh`, `tests/t-journey-chores.sh`, `tests/t-journey-fix.sh` (`teams.5`, `roles.4`).
- [x] 2.2 The carry, its judgment and crew's move of a bolt's branch go, with `tests/py/test_carry.py` and their contract cases; a fix merges as any fix: `tests/py/test_fix.py`, `tests/t-journey-fix.sh` (design: *A conflict is the bolt's, taken by a fix*; `plan.8`, `code.6`).

## 3. A landing is a submission of the bolt to main

- [x] 3.1 `crew bolt submit <bolt>` refuses a main behind GitHub's and a host with no `wt-submit` on its path, submits from `<kit>/places/land-<bolt>` on the bolt's branch with `wt submit main --no-remove` in the asker's name, removes the worktree, levels the main checkout, and records `bolt.submit`; `landing_said` reads the outcome: `tests/py/test_landing.py`, `tests/py/test_parser.py`, `tests/contract/test_git.py` (`test_a_landing_submits_from_a_worktree_on_the_bolt_and_brings_main_level`), `tests/t-journey-land.sh` (design: *The landing submits from a short-lived worktree*; `plan.8`, `plan.16`, `teams.9`).
- [x] 3.2 A landing that conflicts lands nothing, and a fix takes main into the bolt by a submission, after which the landing lands: `tests/t-journey-land.sh` (`plan.8`, `teams.5`).
- [x] 3.3 The tidy deletes a bolt branch crew marked once no plan has the bolt and no worktree is on it, and still removes an older bolt's worktree: `tests/py/test_tidy.py` (`TestBoltBranch`), `tests/t-journey-land.sh` (`plan.9`, `read.4`).

## 4. The bolt's verification is sluice's verdict

- [x] 4.1 `gather` reads each bolt's `Sluice-Result` trailer at its head, and `kit.verification` reads it green only when it starts `passed`; `crew bolts` shows it: `tests/py/test_kit.py` (`TestVerification`), `tests/contract/test_git.py` (`test_a_landings_verdict_is_its_trailer`), `tests/t-journey-land.sh` (design: *Verification is read from the landing commit*; `tests.5`, `read.2`).

## 5. crew's own merges go through sluice

- [x] 5.1 crew's `.config/sluice.toml` requires `#check-full` of `bolt/*` and `main`, open, taking no replay; `.config/wt.toml`, `bolt-verify.sh`, `bolt-status.sh`, `t-merge-gate` and `tests/suite --gate` go: `tests/t-sluice.sh` (crew's own policy), `tests/t-suite.sh` (design: *crew's own policy*; `tests.5`, `tests.10`).
- [x] 5.2 A stub `wt-submit` lands as sluice was read to land, and `tests/run` refuses to run unless it shadows a real one; fixture kits carry a bolt policy: every end-to-end test that gives a bolt, and `tests/suite --affected` ends with "0 failed" (design: *Tests*; `tests.1`, `tests.4`).

## 6. The docs

- [x] 6.1 The coder's, conductor's, dispatcher's, main-level ops's and ops's briefs, README, CLAUDE.md, the skill and the usage say merges are submissions and a landing is `crew bolt submit`: `tests/t-briefs.sh`, `tests/t-docs.sh` (`docs.2`, `tests.6`, `briefs.11`).
- [x] 6.2 The open changes that describe the old merge, `units-build-at-once-and-are-reviewed-in-batches`, `a-kit-declares-its-toolchain-and-tests` and `a-stages-prompt-is-taken-or-sent-again`, are rewritten to it: `openspec validate --strict` on each (`docs.3`).

# Units merge and bolts land only through sluice

## Why

Record 0026 (accepted 2026-10-13, "Drop wt merge now"): a bolt is a branch sluice moves. Merging with `wt merge` behind a kit's merge hooks let a bolt hold what its checks had not passed until a post-merge verification said so, and a landing that conflicted came back as a fix crew judged and moved the bolt to (record 0015), a judgment that failed on real bolts. sluice tests each submission merged with its target and lands it only when the target's required checks pass, so the bolt only ever holds what passed and its verification is sluice's verdict on its last landing.

## What Changes

- **A bolt is the branch `bolt/<bolt>` and no worktree.** `crew bolt give` makes it from the kit's main as it stands, marks it crew's in the kit's git config, and refuses, naming the file, a kit whose `.config/sluice.toml` on main names no checks for its bolt branches. The conductor and ops start in the kit's main checkout; a bolt given before keeps its worktree until it lands or is dropped, and the tidy knows both shapes.
- **Every merge into a bolt is a submission**: the merge stage of a unit, chore or fix is `wt submit bolt/<bolt> --no-remove`; the `sluice = true` flag and `gather.sluice` go. **BREAKING** for a kit with no bolt policy: crew gives it no bolt.
- **A landing is a submission of the bolt to main**: `crew bolt submit <bolt>`, main-level ops's, refused while the kit's main is behind GitHub's, makes a short-lived worktree on the bolt's branch on the team's host, runs `wt submit main` there and waits for sluice, then removes the worktree and brings the kit's main checkout level. A conflict lands nothing and moves nothing; the team takes main into the bolt by a fix submitted to it. The carrying fix, its judgment and crew's move of a bolt's branch go.
- **crew's own merges go through sluice**: crew's `.config/sluice.toml` requires the `check-full` tasks of `bolt/*` and `main`, run open on the host and taking no replay; `.config/wt.toml`'s merge gate and post-merge verification, `bolt-verify.sh`, `bolt-status.sh`, `t-merge-gate` and `tests/suite --gate` go.
- The briefs, README, CLAUDE.md, the skill and the usage say so.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: a bolt is a branch only and moves only through sluice; merges are submissions; a landing is a submission and a conflict the team's, by a fix; the carrying fix goes; the tidy removes a bolt's branch crew made.
- `bolt-plan`: `crew bolt give` makes a branch and no worktree, refused for a kit with no bolt policy.
- `merge-gate`: sluice gates every merge into a bolt and onto main on crew's `check-full` tasks, and the bolt's verification is sluice's verdict; crew's own post-merge verification goes.
- `main-level`: main-level ops lands by `crew bolt submit`.
- `test-suite`: sluice, not a merge hook, runs the suite on each merge.

## Impact

- `plugin/lib/plan.py` (`merge_command`, `bolt_give`, `kit_policy`, `BOLT_BRANCH`, `POLICY`, `LANDING`, `landing_said`, `bolt_submit`, the tidy, the carry gone), `plugin/lib/kit.py` (`bolt_checks`, `verification`, `policy_said`), `plugin/lib/gather.py` (each bolt's verdict, the policy), `plugin/lib/crew.py` (`bolt_place`), `plugin/lib/transcript.py` (the merge prompt), `plugin/bin/crew`, `plugin/hooks/cards`.
- `.config/sluice.toml`, `.config/wt.toml` and `.config/hooks/` gone, `tests/suite`, `tests/run`, `tests/stubs/wt-submit`, `tests/lib.sh`, the tests named in the tasks.
- The briefs of the coder, conductor, dispatcher, main-level ops and ops; README, CLAUDE.md, the skill.
- Every host that runs a team needs `sluice` and `wt-submit` on its path, which the fleet's setup installs at the user's next deploy, and every kit a bolt policy, before its teams merge; crew assumes them as it does `wt`.
- A kit's main moves only through sluice: the user's own commits and the design agent's records are submitted from a branch (`state.3`).

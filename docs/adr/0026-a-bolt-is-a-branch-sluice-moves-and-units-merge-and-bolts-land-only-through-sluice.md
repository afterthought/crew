---
number: 26
title: A bolt is a branch sluice moves, and units merge and bolts land only through sluice
status: proposed
date: 2026-10-13
decision-makers:
- Chuck Swanberg
---

# A bolt is a branch sluice moves, and units merge and bolts land only through sluice

Status: proposed to the user on 2026-10-13, in the elaboration session; accepted only on their yes.

Deciders: the user, in the elaboration session of 2026-10-13, whose words below are the decision; written by the elaboration session. It closes the second point record 0023 held for an elaboration.
Amends: `teams.5`, `plan.8`, `plan.9`, `plan.16` and `tests.5`, with `code.6`'s details; record 0014, D7; record 0023, its second held point. Supersedes record 0015. Drops the held change `no-worktree-holds-a-bolts-branch`.
Sources: `openspec/explorations/bolt-branches-under-sluice/reading.md`; the held change's `design.md` and `proposal.md`; sluice's `phase-1-integrations.md` sections 1, 2, 5 and 7 and its records 0002 and 0006, read on 2026-10-12 and 13 from its `phase-2-git-state` branch; crew's `plan.py` (`merge_command`, `carry`, `tidy_over`), `crew.py` (`bolt_place`), `gather.py` (`sluice`); the kits' post-merge hooks as the reading lists them.

## Context and problem statement

crew keeps each bolt's branch, `bolt/<bolt>`, checked out in a worktree under `<kit>/bolts/`. The worktree was for five things: ops deployed and proved the bolt from it; main-level ops landed from it with `wt merge main`, which rebases the bolt onto main (`plan.8`); a fix that carries the bolt onto main after a conflict became its head by a reset there (record 0015); the kit's post-merge hook ran there after each unit's merge, as the bolt's verification (`tests.5`); and the conductor's and ops's panes opened there. A kit that merges through sluice has its bolt branch moved by sluice itself after each unit lands and guarded against every other move, so that worktree goes stale, the landing's rebase and the carry's reset are refused, and no post-merge hook runs; sluice has already tested what it landed, and its landing commit carries the verdict (sluice record 0006). Record 0023 held the question, the user not persuaded by a checkout on a second branch, `land/<bolt>`: "isn't it just reversing the decision that bolts don't have branches?", and on crew verifying the bolt itself: "won't this just be sluice doing the verification?".

Records 0019 (swancloud) and 0025 took the first and fourth reasons away: ops deploys nothing and proves nothing, and a bolt's proof is the kit's checks. No kit merges through sluice yet: sluice lands bolt branches of a scratch repository end to end on its branch, "sluice lands sluice" is the last piece of its plan, no kit has `sluice = true`, and sluice is not installed on every host crew runs on.

## Decision drivers

- The user's direction in record 0023: "a design where we don't check out the bolt branch as a work tree".
- One merge path, not two designs; crew becomes flywheel, which composes sluice's SDK.
- Verification is the kit's and sluice's, never crew's own port of a test runner (record 0025).
- Nothing of crew's moves a branch sluice guards.

## Decision outcome

The user: a bolt is a branch only, "#1. but why still support wt merge? why not just sluice and wt submit?", and, offered the choice between a sluice-only design with today's path kept untouched for kits not yet on sluice and dropping `wt merge` now, told that no team then merges a unit or lands a bolt until its kit is on sluice: "Drop wt merge now".

1. **A bolt is a branch and nothing else.** `crew bolt give` makes `bolt/<bolt>` from the kit's main and no worktree. Units, chores and fixes are worktrees made from it under `<kit>/places/` and merge into it. The conductor and ops work in the kit's main checkout, as the main-level roles do.
2. **One merge path.** A unit, chore or fix merges into its bolt only by `wt submit bolt/<bolt>`, sluice's verdict its gate; `wt merge` goes from crew's merge stage, its briefs and its gates, and so does the `sluice = true` flag: a kit merges through sluice when its `.config/sluice.toml` names its bolt branches' checks, and crew gives no bolt in a kit without that policy, naming the file (`read.1`).
3. **A bolt lands through sluice.** The landing is main-level ops's submission of the bolt's branch to main, on the user's word as `plan.16` has it; sluice tests main with the bolt on main's checks and lands a merge commit carrying its verdict. When they conflict nothing lands, the conflict is the bolt's (sluice's attribution), and the team takes main into the bolt by a submission to the bolt and submits again. No rebase, no carrying fix: record 0015 is superseded, and nothing of crew's moves a bolt's branch or main by git.
4. **The bolt's verification is sluice's verdict** on its last landing, read by crew from the landing commit's trailers; crew runs nothing of its own and ports no runner. crew's own suite stays as moon tasks tagged `check-full`, which crew's policy requires of its branches.
5. **Bolts already given** keep their worktrees until they land or are dropped, and land only when their kit is on sluice; crew's tidy knows that shape until none is left.

**What sluice has to have before a kit opts in**, facts for the sluice session, not decided here:
- sluice landing itself (its piece 12), and installed on every host crew runs on, the box included;
- a submission of a branch to main by main-level ops: by branch name, or from a short-lived worktree crew makes on the bolt's branch for the submission and removes after, which sluice's hook allows since nothing moves the branch there (today `wt submit` submits the current worktree's branch and refuses a detached one);
- main's meeting with GitHub under sluice's protection, the fetch that brings a host's main up to GitHub's and the push after a landing, which are sluice's remote profile or moves its policy allows; `plan.8`'s refusal of a landing while main is behind GitHub's stands as crew's read;
- each kit's `.config/sluice.toml` with `[branches."bolt/*"]` and `[branches.main]` naming its checks, and the kits' post-merge hooks (swancloud's `flake-gate verify`, switchboard's `post-merge-verify`) becoming sluice checks or main's own.

### Consequences

- `teams.5`, `plan.8`, `plan.9`, `plan.16` and `tests.5` say the above, with `code.6`'s details; amended in this commit, marked proposed until the user's yes. Record 0015 is marked superseded; record 0014's D7 and record 0023's second held point name this record.
- One unit in crew, `units-merge-and-bolts-land-only-through-sluice`: `merge_command` and the merge stage sluice-only; the flag and `gather.sluice` gone; `bolt give` makes a branch and no worktree; `bolt_place` starts the conductor and ops in the kit's main checkout; the landing procedure in `main-ops.md` as a submission; `carry`, `carry_move`, `fix_run`'s carry judgment and their tests gone; the tidy; crew's `.config/wt.toml` post-merge verification, `bolt-verify.sh` and `bolt-status.sh` gone; `.config/sluice.toml` gaining crew's branch policies; README, CLAUDE.md, the skill and the briefs; the `bolt-teams`, `bolt-plan`, `merge-gate`, `kit-toolchain` and `main-level` specs through deltas. It is built once sluice has what the list above names, and until it lands no team merges or lands.
- The held change `no-worktree-holds-a-bolts-branch` on main is removed in the user's name; its reading stays.
- The user's sluice session is told the list above.

## Considered options

- **Keep the worktree and level it after each sluice landing** (the reading's A): the landing's rebase and the carry's reset stay refused in a sluice kit, so its bolt cannot land this way.
- **A checkout on `land/<bolt>`** (B, the held change): the bolt's branch checked out under another name, which the user called reversing the decision; and crew porting sluice's runner to verify bolts, which record 0025 makes the kit's.
- **A branch only, landing through sluice in a sluice kit and from a short-lived landing place with `wt merge` elsewhere:** two paths and new crew code for one that is going away.
- **A sluice-only design with today's path kept untouched for kits not yet on sluice:** one design and one dying path, offered as the recommendation; the user chose to drop `wt merge` now and have sluice first.
- **Sluice only, now** (chosen).

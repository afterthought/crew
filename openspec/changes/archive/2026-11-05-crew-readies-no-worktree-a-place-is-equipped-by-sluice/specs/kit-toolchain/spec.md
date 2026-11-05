## REMOVED Requirements

### Requirement: A kit declares its toolchain and test runner in sluice's policy
**Reason**: crew readies no worktree. A place is equipped by sluice at Flume's asking (Flume record 0036; sluice 147), and sluice reads the policy's `[tests]` table at the revision it is asked at. crew's code has read no `[tests]` since `the-team-machinery-leaves` retired `plan.17` on `teamless/deneb`.
**Migration**: A kit declares its toolchain and runner in `.config/sluice.toml`'s `[tests]`, as sluice reads it. crew reads of the policy only what gates its bolt branches, where they live and whether it declares a preview, through `plugin/lib/kit.py` (`bolt-plan`, `rail-cards`).

### Requirement: A command crew runs in a worktree runs inside its declared toolchain
**Reason**: crew runs nothing in a worktree for its kit's toolchain or runner. sluice's equip runs each step outside its executor, with an environment cleared as a run's is (sluice 147).
**Migration**: None in crew. When a place is made ready, and what its failure does, are Flume's (Flume 11, 12, S16). How it is made ready is sluice's.

### Requirement: A kit's moon is its own
**Reason**: crew runs no `moon --version` and no `moon setup`. sluice's equip runs the runner's version check, which refuses a moon below 2.6, and its setup (sluice 147, C.2).
**Migration**: Which moon a kit runs is still the kit's, and crew never judged it. A kit sluice equips and checks runs moon 2.6 or later, as record 0023 point 3 already said.

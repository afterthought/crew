# Bolts on GitHub

## Why

A bolt's branch is still a local branch on its team's host: `crew bolt give` makes it with git from the kit's main, and `crew bolt land` leaves it to the tidy. So a bolt has as many copies as hosts that touch it, and a merge landed on one host is invisible to another. Record 0032 and `plan.19` put every bolt on GitHub, made and ended by sluice as its one writer, and both things that waited are done: sluice has `branch create` and `branch delete` since 0.20.0 (its ADR 0026), and every swancloud host runs sluice 0.36.4. The user: "propose bolts on GitHub" (2026-10-19). This is part 1 of `no-worktree-holds-main-or-a-bolt-branch`.

## What Changes

- **A give makes the bolt on GitHub.** `crew bolt give` has sluice make `bolt/<bolt>` from main on GitHub, `sluice branch create bolt/<bolt> --from main`, run in the kit's main checkout on the team's host. crew pushes nothing.
- **A give is refused, with the plan unchanged and no branch made,** when the kit's policy on `origin/main` names no remote for its bolt branches, naming the file and the key; when the host's sluice is older than 0.20.0, which has no `branch create`, or its version can't be read, naming the version it needs and the one the host has; and when sluice refuses the create, in sluice's words.
- **Every place is cut from the bolt on GitHub.** A unit's, chore's or fix's place is cut from `origin/bolt/<bolt>` after a fetch and tracks it, so it holds every merge sluice landed, from whichever host.
- **A land ends the bolt on GitHub.** `crew bolt land` has sluice delete the branch, `sluice branch delete bolt/<bolt> --into main`, after the plan write; a refusal is named in sluice's words, the bolt still leaves the plan, and the host's branch goes as `plan.9` has it.
- **A bolt made before this stays local until it lands.** A bolt whose branch crew made on its host before gives used sluice keeps working as today: its places are cut from the local `bolt/<bolt>`, and each read of its team says once that it is local until it lands. No create is run for it: sluice has no command that puts a local branch's tip on GitHub, and its landing's pull request puts it there.
- **crew's test kits stand on a bare remote** with a policy naming `origin` for bolts and main, and the stub sluice answers `--version`, `branch create` and `branch delete` and routes each submission by the branch's policy, as sluice does.
- README, the crew skill and `crew`'s usage header say a give and a land go through sluice (`docs.2`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-plan`: a give through sluice's `branch create`, refused without the remote, the version or sluice's yes; a land through `branch delete`; a bolt made before staying local.
- `bolt-teams`: every place cut from `origin/bolt/<bolt>` after a fetch, tracking it, a bolt made before excepted.

## Impact

- `plugin/lib/plan.py` (`bolt_give`, `BOLT_BRANCH`, `kit_policy`, `make_place`, `PLACE`, `bolt_land`, `tidy`, `tidy_over`, `REBASE`, the upstream reads), `plugin/lib/kit.py` (the policy's remote, sluice's version, sluice's branch documents), `plugin/lib/gather.py` (a place's bolt read from either upstream).
- `plugin/bin/crew`'s usage header, README, `plugin/skills/crew/SKILL.md`.
- `tests/lib.sh` `kit()`, `tests/stubs/sluice`, `tests/stubs/wt-submit`, the logic, contract and journey tests named in the tasks, `tests/moon.yml`.
- The parent change `no-worktree-holds-main-or-a-bolt-branch`: its part 1 tasks ticked and its words for a bolt made before brought to this change's, so its later archive says the same.
- Outside crew, already done or the user's: sluice 0.20.0 or later on every host; a `bolt/*` ruleset on each kit's repository naming sluice's app as its one writer; each kit's own policy naming `remote = "origin"` for `bolt/*` (crew's is the chore `crews-sluice-policy-names-origin-for-bolts`, merged last in this bolt).
- Nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/lib/kit.py
plugin/lib/gather.py
plugin/lib/crew.py
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
tests/lib.sh
tests/stubs/sluice
tests/stubs/wt-submit
tests/py/**
tests/contract/**
tests/t-*.sh
tests/moon.yml
openspec/changes/no-worktree-holds-main-or-a-bolt-branch/**
```

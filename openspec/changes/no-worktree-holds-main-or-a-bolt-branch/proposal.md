# No worktree holds main or a bolt branch

## Why

Record 0032 (proposed 2026-10-16) settles where crew's agents and crew itself work once sluice lands every branch by a leased push to GitHub: no worktree of crew's checks out a kit's `main` or a bolt branch; a kit's `main` folder is a detached anchor at `origin/main` that swancloud's per-host timer alone moves; crew reads main by ref and never levels a checkout; bolts live on GitHub, their branches made and ended by sluice at crew's give and land; crew follows landings, conflicts and stray checkouts through `sluice overview --json`; and crew's own plugin reaches a host live, from a detached worktree the timer moves, or released, pinned by swancloud from crew's release tags. Today conductors and ops work in `<kit>/main` on the branch, crew's landing script levels it with `read-tree` on the host that landed and ops pulls the box's by hand, a landing refuses while the host's `main` lags GitHub's, bolts are local branches, and every session loads crew's plugin from the live `crew/main/plugin`. The user: "no worktree checks out main or a bolt branch"; "having sluice include the create/delete options"; "ideally we can toggle between these modes".

## What Changes

- **Legacy bolt worktrees are detached.** The tidy detaches a `<kit>/bolts/<bolt>` worktree at the bolt's tip when it is clean and names it when dirty, so no worktree of crew's is on a bolt branch; it goes as today when the bolt is over.
- **The landing folder and the levelling step.** `crew bolt submit` keeps its short-lived `places/land-<bolt>` on `bolt/<bolt>`; the landing script levels the kit's main checkout only while that checkout is on branch `main`, says nothing when it is detached, and the step goes once every host's anchor is detached. `crew unit run` refuses a unit start on a bolt whose landing is queued, naming it.
- **Every read of "main now" is `origin/main` after a fetch**: the bolt policy, a landing's head and the landing record, the archive a change folder is read from, the branch a give makes, the fix that takes main into a bolt, the design agent's and the operator's cuts. `plan.8`'s behind-GitHub refusal goes. The landing card closes at `crew bolt land` naming the timer; ops pushes nothing and pulls no host. The briefs lose `read-tree`, the push and the box's pull; the design agent's and the operator's say their branch is cut from `origin/main`, on blueprints too.
- **Waits read the overview.** A stage's wait keeps polling refs and reads `sluice overview --json` for each branch's `version` and for a conflict or a blame of a submission from its place, asking `sluice status <id> --json` where the submission left the queue before a look saw it; nothing of crew's waits on the timer.
- **`crew status` names a stray checkout** from the overview's `holds_queued_branch`, fixing nothing.
- **Bolts on GitHub.** `crew bolt give` refuses a kit whose policy names no `remote` for its bolts or a host whose sluice lacks `branch create`, naming the version; otherwise it runs `sluice branch create bolt/<bolt> --from origin/main`. Every place is cut from `origin/bolt/<bolt>`. `crew bolt land` runs `sluice branch delete bolt/<bolt>` and names a refusal. A bolt made before the commands shipped is put on GitHub by the same create at its tip when first read after. crew pushes nothing.
- **The plugin's modes in the record.** CLAUDE.md's "This checkout is live" is rewritten: `crew/main` is an anchor like any kit's; a host loads crew's plugin live from `crew/live/plugin` or released from swancloud's catalog; the after-landing steps go.
- README, the crew skill and `crew`'s usage header follow (`docs.2`); `board.agent_views` and the mod show a stray checkout where `crew status` names one (`code.8`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bolt-teams`: where conductors and ops work; the landing's submission, its folder and what follows; the legacy bolt worktree detached; the unit refusal.
- `bolt-plan`: a give through sluice's `branch create`, refused without the remote or the command; a land through `branch delete`.
- `main-level`: ops's landing procedure with no push and no pull; the design agent's commits from a branch cut from `origin/main`.
- `merge-gate`: the landing formed on GitHub's main by a leased push; the wait's read of the overview.

## Impact

- `plugin/lib/plan.py` (`LANDING`, `landing_said`, `bolt_submit`, `bolt_land`, `BOLT_BRANCH`, `MAIN`, `main_held`, `PLACE`, `make_place`, `change_folder`, `tidy`, `ONTO`, `landed_at`, `stage_wait`, `unit_run`, the land rows), `plugin/lib/crew.py` (`checkout`, `launch`), `plugin/lib/gather.py` `kit()`, `plugin/lib/kit.py`, `plugin/roles/main-ops.md`, `coder.md`, `conductor.md`, `design.md`, `operator.md`, `plugin/bin/crew`, `plugin/skills/crew/SKILL.md`, README, CLAUDE.md; `tests/py/test_landing.py`, `test_tidy.py`, `test_bolt_commands.py`, `test_kit.py`, `tests/contract/test_git.py`, `tests/lib.sh`, `tests/t-journey-land.sh`, `t-journey-teams.sh`, `t-journey-units.sh`, `t-briefs.sh`, `t-docs.sh`, `tests/moon.yml`.
- Parts 2 to 4 share `plan.py` with `every-crew-card-is-raised-at-its-point` and are built after its fourth change lands; parts 1 and 5 wait on swancloud's bump of sluice on the fleet (`branch create`, `branch delete`, `overview`); part 6 on sluice's `holds_queued_branch` reaching the host; part 7 on swancloud's `crew/live`, the per-host mode, crew in its release sources and its catalog.
- Nothing a team holds in a place changes: a unit's place is on its own branch and stays. A crew behind this change keeps working on a host whose anchor is still on the branch.
- Nothing is added to devenv and nothing outside the standard library is imported (`code.1`).

## Touches

```
plugin/lib/plan.py
plugin/lib/crew.py
plugin/lib/gather.py
plugin/lib/kit.py
plugin/lib/board.py
plugin/hooks/status.js
plugin/roles/
plugin/bin/crew
plugin/skills/crew/SKILL.md
README.md
CLAUDE.md
tests/
swancloud: lib/space-clone.nix, packages/swancloud-views, lib/claude-account-tools.nix (crew/live and the mode), lib/release-sources.nix, modules/home-claude-plugins.nix, packages/sluice (the bump), .config/sluice.toml (its bolts' remote), the bolt/* rulesets
sluice: branch create, branch delete, the statement's clause 45, the refusal's words
blueprints: .config/sluice.toml
```

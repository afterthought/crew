# Proposal

## Why

CLAUDE.md still tells every agent building crew that crew runs from each host's checkout of `main`, that a commit there is live at once, and that after a landing the box's checkout is pulled by hand and mac-studio's brought level with `read-tree`. Since record 0032 none of that holds: `crew/main` is a detached anchor the fleet's timer moves, and a host loads crew live from `crew/live` or released at a pinned tag (`plan.18`, `plan.19`). An agent reading the old words would pull or level a folder nobody may touch.

## What Changes

- CLAUDE.md's section "This checkout is live" becomes "How crew reaches a host". It says that `crew/main` on every host is an anchor at GitHub's main that only the fleet's timer moves, and that nobody works, commits or checks out a branch in it. It says that a host loads crew in one of two modes swancloud sets for it. Live loads from `crew/live/plugin`, a detached worktree the timer moves, so a landing is live minutes later. Released loads the version swancloud pins from crew's release tags, so a landing arrives only when that pin is deployed. Neither mode loads from a checkout on branch `main`. It also says that the user's and the design agent's commits go on a branch cut from `origin/main` and through sluice, with nothing levelled after.
- CLAUDE.md's *Proving and landing a bolt* loses the after-landing steps (the box's fetch and `merge --ff-only`, "pull every host"). Its landing step no longer says ops pushes main or brings any host's checkout up. Its line about restarts says a change reaches a host by its mode, not by a landing alone.
- The briefs are held to the same words. Main-level ops's brief on main already carries no pull of crew's checkout, since part 4 of `no-worktree-holds-main-or-a-bolt-branch` took it out. This change adds a check that no brief tells an agent to pull, fast-forward or level crew's checkout.
- `tests/t-docs.sh` pins CLAUDE.md's new words and the absence of the old ones. `tests/t-briefs.sh` pins that no brief names a pull or levelling of crew's checkout.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This changes crew's how-to and the checks on it, not what any command does (`docs.1`); `.openspec.yaml` sets `skip_specs`.

## Impact

- `CLAUDE.md`: one section rewritten, two bullets of another changed, one removed.
- `tests/t-docs.sh`, `tests/t-briefs.sh`: new phrases. Neither reads a new path, so `tests/moon.yml` is unchanged.
- No code in `plugin/` changes. Which mode a host is in, `crew/live` and the release pin are swancloud's (record 0032 §5–6).

## Touches

```
CLAUDE.md
tests/t-docs.sh
tests/t-briefs.sh
```

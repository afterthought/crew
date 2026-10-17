---
number: 32
title: No worktree holds main or a bolt branch; a kit's main folder is a detached anchor the fleet's timer moves, bolts live on GitHub made and ended by sluice, and crew's plugin runs live or released
status: proposed
date: 2026-10-16
decision-makers:
- Chuck Swanberg
---

# No worktree holds main or a bolt branch; a kit's main folder is a detached anchor the fleet's timer moves, bolts live on GitHub made and ended by sluice, and crew's plugin runs live or released

Status: proposed to the user on 2026-10-16, as `briefs.15` has it; accepted only on their yes.

Deciders: the user, in the sluice design session of 2026-10-16 (the handovers `worktrees-crew.md`, `worktrees-sluice.md`, `worktrees-swancloud.md`) and on the pane with the folders design agent the same day, whose words are quoted at each point they settled; written by the folders design agent.
Amends: `state.3`, `plan.8`, `plan.9`, `plan.16`; adds `plan.18` and `plan.19`.
Sources: `openspec/explorations/agent-folders/reading.md`, read and annotated by the user on 2026-10-16; crew's main at 2d7b87b9; sluice's main at 8d81598 (ADR 0017's leased push, ADR 0023's `overview`, ADR 0024's warning, its landing #15 that puts `remote = "origin"` under sluice's own bolts); swancloud's `lib/claude-account-tools.nix`, `lib/space-clone.nix`, `packages/swancloud-releaser`, `packages/release-signals`, `lib/release-sources.nix`, `modules/home-claude-plugins.nix`; Claude Code's plugin loading (`--plugin-dir` takes a local folder, loaded in place; marketplace plugins are copied to a cache at a version); the recovery session's held items of 2026-10-16 (the box's `box-hold` branch, the sluice bump, atlas-kit's folder on the box).

## Context and problem statement

Since ADR 0017 sluice lands a branch by a leased push to GitHub and then moves the local branch under whatever worktree has it checked out, leaving that worktree's files at the old tree: every landing shows there as a staged revert, and on a host that did not land the local branch does not move at all. Today each kit's `<kit>/main` is on branch `main` and crew's conductors and ops work in it; crew's landing script brings it level with `git read-tree -m -u` on the host that landed, and ops pulls the box's by hand; wldn's atl-1 had every merge refused on 2026-10-14 until ops reset a bolt's worktree by hand, and atlas-kit's folder on the box still holds a landing as staged deletes. Every Claude session on a host loads crew's plugin from that host's `crew/main/plugin`, so a landing is live for every agent the moment the folder moves, with nothing versioned or pinned; crew gained a git-cliff release Action today (`code.10`, v0.1.0 and v0.1.1) that nothing reads yet.

The user settled the direction in the sluice design session: no worktree checks out `main` or a bolt branch; `<kit>/main` stays at its path as a detached anchor at `origin/main`, moved only by swancloud's per-host timer; crew never moves an anchor; sluice warns of a worktree holding a branch it lands on and never refuses or moves; bolts go to GitHub like main. What crew's part left open was settled on the pane, below.

## Decision drivers

- A folder nobody works in cannot be half-moved: "no worktree checks out main or a bolt branch" removes the hazard rather than levelling after it.
- One mover per folder: swancloud's timer for anchors, crew for the places it makes, sluice for branches. Crew moving an anchor and the timer moving it would race.
- Bolts on GitHub let a bolt's places be cut on any host and let a view show any bolt; a bolt's branch then needs a maker and an ender with credentials that work unattended on every host.
- The user wants crew's own code pinned and deployed like every other tool, with a testing mode that costs nothing: "crew plugin will start going through standard crew/sluice/bolt merges and we'll get semantic releases. each crew release should get picked up by our capture system and offered as a swancloud update, which will deploy. we have 'live' right now to save time when testing. ideally we can toggle between these modes."
- Nothing in crew reads a landing's branch name, and a stage's wait reads refs on the team's host; what refs cannot give, a conflict or a blame named to its place, `sluice overview --json` gives (sluice ADR 0023).

## Considered options

1. Per-agent folders (`<kit>/agents/<agent>`) kept level by crew telling agents main moved, and sluice asked to refuse a landing while a worktree holds the branch (the folders brief's start).
2. Detached anchors moved by the fleet's timer, crew reading by ref, sluice warning only; bolts on GitHub with their branches made and ended by sluice; the plugin live or released per host.
3. As 2, but crew pushes each bolt's branch with the host's credentials and deletes it after the landing (the handover's 15:22 revision, from the user's card answer of 19:22Z in the sluice session).

## Decision outcome

Option 2.

### 1. No worktree of crew's holds `main` or a bolt branch

A kit's `<kit>/main` is a detached anchor at `origin/main`, made so by swancloud's `space-clone` and moved only by swancloud's per-host timer, which fetches and moves it when it is clean and names it when it is dirty or still on the branch. crew's `checkout()` returns it as today; a team's conductor and ops start in it and read the bolt by ref (`git log bolt/<b>`); nobody edits in it, and crew never moves it. Every read of "main now" in crew, the policy, a landing's head, the archive a change folder is read from, the fix that takes main into a bolt, the branches the design agent and the operator cut, the bolt a give makes, is `origin/main` after a fetch, never the local ref, which lags on every host that did not land. A worktree of a bolt given before record 0026 (`<kit>/bolts/<b>`) is detached by crew's tidy at the bolt's tip when it is clean, and named when it is dirty, so no worktree of crew's is on a bolt branch; crew removes it as `plan.9` has it when the bolt is over. The landing script's levelling step stays only while the folder it runs in is on branch `main`, says nothing when the folder is detached, and goes once every host's anchor is detached. Blueprints comes under the same rule: its folder detached, a sluice policy for its `main`, the design agent and the daily pass committing on a branch in a worktree of their own and submitting (the user, on the pane: "Why doesn't Sluice submit blueprints? Are we going to have a checked-out main that agents edit directly?"; settled 2026-10-16, "Under the rule").

### 2. Bolts live on GitHub, and sluice makes and ends their branches

Each kit's policy names `remote = "origin"` under `[branches."bolt/*"]`, which the kit's own change adds and crew only reads (`plan.17`): crew refuses to give a bolt whose policy lacks it, as it refuses one with no checks. A bolt's branch is only a ref on GitHub: nothing runs for it, and its worktrees are cut later by crew as places from `origin/bolt/<b>`. So `crew bolt give` asks sluice to make it, `sluice branch create bolt/<b> --from origin/main`, a push leased on the branch being absent, as sluice's GitHub App; and `crew bolt land` asks sluice to end it, `sluice branch delete bolt/<b>`, which sluice refuses while the branch's tip is not in main or a submission is queued on it. The `bolt/*` ruleset on each repository names one writer, sluice's app, for create, update and delete, as main's does; crew pushes nothing to a kit's remote, and `state.5` stands as written. The user: "I agree with everything else you said ... the vocabulary change, and having sluice include the create/delete options" (2026-10-16, on the pane). Why sluice and not crew (option 3): the app's key is unattended on every host, where crew's git on a Mac goes through 1Password's agent and asks a person; sluice's records know whether anything is still queued on the branch, so the delete can refuse safely; and one app-only ruleset is simpler than one that lets crew's credentials create and delete. The words are git's, `create` and `delete`, not `start` and `end`, since nothing runs. Until sluice ships the two commands and swancloud deploys that sluice to the fleet, bolts stay local as today and crew refuses a give that needs them, naming the version; a bolt crew made before then is put on GitHub by the same create at its local tip when it is first read after. Sluice's creation-only ruleset check (its landing #15) is not wanted by this design.

### 3. The landing folder keeps `bolt/<b>`; the card closes at the landing; the behind-GitHub refusal goes; no unit starts while a landing is queued

Sluice takes a submission only from a worktree on a branch, so `crew bolt submit` keeps its short-lived `<kit>/places/land-<b>` on `bolt/<b>` for the minutes main's queue takes; sluice warns and lands anyway, and nothing else lands on the bolt by then (the user: "We have to keep it"). The folder goes once sluice takes a submission by branch name (record 0026). The landing card closes at `crew bolt land`, "landed on GitHub's main at `<sha>`; every host's folder follows by swancloud's timer within minutes": nothing waits on a host, and no agent is told, since none works in a folder that moves (the user: "if I say to land, then what are you waiting for?"). The refusal of a landing while the kit's main on its host is behind GitHub's (`plan.8`, set 2026-10-13) goes: it guarded crew's own push of main, which sluice now makes with a lease, forming every landing on `origin/main`; a host's local `main` lagging is by design, and crew records the landing's head from `origin/main` after a fetch (the user: "Drop it"). Sluice lands what was submitted, so a unit landing on the bolt while the bolt's landing is queued is left out of main's landing and `crew bolt land` refuses until a second submission carries it; crew refuses the unit start instead, naming the queued landing (the user, on the pane: "what if another unit somehow gets spun up and tries to merge into the bolt branch while the bolt branch is trying to submit to main?"; settled, "Add the refusal").

### 4. crew learns of landings, conflicts and stray checkouts from `sluice overview --json`

A stage's wait keeps reading refs on the team's host every ten seconds; what refs cannot give, a conflict or a blame named to the place it came from and a cheap "nothing changed" (`version`), the wait reads from `sluice overview --json` (sluice v0.12.0 or later, `recent[]` and `from.path`). `crew status` names a worktree holding a branch sluice lands on from the overview's `holds_queued_branch`, so a stray checkout is seen, never fixed by crew.

### 5. crew's plugin runs live or released, per host

Each host is in one of two modes, set in swancloud's hosts file. **Released**: crew's release Action tags `v<x.y.z>` on every landing on main (`code.10`); swancloud's release adapter captures the tag as a signal; a bump chore pins crew at that version in swancloud's catalog; sluice lands it; the deployer deploys; sessions load the plugin from the nix store, as every other plugin in the catalog. **Live**: swancloud's timer moves `crew/live`, a detached worktree at `origin/main` that is never on a branch, and the shim passes `--plugin-dir crew/live/plugin`, loaded in place; a landing is live on that host minutes later. In both modes main lands on GitHub through sluice and the Action tags it; a live host loads what its folder holds, whatever the tags say (the user: "Leave it tagging"). Every host starts live; released comes once a crew release has been captured and deployed. The box, which runs the held crew on a local branch `box-hold` today, leaves it for released mode pinned at a tag when wldn moves to main. `crew/main` becomes an anchor like any kit's, and CLAUDE.md's "This checkout is live" is rewritten to say so.

### 6. What is sluice's and swancloud's

Sluice: `holds_queued_branch` in the overview, the warning in `status`, `overview` and `protect`, ADR 0024 and core.20 (landed); `remote` read from `origin/bolt/<b>` and the refusal of a submission to a bolt GitHub lacks (landed, #15, its message to name `sluice branch create`); `branch create` and `branch delete`, with the statement's clause 45 amended for a push expected absent and a delete. Swancloud: `space-clone` making the anchor detached; the `swancloud-views` timer on every host; views; its own bolts on GitHub and the publisher no longer pushing `bolt/*`; the app-only `bolt/*` rulesets, set per repository by the user; the sluice bump on the fleet; `crew/live`, the per-host mode, crew in the release sources and the catalog. Nothing of these is crew's to build; crew's change names each in its Touches and orders its parts after them.

### Consequences

- One change in crew, `no-worktree-holds-main-or-a-bolt-branch`, in seven parts with their order in its design: legacy bolt folders detached; the landing folder and the levelling step, the unit refusal; every "main now" read from `origin/main`, the briefs losing `read-tree` and the push, `plan.8`'s refusal, the card's close, blueprints from a branch; the overview read; `crew status` naming a stray checkout; bolts on GitHub through sluice's create and delete; the plugin's modes in CLAUDE.md.
- `state.3`, `plan.8`, `plan.9` and `plan.16` amended, `plan.18` and `plan.19` added, each proposed with this record.
- A crew behind this design keeps working on a host whose anchor is still on the branch: the levelling step is conditional, and nothing of the new reads needs the timer.

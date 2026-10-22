# Design

## Context

This is part 7 of `no-worktree-holds-main-or-a-bolt-branch` (its tasks 7.1, its design's Decision 7), built as a unit of its own. It rests on `plan.18` (no worktree of crew's holds main, every kit's main folder is a detached anchor the timer moves), `plan.19` (crew's plugin reaches a host live or released, never from a checkout on the branch), `state.3` as amended by record 0032 (main moves only through sluice, a record's or the user's branch is cut from `origin/main`, nothing levels a checkout), `code.10` (crew's release tags), `teams.19` (a standing agent is due a restart when what it loaded changes), `docs.1` (the how-to is CLAUDE.md's), `tests.6` (a brief's rule is pinned in `t-briefs.sh`) and `tests.10` (a test's inputs). It touches the areas of `docs.md` (CLAUDE.md) and `tests.md` (`tests/`).

Main as it stands, read 2026-10-22 at 222d8206:

- CLAUDE.md's *This checkout is live* says sessions load crew from `crew/main`, a commit there is live at once, a host gets crew by `git pull`, and the main checkout is levelled with `read-tree` after a submission.
- *Proving and landing a bolt* says ops "pushes main and brings every host's checkout up to it", and its *After landing* bullet gives the box's `fetch` and `merge --ff-only origin/main`.
- `plugin/roles/main-ops.md` already says "you push nothing, and pull and level no host's checkout", and has no crew-specific step; `t-briefs.sh` already pins that, and that main-ops lacks `/workspace/crew/main` (part 4, task 4.3).
- No brief or skill names `read-tree`, `ff-only`, `/workspace/crew/main` or `crew/main/plugin`.

## Goals / Non-Goals

**Goals:** CLAUDE.md says how crew reaches a host as record 0032 decided it, and no longer gives a step that pulls, fast-forwards or levels crew's checkout; a test fails if those words come back, in CLAUDE.md or in any brief.

**Non-Goals:**

- `crew/live`, the per-host mode, the shim's `--plugin-dir`, the timer and the catalog pin. These are swancloud's (record 0032 §6).
- `openspec/config.yaml`'s context line "swancloud loads the plugin from this checkout". It is the project context every change reads, not the how-to, and is named for the planner.
- The specs' wording "the crew checkout that host's sessions keep" (`bolt-teams`) and "crew's checkout" (`host-holds-and-updates`). Both still read true of a live host.
- README, `plugin/skills/crew/SKILL.md` and `crew`'s usage. No command's behaviour changes, so `docs.2` asks nothing of them.

## Decisions

### 1. CLAUDE.md names the modes and the anchor, not the hosts' modes

The section says what each mode loads from and when a landing reaches a host in it. It does not say which host is in which mode, because swancloud's hosts file sets that and it changes without a crew landing (record 0032 §5: every host starts live, and the box moves to released when wldn moves to main). It keeps the two anchor paths an agent meets, mac-studio's `~/Code/github_afterthought/crew/main` and the box's `/workspace/crew/main`, so an agent knows which folder is the anchor. *Considered:* naming each host's mode, which would be stale at the next swancloud deploy.

### 2. Checks are phrases, in the tests that already read the files

`t-docs.sh` already reads CLAUDE.md, and `t-briefs.sh` already reads `plugin/roles/`. Each gains `has`/`lacks` lines and no new `# Reads:`, so `tests/moon.yml` is unchanged (`tests.10`). The brief check renders every brief, as the "no brief prompts another agent through herdr" check does. A grep of the role files would miss a phrase a `{{TOKEN}}` fills in. *Considered:* a new test file, which would add a moon task for a dozen phrases.

### 3. The restart line follows the modes

*A standing agent loads its brief and crew's plugin when it starts* stays (`teams.19`). "A landing that changes them" becomes a change reaching the host: by the timer moving `crew/live` on a live host, or by swancloud's deploy of a new pin on a released one. A landing alone no longer reaches a released host.

## Task notes

**1.1** Replace the heading `## This checkout is live` and its paragraph with `## How crew reaches a host`, saying in this order:

- On every host, crew's `crew/main` is an anchor: detached at GitHub's main, moved only by swancloud's timer, never worked in, committed in or put on a branch, by an agent, crew or the user (`plan.18`). Keep mac-studio's and the box's paths.
- A host loads crew, the `crew` command and the plugin every Claude session loads, in one of two modes swancloud sets per host (`plan.19`, record 0032):
  - **live**: from `crew/live/plugin`, where `crew/live` is a detached worktree beside `crew/main` at GitHub's main that the same timer moves, so a landing is live there minutes after it lands;
  - **released**: at the version swancloud pins from crew's release tags (`code.10`), so a landing reaches the host only once swancloud's bump to that tag is deployed.
- No host loads crew from a checkout on branch `main`.
- So work is built in a worktree of its own, cut from `origin/main`, and a bolt lands only on the user's word, through sluice.
- `main` moves only through sluice (`state.3`). A commit of anyone's, the user's own and the design agent's records among them, is made on a branch cut from `origin/main` in a worktree of its own, and submitted with `wt submit main` from there. Nothing levels a checkout after: the timer moves every anchor.

Drop "live at once", "by `git pull`, not a deploy" and the `read-tree` sentence.

**1.2** In *Proving and landing a bolt*:

- The **Landing** bullet becomes: ops submits the bolt with `crew bolt submit <bolt>`, which sluice lands on GitHub's main, then closes it with `crew bolt land <bolt>`; nobody pushes main, pulls or levels a host for it. Keep the sentence on a conflicting landing.
- The **After landing** bullet goes whole.
- The restart bullet reads as Decision 3 has it, keeping `teams.19` and the band's line.

**1.3** In `tests/t-docs.sh`, after the "devenv shell --" check, hold CLAUDE.md to:

- having `## How crew reaches a host`, `crew/live/plugin`, `release tags` and `cut from \`origin/main\``;
- lacking `This checkout is live`, `read-tree`, `merge --ff-only`, `git pull` and `brings every host's checkout up`.

Add an `ok` line and extend the opening comment's sentence to name it (`plan.19`). Keep the `# Reads:` line.

**2.1** In `tests/t-briefs.sh`, beside the herdr-prompt check, render every team brief for `swb-1` and every main-level brief for `wldn`. Hold each to lacking `/workspace/crew/main`, `crew/main/plugin`, `merge --ff-only` and `read-tree`, then add an `ok` line: no brief pulls, fast-forwards or levels crew's checkout (`plan.18`, `plan.19`, `tests.6`).

## Risks / Trade-offs

- [Swancloud has not built `crew/live` or the mode yet. Read 2026-10-22 at swancloud 2c70bad3, its shim still loads `<space>/crew/main/plugin` (`lib/claude-account-tools.nix`, `crewPlugin`), and no swancloud branch names `crew/live`.] → Until swancloud's part lands, CLAUDE.md describes the target and not a host as it runs. The source change orders part 7 after swancloud's `crew/live` and mode. The conductor holds this unit's landing until then, or lands it knowingly.
- [An agent that needs a landing at once on a live host waits minutes for the timer.] → It reads `origin/main`, as `plan.18` has every read of main now do.

## After deploy

None. The change is words and the checks on them; a host's mode and folder are swancloud's doctor's to show.

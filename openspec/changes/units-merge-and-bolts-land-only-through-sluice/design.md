# Design

## Context

Before this change a unit's, chore's or fix's merge stage ran `wt merge bolt/<bolt> --no-squash --no-remove` in its place, or `wt submit bolt/<bolt>` where a kit set `sluice = true` in `.config/crew.toml` (`gather.sluice`); a bolt had a worktree at `<kit>/bolts/<bolt>`, where its conductor and ops started; main-level ops landed it with `wt merge main` from that worktree, and a landing whose rebase conflicted came back as a fix that replayed the bolt onto main, which crew judged and moved the bolt's branch to (`carry`, record 0015). crew's own `.config/wt.toml` gated every merge with `tests/suite --gate` and verified each bolt after a merge with `bolt-verify.sh`, read with `bolt-status.sh`.

What sluice does, read from its main at d5f8aa4 to d7fdc39 on 2026-10-13: `sluice submit [--worktree <dir>] <BRANCH>` submits a worktree's HEAD and refuses a detached one (`crates/sluice/src/profiles/worktrunk/mod.rs`); `wt submit` is `wt-submit`, which worktrunk runs from the path, exits 0 landed, 1 failed, 2 refused or in conflict, 130 stopped, and removes the worktree on landing unless `--no-remove` (`wt_submit.rs`); it runs no worktrunk hooks; a landing is a merge commit by `sluice <sluice@localhost>`, its target's tip first, with the trailers `Sluice-Submission`, `Sluice-From`, `Sluice-Tested` and `Sluice-Result` (`passed (9 run, 0 replayed)` on its own landings #4 to #10); its protection hook refuses every move of a protected branch but no-ops, creations and deletions with no submission waiting (`crates/sluice/src/protect.rs`), and its policy's default trust is `["confined"]`.

The rules this rests on: `teams.5` (merges only by `wt submit bolt/<bolt>`, no bolt in a kit without a bolt policy, nothing of crew's moves a bolt's branch), `plan.8` (a bolt cut from main as it stands, a landing a submission to main, refused while main is behind GitHub's, a conflict the bolt's), `plan.9` (crew removes only what it made, both bolt shapes), `plan.16` (one landing procedure, main-level ops's), `tests.5` (sluice gates every merge on the kit's policy, its verdict the bolt's verification), `tests.10` (a landing replays nothing), `read.1` (refuse, naming the file), `read.4` (only what crew made), `code.6`, `code.7` (decisions are functions of facts), `teams.9` (shell assignments only on standard output), `docs.3` (open changes that describe this behaviour are rewritten with it), `docs.4`. Pages whose area this touches: `plan.md`, `teams.md`, `tests.md`, `briefs.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- Nothing of crew's merges into a bolt or onto main but a submission sluice tests and lands.
- crew decides from facts: which checks a kit's policy requires of a bolt branch, what a landing's submission came to, a bolt's verification, which bolt branches are crew's.
- A bolt given before this change lands or is dropped in its old shape.

**Non-Goals:**
- Installing sluice on a host, or writing a kit's policy: swancloud's and each kit's.
- Fetching main up to GitHub's under sluice's guard, which refuses the move: a main behind GitHub's stops the landing, and the user decides.
- Running checks crew's way: sluice runs them its way, from the policy on the target branch.

## Decisions

### A bolt is a branch crew marks as its own

`BOLT_BRANCH` makes `bolt/<bolt>` from the kit's main on the team's host and sets `branch.bolt/<bolt>.crew` in the kit's git config; a branch already there is kept. git drops a branch's config section with the branch, so the mark lives exactly as long as the branch, and the tidy deletes, once no plan has the bolt and no worktree is on it, only branches carrying it (`plan.9`, `read.4`). Alternatives: a list file under the git dir (outlives a branch deleted by hand), or reading every `bolt/*` branch as crew's (takes over a branch a person made).

### The give reads the policy from main's commit

`POLICY` prints `git show main:.config/sluice.toml`, base64, on the team's host; `kit.bolt_checks` reads its `[branches."<pattern>"]` tables, takes the most specific pattern matching a bolt's branch as sluice does (`fnmatch`, fewest `*` then longest), and refuses, naming the file, when the kit has none, it is not TOML, or no table names a non-empty `required` list. Read from main's commit, not the checkout's files, since sluice reads a branch's policy from that branch's revision.

### The landing submits from a short-lived worktree

sluice takes a submission only from a worktree on the branch. `LANDING`, run on the team's host by `crew bolt submit`, adds `<kit>/places/land-<bolt>` on `bolt/<bolt>`, runs `wt submit main --no-remove` there with `SLUICE_AGENT` set to whoever asked, removes the worktree, and when main moved brings the main checkout level with `git read-tree -m -u <old> main`, as sluice's own landings are followed, since sluice moves the branch by `update-ref` and not the checkout's files. It prints `RC`, `OLD`, `NEW`, `KEPT` and `LEVEL` as shell assignments (`teams.9`), which `landing_said` reads: landed only when sluice exited 0 and main moved. Before it, `MAIN` fetches and `main_held` refuses a main behind GitHub's (`plan.8`). Alternative: `sluice submit --worktree` from the main checkout (it submits that worktree's HEAD, main itself).

### A conflict is the bolt's, taken by a fix

A landing that conflicts lands nothing and moves nothing. The conductor starts a fix whose words begin "Take main into the bolt"; its agent merges main into the fix's place, resolving each path, and the fix merges into the bolt as any fix, by a submission. The carry, its judgment and crew's move of the bolt go with record 0015.

### Verification is read from the landing commit

`gather` reads each bolt's `Sluice-Result` trailer at its head with `git log -1 --format=%(trailers:key=Sluice-Result,valueonly)`. `kit.verification` reads green only for a value starting `passed`, `none` when the head is no landing of sluice's, `unknown` when there is no head; `crew bolts` shows it and the rail offers a landing only on green (record 0025's half, in `a-bolts-proof-is-its-verification`).

### crew's own policy

`[executor] kind = "open"`, since crew's tests write the host's test slots and moon's archives outside the checkout sluice's sandbox confines writes to; `[branches."bolt/*"]` requires `#check-full` and trusts `open` and `cache`; `[branches.main]` requires `#check-full` and trusts `open` alone, so a landing replays nothing (`tests.10`). sluice's default trust is `confined`, which no executor on one Mac gives, so both tables state it.

### Tests

A stub `wt-submit` lands as sluice was read to land, with no queue and no checks, so the journeys merge, take main into a bolt and land through `wt submit` as agents run it; `tests/run` refuses to run unless it shadows a real one. Fixture kits carry a bolt policy; `on_branch` commits onto a bolt's branch with no checkout for a test's setup.

## Risks / Trade-offs

- [No host has sluice on an agent's path] → no team merges or lands until swancloud installs it; `_open.md` says so.
- [sluice's guard refuses direct commits on main once installed in a kit] → the design agent's records under `state.3` and the user's own commits on main are refused; a question for the user, held in `_open.md`.
- [The last landing by `wt merge main`] → worktrunk reads hooks from the merging worktree, and this branch removes them, so that merge runs no gate: the suite is run by hand first.
- [Open changes that describe the old merge] → `units-build-at-once-and-are-reviewed-in-batches`, `a-kit-declares-its-toolchain-and-tests` and `a-stages-prompt-is-taken-or-sent-again` are rewritten here (`docs.3`); `a-carrying-fix-is-judged-by-its-commits` describes only the carry and is left for the user to remove.

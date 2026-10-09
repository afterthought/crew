# Design

## Context

See proposal.md for why. The decision is record 0015 (`docs/adr/0015-a-bolt-meets-main-at-its-landing-and-a-fix-carries-it-there.md`), as restated on crew's main at 57e9cb8: a fix carries the bolt when its branch sits on a commit the kit's main holds and `git range-diff` pairs each of the bolt's commits beyond its base with exactly one of the fix's, in order, equal or changed, with no commit of the fix's unpaired; otherwise it merges as a fix. `git cherry` stays `plan.10`'s judge of a branch's unmerged patches and is not used here: resolving a conflict changes the resolved commit's patch, so cherry never sees it as the bolt's.

What is built today:

- `crew fix <team> <name> --merge` (`plugin/bin/crew`, the `fix)` case) checks the fix's place with `own_place`, then `run_stage` ends the slot's agent, starts a fresh one and types `Merge fix/<bolt>/<name> into bolt/<bolt>: wt merge bolt/<bolt> --no-squash --no-remove`, recording `fix.merge`. The conductor waits with `crew fix <team> <name> --wait`.
- A fix's merge is delivered when `gather.fix_merged` holds: the bolt holds the fix's tip, and the fix's tip is not the commit it was made at (its reflog's first entry). The next read of the team (`reap`) then frees the slot and removes the place, and the fix's branch goes once it holds nothing beyond the bolt.
- `wt merge` rebases the branch onto its target first; a conflict "stops the merge with the rebase left open in the worktree, to resolve or abort" (worktrunk 0.80.0, `wt merge --help`, step 3). The main-ops brief says that a landing's conflict is resolved on the bolt, by its team, as a fix, and nothing else.
- After every merge into a bolt, worktrunk runs the kit's `[post-merge]` hooks in the target's worktree; crew's own is `.config/hooks/bolt-verify.sh {{ target }}`, the bolt's verification, which ops reads with `bolt-status.sh` for the bolt's head.
- crew moves a branch it made in one place today: `UNREBASE` in `plan.py`, which undoes its own rebase of a unit with `git reset --hard`.

Readings this rests on, taken 2026-10-09 on mac-studio (git 2.54.0, worktrunk 0.80.0):

- `git range-diff --no-color <bolt range> <fix range>` prints one line per commit, `<i>:  <sha> <op> <j>:  <sha> <subject>`, where `op` is `=` (same patch), `!` (paired, changed), `<` (only in the first range, its right side `-:  -------`) or `>` (only in the second). In a scratch repository, a bolt of three commits whose middle one conflicted with main, replayed onto main with the conflict resolved, paired `1 = 1`, `3 = 3`, and printed the resolved commit unpaired (`2 <` and `2 >`) at the default creation factor, pairing it `2 ! 2` from `--creation-factor=100` up. Record 0015's own reading paired its resolved commit `!` at the default. A fix made from the bolt with one commit of its own printed the bolt's three `=` and `4 >`.
- `wt hook post-merge --target=<branch>` renders the hooks with that target (`--dry-run` printed `bolt-verify.sh bolt/x`); post-* hooks run in the background unless `--foreground`. Run without a terminal for a project command not yet approved, it exits 1 having run nothing, printing "Cannot prompt for approval in non-interactive environment" and how to approve; approvals are the same ones `wt merge` uses (`~/.config/worktrunk/approvals.toml`).

Rules this relies on: `plan.8` and `teams.5` (the rules built), `code.6` (its details already allow crew's move of a bolt to a fix that carries it, which discards nothing), `teams.1` (the slot is freed once the fix has merged and its agent stopped), `teams.2` (no stage over a working agent: the fix's agent is ended as a merge stage would end it), `teams.3` (the fix's own place and branch), `teams.9` (what bash evals is quoted assignments, everything else on standard error), `read.1` (what crew cannot read is named and nothing moves), `read.2` (range-diff's output is read by the format read above, and a line that doesn't match it is a refusal), `read.4` (crew moves only the bolt's branch it made, in the bolt's worktree it made), `record.1`, `record.3`, `record.6`, `roles.2` (the move is a step of the conductor's fix merge, not a landing; the landing still waits for the user's word), `state.3` (nothing lands on main but through the kit's hooks on the user's word), `code.2`, `code.3` (the command already runs on the team's host), `briefs.1`, `briefs.13`, `tests.4`, `tests.6`, `docs.2`, `docs.5`. Pages whose area this touches: `teams.md` (`plugin/bin/crew`), `plan.md` (`plan.py`), `briefs.md` (the roles), `tests.md` (`tests/`), `docs.md` (README, the skill, `docs/architecture/`).

Departures, each named:

- `briefs.2` says a fix's coder touches nothing under `openspec/`. A carrying fix replays the bolt's own commits, and a conflict it resolves may sit under `openspec/` (an archived change, a spec a unit synced). The coder brief lets a carrying fix resolve a conflict in any file the conflict names, and still add nothing of its own. Record 0015 asks for exactly this resolution; `briefs.2`'s details should say so when the design agent next amends it.
- The judgment adds one condition the records leave implicit: the bolt's head is not an ancestor of the fix. A fix made from the bolt and never replayed has nothing beyond the bolt's commits, and pairs every one of them `=`; read by the pairing alone it would "carry" the bolt to where it already is. It goes the ordinary way instead.

## Goals / Non-Goals

**Goals:**
- A bolt whose landing conflicts reaches main through its team's fix and crew's move, with no hand move of a branch.
- The move is checked the way a merge is (the kit's post-merge hooks), and the bolt is proven again before the user is asked to land it.

**Non-Goals:**
- Rebasing a bolt before its landing. A bolt meets main only at its landing (`plan.8`); there is no `crew bolt rebase` (record 0015, option 3).
- A gate before the move. A merge's `[pre-merge]` suite gate runs before the target moves; the move has none, as the record decides: the bolt's checks run after it, ops proves it again, and the landing's own gate runs the suite on the tree that lands.
- Sluice kits (`wt submit`). Their verdict replaces the merge hooks' gate for a merge; a carry is not a merge, and its checks are the kit's post-merge hooks either way.
- Changing the creation factor `git range-diff` pairs with. See Risks.
- Rewording the unit's intent ("every patch"), which is the planner's.

## Decisions

### crew judges the fix before it starts a merge stage

`crew fix <team> <name> --merge` keeps its `own_place` check, then runs one new Python subcommand on the team's host, `plan _carry <team> <fix branch> <bolt>`, before anything else. It prints shell assignments (`teams.9`): `CARRIES=yes` with the bolt's head and the fix's head, or `CARRIES=no` with a one-line reason on standard error, or it refuses. Bash then either carries (below) or goes on to `run_stage` exactly as today, so an ordinary fix's merge is unchanged.

The judgment, read in the kit's main checkout:

1. `bolt/<bolt>` and the fix branch resolve, and the kit has a local `main`; otherwise refuse, naming what is missing (`read.1`).
2. `git merge-base --is-ancestor bolt/<bolt> <fix>`: the bolt's head is an ancestor of the fix → `no` ("it holds the bolt's head: it merges as a fix").
3. `git range-diff --no-color main..bolt/<bolt> main..<fix>`. Each line must match the format read above; one that doesn't is a refusal that quotes it (`read.2`). An empty range on either side → `no`.
4. It carries when every line is `=` or `!` and the i-th line pairs the bolt's i-th commit with the fix's i-th. Otherwise `no`, naming the bolt's commits that found no pair, the fix's own commits that paired with none, or "its commits pair out of order", by short sha and subject.

`main..<branch>` is "the commits beyond the commit of main it sits on": for the bolt, its commits since its base; for the fix, the commits it replayed onto whichever commit of main it was rebased on, which need not be main's tip, since the landing rebases again (the design agent, confirming record 0015).

*Alternatives:* `git cherry` (record 0015 as restated: it never pairs a resolved commit); comparing commit subjects (a unit's two commits can share a subject, and it says nothing about content); a separate `crew fix --carry` the conductor chooses (the conductor would have to judge what crew can read, and a wrong choice either moves the bolt to a fix that adds work or replays main over the bolt).

### crew moves the bolt in the bolt's worktree, after ending the fix's agent

When the fix carries the bolt, bash:

1. ends the slot's agent with `stop`, as `run_stage` does, which records the fix stage's owed end; a working agent refuses it without `--force`, and nothing has moved (`teams.2`);
2. runs `plan _carry <team> <fix> <bolt> --move <bolt head> <fix head>`, which, in `<kit>/bolts/<bolt>`:
   - refuses unless that worktree exists and is on `bolt/<bolt>`, `git status --porcelain` is empty (files git ignores don't count, as for `plan.9`), and no rebase, merge or cherry-pick is in progress (`rebase-merge`, `rebase-apply`, `MERGE_HEAD`, `CHERRY_PICK_HEAD` under its git dir), naming which;
   - refuses unless `bolt/<bolt>` is still at the head the judgment read, and the fix still at its head, so a merge or commit in between is never overwritten;
   - runs `git reset --keep <fix head>` there. `--keep` refuses to touch a file with local changes, a second guard behind the clean check; the old head stays in the branch's reflog and in the run record;
3. runs the kit's post-merge hooks there (next decision);
4. records `fix.carry` and prints what happened;
5. runs `reap`, which finds the fix merged (`gather.fix_merged`: the bolt holds the fix's tip, which moved when the agent rebased), frees the slot and removes the place, as after a merge.

Each refusal is said on standard error and recorded as `fix.carry` with crew's message in `Refused`, through `fix_refused`.

*Alternatives:* `git update-ref` with the old value (atomic, but leaves the bolt's worktree's files at the old tree under a moved branch); `git checkout -B` (the same move with no guard on local changes); doing the move as a stage the fix's agent runs (`plan.8` and `code.6`: no agent moves a bolt's branch).

### The bolt's checks are the kit's post-merge hooks, run by crew

`wt -C <kit>/bolts/<bolt> hook post-merge --target=bolt/<bolt>`, with standard input closed and no `--yes` (`teams.5` rules out `--yes`). It runs whatever the kit's `.config/wt.toml` puts under `[post-merge]`, in the bolt's worktree, in the background, exactly as after `wt merge bolt/<bolt>`; in crew that is `bolt-verify.sh bolt/<bolt>`, so `bolt-status.sh` then reads the new head. A kit with no post-merge hooks runs nothing, as after its merges.

When `wt hook` exits non-zero (the hooks are not approved on this host, or the kit's config can't be read), the move stands: crew says the checks did not start, with worktrunk's own words, and that ops should run the bolt's verification again (`ops.md` already says how, and to ask the user when the kit refuses it). The entry still records the move; it is not a refusal.

*Alternative:* crew runs `bolt-verify.sh` itself. That is crew's own kit's hook; another kit's checks are whatever its `[post-merge]` says.

### What `--merge` prints and records

Carried:

```
bolt/<bolt> moved from <old7> to <new7>: fix/<bolt>/<name> carries the bolt's <n> commits onto main (<k> changed by the resolution)
the bolt's checks are running on <new7>; prove the bolt again before it lands
```

with the second line replaced by `the bolt's checks did not start: <worktrunk's words>; ask ops to run the bolt's verification again, then prove the bolt again before it lands` when `wt hook` failed, and by `the kit has no post-merge hooks, so no checks run on <new7>; prove the bolt again before it lands` when the kit has none (worktrunk exits 0 and prints `No post-merge hooks configured`).

Not carried, on standard error before the usual `<slot> has <fix>: merge, in <path>`:

```
fix/<bolt>/<name> does not carry the bolt onto main (<reason>): merging it as a fix
```

The entry: act `fix.carry`, `On: fix/<bolt>/<name>` and `bolt/<bolt>`, `From: agent/<slot's agent>`, `Why: fix(<name>): moved bolt/<bolt> from <old7> to <new7>` (`record.3`: names and commits only; `record.6`: the fix by its own name). No commit is written, so the entry carries none.

### The briefs

- **main-ops**, step 3: when the rebase conflicts, read the commit it stopped at and the conflicting files (`git status` in the bolt's worktree), then `git rebase --abort` there so the bolt's branch and main are where they were; nothing lands. Tell the conductor and the user the commit and the files: the team carries the bolt onto main with a fix, proves it again, and the landing comes back on a new card. Step 1's "proven" now includes a proof made after any move of the bolt's head: the conductor's word that the proof is clean is for the bolt's current head.
- **conductor**, *Fixes*: when main-ops says a landing's rebase conflicted, start a fix whose words begin "Carry the bolt onto main" and quote main-ops's commit and files. On `--merge`, crew says whether it moved the bolt or started a merge; after a move there is nothing to wait for. Then have ops read the bolt's verification for the new head, ask for a new proof (`crew prove`), and post the landing card again once that proof is clean. When crew instead merges it as a fix, its reason says what the fix did besides replaying the bolt: run the fix again with those words.
- **coder**, *A fix*: a fix whose words begin "Carry the bolt onto main" replays the bolt onto the kit's main: `git rebase main` on the fix's own branch, resolve each conflict keeping both intents, main's and the bolt's, in whatever file the conflict names; add no commit, drop none, change nothing else; run the tests the resolved files affect; end with the commit that conflicted, how it was resolved, and the branch's head. crew makes the branch the bolt's head when the conductor merges it.
- **ops**, *The bolt's verification*: crew's move of the bolt to a fix that carries it starts one, as a merge does; a proof is of the head it was made on, so a bolt whose head moved is proven again.

Each new rule is pinned in `t-briefs.sh` (`tests.6`).

## Risks / Trade-offs

- [A resolution that changes a small commit a lot is not paired at range-diff's default creation factor] → crew says the fix does not carry the bolt, names the commit that found no pair, and merges it as a fix, which conflicts again and stops; the bolt is left as it was and nothing is lost. Whether to raise the creation factor is the design agent's to decide (named to `swancloud-design` with this change); until then the reading above is the evidence, and the conductor sees the reason before the merge stage starts.
- [Any change of the bolt between the judgment and the move] → the move re-reads both heads and refuses if either moved.
- [The bolt's worktree is where the conductor and ops sit, and a dev server may run there] → the move changes its files as a merge into the bolt does; it refuses only for local changes or an operation in progress, which a merge would also stop on.
- [No suite gate before the move] → the record's choice: the bolt's verification runs right after on the new head, ops proves the bolt again, and the landing's own gate runs the suite on what lands.
- [The bolt's landing is itself behind main] → this change edits the `teams.5` details and `_open.md`, which main's 57e9cb8 did not touch; it leaves the `plan.8` details line and the `teams.5` rule line, which 57e9cb8 rewrote, so that its own landing does not conflict there. The stale "until `a-fix-carries-the-bolt-onto-main` lands" note in `plan.8`'s details is the design agent's to drop on main after this lands.

## Migration Plan

Nothing to migrate: the next `crew fix --merge` judges every fix this way. A fix already merging is unaffected. Rolling back restores the plain merge stage; a bolt crew already moved stays where it is, which is where the user would otherwise have moved it by hand.

## Proof in dev

None. crew has nothing to deploy; its proof before landing is the suite on the bolt.

## Proof on real work

Once the bolt has landed and every host has pulled, with the standing agents started fresh:

- The next crew bolt whose landing conflicts goes through it: main-ops aborts and tells the conductor the commit and files; the conductor starts a "Carry the bolt onto main" fix; its agent rebases onto main; `crew fix <team> <name> --merge` prints the move; `sh .config/hooks/bolt-status.sh` in the bolt's worktree shows a run for the new head; ops proves it; the landing card comes back; the landing's rebase replays nothing that conflicts and lands.
- On that first carry, read whether range-diff paired the resolved commit at the default creation factor, and give the reading to `swancloud-design`.

## Task notes

### 1.1

In `plan.py`, a `_carry` subcommand (`_carry <team> <fix> <bolt>`, and `--move <bolt head> <fix head>`), registered with the other private subcommands; it runs on the team's host (bash has already forwarded), in the kit's main checkout for the judgment and in `<kit>/bolts/<bolt>` for the move. The judgment is a pure function over range-diff's text and the two heads, so `t-fix.sh` can reach every branch of it through crew; parse each line with one regular expression for the format in *Context* (`^\s*(\d+|-):\s+([0-9a-f]+|-+)\s+([=!<>])\s+(\d+|-):\s+([0-9a-f]+|-+)\s?(.*)$`) and refuse on any line it does not match. Output for bash: `CARRIES`, `OLD`, `NEW`, `CHANGED` (how many `!`) through `sh()`, as `_run` prints its assignments. A refusal goes through `fail()` (`code.2`).

### 1.2

In `plugin/bin/crew`'s `fix)` case, `--merge` branch: after `own_place`, `e=$(plan _carry "$TEAM" "$fix" "$BOLT")` (refused → `fix_refused fix.carry "$err"`), `eval "$e"`; when `CARRIES=yes`: `stop "$slot"` (a refusal → `fix_refused fix.carry`), then the move, then `wt -C "$KIT_DIR/bolts/$BOLT" hook post-merge --target="bolt/$BOLT" </dev/null`, capturing its output for the message, then the `fix.carry` entry and the two lines in *What `--merge` prints and records*, then `reap`. When `CARRIES=no`, `run_stage` as today. The usage header's `--merge` line says it merges the fix into the bolt or, when the fix carries the bolt onto main, makes it the bolt's head (`docs.2`).

### 1.3

`tests/t-fix.sh` gains, in its own world section: a bolt with three commits, the middle one editing a line that a new commit on the kit's `main` also edits; a fix started on it, whose place the test rebases onto `main` by hand, resolving the conflict, as the agent would (commit with a fixed committer date after the stage's start, so the fix stage reads delivered). Give the kit a `[post-merge]` hook in its `.config/wt.toml` that writes `{{ target }}` and the head to a file, approved in the simulated host's home with `wt config approvals add --yes` run in the kit. Cases:
- `crew fix … --merge` moves `bolt/<bolt>` to the fix's head; the bolt's worktree is at it and clean; the output has both lines; the hook's file names `bolt/<bolt>` and the new head; the entry is `fix.carry` with the `Why` above; no merge prompt was typed; the slot is freed and the place removed by the next `crew status`.
- The same with the hook not approved (a fresh home): the bolt moves and the output says the checks did not start, quoting worktrunk.
- A fix that adds a commit of its own after rebasing, and one that drops one of the bolt's commits: no move, the reason on standard error names the commit, and the usual merge prompt is typed.
- A fix never rebased (still on the bolt's head): no move, "it holds the bolt's head", merge prompt typed (the existing merge cases keep passing).
- The bolt's worktree with an untracked file, and with a rebase in progress: refused, named, recorded as `fix.carry` with `Refused`, the bolt not moved, no merge prompt typed.
Verify `tests/suite t-fix` ends with "0 failed". If the test now reads a file beyond what its tasks list, add it on its `# Reads:` line and run `tests/moon-tasks`.

### 2.1

The four briefs as *The briefs* says, in the briefs' own plain English and without section numbers. main-ops's step 3 keeps "a conflict is resolved on the bolt, by its team, as a fix" and gains the abort, the commit and files, and what comes back. Pin in `t-briefs.sh`: main-ops "git rebase --abort", conductor "Carry the bolt onto main" and "prove the bolt again", coder "git rebase main" and "add no commit", ops a phrase saying the move starts a verification. Verify `tests/suite t-briefs` ends with "0 failed".

### 2.2

README's Teams paragraph on fixes (the one that says "A **fix** is built the same way on `fix/<bolt>/<name>`"): one or two sentences that a fix which replays the bolt's commits onto main becomes the bolt's head by crew's move on `--merge`, the bolt's checks run on it, and it is proven again before it lands; and, where README describes landing, that a landing whose rebase conflicts lands nothing and goes back to the team as such a fix. The crew skill's sentence listing what a stage delivers names "merge's commit on the bolt, or crew's move of the bolt to a fix that carries it". Verify `tests/suite t-docs` ends with "0 failed".

### 2.3

`docs/architecture/teams.md`, `teams.5`'s details: replace "A fix that carries a rebase is never merged as a fix: ADR 0015. Not built: `_open.md`." with its sources, ADR 0015 as restated 2026-10-09, `plan.py` `_carry`, `plugin/bin/crew` `fix`, `tests/t-fix.sh`; keep the `concurrent-units` sentence. `docs/architecture/_open.md`: remove the `plan.8`, `teams.5` line. Leave the `teams.5` rule line and everything in `plan.md` as they are (see Risks). Verify `tests/suite --affected` ends with "0 failed".

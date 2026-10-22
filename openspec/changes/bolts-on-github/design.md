# Design

## Context

Part 1 of `no-worktree-holds-main-or-a-bolt-branch` (its tasks 1.1 to 1.5), built to `plan.19` as crew's main has it at dd9fadd4, with record 0032 §2 and its amendment of 2026-10-22 (proposed, on the user's card): a bolt made before stays local until it lands, and no create puts it on GitHub. Parts 2 to 5 are built; part 7 is `how-crew-reaches-a-host`, in this bolt.

Today `bolt_give` writes the plan, then makes `bolt/<bolt>` with git at the commit `kit_policy` read `origin/main`'s policy at (`BOLT_BRANCH`), and marks it `branch.bolt/<bolt>.crew`. `make_place` cuts every place from the local `bolt/<bolt>`, tracking it. `bolt_land` writes the plan and tidies, and the tidy removes the marked branch once no plan has the bolt (`plan.9`). Every merge is `sluice submit bolt/<bolt> --no-wait --json` from the place, and a landing is `wt submit main` from `places/land-<bolt>`.

What sluice does, read in sluice 0.36.4 at its main 2e98fbd (`crates/sluice/src/branch.rs`, `crates/sluice-core/src/branches.rs`, `crates/sluice/src/profiles/branches.rs`, `pushed_refs.rs`, `local_refs.rs`, `told.rs`), unchanged since v0.20.0, the first release with the commands (its commit 69bd844, ADR 0026):

- **Routing.** sluice decides where a branch lives by the policy at the branch's own local revision, or at a remote's tracking ref of it when there is no local branch: the `remote` of the `[branches]` table that matches it. No remote means local refs (its rule core.15).
- **`sluice branch create <branch> --from <from> [--json]`.** `--from` is a branch name sluice lands on, read where its own policy routes it: `--from main` reads GitHub's main for a kit whose main names `origin`. It refuses when the branch is present (on its remote, or locally), when `from` is absent or ungated, or when the policy at `from`'s revision gives the branch no gate. It makes the branch where the policy at that revision routes it: on the remote by a push leased on its being absent, then sets the local branch to the same commit. Success prints `{"branch", "created", "from"}` and exits 0.
- **`sluice branch delete <branch> [--into main] [--json]`.** Refuses while a submission is queued on the branch, a landing on it is unfinished, or its tip is not in `into`. On the remote, a leased delete, then the local branch and the tracking ref go by ref edits, which leave the branch's git config section.
- **Refusals.** With `--json`, `{"error": {"kind", "message", "next"}}` on standard output: exit 2 for `refused`, 1 for `not_found` (`no branch <branch>`), 3 for `internal`.
- **`sluice --version`** prints `sluice 0.36.4`.
- **A landing on a remote branch** pushes it leased and sets the local branch to the landing commit, so the team's host's `bolt/<bolt>` follows every merge sluice lands there.

It relies on `plan.19`, `plan.9`, `plan.17` (crew only reads a kit's policy, never writes `remote` into it), `plan.18` (reads of main now), `state.5` (crew pushes nothing), `read.1`, `read.2` (sluice's output read by facts checked against it), `read.4`, `code.1`, `code.7`, `code.9`, `docs.2`, `docs.3`, `tests.4`, `tests.10`, `tests.11`. It touches the areas of `plan.md`, `tests.md` and `docs.md`.

## Goals / Non-Goals

**Goals:** a new bolt has one copy, on GitHub, written only by sluice; every place holds what landed on the bolt from any host; a give that can't put the bolt on GitHub changes nothing; a bolt made before keeps working, untouched, until it lands.

**Non-Goals:** the `bolt/*` rulesets (the user's, per repository); each kit's own `remote = "origin"` line (crew's is the chore `crews-sluice-policy-names-origin-for-bolts`); deleting a dropped bolt's branch on GitHub, which neither the intent nor `plan.19` names; moving the bolt's stage reads, `ONTO` or `landed_at` off the local branch (Decision 4); any change to `crew bolt submit`.

## Decisions

### 1. Where a bolt lives is read as sluice reads it

A bolt is on GitHub when the policy at its local `bolt/<bolt>`, or at `origin/bolt/<bolt>` when the host has no local branch, names a `remote` for it in the `[branches]` table that matches it, most specific first, as `kit.bolt_checks` matches. Otherwise it is a bolt made before, on its host only. This is sluice's own routing, so crew and sluice never disagree on where a bolt's merges go: a bolt made before stays local until the merge that brings it a policy naming `origin`, which the planner orders last in its bolt (record 0032's amendment), and a new bolt starts at main's commit, whose policy names `origin`. The decision, `kit.bolt_remote(text, bolt)`, is a function of the policy text (`code.7`); the reads print the policy at both refs, base64, as `POLICY` does.

Considered: whether GitHub has `bolt/<bolt>`. Rejected: an older push of the box's stands on GitHub under some legacy bolts' names (record 0032's amendment), and sluice ignores it while the tip names no remote.

### 2. A give checks, creates, then writes

`bolt_give`, after today's refusals (held team, no checks at `origin/main`):

1. Refuses when the policy at `origin/main` names no `remote` for bolt branches (`kit.bolt_remote` on the text `kit_policy` already read), naming the file and the key: `.config/sluice.toml`'s `[branches."bolt/*"]` has no `remote`.
2. Reads `sluice --version` on the team's host and refuses below 0.20.0, naming 0.20.0 and what the host said; output crew can't read as `sluice X.Y.Z` refuses the same way (`read.1`). `kit.sluice_version(out)` and the floor `kit.SLUICE_BRANCHES = (0, 20, 0)`.
3. Runs `sluice branch create bolt/<bolt> --from main --json` in the kit's main checkout on the team's host, and refuses with sluice's `message` on any refusal, the plan unchanged. Sluice's document is read by `kit.branch_said(out, code)` against the shapes above (`read.2`).
4. Marks the local branch sluice set, `git config branch.bolt/<bolt>.crew given`, so the tidy knows it as crew's (`read.4`).
5. Writes the plan. If the write is refused, the team having taken another bolt since, crew deletes the new branch again, `sluice branch delete bolt/<bolt> --into main`, which sluice allows since its tip is main's, and says so with the refusal.

The create goes before the write so a give that fails at sluice leaves the plan as it was, as the spec has it for every refusal, and a team never holds a bolt with no branch. `BOLT_BRANCH` goes. What the give prints names GitHub, the commit sluice made it at (`created`) and the team's host.

Considered: the write first, then the create, as today's git branch. Rejected: a refused create would leave the team holding a bolt with no branch, and `crew bolt give` refuses a team that holds one, so nothing could make it again.

### 3. A place is cut where its bolt lives

`PLACE` takes the bolt and reads where it lives in the same script (Decision 1's policies), and `make_place` decides the base. For a bolt on GitHub: `git fetch -q origin +refs/heads/bolt/<bolt>:refs/remotes/origin/bolt/<bolt>`, then `git worktree add --track -b <branch> <path> origin/bolt/<bolt>`; a failed fetch, or no `origin/bolt/<bolt>` after it, refuses naming the bolt and git's words, with no place made (`read.1`). For a bolt made before: the local `bolt/<bolt>`, tracking it, as today, with no fetch. A branch that already exists gets its worktree as today. This covers every caller: a unit's construct and its merge's remake, a chore's code, a fix's place.

`REBASE`, which moves a unit or chore to another bolt, sets the branch's upstream the same way: `origin/bolt/<to>` for a bolt on GitHub, `bolt/<to>` for one made before.

### 4. A place's bolt is read from either upstream; the bolt's own reads stay local

A place tracking `origin/bolt/<bolt>` has `%(upstream:short)` `origin/bolt/<bolt>`. Every read of a place's bolt from its upstream, `gather.kit`'s, `tidy_over`'s, the bolt-of read in `plan.py` and `own_place`'s check of a fix's place, takes either form through one function, `gather.bolt_of(up)`, standard library only like the rest of `gather.py`.

The bolt's own reads, its stages in `gather.kit`, `ONTO`, `landed_at`, and the rebase words given to an agent, keep reading the local `bolt/<bolt>`. On the team's host sluice sets that branch at the create and at every merge it lands there, and every merge into a bolt is submitted from that host's places; GitHub's tracking ref, by contrast, may lag a landing pushed as sluice's app until the next fetch. Reading GitHub for these would add a fetch to every team read, which `plan.18` keeps out of the stage reads. Only the cut fetches, so a place is never behind what landed.

### 5. A land deletes the bolt on GitHub

`bolt_land`, after its plan write and before `tidy_after`, runs `sluice branch delete bolt/<bolt> --into main --json` in the kit's main checkout on the team's host. Deleted: said with the commit. Refused: the bolt has still left the plan, and crew prints sluice's `message`, naming the branch kept on GitHub. `not_found` (the branch already gone) is said as gone and refuses nothing. For a bolt made before, sluice routes by its tip: once the bolt's last merge brought a policy naming `origin`, and its landing's pull request pushed the branch, the delete ends it on GitHub; otherwise sluice deletes the local branch. A host that does not answer is named, as `tidied` names one.

The tidy keeps `plan.9`'s handling of the local branch. Since sluice's delete removes the local ref but not its git config section, the tidy unsets a `branch.bolt/<bolt>.crew` mark whose branch is gone, saying nothing, instead of trying to remove a branch that is not there on every read.

### 6. A bolt made before is said once a read

At the end of a team's read (`rebase_and_tidy`), for each bolt the team holds that Decision 1 finds on its host only while the policy at the kit's main now (`gather.now_ref`, as last fetched, no fetch, `plan.18`) names a `remote` for bolt branches, crew prints one line: "bolt/<bolt> is local until it lands: it was made before bolts were on GitHub, so its places are cut from the local branch, and its landing puts it on GitHub". Nothing is run. While main's policy names no remote, nothing is said, every bolt being local. The decision is `bolt_local_said(bolt, lives, main_remote)`, pure.

### 7. The test kits stand on a bare remote, and the stubs route as sluice does

`tests/lib.sh` `kit()` gives each scratch kit an `origin`, a bare repository under the test's remotes, pushes its main there, and writes a policy naming `remote = "origin"` under both `[branches."bolt/*"]` and `[branches.main]`. Main is named too because sluice's `--from main` requires main to be a branch sluice lands on, and part 4 already reads a kit with an origin at `origin/main`, which only stays current if landings on main go there. A kit already standing on its remote, made again on a second host of one test, is cloned from it rather than started anew.

`tests/stubs/sluice` answers `--version` (`sluice 0.36.4`, or what `$CREW_TEST_ROOT/sluice-version` holds, for the refusal's journey), `branch create` and `branch delete` with sluice's documents, exits and refusals, routing each by the policy as Decision 1 says. `tests/stubs/wt-submit`, which the stub `sluice submit` runs too, lands on the remote when the target's policy names one: it fetches the target, forms the merge on the remote's tip, pushes leased on it and sets the local branch, as sluice's pushed refs do. Both stubs' headers say which sluice they follow (`tests.4`).

### 8. The parent change says the same

`no-worktree-holds-main-or-a-bolt-branch` stays open for part 6 and archives after this change, so its deltas would otherwise put back what this change replaces. Its part 1 tasks are ticked as built here; its 1.4, its Decision 6's sentence on a bolt made before, and its `bolt-plan` and `bolt-teams` blocks for the two requirements this change modifies are made to read as this change's (`docs.3`). Its `--from origin/main` becomes `--from main`, which is sluice's argument.

## Task notes

**1.1** `kit.bolt_remote(text, branch)`: parse with `tomllib`, match as `bolt_checks` does, return the table's `remote` when it is a non-empty string, else None; text None (no policy) is None. The give's refusal: "<kit> gives bolts only on GitHub, and its .config/sluice.toml on origin/main names no remote for its bolt branches: its [branches.\"bolt/*\"] needs `remote = \"origin\"`, which is the kit's own change (plan.17), then give the bolt again". Logic cases in `tests/py/test_kit.py`; contract case in `tests/contract/test_kit.py` reading the remote from a real `git show` of a committed policy.

**1.2** `kit.sluice_version(out)` returns the version tuple or None; the refusal names "sluice 0.20.0 or later, which has `branch create`" and the host's words. `kit.branch_said(out, code)` returns (commit, None) or (None, message) and refuses on anything that is not sluice's document (`read.2`). Record the documents the tests read by running sluice 0.36.4 for real in a scratch repository with a bare remote (a create, a create refused as present, a delete, a delete refused as queued if it can be made, else as not landed, and a `not_found`), and keep them in `tests/py/sluice-0.36.4/` beside `tests/py/sluice-0.18.0/`, each with the command that made it.

**1.3** In `test_bolt_commands.py`: the remote refusal, the version refusals (old, unreadable), sluice's refusal passed through, the create's success naming GitHub and the commit, and a write refused after the create deleting the branch again; each with the plan unchanged where the spec says so. `BOLT_BRANCH` goes, and every test that read it moves to the create.

**1.4** `PLACE` and `REBASE` as Decision 3. In `tests/contract/test_git.py`, against a bare remote whose `bolt/b` is ahead of the local branch: `PLACE` cuts `unit/x` from `origin/bolt/b`, its upstream `origin/bolt/b`, holding the remote's commit; and a bolt whose tip's policy names no remote is cut from the local branch with no fetch.

**1.5** `gather.bolt_of("origin/bolt/b") == gather.bolt_of("bolt/b") == "b"`, anything else None. Logic cases in `tests/py/test_tidy.py` (a place tracking `origin/bolt/b` is a place of bolt `b`, merged and over as today) and in `tests/py/test_stages.py` or wherever `gather.kit`'s place reading is pinned.

**1.6** The fixture and stubs as Decision 7. Then `t-journey-teams.sh` holds a give on GitHub (the branch on the kit's bare remote at main's commit, the local branch marked), the remote refusal and the version refusal; `t-journey-units.sh` holds a place cut from `origin/bolt/<bolt>` after a merge pushed to the remote from another clone. Every other `t-journey-*.sh` passes on the new fixture as it is, its expectations moved only where a branch is now on the remote.

**2.1** The delete's words, deleted and refused, in `tests/py/test_landing.py` "The bolt's branch is deleted at its land" and "A delete sluice refuses"; a mark whose branch is gone unset with nothing said, in `test_tidy.py`; `t-journey-land.sh` holds the branch gone from the bare remote after `crew bolt land`, and a refused delete's words. A bolt made before, in `t-journey-land.sh`: made with git on the kit's host, its last merge bringing the policy naming `origin`, landed through the stub `wt submit main` with the branch pushed to the bare remote as sluice's pull request pushes it; `crew bolt land` has the stub delete it there, and no `branch create` is in the stub's log.

**3.1** `bolt_local_said` cases in `test_tidy.py`: a local bolt while main names a remote says the line once; a bolt on GitHub says nothing; a local bolt while main names none says nothing. `t-journey-teams.sh` holds a bolt made with git before the give went through sluice, on a kit whose main then names `origin`: the read says the line, no `branch create` is in the stub's log, and a unit's place is cut from the local branch.

**4.1** README's bolt commands, `plugin/skills/crew/SKILL.md` and `crew`'s usage header: a give has sluice make the bolt on GitHub from main and is refused without the policy's remote or sluice 0.20.0; a land has sluice delete it. `tests/t-docs.sh` pins the words.

**5.1** As Decision 8. `openspec validate no-worktree-holds-main-or-a-bolt-branch` and `openspec validate bolts-on-github` pass.

**6.1** `tests/moon-tasks`, then commit `tests/moon.yml`; then `tests/suite --affected` once.

## Risks / Trade-offs

- [Sluice chooses which main to read by the policy on the host's own `main`, which may lag GitHub's] → crew's main has named `origin` for main since swancloud ADR 0027, so a lagging `main` there still routes to GitHub; a kit whose local `main` predates that would have its bolt made locally, which Decision 6's line then names on the first read.
- [A dropped bolt's branch stays on GitHub] → sluice refuses to delete a branch whose tip is not in main, and nothing in `plan.19` deletes it; named for the planner.
- [A bolt made before whose last merge brought `origin` and which then needs a fix finds no branch on GitHub] → the planner orders the policy chore last and the bolt lands next (record 0032's amendment); a place cut then is refused naming the fetch, not made from a stale branch.
- [Two hosts' queues for one bolt] → accepted until sluice shares its records (`plan.19`).

## After deploy

Steps no check in crew's tiers can prove, since each needs GitHub, sluice's app and a live kit, all in crew's own repository on mac-studio (`docs.6`):

1. The first give on a kit whose policy on GitHub's main names `origin` for its bolts: `bolt/<bolt>` appears on GitHub, pushed by sluice's app, and the first unit's place is cut from it. Doer: the team's ops, once the bolt lands and the kit's policy chore is on main, on the first `crew bolt give` after.
2. That bolt's land: the branch is gone from GitHub, or sluice's refusal is named. Doer: main-level ops, at that bolt's landing, reading GitHub's branch list.
3. This bolt's own landing, crw-4's being a bolt made before: its last merge is the chore that puts `remote = "origin"` on crew's bolt policy, its landing's pull request pushes `bolt/<bolt>` to GitHub as sluice's app, and `crew bolt land` deletes it there. Doer: main-level ops, at the landing, reading GitHub's branch list.
4. The user sets each kit's `bolt/*` ruleset naming sluice's app as its one writer for create, update and delete, before the first give on that kit.

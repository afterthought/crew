# Design

## Context

See proposal.md, Why. The rules this rests on: `plan.19` and its reading of 2026-10-23 ~04:40Z (a bolt on GitHub is read at `refs/remotes/origin/bolt/<bolt>` after a fetch, as main is read; the host's copy is sluice's alone), `plan.18` (how main is read: the survey at `origin/main` as last fetched, a decision of the moment fetching once per command), `read.1` (refuse and name, never fall back), `read.2`, `code.1` (gather.py standard library only), `code.7` (a decision is a function of facts), `state.4`. sluice's statement, agentplot/blueprints dcb59c8 `design/sluice/requirements.md` clause 124 and S58: on a branch whose policy names a remote, the remote's revision is the branch; the host's ref is sluice's copy, levelled at each landing it reads and read by nothing. Pages whose areas this touches: `plan.md` (`gather.py`, `plan.py`, `kit.py`) and `tests.md` (`tests/`). `code.8` is not touched: no field the agents' views draw changes.

What the code does today, on main at 433e1771:

- `gather.kit` lists the host's `refs/heads/bolt/*` and reads each bolt's `exists`, `changes`, `archived`, `open`, `chores`, `head`, `head_at` and `verdict` at `refs/heads/bolt/<b>`. `chore_place` counts a chore's commits beyond `refs/heads/bolt/<b>`, `own_head` reads beyond it, and `fix_merged` falls back to it when the fix tracks no ref naming the bolt.
- `plan.py` reads the host's ref directly in `deliverable_facts` (a merge stage's "the bolt holds it", its head), `land_facts` (the landing card's merge-base with main), `chore_commits`, `undeclared`, `change_words`, `forecast_words`, `rebase_words`, the `ONTO` and `TAKE` scripts, and `landed_at`.
- How sluice 0.36.4 moves things on the host, read in sluice v0.36.4 `crates/sluice/src/profiles/pushed_refs.rs`: every read of the branch fetches `+refs/heads/<b>:refs/remotes/<remote>/<b>` (`read` → `fetch`); a landing is a leased push (`move_to` → `leased`) to `target()`, the remote's URL when sluice speaks as its app, so git moves no tracking ref; only then does it set the host's `refs/heads/<b>` (`self.local.set`), and nothing retries that set when it fails. So after a landing on GitHub the host's tracking ref holds the revision before it until something fetches, and the copy may never move.
- `kit.bolt_lives` (for `place_base` and `split_remote`) reads the bolt's route from the policy at the host's copy, or at the tracking ref when the host has no copy. `PLACE` fetches `origin/bolt/<b>` before cutting a place from it.

## Goals / Non-Goals

**Goals:**
- Every read of a bolt's content, head and verdict is at the one ref the bolt is read at, decided once on facts.
- A merge sluice lands on GitHub is seen by the wait on it at its next look, and by `crew bolts`, whatever sluice did to the host's copy.

**Non-Goals:**
- The landing's submission. `LANDING` makes `places/land-<bolt>` on `bolt/<bolt>` and submits that worktree's head, the host's copy; a submission is its worktree's head (clause 124), and moving that head off the copy is a write, not a read. Until sluice levels the copy at each landing it reads, ops levels a lagging copy by hand before a landing (`plan.19`'s reading, ~04:20Z).
- The split guard. `BOLT_SPLIT` and `kit.split_remote` compare the host's tip with GitHub's to refuse a merge into a legacy bolt whose host tip holds merges GitHub lacks (`plan.19`'s reading for crw-6's signal 906b7fc5). They read nothing of the bolt from the copy; they compare the two, which is their purpose, and stay.
- A place's route. `kit.place_base` reads the bolt's route from the copy's policy and then cuts from GitHub's copy after a fetch; every revision of a bolt on GitHub carries the same route, so the route read there is GitHub's, and nothing of the bolt's content is read from the copy.
- The tidy's reads of the host's bolt branches (`unmark_gone`, `bolt_merged`), which are about crew's marks on the host's branch and legacy bolt worktrees, not about the bolt's content.

## Decisions

### 1. One decision, `gather.bolt_at`, of where a bolt is read

`bolt_at(bolt, tracked, local, remote_at_tracked)` → the ref, or `None` when the bolt is missing: `refs/remotes/origin/bolt/<b>` when `tracked` (the host holds it) and `remote_at_tracked` (the remote the policy at it names for `bolt/<b>`) is not None; else `refs/heads/bolt/<b>` when `local`; else `None`. It is a pure function (`code.7`); `bolt_read(main, bolt)` reads its facts with git (two `rev-parse`s and a `git show` of `.config/sluice.toml` at the tracking ref) and calls it, returning `(ref, None)` or `(None, why)` when the policy there is not TOML (`read.1`).

Why GitHub's copy's own policy, not the host's: the policy at the host's copy is what sluice's copy says, and the rule is that nothing is read from it. A legacy bolt that a refused landing's pull request pushed to GitHub before its policy merge (crw-6's #99) has a GitHub copy whose policy names no remote, so it is read at the host's branch, where its later merges are; once its landing's submission pushes the host's tip, GitHub's copy carries the policy and the bolt is read there.

Why the host's branch when the host has no GitHub copy: then the host's branch is the only copy it has. That is a legacy bolt kept local until it lands (`plan.19`, Not ruled out), or a bolt just given and not yet fetched, which Decision 4 closes by having the give fetch.

Alternatives: (a) the tracking ref whenever it exists, with no policy read: reads a legacy bolt's stale pull-request copy and loses its merges. (b) `kit.bolt_lives`'s order (the host copy's policy first): reads the copy. (c) Two reads of every fact, host and GitHub, with plan.py choosing: doubles the git calls of every survey.

The policy matching moves into gather.py: `branch_table(branches, branch)` and `policy_remote(text, branch)` (the remote a policy's matching table names, or None; raises `ValueError` on text that is not TOML), standard library only (`tomllib`, `fnmatch`, both in Python 3.11+, `code.1`). `kit.branch_table` becomes gather's; `kit.bolt_remote` calls `gather.policy_remote` and keeps its own refusal through `crew.fail`. kit.py imports gather, which imports nothing of crew's.

### 2. Every read of a bolt goes through it

`gather.kit` lists bolts as today (the host's `refs/heads/bolt/*`, the bolts asked for, the bolts places track) plus each `refs/remotes/origin/bolt/*` the host holds of a bolt asked for, and for each answers `at` (the short ref, `origin/bolt/<b>` or `bolt/<b>`, or None) and reads every fact there: `exists` is `at is not None`, and `changes`, `archived`, `open`, `chores`, `head`, `head_at`, `verdict` read at `at`. A policy it can't read gives `{"exists": False, "error": why}`, and `Stages.of` and `bolt_state` read `unknown` with that why for every unit and chore of the bolt that has not landed. `chore_place`, `own_head` and `fix_merged` read at `bolt_read(main, bolt)`'s ref.

In plan.py, a read that has the kit as gathered uses `k["bolts"][b]["at"]` (`land_facts`, `change_words`, `forecast_words`, `rebase_words`); one that reads on the host uses `gather.bolt_read` (`deliverable_facts`, `chore_commits`, `undeclared`, `landed_at`). The `ONTO` and `TAKE` scripts take the bolt's ref as an argument in place of building `refs/heads/bolt/$bolt`, their callers passing it. `rebase_words` tells an agent `git fetch origin` before `git rebase origin/bolt/<b>` for a bolt read on GitHub, and `git rebase bolt/<b>` as today otherwise.

### 3. Fetched as main is fetched

`survey(fleet, held, sites, board, fetch=False)` adds `"fetch": true` to its request; `gather.kit` then runs `git fetch -q origin` in the kit's main checkout before it reads, for a kit with an origin, and answers `{"ok": False, "error": "cannot fetch <main> from GitHub: <git's words>"}` when the fetch fails. A survey that fetches is never served from the command's reading (`READ.kits`): it must read after its own fetch; what it reads is kept as any survey's. `stages_for(fleet, plan, bolts, fetch=False)` passes it on.

Who fetches, by `plan.18`'s line between a read that runs on every team read or refresh and a decision of the moment:

- `bolts_view` (`crew bolts`): `survey(..., fetch=True)`. Once per command, one fetch per kit.
- `bolt_give`'s proven check: `stages_for(..., fetch=True)`.
- `deliverable_facts` for a merge stage: `gather.fetched(main)` (a `git fetch -q origin`, `None` or git's words) before `bolt_read`; when it fails the facts carry `"fetch": why` and `delivered` returns `(None, "can't fetch bolt/<b> from GitHub: <why>")`, so the wait looks again at its next look. A wait reads afresh at every look (`bolt-plan`, *A command reads each kit and the plan once*); the merge look fetches only while the stage's agent is not working, which is when `deliverable` is asked, every `POLL` (10 s) at most. What the merge's end reads after delivery in the same command (`landing_after_merge`, `team_freed`, `raise_land`) reads the tracking ref that fetch moved, with no fetch of its own.
- `BOLT_CREATE`: after sluice's create succeeds, `git fetch -q origin "+refs/heads/bolt/$2:refs/remotes/origin/bolt/$2"`, its failure said on standard error and the give going on, since the branch is made; the team's next read, or the first place's `PLACE`, fetches again.
- Everything else, `crew status`, the rail, the board, a stage run, reads as the host last fetched. On the team's host that is current once the merge's wait has fetched; on other hosts the fleet's timer fetches within minutes, as for main.

Alternatives: fetch in every survey, ruled out by `plan.18` for main for its cost on every thirty-second refresh; fetch only `bolt/<b>` by an explicit refspec, which fails the whole fetch when GitHub has no such branch, where `git fetch -q origin` is what `MAINS` and `landing_opened` already run.

### 4. The stubs can leave the copy behind

`tests/stubs/wt-submit` today pushes a bolt's landing to its remote by name, which moves the tracking ref, and then sets the host's branch, a sluice that levels. With `$CREW_TEST_ROOT/sluice-leaves-copy` present, it pushes to the remote's URL (`git remote get-url`) as sluice does under its app's identity, so git moves no tracking ref, and does not set the host's branch: sluice 0.36.4 as deneb ran it. `tests/stubs/sluice`'s comment and its own landing path, if it lands a bolt, follow the same switch. A journey proves the wait and `crew bolts` see the merge with the switch on.

## Risks / Trade-offs

- [A legacy bolt whose stale GitHub copy already names a remote while the host's tip is ahead of it] → crew would read GitHub's copy and miss the host's merges. Such a bolt arises only from a pull-request push after the policy merge, before the landing's submission; `plan.19`'s reading for batch 27 holds that the split ends at the first landing submission and no legacy bolt can arise again, and the split guard refuses any merge into one meanwhile.
- [A fetch at every merge look] → about one `git fetch` per 10 s per waiting merge while its agent is idle, on the team's host. The same fetch `MAINS` runs; a failure only delays delivery to the next look.
- [A command's later step served a survey that did not fetch] → only a fetching survey bypasses `READ`; a later non-fetching survey in the same command is served the fetched answer, which is newer.
- [`no-worktree-holds-main-or-a-bolt-branch` is open on main and touches the same files] → crew names the overlap at code; this change edits only the reads named here.

## Migration Plan

None beyond landing: the change reads differently and writes nothing. A host whose crew is older keeps reading the host's copy, and ops levels a lagging copy by hand there, on the user's word, until the change reaches it (`plan.19`).

## After deploy

None: every scenario is proved in the logic, contract and end-to-end tiers, and nothing of a live host needs setting.

## Task notes

**1.1** `plugin/lib/gather.py`: add `branch_table` and `policy_remote` as Decision 1 has them, moved from `kit.py` (`kit.py` 140–146, 172–186), and `bolt_at` (pure) and `bolt_read(main, bolt)` (`git rev-parse --verify -q refs/remotes/origin/bolt/<b>^{commit}`, the same for `refs/heads/bolt/<b>`, `git show refs/remotes/origin/bolt/<b>:.config/sluice.toml` only when the first is there). `plugin/lib/kit.py`: `import gather`; `branch_table = gather.branch_table`; `bolt_remote` calls `gather.policy_remote`, catching its `ValueError` into the refusal it gives today. Logic cases in `tests/py/test_bolt_commands.py`, a class `TestWhereABoltIsRead`: GitHub's copy naming origin → `refs/remotes/origin/bolt/b`; GitHub's copy naming none, host copy present → `refs/heads/bolt/b`; no GitHub copy → the host's; neither → None; and `policy_remote` on a policy with `[branches."bolt/*"] remote = "origin"`, one with a more specific table naming none, none at all, and text that is not TOML (raises). `tests/py/test_kit.py`'s existing cases of `bolt_remote` and `branch_table` pass unchanged.

**1.2** `gather.kit`: the bolt list and the per-bolt facts read at `bolt_read`'s ref as Decision 2 has it, with `at` and `error`; `chore_place(path, bolt, ref)` taking the ref from `kit`, `own_head(cwd, branch, bolt)` and `fix_merged` reading at `bolt_read`. `plan.Stages.of` and `bolt_state`: a bolt whose facts carry `error` reads `unknown` with it (a unit's or chore's stage not already `landed` by main). Contract cases in `tests/contract/test_gather.py`, each with a bare clone as GitHub (as `test_places_cut_from_the_bolt_on_github_name_it_by_their_upstream` sets one up) and a policy committed on main with `[branches."bolt/*"] remote = "origin"`: a unit's merge and a chore's merge landed on GitHub's `bolt/te` from another clone and fetched, the host's `bolt/te` left behind, reads both merged, `head` GitHub's and `verdict` its trailer; a chore's place one commit beyond GitHub's bolt reads `ahead` 1; a fix whose tip only GitHub's bolt holds reads merged; a legacy bolt whose GitHub copy's policy names no remote reads at the host's branch with its extra merge; a policy that is not TOML at GitHub's copy reads `exists` False with an `error` naming `.config/sluice.toml`; the existing case that reads a bolt from the host's branch with no policy still passes. A logic case in `tests/py/test_stages.py` or `tests/py/test_bolt_commands.py`: `Stages` over a gathered kit whose bolt carries `error` reads a merged-looking unit `unknown` with that why, and `bolt_state` `unknown`.

**1.3** `plan.py`: `land_facts`'s merge-base, `chore_commits`, `undeclared`, `change_words`, `forecast_words`, `rebase_words`, `landed_at`, and the `ONTO` and `TAKE` scripts (their bolt argument becomes the ref; `rebase_dependents` and the take's caller pass `k["bolts"][b]["at"]` or `bolt_read`'s ref) read at the bolt's ref. Contract cases in `tests/contract/test_git.py`: `ONTO` and `TAKE` given `refs/remotes/origin/bolt/b` rebase onto and leave out GitHub's bolt with the host's `bolt/b` behind it; `landed_at` finds the commit on GitHub's bolt. The existing `ONTO` cases pass with their argument given as `refs/heads/bolt/<b>`. Logic cases in `tests/py/test_forecast.py`: `rebase_words` for a bolt read at `origin/bolt/b` names `git fetch origin` and `git rebase origin/bolt/b`, and for `bolt/b` reads as today.

**2.1** `plan.survey` and `plan.stages_for` take `fetch`; `gather.kit` fetches when its request says so, as Decision 3 has it; a fetching survey skips `READ.kits`. `bolts_view` and `bolt_give`'s proven check pass `fetch=True`. Logic cases in `tests/py/test_bolt_commands.py`, monkeypatching `plan.gathered` to capture the request: `bolts_view`'s survey asks `"fetch": true`; `stages_for` without it does not; a fetching survey is asked even when `READ` holds the kit. Contract case in `tests/contract/test_gather.py`: a request with `fetch` reads a merge pushed to GitHub's `bolt/te` after the host last fetched; one without reads the bolt as last fetched; a `fetch` against an origin that is not there answers `ok` False naming "cannot fetch" and git's words.

**2.2** `deliverable_facts`'s merge path: `gather.fetched(main)` then `bolt_read`; `delivered` says the fetch's failure. Logic cases in `tests/py/test_stage_ends.py`, in the style of `test_a_commit_between_the_reads_never_pairs_its_ticks_or_time_with_the_earlier_head` (monkeypatching `plan.gather.run`): a merge look runs `git fetch -q origin` before any read of the bolt and reads its chores and head at `refs/remotes/origin/bolt/b` when GitHub's copy names origin; a failed fetch gives `(None, "can't fetch bolt/b from GitHub: …")`.

**2.3** `BOLT_CREATE` fetches the branch it made, as Decision 3 has it. Checked end to end in `tests/t-journey-plan.sh` (the journey that gives a bolt on GitHub): after the give, the kit's main checkout holds `refs/remotes/origin/bolt/<bolt>` at the commit the give names.

**3.1** `tests/stubs/wt-submit` (and `tests/stubs/sluice` where it lands a bolt) with the `sluice-leaves-copy` switch, Decision 4, its header comment saying so. `tests/t-journey-units.sh`: with the switch on, a unit's merge into the bolt on GitHub leaves the host's `bolt/<bolt>` and `origin/bolt/<bolt>` where they were, `crew unit wait` returns delivered at GitHub's head, and `crew bolts --json` shows the unit `merged`. Add `# Reads:` lines and run `tests/moon-tasks` if a test's inputs change (`tests.10`).

**3.2** `README.md` (the paragraph on bolts on GitHub, beside "Every unit's, chore's and fix's place is cut from `origin/bolt/<bolt>` after a fetch") and `plugin/skills/crew/SKILL.md` (the same sentence there): a bolt on GitHub is read at `origin/bolt/<bolt>`, never at the host's copy, which is sluice's; `crew bolts`, a give and a wait on a merge fetch it first, every other read takes it as the host last fetched it. `tests/t-docs.sh` passes.

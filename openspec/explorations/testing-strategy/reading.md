# Exploration: a testing strategy for crew and swancloud, with cached checks

Date: 2026-10-07. Pane: exploration beside swancloud-design, session swancloud-1, mac-studio.

## Explored

Chuck brought a prompt from another session ("Cache test runs with moon and devenv, in swancloud and in crew": a check whose inputs haven't changed is never run again, in any worktree; one moon task per check; moon caches only exit 0; inputs must name everything a check reads; nothing live is cached; outputs shared through the git common dir; moon from devenv; the merge gate runs `moon run :test --affected`; `$DEVENV_ROOT` at run time; no `devenv shell --` wrapping) and asked to handle it together with: a testing strategy for crew and swancloud ("i don't think we really have one for swancloud"), worktrunk setup in crew with wtenv, maybe splitting the tests out, and the queued crew unit `a-command-reads-the-kits-once`.

## Found

**crew**

- `tests/run` already exits non-zero when a test fails: its last line is `(( ${#failed[@]} == 0 ))` (there since commit 77ec01e), and `devenv shell -- tests/run no-such-test` returns exit 1. crew's `CLAUDE.md` line 12 says "`tests/run` exits 0 even when a test fails": stale. The pasted prompt's "make tests/run exit non-zero" is already done.
- 44 tests (`tests/t-*.sh`, 3,654 lines with `tests/lib.sh`), run serially by `tests/run`, each in its own scratch dir `$T` with a scratch HOME per simulated host, bare remotes under `$T`, and stub herdr/ssh/hostname/sleep/claude first on PATH, recording into `$T/calls.log` (`tests/lib.sh` lines 1–30). One live test, `t-sites-live.sh`, runs only with `CREW_TEST_LIVE=1`.
- Full suite ~20 min, measured by crw-1-ops 2026-10-07 (`openspec/explorations/command-cost/reading.md`): the cost is crew itself (openspec started twice per unit worktree per read, several plan.py runs per command, stub herdr 40 ms/call), not the tests' own work.
- Every command path crosses `plugin/lib/plan.py` (2,897 lines): `bin/crew` dispatches to plan.py, record.py, sites.py; plan.py imports crew, gather, record, transcript; sites imports plan. So every test's honest inputs are `plugin/**`, `tests/lib.sh`, `tests/stubs/**` and its own file; nothing narrower.
- Commits since 2026-09-20: 153. 89 touch `plugin/` (all tests rerun), 49 touch neither plugin nor tests (full cache replay), 15 touch only tests (only those rerun).
- No moon, no `.config/wt.toml`. `devenv.nix` is jq, python3, recutils. `devenv shell -- true` warm: 0.6–0.8 s. `openspec list --json`: 0.7 s.
- The briefs already assume the switchboard-kit shape: `plugin/roles/coder.md:25` tells coders to run `moon run <project>:test` / `moon run :test --affected` and says `wt merge` checks the branch and the bolt verifies after merge; `conductor.md:68` and `ops.md:22` assume a kit's merge hooks verify (`post-merge-verify`, `main-status`). Only switchboard-kit has them (`switchboard-kit/main/.config/wt.toml`: pre-merge typecheck, test-changed, main-red-check, clean-tree; post-merge verify; pre-remove).
- User-level worktrunk config (`swancloud/main/modules/home-worktrunk.nix`): `[merge] verify = true`, rebase, no squash, remove. Repo hooks run when a repo has them; crew and swancloud have none, so `wt merge` into a bolt there runs no gate today.
- `a-command-reads-the-kits-once` is queued in crew's queue (`crew bolts`), source `openspec/explorations/command-cost/reading.md`.
- swancloud-design, by crew tell: the unit "covers only what happens inside one crew command: one kit read and one state fetch per command, stage facts agreeing with openspec's on the same worktree under a test, and the stub herdr's cost. Not tests/run, not how the suite is split, not caching." The record "holds nothing on caching checks, on a testing strategy for swancloud, or on worktrunk hooks for crew." Giving crew wt hooks "aligns it with what the briefs assume, it reopens nothing." Don't reopen: stages read from the kits (bolt-plan spec); nothing committed to main beside a landing (ADR 0006); a version bump or config alignment or stale instruction is a chore (ADR 0001); outcomes with readings beside them (ADR 0004).

**swancloud**

- No `tests/`, no flake `checks` output, no moon, no `.config/wt.toml`. 16 machines (`machines/`), 8 clanServices of its own (7 wired in `clan.nix`). Six packages carry check phases: devurl-mirror (`test.sh`, a stubbed test in the check phase), crabtalk, herdr-git, paperless-gpt, roamgate, uxc.
- `CLAUDE.md:269`: "A bolt is proven by evaluating and building, never by deploying."
- Two shells: `.envrc` is `use flake` (flake devShell: clan-cli, microvm-restart; `flake.nix` 218–240); `devenv.nix` separately runs an openspecui process and writes `.claude/settings.json` through `files."${config.devenv.root}/..."`; that file is a symlink into the store whose name carries the worktree's absolute path. `devenv shell -- true` warm: 0.55 s.
- `docs/worktrunk-explore/README.md` is a wish-list of wt features; Chuck: disregard it.
- Research: clan-core's own ladder is nix-unit eval tests for module and library logic, container tests as the default for services (faster than VMs, on by default), VM tests where kernel or hardware matters, pytest for CLIs; tests sit beside what they test under `checks/<name>/default.nix`, run as `nix build .#checks.<system>.<name>` (clan.lol/docs/26.05/guides/contributing/testing). numtide/blueprint derives checks automatically from hosts, packages and devshells. Nix's eval cache is bypassed when the git tree is dirty (each evaluation copies the tree to the store under a new hash, deliberately); a clean committed worktree hits the eval cache and the store. An unchanged toplevel has the same drvPath and is already in the store, so "affected" is free in Nix; nix-fast-build evaluates checks in parallel and builds only what is missing. flake-parts and the dendritic pattern are a layout refactor for modularity, not testability.

**wtenv**

- agentplot/wtenv PR #1 (open, branch spike/wtenv): hit 0.53 s, same environment, 20 concurrent worktrees → 1 evaluation. Design: cache under `<git-common-dir>/wtenv/<key>/<variant>`, a devenv adapter that owns `DEVENV_ROOT`, the dotfile, the runtime dir and devenv's files-module paths (so swancloud's settings.json line may pass its check), a Claude Code plugin loading the environment into every Bash command, `wt env warm` on post-start. A bash spike; its results recommend a compiled binary.

## Decided

- Gates in crew: "3. yes to both" — pre-merge on unit → bolt and on bolt → main, in crew's `.config/wt.toml`, inside devenv; post-merge on the bolt runs the full suite as the bolt's verification ops reads.
- Order: "4. moon unit after kits-once".
- The split: "1. you tell me", then "ok" after the challenge "what does this buy us if the input is plugin/*?" Recommendation accepted: one moon task per test file, run in parallel, generated from `tests/t-*.sh` by a script that fails when a test has no task; each task runs `tests/run <name>`; inputs `plugin/**`, `tests/lib.sh`, `tests/stubs/**`, the test file; `t-sites-live` is not a task; outputs linked to `<git-common-dir>/moon-outputs`, `MOON_TOOLCHAIN_FORCE_GLOBALS=true`, moon pinned in devenv. The unit's design states the value honestly: parallelism (the serial 20 min becomes about the longest test plus contention), replay of identical trees across worktrees and stages (the gate replays the agent's pass when the bolt hasn't moved; post-merge always replays the gate's pass; a rerun with nothing changed is free), and test-only edits rerunning one test. Not narrowing on plugin changes.
- swancloud: "2. i don't know that we have tests tbh for swancloud. but maybe do some online research on keeping nix/flake projects moduler, fast, and "testable". maybe some best practices could go in as ADR/constitution and we could refactor over time" — rules proposed for the constitution/ADR, refactored toward over time: every machine's toplevel is a flake check, so `nix flake check` is the one definition of green; a package proves itself in its check phase; a clanService swancloud writes carries a test that runs without the fleet (nix-unit for its options, a container test where it runs a daemon); a bolt's proof is the checks of what it touched, built, not deployed. Measure `nix flake check` (no change, one file, second worktree) before any swancloud moon unit; the expectation is that moon adds nothing there. flake-parts/dendritic stay out of the rules.
- "docs/worktrunk-explore/README.md should be disregarded".
- Shape under ADR 0001: the `CLAUDE.md` exit-code line is a chore; the gate and the moon tasks are units (they decide inputs, granularity and what a merge checks); kits-once stays as queued; wtenv is a spike in a scratch worktree with nothing on main (the pasted prompt: "put nothing in either repo's `main` without asking me").
- "ok. let's return all of your recommendations to the crew".

## Open

- Gate before moon: my recommendation was to land the gate first, at 20 min per merge, since main is live and merges are one at a time; Chuck's "3. ok" answered the section that contained it. Worth an explicit word.
- That the 44 tests don't collide when run at once: nothing read shares state outside `$T`, but the proof is one full parallel run compared with a serial one.
- Which shell swancloud's agents actually sit in (flake devShell via direnv, or devenv): decides where moon or wtenv would come from there.
- swancloud's numbers: no-change `nix flake check`, one-file change, second worktree. The reading comes before the unit.
- Darwin toplevels can only be checked on a Mac: checks per system, and which machine runs the gate for which.
- Whether wtenv is tried at all; if so, a scratch worktree, numbers against PR #1, nothing on main.

## Pointers

- crew: `tests/run`, `tests/lib.sh`, `CLAUDE.md:11-13`, `plugin/roles/coder.md:25`, `conductor.md:68`, `ops.md:22`, `openspec/explorations/command-cost/reading.md`, `docs/adr/0001`, `0004`, `0006`.
- swancloud: `CLAUDE.md:269`, `devenv.nix:16`, `.envrc`, `flake.nix:218-240`, `clan.nix`, `packages/devurl-mirror/{default.nix,test.sh}`, `modules/home-worktrunk.nix`.
- switchboard-kit reference: `main/devenv.nix:818-834` (outputs link), `.moon/workspace.yml`, `.moon/tasks/all.yml`, `.moon/scripts/moon-tests.sh`, `.config/wt.toml`.
- Commands: `crew bolts` (kits-once queued); `devenv shell -- tests/run no-such-test; echo $?` → 1.
- wtenv: https://github.com/agentplot/wtenv/pull/1, `docs/spike-results.md` "The design as it stands".
- Research: https://clan.lol/docs/26.05/guides/contributing/testing, https://github.com/nix-community/nix-unit, https://github.com/numtide/blueprint, https://github.com/Mic92/nix-fast-build, https://discourse.nixos.org/t/nix-evaluation-cache-a-devshell-during-local-development/39159.
- Scratch: OpenSpec explore skill source and wtenv spike results under /private/tmp/claude-501/-Users-chuck-Code-github-afterthought-blueprints-main/1c2a7eb8-9aaf-49bc-a676-06e42f180bb3/scratchpad/.

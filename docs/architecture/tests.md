---
paths:
  - "tests/**"
  - "devenv.nix"
  - ".config/**"
  - ".claude/settings.json"
  - ".claude/hooks/**"
  - ".envrc"
---

# Test rules

The rules for how crew is tested and gated. `core.md` binds here too; the how-to is CLAUDE.md's Tests section. Why the suite gates every merge and runs as moon tasks is record 0008.

## Rules

- **[tests.1]** Tests run only through `tests/run`, which refuses to start outside a devenv shell or unless stub herdr, ssh, hostname and claude shadow the real ones, gives each test its own scratch directory and home per simulated host and bare remotes, and exits non-zero on any failure; only "0 failed" passes.
- **[tests.2]** Every `tests/t-*.sh` opens with a comment saying what it proves and, as its first command, sources `lib.sh` through `${TESTS:?…}`, so it stops when run outside the runner; a test reaches a real service only under `CREW_TEST_LIVE=1`.
- **[tests.3]** A test edits a fixture in place with `rewrite`, never `sed -i`, and runs crew only as a simulated host.
- **[tests.4]** A fix to `plugin/` lands with a test that reproduces the case it fixes, and when the fix depends on how a real tool behaves, the stub is changed to behave the same way.
- **[tests.5]** Every merge into a bolt and onto main is gated by the suite, and the full suite on the bolt after each merge is the bolt's verification; the suite runs as one moon task per test file, in parallel, replayed on an identical tree.
- **[tests.6]** Every rule a brief carries is pinned by a phrase `tests/t-briefs.sh` checks.
- **[tests.7]** A Claude session in a crew checkout works inside crew's devenv shell, entered at its start by the checkout's SessionStart hook; no CLAUDE.md, README, brief or skill tells an agent to wrap a command in `devenv shell --`, and only worktrunk's merge hooks enter the shell themselves.
- **[tests.8]** A test waits on a condition, never on the clock: no fixed sleep decides an outcome, every wait it makes has a limit that holds on a host under heavy load, and a verification that reddens only because the host was busy is a defect of the test, fixed before the next bolt lands.
- **[tests.9]** The suite's parallelism on a host is bounded by that host's cores, shared across every team's verification and merge gate running on it, so two suites side by side never load a host past its cores; a run that would exceed the bound waits its turn rather than thrashing the host.
- **[tests.10]** A test's moon task takes as inputs crew's command core and each other path its outcome depends on, named on its `# Reads:` line, and a merge onto main replays no test.

## Details

**[tests.1]** Rules out: `bash tests/t-x.sh`; a run reaching the real plan; a run on the host's tools in place of the shell's. Source: fixes 0a3753e, d295474; `tests/run`; CLAUDE.md §Tests; agents-work-inside-crews-devenv-shell.

**[tests.2]** Rules out: a test with the guard below its first command; a live call in an ordinary test. Source: all `tests/t-*.sh`; `tests/t-sites-live.sh`.

**[tests.3]** Rules out: `sed -i ''`. Source: fixes 5942223, dd72bd9.

**[tests.4]** Rules out: a code fix with no test; a stub that behaves unlike the tool. Source: fixes e413c48, f734f28, 5e11de2, 25c300d, 04daa5d.

**[tests.5]** Rules out: a merge with no gate; one task for the whole suite. Not ruled out: a kit opted into sluice, whose pre-merge hooks run the suite as `wt submit`'s submit gate and whose verdict decides the merge (ADR 0014, D7; sluice record 0002). Source: ADR 0008; `tests/suite`; `tests/moon-tasks`.

**[tests.6]** Rules out: a brief rule with no phrase in `t-briefs.sh`. Source: fix a2ea85e; rulings-rest-on-readings design. Five brief fixes have no phrase: `_open.md`.

**[tests.7]** Rules out: `devenv shell -- tests/run` in CLAUDE.md; a brief telling an agent to wrap a command; the shell entered by crew-role or by the plugin. Source: signal `2026-10-08-swancloud-planner-0ca5793d/01-agents-run-inside-the-shell-and-only-affected-tests`; swancloud's record 0003, "The shell"; agents-work-inside-crews-devenv-shell; `tests/t-dev-shell.sh`.

**[tests.8]** Rules out: `sleep 1.1` standing for "a later second"; a sixty-second stuck limit as a proof of "never stuck"; a rerun as the fix. Read on 2026-10-10: `t-stage-ends` and `t-amend` failed under a load average of 247 on mac-studio and passed alone (signal 2026-10-10-crw-1-conductor-e7003d11/01); `t-stage-ends.sh` 31 sleeps 1.1 s so a commit lands in a later second and 94, 101 and 134 wait with stuck limits of 60 s and an hour; the host's load was 53, 105 and 202 at 23:52 local. Built 2026-10-11 for the tests' own waits: `until_ok` in `tests/lib.sh` waits on a condition for up to ten minutes, every polling loop's limit is ten minutes, a background wait's timeout thirty, `t-events` waits for its follower's tails rather than two seconds, and `t-stage-ends` backdates a commit rather than sleeping into the next second; a sleep that only orders two writes, which load can only lengthen, stays. Source: `tests.5`; ADR 0008; `tests-hold-under-a-loaded-host`; what is left, crew's own fifteen-second read-back of a prompt, is in `_open.md`.

**[tests.9]** Rules out: fifty moon tasks at once per team on a ten-core host; two teams' suites each sized as if alone. Read by swancloud-ops on 2026-10-10: mac-studio's peak of 247 (23:37 to 23:52 local) lines up with crw-1's verification of a-board-over-the-flow, 48 of 50 tests unreplayed as moon tasks side by side, beside crw-2's code stage running crew's tests and one two-minute swancloud flake check; nix-daemon built only system assembly, the Linux builder and plannotator were not in evidence (signal 2026-10-10-swancloud-design-c0b2ca89/01). Source: ADR 0008 (one moon task per test, in parallel, replayed when unchanged); `tests.5`; ADR 0021, which builds it: `tests/run` runs each test in one of the host's slots (`tests/slot`), half its cores unless `CREW_TEST_SLOTS` says otherwise, shared by every worktree on the host (`tests/t-slot.sh`). Read again by swancloud-ops on 2026-10-11: load 386 on mac-studio, crew's suites in `/tmp/crew-test.*` running beside crw-3's places, and swc-1's verification of a one-line carry ran past seven minutes while the laptop's emergency fix waited on it.

**[tests.10]** Rules out: every task taking all of `plugin/**`, which reran 59 tests for a role's prose; a test reading a hook, a role's words or a page module it does not name; a landing resting on a replay. Not ruled out: `plugin/lib` named bare, as the folder a test imports the core from. The core is `plugin/bin/**` and the modules `plan.py` and `crew.py` import (`CORE` in `tests/moon-tasks`); a test that starts an agent names `plugin/hooks/`, since the stub claude runs the session-start hook; one whose outcome rests on a brief's words names `plugin/roles/`. Read on 2026-10-11 by tracing every test's opens of `plugin/` and replacing the roles' prose: ADR 0021. Source: ADR 0021; `tests/moon-tasks`; `tests/suite --gate`; `.config/wt.toml`; `tests/t-suite.sh`.

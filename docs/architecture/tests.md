---
paths:
  - "tests/**"
  - "devenv.nix"
  - ".config/**"
---

# Test rules

The rules for how crew is tested and gated. `core.md` binds here too; the how-to is CLAUDE.md's Tests section. Why the suite gates every merge and runs as moon tasks is record 0008.

## Rules

- **[tests.1]** Tests run only through `tests/run`, which refuses to start unless stub herdr, ssh, hostname and claude shadow the real ones, gives each test its own scratch directory and home per simulated host and bare remotes, and exits non-zero on any failure; only "0 failed" passes.
- **[tests.2]** Every `tests/t-*.sh` opens with a comment saying what it proves and, as its first command, sources `lib.sh` through `${TESTS:?…}`, so it stops when run outside the runner; a test reaches a real service only under `CREW_TEST_LIVE=1`.
- **[tests.3]** A test edits a fixture in place with `rewrite`, never `sed -i`, and runs crew only as a simulated host.
- **[tests.4]** A fix to `plugin/` lands with a test that reproduces the case it fixes, and when the fix depends on how a real tool behaves, the stub is changed to behave the same way.
- **[tests.5]** Every merge into a bolt and onto main is gated by the suite, and the full suite on the bolt after each merge is the bolt's verification; the suite runs as one moon task per test file, in parallel, replayed on an identical tree.
- **[tests.6]** Every rule a brief carries is pinned by a phrase `tests/t-briefs.sh` checks.

## Details

**[tests.1]** Rules out: `bash tests/t-x.sh`; a run reaching the real plan. Source: fixes 0a3753e, d295474; `tests/run`; CLAUDE.md §Tests.

**[tests.2]** Rules out: a test with the guard below its first command; a live call in an ordinary test. Source: all `tests/t-*.sh`; `tests/t-sites-live.sh`.

**[tests.3]** Rules out: `sed -i ''`. Source: fixes 5942223, dd72bd9.

**[tests.4]** Rules out: a code fix with no test; a stub that behaves unlike the tool. Source: fixes e413c48, f734f28, 5e11de2, 25c300d, 04daa5d.

**[tests.5]** Rules out: a merge with no gate; one task for the whole suite. Source: ADR 0008. Not built: `_open.md`.

**[tests.6]** Rules out: a brief rule with no phrase in `t-briefs.sh`. Source: fix a2ea85e; rulings-rest-on-readings design. Five brief fixes have no phrase: `_open.md`.

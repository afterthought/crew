# Tasks

## 1. crew's own toolchain

- [x] 1.1 crew's devenv carries moon 2.6.1 from moonrepo's release for each platform, hashes pinned, as sluice's did, and `tests/suite t-suite t-merge-gate logic contract` ends with "0 failed" (dc1e6ce; `code.1`, `tests.5`).
- [ ] 1.2 crew's devenv carries proto, jq and recutils; `.prototools` pins moon 2.6.1, Python 3.13.15 and uv, activated with crew's own proto and moon homes; moon's Python toolchain syncs pytest from `tests/pyproject.toml` and `tests/uv.lock`; crew declares its toolchain and runner in `.config/sluice.toml`; `MOON_TOOLCHAIN_FORCE_GLOBALS` is gone; `t-dev-shell` checks moon's version and the tests' Python, and `tests/suite --affected` ends with "0 failed" (design: *crew's own toolchain*; Task notes 1.2; `code.1`, `tests.10`).

## 2. A worktree is made ready through its kit's declaration

- [ ] 2.1 `plugin/lib/kit.py` reads a declaration and decides the steps that make a worktree ready, the command inside the toolchain and moon's floor, with logic cases and a contract case for sourcing, and `tests/suite logic contract` ends with "0 failed" (design: *The declaration*, *The adapters*; Task notes 2.1; `code.1`, `code.7`, `read.1`, `tests.11`).
- [ ] 2.2 `make_place` runs the declared toolchain and the runner's setup in every worktree it makes or finds made, on the team's host with the cleaned environment, refusing in the step's words when one fails, and runs no `crew-prepare`; `t-journey-units` proves the steps after give and construct, inside the toolchain, none for a kit that declares nothing, and a refused setup made good by a second run, and `tests/suite journey-units journey-plan` ends with "0 failed" (design: *When a worktree is made ready*; Task notes 2.2; `read.1`, `read.4`, `teams.9`, `tests.4`).

## 3. The docs

- [ ] 3.1 README says what a kit declares for crew and what crew runs from it, CLAUDE.md says crew's toolchain is proto's pins in devenv's shell, and `tests/suite --affected` ends with "0 failed" (Task notes 3.1; `docs.2`).

## 4. What sluice asks of crew

- [x] 4.1 Every agent crew starts carries `SLUICE_AGENT`, the same as `CREW_AGENT`, at its start and on a herdr resume, `teams.6` says so, and `tests/suite roles session-hook` ends with "0 failed" (4bdc6d0; `teams.6`, `tests.4`).

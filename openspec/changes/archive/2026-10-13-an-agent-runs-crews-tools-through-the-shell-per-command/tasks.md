# Tasks

## 1. No session is entered into crew's shell

- [x] 1.1 `.claude/hooks/devenv-shell`, `.claude/settings.json` and `tests/t-dev-shell.sh` go, and `tests/moon.yml` follows; `tests/moon-tasks --check` passes and `tests/suite --affected` ends with "0 failed" (`tests.7`, `tests.10`).

## 2. The runners enter the shell themselves

- [x] 2.1 `tests/run` and `tests/suite`, started with no `DEVENV_ROOT`, run themselves again under `devenv shell --` from their own checkout, stopping when the shell sets no `DEVENV_ROOT` or there is no devenv; proved by `tests/t-runner.sh` (`tests/suite runner`) (`tests.1`).

## 3. A wrapped command costs a warm entry

- [x] 3.1 crew's shell runs `proto install` only when a pin of `.prototools` is missing from crew's proto home; `tests/contract/test_toolchain.py` (`tests/suite contract`) proves the shell's moon is proto's from crew's own home at or above sluice's floor and the tests run on Python 3.13 with pytest; ten warm entries measured with and without it, the load beside each, in `devenv.nix` and `tests.7` (`code.1`, `tests.11`).

## 4. The docs

- [x] 4.1 CLAUDE.md's Tests section names `devenv shell -- <command>` and drops "no agent wraps", README says the runners enter the shell themselves, and `tests/t-docs.sh` (`tests/suite docs`) checks that CLAUDE.md names the wrap, no brief or skill does, and the `.envrc` and `.gitignore` hold (`tests.7`, `docs.2`).
- [x] 4.2 `tests.1` and `tests.7` lose their not-built clauses, `_open.md` keeps swancloud's half alone, and `a-kit-declares-its-toolchain-and-tests` puts its toolchain requirement on `test-suite`; `openspec validate --strict` passes for both changes (`docs.3`, `docs.4`).

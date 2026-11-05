# Verify: crew-readies-no-worktree-a-place-is-equipped-by-sluice

Read 2026-11-05 on deneb, at `20cc46c8` on `change/crew-readies-no-worktree-a-place-is-equipped-by-sluice`, cut from `teamless/deneb` at `b57c709d`.

**Outcome: archived.** All 7 tasks are ticked, and every check they name passes. Both deltas' requirements and scenarios are met. The change touches the 13 files its proposal names and nothing else outside its own directory. No `crew` behaviour changes. Nothing fails a requirement.

## Tasks

| Task | Check | Read |
|---|---|---|
| 1.1 | Record 0023's two greps | 1 and 1. The line under the title and the amendment are Task notes 1.1's text, word for word. |
| 1.2 | Record 0024's two greps | 1 and 1. The amendment closes the question *Not decided here* left open, and names the task's status as the build's choice with the paths not taken. |
| 1.3 | Record 0028's two greps | 1 and 1. Point 1 goes to Flume (Flume 12, S16). Points 2 and 3 stand. |
| 2.1 | `openspec validate … --strict`; `git grep -n kit-toolchain -- plugin tests README.md CLAUDE.md docs/architecture`; `tests/suite logic` | Valid (openspec 1.15.0). The grep prints nothing. `logic` passed, run with `--force`. `.openspec.yaml` carries `retire_capabilities: true`. `test_kit.py`'s docstring cites Flume's record 0036, and `SCRIPT` is gone. |
| 3.1 | `tests/suite t-docs` | Passed, run with `--force`. The new check holds the README to "crew readies no worktree" and `` `sluice equip` ``, and the policy's lines above its first table to `sluice equip` and no `plan.17`. Its `# Reads:` line names `.config/sluice.toml`, and `tests/moon.yml`'s `t-docs` inputs carry it. |
| 4.1 | `tests/suite contract` | Passed, run with `--force`. `test_the_toolchain_crews_policy_names_only_activates` is as Task notes 4.1 has it: it runs `.config/sluice.toml`'s `[tests] toolchain` from crew's root with a ten-minute limit, and asserts `proto activate` and no `proto install`. The contract task's inputs carry `/.config/sluice.toml`. |
| 5.1 | `tests/suite --affected` | "26 passed (26 replayed), 0 failed". Each replay is of a pass on identical inputs on this host (`tests.9`), and the three tiers above also ran afresh. sluice runs every task afresh at the landing. |

Task notes 4.1's readings, made again:

- `devenv print-dev-env | grep -c 'proto install'` prints 0, and `grep -c 'proto activate'` prints 1.
- `devenv shell -- moon --version` prints `moon 2.6.1`, the pin `.prototools` names. The entry ran `crew:proto:install`, before `devenv:enterShell`, and skipped it by its status ("cached"), every pin being in crew's proto home.

## The deltas

**`kit-toolchain`: three requirements REMOVED, and the capability retired.** Each removal names its reason and where its subject now lives (Flume 11, 12, S16; sluice 147, C.2). Nothing in `plugin/lib` or `plugin/bin` reads `[tests]`, a toolchain or `print-dev-env`, or runs `moon setup`: `git grep` for each prints nothing. `kit.py` reads of the policy only bolt-branch gates, remotes and previews. The archive retires `openspec/specs/kit-toolchain/spec.md`, as Decision 2 has it. Nothing outside the records and archived changes cites the spec.

**`test-suite`, "crew's own toolchain is devenv's system tools and proto's pins": MODIFIED.**

- **The requirement.**
  - The install is a devenv task, `crew:proto:install`, with `before = [ "devenv:enterShell" ]`.
  - Its `status` exits 1 at the first pin missing from `$PROTO_HOME/tools/<tool>/<version>`, and 0 otherwise or with no `.prototools`.
  - Its `exec` runs `proto install --config-mode upwards || true` from the checkout's root.
  - `enterShell` keeps the cache link, the homes (now the shared `homes` fragment) and `proto activate`, and installs nothing.
  - crew declares its toolchain and runner in `.config/sluice.toml`, unchanged.
- **"The tests' Python", "moon's version", "A moon of the user's".** Unchanged scenarios, held by the contract tier's two existing cases, which passed.
- **"The toolchain crew's policy names only activates".** The new contract case, which passed. The printed script holds `proto activate` and no `proto install`.

## The words

- **`.config/sluice.toml`.** The opening comment is Task notes 3.1's text. The tables are unchanged.
- **`README.md`.** Line 18's first sentences are Task notes 3.1's text. The sentence on what crew reads of the policy follows unchanged.
- **`plugin/lib/kit.py`.** The docstring is Task notes 3.1's text. No code changed.
- **`devenv.nix`.** The comments moved with the code as Task notes 4.1 asks. The 2.8 seconds and the reason for a status are on the task. Why it is a task (the printed script holds no task) is on the task too. The comment above `enterShell` says it only activates.
- **`tests/contract/test_toolchain.py`.** The module docstring cites record 0023, point 5, in place of `plan.17`, and gains the new case's sentence.
- **`tests/moon-tasks`.** The docstring says the contract tier takes crew's policy.

## Outside this change

These hold nothing up. They are noted for whoever reads crew next.

- **`plan.17` is still cited in `plugin/lib/kit.py`.** `give_remote`'s docstring and refusal text (lines 140–145) cite it for "writing the key is the kit's own change". `plan.17` was retired on 2026-11-03. The change's design scopes `kit.py` to its module docstring, and the citation is about a bolt branch's remote, not readiness. A later chore can cite the right rule.
- **`teamless/deneb` moved after the cut.** GitHub's branch is `9d854501`, ahead of `b57c709d` by #439, which adds four lines to `CLAUDE.md`. `git merge-tree` merges it with this branch cleanly. `CLAUDE.md` is an input of `t-docs`, so sluice's run at the landing proves the two together.
- **The new contract case's failure on the old `devenv.nix` was not read again.** The design says it fails at `b57c709d`, whose `enterShell` installed, and Task notes 4.1 had the code stage see it fail first. This stage read only that it passes at `20cc46c8`.

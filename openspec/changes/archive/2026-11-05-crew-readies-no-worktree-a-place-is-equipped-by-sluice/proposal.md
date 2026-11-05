# crew readies no worktree: a place is equipped by sluice at Flume's asking

## Why

On 2026-11-05 the user approved Flume's cross-tool design, "a place's readiness is one design across the tools", with Flume's record 0036 ("Approve: start its code"). It gives each part of readiness one owner. The repository declares its tools. sluice equips a working copy (`sluice equip`, sluice's clause 147 on agentplot/blueprints main at 9f1f0fd). Flume asks for that equipping when it makes a place. crew and Boomdrive ready nothing. Its decision 7 names crew's part.

crew's code already readies nothing. `plan.17` was retired on 2026-11-03 with `the-team-machinery-leaves`, and `kit.py` says crew readies no place. But crew's record says otherwise in four places:

- Records 0023, 0024 and 0028 say crew runs the toolchain and `moon setup` in every worktree it makes.
- The `kit-toolchain` spec still requires it.
- The policy's opening comment says crew reads the policy "when it makes a worktree of crew ready".
- `devenv.nix`'s `enterShell` runs `proto install`. So the toolchain sluice and Flume source, `devenv print-dev-env`, installs as well as activates. The kit standard's toolchain.8, in the same design, rules that out.

## What Changes

- **Records 0023, 0024 (point 4) and 0028 gain an amendment.** crew readies no worktree. A place is equipped by sluice at Flume's asking (Flume record 0036; sluice 147). The text in which crew readies a worktree is superseded. Record 0024's open question is closed: a devenv kit's `enterShell` no longer runs `proto install` on any entry.
- **The `kit-toolchain` spec loses its three requirements.** They say crew reads `[tests]`, runs commands under the toolchain, and runs `moon --version` and `moon setup`. With nothing left, the spec goes at the archive.
- **`.config/sluice.toml`'s opening comment says the same.** So do `README.md`'s line on what readies a place and `kit.py`'s docstring, which says the same thing. `tests/t-docs.sh` checks the README's line and the policy's comment.
- **`devenv.nix`'s `enterShell` only activates.** A devenv task, `crew:proto:install`, installs what `.prototools` pins, run before the entry. It is skipped when every pin is already in crew's proto home, so a warm entry costs what it does today. The script `devenv print-dev-env` prints, which sluice and Flume source, installs nothing (kit standard toolchain.8). A new contract case proves it.
- **The `test-suite` requirement for crew's own toolchain says so.** The shell's entry installs a missing pin by its task, and the toolchain the policy names only activates.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kit-toolchain`: every requirement is removed, and the spec goes.
- `test-suite`: "crew's own toolchain is devenv's system tools and proto's pins" changes. Its install becomes a task of the shell's entry, and the toolchain crew's policy names only activates.

## Impact

- **Files:**
  - `docs/adr/0023-…`, `0024-…` and `0028-…` gain their amendments.
  - `openspec/specs/kit-toolchain/spec.md` goes at the archive.
  - Also: `devenv.nix`, `.config/sluice.toml` (its comment alone), `README.md`, `plugin/lib/kit.py` (its docstring alone), `tests/py/test_kit.py` (its docstring and an unused fixture), `tests/contract/test_toolchain.py`, `tests/t-docs.sh`, `tests/moon-tasks` and `tests/moon.yml`.
- **No behaviour of the `crew` command changes.** `plugin/bin/` and `plugin/lib/`'s code are untouched.
- **Where it lands:** only on `teamless/deneb`, through sluice. Nothing reaches crew's main.
- **Siblings, each in its own repository:**
  - Boomdrive's record 0009 amendment.
  - The kit standard's toolchain.8.
  - sluice's `equip` change.
  - Flume's change, which replaces its copied readiness steps with `sluice equip`.

  This change waits on none of them. See the design's Risks.

## Touches

```
docs/adr/0023-a-kit-declares-its-toolchain-and-tests-once-for-crew-and-sluice-alike.md
docs/adr/0024-an-agent-runs-its-kits-tools-through-the-shell-per-command-and-the-host-is-the-container.md
docs/adr/0028-a-fix-starts-in-a-place-that-could-not-be-made-ready-and-a-fix-is-dropped.md
openspec/specs/kit-toolchain/spec.md
devenv.nix
.config/sluice.toml
README.md
plugin/lib/kit.py
tests/py/test_kit.py
tests/contract/test_toolchain.py
tests/t-docs.sh
tests/moon-tasks
tests/moon.yml
```

# Readying judges no runner's floor

## Why

crew refused to make a worktree ready when the kit's toolchain ran a moon below 2.6, taking sluice's moon runner's floor for its own. The user, 2026-10-13: "The version of Moon is decided by every kit repo. It's not enforced by Sluice and it's not enforced by crew. It has to do with certain features the project may or may not want to take advantage of, but Sluice does not require Moon 2.6". Told that sluice's moon runner does refuse a moon below 2.6 at its run (`crates/sluice/src/profiles/moon.rs`, its `FLOOR` and `check_version`, read in sluice 0.2.2 on 2026-10-13), the user ruled: "Keep sluice's floor". So crew enforces no floor, and sluice keeps its own at its run.

## What Changes

- Readying runs `moon --version` and refuses only output that names no version crew can read (`read.1`), then runs `moon setup`; `kit.MOON_FLOOR` and `kit.moon_floor` go, and `kit.moon_said` reads the version.
- plan.17, record 0023 and the README say crew enforces no moon floor, a kit's moon is its own, and sluice's moon runner refuses a moon below 2.6 at its run, so a kit on sluice runs 2.6 or later.
- crew's own contract case holds crew's moon to the version its `.prototools` pins, crew's own choice, not to a floor.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kit-toolchain`: the floor's requirement goes; crew enforces no floor, only a version it cannot read is refused, and sluice's floor is sluice's, at its run.
- `test-suite`: crew's own toolchain runs the moon crew pins, not "moon 2.6 or later".

## Impact

- `plugin/lib/kit.py`, `plugin/lib/plan.py` (`make_place`), `tests/py/test_kit.py`, `tests/contract/test_toolchain.py`.
- `docs/architecture/plan.md` (`plan.17`), record 0023, `README.md`.
- A kit whose toolchain runs a moon below 2.6 now has its places made ready; nothing else changes.

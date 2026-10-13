# Design

## Context

`make_place` (`plugin/lib/plan.py`) makes a worktree ready through its kit's declaration (`plan.17`): the declared toolchain, then for a moon runner `moon --version` and `moon setup` inside it. `kit.moon_floor` refused a moon below `kit.MOON_FLOOR`, (2, 6), described as sluice's moon profile's floor, and record 0023, plan.17's detail, the README and the `kit-toolchain` spec said the same. The user ruled on 2026-10-13 that a kit's moon version is the kit's own, enforced by neither sluice nor crew.

The rules this rests on: `plan.17` (readying through the declaration, assuming neither moon nor devenv, amended with this change to say a runner's version is the kit's own), `read.1` (refuse what crew cannot read, naming it), `code.7` (the reading is a function of the output), `docs.4`, `docs.5`. Pages whose area this touches: `plan.md`, `tests.md`, `docs.md`.

## Goals / Non-Goals

**Goals:**
- Any moon a kit's toolchain runs is set up; only a `moon --version` that names no version is refused.
- Nothing in crew says sluice or its moon runner needs moon 2.6.

**Non-Goals:**
- crew's own pin, moon 2.6.1 in `.prototools`: crew's choice as a kit, kept, and held by crew's contract case to the version it pins.
- Whether a kit's moon has the features its tasks use: the kit's, at its run.

## Decisions

### `moon --version` is still read

A toolchain that puts no moon on the path, or a wrapper that fails, prints no version; refusing then names the cause before `moon setup` fails less clearly (`read.1`). So the step stays, and `kit.moon_said` returns why only when the output names no `moon <x>.<y>.<z>`. Alternative: drop the step and let `moon setup` fail, which names nothing of the moon that ran.

### crew's own toolchain is held to its pin

`tests/contract/test_toolchain.py` asked crew's moon to be at or above `kit.MOON_FLOOR`; it now asks for exactly the version `.prototools` pins, which is what crew's own suite is built against.

## Risks / Trade-offs

- [A kit's older moon lacks a feature its tasks use] → its own run fails in its tools' words; that is the kit's to pin, as the user said.

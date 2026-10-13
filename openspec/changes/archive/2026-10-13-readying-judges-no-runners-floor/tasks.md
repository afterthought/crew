# Tasks

## 1. Readying judges no runner's floor

- [x] 1.1 `kit.MOON_FLOOR` and `kit.moon_floor` go; `kit.moon_said` refuses only a `moon --version` that names no version, and `make_place` runs `moon setup` for any version read: `tests/py/test_kit.py` (`test_any_moon_the_kit_runs_is_set_up_and_only_one_whose_version_cant_be_read_is_refused`, moon 1.41.7 and 2.5.3 set up, an empty and a "command not found" output refused), `tests/t-journey-units.sh` (readying inside the toolchain) (design, *`moon --version` is still read*; `plan.17`, `read.1`, `code.7`).
- [x] 1.2 crew's own moon is held to the version `.prototools` pins: `tests/contract/test_toolchain.py` (`test_moon_is_protos_from_crews_own_home_at_the_version_prototools_pins`) (design, *crew's own toolchain is held to its pin*).

## 2. Nothing says sluice needs moon 2.6

- [x] 2.1 plan.17's rule and detail, record 0023's context and point 4, and the README say a kit's moon is the kit's own and readying refuses only a version it cannot read, quoting the user: `tests/t-docs.sh` and `tests/suite --affected` ending with "0 failed" (`docs.5`, `plan.17`).

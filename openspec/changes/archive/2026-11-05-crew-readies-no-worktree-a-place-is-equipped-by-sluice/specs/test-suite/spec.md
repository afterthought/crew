## MODIFIED Requirements

### Requirement: crew's own toolchain is devenv's system tools and proto's pins
crew's devenv shell SHALL carry proto, jq and recutils as its system tools. Entering it SHALL install the tools crew's `.prototools` pins, by a devenv task run before the entry and only when one is missing from crew's proto home, and SHALL activate them: moon at the version crew pins, Python at the minor the hosts run crew on, and uv. The toolchain crew's policy names, `devenv print-dev-env`, SHALL only activate: the script it prints SHALL install nothing. In a working copy sluice equips, sluice's equip installs the pins (sluice 147; kit standard toolchain.8). crew's tests SHALL run on that Python, with pytest from `tests/pyproject.toml`, locked in `tests/uv.lock` and synced by moon. crew SHALL declare its own toolchain and runner in `.config/sluice.toml` like any kit.

#### Scenario: The tests' Python
- **WHEN** crew's logic tier runs as a moon task inside crew's shell
- **THEN** its `python3` is Python 3.13 with pytest importable

#### Scenario: moon's version
- **WHEN** `moon --version` runs inside crew's shell, as a task of crew's contract tier does
- **THEN** it prints the version `.prototools` pins, installed by proto under crew's own proto home

#### Scenario: A moon of the user's
- **WHEN** the user's own proto or moon home holds an older moon
- **THEN** no moon task of crew's runs it

#### Scenario: The toolchain crew's policy names only activates
- **WHEN** the command `.config/sluice.toml` names as its `[tests]` toolchain is run in crew's checkout
- **THEN** the script it prints activates proto's pins and runs no `proto install`

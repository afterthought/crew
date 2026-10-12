## ADDED Requirements

### Requirement: crew's own toolchain is devenv's system tools and proto's pins
crew's devenv shell SHALL carry proto, jq and recutils as its system tools, and SHALL install and activate the tools crew's `.prototools` pins: moon 2.6 or later, Python at the minor the hosts run crew on, and uv. crew's tests SHALL run on that Python, with pytest from `tests/pyproject.toml`, locked in `tests/uv.lock`, synced by moon. crew SHALL declare its own toolchain and runner in `.config/sluice.toml` like any kit.

#### Scenario: The tests' Python
- **WHEN** crew's logic tier runs as a moon task inside crew's shell
- **THEN** its `python3` is Python 3.13 with pytest importable

#### Scenario: moon's version
- **WHEN** `moon --version` runs inside crew's shell
- **THEN** it prints moon 2.6 or later, installed by proto under crew's own proto home

#### Scenario: A moon of the user's
- **WHEN** the user's own proto or moon home holds an older moon
- **THEN** no moon task of crew's runs it

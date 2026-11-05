"""What crew assumes of its own toolchain, each case naming what assumes it: tests/suite runs crew's tasks (`moon exec`,
the `check-full` tag) with the moon crew's .prototools pins, crew's own choice (record 0023, point 5), installed by
proto under crew's own proto home in the git common dir (devenv.nix), never a moon of the user's; and crew's tests run
on Python 3.13, the minor every host runs crew on (code.1), with pytest synced from tests/pyproject.toml. Each run of
crew's tools through the shell, `devenv shell -- <command>`, gets the same (tests.7, record 0024). The toolchain crew's
policy names (.config/sluice.toml) only activates: the script it prints installs nothing."""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tomllib


def test_the_tests_run_on_the_python_minor_every_host_runs_crew_on_with_pytest():
    import pytest  # noqa: F401, the tests' own runner, from tests/pyproject.toml
    assert sys.version_info[:2] == (3, 13)


def test_moon_is_protos_from_crews_own_home_at_the_version_prototools_pins():
    moon, home = shutil.which("moon"), os.environ.get("PROTO_HOME", "")
    assert home and moon and moon.startswith(home + os.sep), f"moon is {moon}, not proto's under crew's own home {home}"
    prototools = pathlib.Path(__file__).resolve().parents[2] / ".prototools"
    pin = re.search(r'^moon = "([^"]+)"', prototools.read_text(), re.M).group(1)
    said = subprocess.run([moon, "--version"], capture_output=True, text=True).stdout
    assert said.strip() == f"moon {pin}", f"crew's toolchain runs {said.strip()}, and .prototools pins moon {pin}"


def test_the_toolchain_crews_policy_names_only_activates():
    """sluice's equip and Flume's readiness source the script this prints, sluice's inside its executor (sluice 147,
    C.2), and the kit standard's toolchain.8 says sourcing it installs nothing: devenv.nix's enterShell only activates,
    and its task crew:proto:install, which the script leaves out, installs a missing pin."""
    root = pathlib.Path(__file__).resolve().parents[2]
    toolchain = tomllib.loads((root / ".config/sluice.toml").read_text())["tests"]["toolchain"]
    script = subprocess.run(toolchain, cwd=root, capture_output=True, text=True, check=True, timeout=600).stdout
    assert "proto activate" in script, f"`{' '.join(toolchain)}` prints a script that activates no proto pin"
    installs = [line.strip() for line in script.splitlines() if "proto install" in line]
    assert not installs, f"`{' '.join(toolchain)}` prints a script that runs proto install: {installs}"

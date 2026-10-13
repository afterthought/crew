"""What crew assumes of its own toolchain, each case naming what assumes it: tests/suite runs crew's tasks with moon 2.6
or later (`moon exec`, the `check-full` tag), the floor sluice's moon runner sets (kit.MOON_FLOOR) and the version
.prototools pins, installed by proto under crew's own proto home in the git common dir (devenv.nix), never a moon of
the user's; and crew's tests run on Python 3.13, the minor every host runs crew on (code.1), with pytest synced from
tests/pyproject.toml. Each run of crew's tools through the shell, `devenv shell -- <command>`, gets the same (tests.7,
record 0024)."""
import os
import re
import shutil
import subprocess
import sys

import kit


def test_the_tests_run_on_the_python_minor_every_host_runs_crew_on_with_pytest():
    import pytest  # noqa: F401, the tests' own runner, from tests/pyproject.toml
    assert sys.version_info[:2] == (3, 13)


def test_moon_is_protos_from_crews_own_home_at_or_above_sluices_floor():
    moon, home = shutil.which("moon"), os.environ.get("PROTO_HOME", "")
    assert home and moon and moon.startswith(home + os.sep), f"moon is {moon}, not proto's under crew's own home {home}"
    said = subprocess.run([moon, "--version"], capture_output=True, text=True).stdout
    m = re.match(r"moon (\d+)\.(\d+)\.", said)
    assert m and (int(m.group(1)), int(m.group(2))) >= kit.MOON_FLOOR, f"crew's toolchain runs {said.strip()}"

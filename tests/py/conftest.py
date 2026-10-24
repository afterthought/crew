"""The logic tier (tests.11): crew's decisions called in-process on plain facts. Nothing here starts a process: every
way Python starts one raises, so a decision that still reaches a tool fails its test, naming the call."""
import os
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "plugin" / "lib"))


@pytest.fixture(autouse=True)
def no_process(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"a logic test starts no process, and this one ran {args[0] if args else kwargs!r}")
    for name in ("run", "Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refuse)
    for name in ("system", "popen", "execv", "execvp", "execvpe", "spawnv", "spawnvp", "fork"):
        monkeypatch.setattr(os, name, refuse)


@pytest.fixture(autouse=True)
def pushed(monkeypatch):
    """record.emit pushes each entry it writes through record.reach, which fetches and pushes the partition's branch:
    here reach stands for it, recording each label it was asked to push, so every case that emits still runs and one
    can say the push was asked (read.5)."""
    import record
    asked = []
    monkeypatch.setattr(record, "reach", lambda label, eid=None: asked.append(label) or 0)
    return asked

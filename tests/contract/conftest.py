"""The contract tier (tests.11): git, recutils and worktrunk run for real in a scratch directory, each case pinning a
behaviour crew's code assumes and naming what assumes it. Every git here runs with no global or system config, so
the host's own settings and hooks reach nothing."""
import os
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "plugin" / "lib"))


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig"))
    (home / ".gitconfig").write_text("[user]\n\tname = Crew Test\n\temail = test@crew.invalid\n[init]\n\tdefaultBranch = main\n"
                                     "[gc]\n\tauto = 0\n[maintenance]\n\tauto = false\n")
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        monkeypatch.delenv(k, raising=False)


class Repo:
    """A scratch git repository: commit files, branch, merge, and read what crew reads."""

    def __init__(self, path):
        self.path = path
        path.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q")

    def git(self, *args, input=None):
        r = subprocess.run(["git", "-C", str(self.path), *args], capture_output=True, text=True, input=input)
        if r.returncode:
            raise AssertionError(f"git {' '.join(args)}: {r.stderr.strip() or r.stdout.strip()}")
        return r.stdout.strip()

    def commit(self, message, files=None):
        """Commit the files given, {path: text}, and return the commit's sha."""
        for name, text in (files or {}).items():
            f = self.path / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text)
            self.git("add", "--", name)
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    return Repo(tmp_path / "repo")

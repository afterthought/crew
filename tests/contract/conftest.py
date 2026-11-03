"""The contract tier (tests.11): git, recutils, worktrunk and moon run for real in a scratch directory, each case pinning a
behaviour crew's code assumes and naming what assumes it. Every git here runs with no global or system config, so
the host's own settings and hooks reach nothing."""
import atexit
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

# crew's modules read the home at import, the teams file and crew's caches among them, and record.emit pushes each
# entry to its partition's branch: they are imported under a scratch home, so no case reaches the host's own fleet,
# its state repositories or GitHub (tests.11).
os.environ["HOME"] = tempfile.mkdtemp(prefix="crew-contract-home-")
atexit.register(shutil.rmtree, os.environ["HOME"], True)
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


class State:
    """A bare repository standing for a partition's state repository on GitHub, afterthought/crew-state, whose
    madswan/main holds a plan, with crew's cache and this command's reading in scratch: write a branch of files to it, as
    another writer, a host's runner among them, would push one."""

    REPO, LABEL = "afterthought/crew-state", "madswan"

    def __init__(self, tmp_path):
        self.bare = tmp_path / "crew-state.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.bare)], check=True)
        self.fleet = {"partitions": {self.LABEL: {"label": self.LABEL, "state": self.REPO}}, "teams": {}}

    def git(self, *args, input=None):
        r = subprocess.run(["git", "-C", str(self.bare), *args], capture_output=True, text=True, input=input)
        if r.returncode:
            raise AssertionError(f"git {' '.join(args)}: {r.stderr.strip()}")
        return r.stdout.strip()

    def push(self, branch, files, message="seed"):
        """A commit of exactly these files at the top of its tree, {name: text}, on top of the branch where it exists,
        set as the branch; its sha."""
        tree = self.git("mktree", input="".join(f"100644 blob {self.git('hash-object', '-w', '--stdin', input=text)}\t{name}\n"
                                                  for name, text in sorted(files.items())))
        parent = self.git("for-each-ref", "--format=%(objectname)", f"refs/heads/{branch}")
        sha = self.git("commit-tree", tree, *(["-p", parent] if parent else []), "-m", message)
        self.git("update-ref", f"refs/heads/{branch}", sha)
        return sha

    def drop(self, branch):
        self.git("update-ref", "-d", f"refs/heads/{branch}")


@pytest.fixture
def state(tmp_path, monkeypatch):
    import plan
    s = State(tmp_path)
    s.push(f"{s.LABEL}/main", {"plan.rec": plan.HEADER}, "plan: start (chuck@deneb)")
    monkeypatch.setattr(plan, "url", lambda repo: str(s.bare))
    monkeypatch.setattr(plan, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(plan, "READ", plan.Reading())
    return s

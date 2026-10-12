"""What crew assumes of git when gather.py reads a kit, each case naming what assumes it: Stages reads a unit's
stage from the changes main and its bolt's branch hold, its place, and its fix (state.2, plan.12; crew bolts, crew
board and crew sites read every host's kits through gather.kit, once per host)."""
import os

import gather


def change(root, name, done=0, total=2):
    """An OpenSpec change as a construct stage commits it: proposal, design, one spec and its tasks."""
    c = root / "openspec" / "changes" / name
    (c / "specs" / "x").mkdir(parents=True, exist_ok=True)
    (c / "proposal.md").write_text(f"# Proposal\n\n## Touches\n\n```\nsrc/{name}/**\n```\n")
    (c / "design.md").write_text("# Design\n")
    (c / "specs" / "x" / "spec.md").write_text("## ADDED Requirements\n")
    (c / "tasks.md").write_text("## 1. Work\n\n" + "".join(f"- [{'x' if i < done else ' '}] 1.{i + 1} task\n" for i in range(total)))
    return f"openspec/changes/{name}"


class Kit:
    """A kit laid out as crew lays it out: <dir>/main, the bolt's worktree under bolts/, each unit's and fix's under places/."""

    def __init__(self, repo, tmp_path):
        self.repo, self.dir = repo, tmp_path / "kit"
        repo.commit("chore: start", {"README.md": "r\n"})
        repo.git("branch", "bolt/te")
        repo.git("worktree", "add", "-q", str(self.dir / "bolts" / "te"), "bolt/te")

    def place(self, unit, bolt="te", prefix="unit"):
        path = self.dir / "places" / unit.replace("/", "--")
        self.repo.git("worktree", "add", "-q", "--track", "-b", f"{prefix}/{unit}", str(path), f"bolt/{bolt}")
        return path

    def commit(self, path, message):
        self.repo.git("-C", str(path), "add", "-A")
        self.repo.git("-C", str(path), "commit", "-q", "-m", message)

    def read(self):
        return gather.kit({"main": str(self.repo.path), "dir": str(self.dir), "bolts": ["te"]})


def test_main_holds_its_open_and_archived_changes_an_archived_one_without_its_date(repo, tmp_path):
    """Stages: a unit whose change main holds, open or archived, has landed (the archive at merge, record 0006)."""
    k = Kit(repo, tmp_path)
    change(repo.path, "open-one")
    os.makedirs(repo.path / "openspec" / "changes" / "archive")
    change(repo.path, "archived")
    os.rename(repo.path / "openspec/changes/archived", repo.path / "openspec/changes/archive/2026-09-01-archived")
    k.commit(repo.path, "feat: two changes on main")
    assert k.read()["main"] == ["archived", "open-one"]


def test_a_unit_squashed_into_its_bolt_with_its_place_and_branch_gone_is_read_from_the_bolts_tree(repo, tmp_path):
    """Stages: a unit merged the way wt merge squashes by default reads merged, since the bolt's tree holds its change."""
    k = Kit(repo, tmp_path)
    p = k.place("squashed")
    change(p, "squashed", 2, 2)
    k.commit(p, "feat(squashed): one")
    (p / "two").write_text("2\n")
    k.commit(p, "feat(squashed): two")
    b = k.dir / "bolts" / "te"
    repo.git("-C", str(b), "merge", "-q", "--squash", "unit/squashed")
    repo.git("-C", str(b), "commit", "-q", "-m", "feat(squashed)")
    repo.git("worktree", "remove", str(p))
    repo.git("branch", "-qD", "unit/squashed")
    got = k.read()
    assert got["bolts"]["te"]["changes"] == ["squashed"] and got["places"] == {}
    assert got["bolts"]["te"]["worktree"] == str(b) and got["bolts"]["te"]["head"] == repo.git("rev-parse", "bolt/te")


def test_a_place_names_its_bolt_by_its_upstream_and_its_tasks_and_planning_from_its_change(repo, tmp_path):
    """Stages: a place's tasks say code or verify; its planning, whether construct finished (plan.12's direct reading)."""
    k = Kit(repo, tmp_path)
    p = k.place("coding")
    change(p, "coding", 4, 9)
    k.commit(p, "feat(coding)")
    q = k.place("constructing")
    got = k.read()["places"]
    assert (got["coding"]["bolt"], got["coding"]["branch"], got["coding"]["tasks"], got["coding"]["planning"]) == ("te", "unit/coding", [4, 9], True)
    assert got["coding"]["path"] == os.path.realpath(p) and got["coding"]["touches"] == {"entries": ["src/coding/**"]}
    assert (got["constructing"]["tasks"], got["constructing"]["planning"]) == (None, False)
    assert got["constructing"]["head"] == repo.git("rev-parse", "bolt/te") != got["coding"]["head"]


def test_a_fix_is_listed_with_its_bolt_and_reads_merged_only_once_it_moved_and_the_bolt_holds_it(repo, tmp_path):
    """crew bolts and the board: a fix's line; carry and tidy: a fix born at the bolt's head has not merged."""
    k = Kit(repo, tmp_path)
    f = k.place("te/edge", prefix="fix")
    assert k.read()["fixes"] == [{"fix": "fix/te/edge", "path": os.path.realpath(f), "bolt": "te", "merged": False}]
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    assert k.read()["fixes"][0]["merged"] is False
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "--ff-only", "fix/te/edge")
    assert k.read()["fixes"][0]["merged"] is True


def test_a_worktree_outside_places_or_off_a_unit_or_fix_branch_is_no_place(repo, tmp_path):
    """read.4: crew reads, and so tidies, only the worktrees it made."""
    k = Kit(repo, tmp_path)
    repo.git("worktree", "add", "-q", "-b", "unit/elsewhere", str(tmp_path / "elsewhere"), "bolt/te")
    repo.git("worktree", "add", "-q", "-b", "scratch", str(k.dir / "places" / "scratch"), "bolt/te")
    got = k.read()
    assert got["places"] == {} and got["fixes"] == []

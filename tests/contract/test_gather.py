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


def test_a_place_whose_merge_archived_its_change_reads_it_from_the_archive_and_the_bolt_then_holds_it_archived(repo, tmp_path):
    """Stages and the merge's deliverable: a unit's merge archives its change first (teams.17, record 0006), so its
    place reads the archived change's tasks and Touches, still waiting to merge, and gather.archived names the change
    once the bolt holds it so, and not while the bolt holds it open."""
    k = Kit(repo, tmp_path)
    p = k.place("merging")
    change(p, "merging", 2, 2)
    k.commit(p, "feat(merging)")
    os.makedirs(p / "openspec" / "changes" / "archive")
    repo.git("-C", str(p), "mv", "openspec/changes/merging", "openspec/changes/archive/2026-10-13-merging")
    k.commit(p, "docs(openspec): archive merging")
    got = k.read()["places"]["merging"]
    assert (got["tasks"], got["planning"], got["archived"], got["open"]) == ([2, 2], True, True, [])
    assert got["touches"] == {"entries": ["src/merging/**"]}
    assert gather.archived(str(repo.path), "bolt/te") == []
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "--no-ff", "-m", "merge", "unit/merging")
    assert gather.archived(str(repo.path), "bolt/te") == ["merging"] and "merging" in gather.changes(str(repo.path), "bolt/te")


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


def test_a_chore_is_read_from_the_trailer_of_its_commits_on_main_and_each_bolt(repo, tmp_path):
    """Stages, slot_stage and tidy: a chore has merged once its bolt's history holds a commit whose `Chore:` trailer names
    it, and landed once main's does, as git parses trailers; the words in a body that is not the last paragraph are no
    trailer (plan.11, state.2)."""
    k = Kit(repo, tmp_path)
    p = k.place("bump", prefix="chore")
    (p / "pin").write_text("1\n")
    repo.git("-C", str(p), "add", "-A")
    repo.git("-C", str(p), "commit", "-q", "-m", "chore: pin the shell", "--trailer", "Chore: bump")
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "--ff-only", "chore/bump")
    repo.commit("docs: Chore: in a subject is no trailer\n\nChore: not-this-one\n\nA last paragraph of prose.")
    got = k.read()
    assert (got["chores"], got["bolts"]["te"]["chores"]) == ([], ["bump"])
    assert gather.chores(str(repo.path), "refs/heads/missing") == []


def test_a_chores_place_is_read_with_how_far_it_is_beyond_its_bolt(repo, tmp_path):
    """Stages: a chore with a place reads code until its place holds a commit beyond the bolt, and verify after; its place
    is directly in places/ as chore-<name> on chore/<name>, tracking its bolt (plan.11)."""
    k = Kit(repo, tmp_path)
    p = k.dir / "places" / "chore-bump"
    repo.git("worktree", "add", "-q", "--track", "-b", "chore/bump", str(p), "bolt/te")
    got = k.read()["chore_places"]["bump"]
    assert (got["ahead"], got["bolt"], got["branch"]) == (0, "te", "chore/bump")
    (p / "pin").write_text("1\n")
    k.commit(p, "chore: one")
    assert k.read()["chore_places"]["bump"]["ahead"] == 1
    assert "bump" not in k.read()["places"]


def test_a_chores_commits_and_their_trailers_are_read_as_its_merge_checks_them(repo, tmp_path):
    """chore_check: a chore's merge is refused for each commit beyond its bolt whose trailers do not name it, read by
    plan.CHORE_LOG and parsed by plan.chore_log (plan.11, roles.3)."""
    import plan
    k = Kit(repo, tmp_path)
    p = k.place("bump", prefix="chore")
    for i, trailer in enumerate((["--trailer", "Chore: bump"], [], ["--trailer", "Chore: other", "--trailer", "Chore: bump"])):
        (p / f"f{i}").write_text(f"{i}\n")
        repo.git("-C", str(p), "add", "-A")
        repo.git("-C", str(p), "commit", "-q", "-m", f"chore: step {i}", *trailer)
    got = plan.chore_log(repo.git(*plan.CHORE_LOG, "refs/heads/bolt/te..refs/heads/chore/bump"))
    assert [(s, names) for _, s, names in got] == [("chore: step 0", ["bump"]), ("chore: step 1", []), ("chore: step 2", ["other", "bump"])]
    assert [s for _, s in plan.untrailed(got, "bump")] == ["chore: step 1"]


def test_a_dependents_place_takes_a_chores_head_and_a_chores_own_work_leaves_out_what_it_took(repo, tmp_path):
    """run_check's and chore_check's take (plan.TAKE): a unit's place takes the head of a chore it comes after by its
    branch, chore/<name>, and a chore's place takes a unit's, printing each name and head (plan.13); a chore's own work,
    which its stage (gather.chore_place), its code's deliverable (gather.own_head) and its merge's trailer check
    (plan.CHORE_LOG) read, is its first-parent line with no merges, so what it took is never its own (plan.11)."""
    import subprocess
    import plan
    k = Kit(repo, tmp_path)
    a = k.place("a")
    (a / "a").write_text("a\n")
    k.commit(a, "feat(a): its work")
    cp = k.dir / "places" / "chore-pin"
    repo.git("worktree", "add", "-q", "--track", "-b", "chore/pin", str(cp), "bolt/te")
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(cp), "pin", "te", "unit/a"], capture_output=True, text=True)
    assert (took.returncode, took.stdout.split()) == (0, ["a", repo.git("rev-parse", "--short=7", "unit/a")])
    assert k.read()["chore_places"]["pin"]["ahead"] == 0
    assert gather.own_head(str(repo.path), "chore/pin", "te") == (None, None)
    (cp / "pin").write_text("1\n")
    repo.git("-C", str(cp), "add", "-A")
    repo.git("-C", str(cp), "commit", "-q", "-m", "chore: pin", "--trailer", "Chore: pin")
    assert k.read()["chore_places"]["pin"]["ahead"] == 1
    assert gather.own_head(str(repo.path), "chore/pin", "te")[0] == repo.git("rev-parse", "--short", "chore/pin")
    own = plan.chore_log(repo.git(*plan.CHORE_LOG, "refs/heads/bolt/te..refs/heads/chore/pin"))
    assert [(subject, names) for _, subject, names in own] == [("chore: pin", ["pin"])]
    b = k.place("b")
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(b), "b", "te", "chore/pin"], capture_output=True, text=True)
    assert (took.returncode, took.stdout.split()) == (0, ["pin", repo.git("rev-parse", "--short=7", "chore/pin")])
    repo.git("-C", str(b), "merge-base", "--is-ancestor", "chore/pin", "HEAD")

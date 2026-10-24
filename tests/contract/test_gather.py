"""What crew assumes of git when gather.py reads a kit, each case naming what assumes it: Stages reads a unit's
stage from the changes main and its bolt's branch hold, its place, and its fix (state.2, plan.12; crew bolts, crew
board and crew sites read every host's kits through gather.kit, once per host)."""
import os
import subprocess

import gather

# A kit whose bolts live on GitHub (plan.19): the policy names origin for its bolt branches.
ON_GITHUB = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'


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


def test_a_change_carried_onto_the_bolt_inside_another_units_merge_is_read_open_with_its_tasks(repo, tmp_path):
    """Stages, the slots and the tidy: a unit has merged only once its bolt holds its change archived (teams.17), so the
    bolt's read gives the changes it holds archived apart from those it holds open, with each open one's tasks as the
    bolt holds them, but a change main already holds; and the unit branch's open changes, which a merge is refused for
    carrying (gather.opened)."""
    k = Kit(repo, tmp_path)
    change(repo.path, "on-main", 1, 1)
    k.commit(repo.path, "feat: a change open on main")
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "main")
    d = k.place("d")
    change(d, "d", 1, 2)
    k.commit(d, "feat(d)")
    s = k.place("s")
    change(s, "s", 2, 2)
    k.commit(s, "feat(s)")
    repo.git("-C", str(s), "merge", "-q", "--no-ff", "-m", "merge d", "unit/d")
    assert gather.opened(str(repo.path), "unit/s") == ["d", "on-main", "s"]
    os.makedirs(s / "openspec" / "changes" / "archive", exist_ok=True)
    repo.git("-C", str(s), "mv", "openspec/changes/s", "openspec/changes/archive/2026-10-13-s")
    k.commit(s, "docs(openspec): archive s")
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "--no-ff", "-m", "merge s", "unit/s")
    bolt = k.read()["bolts"]["te"]
    assert (bolt["archived"], bolt["open"]) == (["s"], {"d": [1, 2]})


def test_places_cut_from_the_bolt_on_github_name_it_by_their_upstream(repo, tmp_path):
    """Stages through gather.bolt_of (plan.19): a unit's, a chore's and a fix's place cut from origin/bolt/<bolt> name
    that bolt, as one cut from the host's own bolt/<bolt> does, and the bolt is read from the host's own branch."""
    import subprocess
    k = Kit(repo, tmp_path)
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git")); repo.git("fetch", "-q", "origin")
    for prefix, name, path in (("unit", "u", "u"), ("chore", "c", "chore-c"), ("fix", "te/f", "te--f")):
        repo.git("worktree", "add", "-q", "--track", "-b", f"{prefix}/{name}", str(k.dir / "places" / path), "origin/bolt/te")
    got = k.read()
    assert (got["places"]["u"]["bolt"], got["chore_places"]["c"]["bolt"], got["fixes"][0]["bolt"]) == ("te", "te", "te")
    assert got["bolts"]["te"]["head"] == repo.git("rev-parse", "bolt/te")


def test_a_fix_is_listed_with_its_bolt_and_reads_merged_only_once_it_moved_and_the_bolt_holds_it(repo, tmp_path):
    """crew bolts and the board: a fix's line; carry and tidy: a fix born at the bolt's head has not merged."""
    k = Kit(repo, tmp_path)
    f = k.place("te/edge", prefix="fix")
    assert k.read()["fixes"] == [{"fix": "fix/te/edge", "path": os.path.realpath(f), "bolt": "te", "merged": False, "dropped": False,
                                  "on_main": True, "moved": False}]
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    assert k.read()["fixes"][0]["merged"] is False
    repo.git("-C", str(k.dir / "bolts" / "te"), "merge", "-q", "--ff-only", "fix/te/edge")
    assert k.read()["fixes"][0]["merged"] is True


def landed_fix(repo, k):
    """A fix with a commit of its own merged into its bolt, and the bolt landed on main and its branch deleted, as
    sluice's landing leaves it: the fix's upstream reads gone."""
    f = k.place("te/edge", prefix="fix")
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    b = k.dir / "bolts" / "te"
    repo.git("-C", str(b), "merge", "-q", "--no-ff", "-m", "merge fix", "fix/te/edge")
    repo.git("merge", "-q", "--no-ff", "-m", "land te", "bolt/te")
    repo.git("worktree", "remove", str(b))
    repo.git("branch", "-qD", "bolt/te")
    assert repo.git("for-each-ref", "--format=%(upstream:short) %(upstream:track)", "refs/heads/fix/te/edge") == "bolt/te [gone]"
    return f


def test_a_fix_whose_bolt_landed_and_whose_place_is_gone_is_read_from_its_branch(repo, tmp_path):
    """slot_stage and the tidy's sweep (teams.1, teams.3): a fix branch no worktree holds is listed in fix_branches with
    its bolt from its upstream, still named though the bolt's branch is gone, and reads on main and moved, merged no
    more with its bolt's branch gone; it is no place, so the board and the sites page, which draw places, do not see it."""
    k = Kit(repo, tmp_path)
    f = landed_fix(repo, k)
    repo.git("worktree", "remove", str(f))
    got = k.read()
    assert got["fixes"] == []
    assert got["fix_branches"] == {"fix/te/edge": {"bolt": "te", "merged": False, "on_main": True, "moved": True}}


def test_a_fix_whose_bolt_landed_with_its_place_standing_reads_on_main_and_moved(repo, tmp_path):
    """slot_stage and tidy_over (teams.1, teams.3): a fix's place carries the same facts, and its branch is not listed
    again in fix_branches."""
    k = Kit(repo, tmp_path)
    landed_fix(repo, k)
    got = k.read()
    assert [(x["fix"], x["bolt"], x["merged"], x["on_main"], x["moved"]) for x in got["fixes"]] == [("fix/te/edge", "te", False, True, True)]
    assert got["fix_branches"] == {}


def test_a_fix_tracking_its_bolt_on_github_reads_its_bolt_and_merges_at_that_ref(repo, tmp_path):
    """slot_stage, the tidy and the drop's and the merge's fix_merged (plan.19): a fix whose place was cut from
    origin/bolt/<bolt> tracks the remote-tracking branch, %(upstream:short) prints origin/bolt/<bolt>, and the fix
    reads its bolt from it and merged once that ref, where its bolt on GitHub is read, not the host's own
    bolt/<bolt>, holds its tip."""
    import subprocess
    repo.commit("chore: bolts live on GitHub", {".config/sluice.toml": ON_GITHUB})
    k = Kit(repo, tmp_path)
    origin = tmp_path / "github.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin))
    repo.git("fetch", "-q", "origin")
    f = k.dir / "places" / "fix-te--edge"
    repo.git("worktree", "add", "-q", "--track", "-b", "fix/te/edge", str(f), "origin/bolt/te")
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/fix/te/edge") == "origin/bolt/te"
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    got = k.read()["fixes"][0]
    assert (got["bolt"], got["merged"], got["on_main"]) == ("te", False, False)
    repo.git("push", "-q", "origin", "fix/te/edge:bolt/te")
    repo.git("fetch", "-q", "origin")
    got = k.read()["fixes"][0]
    assert (got["bolt"], got["merged"], got["on_main"], got["moved"]) == ("te", True, False, True)
    assert gather.fix_merged(str(repo.path), "fix/te/edge", "te") is True
    assert repo.git("rev-parse", "bolt/te") != repo.git("rev-parse", "fix/te/edge")


def test_a_fix_just_cut_at_mains_commit_is_on_main_and_has_not_moved(repo, tmp_path):
    """slot_stage (teams.1): a fix cut from its bolt at a commit main holds reads on main, but has not moved, so it is in
    flight while its bolt is planned."""
    k = Kit(repo, tmp_path)
    k.place("te/edge", prefix="fix")
    got = k.read()["fixes"][0]
    assert (got["merged"], got["on_main"], got["moved"]) == (False, True, False)
    assert gather.bolt_ref("bolt/te") == ("te", "refs/heads/bolt/te")
    assert gather.bolt_ref("origin/bolt/te") == ("te", "refs/remotes/origin/bolt/te")
    assert gather.bolt_ref("origin/main") == gather.bolt_ref("") == gather.bolt_ref("bolt/") == (None, None)


def test_a_fix_whose_bolt_has_landed_and_its_branch_gone_reads_unmerged_and_git_says_nothing(repo, tmp_path, capfd):
    """crew plan approve and every read of the kits: a fix's place left standing after its bolt landed tracks a branch
    that is gone, and git's fatal for it is never printed (signal 2026-10-13-swancloud-planner-6eabf8e7/02)."""
    k = Kit(repo, tmp_path)
    f = k.place("te/edge", prefix="fix")
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    repo.git("worktree", "remove", str(k.dir / "bolts" / "te"))
    repo.git("branch", "-qD", "bolt/te")
    capfd.readouterr()
    got = k.read()
    assert got["fixes"][0]["merged"] is False and got["bolts"]["te"]["exists"] is False
    assert capfd.readouterr().err == ""


def test_a_fix_its_conductor_dropped_reads_dropped_while_its_place_still_stands(repo, tmp_path):
    """plan.fixes_in_flight (record 0028): crew fix --drop marks the branch dropped in the kit's git config, and a fix
    so marked holds no landing though the tidy has not yet removed its place."""
    k = Kit(repo, tmp_path)
    k.place("te/edge", prefix="fix")
    repo.git("config", "branch.fix/te/edge.crew", "dropped")
    assert k.read()["fixes"][0]["dropped"] is True


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
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(cp), "pin", "refs/heads/bolt/te", "unit/a"], capture_output=True, text=True)
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
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(b), "b", "refs/heads/bolt/te", "chore/pin"], capture_output=True, text=True)
    assert (took.returncode, took.stdout.split()) == (0, ["pin", repo.git("rev-parse", "--short=7", "chore/pin")])
    repo.git("-C", str(b), "merge-base", "--is-ancestor", "chore/pin", "HEAD")


def test_a_branchs_commits_are_its_first_parent_line_newest_first_and_a_chores_its_own_beyond_its_bolt(repo, tmp_path, monkeypatch):
    """A stuck report's commits (plan.stuck_said, teams.4): gather.since lists a branch's first-parent line from its
    head with each commit's short sha, committer time and subject, newest first, so stuck_said can keep those made since
    the stage began; another unit's work a place merged in is not listed, only the merge; a chore's, read beyond its
    bolt, leaves out what its place took (plan.11); a branch git can't read is None."""
    k = Kit(repo, tmp_path)
    p, o = k.place("a"), k.place("other")
    (o / "o").write_text("o\n")
    k.commit(o, "feat(other): its work")
    for at, name in (("2026-10-23T01:00:00+00:00", "before"), ("2026-10-23T02:10:00+00:00", "first"), ("2026-10-23T02:20:00+00:00", "second")):
        monkeypatch.setenv("GIT_COMMITTER_DATE", at)
        (p / name).write_text(f"{name}\n")
        k.commit(p, f"feat(a): {name}")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2026-10-23T02:30:00+00:00")
    repo.git("-C", str(p), "merge", "-q", "--no-edit", "unit/other")
    sha = lambda n: repo.git("rev-parse", "--short", f"unit/a~{n}")
    assert gather.since(str(repo.path), "refs/heads/unit/a")[:4] == [
        (sha(0), "2026-10-23T02:30:00Z", "Merge branch 'unit/other' into unit/a"),
        (sha(1), "2026-10-23T02:20:00Z", "feat(a): second"),
        (sha(2), "2026-10-23T02:10:00Z", "feat(a): first"),
        (sha(3), "2026-10-23T01:00:00Z", "feat(a): before")]
    cp = k.dir / "places" / "chore-pin"
    repo.git("worktree", "add", "-q", "--track", "-b", "chore/pin", str(cp), "unit/a")
    (cp / "pin").write_text("1\n")
    k.commit(cp, "chore: pin")
    assert [s for _, _, s in gather.since(str(repo.path), "refs/heads/chore/pin", "refs/heads/unit/a")] == ["chore: pin"]
    assert gather.since(str(repo.path), "refs/heads/unit/none") is None


def test_a_kit_on_github_reads_what_has_landed_from_origin_main_not_the_hosts_own_main(repo, tmp_path):
    """Stages and the tidy through gather.kit (plan.18): a kit with an origin remote reads its landed changes and chores
    at origin/main as the host last fetched it, which a landing elsewhere moved and the host's own main lags; what
    only the host's own main holds has not landed. A kit with no origin reads its own main."""
    import subprocess
    k = Kit(repo, tmp_path)
    origin = tmp_path / "github.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin))
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", str(origin), str(other)], check=True)
    change(other, "landed-elsewhere")
    subprocess.run(["git", "-C", str(other), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(other), "commit", "-qm", "chore(land): #1 bolt/x"], check=True)
    subprocess.run(["git", "-C", str(other), "push", "-q", "origin", "main"], check=True)
    change(repo.path, "only-here")
    k.commit(repo.path, "feat: only on the host's own main")
    repo.git("fetch", "-q", "origin")
    assert k.read()["main"] == ["landed-elsewhere"]
    repo.git("remote", "remove", "origin")
    assert k.read()["main"] == ["only-here"]


def test_a_kit_whose_main_now_is_missing_is_not_read(repo, tmp_path):
    """gather.kit (read.1): a kit with an origin that has no origin/main is named unread, never read at its own main."""
    k = Kit(repo, tmp_path)
    repo.git("remote", "add", "origin", str(tmp_path / "never-fetched.git"))
    got = k.read()
    assert got["ok"] is False and "has no origin/main to read" in got["error"]


def on_github(repo, tmp_path, policy=ON_GITHUB):
    """A kit whose main and bolt/te carry policy, and its GitHub: a bare clone as origin, fetched; and a clone of
    GitHub on bolt/te, where sluice lands the bolt's merges from another host."""
    if policy is not None:
        repo.commit("chore: the kit's policy", {".config/sluice.toml": policy})
    k = Kit(repo, tmp_path)
    origin = tmp_path / "github.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin))
    repo.git("fetch", "-q", "origin")
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "bolt/te", str(origin), str(other)], check=True)
    return k, type(repo)(other)


def landed_on_github(other, files, message):
    """A merge sluice lands on GitHub's bolt/te, pushed from the other clone, its verdict a trailer on its commit."""
    other.commit(message, files)
    other.git("push", "-q", "origin", "HEAD:bolt/te")
    return other.git("rev-parse", "HEAD")


def test_a_merge_landed_on_github_is_read_there_with_the_hosts_copy_left_behind(repo, tmp_path):
    """Stages, crew bolts and the landing card (bolt-plan "A merge landed on GitHub while the host's copy stayed
    behind"): a bolt on GitHub is read at origin/bolt/<bolt> as the host last fetched it, its archived change, its
    chore, its head and the verdict at that head, never at the host's own bolt/<bolt>, sluice's copy."""
    k, other = on_github(repo, tmp_path)
    before = repo.git("rev-parse", "bolt/te")
    other.commit("chore: pin\n\nChore: c", {"pin": "1\n"})
    archive = "openspec/changes/archive/2026-10-23-u"
    head = landed_on_github(other, {f"{archive}/proposal.md": "# u\n", f"{archive}/tasks.md": "- [x] 1.1 t\n"},
                            "Merge unit/u into bolt/te\n\nSluice-Result: passed (9 run, 0 replayed)")
    repo.git("fetch", "-q", "origin")
    got = k.read()["bolts"]["te"]
    assert repo.git("rev-parse", "bolt/te") == before != head
    assert (got["at"], got["exists"], got["head"], got["verdict"]) == ("origin/bolt/te", True, head, "passed (9 run, 0 replayed)")
    assert (got["archived"], got["chores"], "u" in got["changes"]) == (["u"], ["c"], True)
    assert gather.bolt_read(str(repo.path), "te") == ("refs/remotes/origin/bolt/te", None)


def test_a_chores_place_and_a_fix_beside_a_bolt_on_github_are_read_against_githubs_copy(repo, tmp_path):
    """Stages and slot_stage (bolt-plan "A chore's place and a fix beside a bolt on GitHub"): a chore's place one
    commit of its own beyond GitHub's bolt reads ahead 1, which the host's copy two commits behind would read 3, and
    its own head is that commit (gather.own_head); a fix tracking the host's bolt/<bolt> whose tip only GitHub's bolt
    holds reads merged."""
    k, other = on_github(repo, tmp_path)
    f = k.place("te/edge", prefix="fix")
    (f / "edge").write_text("e\n")
    k.commit(f, "fix(te): the edge")
    repo.git("push", "-q", "origin", "fix/te/edge:bolt/te")
    other.git("pull", "-q", "--ff-only", "origin", "bolt/te")
    landed_on_github(other, {"one": "1\n"}, "feat: one")
    repo.git("fetch", "-q", "origin")
    cp = k.dir / "places" / "chore-bump"
    repo.git("worktree", "add", "-q", "--track", "-b", "chore/bump", str(cp), "origin/bolt/te")
    (cp / "pin").write_text("1\n")
    k.commit(cp, "chore: pin")
    got = k.read()
    assert repo.git("rev-list", "--count", "bolt/te..chore/bump") == "3"
    assert got["chore_places"]["bump"]["ahead"] == 1
    assert gather.own_head(str(repo.path), "chore/bump", "te")[0] == repo.git("rev-parse", "--short", "chore/bump")
    assert (got["fixes"][0]["bolt"], got["fixes"][0]["merged"]) == ("te", True)
    assert gather.fix_merged(str(repo.path), "fix/te/edge", "te") is True
    assert subprocess.run(["git", "-C", str(repo.path), "merge-base", "--is-ancestor", "fix/te/edge", "bolt/te"]).returncode == 1


def test_a_bolt_kept_on_its_host_is_read_at_its_own_branch_with_the_merges_github_lacks(repo, tmp_path):
    """Stages (bolt-plan "A bolt kept on its host"): a bolt made before gives went through sluice, whose copy on GitHub
    a refused landing's pull request pushed before the merge that brought its policy naming origin, is read at the
    host's bolt/<bolt>, where its later merges are."""
    k, _ = on_github(repo, tmp_path, policy=None)
    b = k.dir / "bolts" / "te"
    (b / ".config").mkdir()
    (b / ".config" / "sluice.toml").write_text(ON_GITHUB)
    k.commit(b, "Merge main into bolt/te")
    got = k.read()["bolts"]["te"]
    assert (got["at"], got["head"]) == ("bolt/te", repo.git("rev-parse", "bolt/te"))
    assert repo.git("rev-parse", "origin/bolt/te") != got["head"]


def test_a_bolt_whose_policy_on_github_is_not_toml_is_read_nowhere(repo, tmp_path):
    """Stages (bolt-plan "A policy crew can't read", read.1): the bolt is marked missing with why, naming the file and the
    bolt, and nothing is read from the host's bolt/<bolt>."""
    k, other = on_github(repo, tmp_path)
    landed_on_github(other, {".config/sluice.toml": "[branches\n"}, "chore: a broken policy")
    repo.git("fetch", "-q", "origin")
    got = k.read()["bolts"]["te"]
    assert (got["exists"], got["at"], got["head"], got["changes"]) == (False, None, None, [])
    assert got["error"].startswith(".config/sluice.toml at origin/bolt/te is not TOML, so crew can't read bolt te: ")


def test_a_read_that_asks_a_fetch_reads_what_github_holds_now_and_every_other_as_last_fetched(repo, tmp_path):
    """crew bolts, a give's proven check (plan.survey with fetch) and every other read (plan.18, plan.19): a request
    with fetch runs `git fetch -q origin` in the kit's main checkout first and reads a merge pushed to GitHub's bolt
    since; one without reads the bolt as the host last fetched it; a fetch that fails reads the kit unread, naming
    GitHub and git's words, and nothing from the host's copy."""
    k, other = on_github(repo, tmp_path)
    head = landed_on_github(other, {"one": "1\n"}, "Merge unit/u into bolt/te\n\nSluice-Result: passed (9 run, 0 replayed)")
    req = {"main": str(repo.path), "dir": str(k.dir), "bolts": ["te"]}
    assert gather.kit(req)["bolts"]["te"]["head"] == repo.git("rev-parse", "origin/bolt/te") != head
    got = gather.kit(req, fetch=True)["bolts"]["te"]
    assert (got["head"], got["verdict"]) == (head, "passed (9 run, 0 replayed)")
    repo.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    got = gather.kit(req, fetch=True)
    assert got["ok"] is False and got["error"].startswith(f"cannot fetch {repo.path} from GitHub: ")
    assert "gone.git" in got["error"]
    assert gather.fetched(str(repo.path)).startswith("fatal:")
    repo.git("remote", "remove", "origin")
    assert gather.fetched(str(repo.path)) is None

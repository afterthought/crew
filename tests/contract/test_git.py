"""What crew assumes of git, each case naming what assumes it."""
import base64
import os
import shlex
import shutil
import subprocess
import time

import pytest


def test_a_first_parent_log_leaves_out_a_siblings_work_taken_by_a_merge(repo):
    """plan.undeclared (teams.12): a unit's own paths are its first-parent commits beyond its bolt; a sibling unit's
    work its place took by a merge, to settle a forecast, is behind the merge's second parent."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt")
    repo.git("checkout", "-q", "-b", "sibling", "bolt")
    repo.commit("feat(sibling)", {"plugin/lib/plan.py": "sibling\n"})
    repo.git("checkout", "-q", "-b", "unit", "bolt")
    repo.commit("feat(unit)", {"docs/unit.md": "unit\n"})
    repo.git("merge", "-q", "--no-ff", "sibling", "-m", "chore: take sibling's work")
    mine = repo.git("log", "--format=", "--name-only", "--no-merges", "--first-parent", "unit", "--not", "refs/heads/bolt")
    every = repo.git("log", "--format=", "--name-only", "--no-merges", "unit", "--not", "refs/heads/bolt")
    assert set(mine.split()) == {"docs/unit.md"}
    assert set(every.split()) == {"docs/unit.md", "plugin/lib/plan.py"}


def test_merge_tree_names_the_conflicting_paths_and_writes_no_ref(repo):
    """plan's forecast (teams.12): git merge-tree --write-tree --name-only exits 1 on a conflict and lists the
    conflicting paths after the tree, and moves no ref."""
    repo.commit("main", {"a": "1\n"})
    repo.git("checkout", "-q", "-b", "one")
    repo.commit("one", {"a": "one\n"})
    repo.git("checkout", "-q", "-b", "two", "main")
    repo.commit("two", {"a": "two\n"})
    refs = repo.git("for-each-ref")
    r = subprocess.run(["git", "-C", str(repo.path), "merge-tree", "--write-tree", "--name-only", "one", "two"],
                       capture_output=True, text=True)
    assert r.returncode == 1
    lines = r.stdout.splitlines()
    assert lines[1] == "a"
    assert repo.git("for-each-ref") == refs


def dependency_rebased(repo, own=None):
    """A dependency a and a dependent b whose place took a's head and added its own commit (own, else one of b's own
    files); then the bolt moves, a is rebased onto it, new hashes, and its settle revises a's own work. Returns the
    head b took, which crew records as the construct's Took."""
    repo.commit("main", {"shared.txt": "one\ntwo\nthree\n"})
    repo.git("branch", "bolt")
    repo.git("checkout", "-q", "-b", "a", "bolt")
    took = repo.commit("feat(a): its change", {"a/design.md": "z\n", "shared.txt": "one\ntwo, as a has it\nthree\n"})
    repo.git("checkout", "-q", "-b", "b", "a")
    repo.commit("feat(b): its change", own or {"b/design.md": "y\n"})
    repo.git("checkout", "-q", "bolt")
    repo.commit("feat: the bolt's own", {"bolt.txt": "the bolt\n"})
    repo.git("checkout", "-q", "a")
    repo.git("rebase", "-q", "bolt")
    repo.commit("fix(a): settled on the bolt", {"a/design.md": "z, as it stands on the bolt\n",
                                                "shared.txt": "one\ntwo, as a has it, settled\nthree\n"})
    assert repo.git("merge-base", "a", "b") != took
    return took


def test_merge_tree_from_the_head_a_dependent_took_leaves_out_its_dependencys_own_work(repo):
    """plan.forecasts_due through plan.merge_tree (teams.12, plan.13): from their merge base, the bolt both started on,
    a dependent carrying its dependency's old commits conflicts with the dependency rebased and settled on the
    dependency's own files; git merge-tree --merge-base=<the head it took> (git 2.40+) compares only what the dependent
    adds beyond it, and finds no conflict."""
    import plan
    took = dependency_rebased(repo)
    assert plan.merge_tree(str(repo.path), "a", "b") == ["a/design.md", "shared.txt"]
    assert plan.merge_tree(str(repo.path), "a", "b", took) == []


def test_merge_tree_from_the_head_a_dependent_took_still_forecasts_its_own_overlap(repo):
    """plan.forecasts_due through plan.merge_tree (teams.12): a dependent whose own commit changes the line its
    dependency's settle rewrote is forecast to conflict there from the head it took, and only there."""
    import plan
    took = dependency_rebased(repo, own={"shared.txt": "one\ntwo, as b has it\nthree\n"})
    assert plan.merge_tree(str(repo.path), "a", "b", took) == ["shared.txt"]


def rebase(repo, tmp_path, unit, src, to, upstream=None):
    """plan.REBASE as crew unit move runs it in the unit's place: <place> <from bolt> <to bolt> <unit> <kind> <the
    upstream of the bolt it moves to>, bolt/<to> unless given."""
    import plan
    return subprocess.run(["bash", "-c", plan.REBASE, "crew", str(tmp_path / "place"), src, to, unit, "unit", upstream or f"bolt/{to}"],
                          capture_output=True, text=True)


def test_a_move_rebases_the_units_own_commits_onto_the_new_bolt_and_tracks_it(repo, tmp_path):
    """plan.op_unit_move: the unit's commits beyond its old bolt go onto the new bolt, which its branch then tracks,
    the old bolt's commits dropping out; the head it was at is printed for the undo."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/te"); repo.git("branch", "bolt/cp")
    repo.git("checkout", "-q", "bolt/te"); repo.commit("feat: te's own", {"te": "1\n"})
    repo.git("worktree", "add", "-q", "--track", "-b", "unit/c", str(tmp_path / "place"), "bolt/te")
    subprocess.run(["git", "-C", str(tmp_path / "place"), "commit", "-q", "--allow-empty", "-m", "feat(c): its own"], check=True)
    orig = repo.git("rev-parse", "unit/c")
    r = rebase(repo, tmp_path, "c", "te", "cp")
    assert r.returncode == 0 and r.stdout.strip() == orig
    assert repo.git("log", "--format=%s", "bolt/cp..unit/c") == "feat(c): its own"
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/c") == "bolt/cp"


def test_a_move_whose_rebase_conflicts_leaves_the_branch_and_place_as_they_were(repo, tmp_path):
    """plan.op_unit_move: a rebase that conflicts is aborted, exit 3, so the move is abandoned and the plan unchanged."""
    repo.commit("main", {"same": "1\n"})
    repo.git("branch", "bolt/te"); repo.git("branch", "bolt/cp")
    repo.git("checkout", "-q", "bolt/cp"); repo.commit("feat: cp's way", {"same": "cp\n"})
    repo.git("worktree", "add", "-q", "--track", "-b", "unit/d", str(tmp_path / "place"), "bolt/te")
    (tmp_path / "place" / "same").write_text("d\n")
    subprocess.run(["git", "-C", str(tmp_path / "place"), "commit", "-qam", "feat(d): d's way"], check=True)
    tip = repo.git("rev-parse", "unit/d")
    r = rebase(repo, tmp_path, "d", "te", "cp")
    assert r.returncode == 3
    assert repo.git("rev-parse", "unit/d") == tip
    assert subprocess.run(["git", "-C", str(tmp_path / "place"), "status", "--porcelain"], capture_output=True, text=True).stdout == ""


def test_a_unit_moved_to_a_bolt_on_github_tracks_it_there(repo, tmp_path):
    """plan.op_unit_move through REBASE and bolt_upstream (plan.19): a unit moved to a bolt on GitHub tracks
    origin/bolt/<bolt>, as a place cut from it does."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/te"); repo.git("branch", "bolt/cp")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git")); repo.git("fetch", "-q", "origin")
    repo.git("worktree", "add", "-q", "--track", "-b", "unit/c", str(tmp_path / "place"), "origin/bolt/te")
    r = rebase(repo, tmp_path, "c", "te", "cp", "origin/bolt/cp")
    assert r.returncode == 0, r.stderr
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/c") == "origin/bolt/cp"


def bolt_on(repo, tmp_path, remote):
    """A kit whose bolt/b names the remote for its bolts in its policy at the tip (or none), with GitHub's bolt/b one
    commit ahead of the host's own, pushed from another clone, as a merge sluice landed from another host leaves it."""
    policy = '[branches."bolt/*"]\nrequired = ["#check-full"]\n' + (f'remote = "{remote}"\n' if remote else "")
    repo.commit("main", {".config/sluice.toml": policy})
    repo.git("branch", "bolt/b")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git")); repo.git("fetch", "-q", "origin")
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "bolt/b", str(tmp_path / "github.git"), str(other)], check=True)
    (other / "landed").write_text("from another host\n")
    subprocess.run(["git", "-C", str(other), "add", "landed"], check=True)
    subprocess.run(["git", "-C", str(other), "commit", "-qm", "chore(land): #1 unit/x"], check=True)
    subprocess.run(["git", "-C", str(other), "push", "-q", "origin", "bolt/b"], check=True)
    return subprocess.run(["git", "-C", str(other), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def cut(repo, tmp_path, unit, bolt="b"):
    """plan.make_place's PLACE, as it runs it: first with no base, saying where the bolt lives, then with the base
    kit.place_base chooses from that."""
    import kit
    run = lambda base: script("PLACE", str(repo.path), str(tmp_path / "places" / unit), f"unit/{unit}", bolt, base, kit.DECLARATION).stdout
    said = run("")
    assert "GITDIR=" not in said
    return run(kit.place_base(said, bolt))


def test_a_place_of_a_bolt_on_github_is_cut_from_it_there_after_a_fetch_and_tracks_it(repo, tmp_path):
    """plan.make_place through PLACE (plan.19): a unit's place of a bolt whose policy names origin is cut from
    origin/bolt/<bolt> after a fetch, tracking it, and holds the merge landed there from another host, which the host's
    own bolt/<bolt> lags."""
    import kit
    landed = bolt_on(repo, tmp_path, "origin")
    said = cut(repo, tmp_path, "x")
    assert kit.place_said(said, "b")[0]
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/x") == "origin/bolt/b"
    assert repo.git("rev-parse", "unit/x") == landed != repo.git("rev-parse", "bolt/b")


def test_a_place_of_a_bolt_made_before_is_cut_from_the_hosts_own_branch_with_no_fetch(repo, tmp_path):
    """plan.make_place through PLACE (plan.19, bolt-teams "A place of a bolt made before"): a bolt whose tip's policy
    names no remote is cut from the host's own bolt/<bolt>, tracking it, and nothing is fetched for it."""
    landed = bolt_on(repo, tmp_path, None)
    repo.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))  # a fetch would fail
    cut(repo, tmp_path, "x")
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/x") == "bolt/b"
    assert repo.git("rev-parse", "unit/x") == repo.git("rev-parse", "bolt/b") == repo.git("rev-parse", "origin/bolt/b") != landed


def test_a_place_of_a_bolt_github_does_not_have_is_not_made_and_the_fetch_is_named(repo, tmp_path):
    """plan.make_place through PLACE (bolt-teams "The bolt on GitHub cannot be fetched", read.1): a fetch that fails, as
    when GitHub has no bolt/<bolt>, makes no place, and crew names the bolt and git's words."""
    import kit
    import pytest
    from crew import Refusal
    bolt_on(repo, tmp_path, "origin")
    subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "branch", "-q", "-D", "bolt/b"], check=True)
    said = cut(repo, tmp_path, "x")
    with pytest.raises(Refusal, match=r"^no place is made: crew cannot fetch bolt/b from GitHub to cut it from: .*bolt/b"):
        kit.place_said(said, "b")
    assert not (tmp_path / "places" / "x").exists()
    assert subprocess.run(["git", "-C", str(repo.path), "rev-parse", "--verify", "-q", "unit/x"], capture_output=True).returncode == 1


def split_kit(repo, tmp_path, merges):
    """A kit whose bolt/b is on a bare GitHub stand-in as the host's was when it was pushed there, then took the given
    number of merges on the host alone, as a legacy bolt split by an older push stands."""
    repo.commit("chore: start", {"README.md": "r\n"})
    repo.git("branch", "bolt/b")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git"))
    for n in range(merges):
        repo.git("checkout", "-q", "-b", f"unit/u{n}", "bolt/b")
        repo.commit(f"feat: u{n}", {f"u{n}": "u\n"})
        repo.git("checkout", "-q", "bolt/b")
        repo.git("merge", "-q", "--no-ff", "-m", f"chore(land): #{n} unit/u{n}", f"unit/u{n}")
    repo.git("checkout", "-q", "main")
    return repo.git("rev-parse", "bolt/b")


def split_of(repo, remote="origin"):
    """plan.BOLT_SPLIT in the kit's main checkout, as bolt_split_check runs it, and kit.bolt_split's reading of it."""
    import kit
    r = script("BOLT_SPLIT", str(repo.path), "b", remote)
    assert r.returncode == 0, r.stderr
    return r.stdout, kit.bolt_split(r.stdout, "b")


def test_a_bolt_whose_host_tip_github_lacks_is_split_by_the_merges_it_lacks(repo, tmp_path):
    """plan.split_refusal through BOLT_SPLIT (plan.19, bolt-teams "A merge into a split bolt"): the host's bolt/b two
    merges ahead of GitHub's, fetched once into origin/bolt/b, is not held there, and the two merges are counted."""
    tip = split_kit(repo, tmp_path, 2)
    out, f = split_of(repo)
    there = subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-parse", "bolt/b"], capture_output=True, text=True).stdout.strip()
    assert "HELD=no" in out and "MERGES=2" in out
    assert f == dict(local=tip, there=there, held="no", merges=2, read=None)
    assert repo.git("rev-parse", "origin/bolt/b") == there


def test_a_bolt_github_holds_at_the_hosts_tip_or_beyond_is_not_split(repo, tmp_path):
    """plan.split_refusal through BOLT_SPLIT (bolt-teams "GitHub's copy holds the host's tip"): GitHub's bolt/b at the
    host's tip, or ahead of it with a merge sluice landed there from another host, holds the host's tip."""
    tip = split_kit(repo, tmp_path, 1)
    repo.git("push", "-q", "origin", "bolt/b")
    out, f = split_of(repo)
    assert "HELD=yes" in out and f["held"] == "yes" and f["there"] == tip
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "bolt/b", str(tmp_path / "github.git"), str(other)], check=True)
    subprocess.run(["git", "-C", str(other), "commit", "-q", "--allow-empty", "-m", "chore(land): #2 unit/x"], check=True)
    subprocess.run(["git", "-C", str(other), "push", "-q", "origin", "bolt/b"], check=True)
    out, f = split_of(repo)
    assert "HELD=yes" in out and f["held"] == "yes" and f["there"] != tip and f["merges"] == 0


def test_a_bolt_github_has_no_copy_of_says_so_and_fetches_nothing(repo, tmp_path):
    """plan.split_refusal through BOLT_SPLIT (bolt-teams "GitHub has no copy"): `git ls-remote --exit-code` exits 2 for
    a ref the remote lacks, which BOLT_SPLIT prints as THERE=-, fetching nothing."""
    split_kit(repo, tmp_path, 1)
    subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "branch", "-q", "-D", "bolt/b"], check=True)
    assert subprocess.run(["git", "-C", str(repo.path), "ls-remote", "--exit-code", "origin", "refs/heads/bolt/b"],
                          capture_output=True).returncode == 2
    out, f = split_of(repo)
    assert out.strip() == "THERE=-" and f["there"] == "-" and f["read"] is None
    assert subprocess.run(["git", "-C", str(repo.path), "rev-parse", "--verify", "-q", "origin/bolt/b"], capture_output=True).returncode == 1


def test_a_bolt_whose_remote_cannot_be_read_gives_gits_words(repo, tmp_path):
    """plan.split_refusal through BOLT_SPLIT (bolt-teams "GitHub's copy cannot be read", read.1): a remote whose URL does
    not resolve exits neither 0 nor 2, and BOLT_SPLIT prints git's words on one line as READ."""
    split_kit(repo, tmp_path, 1)
    repo.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    out, f = split_of(repo)
    assert out.startswith("READ=") and len(out.strip().splitlines()) == 1
    assert "gone.git" in f["read"] and f["there"] is None


def found_of(repo, remote="origin"):
    """plan.BOLT_FOUND in the kit's main checkout, as bolt_give runs it once sluice refused to make bolt/b, and
    kit.bolt_found's reading of it."""
    import kit
    r = script("BOLT_FOUND", str(repo.path), "b", remote)
    assert r.returncode == 0, r.stderr
    return r.stdout, kit.bolt_found(r.stdout, "b")


def test_a_bolt_a_give_left_at_main_on_github_is_found_there_at_mains_commit(repo, tmp_path):
    """plan.made_said through BOLT_FOUND (plan.19): bolt/b on a bare GitHub stand-in at its main's commit, and the
    host's own at the same, as sluice's create leaves them when the give fails after it, read by one ls-remote for the
    bolt and main beside the host's own ref; the host's own gone reads as None."""
    head = repo.commit("chore: start", {"README.md": "r\n"})
    repo.git("branch", "bolt/b")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git"))
    repo.commit("feat: the host's main moves on", {"x": "x\n"})
    _, f = found_of(repo)
    assert f == dict(own=head, there=head, main=head, read=None)
    repo.git("branch", "-q", "-D", "bolt/b")
    assert found_of(repo)[1]["own"] is None


def test_a_bolt_github_has_no_copy_of_is_found_nowhere_there(repo, tmp_path):
    """plan.made_said through BOLT_FOUND: a remote that lacks bolt/b gives THERE=-, read as None beside its main."""
    head = repo.commit("chore: start", {"README.md": "r\n"})
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(tmp_path / "github.git")], check=True)
    repo.git("remote", "add", "origin", str(tmp_path / "github.git"))
    out, f = found_of(repo)
    assert "THERE=-" in out and f == dict(own=None, there=None, main=head, read=None)


def test_a_bolt_whose_remote_cannot_be_asked_is_found_with_gits_words(repo, tmp_path):
    """plan.made_said through BOLT_FOUND (read.1): a remote whose URL does not resolve gives git's words on one line as
    READ, after the host's own ref."""
    repo.commit("chore: start", {"README.md": "r\n"})
    repo.git("remote", "add", "origin", str(tmp_path / "gone.git"))
    out, f = found_of(repo)
    assert out.splitlines()[1].startswith("READ=") and len(out.strip().splitlines()) == 2
    assert "gone.git" in f["read"] and f["there"] is None


def onto(place, bolt, *heads):
    """plan.ONTO as rebase_dependents runs it in a dependent's place: <place> <the bolt's ref> [<head left out>...]."""
    import plan
    return subprocess.run(["bash", "-c", plan.ONTO, "crew", str(place), bolt, *heads], capture_output=True, text=True)


def settled_and_merged(repo, tmp_path, moved=False, own=None):
    """unit/a's change, and unit/b's place, which took a's head as crew's take does, by a merge, a fast-forward unless
    the bolt moved after a's place was made (moved), and added a commit of its own (own, else a file of b's own); then
    the bolt changes a's line,
    and a's settle rebases a onto it, resolving the line and revising a's design in the same commit, and a merges.
    Returns b's place and the head it took, which crew records as the construct's Took."""
    repo.commit("main", {"shared.txt": "one\ntwo\nthree\n", "f": "f\n"})
    repo.git("branch", "bolt/t")
    repo.git("checkout", "-q", "-b", "unit/a", "bolt/t")
    took = repo.commit("feat(a): its change", {"a/design.md": "z\n", "shared.txt": "one\ntwo, as a has it\nthree\n"})
    if moved:
        repo.git("checkout", "-q", "bolt/t")
        repo.commit("feat(x): its line", {"f": "x\n"})
    place = tmp_path / "place"
    repo.git("worktree", "add", "-q", "-b", "unit/b", str(place), "bolt/t")
    in_place = lambda *a: subprocess.run(["git", "-C", str(place), *a], check=True, capture_output=True)
    in_place("merge", "-q", "--no-edit", "-m", "chore(b): build on a as it stands", "unit/a")
    for name, text in (own or {"b.md": "b\n"}).items():
        (place / name).write_text(text)
        in_place("add", name)
    in_place("commit", "-qm", "feat(b): its own")
    repo.git("checkout", "-q", "bolt/t")
    repo.commit("feat: the bolt's line",
                {"shared.txt": "one\ntwo, as the bolt has it\nthree\n", **({"f": "x, then y\n"} if moved else {})})
    repo.git("checkout", "-q", "unit/a")
    assert subprocess.run(["git", "-C", str(repo.path), "rebase", "-q", "bolt/t"], capture_output=True).returncode != 0
    (repo.path / "shared.txt").write_text("one\ntwo, as a has it, and as the bolt has it\nthree\n")
    (repo.path / "a" / "design.md").write_text("z, as it stands on the bolt\n")
    repo.git("add", "shared.txt", "a/design.md")
    subprocess.run(["git", "-C", str(repo.path), "rebase", "--continue"], check=True, capture_output=True,
                   env=dict(os.environ, GIT_EDITOR="true"))
    repo.git("checkout", "-q", "bolt/t")
    repo.git("merge", "-q", "--no-ff", "unit/a", "-m", "Merge a")
    return place, took


def test_a_dependents_rebase_replaying_its_settled_dependencys_old_commit_conflicts_on_the_dependencys_own_files(repo, tmp_path):
    """plan.rebase_dependents (plan.13): rebased onto the bolt alone, a dependent replays the commit of its dependency
    its place took, which the dependency's settle rewrote, and conflicts on the dependency's own files; with the head it
    took left out, only its own commit is replayed, and the rebase is clean."""
    place, took = settled_and_merged(repo, tmp_path)
    tip = repo.git("rev-parse", "unit/b")
    r = onto(place, "refs/heads/bolt/t")
    assert r.returncode == 3 and r.stdout.startswith("conflict ") and "a/design.md" in r.stdout.split()
    assert repo.git("rev-parse", "unit/b") == tip
    r = onto(place, "refs/heads/bolt/t", took[:7])
    assert (r.returncode, r.stdout.strip()) == (0, "rebased")
    assert repo.git("log", "--format=%s", "bolt/t..unit/b") == "feat(b): its own"


def test_a_dependents_rebase_leaves_out_the_bolts_commits_with_the_head_it_took(repo, tmp_path):
    """plan.ONTO: where the bolt moved between the dependency's place and the dependent's, git rebase --onto the bolt
    from the head taken alone replays the bolt's commits between them and conflicts where the bolt changed them again;
    ONTO's upstream, a commit with no ref whose parents are the bolt and that head, leaves out both."""
    place, took = settled_and_merged(repo, tmp_path, moved=True)
    r = subprocess.run(["git", "-C", str(place), "rebase", "-q", "--onto", "bolt/t", took], capture_output=True, text=True)
    assert r.returncode != 0
    assert unmerged(place) == ["f"]
    subprocess.run(["git", "-C", str(place), "rebase", "--abort"], check=True)
    r = onto(place, "refs/heads/bolt/t", took[:7])
    assert (r.returncode, r.stdout.strip()) == (0, "rebased")
    assert repo.git("log", "--format=%s", "--no-merges", "bolt/t..unit/b") == "feat(b): its own"
    assert repo.git("for-each-ref", "--format=%(refname)", "refs/heads").split() == [
        "refs/heads/bolt/t", "refs/heads/main", "refs/heads/unit/a", "refs/heads/unit/b"]


def unmerged(place):
    return subprocess.run(["git", "-C", str(place), "diff", "--name-only", "--diff-filter=U"], capture_output=True,
                          text=True).stdout.split()


def test_the_rebase_a_dependent_is_told_makes_crews_upstream_again_and_meets_only_its_own_overlap(repo, tmp_path):
    """plan.rebase_words (plan.13): crew's rebase of a dependent whose own commit changed the line its dependency's
    settle rewrote conflicts there; the command the dependent is told makes again the upstream that rebase used, which
    has no ref, and run in its place by bash meets the same conflict and none on the dependency's own files."""
    import plan
    place, took = settled_and_merged(repo, tmp_path, moved=True, own={"shared.txt": "one\ntwo, as b has it\nthree\n"})
    r = onto(place, "refs/heads/bolt/t", took[:7])
    assert r.returncode == 3 and r.stdout.split()[1:] == ["shared.txt"]
    words = plan.rebase_words("t", [f"a@{took[:7]}"])
    command = words[words.index("(git rebase ") + 1:-1]
    assert subprocess.run(["bash", "-c", command], cwd=place, capture_output=True, text=True).returncode != 0
    assert unmerged(place) == ["shared.txt"]
    subprocess.run(["git", "-C", str(place), "rebase", "--abort"], check=True)


def kit_with_github(repo, tmp_path):
    """A kit's main checkout whose origin is a bare GitHub stand-in, and another clone that pushes to it."""
    repo.commit("chore: start", {"README.md": "r\n"})
    origin = tmp_path / "github.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin)); repo.git("fetch", "-q", "origin")
    subprocess.run(["git", "clone", "-q", str(origin), str(tmp_path / "other")], check=True)

    def pushed(name):
        o = tmp_path / "other"
        subprocess.run(["git", "-C", str(o), "pull", "-q", "--rebase", "origin", "main"], check=True)
        (o / name).write_text(name)
        subprocess.run(["git", "-C", str(o), "add", name], check=True)
        subprocess.run(["git", "-C", str(o), "commit", "-qm", f"feat: {name}"], check=True)
        subprocess.run(["git", "-C", str(o), "push", "-q", "origin", "main"], check=True)
    return pushed


def main_at(repo):
    """plan.MAIN in the kit's main checkout: what kit.main_now decides main now from, and that decision."""
    import kit
    import plan
    r = subprocess.run(["bash", "-c", plan.MAIN, "crew", str(repo.path)], capture_output=True, text=True)
    return r, kit.main_now(r.stdout, "k", "h")


def test_a_landing_reads_githubs_main_after_a_fetch_however_far_the_hosts_own_main_lags(repo, tmp_path):
    """plan.bolt_land through MAIN (plan.8, plan.14, plan.18): the commit main holds now is GitHub's, origin/main after a
    fetch, which the landing records, against a bare remote whose main is ahead of the host's own; a kit with no origin
    says its own main's; a fetch that fails is refused, naming it (read.1)."""
    head = repo.commit("main", {"README": "r\n"})
    assert main_at(repo)[1] == ("main", head, None)
    pushed = kit_with_github(repo, tmp_path)
    repo.commit("feat: local", {"local": "l\n"}); pushed("later")
    github = subprocess.run(["git", "-C", str(tmp_path / "other"), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert main_at(repo)[1] == ("origin/main", github, None)
    repo.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    r, (ref, sha, why) = main_at(repo)
    assert r.returncode == 0 and ref is None and why.startswith("cannot fetch k from GitHub on h, so cannot read its main now: fatal:"), why


def script(name, *args, cwd=None):
    import plan
    return subprocess.run(["bash", "-c", getattr(plan, name), "crew", *args], capture_output=True, text=True, cwd=cwd)


def test_the_mark_crew_sets_on_a_bolts_branch_goes_when_git_deletes_the_branch(repo):
    """plan.tidy (plan.9, read.4): crew marks a bolt's branch as its own in the kit's git config, branch.bolt/<bolt>.crew,
    once sluice has made it (BOLT_CREATE), and the mark goes with the branch when git deletes it, so the tidy reads it as
    crew's while the branch stands and never after."""
    head = repo.commit("main", {"README": "r\n"})
    repo.git("branch", "-q", "--no-track", "bolt/b", head)
    repo.git("config", "branch.bolt/b.crew", "given")
    assert repo.git("config", "--get-regexp", r"^branch\.bolt/.*\.crew$") == "branch.bolt/b.crew given"
    repo.git("branch", "-q", "-D", "bolt/b")
    assert subprocess.run(["git", "-C", str(repo.path), "config", "--get-regexp", r"^branch\.bolt/"], capture_output=True).returncode == 1


def test_a_branch_removed_by_ref_edits_leaves_crews_mark_behind(repo):
    """plan.tidy through bolt_branch_end (plan.19): sluice's branch delete removes the local branch by ref edits, as
    git update-ref -d does, which leave the branch's git config section, crew's mark among it, so the tidy unsets a mark
    whose branch is gone (read on sluice 0.36.4, tests/py/sluice-0.36.4/README)."""
    head = repo.commit("main", {"README": "r\n"})
    repo.git("branch", "-q", "--no-track", "bolt/b", head)
    repo.git("config", "branch.bolt/b.crew", "given")
    repo.git("update-ref", "-d", "refs/heads/bolt/b")
    assert repo.git("config", "--get-regexp", r"^branch\.bolt/.*\.crew$") == "branch.bolt/b.crew given"
    repo.git("config", "--unset", "branch.bolt/b.crew")
    assert subprocess.run(["git", "-C", str(repo.path), "config", "--get-regexp", r"^branch\.bolt/"], capture_output=True).returncode == 1


def test_a_kits_policy_is_read_from_mains_commit(repo):
    """plan.kit_policy (teams.5): the policy is what main's commit holds, as sluice reads a branch's policy, not the
    main checkout's files; a main without one says so."""
    import kit
    repo.commit("main", {"README": "r\n"})
    assert kit.policy_said(script("POLICY", str(repo.path), ".config/sluice.toml").stdout, "k", "h")[:2] == (None, "main")
    text = '[branches."bolt/*"]\nrequired = ["#check-full"]\n'
    repo.commit("chore: policy", {".config/sluice.toml": text})
    (repo.path / ".config" / "sluice.toml").write_text("not what main holds\n")
    assert kit.policy_said(script("POLICY", str(repo.path), ".config/sluice.toml").stdout, "k", "h")[:2] == (text, "main")


def test_a_kits_policy_is_read_from_githubs_main_ahead_of_the_hosts_own(repo, tmp_path):
    """plan.kit_policy through POLICY (plan.18): a kit on GitHub has its policy read from origin/main after a fetch,
    where it was written, not from the host's own main, which lags it."""
    import kit
    pushed = kit_with_github(repo, tmp_path)
    o = tmp_path / "other"
    (o / ".config").mkdir()
    text = '[branches."bolt/*"]\nrequired = ["#check-full"]\n'
    (o / ".config" / "sluice.toml").write_text(text)
    subprocess.run(["git", "-C", str(o), "add", ".config/sluice.toml"], check=True)
    subprocess.run(["git", "-C", str(o), "commit", "-qm", "chore: policy"], check=True)
    subprocess.run(["git", "-C", str(o), "push", "-q", "origin", "main"], check=True)
    assert kit.policy_said(script("POLICY", str(repo.path), ".config/sluice.toml").stdout, "k", "h")[:2] == (text, "origin/main")
    assert not (repo.path / ".config" / "sluice.toml").exists()


def test_a_legacy_bolts_tip_is_read_with_the_remotes_that_hold_it(repo, tmp_path):
    """plan.BOLT_TIP and plan.forecast_way (plan.19): the policy is read from the host's own bolt/<bolt>, not main's,
    as sluice routes a branch by the policy at its tip, and a remote holds the bolt once this host has a tracking ref
    of it from there, read with no fetch (plan.18); a bolt the host keeps no branch of has no tip."""
    import plan
    pushed = kit_with_github(repo, tmp_path)
    pushed("later")
    repo.git("branch", "bolt/t")
    repo.git("switch", "-q", "bolt/t")
    policy = '[branches."bolt/*"]\nremote = "origin"\nrequired = ["#check-full"]\n'
    tip = repo.commit("chore: bolts on origin", {".config/sluice.toml": policy})
    repo.git("switch", "-q", "--detach", "main")
    r = script("BOLT_TIP", str(repo.path), "t", ".config/sluice.toml")
    assert r.returncode == 0 and f"TIP={tip}\n" in r.stdout and "TRACKED=\n" in r.stdout, r.stdout + r.stderr
    assert plan.forecast_way("t", r.stdout) == ("place", None)
    repo.git("push", "-q", "origin", "bolt/t")
    repo.git("fetch", "-q", "origin")
    r = script("BOLT_TIP", str(repo.path), "t", ".config/sluice.toml")
    assert "TRACKED=origin \n" in r.stdout and plan.forecast_way("t", r.stdout) == ("branch", None), r.stdout
    assert "TIP=-\n" in script("BOLT_TIP", str(repo.path), "u", ".config/sluice.toml").stdout


def forecast_from_place(repo, tmp_path, bolt="t"):
    """plan.FORECAST_PLACE in the kit's main checkout, with a stand-in sluice that records the worktree it was asked
    to forecast from, the branch that worktree is on and its head, and answers with no conflict."""
    import plan
    bin_ = tmp_path / "bin"
    bin_.mkdir(exist_ok=True)
    (bin_ / "sluice").write_text(
        '#!/usr/bin/env bash\n'
        f'[ "$*" = "submit main --check --worktree $5 --json" ] || exit 64\n'
        f'echo "$5 $(git -C "$5" symbolic-ref --short HEAD) $(git -C "$5" rev-parse HEAD)" >> {tmp_path}/asked\n'
        'printf \'{"conflict": null, "head": "%s", "onto": "o", "ahead": []}\' "$(git -C "$5" rev-parse HEAD)"\n')
    (bin_ / "sluice").chmod(0o755)
    path = repo.path.parent / "places" / f"forecast-{bolt}"
    r = subprocess.run(["bash", "-c", plan.FORECAST_PLACE, "crew", str(repo.path), str(path), bolt], capture_output=True,
                       text=True, env=dict(os.environ, PATH=f"{bin_}:{os.environ['PATH']}"))
    assert r.returncode == 0, r.stderr
    return path, plan.place_checked(bolt, r.stdout, r.stderr), r.stdout


def test_a_legacy_bolt_is_forecast_from_a_place_crew_makes_on_it_with_no_checkout_and_removes(repo, tmp_path):
    """plan.FORECAST_PLACE (plan.19): with no worktree on bolt/<bolt>, crew makes its own on the branch with no
    checkout, which sluice reads as on the branch at the bolt's tip, and removes it once sluice has answered, its
    staged deletions forced; the branch is where it was. One a stopped forecast left there is taken and removed."""
    import plan
    repo.commit("main", {"README": "r\n"})
    tip = repo.commit("feat: bolt work", {"work.txt": "w\n"})
    repo.git("branch", "bolt/t")
    repo.git("switch", "-q", "--detach", "HEAD~1")
    path, (checked, kept), out = forecast_from_place(repo, tmp_path)
    assert (tmp_path / "asked").read_text() == f"{path} bolt/t {tip}\n"
    assert plan.bolt_forecast_read(*checked) == ({"conflict": None, "head": tip, "onto": "o", "ahead": []}, None) and kept is None
    assert not path.exists() and str(path) not in repo.git("worktree", "list")
    assert repo.git("rev-parse", "bolt/t") == tip
    repo.git("worktree", "add", "-q", "--no-checkout", str(path), "bolt/t")
    forecast_from_place(repo, tmp_path)
    assert not path.exists() and str(path) not in repo.git("worktree", "list")


def test_a_worktree_already_on_the_bolt_is_the_place_its_forecast_is_read_from_and_is_kept(repo, tmp_path):
    """plan.FORECAST_PLACE (plan.19): a worktree on bolt/<bolt> that is not crew's forecast place, the landing's while
    its submission is with sluice, is forecast from as it stands and left there; a path git cannot make a worktree at
    is said with git's words, nothing forecast."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/t")
    land = repo.path.parent / "places" / "land-t"
    repo.git("worktree", "add", "-q", str(land), "bolt/t")
    path, (checked, kept), out = forecast_from_place(repo, tmp_path)
    assert (tmp_path / "asked").read_text().split()[:2] == [str(land), "bolt/t"] and checked[0] == 0 and kept is None
    assert land.exists() and not path.exists()
    repo.git("worktree", "remove", str(land))
    path.mkdir(parents=True)
    (path / "theirs.txt").write_text("x\n")
    _, (checked, kept), _ = forecast_from_place(repo, tmp_path)
    assert checked[0] is None and checked[2].startswith(f"no place on bolt/t could be made to forecast it from: fatal: '{path}' already exists"), checked


def test_a_units_change_is_read_from_mains_commit_into_a_folder(repo, tmp_path):
    """plan.change_folder through change_written (plan.18): a change that no place or bolt worktree holds is read as the
    kit's main holds it at a commit, open or else archived, its Markdown written into the session's folder, not read
    from the main checkout's files; a change main does not hold is None."""
    import plan
    repo.commit("main", {"README": "r\n"})
    sha = repo.commit("docs(openspec): archive a", {"openspec/changes/archive/2026-10-16-a/proposal.md": "p\n",
                                                     "openspec/changes/archive/2026-10-16-a/specs/x/spec.md": "s\n",
                                                     "openspec/changes/archive/2026-10-16-a/.openspec.yaml": "y\n"})
    repo.git("checkout", "-q", "HEAD~1")
    into = tmp_path / "card" / "change"
    assert plan.change_written(str(repo.path), sha, "a", into) == str(into)
    assert sorted(str(f.relative_to(into)) for f in into.rglob("*") if f.is_file()) == ["proposal.md", "specs/x/spec.md"]
    assert (into / "proposal.md").read_text() == "p\n"
    assert plan.change_written(str(repo.path), sha, "b", tmp_path / "none") is None


def test_a_landings_verdict_is_its_trailer(repo):
    """gather.kit (tests.5, record 0025): sluice's verdict on a landing is the Sluice-Result trailer of its merge
    commit, read with git log's trailer format; a commit sluice did not make has none."""
    import gather
    repo.commit("main", {"README": "r\n"})
    assert gather.run(["git", "log", "-1", "--format=%(trailers:key=Sluice-Result,valueonly)", "HEAD"], str(repo.path)).strip() == ""
    repo.commit("chore(land): #9 unit/a\n\nSluice-Submission: 9\nSluice-From: swb-1-unit-1 (unit/a)\nSluice-Tested: abc\n"
                "Sluice-Result: passed (9 run, 0 replayed)")
    assert gather.run(["git", "log", "-1", "--format=%(trailers:key=Sluice-Result,valueonly)", "HEAD"], str(repo.path)).strip() == (
        "passed (9 run, 0 replayed)")


# sluice 0.36.4's answer to a submission to a main that takes pull requests, once intake has queued the one it opened
# (lib.rs submit_pull under --no-wait --json).
PULLED = '{"branch":"main","pull_request":113,"state":"queued: next on main"}'


def landing(repo, tmp_path):
    """plan.SUBMIT and plan.LANDED as bolt_submit runs them on the team's host, for bolt b of the kit at repo, after
    plan.MAIN has read main now there, with a path holding wt and the tools they run but no wt-submit; and stand_in(),
    which puts a stand-in wt-submit there that takes `main --no-wait --json --no-remove` and lands as sluice does: a merge
    commit moved onto main by git update-ref, which leaves a checkout on main behind its HEAD, and, with stray, leaves a
    file git does not ignore in the landing's worktree; with on_github, it forms the merge on origin/main and pushes it
    there, leaving the host's own main where it was, then fails releasing a place, its outcome sluice's exit 3, as
    sluice 0.36.4 does on a release that fails after its push; with refused, it pushes nothing, its outcome a conflict,
    exit 2; with at_once, sluice refuses the submission itself, saying why on standard error and exiting 2; with
    failing, it pushes nothing, its outcome sluice itself failing while the submission waits, exit 3; with pulled, it
    lands nothing and answers as sluice 0.36.4 does on a main that takes pull requests once intake has queued the one it
    opened, its number on standard output and no submission, exit 0. Otherwise it names no submission, so SUBMIT leaves
    no `sluice wait` running; the outcome sluice's wait would give is handed to LANDED as crew hands it, with sluice's
    last line, or, with none, SUBMIT's exit and the last line SUBMIT says the submission said, as landing_ended hands
    them. A stand-in sluice beside it takes `sluice wait 7`, for SUBMIT run again with a submission and its tip (again):
    the wait SUBMIT leaves running ends at once, and the one plan.WAIT runs, as landing_ended does, finds the landing's
    place made again on bolt/b, lands from it as wt-submit does and exits 0, handed to LANDED with its last line; and
    `sluice wait main`, which writes where it ran and what it was asked to the file followed, and ends once the file
    release is there. Each run is
    LANDED's result, SUBMIT's said on its standard error before LANDED's, or SUBMIT's own when it refused, and the
    commit main now was at before it."""
    import plan
    land = tmp_path / "places" / "land-b"
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    wt = shutil.which("wt") or pytest.skip("worktrunk's wt is not on this host's path")
    os.symlink(wt, bin_ / "wt")
    for tool in ("git", "bash", "sh", "env", "hostname", "mktemp", "xargs", "dirname", "cat", "printf", "rm", "base64", "tr"):
        if shutil.which(tool):
            os.symlink(shutil.which(tool), bin_ / tool)
    outcome = tmp_path / "outcome"

    def land_with(path, *again):
        _, (_, before, why) = main_at(repo)
        assert not why, why
        env = dict(os.environ, PATH=path)
        r = subprocess.run(["bash", "-c", plan.SUBMIT, "crew", str(repo.path), str(land), "b", "wldn-ops", *again],
                           capture_output=True, text=True, env=env)
        if r.returncode:
            return r, before
        f = dict(w.split("=", 1) for w in shlex.split(r.stdout.strip().splitlines()[-1]))
        told = base64.b64decode(f["SAID"], validate=True).decode().strip().splitlines()
        if f["ID"]:  # a submission SUBMIT waits on: sluice's outcome of it, a call of plan.WAIT
            w = subprocess.run(["bash", "-c", plan.WAIT, "crew", str(repo.path), f["ID"]], capture_output=True, text=True, env=env)
            r.stderr += w.stderr
            rc, said = str(w.returncode), (w.stderr.strip().splitlines() or [""])[-1]
        else:
            rc, said = outcome.read_text().split("\n", 1) if outcome.exists() else (f["RC"], told[-1] if told else "")
        outcome.unlink(missing_ok=True)
        e = subprocess.run(["bash", "-c", plan.LANDED, "crew", str(repo.path), str(land), "b", f["TIP"], f["OLD"], rc,
                            base64.b64encode(said.encode()).decode()], capture_output=True, text=True, env=env)
        return subprocess.CompletedProcess(e.args, e.returncode, e.stdout, r.stderr + e.stderr), before

    def stand_in(stray=False, on_github=False, refused=False, at_once=False, failing=False, pulled=False):
        onto = "refs/remotes/origin/main" if on_github else "main"
        pushed = 'git push -q origin "$new:refs/heads/main" || exit 2\necho "landed #1 on GitHub\'s main"\n'
        moved = (pushed + 'echo "sluice: releasing try/b: its command failed" >&2\n'
                 f'printf "3\\nsluice: releasing try/b: its command failed" > "{outcome}"' if on_github else
                 f'git update-ref refs/heads/main "$new"\necho "landed #1"\nprintf "0\\n" > "{outcome}"')
        lands = f'''{"git fetch -q origin" if on_github else ""}
tree=$(printf 'x\\n' | git hash-object -w --stdin)
idx=$(mktemp); GIT_INDEX_FILE=$idx git read-tree {onto}
GIT_INDEX_FILE=$idx git update-index --add --cacheinfo 100644,$tree,landed.txt
new=$(GIT_INDEX_FILE=$idx git write-tree | xargs -I{{}} git commit-tree {{}} -p {onto} -p HEAD -m "chore(land): #1 bolt/b")
'''
        failed = "sluice: a round of main failed: its lock could not be taken"
        (bin_ / "wt-submit").write_text(f'''#!/bin/sh
[ "$1 $2 $3 $4" = "main --no-wait --json --no-remove" ] || exit 9
[ "$(git symbolic-ref --short HEAD)" = bolt/b ] || exit 8
echo "$SLUICE_AGENT" > "{tmp_path}/agent"
git status --porcelain > "{tmp_path}/status"
{f"echo 'sluice: bolt/b conflicts with main' >&2; printf '2\\nsluice: bolt/b conflicts with main' > '{outcome}'; exit 0" if refused else ""}
{"echo 'sluice: main has no gate for bolt/b' >&2; exit 2" if at_once else ""}
{f"echo '{failed}' >&2; printf '3\\n{failed}' > '{outcome}'; exit 0" if failing else ""}
{f"echo '{PULLED}'; exit 0" if pulled else ""}
{"echo s > stray.txt" if stray else ""}
{lands}{moved}
''')
        (bin_ / "sluice").write_text(f'''#!/bin/sh
[ "$1 $2" = "wait main" ] && {{ echo "$PWD $*" > "{tmp_path}/followed"; n=0
  while [ ! -e "{tmp_path}/release" ] && [ $n -lt 6000 ]; do sleep 0.1; n=$((n + 1)); done; exit 0; }}
[ "$1 $2" = "wait 7" ] || exit 9
[ "$3 $4" = "--timeout 9m" ] || exit 0
cd "{land}" && [ "$(git symbolic-ref --short HEAD)" = bolt/b ] || exit 8
{lands}{pushed if on_github else 'git update-ref refs/heads/main "$new"'}
''')
        for tool in ("wt-submit", "sluice"):
            (bin_ / tool).chmod(0o755)
        return lambda *again: land_with(f"{bin_}:{os.environ['PATH']}", *again)
    return land, lambda: land_with(str(bin_)), stand_in


def marked(repo):
    """plan.LANDED_MARK as bolt_submit runs it once landing_said read the bolt landed: what plan.mark_said makes of it."""
    import plan
    m = script("LANDED_MARK", str(repo.path), "b")
    return plan.mark_said(m.returncode, m.stdout, m.stderr)


def test_a_landing_submits_from_a_worktree_on_the_bolt_and_brings_main_level(repo, tmp_path):
    """plan.bolt_submit (plan.16, record 0026): sluice takes a submission only from a worktree on its branch, so the
    landing makes one on bolt/<bolt>, runs `wt submit main --no-wait --json` there, which the real worktrunk runs as wt-submit from the
    path, removes it, and brings the kit's main checkout level with what sluice moved while it is on branch main,
    keeping an untracked file there. With no wt-submit on the path the landing is refused, naming it, with nothing
    made. Once crew has read that it landed, the bolt's branch crew marked given is marked landed in the kit's git
    config by LANDED_MARK, which a refused landing leaves as it was and git drops with the branch (record 0003)."""
    import plan
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("config", "branch.bolt/b.crew", "given")
    (repo.path / "notes.txt").write_text("the user's own\n")
    land, unready, stand_in = landing(repo, tmp_path)
    r, _ = unready()
    assert r.returncode == 2 and "wt submit needs sluice's wt-submit, which is not on" in r.stderr, r.stderr
    assert not land.exists()
    assert repo.git("config", "branch.bolt/b.crew") == "given"
    r, before = stand_in()()
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before)
    assert landed and "MARKED" not in r.stdout, r.stdout + r.stderr
    assert repo.git("config", "branch.bolt/b.crew") == "given"
    assert marked(repo) == "yes"
    assert "mark" not in plan.landing_said("b", "kit", "h", r.stdout, before, "yes")[1]
    assert repo.git("config", "branch.bolt/b.crew") == "landed"
    assert (tmp_path / "agent").read_text().strip() == "wldn-ops"
    assert not land.exists() and "land-b" not in repo.git("worktree", "list")
    assert (repo.path / "landed.txt").read_text() == "x\n"
    assert repo.git("status", "--porcelain") == "?? notes.txt"
    repo.git("branch", "-q", "-D", "bolt/b")
    assert subprocess.run(["git", "-C", str(repo.path), "config", "--get", "branch.bolt/b.crew"]).returncode == 1


def test_a_landing_of_a_bolt_branch_crew_did_not_mark_leaves_it_unmarked(repo, tmp_path):
    """plan.LANDED_MARK and plan.landing_said (read.4): a bolt's branch with no mark of crew's is not crew's, so its
    landing sets none and says so."""
    import plan
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    _, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in()()
    assert plan.landing_said("b", "kit", "h", r.stdout, before)[0], r.stdout + r.stderr
    assert marked(repo) == "no"
    assert plan.landing_said("b", "kit", "h", r.stdout, before, "no")[1].endswith(
        "crew could not mark bolt/b landed: its branch carries no mark of crew's.")
    assert subprocess.run(["git", "-C", str(repo.path), "config", "--get", "branch.bolt/b.crew"]).returncode == 1


def test_a_landings_worktree_git_cannot_remove_is_kept_and_named_in_gits_words(repo, tmp_path):
    """plan.LANDED and plan.landing_said (read.1, plan.19): a landing's worktree holding a file git does not ignore is
    one git worktree remove refuses; the landing still lands, and names the worktree with git's words, which LANDED
    keeps rather than discarding, for crew bolt land to sweep it with the bolt or name it there."""
    import plan
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    land, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(stray=True)()
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before)
    assert landed, r.stdout + r.stderr
    assert (land / "stray.txt").exists() and "land-b" in repo.git("worktree", "list")
    assert f"Its worktree {land} is kept, git refusing to remove it: fatal: '{land}' contains modified or untracked files" in words, words
    assert words.endswith("crew bolt land removes it with the bolt, or names it with why it stays."), words


def test_a_landing_against_a_detached_main_checkout_leaves_it_untouched_and_says_nothing_of_levelling(repo, tmp_path):
    """plan.bolt_submit and plan.landing_said (plan.18): a kit's main checkout detached, the anchor the fleet's timer
    moves, is left at the commit it was at with its files as they were when sluice moves main, and the landing says
    nothing of levelling it."""
    import plan
    was = repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("switch", "-q", "--detach")
    land, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in()()
    assert "LEVEL=detached" in r.stdout, r.stdout + r.stderr
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before)
    assert landed and "level" not in words, words
    assert repo.git("rev-parse", "HEAD") == was and repo.git("rev-parse", "main") != was
    assert not (repo.path / "landed.txt").exists() and repo.git("status", "--porcelain") == ""


def test_a_landing_sluice_pushed_to_github_and_then_failed_is_a_landing(repo, tmp_path):
    """plan.LANDED, plan.landing_said and plan.LANDED_MARK (plan.18, plan.16): sluice forms the landing on GitHub's
    main and pushes it, then fails releasing a place and exits 3 with the host's own main where it was, as it did for
    swancloud's a-landed-places-preview-is-released (signal 2026-10-22-swancloud-ops-b237b51b/01). LANDED's fetch
    after sluice's outcome reads GitHub's main moved and holding the bolt's tip, so the bolt landed there, sluice's exit
    and its last line named as what came after the push, nothing said of levelling a main that did not move, and the
    branch is then marked landed. A stand-in that pushes nothing and exits 2 lands nothing, and main is where it was,
    its refusal recorded in sluice's words, from its wait's or, when sluice refused the submission at once, from what
    SUBMIT says it said (rail-cards "A refused landing is held on its row")."""
    import plan
    pushed = kit_with_github(repo, tmp_path)
    pushed("from-a-mac")
    repo.git("branch", "bolt/b", "origin/main")
    repo.git("config", "branch.bolt/b.crew", "given")
    tip = repo.git("commit-tree", "-p", "bolt/b", "-m", "feat: the bolt's", repo.git("rev-parse", "bolt/b^{tree}"))
    repo.git("update-ref", "refs/heads/bolt/b", tip)
    own = repo.git("rev-parse", "main")
    _, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(refused=True)()
    assert before == repo.git("rev-parse", "origin/main") and "RC=2 " in r.stdout, r.stdout + r.stderr
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before)
    assert not landed and words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was."), words
    assert plan.landing_said("b", "kit", "h", r.stdout, before, recorded=True) == (False, "sluice: bolt/b conflicts with main")
    r, before = stand_in(at_once=True)()
    assert "RC=2 " in r.stdout and "sluice: main has no gate for bolt/b" in r.stderr, r.stdout + r.stderr
    assert plan.landing_said("b", "kit", "h", r.stdout, before, recorded=True) == (False, "sluice: main has no gate for bolt/b")
    r, before = stand_in(on_github=True)()
    assert "RC=3 " in r.stdout and "sluice: releasing try/b: its command failed" in r.stderr, r.stdout + r.stderr
    github = subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-parse", "main"],
                            capture_output=True, text=True).stdout.strip()
    assert github != before and repo.git("rev-parse", "main") == own
    assert repo.git("rev-parse", f"{github}^2") == tip
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before)
    assert (landed, words) == (True, f"bolt/b landed on kit's main at {github[:7]}: now crew bolt land b. sluice exited 3 after "
                                     "its push: sluice: releasing try/b: its command failed. That is sluice's to report, apart "
                                     "from the landing."), r.stdout
    assert marked(repo) == "yes" and repo.git("config", "branch.bolt/b.crew") == "landed"


def test_a_landings_worktree_is_cut_on_a_split_legacy_bolt_writing_no_bolt_ref(repo, tmp_path):
    """plan.SUBMIT (plan.19, sluice clause 124): a legacy bolt whose host branch is ahead of its stale copy on GitHub,
    under a stand-in for sluice's guard that refuses a write to refs/heads/bolt/b differing from origin's copy, as
    sluice's reference-transaction hook judges one (swancloud-ops's signal 2026-10-23-swancloud-ops-7c7811ae/01: "is
    protected by sluice"). A plain git worktree add's checkout writes the branch to the value it holds, which the guard
    refuses; the landing's --no-checkout add writes only the worktree's HEAD and read-tree -m -u HEAD its files and
    index, no transaction on the branch, so the worktree stands clean on bolt/b at the host's tip and the landing lands
    the host's tip as any bolt does."""
    import plan
    kit_with_github(repo, tmp_path)
    repo.git("branch", "bolt/b", "origin/main")
    repo.git("push", "-q", "origin", "bolt/b")
    repo.git("fetch", "-q", "origin")
    repo.git("checkout", "-q", "bolt/b")
    tip = repo.commit("feat: the bolt's, on the host alone", {"bolt.txt": "b\n"})
    repo.git("checkout", "-q", "main")
    assert repo.git("rev-parse", "origin/bolt/b") != tip
    log = tmp_path / "guard.log"
    guard = repo.path / ".git" / "hooks" / "reference-transaction"
    guard.parent.mkdir(exist_ok=True)
    guard.write_text(f'''#!/bin/sh
while read -r old new ref; do
  echo "$1 $ref" >> "{log}"
  if [ "$1" = prepared ] && [ "$ref" = refs/heads/bolt/b ] && [ "$new" != "$(git rev-parse -q --verify refs/remotes/origin/bolt/b)" ]; then
    echo "bolt/b is protected by sluice" >&2; exit 1
  fi
done
''')
    guard.chmod(0o755)
    plain = subprocess.run(["git", "-C", str(repo.path), "worktree", "add", "-q", str(tmp_path / "plain"), "bolt/b"],
                           capture_output=True, text=True)
    assert plain.returncode != 0 and "bolt/b is protected by sluice" in plain.stderr, plain.stderr
    log.write_text("")
    _, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(on_github=True)()
    assert "RC=3 " in r.stdout and f"TIP={tip} " in r.stdout, r.stdout + r.stderr
    assert "refs/heads/bolt/b" not in log.read_text(), log.read_text()
    assert (tmp_path / "status").read_text() == ""
    github = subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-parse", "main"],
                            capture_output=True, text=True).stdout.strip()
    assert repo.git("rev-parse", f"{github}^2") == tip and repo.git("rev-parse", "bolt/b") == tip
    assert plan.landing_said("b", "kit", "h", r.stdout, before)[0], r.stdout


def test_a_submission_sluice_failed_on_is_waited_on_again_while_its_record_has_it_standing(repo, tmp_path):
    """plan.SUBMIT, plan.WAIT, plan.LANDED, plan.sluice_failed, plan.landing_said and plan.wait_again (plan.16,
    plan.18): sluice itself fails while the landing's submission waits, exiting 3 with nothing pushed, so GitHub's main
    does not hold the bolt's tip and whether the bolt lands is sluice's own record's to say, never "did not land" on the
    exit alone. With the record holding the submission queued, SUBMIT given its id and the tip it submitted makes the
    landing's place again and submits nothing, sluice's wait on it (WAIT) lands it, and LANDED judges main now against
    that tip; the place goes after."""
    import plan
    pushed = kit_with_github(repo, tmp_path)
    pushed("from-a-mac")
    repo.git("branch", "bolt/b", "origin/main")
    tip = repo.git("commit-tree", "-p", "bolt/b", "-m", "feat: the bolt's", repo.git("rev-parse", "bolt/b^{tree}"))
    repo.git("update-ref", "refs/heads/bolt/b", tip)
    land, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(on_github=True, failing=True)()
    assert "RC=3 " in r.stdout and "sluice: a round of main failed" in r.stderr, r.stdout + r.stderr
    assert plan.sluice_failed(r.stdout, before) == tip and not land.exists()
    queued = {"id": 7, "state": "queued"}
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before, sub=queued)
    assert not landed and "did not land" not in words and words.endswith("crew waits on it again (sluice wait 7)."), words
    assert plan.wait_again(queued, 0) == 7
    r, again = stand_in(on_github=True)("7", tip)
    assert again == before and f"RC=0 TIP={tip} " in r.stdout, r.stdout + r.stderr
    github = subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-parse", "main"],
                            capture_output=True, text=True).stdout.strip()
    assert plan.landing_said("b", "kit", "h", r.stdout, before) == (True, f"bolt/b landed on kit's main at {github[:7]}: now crew bolt land b.")
    assert plan.sluice_failed(r.stdout, before) is None
    assert not land.exists() and "land-b" not in repo.git("worktree", "list")



def test_a_landing_sluice_queued_as_a_pull_request_is_followed_from_its_place_while_it_stands(repo, tmp_path):
    """plan.SUBMIT, plan.submitted_line and plan.landing_now (plan.16, plan.8): to a main that takes pull requests
    sluice 0.36.4 answers a landing's submission with the pull request it opened, its number and no submission. SUBMIT
    reads its number, PULL, beside no ID, hands crew the answer as sluice printed it, and leaves `sluice wait main`
    running from the landing's place, which follows the pull request to its submission's outcome, its process held in
    crew-landing, so no stage starts on the bolt while it stands; once that wait ends the mark is emptied."""
    import plan
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    land, _, stand_in = landing(repo, tmp_path)
    stand_in(pulled=True)
    env = dict(os.environ, PATH=f"{tmp_path / 'bin'}:{os.environ['PATH']}")
    r = subprocess.run(["bash", "-c", plan.SUBMIT, "crew", str(repo.path), str(land), "b", "wldn-ops"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 0, r.stderr
    f = dict(w.split("=", 1) for w in shlex.split(r.stdout.strip().splitlines()[-1]))
    assert (f["RC"], f["ID"], f["PULL"]) == ("0", "", "113") and base64.b64decode(f["ANSWER"]).decode().strip() == PULLED
    assert plan.submitted_line("b", "kit", f) == "bolt/b submitted to kit's main as pull request #113"
    t = {"kit": {"dir": str(tmp_path)}}
    followed, release, end = tmp_path / "followed", tmp_path / "release", time.monotonic() + 600  # tests.8: a condition
    while not followed.exists() and time.monotonic() < end:
        time.sleep(0.1)
    ran_in, *asked = followed.read_text().split()
    assert os.path.realpath(ran_in) == os.path.realpath(land) and asked == ["wait", "main", "--timeout", "24h", "--json"]
    assert plan.landing_now(t, "b") == (str(land), True, True)
    release.write_text("")
    while plan.landing_now(t, "b")[2] and time.monotonic() < end:
        time.sleep(0.1)
    assert plan.landing_now(t, "b") == (str(land), True, False)

def test_a_units_change_is_found_on_its_bolt_through_sluices_merge_after_the_merge_archived_it(repo):
    """plan.landed_at (plan.13, teams.17, record 0026): the commit that brought a unit's change to its bolt, which
    rebase_dependents compares with what a dependent's place holds, is found when sluice landed the unit as a merge
    commit and the unit's merge archived the change first. git log's default history simplification follows only the
    first parent of a merge whose tree matches it on the path, and the bolt's side never held openspec/changes/<unit>, so
    without --full-history the unit's side is pruned and nothing is found."""
    import plan
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("checkout", "-q", "-b", "unit/a", "bolt/b")
    made = repo.commit("docs(a): the change", {"openspec/changes/a/proposal.md": "p\n"})
    repo.git("mv", "openspec/changes/a", "openspec/changes/archive-2026-10-13-a")
    repo.git("commit", "-q", "-m", "docs(openspec): archive a")
    repo.git("checkout", "-q", "bolt/b")
    repo.commit("feat: the bolt's own", {"other": "o\n"})
    repo.git("merge", "-q", "--no-ff", "-m", "chore(land): #1 unit/a", "unit/a")
    assert plan.landed_at(str(repo.path), "b", "a") == made


def test_git_cherry_finds_nothing_of_a_units_own_once_its_commits_reached_the_bolt_rebased(repo):
    """plan.branch_gone and plan.branch_kept (plan.10, record 0003): a unit's commits that reached its bolt under other
    hashes, rebased or cherry-picked as they merged, are - lines to git cherry, which compares each commit's patch, so
    the branch goes; a commit whose patch the bolt lacks is a + line, so it is kept."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("checkout", "-q", "-b", "unit/u", "bolt/b")
    one = repo.commit("feat(u): one", {"u1": "1\n"})
    two = repo.commit("feat(u): two", {"u2": "2\n"})
    repo.git("checkout", "-q", "bolt/b")
    repo.commit("feat: the bolt's own", {"other": "o\n"})
    repo.git("cherry-pick", one, two)
    assert repo.git("rev-parse", "bolt/b") != two
    assert repo.git("cherry", "bolt/b", "unit/u") == f"- {one}\n- {two}"
    repo.git("checkout", "-q", "unit/u")
    three = repo.commit("feat(u): three", {"u3": "3\n"})
    assert repo.git("cherry", "bolt/b", "unit/u").splitlines()[-1] == f"+ {three}"


def test_git_cherry_does_not_list_a_merge_commit_on_the_branch(repo):
    """plan.branch_kept (plan.10): a dependent's branch that took another unit's head by a merge counts only its own
    commits whose patch the bolt lacks, since git cherry leaves merge commits out."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("checkout", "-q", "-b", "unit/a", "bolt/b")
    a = repo.commit("feat(a): its own", {"a": "a\n"})
    repo.git("checkout", "-q", "-b", "unit/d", "bolt/b")
    repo.git("merge", "-q", "--no-ff", "-m", "chore(d): build on a", "unit/a")
    merge = repo.git("rev-parse", "HEAD")
    repo.git("checkout", "-q", "bolt/b")
    repo.git("merge", "-q", "--no-ff", "-m", "Merge a", "unit/a")
    assert merge not in repo.git("cherry", "bolt/b", "unit/d")
    assert repo.git("cherry", "bolt/b", "unit/d") == ""
    repo.git("checkout", "-q", "unit/d")
    d = repo.commit("feat(d): its own", {"d": "d\n"})
    assert repo.git("cherry", "bolt/b", "unit/d") == f"+ {d}" and a not in repo.git("cherry", "bolt/b", "unit/d")


def test_a_deleted_bolt_is_still_named_as_the_upstream_but_neither_compared_nor_found(repo, tmp_path):
    """plan.branch_target, through branch_gone (plan.10): once the bolt's branch is gone, %(upstream:short), which
    gather.upstreams reads, still names it, so whether the bolt exists is read with rev-parse --verify; git cherry
    against it exits non-zero, which keeps the branch when nothing else is compared (read.1)."""
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    repo.git("worktree", "add", "-q", "--track", "-b", "unit/u", str(tmp_path / "place"), "bolt/b")
    repo.git("branch", "-q", "-D", "bolt/b")
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/u") == "bolt/b"
    verify = subprocess.run(["git", "-C", str(repo.path), "rev-parse", "--verify", "-q", "refs/heads/bolt/b"], capture_output=True, text=True)
    assert verify.returncode != 0 and verify.stdout == ""
    cherry = subprocess.run(["git", "-C", str(repo.path), "cherry", "bolt/b", "unit/u"], capture_output=True, text=True)
    assert cherry.returncode != 0 and "bolt/b" in cherry.stderr


def test_a_bolt_on_github_a_branch_tracks_is_found_at_the_ref_its_upstream_names(repo, tmp_path):
    """plan.branch_gone (plan.10, plan.19): a fix cut from origin/bolt/<bolt> names it as its upstream, which is no
    branch of the host's, so whether its bolt stands is read at gather.bolt_ref's refs/remotes/origin/bolt/<bolt>; read
    under refs/heads/ it would seem gone, and the fix be compared with main rather than the bolt holding it."""
    import gather
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/b")
    origin = tmp_path / "github.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin))
    repo.git("branch", "-q", "-D", "bolt/b")
    repo.git("fetch", "-q", "origin")
    repo.git("branch", "-q", "--track", "fix/b/edge", "origin/bolt/b")
    up = repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/fix/b/edge")
    assert up == "origin/bolt/b"
    verify = lambda ref: subprocess.run(["git", "-C", str(repo.path), "rev-parse", "--verify", "-q", ref], capture_output=True).returncode
    assert verify(f"refs/heads/{up}") != 0
    assert verify(gather.bolt_ref(up)[1]) == 0
    assert repo.git("cherry", up, "fix/b/edge") == ""


def test_a_place_made_on_a_kept_branch_takes_it_as_it_stands_tracks_the_new_bolt_and_prints_its_commit(repo, tmp_path):
    """plan.make_place through PLACE (record 0003, plan.10): unit/u, kept when u was dropped from bolt a, whose bolt's
    branch is gone, is taken by the place of a unit u added to bolt b as it stands, holding its kept commit; it then
    tracks bolt/b where it lives, the host's own branch for a bolt whose policy names no remote (plan.19), so the stages
    read it as b's, and PLACE prints the commit as KEPT, which kit.place_said passes over. A place already there, or one
    made with a new branch, prints no KEPT."""
    import kit
    repo.commit("main", {"README": "r\n"})
    repo.git("branch", "bolt/a")
    repo.git("branch", "--track", "unit/u", "bolt/a")
    repo.git("checkout", "-q", "unit/u")
    kept = repo.commit("feat(u): written before the drop", {"u": "u\n"})
    repo.git("checkout", "-q", "main")
    repo.git("branch", "-q", "-D", "bolt/a")
    repo.git("branch", "bolt/b")
    place = tmp_path / "places" / "u"
    said = cut(repo, tmp_path, "u")
    assert f"KEPT={kept[:7]}" in said.splitlines()
    assert kit.place_said(said, "b")[1] is None
    assert subprocess.run(["git", "-C", str(place), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() == kept
    assert (place / "u").read_text() == "u\n"
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/u") == "bolt/b"
    again = script("PLACE", str(repo.path), str(place), "unit/u", "b", "", kit.DECLARATION)
    assert again.returncode == 0 and "GITDIR=" in again.stdout and "KEPT=" not in again.stdout
    assert "KEPT=" not in cut(repo, tmp_path, "v")
    assert repo.git("for-each-ref", "--format=%(upstream:short)", "refs/heads/unit/v") == "bolt/b"


def test_a_dependent_rebases_onto_and_takes_beside_the_bolt_where_it_is_read_on_github(repo, tmp_path):
    """plan.ONTO, plan.TAKE and plan.landed_at given GitHub's copy, refs/remotes/origin/bolt/<bolt> (plan.19,
    gather.bolt_read): with the host's bolt/<bolt> left behind it, a dependent's place is rebased onto GitHub's bolt,
    a place holding nothing of its own beyond GitHub's bolt takes what it comes after, and the commit that brought a
    unit's change to the bolt is found on GitHub's."""
    import plan
    repo.commit("main", {"README": "r\n"})
    origin = tmp_path / "github.git"
    repo.git("branch", "bolt/b")
    subprocess.run(["git", "clone", "-q", "--bare", str(repo.path), str(origin)], check=True)
    repo.git("remote", "add", "origin", str(origin))
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "bolt/b", str(origin), str(other)], check=True)
    o = lambda *a: subprocess.run(["git", "-C", str(other), *a], check=True, capture_output=True, text=True).stdout.strip()
    (other / "openspec" / "changes" / "a").mkdir(parents=True)
    (other / "openspec" / "changes" / "a" / "proposal.md").write_text("p\n")
    o("add", "-A"); o("commit", "-qm", "docs(a): the change")
    made = o("rev-parse", "HEAD")
    (other / "x").write_text("x\n")
    o("add", "x"); o("commit", "-qm", "feat: the bolt's own")
    o("push", "-q", "origin", "HEAD:bolt/b")
    repo.git("fetch", "-q", "origin")
    github = "refs/remotes/origin/bolt/b"
    assert repo.git("rev-parse", "bolt/b") != repo.git("rev-parse", github)
    assert plan.landed_at(str(repo.path), "b", "a", at=github) == made
    assert plan.landed_at(str(repo.path), "b", "a", at="refs/heads/bolt/b") is None
    place = tmp_path / "place"
    repo.git("worktree", "add", "-q", "-b", "unit/c", str(place), "bolt/b")
    (place / "c").write_text("c\n")
    subprocess.run(["git", "-C", str(place), "add", "c"], check=True)
    subprocess.run(["git", "-C", str(place), "commit", "-qm", "feat(c): its own"], check=True)
    r = onto(place, github)
    assert (r.returncode, r.stdout.strip()) == (0, "rebased")
    assert repo.git("merge-base", "--is-ancestor", github, "unit/c") == ""
    assert repo.git("log", "--format=%s", f"{github}..unit/c") == "feat(c): its own"
    d = tmp_path / "d"
    repo.git("worktree", "add", "-q", "-b", "unit/d", str(d), made)
    (d / "d").write_text("d\n")
    subprocess.run(["git", "-C", str(d), "add", "d"], check=True)
    subprocess.run(["git", "-C", str(d), "commit", "-qm", "feat(d): its own"], check=True)
    fresh = tmp_path / "fresh"
    repo.git("worktree", "add", "-q", "-b", "unit/e", str(fresh), github)
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(fresh), "e", "refs/heads/bolt/b", "unit/d"], capture_output=True, text=True)
    assert (took.returncode, took.stdout) == (0, ""), "read at the host's copy, GitHub's own commit counts as the place's"
    took = subprocess.run(["bash", "-c", plan.TAKE, "crew", str(fresh), "e", github, "unit/d"], capture_output=True, text=True)
    assert (took.returncode, took.stdout.split()) == (0, ["d", repo.git("rev-parse", "--short=7", "unit/d")])

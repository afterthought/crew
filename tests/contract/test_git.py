"""What crew assumes of git, each case naming what assumes it."""
import base64
import os
import shlex
import shutil
import subprocess
import time

import pytest


def test_merge_tree_names_the_conflicting_paths_and_writes_no_ref(repo):
    """plan.forecast_rows, the landings card's forecast of its rows (rail-cards "The landings card forecasts each row's
    conflicts"): git merge-tree --write-tree --name-only exits 1 on a conflict and lists the conflicting paths after
    the tree, and moves no ref."""
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


def unmerged(place):
    return subprocess.run(["git", "-C", str(place), "diff", "--name-only", "--diff-filter=U"], capture_output=True,
                          text=True).stdout.split()


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
    sluice lands submission 7 once, whichever wait on it asks first, the waiter SUBMIT leaves running or the one
    plan.WAIT runs as landing_ended does, finding the landing's place made again on bolt/b and landing from it as
    wt-submit does, and every wait on it ends with that landing's exit, plan.WAIT's handed to LANDED with its last line; and
    `sluice wait main`, which writes where it ran and what it was asked to the file followed, and ends once the file
    release is there. Each run reads the bolt's two copies and decides the head it submits first, as landing_submitted
    does (LAND_COPIES, kit.land_copies, landing_head), then runs between when given, then SUBMIT with that head and the
    copy's value as read; one run again with a submission and its tip reads nothing and gives no head. Each run is
    LANDED's result, SUBMIT's said on its standard error before LANDED's and its assignments as submit, or SUBMIT's own
    when it refused, and the commit main now was at before it."""
    import kit
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

    def land_with(path, *again, between=None):
        _, (_, before, why) = main_at(repo)
        assert not why, why
        env = dict(os.environ, PATH=path)
        head = own = ""
        if not again:
            c = subprocess.run(["bash", "-c", plan.LAND_COPIES, "crew", str(repo.path), "b", kit.DECLARATION],
                               capture_output=True, text=True, env=env)
            assert c.returncode == 0, c.stderr
            f = kit.land_copies(c.stdout, "b")
            d = plan.landing_head("b", "h", f)
            assert isinstance(d, dict), d
            head, own = (d["head"], f["own"]) if d["head"] else ("", "")
        if between:
            between()
        r = subprocess.run(["bash", "-c", plan.SUBMIT, "crew", str(repo.path), str(land), "b", "wldn-ops", head, own, *again],
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
        done = subprocess.CompletedProcess(e.args, e.returncode, e.stdout, r.stderr + e.stderr)
        done.submit = f
        return done, before

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
once="{tmp_path}/sluice-7"
if mkdir "$once" 2>/dev/null; then
  (cd "{land}" && [ "$(git symbolic-ref --short HEAD)" = bolt/b ] || exit 8
{lands}{pushed if on_github else 'git update-ref refs/heads/main "$new"'}
  ); rc=$?; echo "$rc" > "$once/rc.new" && mv "$once/rc.new" "$once/rc"; exit "$rc"
fi
n=0; while [ ! -e "$once/rc" ] && [ $n -lt 6000 ]; do sleep 0.1; n=$((n + 1)); done
exit "$(cat "$once/rc")"
''')
        shutil.rmtree(tmp_path / "sluice-7", ignore_errors=True)
        for tool in ("wt-submit", "sluice"):
            (bin_ / tool).chmod(0o755)
        return lambda *again, between=None: land_with(f"{bin_}:{os.environ['PATH']}", *again, between=between)
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
    recorded in sluice's words, from its wait's or, when sluice refused the submission at once, from what SUBMIT says it
    said: refused when sluice's record has it in conflict (rail-cards "A refused landing is held on its row"), and
    stopped when sluice gave none (plan.landing_blame)."""
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
    conflict = {"schema": plan.SUBMISSION, "id": 1, "state": "conflict", "conflict": {"paths": ["README.md"], "with": []}}
    landed, words = plan.landing_said("b", "kit", "h", r.stdout, before, doc=conflict)
    assert not landed and words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was."), words
    assert plan.landing_said("b", "kit", "h", r.stdout, before, recorded=True, doc=conflict) == (False, "sluice: bolt/b conflicts with main")
    assert plan.landing_end("b", "kit", "h", r.stdout, before)[2:] == ("sluice: bolt/b conflicts with main", True)
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


BOLTS_ON_ORIGIN = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'


def bolt_lives_on_github(repo, tmp_path, behind=2):
    """A kit whose bolt/b lives on a bare GitHub stand-in, the policy in it naming origin for it, the host's own copy at
    the bolt's first commit while GitHub's holds `behind` merges beyond it, landed there from another clone, as sluice
    0.36.4 leaves a host's copy (plan.19): (the host's copy, GitHub's head, merged), merged(n) landing n more merges on
    GitHub's bolt/b and giving its head."""
    kit_with_github(repo, tmp_path)
    repo.git("checkout", "-q", "-b", "bolt/b", "origin/main")
    own = repo.commit("chore: the bolt's policy names origin", {".config/sluice.toml": BOLTS_ON_ORIGIN})
    repo.git("checkout", "-q", "main")
    repo.git("push", "-q", "origin", "bolt/b")
    o, n = tmp_path / "other", [0]

    def git(*a):
        return subprocess.run(["git", "-C", str(o), *a], check=True, capture_output=True, text=True).stdout.strip()

    def merged(count):
        git("fetch", "-q", "origin", "bolt/b")
        git("checkout", "-q", "-B", "bolt/b", "FETCH_HEAD")
        for _ in range(count):
            n[0] += 1
            git("checkout", "-q", "-b", f"unit/u{n[0]}")
            (o / f"u{n[0]}").write_text("u\n")
            git("add", f"u{n[0]}")
            git("commit", "-qm", f"feat: u{n[0]}")
            git("checkout", "-q", "bolt/b")
            git("merge", "-q", "--no-ff", "-m", f"chore(land): #{n[0]} unit/u{n[0]}", f"unit/u{n[0]}")
        git("push", "-q", "origin", "bolt/b")
        return git("rev-parse", "HEAD")
    return own, merged(behind), merged


def sluices_guard(repo, tmp_path):
    """A stand-in for sluice's guard in the kit's main checkout (sluice protect.rs hook, plan.19): a write of
    refs/heads/bolt/b passes only when its new value is GitHub's bolt/b as the guard reads it then, by its own read of
    origin, as sluice's route reads a branch on a remote; every transaction's ref and new value logged. Returns the log."""
    log = tmp_path / "guard.log"
    guard = repo.path / ".git" / "hooks" / "reference-transaction"
    guard.parent.mkdir(exist_ok=True)
    guard.write_text(f'''#!/bin/sh
while read -r old new ref; do
  echo "$1 $ref $new" >> "{log}"
  if [ "$1" = prepared ] && [ "$ref" = refs/heads/bolt/b ]; then
    there=$(git ls-remote origin refs/heads/bolt/b); there=${{there%%[[:space:]]*}}
    [ "$new" = "$there" ] || {{ echo "bolt/b is protected by sluice" >&2; exit 1; }}
  fi
done
''')
    guard.chmod(0o755)
    log.write_text("")
    return log


def writes(log):
    """The writes of the host's bolt/b the guard was asked to let through, as (state, new value)."""
    return [(state, new) for state, ref, new in (l.split() for l in log.read_text().splitlines()) if ref == "refs/heads/bolt/b"]


def github_main(tmp_path):
    return subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-parse", "main"],
                          capture_output=True, text=True).stdout.strip()


def test_a_bolts_two_copies_are_read_after_one_fetch(repo, tmp_path):
    """plan.LAND_COPIES and kit.land_copies (plan.19, design Decision 1): the host's copy two merges behind GitHub's,
    fetched once into origin/bolt/b, is held there and lacks the two; a host with no copy reads none; a copy ahead and a
    copy diverged are read as each; GitHub without the branch or a kit with no origin reads no copy there, fetching
    nothing; a remote that can't be read gives git's words."""
    import kit
    own, there, merged = bolt_lives_on_github(repo, tmp_path)
    def read():
        r = script("LAND_COPIES", str(repo.path), "b", kit.DECLARATION)
        assert r.returncode == 0, r.stderr
        return kit.land_copies(r.stdout, "b")
    assert read() == dict(own=own, there=there, remote="origin", held="yes", ahead="no", lacks=0, beyond=2, read=None)
    assert repo.git("rev-parse", "origin/bolt/b") == there
    repo.git("branch", "-q", "-D", "bolt/b")
    assert read() == dict(own="-", there=there, remote="origin", held="yes", ahead=None, lacks=None, beyond=None, read=None)
    repo.git("branch", "-q", "bolt/b", there)
    repo.git("checkout", "-q", "bolt/b")
    repo.git("checkout", "-q", "-b", "unit/x")
    repo.commit("feat: x", {"x": "x\n"})
    repo.git("checkout", "-q", "bolt/b")
    repo.git("merge", "-q", "--no-ff", "-m", "chore(land): #9 unit/x", "unit/x")
    repo.git("checkout", "-q", "main")
    ahead = repo.git("rev-parse", "bolt/b")
    assert read() == dict(own=ahead, there=there, remote="origin", held="no", ahead="yes", lacks=1, beyond=0, read=None)
    later = merged(1)
    assert read() == dict(own=ahead, there=later, remote="origin", held="no", ahead="no", lacks=1, beyond=1, read=None)
    subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "branch", "-q", "-D", "bolt/b"], check=True)
    assert script("LAND_COPIES", str(repo.path), "b", kit.DECLARATION).stdout == "THERE=-\n"
    repo.git("remote", "set-url", "origin", str(tmp_path / "gone.git"))
    assert "gone.git" in read()["read"]
    repo.git("remote", "remove", "origin")
    assert script("LAND_COPIES", str(repo.path), "b", kit.DECLARATION).stdout == "THERE=-\n"


def test_a_landing_levels_a_copy_behind_githubs_and_submits_githubs_head(repo, tmp_path):
    """plan.SUBMIT through LAND_COPIES and landing_head (bolt-teams "The host's copy lags GitHub's"): the host's copy two
    merges behind GitHub's is set to GitHub's head by one guarded update-ref, which sluice's guard lets through, the
    landing's worktree is cut there and submitted clean, LEVEL naming the copy's old value, and GitHub's main, once
    the stand-in sluice has landed it, holds both merges the copy lacked."""
    import plan
    own, there, _ = bolt_lives_on_github(repo, tmp_path)
    log = sluices_guard(repo, tmp_path)
    _, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(on_github=True)()
    assert (r.submit["TIP"], r.submit["LEVEL"]) == (there, own), r.stdout + r.stderr
    assert ("prepared", there) in writes(log) and {v for _, v in writes(log)} == {there}, log.read_text()
    assert repo.git("rev-parse", "bolt/b") == there and (tmp_path / "status").read_text() == ""
    assert repo.git("reflog", "-1", "--format=%gs", "refs/heads/bolt/b") == "crew: level to GitHub's bolt/b for its landing"
    main = github_main(tmp_path)
    assert repo.git("rev-parse", f"{main}^2") == there
    assert subprocess.run(["git", "--git-dir", str(tmp_path / "github.git"), "rev-list", "--count", "--merges", f"{own}..{main}"],
                          capture_output=True, text=True).stdout.strip() == "3"
    assert plan.landing_said("b", "kit", "h", r.stdout, before)[0], r.stdout


def test_a_host_with_no_copy_has_one_made_at_githubs_head(repo, tmp_path):
    """plan.SUBMIT (bolt-teams "The host has no copy"): a host with no bolt/b of its own has it made at GitHub's head,
    guarded as absent, LEVEL=-, and submits that head."""
    _, there, _ = bolt_lives_on_github(repo, tmp_path)
    repo.git("branch", "-q", "-D", "bolt/b")
    log = sluices_guard(repo, tmp_path)
    _, _, stand_in = landing(repo, tmp_path)
    r, _ = stand_in(on_github=True)()
    assert (r.submit["TIP"], r.submit["LEVEL"]) == (there, "-"), r.stdout + r.stderr
    assert {v for _, v in writes(log)} == {there} and repo.git("rev-parse", "bolt/b") == there


def test_github_moved_after_the_read_refuses_the_level_and_cuts_nothing(repo, tmp_path):
    """plan.SUBMIT (bolt-teams "GitHub moved after crew read it"): GitHub's bolt/b takes another merge after the
    landing read it, so the guard, reading GitHub again, refuses the level to the head crew read; nothing is cut or
    submitted, the host's copy is where it was, and SUBMIT says so in the guard's words."""
    own, there, merged = bolt_lives_on_github(repo, tmp_path)
    sluices_guard(repo, tmp_path)
    land, _, stand_in = landing(repo, tmp_path)
    r, _ = stand_in(on_github=True)(between=lambda: merged(1))
    assert r.returncode == 2 and "bolt/b is protected by sluice" in r.stderr, r.stdout + r.stderr
    assert f"copy of bolt/b was not levelled to GitHub's {there[:7]}: " in r.stderr.strip().splitlines()[-1], r.stderr
    assert not land.exists() and repo.git("rev-parse", "bolt/b") == own
    assert not (tmp_path / "agent").exists()


def test_a_copy_that_moved_since_the_read_refuses_the_level(repo, tmp_path):
    """plan.SUBMIT (design Decision 3): the level is guarded by the copy's value as read, so a copy that moved since,
    another hand's write, makes git refuse it; nothing is cut or submitted."""
    own, there, _ = bolt_lives_on_github(repo, tmp_path)
    land, _, stand_in = landing(repo, tmp_path)
    moved = repo.git("commit-tree", "-p", own, "-m", "elsewhere", repo.git("rev-parse", f"{own}^{{tree}}"))
    r, _ = stand_in(on_github=True)(between=lambda: repo.git("update-ref", "refs/heads/bolt/b", moved))
    assert r.returncode == 2 and f"copy of bolt/b was not levelled to GitHub's {there[:7]}: " in r.stderr, r.stderr
    assert not land.exists() and repo.git("rev-parse", "bolt/b") == moved


def test_a_legacy_tip_ahead_of_githubs_is_submitted_with_no_write(repo, tmp_path):
    """plan.SUBMIT (bolt-teams "A legacy bolt's host tip is ahead of GitHub's copy"): the host's tip holds a merge
    GitHub's lacks, so the landing writes no ref and submits that tip, which GitHub's main then holds."""
    import plan
    _, there, _ = bolt_lives_on_github(repo, tmp_path, behind=0)
    repo.git("checkout", "-q", "-b", "unit/x", "bolt/b")
    repo.commit("feat: x", {"x": "x\n"})
    repo.git("checkout", "-q", "bolt/b")
    repo.git("merge", "-q", "--no-ff", "-m", "chore(land): #9 unit/x", "unit/x")
    tip = repo.git("rev-parse", "HEAD")
    repo.git("checkout", "-q", "main")
    log = sluices_guard(repo, tmp_path)
    _, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(on_github=True)()
    assert (r.submit["TIP"], r.submit["LEVEL"]) == (tip, ""), r.stdout + r.stderr
    assert writes(log) == [] and repo.git("rev-parse", "bolt/b") == tip != there
    assert repo.git("rev-parse", f"{github_main(tmp_path)}^2") == tip
    assert plan.landing_said("b", "kit", "h", r.stdout, before)[0], r.stdout


def test_a_landing_worktree_that_stands_is_brought_to_githubs_head(repo, tmp_path):
    """plan.SUBMIT (bolt-teams "A landing worktree that stands from before"): <kit>/places/land-b stands on bolt/b at the
    host's old copy from an earlier attempt; once the copy is levelled its files are brought to GitHub's head by
    read-tree -m -u, writing no ref, and it is submitted clean there; one holding a change git would overwrite submits
    nothing, in git's words."""
    own, there, merged = bolt_lives_on_github(repo, tmp_path)
    land = tmp_path / "places" / "land-b"
    repo.git("worktree", "add", "-q", "--no-checkout", str(land), "bolt/b")
    subprocess.run(["git", "-C", str(land), "read-tree", "-m", "-u", "HEAD"], check=True)
    assert not (land / "u1").exists()
    log = sluices_guard(repo, tmp_path)
    _, _, stand_in = landing(repo, tmp_path)
    r, _ = stand_in(on_github=True)()
    assert (r.submit["TIP"], r.submit["LEVEL"]) == (there, own), r.stdout + r.stderr
    assert {v for _, v in writes(log)} == {there} and (tmp_path / "status").read_text() == ""
    repo.git("worktree", "add", "-q", "--no-checkout", str(land), "bolt/b")
    subprocess.run(["git", "-C", str(land), "read-tree", "-m", "-u", "HEAD"], check=True)
    later = merged(1)
    (land / "u3").write_text("mine\n")
    r, _ = stand_in(on_github=True)()
    assert r.returncode == 2 and f"the landing's worktree {land} could not be brought to {later[:7]}: " in r.stderr, r.stderr
    assert (land / "u3").read_text() == "mine\n"


def test_a_wait_on_an_earlier_submission_levels_nothing(repo, tmp_path):
    """plan.SUBMIT (design Decision 3): given a submission and the tip it submitted, the landing waits on it again with
    no head, so nothing is read or levelled, even with GitHub's bolt/b moved on since, and TIP is the tip given."""
    import plan
    own, there, merged = bolt_lives_on_github(repo, tmp_path)
    log = sluices_guard(repo, tmp_path)
    land, _, stand_in = landing(repo, tmp_path)
    r, before = stand_in(on_github=True, failing=True)()
    assert "RC=3 " in r.stdout and plan.sluice_failed(r.stdout, before) == there, r.stdout + r.stderr
    merged(1)
    log.write_text("")
    r, _ = stand_in(on_github=True)("7", there)
    assert (r.submit["RC"], r.submit["TIP"], r.submit["LEVEL"]) == ("0", there, ""), r.stdout + r.stderr
    assert writes(log) == [] and repo.git("rev-parse", "bolt/b") == there


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
    r = subprocess.run(["bash", "-c", plan.SUBMIT, "crew", str(repo.path), str(land), "b", "wldn-ops", "", ""], capture_output=True,
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
    assert os.path.realpath(ran_in) == os.path.realpath(land) and asked == ["wait", "main", "--timeout", "9m", "--json"]
    assert plan.landing_now(t, "b") == (str(land), True, True)
    release.write_text("")
    while plan.landing_now(t, "b")[2] and time.monotonic() < end:
        time.sleep(0.1)
    assert plan.landing_now(t, "b") == (str(land), True, False)


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


def work_kit(repo, monkeypatch):
    """A kit whose main checkout is repo, built by one team on this host, and bolt/z cut from main holding its own
    commit; bolt_work reads the bolt there, a kit with no origin reading its own main (plan.bolt_work)."""
    import crew
    monkeypatch.setattr(crew, "this_host", lambda: "here")
    kit = {"name": "k", "repo": "o/k", "main": str(repo.path), "dir": str(repo.path.parent)}
    fleet = {"partitions": {"p": {"label": "p", "machine": "here", "teams": ["k-1"]}},
             "teams": {"k-1": {"name": "k-1", "label": "p", "machine": "here", "kit": kit}}, "hosts": {}}
    repo.commit("chore: start", {"a.txt": "one\n"})
    repo.git("switch", "-q", "-c", "bolt/z")
    repo.commit("feat: the bolt's own", {"a.txt": "one, as the bolt has it\n"})
    repo.git("switch", "-q", "main")
    return fleet


def own_work(fleet, sent):
    import plan
    got = plan.bolt_work(fleet, "p", "k", {"z": (sent[:7], None)})["z"]
    assert got["why"] is None, got["why"]
    return [s for _, s in got["gained"]], [s for _, s in got["lost"]]


def merged_in(repo, branch, message, resolved=None):
    """branch merged into the branch checked out with --no-ff, a conflict resolved in the merge commit as resolved
    says, {path: text}."""
    r = subprocess.run(["git", "-C", str(repo.path), "merge", "-q", "--no-ff", branch, "-m", message], capture_output=True, text=True)
    if r.returncode:
        assert resolved, r.stdout + r.stderr
        for name, text in resolved.items():
            (repo.path / name).write_text(text)
            repo.git("add", "--", name)
        repo.git("commit", "-q", "--no-edit")
    return repo.git("rev-parse", "HEAD")


def test_a_bolt_that_took_main_in_with_a_conflict_resolved_holds_the_same_work_of_its_own(repo, monkeypatch):
    """plan.bolt_work (rail-cards, Decision 1): a take-main fix merges main, resolving a conflict in its merge commit,
    and sluice merges the fix into the bolt with --no-ff: git log --no-merges both ways, main excluded, lists nothing,
    so the user's send at the bolt's old head stands."""
    fleet = work_kit(repo, monkeypatch)
    sent = repo.git("rev-parse", "bolt/z")
    repo.commit("feat: main's own", {"a.txt": "one, as main has it\n"})
    repo.git("switch", "-q", "-c", "fix/z/take-main", "bolt/z")
    merged_in(repo, "main", "Merge main", {"a.txt": "one, as both have it\n"})
    repo.git("switch", "-q", "bolt/z")
    merged_in(repo, "fix/z/take-main", "Merge fix/z/take-main")
    assert repo.git("rev-parse", "bolt/z") != sent
    assert own_work(fleet, sent) == ([], [])


def test_a_fix_that_commits_a_change_is_work_the_bolt_gained(repo, monkeypatch):
    """plan.bolt_work (rail-cards "A fix adds a commit"): the fix's own commit is listed as gained, by its subject."""
    fleet = work_kit(repo, monkeypatch)
    sent = repo.git("rev-parse", "bolt/z")
    repo.git("switch", "-q", "-c", "fix/z/lease", "bolt/z")
    repo.commit("fix: keep the lease", {"lease.txt": "kept\n"})
    repo.git("switch", "-q", "bolt/z")
    merged_in(repo, "fix/z/lease", "Merge fix/z/lease")
    assert own_work(fleet, sent) == (["fix: keep the lease"], [])


def test_two_take_main_merges_from_one_tip_neither_an_ancestor_of_the_other_hold_the_same_work(repo, monkeypatch):
    """plan.bolt_work (rail-cards "The host's copy is brought level", plan.19's e104bcf and d64278b): the host's copy
    took main in at one commit and GitHub's at a later one, from the same tip, so neither head is an ancestor of the
    other; neither holds a non-merge commit of its own the other and main lack."""
    fleet = work_kit(repo, monkeypatch)
    tip = repo.git("rev-parse", "bolt/z")
    repo.commit("feat: main's first", {"b.txt": "b\n"})
    repo.git("switch", "-q", "--detach", tip)
    host = merged_in(repo, "main", "Merge main into the host's copy")
    repo.git("switch", "-q", "main")
    repo.commit("feat: main's second", {"c.txt": "c\n"})
    repo.git("switch", "-q", "bolt/z")
    github = merged_in(repo, "main", "Merge main into GitHub's copy")
    for one, other in ((host, github), (github, host)):
        assert subprocess.run(["git", "-C", str(repo.path), "merge-base", "--is-ancestor", one, other]).returncode == 1
    assert own_work(fleet, host) == ([], [])


def runner_files(host, answers="", places=""):
    """A runner's branch as a host's runner writes it (runner.RUNNER, ANSWERS, PLACES)."""
    import runner
    return {"runner.rec": runner.RUNNER + f"\nHost: {host}\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n",
            "answers.rec": runner.ANSWERS + answers, "places.rec": runner.PLACES + places}


def test_the_runners_branches_come_with_the_flywheels_branch_in_one_fetch_and_each_hosts_is_read_at_its_tip(state, monkeypatch):
    """plan.tip_of's fetch of <label>/main brings <label>/runner/* with it (plan.beside, plan.12), and plan.runners reads
    each host's three files at its tip in crew's cache with no fetch of its own, checked by recfix (Decision 4 of
    teams-cross-to-flume-as-their-bolts-land): deneb's answer and place for request 3 are read; alpha, which has no
    branch, is named; a host whose file recfix refuses hides only its own work; and a host's branch gone from the
    repository is gone from the cache at the next fetch."""
    import json
    import plan
    import runner
    status = json.dumps({"status": {"places": [{"place": "/crew/places/change--a", "phase": "live"}], "host": {}}})
    deneb = state.push("madswan/runner/deneb", runner_files(
        "deneb", "\nRequest: 3\nOutcome: launched\nPlace: /crew/places/change--a\nAt: 2026-10-31T12:01:00Z\n",
        f"\nRequest: 3\nPlace: /crew/places/change--a\nAt: 2026-10-31T12:02:00Z\nStatus: {status}\n"))
    state.push("madswan/runner/gamma", dict(runner_files("gamma"), **{"answers.rec": runner.ANSWERS + "\nRequest: 1\nOutcome: queued\nAt: 2026-10-31T12:01:00Z\n"}))
    state.push("swancloud/runner/deneb", runner_files("deneb"))  # another partition's runner on the same repository
    fetches = []
    git = plan.git
    monkeypatch.setattr(plan, "git", lambda repo, *args, **k: (fetches.append(args) if args[0] == "fetch" else None, git(repo, *args, **k))[1])

    reads = plan.runners(state.REPO, state.LABEL)
    assert len(fetches) == 1 and "+refs/heads/madswan/runner/*:refs/crew/madswan/runner/*" in fetches[0] and "--prune" in fetches[0]
    assert sorted(reads) == ["deneb", "gamma"]
    d = reads["deneb"]
    assert (d["why"], d["tip"], d["runner"].get("Version")) == (None, deneb, "0.1.0")
    assert d["answers"][3].get("Outcome") == "launched" and d["places"][3]["status"] == json.loads(status)
    assert reads["gamma"]["why"].startswith("gamma's runner can't be read: madswan/runner/gamma at ")
    assert "answers.rec fails recfix --check" in reads["gamma"]["why"]
    assert runner.of_host(reads, state.LABEL, "alpha")["why"] == "no runner answers on alpha: madswan/runner/alpha does not exist"
    assert plan.runners(state.REPO, state.LABEL) is reads and len(fetches) == 1

    state.drop("madswan/runner/gamma")
    plan.tip_of(state.REPO, "madswan/main", fresh=True)
    plan.READ.memory.clear()
    assert sorted(plan.runners(state.REPO, state.LABEL)) == ["deneb"]
    subprocess.run(["git", "-C", str(plan.cache(state.REPO)), "pack-refs", "--all"], check=True)
    plan.READ.memory.clear()
    assert plan.runner_tips(state.REPO, state.LABEL) == {"deneb": deneb}


def test_main_holds_reads_gits_exit_for_each_commit_a_crossed_bolts_places_landed_at(repo):
    """plan.MAIN_HOLDS, which a crossed bolt's close reads (plan.main_holds, runner.unlanded; Decision 12 of
    teams-cross-to-flume-as-their-bolts-land): git merge-base --is-ancestor exits 0 for a commit main holds, the bolt's
    merge landed there, 1 for one on a bolt that has not landed, and neither for a commit the checkout lacks, which crew
    reads as untold (read.1)."""
    import plan
    repo.commit("chore: start", {"README.md": "r\n"})
    repo.git("checkout", "-q", "-b", "bolt/x")
    landed = repo.commit("feat: a", {"a": "a\n"})
    repo.git("checkout", "-q", "-b", "bolt/y", "main")
    waiting = repo.commit("feat: b", {"b": "b\n"})
    repo.git("checkout", "-q", "main")
    repo.git("merge", "-q", "--no-ff", "-m", "chore(land): x", "bolt/x")
    gone = "0" * 40
    r = subprocess.run(["bash", "-c", plan.MAIN_HOLDS, "crew", str(repo.path), "main", landed, waiting, gone], capture_output=True, text=True)
    assert r.returncode == 0
    said = dict(l.split() for l in r.stdout.splitlines())
    assert (said[landed], said[waiting]) == ("0", "1") and said[gone] not in ("0", "1")


def change_files(out):
    """CHANGE_AT's output as plan.change_at reads it: [(path under the change, content)], in the order printed."""
    parts = out.split("\0")
    return list(zip(parts[0:-1:2], parts[1::2]))


def test_a_change_is_read_at_its_commit_open_or_archived_and_markdown_alone(repo):
    """plan.CHANGE_AT, which a batch's reading reads each unit's change with (batch_folder_write, change_at): a unit
    given through Flume is batched once its change is archived on its bolt, at the commit holding it so, and its change
    is read there from the archive's dated folder, as an open change is read from its own; a file not Markdown is left
    out, and a commit holding no change by the name prints nothing."""
    open_at = repo.commit("docs(a): the change", {"openspec/changes/a/proposal.md": "# a\n", "openspec/changes/a/tasks.md": "- [ ] 1.1 x\n",
                                                  "openspec/changes/a/.openspec.yaml": "schema: spec-driven\n"})
    r = script("CHANGE_AT", str(repo.path), open_at, "a")
    assert r.returncode == 0 and change_files(r.stdout) == [("proposal.md", "# a\n"), ("tasks.md", "- [ ] 1.1 x\n")]
    (repo.path / "openspec/changes/archive").mkdir()
    repo.git("mv", "openspec/changes/a", "openspec/changes/archive/2026-10-31-a")
    archived = repo.commit("docs(a): archive the change")
    r = script("CHANGE_AT", str(repo.path), archived, "a")
    assert r.returncode == 0 and change_files(r.stdout) == [("proposal.md", "# a\n"), ("tasks.md", "- [ ] 1.1 x\n")]
    r = script("CHANGE_AT", str(repo.path), archived, "b")
    assert (r.returncode, r.stdout) == (0, "")

"""What crew assumes of git, each case naming what assumes it."""
import subprocess


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


def here():
    import crew
    return {}, {"machine": crew.this_host()}


def test_commits_beyond_reads_each_commits_message_and_author_whole(repo):
    """plan.commits_beyond, which carry_refusal judges by (plan.8): oldest first, a message of several lines whole."""
    import plan
    base = repo.commit("main", {"a": "1\n"})
    repo.commit("feat: one\n\nWhy, over\ntwo lines.", {"a": "2\n"})
    repo.commit("feat: two", {"b": "1\n"})
    fleet, t = here()
    got = plan.commits_beyond(fleet, t, str(repo.path), base, "HEAD")
    assert [c["subject"] for c in got] == ["feat: one", "feat: two"]
    assert got[0]["who"] == ("Crew Test", "test@crew.invalid", "feat: one\n\nWhy, over\ntwo lines.\n")
    assert got[0]["short"] == got[0]["sha"][:7]


def test_a_patch_id_holds_for_a_replay_and_changes_with_its_context(repo):
    """plan.patch_ids, which changed_by_resolution counts by: a commit replayed onto the same lines keeps its patch id;
    one replayed where main rewrote the lines around it gets another; an empty commit has none."""
    import plan
    twenty = "".join(f"{i}\n" for i in range(1, 21))
    base = repo.commit("main", {"twenty": twenty})
    repo.git("checkout", "-q", "-b", "bolt")
    ten = repo.commit("feat: ten", {"twenty": twenty.replace("\n10\n", "\nten\n")})
    empty = repo.commit("chore: empty")
    repo.git("checkout", "-q", "-b", "same", base)
    repo.git("cherry-pick", "--allow-empty", ten, empty)
    same_ten, same_empty = repo.git("rev-parse", "HEAD~1"), repo.git("rev-parse", "HEAD")
    repo.git("checkout", "-q", "-b", "moved", base)
    around = "".join(f"main {i}\n" if i in (7, 8, 9, 11, 12, 13) else f"{i}\n" for i in range(1, 21))
    repo.commit("docs: main's lines around ten", {"twenty": around})
    moved_base = repo.git("rev-parse", "HEAD")
    moved_ten = repo.commit("feat: ten", {"twenty": around.replace("\n10\n", "\nten\n")})
    fleet, t = here()
    ids = plan.patch_ids(fleet, t, str(repo.path), base, "bolt", "same")
    assert ids[ten] == ids[same_ten]
    assert empty not in ids and same_empty not in ids
    moved = plan.patch_ids(fleet, t, str(repo.path), moved_base, "moved")
    assert moved[moved_ten] != ids[ten]


def bolt_and_fix(repo):
    """main, a bolt of two commits beyond it, and a fix holding them replayed onto main moved on, plus one of its own."""
    base = repo.commit("main", {"a": "1\n"})
    repo.git("checkout", "-q", "-b", "bolt")
    repo.commit("feat: one", {"one": "1\n"})
    repo.commit("feat: two", {"two": "2\n"})
    repo.git("checkout", "-q", "main")
    main = repo.commit("docs: main moves", {"m": "m\n"})
    repo.git("checkout", "-q", "-b", "fix", "bolt")
    repo.git("rebase", "-q", "main")
    repo.commit("fix: one of its own", {"own": "o\n"})
    return base, main


def test_range_diff_is_printed_as_the_reading(repo, capsys):
    """plan.range_reading (plan.8): git range-diff of the two sides beyond main, printed whole on standard error under
    a line saying it judges nothing; a commit only the fix has shows as added."""
    import plan
    _, main = bolt_and_fix(repo)
    fleet, t = here()
    plan.range_reading(fleet, t, str(repo.path), main, repo.git("rev-parse", "bolt"), repo.git("rev-parse", "fix"), "b", "fix/b/f")
    err = capsys.readouterr().err
    assert err.startswith("git range-diff main..bolt/b main..fix/b/f, the reading, which judges nothing")
    own = repo.git("rev-parse", "--short=7", "fix")
    assert f"-:  ------- > 3:  {own} fix: one of its own" in err


def test_a_range_diff_that_fails_is_named_in_gits_words_without_its_usage(repo, capsys):
    """plan.range_reading: git range-diff refuses a range that is not one (here an unknown commit), and crew names it
    in git's first paragraph, never the usage git prints after it, and judges as before."""
    import plan
    _, main = bolt_and_fix(repo)
    fleet, t = here()
    plan.range_reading(fleet, t, str(repo.path), main, "0" * 40, repo.git("rev-parse", "fix"), "b", "fix/b/f")
    err = capsys.readouterr().err
    assert err.startswith("git range-diff main..bolt/b main..fix/b/f could not be read: ")
    assert "usage:" not in err


def rebase(repo, tmp_path, unit, src, to):
    """plan.REBASE as crew unit move runs it in the unit's place: <place> <from bolt> <to bolt> <unit>."""
    import plan
    return subprocess.run(["bash", "-c", plan.REBASE, "crew", str(tmp_path / "place"), src, to, unit], capture_output=True, text=True)


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


def fresh(repo):
    import plan
    return subprocess.run(["bash", "-c", plan.FRESH, "crew", str(repo.path)], capture_output=True, text=True)


def behind(repo):
    import plan
    return subprocess.run(["bash", "-c", plan.BEHIND, "crew", str(repo.path)], capture_output=True, text=True)


def test_a_bolt_is_cut_from_githubs_main_and_a_clean_main_behind_it_fast_forwarded(repo, tmp_path):
    """plan.fresh_base (plan.8): a host's kit main lags GitHub's; the bolt is cut from origin/main, fetched first."""
    kit_with_github(repo, tmp_path)("from-a-mac")
    r = fresh(repo)
    assert (r.returncode, r.stdout.strip(), r.stderr.strip()) == (0, "origin/main", "main fast-forwarded 1 commit to GitHub's")
    assert repo.git("rev-parse", "main") == repo.git("rev-parse", "origin/main")


def test_a_main_holding_all_of_githubs_and_more_cuts_the_bolt_from_itself(repo, tmp_path):
    kit_with_github(repo, tmp_path)
    repo.commit("feat: local", {"local": "l\n"})
    r = fresh(repo)
    assert (r.stdout.strip(), r.stderr.strip()) == ("main", "main holds 1 commit GitHub's main does not yet have; the bolt is cut from them")


def test_a_main_gone_its_own_way_is_refused_and_a_dirty_one_left_as_it_is(repo, tmp_path):
    pushed = kit_with_github(repo, tmp_path)
    repo.commit("feat: local", {"local": "l\n"}); pushed("another")
    r = fresh(repo)
    assert r.returncode == 1 and r.stderr.strip() == (
        "main on this host has 1 commit of its own and lacks 1 commit of GitHub's: rebase it onto origin/main first, and never push it with force")
    repo.git("rebase", "-q", "origin/main"); repo.git("push", "-q", "origin", "main")
    (repo.path / "README.md").write_text("wip\n"); pushed("yet-another")
    r = fresh(repo)
    assert (r.stdout.strip(), r.stderr.strip()) == ("origin/main", "main is 1 commit behind GitHub's and was left as it is "
                                                     "(another branch is checked out there, or it has uncommitted changes)")


def test_a_landing_reads_how_far_main_is_from_githubs(repo, tmp_path):
    """plan.bolt_land (plan.8): refused while the kit's main is behind GitHub's; a kit with no origin says nothing."""
    assert behind(repo).stdout == ""
    pushed = kit_with_github(repo, tmp_path)
    repo.commit("feat: local", {"local": "l\n"}); pushed("later")
    assert behind(repo).stdout.strip() == "1 1"

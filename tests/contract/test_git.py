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

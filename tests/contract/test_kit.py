"""What crew assumes of bash and git when it makes a worktree ready through its kit's declaration (kit.py, plan.17):
the kept toolchain is sourced by the bash on PATH, whatever bash 4 syntax it holds; and the worktree's own git
directory, where the toolchain is kept, goes with the worktree."""
import pathlib
import subprocess

import kit


def test_a_toolchain_with_bash_4_syntax_is_sourced_by_the_bash_on_path(tmp_path):
    # devenv print-dev-env's output holds a case fall-through, `;&`, which macOS's /bin/bash 3.2 cannot parse
    # (sluice 9cf83c9); kit.in_toolchain sources it with the bash on PATH.
    script = tmp_path / "toolchain.sh"
    script.write_text('echo "setting up" \ncase x in x) export PICKED=one ;& y) export PICKED="$PICKED two" ;; esac\n'
                      'export TOOL_FROM=toolchain\n')
    r = subprocess.run(kit.in_toolchain(str(script), ["sh", "-c", 'echo "$TOOL_FROM $PICKED"']), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout == "toolchain one two\n"
    assert "setting up" in r.stderr


def test_the_kept_toolchain_goes_with_its_worktree(repo, tmp_path):
    # make_place keeps the toolchain under `git rev-parse --absolute-git-dir` of the worktree, outside its tree,
    # so git status there never shows it and removing the worktree removes it.
    repo.commit("chore: start", {"README.md": "r\n"})
    place = tmp_path / "places" / "a"
    repo.git("worktree", "add", "-q", "-b", "unit/a", str(place))
    gitdir = subprocess.run(["git", "-C", str(place), "rev-parse", "--absolute-git-dir"], capture_output=True, text=True).stdout.strip()
    kept = pathlib.Path(gitdir) / "crew" / "toolchain.sh"
    kept.parent.mkdir(parents=True)
    kept.write_text("export X=1\n")
    assert subprocess.run(["git", "-C", str(place), "status", "--porcelain"], capture_output=True, text=True).stdout == ""
    repo.git("worktree", "remove", str(place))
    assert not kept.exists()

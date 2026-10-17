"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host."""
import plan

OLD, NEW = "a" * 40, "b" * 40


def said(rc, new=NEW, kept="''", level="yes"):
    return f"RC={rc} OLD={OLD} NEW={new} KEPT={kept} LEVEL={level}\n"


def test_a_landing_says_where_main_is_and_what_comes_next():
    assert plan.landing_said("b", "switchboard-kit", said(0)) == (
        True, "bolt/b landed on switchboard-kit's main at bbbbbbb: push main, then crew bolt land b.")


def test_a_main_checkout_not_brought_level_is_named_with_the_command():
    landed, words = plan.landing_said("b", "k", said(0, level="'git read-tree could not bring it level'"))
    assert landed and words.endswith("k's main checkout was not brought level (git read-tree could not bring it level): "
                                     "git read-tree -m -u aaaaaaa main there.")


def test_a_conflict_lands_nothing_and_is_the_bolts_to_take():
    landed, words = plan.landing_said("b", "k", said(2, new=OLD))
    assert not landed
    assert words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
    assert "the team takes main into it by a submission to the bolt" in words


def test_checks_that_failed_land_nothing():
    assert plan.landing_said("b", "k", said(1, new=OLD))[1].startswith("bolt/b did not land: main's checks failed on it")


def test_a_worktree_git_could_not_remove_is_named():
    assert plan.landing_said("b", "k", said(2, new=OLD, kept="/k/places/land-b"))[1].endswith(
        "Its worktree /k/places/land-b is kept: remove it once you have read why.")


def test_words_crew_cannot_read_land_nothing():
    assert plan.landing_said("b", "k", "wt: command not found\n") == (
        False, "crew can't read what the submission of bolt/b to k's main came to: wt: command not found")


def test_the_anchor_is_detached_and_the_landing_says_nothing_of_levelling_it():
    """bolt-teams "The anchor is detached" (plan.18): the fleet's timer moves a detached main checkout, so a landing
    neither levels it nor says anything of it."""
    landed, words = plan.landing_said("b", "k", said(0, level="detached"))
    assert landed and "level" not in words and "read-tree" not in words

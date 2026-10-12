"""Whether a fix carries its bolt onto main (plan.8, teams.5): plan.carry_refusal and plan.changed_by_resolution, on
the commits each side holds beyond main. The move and its record are the journey's (t-journey-units)."""
from facts import commit, replayed

import plan

THREE, TEN = commit("feat: three"), commit("feat: ten")
BOLT = [THREE, TEN]


def refusal(bolt, fix, holds=False):
    return plan.carry_refusal("tenant-environments", holds, bolt, fix)


def test_a_fix_holding_the_bolts_head_merges_as_a_fix():
    assert refusal(BOLT, BOLT, holds=True) == "it holds the bolt's head"


def test_a_bolt_with_nothing_beyond_main_is_carried_by_nothing():
    assert refusal([], [replayed(TEN)]) == "bolt/tenant-environments has no commits beyond main"


def test_a_fix_with_nothing_beyond_main_carries_nothing():
    assert refusal(BOLT, []) == "it has no commits beyond main"


def test_the_bolts_commits_replayed_in_order_carry_it():
    assert refusal(BOLT, [replayed(THREE), replayed(TEN)]) is None


def test_a_reworded_commit_is_not_the_bolts_and_both_are_named():
    fix = [replayed(THREE), replayed(TEN, subject="feat: ten, reworded")]
    assert refusal(BOLT, fix) == (f"the bolt's commit {TEN['short']} (feat: ten) is not in it; "
                                  f"its commit {fix[1]['short']} (feat: ten, reworded) is none of the bolt's")


def test_a_re_authored_commit_is_not_the_bolts():
    fix = [replayed(THREE), replayed(TEN, author=("Bob", "bob@example.com"))]
    assert refusal(BOLT, fix) == (f"the bolt's commit {TEN['short']} (feat: ten) is not in it; "
                                  f"its commit {fix[1]['short']} (feat: ten) is none of the bolt's")


def test_the_bolts_commits_in_another_order_do_not_carry_it():
    assert refusal(BOLT, [replayed(TEN), replayed(THREE)]) == "its commits are the bolt's in another order"


def test_a_commit_of_the_fixs_own_is_named():
    own = commit("fix: something else")
    assert refusal(BOLT, [replayed(THREE), replayed(TEN), own]) == f"its commit {own['short']} (fix: something else) is none of the bolt's"


def test_a_dropped_commit_is_named():
    assert refusal(BOLT, [replayed(TEN)]) == f"the bolt's commit {THREE['short']} (feat: three) is not in it"


def test_several_missing_commits_are_named_together():
    other = commit("feat: other")
    assert refusal(BOLT, [other]) == (f"the bolt's commits {THREE['short']} (feat: three), {TEN['short']} (feat: ten) are not in it; "
                                      f"its commit {other['short']} (feat: other) is none of the bolt's")


def test_changed_by_resolution_counts_the_replays_whose_patch_differs():
    fix = [replayed(THREE), replayed(TEN)]
    ids = {THREE["sha"]: "p3", fix[0]["sha"]: "p3", TEN["sha"]: "p10", fix[1]["sha"]: "p10-in-mains-context"}
    assert plan.changed_by_resolution(BOLT, fix, ids) == 1


def test_a_commit_whose_patch_is_empty_on_both_sides_is_unchanged():
    fix = [replayed(THREE), replayed(TEN)]
    assert plan.changed_by_resolution(BOLT, fix, {THREE["sha"]: "p3", fix[0]["sha"]: "p3"}) == 0

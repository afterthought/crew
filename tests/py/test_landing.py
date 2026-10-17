"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host."""
import plan

OLD, NEW = "a" * 40, "b" * 40


def said(rc, new=NEW, kept="''", level="yes"):
    return f"RC={rc} OLD={OLD} NEW={new} KEPT={kept} LEVEL={level}\n"


def test_a_landing_says_where_main_is_and_what_comes_next():
    assert plan.landing_said("b", "switchboard-kit", said(0)) == (
        True, "bolt/b landed on switchboard-kit's main at bbbbbbb: now crew bolt land b.")


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


def test_the_hosts_main_lags_githubs_and_nothing_is_refused_for_it():
    """bolt-teams "Main is behind GitHub's" (plan.8, plan.18): the landing reads only the commit GitHub's main holds
    after a fetch, which it records, and a host's own main lagging it refuses nothing."""
    github, own = "d" * 40, "e" * 40
    assert plan.main_held("k", "chuck-herdr-alpha", f"ORIGIN=yes\nFETCHED=ok\nGITHUB={github}\nOWN={own}\n") == (github, None)


class TestTheCardsClose:
    """crew bolt land closes the bolt's landing card on its team's host (plan.16, record 0032 §3): with where GitHub's
    main holds the landing and that every host's folder follows by the timer, under whichever landing key the conductor
    holds one."""

    def test_the_card_closes_naming_githubs_main_sluices_submission_and_the_timer(self):
        assert plan.landed_words("c" * 40, "46") == (
            "landed on GitHub's main at ccccccc (#46); every host's folder follows by swancloud's timer within minutes")

    def test_a_head_sluice_did_not_make_is_named_without_a_number(self):
        for n in ("", None, "46 47", "x"):
            assert plan.landed_words("c" * 40, n) == (
                "landed on GitHub's main at ccccccc; every host's folder follows by swancloud's timer within minutes")

    def test_the_conductors_open_cards_under_the_bolts_landing_keys_old_and_new(self):
        post = lambda key, card, by="swb-1-conductor": {"Act": "card.post", "Key": key, "Card": card, "By": by}
        entries = [post("land/b/abc1234", "req_1"), post("land/b", "req_2"), post("land/b/abc9999", "req_3"),
                   {"Act": "card.close", "Card": "req_3", "Key": "land/b/abc9999", "By": "swb-1-conductor"},
                   post("land/b", "req_4", by="swb-2-conductor"), post("land/bb", "req_5"), post("proposal/1", "req_6")]
        assert plan.landing_card_keys(entries, "b", "swb-1-conductor") == ["land/b", "land/b/abc1234"]
        assert plan.landing_card_keys(entries, "c", "swb-1-conductor") == []

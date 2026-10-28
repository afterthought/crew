"""The console's tabs (the operator-agent spec, The console opens with its shell alone and The console keeps the tabs it
has open): plan.console_tabs on the tabs named, the tabs the console's panes file records with whether herdr still has
each pane, and who follows on the host; and plan.console_asked on the words after the label. That crew console up opens
what the decision names is the main journey's (t-journey-main)."""
import pytest

from crew import Refusal

import plan


def tabs(asked=(), recorded=None, follower="job"):
    return plan.console_tabs(set(asked), recorded or {}, follower)


def test_a_first_up_while_the_hosts_job_follows_opens_the_shell_tab_alone():
    assert tabs() == (["shell"], [], [])


def test_a_first_up_while_no_one_follows_opens_the_shell_and_the_rail_tab_whose_loop_follows():
    assert tabs(follower="none") == (["shell", "rail"], [], [])


def test_a_rail_tab_following_is_no_job_so_the_rail_tab_opens():
    assert tabs(follower="tab") == (["shell", "rail"], [], [])


def test_a_follower_crew_cant_read_is_no_job_so_the_rail_tab_opens():
    assert tabs(follower="unknown") == (["shell", "rail"], [], [])


def test_the_rail_named_while_the_job_follows_opens_beside_the_shell():
    assert tabs(["rail"]) == (["shell", "rail"], [], [])


def test_tabs_named_open_in_the_order_flow_rail_board_after_the_shell():
    assert tabs(["board", "flow", "rail"]) == (["shell", "flow", "rail", "board"], [], [])


def test_a_second_up_keeps_every_open_tab_and_opens_nothing():
    assert tabs(recorded={"shell": True, "rail": True}) == ([], ["shell", "rail"], [])
    assert tabs(recorded={"shell": True, "flow": True, "rail": True, "board": True}) == ([], ["shell", "flow", "rail", "board"], [])


def test_a_console_opened_before_its_shell_tab_keeps_its_tabs_and_gains_the_shell():
    assert tabs(recorded={"flow": True, "rail": True, "board": True}) == (["shell"], ["flow", "rail", "board"], [])


def test_a_board_tab_the_user_closed_is_forgotten_and_not_opened_again():
    assert tabs(recorded={"shell": True, "board": False}) == ([], ["shell"], ["board"])


def test_a_closed_tab_named_again_is_opened_again():
    assert tabs(["board"], {"shell": True, "board": False}) == (["board"], ["shell"], [])


def test_a_closed_rail_tab_opens_again_while_no_job_follows_and_is_forgotten_while_one_does():
    assert tabs(recorded={"shell": True, "rail": False}, follower="none") == (["rail"], ["shell"], [])
    assert tabs(recorded={"shell": True, "rail": False}) == ([], ["shell"], ["rail"])


def test_a_shell_tab_the_user_closed_opens_again():
    assert tabs(recorded={"shell": False, "rail": True}) == (["shell"], ["rail"], [])


def test_the_words_after_the_label_are_the_tabs_in_any_order():
    assert plan.console_asked([]) == set()
    assert plan.console_asked(["board", "flow"]) == {"flow", "board"}


@pytest.mark.parametrize("words, said", [(["page"], "crew console up opens the tabs flow, rail and board; there is no tab page"),
                                         (["shell"], "crew console up opens the tabs flow, rail and board; there is no tab shell"),
                                         (["rail", "rail"], "crew console up names the rail tab twice")])
def test_a_word_that_is_no_tab_or_a_tab_named_twice_is_refused(words, said):
    with pytest.raises(Refusal, match=said):
        plan.console_asked(words)

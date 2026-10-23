"""plan.py builds only the command a run names (plan.parser with only): each run parses as the whole parser does."""
import pytest

import plan

RUNS = [
    ["bolts", "--label", "wldn", "--json"],
    ["bolt", "new", "tenant-environments", "Tenants hold environments.", "--repo", "switchboard-kit"],
    ["bolt", "order", "b", "--first"],
    ["rail", "--label", "wldn"],
    ["card", "sweep", "--label", "wldn"],
    ["state", "init", "wldn"],
    ["_team", "restart", "swb-1", "ops", "--no-greet"],
    ["bolt", "submit", "b", "--label", "wldn"],
    ["bolt", "submit", "b", "--excerpt", "Land crw-5's bolt"],
    ["_unit-run", "a", "construct", "--force", "--", "-x is the tenant"],
    ["_fix-run", "swb-1", "tidy", "wait", "--timeout", "0"],
]


@pytest.mark.parametrize("argv", RUNS, ids=lambda a: " ".join(a[:2]))
def test_a_run_parses_as_the_whole_parser_parses_it(argv):
    whole = plan.parser().parse_args(argv)
    ap = plan.parser(only=argv[0])
    assert argv[0] in ap.built
    assert vars(ap.parse_args(argv)) == vars(whole)


def test_a_landing_takes_the_users_words_and_has_none_by_default():
    """plan.16: the word to land given in ops's pane goes with the submission; without it, the word is the card's."""
    assert plan.parser().parse_args(["bolt", "submit", "b", "--excerpt", "Land it"]).excerpt == "Land it"
    assert plan.parser().parse_args(["bolt", "submit", "b"]).excerpt is None


def test_a_name_that_is_no_command_is_not_built():
    assert "no-such-command" not in plan.parser(only="no-such-command").built


def test_a_unit_is_given_no_approval_to_run(capsys):
    """plan.6: a unit whose change is committed goes on to code with no approval, so there is no command to give one."""
    with pytest.raises(SystemExit):
        plan.parser(only="unit").parse_args(["unit", "approve", "c"])
    assert "invalid choice: 'approve'" in capsys.readouterr().err

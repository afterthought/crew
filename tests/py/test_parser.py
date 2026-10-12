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
    ["_prove", "swb-1", "--wait", "--timeout", "0", "--stuck", "60000"],
    ["_unit-run", "a", "construct", "--force", "--", "-x is the tenant"],
    ["_fix-run", "swb-1", "tidy", "wait", "--timeout", "0"],
]


@pytest.mark.parametrize("argv", RUNS, ids=lambda a: " ".join(a[:2]))
def test_a_run_parses_as_the_whole_parser_parses_it(argv):
    whole = plan.parser().parse_args(argv)
    ap = plan.parser(only=argv[0])
    assert argv[0] in ap.built
    assert vars(ap.parse_args(argv)) == vars(whole)


def test_a_name_that_is_no_command_is_not_built():
    assert "no-such-command" not in plan.parser(only="no-such-command").built


def test_a_unit_is_given_no_approval_to_run(capsys):
    """plan.6: a unit whose change is committed goes on to code with no approval, so there is no command to give one."""
    with pytest.raises(SystemExit):
        plan.parser(only="unit").parse_args(["unit", "approve", "c"])
    assert "invalid choice: 'approve'" in capsys.readouterr().err

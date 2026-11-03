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
    ["_sweep", "wldn", "switchboard-kit", "--dir", "/kit", "--landed", "b", "--outcome", "Landed.", "--units", "a", "c"],
    ["bolt", "submit", "b", "--label", "wldn"],
    ["bolt", "submit", "b", "--excerpt", "Land crw-5's bolt"],
    ["bolt", "leave", "b", "c", "--excerpt", "Hold the phone bolt", "--label", "wldn"],
    ["fix", "x", "rail-word", "Say land.", "--label", "madswan"],
    ["fix", "x", "rail-word", "--drop"],
    ["_console", "up", "wldn"],
    ["_console", "up", "wldn", "rail", "board"],
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


def test_a_stop_takes_the_users_words_and_none_is_refused(capsys):
    """main-level "A landing stopped in ops's pane is recorded as the user's words": a stop is only ever on them."""
    assert plan.parser().parse_args(["bolt", "leave", "b", "--excerpt", "Hold it"]).excerpt == "Hold it"
    with pytest.raises(SystemExit):
        plan.parser().parse_args(["bolt", "leave", "b"])
    assert "--excerpt" in capsys.readouterr().err


def test_a_name_that_is_no_command_is_not_built():
    assert "no-such-command" not in plan.parser(only="no-such-command").built


def test_a_unit_is_given_no_approval_to_run(capsys):
    """plan.6: a unit whose change is committed goes on to code with no approval, so there is no command to give one."""
    with pytest.raises(SystemExit):
        plan.parser(only="unit").parse_args(["unit", "approve", "c"])
    assert "invalid choice: 'approve'" in capsys.readouterr().err

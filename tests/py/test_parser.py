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
    ["kit", "rename", "tailrace", "timber", "--label", "madswan"],
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


def test_a_kits_rename_is_a_plan_command_a_proposal_may_hold():
    """Decision 2 of a-kit-renamed-on-its-host-is-renamed-across-the-plan: crew kit rename <old> <new>, with --label,
    parsed by the command line's own grammar on the command line and in a proposal's Do (plan.3), its act kit.rename,
    a refusal's entry naming kit/<old>."""
    a = plan.parser().parse_args(["kit", "rename", "tailrace", "agentplot/timber", "--label", "madswan"])
    assert (a.cmd, a.sub, a.old, a.new, a.label) == ("kit", "rename", "tailrace", "agentplot/timber", "madswan")
    d = plan.do_args("madswan", "crew kit rename flywheel-cloud boomdrive-cloud")
    assert (d.cmd, d.sub, d.old, d.new, d.label) == ("kit", "rename", "flywheel-cloud", "boomdrive-cloud", "madswan")
    assert ("kit", "rename") in plan.PROPOSABLE and ("kit", "rename") in plan.PLAN_WRITES
    assert plan.ACTS[("kit", "rename")] == "kit.rename" and plan.named(a) == ["kit/tailrace"]
    assert plan.do_named(d) == "kit rename flywheel-cloud boomdrive-cloud" and plan.summary([d]) == "rename kit flywheel-cloud boomdrive-cloud"
    assert plan.objects([d]) == ["kit/boomdrive-cloud", "kit/flywheel-cloud"]


@pytest.mark.parametrize("old, new", [("Tailrace", "timber"), ("tailrace", "agentplot/timber/x"), ("tailrace", "timber_2"), ("tail.race", "timber")])
def test_a_kit_named_otherwise_than_crew_names_one_is_refused(old, new, capsys):
    """code.4: a kit is named by its name, lowercase words with dashes, or <owner>/<name>, on the command line and in a
    proposal's Do alike."""
    with pytest.raises(SystemExit):
        plan.parser().parse_args(["kit", "rename", old, new])
    assert "a kit is named by its name" in capsys.readouterr().err
    with pytest.raises(plan.Refusal, match="a kit is named by its name, lowercase words with dashes, or <owner>/<name>"):
        plan.do_args("madswan", f"kit rename {old} {new}")

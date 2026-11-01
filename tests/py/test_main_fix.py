"""A red main's fix is a Flume fix place on main (Decision 11 of teams-cross-to-flume-as-their-bolts-land, the main-level
spec's "A red main's fix is a fix place on main where a crossed team builds the kit", state.3): plan.main_fix_change
on a write of madswan's plan, with crw-4 crossed to Flume in stream madswan and crw-5 on today's path, both building
crew on deneb (facts.crossed_fleet); runner.main_fixer and runner.main_fix_launch for the team and the launch. That
crew main fix reaches the plan from the command line, on the stubs, is t-journey-main-fix's."""
import pytest

import plan
import runner
from facts import FactsWrite, crossed_fleet, flume_plan, ran

WORDS = "tests:logic failed on main after landing x: tests/py/test_rail.py::TestRows reads a fixture that is gone."


@pytest.fixture(autouse=True)
def ops(monkeypatch):
    monkeypatch.setenv("CREW_AGENT", "madswan-ops")


def write(bolts=(), runners=None):
    """madswan's plan with its bolts, each (name, team, Path), and deneb's runner as given, answering by default."""
    return FactsWrite(flume_plan(bolts), runners=ran() if runners is None else runners, label="madswan")


def requests(w):
    return [{f: v for f, v in r.fields if f not in ("Date", "By")} for r in plan.Plan(w.files["requests.rec"]).recs("Request")]


class TestLaunch:
    def test_main_red_after_a_landing_is_a_fix_place_on_main_held_for_the_users_send_with_ops_its_recipient(self):
        """The spec's "Main red after a landing": ops runs crew main fix crew a-test-reads-its-fixture "<words>"."""
        w = write()
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "start", WORDS) == dict(
            n=1, host="deneb", stream="madswan")
        assert requests(w) == [{
            "Request": "1", "Act": "launch", "Host": "deneb", "Work": "fix/main/crew/a-test-reads-its-fixture", "Repo": "afterthought/crew",
            "Kind": "fix", "Name": "main--a-test-reads-its-fixture", "Base": "main", "Stream": "madswan", "Priority": "1",
            "Intent": "madswan/main/crew", "Recipient": "madswan/ops", "Hold": "submission", "Brief": WORDS}]
        assert w.subject == "plan(main): fix a-test-reads-its-fixture of crew"

    def test_its_priority_is_above_every_bolt_given_through_flume(self):
        w = write([("x", "crw-4", "flume"), ("y", "crw-4", "flume"), ("z", "crw-5", None)])
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert requests(w)[0]["Priority"] == "3"
        assert runner.priority_of(w.plan, "x") == 2

    def test_a_name_in_use_on_the_kits_main_is_refused(self):
        w = write()
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        with pytest.raises(plan.Refusal, match=r"^fix red of crew's main is in use: it is launched as Flume place main--red \(request 1\), "
                                               r"so name this fix differently$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", "Again.")

    def test_no_runner_answering_on_the_teams_host_is_refused_naming_state_3s_way(self):
        w = write(runners={})
        with pytest.raises(plan.Refusal, match="^no runner answers on deneb: madswan/runner/deneb does not exist, so nothing would launch "
                                               "the fix there; until the runner \\(flywheel-runner\\) serves madswan there, a fix of crew's red "
                                               "main is a bolt of one chore, proposed first among the planned \\(state.3\\); tell "
                                               "madswan-planner, who proposes it$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert "requests.rec" not in w.files


class TestWhichTeam:
    NONE = ("^no team of madswan builds crew in a Flume stream, so a fix of its red main is no Flume place: it is a bolt of one "
            "chore, proposed first among the planned, which the dispatcher gives to the next team that frees \\(state.3\\); tell "
            "madswan-planner, who proposes it$")

    def test_no_team_builds_the_kit_in_a_stream_and_it_is_refused_naming_a_bolt_of_one_chore(self):
        """The spec's "No runner keeps the kit with a stream", read until 5.2 as no team naming a stream."""
        w = write()
        with pytest.raises(plan.Refusal, match=self.NONE):
            plan.main_fix_change(crossed_fleet(**{"crw-4": False}), w, "crew", "gate-word", "start", WORDS)
        assert "requests.rec" not in w.files

    def test_a_team_holding_a_bolt_given_before_flume_builds_the_fix_all_the_same(self):
        """crw-4 names a stream while it holds x, given before it was given through Flume: no path holds it back."""
        w = write([("x", "crw-4", None)], runners=ran())
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "gate-word", "start", WORDS) == dict(n=1, host="deneb", stream="madswan")

    def test_teams_on_one_host_launch_on_it_in_the_first_by_names_stream(self):
        fleet = crossed_fleet(**{"crw-5": "late"})
        assert runner.main_fixer(fleet["teams"], "madswan", "crew", "deneb") == ("crw-4", None)
        assert runner.main_fixer(fleet["teams"], "madswan", "crew", "mac-studio") == ("crw-4", None)

    def test_teams_on_several_hosts_launch_on_the_main_levels_and_none_of_them_it_is_refused_naming_them(self):
        """Decisions 4 and 15 of the-team-machinery-leaves: crew main fix takes no --team; among several hosts the
        partition's main-level host is the one, and with none of them it crew guesses none (read.1)."""
        fleet = crossed_fleet(**{"crw-5": "late"})
        fleet["teams"]["crw-5"]["machine"] = "alpha"
        assert runner.main_fixer(fleet["teams"], "madswan", "crew", "deneb") == ("crw-4", None)
        assert runner.main_fixer(fleet["teams"], "madswan", "crew", "alpha") == ("crw-5", None)
        assert runner.main_fixer(fleet["teams"], "madswan", "crew", "mac-studio") == (
            None, "crw-4 and crw-5 build crew through Flume on alpha and deneb, none of them madswan's main-level host mac-studio, "
                  "so crew can't tell the one host a fix of its main runs on")
        fleet["partitions"]["madswan"]["machine"] = "alpha"
        w = write(runners=ran(host="alpha"))
        assert plan.main_fix_change(fleet, w, "crew", "red", "start", WORDS) == dict(n=1, host="alpha", stream="late")


class TestDrop:
    def test_drop_drops_its_launch(self):
        w = write(runners=ran({1: "code"}))
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "red", "drop", None) == dict(n=2, host="deneb", stream="madswan")
        assert requests(w)[1] == {"Request": "2", "Act": "drop", "Host": "deneb", "Work": "fix/main/crew/red", "Of": "1"}
        assert w.subject == "plan(main): drop fix red of crew"

    @pytest.mark.parametrize("at, said", [
        ("landed", "^fix/main/crew/red has merged into main, so it is not dropped: what it changed is main's, and a new fix undoes it$"),
        (None, "^can't tell whether fix/main/crew/red's place has merged into main, so it is not dropped: no runner answers on deneb")])
    def test_a_landed_fix_or_one_crew_cant_read_is_not_dropped(self, at, said):
        w = write()
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        w = FactsWrite(w.plan.text(), files=w.files, runners=ran({1: at}) if at else {}, label="madswan")
        with pytest.raises(plan.Refusal, match=said):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "drop", None)

    def test_a_fix_with_no_launch_is_not_there_to_drop(self):
        with pytest.raises(plan.Refusal, match="^crew has no fix fix/main/crew/red: no launch of it stands in requests.rec$"):
            plan.main_fix_change(crossed_fleet(), write(), "crew", "red", "drop", None)


class TestSend:
    """The main-level spec's "The user's send": once the runner's record shows the fix's code delivered and its
    submission held (tests/py/flume-0.3.6/held.json), ops's crew main fix crew <name> --send on the user's send appends
    the retry of its submission, once."""
    def launched(self, at="held"):
        """crew main fix crew a-test-reads-its-fixture launched as request 1, deneb's runner showing its place at the flume
        fixture named."""
        w = write(runners=ran({1: at}))
        plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "start", WORDS)
        return w

    def test_the_users_send_appends_the_retry_of_its_submission(self):
        w = self.launched()
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None) == dict(
            n=2, host="deneb", stream="madswan")
        assert requests(w)[1] == {"Request": "2", "Act": "retry", "Host": "deneb", "Work": "fix/main/crew/a-test-reads-its-fixture",
                                  "Of": "1", "Submission": "yes"}
        assert w.subject == "plan(main): send fix a-test-reads-its-fixture of crew"

    def test_a_send_is_made_once(self):
        w = self.launched()
        plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)
        with pytest.raises(plan.Refusal, match="^fix/main/crew/a-test-reads-its-fixture was sent on the user's word by request 2, which "
                                               "the runner on deneb acts on, so it is not sent twice$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)

    def test_a_send_the_runner_refused_is_made_again_and_one_crew_cant_read_stands(self):
        reading = ran({1: "held"})["deneb"]
        reading["answers"][2] = plan.Rec("Answer", [("Request", "2"), ("Outcome", "refused"), ("At", "2026-10-31T12:03:00Z")])
        rs = [plan.Rec("Request", [("Request", "1"), ("Act", "launch"), ("Work", "fix/main/crew/x")]),
              plan.Rec("Request", [("Request", "2"), ("Act", "retry"), ("Of", "1"), ("Submission", "yes")])]
        assert runner.sent_of(rs, reading, rs[0]) is None
        assert runner.sent_of(rs, dict(reading, why="unread"), rs[0]) is rs[1]

    def test_a_fix_whose_code_has_not_delivered_is_not_sent(self):
        w = self.launched("code")
        with pytest.raises(plan.Refusal, match=r"^fix/main/crew/a-test-reads-its-fixture's place \S+ is at code, and a fix of main is sent "
                                               r"only once its code has delivered and its submission waits held$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)

    def test_one_crew_cant_read_or_with_no_launch_is_not_sent(self):
        w = self.launched()
        w.runner_of = lambda host: runner.of_host({}, "madswan", host)
        with pytest.raises(plan.Refusal, match="^can't tell whether fix/main/crew/a-test-reads-its-fixture's submission waits held, so it "
                                               "is not sent: no runner answers on deneb"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)
        with pytest.raises(plan.Refusal, match="^no launch of fix/main/crew/red stands in requests.rec, so there is no fix of main to send$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "send", None)


class TestCommand:
    def test_crew_main_fix_is_its_own_row_of_the_role_table(self, monkeypatch):
        """Decision 16: main-level ops and the user run it; a conductor or the planner is refused, told ops runs it."""
        fleet = dict(crossed_fleet(), partitions={"madswan": {"label": "madswan", "teams": ["crw-4", "crw-5"], "roles": {}}})
        a = plan.parser().parse_args(["main", "fix", "crew", "red", WORDS])
        assert (a.cmd, a.sub, a.kit, a.name, a.words, a.drop) == ("main", "fix", "crew", "red", WORDS, False)
        with pytest.raises(SystemExit):
            plan.parser().parse_args(["main", "fix", "crew", "red", WORDS, "--team", "crw-4"])
        plan.may_write(fleet, ("main", "fix"), a)
        monkeypatch.setenv("CREW_AGENT", "madswan-planner")
        with pytest.raises(plan.Refusal, match="^madswan-planner does not run crew main fix: main-level ops and the user do; tell madswan-ops$"):
            plan.may_write(fleet, ("main", "fix"), a)

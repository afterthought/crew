"""A red main's fix is a Flume fix place on main (Decision 11 of teams-cross-to-flume-as-their-bolts-land, Decision 15 of
the-team-machinery-leaves, state.3): plan.main_fix_change on a write of madswan's plan, the launch in crew's repository
naming no team, host or stream, taken by a runner whose configuration names it (the user's ruling of 2026-11-01;
runner.main_fix_launch), deneb's runner answering for madswan by default (facts.ran). That crew main fix reaches the plan
from the command line, on the stubs, is t-journey-main-fix's."""
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
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "start", WORDS) == dict(n=1, host=None)
        assert requests(w) == [{
            "Request": "1", "Act": "launch", "Work": "fix/main/crew/a-test-reads-its-fixture", "Repo": "crew",
            "Kind": "fix", "Name": "main--a-test-reads-its-fixture", "Base": "main", "Priority": "1",
            "Intent": "madswan/main/crew", "Recipient": "madswan/ops", "Hold": "submission", "Brief": WORDS}]
        assert w.subject == "plan(main): fix a-test-reads-its-fixture of crew"

    def test_its_priority_is_above_every_started_bolt(self):
        """x and y are started and z planned: the fix goes above x and y, and z counts for nothing."""
        w = write([("x", None, "flume"), ("y", None, "flume"), ("z", None, None)])
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert requests(w)[0]["Priority"] == "3"
        assert runner.priority_of(w.plan, "x") == 2

    def test_a_name_in_use_on_the_kits_main_is_refused(self):
        w = write()
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        with pytest.raises(plan.Refusal, match=r"^fix red of crew's main is in use: it is launched as Flume place main--red \(request 1\), "
                                               r"so name this fix differently$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", "Again.")

    def test_no_runner_answering_for_the_partition_is_refused_naming_state_3s_way(self):
        w = write(runners={})
        with pytest.raises(plan.Refusal, match="^no runner answers for madswan: its state repository holds no madswan/runner/<host>, so "
                                               "nothing would take the fix; until a runner \\(flywheel-runner\\) serves madswan, a fix of "
                                               "crew's red main is a bolt of one chore, proposed first among the planned \\(state.3\\); "
                                               "tell madswan-planner, who proposes it$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert "requests.rec" not in w.files


class TestDrop:
    def test_drop_drops_its_launch(self):
        w = write(runners=ran({1: "code"}))
        plan.main_fix_change(crossed_fleet(), w, "crew", "red", "start", WORDS)
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "red", "drop", None) == dict(n=2, host="deneb")
        assert requests(w)[1] == {"Request": "2", "Act": "drop", "Work": "fix/main/crew/red", "Of": "1"}
        assert w.subject == "plan(main): drop fix red of crew"

    @pytest.mark.parametrize("at, said", [
        ("landed", "^fix/main/crew/red has merged into main, so it is not dropped: what it changed is main's, and a new fix undoes it$"),
        (None, "^can't tell whether fix/main/crew/red's place has merged into main, so it is not dropped: no runner answers for the partition")])
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
        assert plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None) == dict(n=2, host="deneb")
        assert requests(w)[1] == {"Request": "2", "Act": "retry", "Work": "fix/main/crew/a-test-reads-its-fixture", "Of": "1",
                                  "Submission": "yes"}
        assert w.subject == "plan(main): send fix a-test-reads-its-fixture of crew"

    def test_a_send_is_made_once(self):
        w = self.launched()
        plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)
        with pytest.raises(plan.Refusal, match="^fix/main/crew/a-test-reads-its-fixture was sent on the user's word by request 2, which "
                                               "the runner that took it acts on, so it is not sent twice$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)

    def test_a_send_the_runner_refused_is_made_again_and_one_crew_cant_read_stands(self):
        reading = ran({1: "held"})["deneb"]
        reading["answers"][2] = plan.Rec("Answer", [("Request", "2"), ("Outcome", "refused"), ("At", "2026-10-31T12:03:00Z")])
        rs = [plan.Rec("Request", [("Request", "1"), ("Act", "launch"), ("Work", "fix/main/crew/x")]),
              plan.Rec("Request", [("Request", "2"), ("Act", "retry"), ("Of", "1"), ("Submission", "yes")])]
        assert runner.sent_of(rs, {"deneb": reading}, rs[0]) is None
        assert runner.sent_of(rs, {"deneb": dict(reading, why="unread")}, rs[0]) is rs[1]

    def test_a_fix_whose_code_has_not_delivered_is_not_sent(self):
        w = self.launched("code")
        with pytest.raises(plan.Refusal, match=r"^fix/main/crew/a-test-reads-its-fixture's place \S+ is at code, and a fix of main is sent "
                                               r"only once its code has delivered and its submission waits held$"):
            plan.main_fix_change(crossed_fleet(), w, "crew", "a-test-reads-its-fixture", "send", None)

    def test_one_crew_cant_read_or_with_no_launch_is_not_sent(self):
        w = self.launched()
        w.runners = lambda: {}
        with pytest.raises(plan.Refusal, match="^can't tell whether fix/main/crew/a-test-reads-its-fixture's submission waits held, so it "
                                               "is not sent: no runner answers for the partition"):
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

"""A fix of a started bolt (bolt-teams "A fix is a fix place on its bolt", Decision 15 of the-team-machinery-leaves,
teams.3): crew fix <bolt> <name> "<words>" a launch of Flume's fix kind on the bolt's branch (plan.fix_flume,
runner.fix_launch), dropped by --drop (runner.fix_drop_refusal), merged and waited on by Flume alone, holding the
bolt's landing while it is in flight (runner.fixes_in_flight). That the command writes the launch and starts no
agent is the crossed path's journey's (t-journey-cross)."""
import pytest

from facts import FactsWrite, crossed_fleet, flume_plan, ran

import plan
import runner


class TestAFixOfAStartedBolt:
    @pytest.fixture(autouse=True)
    def planner(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-planner")
        self.FLEET = crossed_fleet()

    def bolt(self, runners=None, work=("a",)):
        """x, started through crw-4, crossed in stream madswan on deneb, its units launched as the start launches them."""
        w = FactsWrite(flume_plan([("x", None, None)], [(u, "x", [], "unit", []) for u in work]), runners=runners, label="madswan")
        b = w.plan.bolt("x")
        b.set("Team", "crw-4")
        b.set("Path", "flume", after="Team")
        plan.reach_places(self.FLEET, w, "x", dict(self.FLEET["teams"]["crw-4"]))
        return w

    def fix(self, w, mode, name, words=""):
        return plan.fix_flume(self.FLEET, w, "x", mode, name, words)

    def launches(self, w):
        return [{f: v for f, v in r.fields if f not in ("Date", "By")} for r in plan.Plan(w.files["requests.rec"]).recs("Request")]

    def test_a_review_note_marked_fix_is_a_launch_of_a_fix_on_the_bolts_branch(self):
        """The planner runs crew fix x rail-word "Say 'land' for a started bolt" on a batch's note."""
        w = self.bolt()
        assert self.fix(w, "start", "rail-word", "Say 'land' for a started bolt") == dict(n=2, host="deneb", stream="madswan")
        assert self.launches(w)[1] == {
            "Request": "2", "Act": "launch", "Host": "deneb", "Work": "fix/x/rail-word", "Repo": "afterthought/crew", "Kind": "fix",
            "Name": "x--rail-word", "Base": "bolt/x", "Stream": "madswan", "Priority": "1", "Intent": "madswan/x",
            "Recipient": "madswan/planner", "Brief": "Say 'land' for a started bolt"}
        assert w.subject == "plan(x): fix rail-word"

    def test_a_name_in_use_on_the_bolt_is_refused(self):
        w = self.bolt()
        self.fix(w, "start", "rail-word", "Say land.")
        with pytest.raises(plan.Refusal, match=r"^fix rail-word is in use on bolt x: it is launched as Flume place x--rail-word \(request 2\), "
                                               r"so name this fix differently$"):
            self.fix(w, "start", "rail-word", "Again.")

    def test_drop_drops_its_launch(self):
        w = self.bolt(runners=ran({2: "code"}))
        self.fix(w, "start", "rail-word", "Say land.")
        assert self.fix(w, "drop", "rail-word") == dict(n=3, host="deneb", stream="madswan")
        assert self.launches(w)[2] == {"Request": "3", "Act": "drop", "Host": "deneb", "Work": "fix/x/rail-word", "Of": "2"}
        assert w.subject == "plan(x): drop fix rail-word"

    @pytest.mark.parametrize("at, said", [
        ("landed", "^fix/x/rail-word has merged into bolt/x, so it is not dropped: what it changed is the bolt's, and a new fix undoes it$"),
        (None, "^can't tell whether fix/x/rail-word's place has merged into bolt/x, so it is not dropped: no runner answers on deneb")])
    def test_a_merged_fix_or_one_crew_cant_read_is_not_dropped(self, at, said):
        w = self.bolt(runners=ran({2: at}) if at else None)
        self.fix(w, "start", "rail-word", "Say land.")
        with pytest.raises(plan.Refusal, match=said):
            self.fix(w, "drop", "rail-word")

    def test_a_fix_with_no_launch_is_not_there_to_drop(self):
        with pytest.raises(plan.Refusal, match="^bolt x has no fix fix/x/gap: no launch of it stands in requests.rec$"):
            self.fix(self.bolt(), "drop", "gap")

    def test_a_bolt_not_started_has_no_fix(self):
        w = FactsWrite(flume_plan([("x", None, None)], [("a", "x", [], "unit", [])]), label="madswan")
        with pytest.raises(plan.Refusal, match="^bolt x has not been started, so a fix of it has no Flume place to run in$"):
            self.fix(w, "start", "gap", "A gap.")

    @pytest.mark.parametrize("argv", [["fix", "x", "rail-word", "--merge"], ["fix", "x", "rail-word", "--wait"],
                                      ["fix", "x", "rail-word", "Words.", "--bolt", "x"]])
    def test_merge_wait_and_bolt_are_no_options_it_has(self, argv):
        with pytest.raises(SystemExit):
            plan.parser().parse_args(argv)

    def test_a_fix_in_flight_holds_the_bolts_landing_until_it_has_merged_or_been_dropped(self):
        """Fixes rail-word in code, tidy merged, gone dropped by crew and stray on a host crew can't read."""
        w = self.bolt(runners=ran({2: "code", 3: "landed"}))
        for name in ("rail-word", "tidy", "gone"):
            self.fix(w, "start", name, f"Fix {name}.")
        self.fix(w, "drop", "gone")
        requests = plan.Plan(w.files["requests.rec"]).recs("Request")
        assert runner.fixes_in_flight(requests, ran({2: "code", 3: "landed"}), "madswan", "x") == {"fix/x/rail-word": "Fix rail-word."}
        assert runner.fixes_in_flight(requests, {}, "madswan", "x") == {"fix/x/rail-word": "Fix rail-word.", "fix/x/tidy": "Fix tidy."}
        assert plan.landing_unready([("a", "unit", "merged")], "h" * 40, "passed", ["fix/x/rail-word"]) == "fix/x/rail-word is in flight on it"
        row = plan.landing_rows(["x"], {"x": {"head": "h" * 40, "fixes": {"fix/x/rail-word": "Fix rail-word."}}}, {})[0]
        assert (row["box"], row["why"]) == (False, "held for a fix: Fix rail-word. (fix/x/rail-word)")

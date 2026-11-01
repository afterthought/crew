"""A team's work through Flume (record 0050 parts 2 and 3, the change teams-cross-to-flume-as-their-bolts-land; Decisions 1
and 14 of the-team-machinery-leaves): a team runs no standing agent, every standing-agent or slot command of it refused; a
start launches its bolt whole; plan writes reach its places; a place is answered by a retry. The commands that act on it are
the cross journey's (t-journey-cross)."""
import re

import pytest

from facts import flume_plan, madswan_fleet
import plan
import runner

CREW = "crew"


def team(flume, name="crw-4"):
    return {"name": name, "flume": flume, "label": "madswan", "machine": "deneb"}


# ------------------------------------------------------------------------------------- a crossed team's bolt launched

FLEET = madswan_fleet()


def unit(name, bolt="x", after=(), kind="unit", sources=()):
    return (name, bolt, list(after), kind, list(sources))


@pytest.fixture(autouse=True)
def writer(monkeypatch):
    monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")


def requests(w):
    """requests.rec as the write leaves it: each request's fields but its Date and By, as {field: value or [values]}."""
    out = []
    for r in plan.Plan(w.files.get("requests.rec") or runner.REQUESTS).recs("Request"):
        d = {}
        for f, v in r.fields:
            if f not in ("Date", "By"):
                d[f] = d[f] + [v] if f == "After" and f in d else [v] if f == "After" else v
        out.append(d)
    return out


def launch(n, work, name, after=(), kind="change", bolt="x", priority="1", brief=None):
    """A launch request as a start writes it, in crew's repository as the plan names it and naming no host or stream,
    for a runner whose configuration names it to take (the user's ruling of 2026-11-01)."""
    d = {"Request": str(n), "Act": "launch", "Work": work, "Repo": CREW, "Kind": kind, "Name": name,
         "Base": f"bolt/{bolt}", "Priority": priority, "Intent": f"madswan/{bolt}", "Recipient": "madswan/planner"}
    if after:
        d["After"] = [str(a) for a in after]
    d["Brief"] = brief or f"Build {name}."
    return d


def given(*bolts, work=(), files=None, runners=None):
    """A write over madswan's plan, each bolt as (name, started, Path or None) (facts.flume_plan)."""
    from facts import FactsWrite
    return FactsWrite(flume_plan(bolts, work), files=files, runners=runners, label="madswan")


def start(w, bolt):
    """What a start's change function does once sluice made the branch (plan.op_bolt_start): Path: flume set, no Team,
    and the bolt's work launched in its repository (plan.reach_places)."""
    w.plan.bolt(bolt).set("Path", "flume")
    return plan.reach_places(FLEET, w, bolt)


class TestStart:
    """A start launches its bolt whole (Decision 5 of teams-cross-to-flume-as-their-bolts-land, Decision 14 of
    the-team-machinery-leaves): a launch per unit and chore, in the file's order, each after the launches of its After
    work, with no team on the bolt and no bound for the bolts already started."""

    def test_a_bolt_of_three(self):
        """crew bolt start x, x holding units a and b, b after a, and chore c: three launches of change, change and
        chore on bolt/x, b's naming a's as its After, and the bolt marked started with no Team."""
        w = given(("x", None, None), work=[unit("a", sources=["signals/s1", "README.md"]), unit("b", after=["a"]), unit("c", kind="chore")])
        assert start(w, "x") == [(1, "unit/a"), (2, "unit/b"), (3, "chore/c")]
        assert requests(w) == [launch(1, "unit/a", "a", brief="Build a. Sources: signals/s1; README.md."),
                               launch(2, "unit/b", "b", after=[1]), launch(3, "chore/c", "c", kind="chore")]
        assert (w.plan.bolt("x").get("Team"), w.plan.bolt("x").get("Path")) == (None, "flume")
        assert plan.started(w.plan.bolt("x"))

    def test_a_dependent_listed_first_is_launched_after_its_after_work(self):
        w = given(("x", None, None), work=[unit("b", after=["a"]), unit("a")])
        assert start(w, "x") == [(1, "unit/a"), (2, "unit/b")]
        assert requests(w)[1]["After"] == ["1"]

    def test_a_chores_brief_is_its_words_alone(self):
        w = given(("x", None, None), work=[unit("c", kind="chore", sources=["signals/s1"])])
        start(w, "x")
        assert requests(w)[0]["Brief"] == "Build c."

    def test_a_third_bolt_started_has_its_launches_follow_the_requests_already_written(self):
        """x and y are started, each with work launched, and z is started: z is launched, nothing refused for x and y."""
        w = given(("x", None, None), ("y", None, None), ("z", None, None),
                  work=[unit("a"), unit("b", bolt="y"), unit("c", bolt="z")])
        start(w, "x")
        start(w, "y")
        assert start(w, "z") == [(4, "unit/c")]
        assert [r["Act"] for r in requests(w)] == ["launch", "launch", "priority", "launch", "priority", "priority"]

    def test_a_start_with_no_runner_for_the_partition_is_refused_naming_it(self):
        """The state repository holds no madswan/runner/<host> at all: nothing would take the bolt's work."""
        assert runner.runnerless("madswan", {}) == (
            "no runner answers for madswan: its state repository holds no madswan/runner/<host>, so nothing would take the bolt's "
            "work; a start waits for a runner (flywheel-runner) to serve the partition")
        assert runner.runnerless("madswan", {"alpha": "a" * 40}) is None

    def test_what_the_start_says_names_each_launch_and_that_no_agent_starts(self):
        assert plan.launched_said("crew", "x", [(1, "unit/a"), (2, "chore/c")]) == (
            "no agent starts: unit/a (request 1), chore/c (request 2) is launched in crew, for a runner whose configuration "
            "names it to take, in the stream its host maps it to, and crew bolts shows their places")


def ops(w, *dos, stages=None, n=None):
    """Plan commands applied to the write as a proposal holds them, in madswan's partition (facts.apply)."""
    from facts import apply, known
    return apply(w, *dos, ctx=known(w, stages=stages, n=n, fleet=FLEET))


def launched(*bolts, work=(), runners=None):
    """A write over a plan whose bolts are each started, their work launched as the start launches it."""
    w = given(*[(b, None, None) for b in bolts], work=work, runners=runners)
    for b in bolts:
        start(w, b)
    return w


class TestReach:
    """A plan write reaches a crossed team's places as its own act (Decision 7): added or moved-in work launched, dropped
    work and a dropped bolt's places dropped, and a move out, a split or a change of After of launched work refused."""

    def test_a_unit_added_to_a_crossed_bolt_is_launched_after_the_launch_of_its_after_work(self):
        w = launched("x", work=[unit("a")])
        ops(w, 'unit add b "Build b." --bolt x --after a', 'chore add c "Build c." --bolt x')
        assert requests(w)[1:] == [launch(2, "unit/b", "b", after=[1]), launch(3, "chore/c", "c", kind="chore")]

    def test_work_added_to_a_bolt_not_started_or_the_queue_is_not_launched(self):
        w = given(("x", None, None), work=[unit("a")])
        ops(w, 'unit add b "Build b." --bolt x', f'unit add q "Build q." --repo {CREW}')
        assert "requests.rec" not in w.files

    def test_a_unit_moved_in_from_the_queue_is_launched(self):
        w = launched("x", work=[unit("a"), unit("q", bolt=None)])
        ops(w, "unit move q x")
        assert requests(w)[1] == launch(2, "unit/q", "q")

    def test_launched_work_moved_out_is_refused_naming_its_place_and_drop_then_add(self):
        """A proposal moves a, launched on crossed crw-4's x, to bolt y."""
        w = launched("x", work=[unit("a")])
        w.plan.insert(plan.Rec("Bolt", [("Bolt", "y"), ("Repo", CREW), ("Goal", "Goal of y.")]))
        with pytest.raises(plan.Refusal, match=r"^unit a is launched as Flume place a on bolt/x \(request 1\), whose base and order are fixed "
                                               r"at its launch, so it is not moved to y: drop it \(crew unit drop a\) and add it again as it "
                                               r"should be \(crew unit add\)$"):
            ops(w, "unit move a y")

    def test_a_split_of_launched_work_is_refused(self):
        w = launched("x", work=[unit("a")])
        with pytest.raises(plan.Refusal, match=r"^unit a is launched as Flume place a .* so it is not split: drop it"):
            ops(w, 'unit split a "Half of a." --into a2 "The other half."')

    def test_a_change_of_after_of_launched_work_is_refused_and_one_that_changes_nothing_passes(self):
        def bolt():
            return launched("x", work=[unit("a"), unit("b", after=["a"]), unit("c")])
        with pytest.raises(plan.Refusal, match=r"^unit b is launched as Flume place b .* so it is not put after a, c: drop it"):
            ops(bolt(), "unit after b a c")
        with pytest.raises(plan.Refusal, match=r"so it is not put after nothing"):
            ops(bolt(), "unit after b --none")
        w = bolt()
        before = w.files["requests.rec"]
        ops(w, "unit after b a")
        assert w.files["requests.rec"] == before

    def test_a_unit_dropped_drops_its_launch_and_a_dependent_held_for_it_is_launched_again_without_it(self):
        """The user approves dropping c, launched on crossed crw-4's x."""
        w = launched("x", work=[unit("a"), unit("c"), unit("b", after=["a", "c"])])
        ops(w, 'unit drop c "Not needed."')
        assert [(r["Request"], r["Act"], r["Work"], r.get("Of"), r.get("After")) for r in requests(w)[3:]] == [
            ("4", "drop", "unit/c", "2", None), ("5", "drop", "unit/b", "3", None), ("6", "launch", "unit/b", None, ["1"])]

    def test_a_dropped_bolt_drops_every_place_it_launched_and_requeued_too(self):
        w = launched("x", work=[unit("a"), unit("c", kind="chore")])
        w.files["requests.rec"] += "\n" + "\n".join(plan.Rec("Request", runner.request_fields(
            3, "launch", "fix/x/tidy", dict(launch(3, "fix/x/tidy", "x--tidy"), Kind="fix"), "2026-10-31T12:00:00Z", "madswan-planner")).lines()) + "\n"
        ops(w, 'bolt drop x "Not needed."')
        assert [(r["Act"], r["Work"], r.get("Of")) for r in requests(w)[3:]] == [
            ("drop", "unit/a", "1"), ("drop", "chore/c", "2"), ("drop", "fix/x/tidy", "3")]
        w = launched("x", work=[unit("a")])
        ops(w, 'bolt drop x "Later." --requeue')
        assert [(r["Act"], r.get("Of")) for r in requests(w)[1:]] == [("drop", "1")]

    def test_a_bolt_not_started_is_refused(self):
        w = given(("x", None, None), work=[unit("a")])
        with pytest.raises(plan.Refusal, match="^bolt x is not started, so nothing of its work is launched$"):
            plan.reach_places(FLEET, w, "x")


def path_at(name):
    """The place a flume 0.3.6 status fixture stands at (facts.ran), without a tidied place's @<when>."""
    import json
    from facts import FLUME
    return json.loads((FLUME / f"{name}.json").read_text())["status"]["places"][0]["place"].split("@")[0]


class TestAnswer:
    """crew answer <work> "<words>" is the retry that answers a place that stopped short or waits on its caller
    (Decision 9), refused naming the place's stage otherwise."""

    def answered(self, at, work=(unit("a"),), named="a", words="madswan's"):
        """crw-4's x launched with its work, request 1's place standing at the status fixture named, answered."""
        from facts import ran
        w = launched("x", work=list(work), runners=ran({1: at}))
        return w, plan.answer_place(w, named, words)

    def test_a_stage_that_stopped_short_asking_is_retried_with_the_answer(self):
        """The runner's record shows a's code stopped short asking, and the planner runs crew answer a "madswan's"."""
        w, got = self.answered("stopped-short")
        assert requests(w)[1] == {"Request": "2", "Act": "retry", "Work": "unit/a", "Of": "1", "Stage": "code", "Words": "madswan's"}
        assert got == dict(n=2, work="unit/a", host="deneb", place=path_at("stopped-short"), what="code")
        assert (w.subject, w.on) == ("plan(x): answer unit/a's code", ["unit/a", "bolt/x"])

    @pytest.mark.parametrize("at", ["on-hold", "stalled"])
    def test_a_place_waiting_on_its_caller_to_retry_a_stage_is_retried_at_that_stage(self, at):
        """on-hold's code waits on its caller while construct is current; stalled's code was lost past Flume's bound."""
        w, _ = self.answered(at)
        assert (requests(w)[1]["Stage"], requests(w)[1]["Words"]) == ("code", "madswan's")

    def test_nothing_to_answer_is_refused_naming_its_stage(self):
        """a's place is in code with no question, and crew answer a "yes" runs."""
        with pytest.raises(plan.Refusal, match=rf"^unit/a's place {path_at('code')} is at code, with no question and nothing it "
                                               r"waits on its caller for, so there is nothing to answer: crew bolts shows its stage$"):
            self.answered("code", words="yes")

    @pytest.mark.parametrize("at, said", [("submitted", "submitted to sluice (413)"), ("landed", "merged"), ("queued", "queued for room at construct")])
    def test_a_place_further_on_is_refused_naming_where_it_is(self, at, said):
        with pytest.raises(plan.Refusal, match=rf"^unit/a's place .* is {re.escape(said)}, with no question"):
            self.answered(at)

    def test_a_fix_is_answered_by_its_places_name(self):
        from facts import ran
        w = launched("x", work=[unit("a")], runners=ran({2: "stopped-short"}))
        fields = {k: v for k, v in launch(2, "fix/x/rail-word", "x--rail-word").items() if k not in ("Request", "Act", "Work")}
        plan.request(w, "launch", "fix/x/rail-word", **dict(fields, Kind="fix"))
        plan.answer_place(w, "x--rail-word", "Say land.")
        assert (requests(w)[2]["Work"], requests(w)[2]["Of"], requests(w)[2]["Stage"]) == ("fix/x/rail-word", "2", "code")

    def test_work_with_no_launch_standing_is_refused(self):
        """b is planned on crw-5's bolt, on today's path."""
        w = given(("t", "crw-5", None), work=[unit("b", bolt="t")])
        with pytest.raises(plan.Refusal, match=r"^no launch of b stands in requests.rec, so no Flume place of it waits on an answer"):
            plan.answer_place(w, "b", "yes")

    def test_a_partition_no_runner_answers_for_refuses_naming_why(self):
        w = launched("x", work=[unit("a")])
        with pytest.raises(plan.Refusal, match=r"^can't tell whether unit/a's place waits on an answer: no runner answers for the "
                                               r"partition: no <label>/runner/<host> branch exists, so nothing takes request 1$"):
            plan.answer_place(w, "a", "yes")

    def test_a_place_held_for_its_after_work_has_nothing_to_answer(self):
        from facts import ran
        w = launched("x", work=[unit("a"), unit("b", after=["a"])], runners=ran({1: "code"}, held=[2]))
        with pytest.raises(plan.Refusal, match=r"^unit/b's place is held for its After work, with no question"):
            plan.answer_place(w, "b", "yes")

    def test_a_submission_waiting_on_its_caller_is_sent_again_and_one_held_is_the_users_send(self):
        assert runner.answer_retry("fix/x/rail-word", {"stage": "waits", "of": None, "held": False, "place": "/p"}) == ("submission", None)
        assert runner.answer_retry("fix/main/crew/red", {"stage": "waits", "of": None, "held": True, "place": "/crew/places/fix--main--red"}) == (
            None, "fix/main/crew/red's place /crew/places/fix--main--red has delivered, and its submission waits held for the user's "
                  "send, which no answer gives: crew main fix crew red --send, on the user's word")

    def test_two_works_answering_to_one_name_are_both_named(self):
        requests_ = [plan.Rec("Request", runner.request_fields(1, "launch", "unit/x--n", dict(launch(1, "unit/x--n", "x--n")), "2026-10-31T12:00:00Z", "u")),
                     plan.Rec("Request", runner.request_fields(2, "launch", "fix/x/n", dict(launch(2, "fix/x/n", "x--n"), Kind="fix"), "2026-10-31T12:00:00Z", "u"))]
        assert runner.named_launch(requests_, "x--n") == (None, "x--n names fix/x/n and unit/x--n: name the one meant as requests.rec does")

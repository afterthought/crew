"""A unit's stage, read from its place and its Amended mark (plan.6, state.2): plan.place_stage; a drop refused for work
whose stage crew cannot tell (read.1); and a started bolt's work, its stage read from the runner's records: plan.Stages."""
import pytest

from facts import FactsWrite, apply, crew_read, known, madswan_fleet, plan_text

import plan
import runner


def place(done=0, total=0, planning=False, head=None):
    return {"tasks": (done, total) if total else None, "planning": planning, "head": head}


@pytest.mark.parametrize("pl, stage", [
    (place(), "construct"),
    (place(planning=True), "planned"),
    (place(0, 5, planning=True), "planned"),
    (place(2, 5, planning=True), "code"),
    (place(5, 5, planning=True), "verify"),
], ids=["nothing written", "planning, no tasks", "tasks, none done", "some done", "all done"])
def test_an_unmarked_unit_reads_its_stage_from_its_tasks(pl, stage):
    assert plan.place_stage(pl) == stage


@pytest.mark.parametrize("mark", ["intent", "proposal/124"])
def test_an_amended_unit_reads_amended_until_construct_runs_again(mark):
    assert plan.place_stage(place(5, 5, planning=True), mark) == "amended"
    assert plan.place_stage(None, mark) == "amended"


def test_a_unit_whose_construct_started_again_is_in_construct_until_it_commits():
    assert plan.place_stage(place(5, 5, planning=True, head="abc123"), "abc123") == "construct"
    assert plan.place_stage(None, "abc123") == "construct"


def test_once_construct_has_committed_again_the_mark_stops_counting():
    assert plan.place_stage(place(1, 6, planning=True, head="def456"), "abc123") == "code"


def fresh():
    return FactsWrite(plan_text(bolts=[("tenant-environments", "switchboard-kit", "swb-1"), ("console-pages", "switchboard-kit", "swb-2")],
                                units=[("bump", "switchboard-kit", "tenant-environments", [], "chore"), ("b", "switchboard-kit", "tenant-environments", [])]))


def test_work_whose_stage_crew_cannot_tell_is_not_dropped():
    """bump's stage unknown, its host silent: the drop is refused naming why (read.1)."""
    w = fresh()
    ctx = known(w)
    ctx.of = lambda name: {"stage": "unknown", "worktree": None, "open": [], "head": None, "why": "its host did not answer"}
    with pytest.raises(plan.Refusal, match="cannot tell chore bump's stage: its host did not answer"):
        apply(w, 'chore drop bump "Not now."', ctx=ctx)


# ------------------------------------------------------------------------- a crossed team's work, from the runner's records

class TestCrossed:
    """bolt-plan "A started bolt's work reads its stage from the runner's records" and "A started place's stage is where
    Flume's status has it" (Decision 8 of teams-cross-to-flume-as-their-bolts-land): plan.Stages answers runner.stage_of
    for each unit and chore of a bolt marked Path: flume, from the runner that took its launch, never reading a place in
    the kit, and reads the kit where that runner reported it (the user's ruling of 2026-11-01)."""
    FLEET = madswan_fleet()

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")

    def stages(self, runners, main=(), chores=(), runs=None):
        """Stages of x, started, holding a, b after a, and chore c, launched as requests 1 to 3, with the partition's runners
        as given (facts.ran, deneb's), and crew's kit as read on deneb holding main's changes and chores."""
        from facts import launched
        p, requests = launched(["x"], work=[("a", "x", [], "unit", []), ("b", "x", ["a"], "unit", []), ("c", "x", [], "chore", [])],
                               fleet=self.FLEET)
        return plan.Stages(self.FLEET, p, crew_read(main, chores, {"x": {}}), runs={"madswan": runs if runs is not None else (requests, runners)},
                           label="madswan")

    def test_a_dependent_waits_on_the_work_it_comes_after(self):
        """bolt-plan "A dependent waits": b's launch answered held, a's place not yet landed."""
        from facts import ran
        s = self.stages(ran({1: "code"}, held=[2])).of("b")
        assert (s["stage"], s["flume"]["after"], s["worktree"]) == ("waiting", ["unit/a"], None)

    def test_the_runners_host_silent_reads_every_crossed_piece_unknown(self):
        """bolt-plan "The runner's host is silent": deneb's runner branch can't be read, so crew can't tell which runner
        took each launch; with no runner answering for the partition at all, nothing takes them (read.1)."""
        silent = {"deneb": runner.host_read("madswan", "deneb", "5e1f0c2a" + "0" * 32, {}, {"runner.rec": "recfix refused it"})}
        st = self.stages(silent)
        why = "deneb's runner can't be read: madswan/runner/deneb at 5e1f0c2: recfix refused it"
        assert [(st.of(n)["stage"], st.of(n)["why"]) for n in "abc"] == [
            ("unknown", f"no runner crew read has taken request {n}, and {why}") for n in (1, 2, 3)]
        assert st.unread(st.plan.bolt("x")) == ("deneb's runner", why)
        none = self.stages({})
        assert none.of("a")["why"] == "no runner answers for the partition: no <label>/runner/<host> branch exists, so nothing takes request 1"

    def test_requests_crew_cant_read_read_every_crossed_piece_unknown(self):
        st = self.stages(None, runs="could not fetch madswan/main of afterthought/crew-state over https: no network")
        assert st.of("a")["stage"] == "unknown"
        assert st.of("a")["why"] == ("crew can't read madswan's requests or runners: could not fetch madswan/main of "
                                     "afterthought/crew-state over https: no network")

    def test_a_unit_in_code_reads_its_tasks(self):
        """bolt-plan "A unit in code"."""
        from facts import ran
        s = self.stages(ran({1: "code"})).of("a")
        assert (s["stage"], s["tasks"]) == ("code", (6, 26))
        assert runner.piece_said(s["flume"]) == ("code 6/26", "")

    def test_a_construct_that_asked_needs_an_answer_with_its_question(self):
        """bolt-plan "A construct that asked"."""
        from facts import ran
        s = self.stages(ran({1: "stopped-short"})).of("a")
        assert s["stage"] == "needs"
        assert runner.piece_said(s["flume"])[1].startswith("asks at code: Head 118ec46 is ready for your flume:live run (6.1).")

    def test_a_place_sent_back_by_sluice_reads_its_stage_with_sluices_words(self):
        """bolt-plan "Sent back by sluice"."""
        from facts import ran
        s = self.stages(ran({2: "sent-back"})).of("b")
        assert (s["stage"], s["flume"]["sent_back"]) == ("code", 1)
        assert runner.piece_said(s["flume"]) == ("code 26/26", "sent back by sluice: check-full failed on "
                                                 "bolt/crew-runs-its-work-through-flume with change/teams-cross-to-flume-as-"
                                                 "their-bolts-land merged: tests:logic (1 failed: tests/py/test_runner.py::"
                                                 "TestStageOf::test_a_crossed_piece_reads_its_stage)")

    def test_a_place_landed_on_its_bolt_reads_merged_and_landed_once_main_holds_it(self):
        """bolt-plan "Landed on the bolt": merged while x has not landed; landed once crew's main holds a's change, or c's
        trailer, as today's do."""
        from facts import ran
        runners = ran({1: "landed", 3: "landed"})
        assert [self.stages(runners).of(n)["stage"] for n in "ac"] == ["merged", "merged"]
        assert [self.stages(runners, main=["a"], chores=["c"]).of(n)["stage"] for n in "ac"] == ["landed", "landed"]

    def test_a_launch_the_runner_has_not_answered_is_launching_and_no_launch_is_unknown(self):
        from facts import ran
        assert self.stages(ran()).of("a")["stage"] == "launching"
        st = self.stages(None, runs=([], ran()))
        assert (st.of("a")["stage"], st.of("a")["why"]) == ("unknown", "unit/a has no launch in requests.rec")

    def test_a_crossed_bolts_fixes_read_their_stages_from_the_runner(self):
        """bolt-plan's requirement holds for a fix: fix/x/tidy, launched as request 4, read at code."""
        from facts import ran
        st = self.stages(ran({4: "code"}))
        requests, _ = st.runs["madswan"]
        fix = plan.Rec("Request", [("Request", "4"), ("Act", "launch"), ("Work", "fix/x/tidy"), ("Name", "x--tidy"),
                                   ("Base", "bolt/x"), ("Kind", "fix")])
        st.runs["madswan"] = (requests + [fix], st.runs["madswan"][1])
        assert [(w, s["stage"]) for w, _, s in st.fixes(st.plan.bolt("x"))] == [("fix/x/tidy", "code")]

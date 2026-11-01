"""A unit's stage, read from its place and its Amended mark (plan.6, state.2): plan.place_stage; a unit's or chore's
place of a bolt it has left, which is not its place (teams.1): plan.Stages, plan.left_refusal, plan.left_over, and the
unit and chore drop and move, which a place crew cannot read does not refuse (read.1); and the bolt its merge is looked
for in, the one the plan places it in now: plan.merge_bolt."""
import pytest

from facts import FactsWrite, apply, crew_read, crossed_fleet_read, known, plan_text

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


# A unit or chore added again under a name it had in another bolt, its place kept from the drop at its path and
# tracking the old bolt (breadboard-kit on chuck-herdr-alpha, 2026-10-23: chore
# breadboards-console-declares-its-endpoint-through-the-fragment, re-added to bolt
# breadboards-console-is-found-as-the-fragment-declares-it, its clean place still tracking the landed and gone bolt
# breadboard-carries-nothing-the-design-retired, and its code refused, "tracks no bolt crew can read"; signal
# 2026-10-23-brd-2-conductor-d2ed533c/01 on wldn/main).
KIT, OLD, NEW = "breadboard-kit", "breadboard-carries-nothing-the-design-retired", "breadboards-console-is-found-as-the-fragment-declares-it"
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "box", "teams": ["brd-2"]}},
         "teams": {"brd-2": {"name": "brd-2", "label": "wldn", "machine": "box", "kit": {"main": "/kit/main", "dir": "/kit", "name": KIT}}}}


def again(*work):
    """A plan whose bolt NEW holds work, each (name, kind) with kind "chore" or "unit", as added again after OLD landed."""
    return plan_text(bolts=[(NEW, KIT, "brd-2")], units=[(n, KIT, NEW, [], *(("chore",) if k == "chore" else ())) for n, k in work])


def kit(chore_places=None, places=None):
    """breadboard-kit as gathered, holding NEW's branch and not OLD's, which landed and is gone."""
    return {"ok": True, "main": [], "chores": [], "places": places or {}, "chore_places": chore_places or {}, "fixes": [],
            "bolts": {NEW: {"exists": True, "changes": [], "archived": [], "open": {}, "chores": [], "head": "d" * 40}}}


def stages(k, text):
    return plan.Stages(FLEET, plan.Plan(text), {"box": {"ok": True, "kits": {"/kit/main": k}}})


def chore_place(bolt, ahead):
    return {"path": "/kit/places/chore-bump", "head": "e" * 40, "head_at": "2026-10-23T16:00:00Z", "ahead": ahead, "bolt": bolt,
            "branch": "chore/bump"}


def unit_place(bolt):
    return {"path": "/kit/places/a", "head": "a" * 40, "head_at": "2026-10-23T16:00:00Z", "tasks": (2, 2), "planning": True,
            "open": [], "bolt": bolt, "branch": "unit/a"}


class TestAPlaceOfABoltItHasLeft:
    def test_a_chore_added_again_reads_as_having_no_place_and_its_old_place_is_marked_left(self):
        s = stages(kit({"bump": chore_place(OLD, None)}), again(("bump", "chore"))).of("bump")
        assert (s["stage"], s["worktree"], s["left"]["path"]) == ("ready", None, "/kit/places/chore-bump")

    def test_a_unit_added_again_reads_as_having_no_place_not_at_the_stage_its_old_place_holds(self):
        s = stages(kit(places={"a": unit_place(OLD)}), again(("a", "unit"))).of("a")
        assert (s["stage"], s["worktree"], s["left"]["bolt"]) == ("ready", None, OLD)

    def test_a_place_of_its_own_bolt_is_its_place(self):
        assert stages(kit({"bump": chore_place(NEW, 1)}), again(("bump", "chore"))).of("bump")["stage"] == "verify"
        s = stages(kit(places={"a": unit_place(NEW)}), again(("a", "unit"))).of("a")
        assert (s["stage"], s["worktree"], s.get("left")) == ("verify", "/kit/places/a", None)

    def test_a_place_of_its_own_bolt_crew_cannot_read_is_unknown_for_its_place_alone(self):
        s = stages(kit({"bump": chore_place(NEW, None)}), again(("bump", "chore"))).of("bump")
        assert (s["stage"], s.get("place_unread"), s.get("left")) == ("unknown", True, None)
        s = stages(kit({"bump": chore_place(None, None)}), again(("bump", "chore"))).of("bump")
        assert (s["stage"], s.get("place_unread")) == ("unknown", True)


def unread(name):
    """A stage unknown for its place alone: the place tracks a bolt crew cannot read."""
    return {"stage": "unknown", "worktree": f"/kit/places/chore-{name}", "open": [], "head": None,
            "why": f"chore {name}'s place /kit/places/chore-{name} tracks no bolt crew can read", "place_unread": True}


def fresh():
    return FactsWrite(plan_text(bolts=[("tenant-environments", "switchboard-kit", "swb-1"), ("console-pages", "switchboard-kit", "swb-2")],
                                units=[("bump", "switchboard-kit", "tenant-environments", [], "chore"), ("b", "switchboard-kit", "tenant-environments", [])]))


class TestAPlaceCrewCannotRead:
    def ctx(self, w, s):
        ctx = known(w)
        ctx.of = lambda name: s
        return ctx

    def test_its_work_is_dropped_all_the_same(self):
        w = fresh()
        apply(w, 'chore drop bump "Not now."', ctx=self.ctx(w, unread("bump")))
        assert w.plan.item("bump") is None

    def test_its_work_is_moved_all_the_same_its_place_not_rebased(self):
        w = fresh()
        op = plan.OPS[("chore", "move")](self.ctx(w, unread("bump")), plan.do_args("wldn", "chore move bump console-pages"))
        op.change(w)
        assert op.prepare is None and w.plan.item("bump").get("Bolt") == "console-pages"

    def test_work_whose_host_does_not_answer_is_still_refused(self):
        w = fresh()
        s = dict(unread("bump"), why="its host did not answer", place_unread=None)
        with pytest.raises(plan.Refusal, match="cannot tell chore bump's stage: its host did not answer"):
            apply(w, 'chore drop bump "Not now."', ctx=self.ctx(w, s))


# ------------------------------------------------------------------------- a crossed team's work, from the runner's records

class TestCrossed:
    """bolt-plan "A crossed team's work reads its stage from the runner's records" and "A crossed place's stage is where
    Flume's status has it" (Decision 8 of teams-cross-to-flume-as-their-bolts-land): plan.Stages answers runner.stage_of
    for each unit and chore of a bolt marked Path: flume, never reading a place in the kit."""
    FLEET = crossed_fleet_read()

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")

    def stages(self, runners, main=(), chores=(), runs=None):
        """Stages of x given to crossed crw-4 holding a, b after a, and chore c, launched as requests 1 to 3, with deneb's
        runner as given (facts.ran), and crew's kit as read on deneb holding main's changes and chores."""
        from facts import launched
        p, requests = launched(["x"], work=[("a", "x", [], "unit", []), ("b", "x", ["a"], "unit", []), ("c", "x", [], "chore", [])],
                               fleet=self.FLEET)
        return plan.Stages(self.FLEET, p, crew_read(main, chores, {"x": {}}), runs={"madswan": runs if runs is not None else (requests, runners)})

    def test_a_dependent_waits_on_the_work_it_comes_after(self):
        """bolt-plan "A dependent waits": b's launch answered held, a's place not yet landed."""
        from facts import ran
        s = self.stages(ran({1: "code"}, held=[2])).of("b")
        assert (s["stage"], s["flume"]["after"], s["worktree"]) == ("waiting", ["unit/a"], None)

    def test_the_runners_host_silent_reads_every_crossed_piece_unknown(self):
        """bolt-plan "The runner's host is silent": deneb's runner branch can't be read."""
        st = self.stages({})
        why = "no runner answers on deneb: madswan/runner/deneb does not exist"
        assert [(st.of(n)["stage"], st.of(n)["why"]) for n in "abc"] == [("unknown", why)] * 3
        assert st.unread(st.plan.bolt("x")) == ("deneb's runner", why)

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
        fix = plan.Rec("Request", [("Request", "4"), ("Act", "launch"), ("Host", "deneb"), ("Work", "fix/x/tidy"), ("Name", "x--tidy"),
                                   ("Base", "bolt/x"), ("Kind", "fix")])
        st.runs["madswan"] = (requests + [fix], st.runs["madswan"][1])
        assert [(w, s["stage"]) for w, _, s in st.fixes(st.plan.bolt("x"))] == [("fix/x/tidy", "code")]

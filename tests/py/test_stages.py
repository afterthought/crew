"""A unit's stage, read from its place and its Amended mark (plan.6, state.2): plan.place_stage; and a unit's or
chore's place of a bolt it has left, which is not its place (teams.1): plan.Stages, plan.left_refusal, plan.left_over,
and the unit and chore drop and move, which a place crew cannot read does not refuse (read.1)."""
import pytest

from facts import FactsWrite, apply, known, plan_text

import plan


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

    def test_no_stage_starts_while_a_place_it_has_left_stands_and_one_cuts_its_place_from_its_bolt_once_it_is_gone(self):
        assert plan.left_refusal("chore", "bump", NEW, None) is None
        assert plan.left_refusal("chore", "bump", NEW, chore_place(OLD, None)) == (
            f"chore bump's place /kit/places/chore-bump tracks bolt/{OLD}, which it has left for bolt/{NEW}, and still stands: "
            "crew's tidy removes it only when it is clean, unlocked and no slot or run holds it, and once it is gone bump's stage "
            f"cuts its place from bolt/{NEW}")

    @pytest.mark.parametrize("bolt, now, over", [
        (OLD, NEW, f"chore bump has left bolt/{OLD} for bolt/{NEW}"), (OLD, None, f"chore bump has left bolt/{OLD} for the queue"),
        (NEW, NEW, None), (None, NEW, None)], ids=["another bolt", "the queue", "its bolt", "no bolt crew can name"])
    def test_the_tidy_takes_a_place_of_a_bolt_its_work_has_left_as_over(self, bolt, now, over):
        assert plan.left_over("chore", "bump", bolt, now) == over


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

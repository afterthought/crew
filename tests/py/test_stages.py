"""A unit's stage, read from its place and its Amended mark (plan.6, state.2): plan.place_stage; a unit's or chore's
place of a bolt it has left, which is not its place (teams.1): plan.Stages, plan.left_refusal, plan.left_over, and the
unit and chore drop and move, which a place crew cannot read does not refuse (read.1); and the bolt its merge is looked
for in, the one the plan places it in now: plan.merge_bolt."""
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


class TestMergeLookReadsTheUnitsOwnBolt:
    """crew unit wait's merge look reads the bolt the plan places the unit in now (plan.merge_bolt), never another
    team's bolt or one the unit was in before, so a merge its bolt holds is seen. On 2026-10-23 crw-5's wait on the merge
    of a-bolt-on-github-is-read-where-it-lives read crw-4's bolt a-landing-writes-no-bolt-ref, its branch's upstream,
    and said stuck while bolt/crew-reads-a-github-bolt-from-github held it (signal
    2026-10-23-crw-5-conductor-63fbcc2d/01)."""
    UNIT, OURS, THEIRS = "a-bolt-on-github-is-read-where-it-lives", "crew-reads-a-github-bolt-from-github", "a-landing-writes-no-bolt-ref"

    def plan(self, bolt=OURS, repo=None):
        text = (f"%rec: Bolt\n\nBolt: {self.OURS}\nTeam: crw-5\n" + (f"Repo: {repo}\n" if repo else "")
                + f"\nBolt: {self.THEIRS}\nTeam: crw-4\n\n%rec: Unit\n\nUnit: {self.UNIT}\n" + (f"Bolt: {bolt}\n" if bolt else ""))
        return plan.Plan(text)

    def test_the_bolt_the_plan_places_it_in_now(self):
        assert plan.merge_bolt(self.plan(), "crw-5", self.UNIT) == (self.OURS, None, None)

    def test_with_that_bolts_kit(self):
        assert plan.merge_bolt(self.plan(repo="crew"), "crw-5", self.UNIT) == (self.OURS, "crew", None)

    def test_never_another_teams_bolt(self):
        assert plan.merge_bolt(self.plan(self.THEIRS), "crw-5", self.UNIT) == (
            None, None, f"the plan places {self.UNIT} in bolt {self.THEIRS}, which crw-5 does not hold")

    def test_a_unit_queued_again_has_no_bolt_to_read(self):
        assert plan.merge_bolt(self.plan(None), "crw-5", self.UNIT) == (None, None, f"the plan places {self.UNIT} in no bolt")

    def test_a_unit_the_plan_no_longer_holds(self):
        assert plan.merge_bolt(self.plan(), "crw-5", "gone") == (None, None, "the plan holds no gone")

    def test_a_merge_look_reads_the_plans_bolt_and_never_the_branchs_upstream(self, monkeypatch):
        from facts import owed
        t = {"name": "crw-5", "label": "swancloud", "kit": {"main": "/kit/main", "dir": "/kit"}}
        ours = f"refs/remotes/origin/bolt/{self.OURS}"
        calls = []

        def run(argv, cwd):
            calls.append(argv)
            assert self.THEIRS not in " ".join(argv) and argv[:2] != ["git", "for-each-ref"], f"an unexpected read: {argv}"
            if argv[:3] == ["git", "remote", "get-url"]:
                return "https://github.com/o/crew.git\n"
            if argv[:2] == ["git", "rev-parse"] and argv[-1] == f"{ours}^{{commit}}":
                return "1" * 40 + "\n"
            if argv[:2] == ["git", "rev-parse"] and argv[-1].endswith("^{commit}"):
                return None
            if argv[:2] == ["git", "show"] and argv[-1] == f"{ours}:.config/sluice.toml":
                return '[branches."bolt/*"]\nremote = "origin"\n'
            if argv[:2] == ["git", "ls-tree"] and argv[4] == ours:
                return f"openspec/changes/archive/2026-10-23-{self.UNIT}\n"
            if argv[:3] == ["git", "rev-parse", "--short"] and argv[-1] == ours:
                return "12bab11\n"
            raise AssertionError(f"an unexpected read: {argv}")
        monkeypatch.setattr(plan.gather, "run", run)
        monkeypatch.setattr(plan.gather, "ran", lambda argv, cwd: (0, "", ""))
        monkeypatch.setattr(plan, "plans", lambda fleet, labels, errors=None: [("swancloud", "o/state", "tip", self.plan())])
        o = owed("merge", name=self.UNIT, slot="unit-1", team="crw-5")
        assert plan.delivered(o, plan.deliverable_facts({}, t, o)) == (f"bolt/{self.OURS}@12bab11", f"bolt/{self.OURS} holds it at 12bab11")

    def test_a_plan_crew_cant_read_delivers_nothing_and_says_why(self, monkeypatch):
        from facts import owed
        t = {"name": "crw-5", "label": "swancloud", "kit": {"main": "/kit/main", "dir": "/kit"}}

        def unread(fleet, labels, errors=None):
            errors["swancloud/main of o/state"] = "could not fetch swancloud/main of o/state over https: no network"
            return []
        monkeypatch.setattr(plan, "plans", unread)
        o = owed("merge", name=self.UNIT, team="crw-5")
        assert plan.delivered(o, plan.deliverable_facts({}, t, o)) == (
            None, "no bolt crew can read for it: swancloud/main of o/state could not be read: "
                  "could not fetch swancloud/main of o/state over https: no network")

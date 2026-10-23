"""A unit's stage, read from its place and its Amended mark (plan.6, state.2): plan.place_stage; and the bolt its merge is
looked for in, the one the plan places it in now: plan.merge_bolt."""
import pytest

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

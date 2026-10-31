"""A team crossing to Flume, one team at a time (record 0050 parts 2 and 3, the change
teams-cross-to-flume-as-their-bolts-land): a team's path from its setting and the bolts it holds (runner.team_path,
runner.path_of). The commands that act on it, a give's refusal and a crossed team's end, are the cross journey's
(t-journey-cross)."""
import pytest

import plan
import runner

CREW = "crew"


def plan_with(bolts):
    """A plan whose bolts are given as (name, team or None, Path or None), in order."""
    return plan.Plan("%rec: Bolt\n%key: Bolt\n\n" + "".join(
        f"Bolt: {b}\nRepo: {CREW}\nGoal: Goal of {b}.\n" + (f"Team: {t}\n" if t else "") + (f"Path: {p}\n" if p else "") + "\n"
        for b, t, p in bolts) + "%rec: Unit\n%key: Unit\n")


def team(flume, name="crw-4"):
    return {"name": name, "flume": flume, "label": "madswan", "machine": "deneb"}


class TestPath:
    """A team's path is today's, due or crossed, from its setting and the Path of each bolt it holds (Decision 2)."""

    @pytest.mark.parametrize("setting, held, path", [
        (False, [], ("today", None)),
        (False, [None], ("today", None)),
        (False, [None, None], ("today", None)),
        ("madswan", [], ("crossed", None)),
        ("madswan", ["flume"], ("crossed", None)),
        ("madswan", ["flume", "flume"], ("crossed", None)),
        ("madswan", [None], ("due", "cross")),
        ("madswan", ["flume", None], ("due", "cross")),
        (False, ["flume"], ("due", "back")),
        (False, [None, "flume"], ("due", "back"))])
    def test_the_setting_and_each_bolt_held_give_the_path(self, setting, held, path):
        assert runner.team_path(setting, held) == path

    def test_the_setting_turned_on_while_the_team_builds_a_bolt_of_todays_path_makes_it_due_to_cross(self):
        p = plan_with([("x", "crw-4", None), ("y", None, None)])
        assert runner.path_of(p, team("madswan")) == ("due", "cross")

    def test_a_team_holding_nothing_when_its_setting_turns_on_is_crossed(self):
        assert runner.path_of(plan_with([("x", "crw-5", None)]), team("madswan")) == ("crossed", None)

    def test_turned_back_while_it_holds_a_bolt_given_through_flume_it_is_due_back(self):
        assert runner.path_of(plan_with([("y", "crw-4", "flume")]), team(False)) == ("due", "back")

    def test_only_the_teams_own_bolts_count(self):
        p = plan_with([("x", "crw-5", None), ("y", "crw-4", "flume")])
        assert runner.path_of(p, team("madswan")) == ("crossed", None)
        assert runner.path_of(p, team("madswan", "crw-5")) == ("due", "cross")


class TestDue:
    """A team due to cross is given no new bolt, and no dispatcher is told it can take one (Decision 2)."""

    def test_a_give_to_a_due_team_is_refused_naming_each_bolt_and_the_path_it_was_given_on(self):
        assert runner.due_refusal("crw-4", ("due", "cross"), [("x", None)]) == (
            "crw-4 is due to cross to Flume, so it is given no bolt now: it holds x, given on today's path, and is given its next "
            "bolt once x has landed or been dropped")

    def test_two_bolts_of_todays_path_are_both_named_and_both_finished_first(self):
        assert runner.due_refusal("crw-4", ("due", "cross"), [("x", None), ("z", None)]).endswith(
            "it holds x and z, given on today's path, and is given its next bolt once x and z have landed or been dropped")

    def test_due_back_names_the_bolts_given_through_flume_as_the_ones_it_finishes_first(self):
        assert runner.due_refusal("crw-4", ("due", "back"), [("y", "flume"), ("x", None)]) == (
            "crw-4 is due back to today's path, so it is given no bolt now: it holds y, given through Flume and x, given on "
            "today's path, and is given its next bolt once y has landed or been dropped")

    @pytest.mark.parametrize("path", [("today", None), ("crossed", None)])
    def test_a_team_that_is_not_due_is_not_refused_for_it(self, path):
        assert runner.due_refusal("crw-4", path, [("x", None)]) is None

    def test_a_proven_bolt_waiting_to_land_on_a_due_team_tells_no_dispatcher_it_is_free(self):
        p = plan_with([("x", "crw-4", None), ("next", None, None)])
        assert not plan.free_now(plan.give_due(p, team("madswan")) or plan.give_refusal("crw-4", []), "next")
        assert plan.free_now(plan.give_due(p, team(False)) or plan.give_refusal("crw-4", []), "next")

    def test_a_bolt_landed_by_a_team_the_write_leaves_due_tells_no_dispatcher(self):
        teams = {"crw-4": team("madswan"), "crw-5": team(False, "crw-5")}
        after = plan_with([("z", "crw-4", None), ("w", "crw-5", None)])
        assert plan.due_teams({"teams": teams}, after) == {"crw-4"}

        def told(freed_by):
            seen = dict(before={"x": freed_by}, after={}, touched=["x"], quiet=set(), due=plan.due_teams({"teams": teams}, after))
            return plan.notices(teams, seen, "madswan-ops", "plan(x): land the bolt (madswan-ops)")[2]
        assert not told("crw-4")
        assert told("crw-5")


class TestCrossing:
    """Once a team has crossed, its conductor and ops are due an end, and the crossing is whole once neither is up
    (Decision 3)."""

    def test_once_crossed_every_role_up_is_due_an_end_and_the_crossing_is_whole_once_none_is(self):
        assert runner.cross_due(("crossed", None), ["conductor", "ops"]) == (["conductor", "ops"], False)
        assert runner.cross_due(("crossed", None), ["ops"]) == (["ops"], False)
        assert runner.cross_due(("crossed", None), []) == ([], True)

    @pytest.mark.parametrize("path", [("today", None), ("due", "cross"), ("due", "back")])
    def test_a_team_that_has_not_crossed_owes_its_agents_nothing(self, path):
        assert runner.cross_due(path, ["conductor", "ops"]) == ([], False)
        assert runner.cross_due(path, []) == ([], False)


class TestNoStandingAgent:
    """A crossed team runs no standing agent: every standing-agent or slot command of it is refused at once, naming
    where its work runs (Decision 15)."""
    FLEET = {"teams": {}, "partitions": {"madswan": {"label": "madswan"}}}

    def test_a_crossed_teams_command_is_refused_naming_flume_its_host_its_stream_and_crew_bolts(self):
        assert runner.crossed_refusal("crw-4", ("crossed", None), "madswan", "deneb", "up crw-4") == (
            "crw-4 has crossed to Flume: its work runs in Flume places on deneb, in stream madswan, and crew bolts shows them; it "
            "runs no conductor, ops or slot, so crew up crw-4 has nothing of it to act on")

    @pytest.mark.parametrize("path", [("today", None), ("due", "cross"), ("due", "back")])
    def test_a_team_that_has_not_crossed_is_not_refused_for_it(self, path):
        assert runner.crossed_refusal("crw-4", path, "madswan", "deneb", "up crw-4") is None

    def reads(self, monkeypatch, found, errors=None):
        read = []

        def plans(fleet, labels, errs=None):
            read.append(labels)
            errs.update(errors or {})
            return [] if errors else [("madswan", "afterthought/crew-state", "a" * 40 if found else None, found)]
        monkeypatch.setattr(plan, "plans", plans)
        return read

    def test_a_team_whose_setting_is_off_is_not_refused_and_its_plan_is_not_read(self, monkeypatch):
        read = self.reads(monkeypatch, plan_with([("x", "crw-4", None)]))
        plan.not_crossed(self.FLEET, team(False), "up crw-4")
        assert read == []

    def test_a_crossed_team_is_refused_from_its_plan_and_a_due_one_is_not(self, monkeypatch):
        self.reads(monkeypatch, plan_with([("x", "crw-4", "flume")]))
        with pytest.raises(plan.Refusal, match="^crw-4 has crossed to Flume: its work runs in Flume places on deneb"):
            plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")
        self.reads(monkeypatch, plan_with([("x", "crw-4", None)]))
        plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")

    def test_a_branch_not_started_holds_no_bolt_of_the_team_so_it_has_crossed(self, monkeypatch):
        self.reads(monkeypatch, None)
        assert plan.crossing_path(self.FLEET, team("madswan")) == ("crossed", None)

    def test_a_plan_that_cannot_be_read_refuses_naming_it(self, monkeypatch):
        self.reads(monkeypatch, None, {"madswan/main of afterthought/crew-state": "timed out"})
        with pytest.raises(plan.Refusal, match="^can't tell whether crw-4 has crossed to Flume: madswan/main of "
                                               "afterthought/crew-state could not be read: timed out$"):
            plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")

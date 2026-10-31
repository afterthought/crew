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

"""A team's conductor and ops carry their bolt's branch for sluice's plugins (teams.20): which agent is told which
branch, the report herdr is given, and when a running agent's branch is stale enough to restart it. That crew-role exports it, that a start, a landing and herdr's bare resume put
it on the pane, is the teams, landing and session hook journeys' (t-journey-teams, t-journey-land, t-session-hook).
Of two bolts a team holds, the one it builds is the one given last (plan.building, teams.16)."""
import pytest

import crew
import plan


def test_a_conductor_and_ops_on_a_bolt_carry_its_branch():
    assert crew.hint_branch("conductor", "b7") == "bolt/b7"
    assert crew.hint_branch("ops", "b7") == "bolt/b7"


def test_a_team_that_holds_no_bolt_carries_none():
    assert crew.hint_branch("conductor", None) is None
    assert crew.hint_branch("ops", None) is None


def test_a_unit_carries_none_since_its_place_is_on_its_own_branch():
    assert crew.hint_branch("unit-2", "b7") is None


def test_the_branch_is_reported_from_crew_with_no_time_to_live_and_no_sequence():
    assert crew.hint_args("w4:p2", "bolt/b7") == ["pane", "report-metadata", "w4:p2", "--source", "crew", "--token", "sluice_branch=bolt/b7"]


def test_no_branch_clears_the_token():
    assert crew.hint_args("w4:p2", None) == ["pane", "report-metadata", "w4:p2", "--source", "crew", "--clear-token", "sluice_branch"]


STARTED = {"session": "sid-1", "commit": "c1", "version": "v0.14.0", "launch": "abc"}


def test_an_agent_whose_bolt_landed_under_it_is_due_a_restart():
    due, why = crew.branch_due(dict(STARTED, branch="bolt/b7"), None)
    assert due and why == "its team no longer holds bolt/b7, which sluice's board still named"


def test_an_agent_whose_team_now_holds_another_bolt_is_due_a_restart():
    due, why = crew.branch_due(dict(STARTED, branch="bolt/b7"), "bolt/b8")
    assert due and why == "its team's bolt is now bolt/b8, which sluice's board names"


def test_an_agent_on_its_teams_bolt_or_with_none_is_not_due():
    assert crew.branch_due(dict(STARTED, branch="bolt/b7"), "bolt/b7") == (False, None)
    assert crew.branch_due(dict(STARTED, branch=""), None) == (False, None)


def test_an_agent_started_before_crew_kept_its_branch_is_not_due_for_it():
    assert crew.branch_due(dict(STARTED, branch=None), "bolt/b7") == (False, None)
    assert crew.branch_due(None, "bolt/b7") == (False, None)


# A team builds one bolt and may hold one more that waits to land (teams.16): the bolt it builds, the one given last,
# is the one its conductor and ops carry (plan.building).
def give(bolt, team="swc-1", refused=None):
    e = {"Act": "bolt.give", "On": [f"bolt/{bolt}", f"team/{team}"]}
    return dict(e, Refused=refused) if refused else e


def test_a_team_holding_one_bolt_builds_it_and_one_holding_none_builds_none():
    assert plan.building("swc-1", ["doctor-rows"], []) == "doctor-rows"
    assert plan.building("swc-1", [], []) is None


@pytest.mark.parametrize("gives, built", [(["doctor-rows", "ssh-fix"], "ssh-fix"), (["ssh-fix", "doctor-rows"], "doctor-rows"),
                                          (["ssh-fix"], "ssh-fix"), (["doctor-rows", "ssh-fix", "doctor-rows"], "doctor-rows")])
def test_of_two_bolts_a_team_builds_the_one_given_last(gives, built):
    assert plan.building("swc-1", ["doctor-rows", "ssh-fix"], gives) == built


def test_two_bolts_neither_of_which_the_record_gives_are_refused():
    with pytest.raises(plan.Refusal, match="can't tell which bolt swc-1 builds: the run record holds no give of doctor-rows or ssh-fix"):
        plan.building("swc-1", ["doctor-rows", "ssh-fix"], ["older"])


def test_the_gives_are_the_records_unrefused_gives_to_the_team_oldest_first():
    entries = [give("doctor-rows"), give("other", team="swb-1"), give("ssh-fix", refused="swc-1 holds two"), give("ssh-fix"),
               {"Act": "bolt.land", "On": ["bolt/doctor-rows"]}]
    assert plan.given_to(entries, "swc-1") == ["doctor-rows", "ssh-fix"]


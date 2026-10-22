"""A team's conductor and ops carry their bolt's branch for sluice's plugins (teams.20): which agent is told which
branch, the report herdr is given, and when a running agent's branch is stale enough to restart it. That crew-role exports it, that a start, a landing and herdr's bare resume put
it on the pane, is the teams, landing and session hook journeys' (t-journey-teams, t-journey-land, t-session-hook)."""
import crew


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

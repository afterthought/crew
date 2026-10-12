"""A team's slots, panes and status on its host (teams.1, teams.2, teams.9, read.1, read.2), as crew status reads them in
one process: crew.reaped for what a team's read does with a slot, crew.held_object for how the run record names what
a slot holds, crew.listed for reading herdr's listings, crew.context_of and crew.holds_said for what status shows, and
what crew says of a working agent it will not end. Reading and freeing slots through the command are the units
journey's (t-journey-units, t-journey-fix, t-journey-merge)."""
import json

import pytest

import crew

class TestReaped:
    @pytest.mark.parametrize("stage, said", [
        ("merged", "swb-1-unit-1 is free: a has merged into its bolt"),
        ("landed", "swb-1-unit-1 is free: a has merged into its bolt"),
        ("dropped", "swb-1-unit-1 is free: a was dropped from the plan"),
        ("left", "swb-1-unit-1 is free: a has left swb-1's bolt"),
    ])
    def test_a_slot_whose_work_is_over_is_freed_once_its_agent_is_not_working(self, stage, said):
        assert crew.reaped("swb-1-unit-1", "swb-1", "a", stage, "idle") == ("free", said)

    @pytest.mark.parametrize("stage, said", [
        ("merged", None),
        ("dropped", "swb-1-unit-1 still holds a, dropped from the plan: its agent is working; it is freed once that settles"),
        ("left", "swb-1-unit-1 still holds a, which has left swb-1's bolt: its agent is working; it is freed once that settles"),
    ])
    def test_while_its_agent_works_it_is_kept(self, stage, said):
        assert crew.reaped("swb-1-unit-1", "swb-1", "a", stage, "working") == ("keep", said)

    @pytest.mark.parametrize("stage", ["construct", "code", "verify", "fix", "unknown", "none"])
    def test_work_that_goes_on_keeps_its_slot_and_says_nothing(self, stage):
        assert crew.reaped("swb-1-unit-1", "swb-1", "a", stage, None) == (None, None)


class TestHeldObject:
    def test_a_unit_is_named_as_a_unit(self):
        assert crew.held_object("unit", "a") == "unit/a"

    def test_a_fix_named_with_its_bolt_is_named_as_it_is(self):
        assert crew.held_object("fix", "fix/tenant-environments/tidy") == "fix/tenant-environments/tidy"

    def test_a_fix_given_before_its_name_held_its_bolt_takes_the_bolt_its_branch_tracks(self):
        assert crew.held_object("fix", "fix/tidy", "bolt/tenant-environments") == "fix/tenant-environments/tidy"


# herdr 0.9.3's answers on mac-studio, 2026-10-12: `agent list` of a session, and of one whose server is not running.
LISTED = {"id": "cli:agent:list", "result": {"type": "agent_list", "agents": [
    {"agent": "claude", "agent_session": {"agent": "claude", "kind": "id", "source": "herdr:claude", "value": "f67c15ab-693f"},
     "agent_status": "working", "cwd": "/w", "pane_id": "w1:p2", "tab_id": "w1:t2", "workspace_id": "w1"},
    {"agent": "claude", "agent_session": {"agent": "claude", "kind": "id", "source": "herdr:claude", "value": "a16aaf5f-943b"},
     "agent_status": "idle", "cwd": "/w", "name": "swancloud-operator-mac-studio", "pane_id": "w2:p1", "tab_id": "w2:t1",
     "workspace_id": "w2"}]}}
NOT_RUNNING = ('{"id":"cli:agent:list","error":{"code":"server_not_running","message":"no herdr server is running at '
               '/Users/chuck/.config/herdr/sessions/nosuch/herdr.sock; run `herdr session attach nosuch` to start or attach it"}}')


class TestListed:
    def test_every_agent_is_read_from_one_listing_an_unnamed_one_with_no_name(self):
        agents = crew.listed("agent", 0, json.dumps(LISTED), "", "in session swancloud on mac-studio")
        assert [(a["pane_id"], a.get("name"), a["agent_status"]) for a in agents] == [
            ("w1:p2", None, "working"), ("w2:p1", "swancloud-operator-mac-studio", "idle")]

    def test_a_session_whose_server_is_not_running_has_no_agents(self):
        assert crew.listed("agent", 1, "", NOT_RUNNING, "in session nosuch on mac-studio") == []

    def test_any_other_failure_is_refused_in_herdrs_words(self):
        with pytest.raises(crew.Refusal) as e:
            crew.listed("pane", 1, "", '{"error":{"code":"internal","message":"boom"}}\n', "in session wldn-1 on mac-studio")
        assert str(e.value) == 'herdr\'s pane list in session wldn-1 on mac-studio failed: {"error":{"code":"internal","message":"boom"}}'

    def test_an_answer_crew_cannot_read_is_refused(self):
        with pytest.raises(crew.Refusal) as e:
            crew.listed("agent", 0, '{"result": {"agents": null}}', "", "in session wldn-1 on mac-studio")
        assert str(e.value) == "herdr's agent list in session wldn-1 on mac-studio can't be read"


def record(**v):
    """A transcript record as Claude Code writes it: one line of JSON with no spaces between its fields."""
    return json.dumps(v, separators=(",", ":"))


def turn(used, sidechain=False):
    return record(type="assistant", isSidechain=sidechain, timestamp="2026-10-12T09:30:00.000Z",
                  message={"usage": {"input_tokens": 10, "cache_read_input_tokens": used, "cache_creation_input_tokens": None}})


class TestStatus:
    def test_a_standing_agents_context_is_its_last_own_turns_its_compactions_counted_and_its_start_read(self):
        lines = [record(type="user", timestamp="2026-10-11T22:05:00.000Z"), turn(150000), record(type="user", isCompactSummary=True),
                 turn(250000), turn(900000, sidechain=True)]
        assert crew.context_of(lines, 1000000) == ("250k", "25%", "1", "10-11T22:05")

    def test_a_session_with_no_turn_yet_uses_nothing(self):
        assert crew.context_of([record(type="user")], 1000000) == ("0k", "0%", "0", "")

    def test_a_slot_shows_its_work_and_stage_with_its_tasks_in_code_or_verify(self):
        assert crew.holds_said({"name": "a", "stage": "verify", "counts": "3/3"}, ["unit-1", "unit", "a", "/p/a"]) == "a  verify 3/3"
        assert crew.holds_said({"name": "b", "stage": "construct", "counts": "0/2"}, ["unit-2", "unit", "b", "/p/b"]) == "b  construct"

    def test_work_held_whose_stage_was_not_read_is_unknown_and_a_free_slot_holds_nothing(self):
        assert crew.holds_said(None, ["unit-1", "unit", "a", "/p/a"]) == "a  unknown"
        assert crew.holds_said(None, None) == ""


class TestRefused:
    def test_a_working_agent_is_ended_only_with_force(self):
        assert crew.working_said("swb-1-unit-4") == "swb-1-unit-4 is working; add --force to end it anyway."

"""Reading herdr's session on a team's host (read.1, read.2): crew.listed for its `agent list` and `pane list`, which
answer every agent's status and every pane's life at a moment from one listing, as herdr 0.9.3 answers them. Reading
them through the command is the units journey's (t-journey-units)."""
import json

import pytest

import crew

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

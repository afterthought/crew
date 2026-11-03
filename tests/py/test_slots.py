"""A main level's panes and agents on its host (teams.2, teams.9, read.1, read.2), as its commands read them in one
process: crew.listed for reading herdr's listings, crew.herdr_made for reading what herdr made, crew.name_back for when
crew gives an agent its dropped name back and crew.found_answer for reading an agent on another host, and the words
crew says when it ends or starts an agent. Starting its agents through the command is the main level's journey's
(t-journey-main)."""
import json
import types

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


class TestNameBack:
    """An agent crew started is found under its name while its own session runs in its pane (briefs.17): swc-3-conductor
    on deneb, 2026-10-23, nameless in its pane once the Claude its landing card's session started for the user reported
    itself there (signal 2026-10-23-swc-3-conductor-8556b697/01)."""

    def test_an_unnamed_agent_in_its_pane_whose_session_crew_started_as_it_is_given_its_name_back(self):
        a = {"pane_id": "w7:p1", "agent_status": "idle", "agent_session": {"value": "0b1c"}}
        assert crew.name_back("swc-3-conductor", "w7:p1", a, "0b1c") == (True, None)

    def test_a_session_crew_did_not_start_as_it_is_never_given_its_name(self):
        a = {"pane_id": "w7:p1", "agent_status": "working", "agent_session": {"value": "9f2e"}}
        assert crew.name_back("swc-3-conductor", "w7:p1", a, "0b1c") == (False, (
            "herdr lists the agent in its pane w7:p1 by no name, in session 9f2e, which crew did not start as swc-3-conductor"))
        assert crew.name_back("swc-3-conductor", "w7:p1", a, None)[0] is False

    def test_an_unnamed_agent_herdr_names_no_session_for_is_a_read_crew_names(self):
        a = {"pane_id": "w7:p1", "agent_status": "idle"}
        assert crew.name_back("swc-3-conductor", "w7:p1", a, "0b1c") == (False, (
            "herdr lists the agent in its pane w7:p1 by no name and names no session for it, so crew can't tell it is swc-3-conductor"))

    def test_another_agent_in_its_pane_keeps_its_own_name(self):
        a = {"pane_id": "w7:p1", "name": "swc-3-ops", "agent_status": "idle", "agent_session": {"value": "0b1c"}}
        assert crew.name_back("swc-3-conductor", "w7:p1", a, "0b1c") == (
            False, "herdr lists no agent named swc-3-conductor, and its pane w7:p1 holds swc-3-ops")

    def test_no_agent_in_its_pane_or_no_pane_kept_is_not_up(self):
        assert crew.name_back("swc-3-conductor", "w7:p1", None, "0b1c") == (False, None)
        assert crew.name_back("swc-3-conductor", "", None, None) == (False, None)


class TestFoundAnswer:
    """read_agent of an agent on another host: herdr's agent get there, or that host's crew.py found when herdr lists
    none by its name (read.1)."""

    def ran(self, code, out="", err=""):
        return types.SimpleNamespace(returncode=code, stdout=out, stderr=err)

    @pytest.fixture(autouse=True)
    def here(self, monkeypatch):
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")

    def test_herdrs_agent_or_founds_is_the_agent_and_a_null_one_is_not_up(self):
        a = {"pane_id": "w7:p1", "name": "swc-3-conductor", "agent_status": "idle"}
        assert crew.found_answer("deneb", self.ran(0, json.dumps({"result": {"agent": a}}))) == (a, None)
        assert crew.found_answer("deneb", self.ran(0, json.dumps({"result": {"agent": None}}))) == (None, None)

    def test_what_found_could_not_read_is_named(self):
        why = "herdr lists the agent in its pane w7:p1 by no name, in session 9f2e, which crew did not start as swc-3-conductor"
        assert crew.found_answer("deneb", self.ran(0, json.dumps({"unread": why}))) == (None, why)

    def test_a_host_that_does_not_answer_a_found_that_fails_and_an_answer_crew_cant_read_are_each_named(self):
        assert crew.found_answer("deneb", self.ran(255, err="ssh: connect to host deneb port 22: Operation timed out")) == (
            None, "deneb did not answer (ssh: connect to host deneb port 22: Operation timed out)")
        assert crew.found_answer("deneb", self.ran(1, err="usage: crew.py ...")) == (
            None, "crew on deneb could not look for it in the pane it keeps for it: usage: crew.py ...")
        assert crew.found_answer("deneb", self.ran(0, "{}")) == (None, "herdr's answer on deneb about it can't be read")


# herdr's `workspace create` answer, as crew reads it and the stub herdr gives it.
CREATED = {"result": {"workspace": {"workspace_id": "w3", "label": "crw-2 units"}, "tab": {"tab_id": "w3:t1"},
                      "root_pane": {"pane_id": "w3:p1"}}}
WORKSPACE_ID = [("workspace", "workspace_id")]


def created(**workspace):
    return json.dumps({"result": {**CREATED["result"], "workspace": workspace}})


class TestMade:
    def test_a_workspace_herdr_made_is_read_with_its_id(self):
        made = crew.herdr_made("workspace", "create", 0, json.dumps(CREATED), "", "in session crw-2", WORKSPACE_ID)
        assert made["workspace"]["workspace_id"] == "w3"

    @pytest.mark.parametrize("out", [created(workspace_id="", label="crw-2 units"), created(label="crw-2 units"),
                                     created(workspace_id=None), json.dumps({"result": {"tab": {"tab_id": "w3:t1"}}})])
    def test_a_workspace_with_an_empty_or_missing_id_is_refused_as_a_malformed_answer_is(self, out):
        with pytest.raises(crew.Refusal) as e:
            crew.herdr_made("workspace", "create", 0, out, "", "in session crw-2", WORKSPACE_ID)
        assert str(e.value) == "herdr could not create a workspace in session crw-2: exit 0"
        with pytest.raises(crew.Refusal) as malformed:
            crew.herdr_made("workspace", "create", 0, "not json", "", "in session crw-2", WORKSPACE_ID)
        assert str(malformed.value) == str(e.value)

    def test_a_refusal_is_in_herdrs_words_when_it_says_any(self):
        with pytest.raises(crew.Refusal) as e:
            crew.herdr_made("workspace", "create", 1, "", 'herdr: starting\n{"error":{"code":"internal","message":"boom"}}\n',
                            "in session crw-2", WORKSPACE_ID)
        assert str(e.value) == 'herdr could not create a workspace in session crw-2: {"error":{"code":"internal","message":"boom"}}'

    def test_a_workspace_with_no_id_is_kept_nowhere_so_no_tab_is_made_against_it(self, tmp_path):
        acts = []

        class Herdr:
            def run(self, *args):
                acts.append(args[:2])
                return types.SimpleNamespace(returncode=0, stdout=created(workspace_id="", label="wldn"), stderr="")

        agents = crew.Agents(None, "main", "wldn", "wldn", "wldn-3", tmp_path, (), "/w", None)
        agents.herdr = Herdr()
        agents.ensure()
        with pytest.raises(crew.Refusal):
            agents.workspace("wldn", "/w")
        assert (tmp_path / "layout").read_text() == "" and agents.get("layout", crew.ws_key("wldn")) == ""
        assert acts == [("workspace", "create")]


class TestRefused:

    def test_a_working_agent_is_ended_only_with_force(self):
        assert crew.working_said("wldn-planner") == "wldn-planner is working; add --force to end it anyway."

    @pytest.mark.parametrize("stage, said", [(None, "wldn-ops started in w1:p2"), ("resume", "wldn-ops resumed in w1:p2")])
    def test_a_role_started_says_how(self, stage, said):
        assert crew.started_said("wldn-ops", "w1:p2", stage) == said

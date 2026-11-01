"""A team's slots, panes and status on its host (teams.1, teams.2, teams.9, teams.15, read.1, read.2), as crew unit run,
crew unit wait, crew fix and crew status decide them in one process: crew.slot_for for the slot a unit or fix runs in,
crew.lent_for for the slot a fix that finds every slot in flight takes lent, and Team.take and Team.give_back for the
lending kept in the team's files (record 0045), crew.reaped for what a team's read does with a slot, crew.held_object
for how the run record names what a slot holds,
crew.slot_pane_at for where a slot's pane opens, crew.listed for reading herdr's listings, crew.herdr_made for reading
what herdr made, crew.name_back for when crew gives an agent its dropped name back and crew.found_answer for reading
an agent on another host, crew.context_of and crew.holds_said for what status shows, and the words crew says when a
stage is refused. Taking a slot, starting its agent and sending its prompt through the command are the units journey's
(t-journey-units, t-journey-slots)."""
import json
import types

import pytest

import crew

SLOTS = ["unit-1", "unit-2", "unit-3", "unit-4"]


class TestSlotFor:
    def test_work_a_slot_holds_runs_there_and_takes_nothing(self):
        held = [["unit-1", "unit", "a", "/p/a"], ["unit-2", "unit", "b", "/p/b"]]
        assert crew.slot_for("swb-1", SLOTS, held, "b") == ("unit-2", False)

    def test_new_work_takes_the_first_slot_that_holds_nothing(self):
        held = [["unit-1", "unit", "a", "/p/a"], ["unit-3", "fix", "fix/te/tidy", "/p/fix-te--tidy"]]
        assert crew.slot_for("swb-1", SLOTS, held, "c") == ("unit-2", True)

    def test_with_every_slot_in_flight_new_work_is_refused_naming_what_each_holds(self):
        held = [[s, "unit", u, f"/p/{u}"] for s, u in zip(SLOTS, "abcd")]
        with pytest.raises(crew.Refusal) as e:
            crew.slot_for("swb-1", SLOTS, held, "e")
        assert str(e.value) == "all 4 of swb-1's slots are in flight: unit-1 holds a; unit-2 holds b; unit-3 holds c; unit-4 holds d"

    def test_work_waiting_in_a_slot_lent_to_a_fix_is_refused_until_the_fix_gives_it_back(self):
        held = [["unit-1", "unit", "a", "/p/a"], ["unit-2", "fix", "fix/te/tidy", "/p/fix-te--tidy"]]
        with pytest.raises(crew.Refusal) as e:
            crew.slot_for("swb-1", SLOTS, held, "b", [["unit-2", "chore", "b", "/p/chore-b"]])
        assert str(e.value) == ("b waits in swb-1-unit-2, lent to fix/te/tidy: it goes on there once that fix has merged "
                                "or been dropped")


class TestLentFor:
    """A fix that finds every slot in flight (teams.1, teams.3, record 0045): crw-5 on 2026-10-28, four verified chores
    in its four slots with no agent running, waiting on one fix that could get no slot."""

    HELD = [[s, "chore", c, f"/p/chore-{c}"] for s, c in zip(SLOTS, "abcd")]

    def test_with_every_slot_holding_verified_work_waiting_the_fix_takes_the_first_lent(self):
        assert crew.lent_for("crw-5", SLOTS, self.HELD, {s: "idle" for s in SLOTS}, set()) == "unit-1"
        assert crew.lent_for("crw-5", SLOTS, self.HELD, {}, set()) == "unit-1"

    def test_a_slot_whose_agent_is_running_is_never_lent(self):
        status = {"unit-1": "working", "unit-2": "blocked", "unit-3": "done"}
        assert crew.lent_for("crw-5", SLOTS, self.HELD, status, set()) == "unit-3"

    def test_a_slot_whose_stage_is_under_way_or_that_holds_a_fix_is_never_lent(self):
        held = [["unit-1", "fix", "fix/b/other", "/p/fix-b--other"]] + self.HELD[1:]
        assert crew.lent_for("crw-5", SLOTS, held, {}, {"unit-2", "unit-3"}) == "unit-4"

    def test_with_no_slot_that_can_be_lent_the_fix_is_refused_naming_why_each_is_not(self):
        held = [["unit-1", "fix", "fix/b/other", "/p/fix-b--other"]] + self.HELD[1:]
        with pytest.raises(crew.Refusal) as e:
            crew.lent_for("crw-5", SLOTS, held, {"unit-2": "working", "unit-4": "blocked"}, {"unit-3"})
        assert str(e.value) == ("all 4 of crw-5's slots are in flight, and none can be lent to a fix: unit-1 holds fix/b/other; "
                                "unit-2's agent is working on b; unit-3's stage on c has not ended; unit-4's agent is blocked on d")


class TestReaped:
    @pytest.mark.parametrize("stage, said", [
        ("merged", "swb-1-unit-1 is free: a has merged into its bolt"),
        ("landed", "swb-1-unit-1 is free: a has landed on main"),
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

    def test_a_slot_lent_to_a_fix_is_given_back_to_the_work_it_was_lent_from(self):
        assert crew.reaped("swb-1-unit-2", "swb-1", "fix/te/tidy", "merged", "idle", "b") == (
            "free", "swb-1-unit-2 is given back to b: fix/te/tidy has merged into its bolt")

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


class TestSlotPaneAt:
    def test_the_first_slot_in_flight_opens_the_units_workspace(self):
        assert crew.slot_pane_at([("conductor", "w1:p1"), ("ops", "w1:p2")], lambda p: True) == (None, None)

    def test_a_new_pane_halves_the_newest_slot_pane_right_when_an_odd_number_are_open_and_down_when_even(self):
        panes = [("conductor", "w1:p1"), ("unit-1", "w2:p3"), ("ops", "w1:p2"), ("unit-3", "w2:p5")]
        assert crew.slot_pane_at(panes[:2], lambda p: True) == ("w2:p3", "right")
        assert crew.slot_pane_at(panes, lambda p: True) == ("w2:p5", "down")

    def test_a_slot_pane_closed_is_not_counted(self):
        panes = [("unit-1", "w2:p3"), ("unit-2", "w2:p4")]
        assert crew.slot_pane_at(panes, lambda p: p != "w2:p4") == ("w2:p3", "right")


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
                return types.SimpleNamespace(returncode=0, stdout=created(workspace_id="", label="crw-2 units"), stderr="")

        agents = crew.Agents(None, "team", "crw-2", "crew", "crw-2", tmp_path, None, "/w", None)
        agents.herdr = Herdr()
        agents.ensure()
        with pytest.raises(crew.Refusal):
            agents.workspace("crw-2 units", "/w")
        assert (tmp_path / "layout").read_text() == "" and agents.get("layout", crew.ws_key("crw-2 units")) == ""
        assert acts == [("workspace", "create")]


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

    @pytest.mark.parametrize("stage, said", [(None, "swb-1-ops started in w1:p2"), ("resume", "swb-1-ops resumed in w1:p2"),
                                             ("code", "swb-1-ops started code in w1:p2")])
    def test_a_role_started_says_how(self, stage, said):
        assert crew.started_said("swb-1-ops", "w1:p2", stage) == said

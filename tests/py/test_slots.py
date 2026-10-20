"""A team's slots, panes and status on its host (teams.1, teams.2, teams.9, teams.15, read.1, read.2), as crew unit run,
crew unit wait, crew fix and crew status decide them in one process: crew.slot_for for the slot a unit or fix runs in,
crew.reaped for what a team's read does with a slot, crew.held_object for how the run record names what a slot holds,
crew.slot_pane_at for where a slot's pane opens, crew.listed for reading herdr's listings, crew.herdr_made for reading
what herdr made, crew.context_of and crew.holds_said for what status shows, and the words crew says when a stage is
refused. Taking a slot, starting its agent and sending its prompt through the command are the units journey's
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

    def test_a_unit_carried_onto_its_bolt_inside_another_merge_is_named_so_its_merge_owed(self):
        # teams.17: wldn, swb-4, 2026-10-13, signal 45f551aa/01.
        assert crew.holds_said({"name": "d", "stage": "verify", "counts": "4/4", "carried": True}, ["unit-1", "unit", "d", "/p/d"]) == (
            "d  verify 4/4  carried by another's merge, its own merge owed")
        assert crew.carried_said("d", "b1", "verify") == (
            "d is carried onto bolt/b1 inside another unit's merge, its change open there: it is in verify, its own merge "
            "owed (crew unit run d merge)")

    def test_work_held_whose_stage_was_not_read_is_unknown_and_a_free_slot_holds_nothing(self):
        assert crew.holds_said(None, ["unit-1", "unit", "a", "/p/a"]) == "a  unknown"
        assert crew.holds_said(None, None) == ""


class TestRefused:
    def test_a_team_taken_down_runs_no_stage_until_it_is_brought_up(self):
        assert crew.down_said("swb-1") == "swb-1 is down; crew up swb-1 brings it back"

    def test_a_working_agent_is_ended_only_with_force(self):
        assert crew.working_said("swb-1-unit-4") == "swb-1-unit-4 is working; add --force to end it anyway."

    @pytest.mark.parametrize("how, why, said", [
        ("never", "sent twice", "swb-1-unit-4 never took its construct prompt for d, sent twice; the stage never started and nothing is "
                                "left typed in its pane: run it again with crew unit run d construct"),
        ("unread", "it is no longer up", "crew could not tell whether swb-1-unit-4 took its construct prompt for d: it is no longer up; "
                                         "nothing more was sent, and the stage is taken as never started: run it again with crew unit run d construct"),
    ])
    def test_a_prompt_never_taken_or_not_read_as_taken_starts_no_stage_and_says_how_to_run_it_again(self, how, why, said):
        assert crew.never_started("swb-1-unit-4", "construct", "d", "unit/d", "swb-1", how, why) == said

    def test_a_fixs_stage_is_run_again_by_the_fixs_own_command(self):
        assert crew.never_started("swb-1-unit-1", "merge", "fix/te/tidy", "fix/te/tidy", "swb-1", "never", "sent twice").endswith(
            "run it again with crew fix swb-1 tidy --merge")

    @pytest.mark.parametrize("stage, said", [(None, "swb-1-ops started in w1:p2"), ("resume", "swb-1-ops resumed in w1:p2"),
                                             ("code", "swb-1-ops started code in w1:p2")])
    def test_a_role_started_says_how(self, stage, said):
        assert crew.started_said("swb-1-ops", "w1:p2", stage) == said

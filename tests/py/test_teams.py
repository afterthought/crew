"""Teams, the main level and their agents (teams.2, teams.6, teams.7, teams.11, plan.15): crew.load for what a team's
session resolves its partition, kit and blueprints to, crew.greet_waits for one look of
a greeting's wait, crew.standing_greeting for what an agent crew starts outside a team is greeted with,
crew.greeted_roles for which of a team's agents a command greets and crew.ops_greeting for what its ops is told,
crew.dispatch_place and crew.operator_session for where those run, crew.tab_holds for what an operator's tab holds,
crew.dead_said for a pane herdr lists with no terminal behind it and crew.opens_at for where a pane opens again,
crew.last_conversation for where a role resumes,
crew.brief_due and crew.brief_role for the brief a session herdr resumed is given back at a compaction,
plan.amended_said for what a conductor brought back is told, and what crew up, restart, resume, clear and needs decide
before they act. Starting, greeting, reviving and taking them down through the command are the teams journey's
(t-journey-teams, t-journey-main)."""
import json
import os

import pytest

import crew
import plan

BOX = "chuck-herdr-alpha"
FLEET = {"partitions": {"wldn": {"label": "wldn", "partition": "clients/willdan", "machine": BOX, "session": "wldn-3", "teams": ["swb-1", "atl-1"]}},
         "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": BOX, "session": "wldn-1"},
                   "atl-1": {"name": "atl-1", "label": "wldn", "machine": "mac-studio", "session": "wldn-5"}},
         "hosts": {"mac-studio": {"sessions": {"wldn": {"partition": "clients/willdan"}, "madswan": {"partition": "business"}}}}}


class TestLoad:
    """A team's partition, kit and blueprints come from the herdr session it runs in; the files' refusals are t-teams'."""

    @pytest.fixture
    def fleet(self, tmp_path, monkeypatch):
        def sess(space, partition, repos):
            return {"dir": f"{tmp_path}/{space}", "partition": partition, "repos": repos}
        willdan = ["WilldanGroup/switchboard-kit", "WilldanGroup/willdan-blueprints"]
        hosts = {BOX: {"ssh": BOX, "sessions": {s: sess("box/willdan", "clients/willdan", willdan) for s in ("wldn-1", "wldn-3")}},
                 "mac-studio": {"ssh": "mac-studio", "sessions": {
                     "madswan-1": sess("mac/madswan", "business", ["afterthought/blueprints", "afterthought/crew"]),
                     "madswan-2": sess("mac/agentplot", "business", ["agentplot/blueprints", "agentplot/flywheel-next", "agentplot/weir"])}}}
        part = {"state": "afterthought/crew-state", "review": {"every": 5, "hours": 4}}
        teams = {"version": 2,
                 "partitions": [dict(part, label="wldn", partition="clients/willdan", blueprints=["WilldanGroup/willdan-blueprints"],
                                     machine=BOX, session="wldn-3"),
                                dict(part, label="madswan", partition="business", blueprints=["afterthought/blueprints", "agentplot/blueprints"],
                                     machine="mac-studio", session="madswan-1")],
                 "teams": [{"name": "swb-1", "system": "Switchboard", "machine": BOX, "session": "wldn-1", "units": 4,
                            "repos": ["switchboard-kit", "willdan-blueprints"]},
                           {"name": "apk-1", "system": "Flywheel", "machine": "mac-studio", "session": "madswan-2", "units": 4,
                            "repos": ["flywheel-next", "blueprints"]},
                           {"name": "fwn-2", "system": "Flywheel", "machine": "mac-studio", "session": "madswan-2", "units": 2,
                            "repos": ["flywheel-next", "weir", "blueprints"]}]}
        (tmp_path / "herdr-hosts.json").write_text(json.dumps({"version": 1, "hosts": hosts}))
        (tmp_path / "teams.json").write_text(json.dumps(teams))
        monkeypatch.setattr(crew, "HOSTS", tmp_path / "herdr-hosts.json")
        monkeypatch.setattr(crew, "TEAMS", tmp_path / "teams.json")
        crew.load.cache_clear()
        yield crew.load()
        crew.load.cache_clear()

    def test_a_teams_partition_kit_and_blueprints_come_from_its_session(self, fleet, tmp_path):
        t = crew.team_of(fleet, "swb-1")
        assert (t["label"], t["units"], t["machine"], t["session"]) == ("wldn", 4, BOX, "wldn-1")
        box = f"{tmp_path}/box/willdan"
        assert (t["kit"]["main"], t["kit"]["dir"]) == (f"{box}/switchboard-kit/main", f"{box}/switchboard-kit")
        assert t["blueprints"]["main"] == f"{box}/willdan-blueprints/main"

    def test_a_team_holds_its_kits_its_first_its_kit_until_it_works_on_a_bolt_of_another(self, fleet, tmp_path):
        """A team holds its kits, one or more (record 0035): slc-1 and flm-1 both hold agentplot/weir."""
        t = crew.team_of(fleet, "fwn-2")
        mac = f"{tmp_path}/mac/agentplot"
        assert [(k["name"], k["repo"], k["main"]) for k in t["kits"]] == [
            ("flywheel-next", "agentplot/flywheel-next", f"{mac}/flywheel-next/main"), ("weir", "agentplot/weir", f"{mac}/weir/main")]
        assert t["kit"]["name"] == "flywheel-next" and t["blueprints"]["repo"] == "agentplot/blueprints"
        weir = crew.with_kit(t, "weir")
        assert (weir["kit"]["main"], weir["name"], weir["machine"]) == (f"{mac}/weir/main", "fwn-2", "mac-studio")
        assert crew.with_kit(t, "agentplot/flywheel-next") is t and crew.builds(t, "weir") and not crew.builds(t, "sluice")
        with pytest.raises(crew.Refusal, match="fwn-2 builds flywheel-next and weir, not sluice"):
            crew.with_kit(t, "sluice")
        assert [k["name"] for k in crew.team_of(fleet, "apk-1")["kits"]] == ["flywheel-next"]

    def test_a_repos_name_is_resolved_to_owner_and_name_through_the_teams_session(self, fleet, tmp_path):
        t = crew.team_of(fleet, "apk-1")
        assert (t["label"], t["blueprints"]["repo"]) == ("madswan", "agentplot/blueprints")
        assert t["blueprints"]["main"] == f"{tmp_path}/mac/agentplot/blueprints/main"


class TestRoleSessions:
    """A main-level role may run in a session of its own, named in its partition's roles (record 0035): so a
    partition's design agent and planner, both Fable, sit in two sessions on two Claude accounts."""

    def load(self, tmp_path, monkeypatch, roles, extra=None):
        def sess(space, partition, repos, account):
            return {"dir": f"{tmp_path}/{space}", "partition": partition, "repos": repos, "account": account}
        bp = ["afterthought/blueprints", "afterthought/crew"]
        hosts = {"deneb": {"ssh": "deneb", "kind": "darwin", "sessions": dict({
            "swancloud-1": sess("deneb/madswan", "personal", bp, "madswan"),
            "swancloud-2": sess("deneb/madswan", "personal", bp, "madswan-2"),
            "madswan-1": sess("deneb/madswan", "business", bp, "madswan-2")}, **(extra or {}))}}
        teams = {"version": 2, "partitions": [{"label": "swancloud", "partition": "personal", "blueprints": ["afterthought/blueprints"],
                                               "state": "afterthought/crew-state", "review": {"every": 5, "hours": 4},
                                               "machine": "deneb", "session": "swancloud-1", "roles": roles}], "teams": []}
        (tmp_path / "herdr-hosts.json").write_text(json.dumps({"version": 1, "hosts": hosts}))
        (tmp_path / "teams.json").write_text(json.dumps(teams))
        monkeypatch.setattr(crew, "HOSTS", tmp_path / "herdr-hosts.json")
        monkeypatch.setattr(crew, "TEAMS", tmp_path / "teams.json")
        crew.load.cache_clear()
        try:
            return crew.load()
        finally:
            crew.load.cache_clear()

    def test_a_role_named_a_session_runs_there_the_reviewer_beside_the_planner_and_the_rest_in_the_main_levels(self, tmp_path, monkeypatch):
        fleet = self.load(tmp_path, monkeypatch, {"planner": {"session": "swancloud-2", "effort": "max"}})
        p = crew.partition_of(fleet, "swancloud")
        assert p["sessions"] == {"design": "swancloud-1", "planner": "swancloud-2", "ops": "swancloud-1", "operator": "swancloud-1",
                                 "reviewer": "swancloud-2"}
        assert crew.place_of_agent(fleet, "swancloud-planner") == ("deneb", "swancloud-2")
        assert crew.place_of_agent(fleet, "swancloud-operator") == ("deneb", "swancloud-1")
        assert crew.main_sessions(p) == [("swancloud-1", ("design", "ops", "operator")), ("swancloud-2", ("planner",))]

    def test_with_none_named_every_role_is_in_the_main_levels_session(self, tmp_path, monkeypatch):
        p = crew.partition_of(self.load(tmp_path, monkeypatch, {}), "swancloud")
        assert crew.main_sessions(p) == [("swancloud-1", ("design", "planner", "ops", "operator"))]

    @pytest.mark.parametrize("roles, said", [
        ({"planner": {"session": "madswan-1"}}, "partition swancloud's planner runs in deneb's session madswan-1, which is in partition business, not personal"),
        ({"planner": {"session": "swancloud-9"}}, "partition swancloud's planner uses herdr session swancloud-9, which .* does not list on deneb"),
        ({"dispatcher": {"session": "swancloud-2"}}, "roles.dispatcher.session can't be named: a dispatcher runs on each host"),
        ({"planner": {"session": ""}}, "roles.planner.session must name a session of the main level's machine"),
        ({"planner": {"seat": "x"}}, "roles.planner sets only 'model', 'effort' or 'session'")])
    def test_a_session_of_another_partition_or_none_and_a_dispatchers_are_refused(self, tmp_path, monkeypatch, roles, said):
        with pytest.raises(crew.Refusal, match=said):
            self.load(tmp_path, monkeypatch, roles)

    def test_a_brief_names_where_each_main_level_role_runs_and_on_which_account(self, tmp_path, monkeypatch):
        fleet = self.load(tmp_path, monkeypatch, {"planner": {"session": "swancloud-2"}})
        monkeypatch.setattr(crew, "this_host", lambda: "deneb")
        tok = crew.main_tokens(fleet, crew.partition_of(fleet, "swancloud"), "planner", "")
        assert ("`swancloud-design` in session swancloud-1 (account madswan); `swancloud-planner` in session swancloud-2 "
                "(account madswan-2)") in tok["MAIN_SESSIONS"]
        assert tok["MAIN_SESSIONS"] in tok["ROSTER"] and tok["OPERATORS"] == "`swancloud-operator` on deneb"

    def test_a_team_overrides_no_session(self, tmp_path, monkeypatch):
        with pytest.raises(crew.Refusal, match="roles.coder sets only 'model' or 'effort'"):
            crew.roles_of({"roles": {"coder": {"session": "x"}}}, "team swb-1", crew.TEAM_ROLES)


class TestMoved:
    """A state folder's panes recorded in another session than its agents run in now name nothing there, so crew sets
    them aside rather than taking another agent at the same pane id for its own (teams.2; deneb, 2026-10-20: a stale
    swancloud-main panes file made crew main up take crw-5's agents for the design agent and planner)."""

    def test_a_folder_that_names_another_session_is_said_and_one_that_names_this_or_none_is_not(self):
        assert crew.moved_said("swancloud", "swancloud-2", "swancloud-1") == (
            "swancloud's panes were recorded in session swancloud-2, and it runs in swancloud-1 now; their ids name nothing here")
        assert crew.moved_said("swancloud", "swancloud-1", "swancloud-1") is None
        assert crew.moved_said("swancloud", "", "swancloud-1") is None


class TestGreetWaits:
    def look(self, status, asking=False, asked=False, out_of_time=False):
        return crew.greet_waits("wldn-planner", status, asking, asked, out_of_time, "crew main up wldn starts and greets it", "Read where wldn stands.")

    @pytest.mark.parametrize("status", ["idle", "done"])
    def test_an_agent_settled_with_no_question_is_greeted(self, status):
        assert self.look(status) == ("greet", None)

    def test_one_waiting_on_a_question_is_said_once_and_given_five_minutes(self):
        assert self.look("blocked", asking=True) == ("asking", "wldn-planner is waiting on a question in its pane; answer it there and it will be greeted")
        assert self.look("blocked", asking=True, asked=True) == (None, None)

    def test_one_never_ready_is_said_with_the_tell_that_would_greet_it_and_one_not_up_with_its_hint(self):
        assert self.look("working", out_of_time=True) == ("gave up", "wldn-planner was not ready to greet; once it is: crew tell wldn-planner 'Read where wldn stands.'")
        assert self.look(None, out_of_time=True) == ("gave up", "wldn-planner is not up: crew main up wldn starts and greets it")

    def test_else_it_looks_again(self):
        assert self.look("working") == (None, None)


class TestStandingGreeting:
    @pytest.mark.parametrize("name, says", [
        ("wldn-design", "curate the signals that have no move"), ("wldn-planner", "crew plan proposed"),
        ("wldn-ops", "land nothing until it comes"), ("wldn-dispatch-mac-studio", "Read where wldn stands on mac-studio with"),
        ("wldn-operator", "what is moving and what waits on me")])
    def test_each_role_has_its_greeting(self, name, says):
        label, text, why, hint = crew.standing_greeting(FLEET, name)
        assert label == "wldn" and says in text

    def test_its_entry_and_its_hint_name_the_main_level_the_operators_among_it(self):
        assert crew.standing_greeting(FLEET, "wldn-design")[2:] == ("main(wldn): greet wldn-design", "crew main up wldn starts and greets it")
        assert crew.standing_greeting(FLEET, "wldn-operator")[2:] == (
            "main(wldn): greet wldn-operator", "crew main up wldn starts and greets it")

    @pytest.mark.parametrize("name, said", [
        ("swb-1-ops", "swb-1-ops is one of team swb-1's agents, not one crew starts outside a team"),
        ("wldn-reviewer", "wldn-reviewer is sent its batch as its prompt by crew review, and is not greeted"),
        ("nobody", "no agent nobody: crew starts none by that name")])
    def test_a_teams_agent_the_reviewer_and_an_unknown_name_are_refused(self, name, said):
        with pytest.raises(crew.Refusal, match=said):
            crew.standing_greeting(FLEET, name)


class TestTeamGreetings:
    """Every agent crew starts gets a first message, so it has a conversation a resume after a herdr restart can pick up
    (teams.7): crw-2's give of 2026-10-19 restarted its conductor and ops and greeted only the conductor, so herdr's
    resume of crw-2-ops found no conversation and left its pane a shell, and crew resume then started it fresh and
    ungreeted again."""

    @pytest.mark.parametrize("act", ["up", "rebuild", "restart", "give"])
    def test_each_role_a_command_starts_fresh_is_greeted_ops_with_the_conductor(self, act):
        assert crew.greeted_roles(act, ["conductor", "ops"], ["conductor", "ops"]) == ["conductor", "ops"]
        assert crew.greeted_roles(act, ["ops"], ["ops"]) == ["ops"]

    def test_a_restart_told_not_to_greet_greets_none_since_its_caller_does(self):
        assert crew.greeted_roles("restart", ["conductor", "ops"], ["conductor", "ops"], greet=False) == []

    def test_a_resume_greets_what_it_had_to_start_fresh_and_nothing_it_brought_back_with_its_conversation(self):
        assert crew.greeted_roles("resume", ["ops"], ["ops"]) == ["ops"]
        assert crew.greeted_roles("resume", ["conductor", "ops"], ["ops"]) == ["ops"]
        assert crew.greeted_roles("resume", ["conductor", "ops"], []) == []

    def test_a_revive_greets_the_conductor_it_brought_back_and_ops_only_when_it_started_fresh(self):
        assert crew.greeted_roles("revive", ["conductor", "ops"], []) == ["conductor"]
        assert crew.greeted_roles("revive", ["ops"], []) == []
        assert crew.greeted_roles("revive", ["ops"], ["ops"]) == ["ops"]

    def test_ops_is_told_who_it_is_what_its_team_holds_and_to_wait_to_be_told(self):
        assert crew.ops_greeting("crw-2", "tells-reach-the-pane") == (
            "You are crw-2's ops; your team holds the bolt tells-reach-the-pane. Nothing is asked of you now: reply in "
            "one line, then wait until your conductor or I tell you what is needed.")
        assert "your team holds no bolt. Nothing is asked of you now" in crew.ops_greeting("crw-2", None)

    def test_a_conductor_of_a_team_holding_two_bolts_is_told_both_its_landing_card_and_each_fix_in_flight(self):
        """A give beside a waiting bolt restarts the conductor fresh at its next stop (teams.16)."""
        assert plan.two_bolts_said("swc-1", "ssh-fix", "doctor-rows", ("land/doctor-rows", "req_7"), ["take-main"]) == (
            "Your team now builds the bolt ssh-fix. Bolt doctor-rows waits to land; its landing card land/doctor-rows is "
            "yours: call get_request (requestId req_7, name swc-1-conductor), then run crew card wait land/doctor-rows in "
            "the background. Fix take-main is in flight on it: wait on it with crew fix swc-1 take-main --wait --bolt doctor-rows.")

    def test_with_no_card_or_fix_it_names_both_bolts_and_a_kit_not_read_is_said(self):
        assert plan.two_bolts_said("swc-1", "ssh-fix", "doctor-rows", None, []) == "Your team now builds the bolt ssh-fix. Bolt doctor-rows waits to land."
        assert plan.two_bolts_said("swc-1", "ssh-fix", "doctor-rows", None, None, "box did not answer").endswith(
            "waits to land. crew could not read its fixes (box did not answer): read crew status swc-1.")

    def test_status_names_the_bolt_a_team_builds_and_the_one_waiting_to_land(self):
        assert plan.two_held_said("swc-1", "ssh-fix", "doctor-rows") == "swc-1 builds ssh-fix; doctor-rows waits to land"

    def test_a_give_beside_a_waiting_bolt_says_its_roles_start_again_at_their_next_stop(self):
        assert plan.given_beside("swc-1", "ssh-fix", ["conductor", "ops"], 0, "") == (
            "swc-1-conductor and swc-1-ops start again on bolt/ssh-fix at their next stop")
        assert plan.given_beside("swc-1", "ssh-fix", ["ops"], 0, "") == "swc-1-ops starts again on bolt/ssh-fix at its next stop"
        assert plan.given_beside("swc-1", "ssh-fix", ["conductor", "ops"], 255, "") == (
            "swc-1's host did not answer: swc-1-conductor and swc-1-ops carry bolt/ssh-fix once next started")

    def test_ops_of_a_team_holding_two_bolts_is_told_the_one_it_builds_and_the_one_waiting(self):
        assert crew.ops_greeting("swc-1", "ssh-fix", waiting="doctor-rows").startswith(
            "You are swc-1's ops; your team builds the bolt ssh-fix. Bolt doctor-rows waits to land. Nothing is asked of you now")

    def test_a_plan_crew_could_not_read_is_said_rather_than_no_bolt(self):
        said = crew.ops_greeting("crw-2", None, "wldn/main of afterthought/crew-state could not be read:\nfatal: unable to access")
        assert "crew could not read which bolt your team holds (wldn/main of afterthought/crew-state could not be read: fatal: " \
               "unable to access). Nothing is asked of you now" in said
        assert "holds no bolt" not in said


class TestPlaces:
    def test_a_dispatcher_runs_in_the_main_levels_session_on_its_host_else_in_its_first_teams(self):
        assert crew.dispatch_place(FLEET, "wldn", BOX) == "wldn-3"
        assert crew.dispatch_place(FLEET, "wldn", "mac-studio") == "wldn-5"
        with pytest.raises(crew.Refusal, match="no team of wldn runs on macbook-pro, so macbook-pro has no dispatcher"):
            crew.dispatch_place(FLEET, "wldn", "macbook-pro")

    def test_an_operator_runs_in_the_session_named_for_its_partition(self):
        assert crew.operator_session(FLEET, "wldn", "mac-studio") == {"partition": "clients/willdan"}
        with pytest.raises(crew.Refusal, match=f"{BOX} has no session named wldn"):
            crew.operator_session(FLEET, "wldn", BOX)
        fleet = dict(FLEET, partitions=dict(FLEET["partitions"], madswan={"label": "madswan", "partition": "personal"}))
        with pytest.raises(crew.Refusal, match="mac-studio's session madswan is in partition business, not personal"):
            crew.operator_session(fleet, "madswan", "mac-studio")


# herdr 0.9.3's pane process-info on mac-studio, 2026-10-18: swancloud's rail tab (w2:pF) as herdr brought it back after
# the host's restart of 2026-10-15, its shell alone, the loop that wrote the agents' views gone with the restart.
RESTORED = {"foreground_process_group_id": 2301, "pane_id": "w2:pF", "shell_pid": 2301,
            "foreground_processes": [{"argv": ["-zsh"], "argv0": "zsh", "cmdline": "-zsh", "cwd": "/Users/chuck", "name": "zsh", "pid": 2301}]}


def running(*argvs):
    return {"foreground_process_group_id": 9001, "pane_id": "w2:pF", "shell_pid": 2301,
            "foreground_processes": [{"argv": list(a), "pid": 9001 + i} for i, a in enumerate(argvs)]}


class TestOperatorTabs:
    """What crew console up finds in a tab's pane it opened before (crew.tab_holds, code.7): its loop running, the
    shell alone a restart left, which runs the loop again, or something else, which crew leaves (read.4)."""

    def test_a_pane_a_restart_left_holds_its_shell_alone_and_its_loop_runs_again(self):
        assert crew.tab_holds(RESTORED, ["_rail", "swancloud"]) == ("shell", None)

    def test_a_tabs_loop_runs_when_a_foreground_process_ends_with_its_words_and_the_bash_its_crew_execs_keeps_them(self):
        rail = running(["bash", "/c/plugin/bin/crew", "_rail", "swancloud"], ["python3", "/c/plugin/lib/record.py", "events", "--follow", "--label", "swancloud"])
        assert crew.tab_holds(rail, ["_rail", "swancloud"]) == ("running", None)
        flow = running(["python3", "/c/plugin/bin/../lib/record.py", "events", "--follow", "--label", "swancloud"])
        assert crew.tab_holds(flow, ["events", "--follow", "--label", "swancloud"]) == ("running", None)

    def test_anything_else_in_the_foreground_is_left_and_named(self):
        assert crew.tab_holds(running(["less", "notes"]), ["_board", "swancloud"]) == ("other", "less notes")
        assert crew.tab_holds(running(["bash", "/c/plugin/bin/crew", "_rail", "wldn"]), ["_rail", "swancloud"]) == ("other", "bash /c/plugin/bin/crew _rail wldn")
        assert crew.tab_holds(running(), ["_board", "swancloud"]) == ("other", "process group 9001")

    @pytest.mark.parametrize("info", [None, {}, {"shell_pid": 1, "foreground_process_group_id": "1", "foreground_processes": []},
                                      {"shell_pid": 1, "foreground_process_group_id": 1}])
    def test_an_answer_crew_cant_read_is_said_and_runs_nothing(self, info):
        assert crew.tab_holds(info, ["_rail", "swancloud"]) == (None, "herdr's process-info for it can't be read")


# herdr 0.9.3's pane list of swancloud's session on mac-studio, 2026-10-19: crw-3's w10:p6, which herdr could not bring
# back at its restart, its folder a worktree since removed, and crw-1's conductor pane, brought back with its shell.
DEAD = {"agent_status": "unknown", "cwd": "/c/crew.git/wt/trash/the-board-is-a-page-1791745030", "focused": False,
        "pane_id": "w10:p6", "restore_error": "Saved directory is unavailable. Restore the directory and restart this session.",
        "revision": 0, "tab_id": "w10:t1", "terminal_id": "term_65e35acc23da81a", "workspace_id": "w10"}
BACK = {"agent_status": "unknown", "cwd": "/c/bolts/curation-and-holds", "focused": False, "foreground_cwd": "/c/bolts/curation-and-holds",
        "pane_id": "w3:p1", "revision": 0, "scroll": {"max_offset_from_bottom": 0, "offset_from_bottom": 0, "viewport_rows": 77},
        "tab_id": "w3:t1", "terminal_id": "term_65e35acc0e86bf", "workspace_id": "w3"}


class TestDeadPanes:
    """A pane crew keeps that herdr lists with no terminal behind it, as crw-2's were when crew up did not bring its
    conductor back at test D (2026-10-18), is dead (crew.dead_said, teams.2); one an agent holds never is (read.4); and a
    pane not there opens again beside its tab's other pane, else in its workspace while that stands (crew.opens_at);
    crew revive opens again a pane brought back dead and picks up one brought back empty (crew.revived). Closing and
    opening them through crew up is the teams journey's, through crew revive and crew main up the main journey's."""

    def test_a_pane_herdr_could_not_bring_back_is_dead_said_with_its_folder_and_herdrs_words(self):
        assert crew.dead_said("crw-3", "conductor", DEAD, None) == (
            "crw-3's conductor pane w10:p6 is dead: herdr could not bring it back in /c/crew.git/wt/trash/the-board-is-a-page-1791745030 "
            "(Saved directory is unavailable. Restore the directory and restart this session.)")
        assert crew.dead_said("crw-3", "ops", {k: v for k, v in DEAD.items() if k != "cwd"}, None) == (
            "crw-3's ops pane w10:p6 is dead: herdr could not bring it back (Saved directory is unavailable. Restore the directory and "
            "restart this session.)")

    def test_a_pane_brought_back_with_its_shell_or_not_listed_is_not_dead(self):
        assert crew.dead_said("crw-1", "conductor", BACK, None) is None
        assert crew.dead_said("crw-1", "conductor", None, None) is None

    @pytest.mark.parametrize("status", ["idle", "working", "blocked", "done"])
    def test_a_pane_an_agent_holds_is_never_dead(self, status):
        assert crew.dead_said("crw-3", "conductor", DEAD, status) is None

    @pytest.mark.parametrize("err", ["", "  ", None, 1, ["Saved directory is unavailable."]])
    def test_a_restore_error_with_no_words_is_not_read_as_one(self, err):
        assert crew.dead_said("crw-3", "conductor", dict(DEAD, restore_error=err), None) is None

    def test_revive_opens_again_a_pane_brought_back_dead_and_picks_up_one_brought_back_empty(self):
        assert crew.revived(DEAD, None) == "dead"
        assert crew.revived(BACK, None) == "empty"

    @pytest.mark.parametrize("item, status", [(BACK, "idle"), (DEAD, "working"), (None, None)])
    def test_revive_leaves_a_pane_an_agent_holds_and_one_herdr_does_not_list(self, item, status):
        assert crew.revived(item, status) is None

    def test_a_pane_opens_beside_its_tabs_other_pane_else_in_its_workspace_while_it_stands_else_in_a_new_one(self):
        assert crew.opens_at("w2X:p2", "w2X") == ("split", "w2X:p2")
        assert crew.opens_at("", "w2X") == ("tab", "w2X")
        assert crew.opens_at("", "") == ("workspace", None)


class TestResume:
    @pytest.fixture
    def home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setattr(crew, "SESSIONS", tmp_path / ".local/state/crew/sessions")
        crew.SESSIONS.mkdir(parents=True)
        return tmp_path

    def session(self, home, sid, agent, cwd=None, spoken=True, mtime=0, began=None):
        (crew.SESSIONS / sid).write_text(f"CREW_AGENT={agent}\nCREW_LABEL=wldn\n" + (f"CREW_CWD={cwd}\n" if cwd else ""))
        os.utime(crew.SESSIONS / sid, (mtime, mtime))
        if spoken:
            d = home / ".claude/projects/-work"
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{sid}.jsonl").write_text(json.dumps({"type": "user", "cwd": began or cwd}) + "\n")

    def test_a_role_resumes_its_last_conversation_in_the_folder_it_began_in(self, home):
        (home / "kit").mkdir(); (home / "bolt").mkdir()
        self.session(home, "s1", "swb-1-conductor", str(home / "kit"), mtime=1)
        assert crew.last_conversation("swb-1-conductor") == ("s1", str(home / "kit"))
        self.session(home, "s2", "swb-1-conductor", str(home / "bolt"), mtime=2)
        assert crew.last_conversation("swb-1-conductor") == ("s2", str(home / "bolt"))

    def test_a_last_session_never_spoken_to_starts_fresh_not_the_one_before(self, home):
        (home / "kit").mkdir()
        self.session(home, "s1", "swb-1-conductor", str(home / "kit"), mtime=1)
        self.session(home, "s2", "swb-1-conductor", str(home / "kit"), spoken=False, mtime=2)
        assert crew.last_conversation("swb-1-conductor") is None

    def test_a_record_kept_before_the_folder_was_is_read_from_its_transcript(self, home):
        (home / "kit").mkdir()
        self.session(home, "old", "swb-1-ops", None, began=str(home / "kit"), mtime=1)
        assert crew.last_conversation("swb-1-ops") == ("old", str(home / "kit"))

    def test_a_folder_gone_is_not_resumed(self, home):
        self.session(home, "s1", "swb-1-ops", str(home / "gone"), mtime=1)
        assert crew.last_conversation("swb-1-ops") is None


class TestBriefBack:
    SAVED = {"CREW_AGENT": "swb-1-conductor", "CREW_LABEL": "wldn", "CREW_CWD": "/kit", "CREW_ROLE": "conductor"}

    def test_a_compaction_of_a_session_herdr_resumed_gives_its_agents_brief_back(self):
        assert crew.brief_due("compact", False, self.SAVED) == "swb-1-conductor"

    @pytest.mark.parametrize("source", ["resume", "startup", "clear", "fork", None])
    def test_any_other_start_gives_none_a_resume_keeping_the_brief_in_its_transcript(self, source):
        assert crew.brief_due(source, False, self.SAVED) is None

    def test_a_session_crew_role_started_carries_its_brief_through_a_compaction_and_is_given_none(self):
        assert crew.brief_due("compact", True, self.SAVED) is None

    @pytest.mark.parametrize("saved", [{}, {"CREW_AGENT": ""}, {"CREW_LABEL": "wldn"}])
    def test_a_session_no_crew_agent_is_recorded_for_is_given_none(self, saved):
        assert crew.brief_due("compact", False, saved) is None

    @pytest.mark.parametrize("name, recorded, found", [
        ("swb-1-unit-2", "coder", ("swb-1", "coder")), ("swb-1-unit-2", "verify", ("swb-1", "verify")),
        ("swb-1-conductor", "conductor", ("swb-1", "conductor")), ("wldn-ops", "main-ops", ("wldn", "main-ops"))])
    def test_the_brief_is_built_from_the_definition_crew_role_recorded(self, name, recorded, found):
        assert crew.brief_role(FLEET, name, recorded) == found

    @pytest.mark.parametrize("name, found", [
        ("swb-1-conductor", ("swb-1", "conductor")), ("swb-1-ops", ("swb-1", "ops")), ("atl-1-ops", ("atl-1", "ops")),
        ("wldn-design", ("wldn", "design")), ("wldn-planner", ("wldn", "planner")), ("wldn-ops", ("wldn", "main-ops")),
        ("wldn-reviewer", ("wldn", "reviewer")), ("wldn-dispatch-chuck-herdr-alpha", ("wldn", "dispatcher")),
        ("wldn-operator", ("wldn", "operator"))])
    def test_a_session_recorded_before_crew_role_named_its_definition_is_given_the_one_its_name_gives(self, name, found):
        assert crew.brief_role(FLEET, name, "") == found
        assert crew.brief_role(FLEET, name, None) == found

    def test_a_unit_slots_name_gives_no_definition_since_its_stage_does(self):
        with pytest.raises(crew.Refusal, match="swb-1-unit-2's session record names no definition"):
            crew.brief_role(FLEET, "swb-1-unit-2", "")

    def test_a_name_crew_starts_no_agent_by_is_refused(self):
        with pytest.raises(crew.Refusal, match="no agent swb-9-conductor"):
            crew.brief_role(FLEET, "swb-9-conductor", "conductor")

    def test_the_brief_comes_back_whole_behind_a_line_saying_what_it_is_and_to_read_a_file_it_is_cut_to(self):
        said = crew.brief_back_said("swb-1-conductor", "You are swb-1's conductor.\n\nKeep the bolt moving.")
        first, rest = said.split("\n\n", 1)
        assert first.startswith("[crew] This is your brief as swb-1-conductor") and "read that file whole now" in first
        assert rest == "You are swb-1's conductor.\n\nKeep the bolt moving."


class TestAmended:
    def test_a_conductor_brought_back_is_told_each_unit_waiting_amended(self):
        assert plan.amended_said(["amended-one"], []) == (
            "Unit amended-one was amended and no construct runs on it: run construct on it now (crew unit run amended-one construct).")
        assert plan.amended_said(["a", "b"], []).startswith("Units a, b were amended and no construct runs on them")
        assert plan.amended_said([], []) == ""

    def test_a_plan_crew_cannot_read_is_said_rather_than_name_no_unit(self):
        assert plan.amended_said([], ["wldn/main of WilldanGroup/crew-state could not be read: could not\nfetch wldn/main"]) == (
            "crew could not read whether a unit of your bolt waits amended (wldn/main of WilldanGroup/crew-state could not be read: "
            "could not fetch wldn/main): read crew bolts.")


def test_a_partition_crew_does_not_know_is_refused_and_one_with_no_teams_has_no_dispatcher():
    with pytest.raises(crew.Refusal, match="no partition 'nope'. partitions: wldn"):
        crew.partition_of(FLEET, "nope")
    fleet = dict(FLEET, partitions=dict(FLEET["partitions"], swancloud={"label": "swancloud", "teams": []}))
    assert crew.partition_hosts(fleet, "swancloud") == [] and crew.partition_hosts(FLEET, "wldn") == [BOX, "mac-studio"]


def test_a_greeting_never_taken_says_the_tell_that_would_send_it_once_the_agent_is_ready():
    again = "once it is ready: crew tell swb-1-conductor 'Read where your bolt stands.'"
    assert crew.untaken_said("swb-1-conductor", "its greeting", "never", "sent twice", again) == (
        "swb-1-conductor did not take its greeting, sent twice; nothing is left typed; " + again)
    assert crew.untaken_said("swb-1-conductor", "its greeting", "unread", "it went to work") == (
        "crew could not tell whether swb-1-conductor took its greeting: it went to work; nothing more was sent")


class TestStandingCommands:
    """What crew up, restart, resume, clear and needs decide before they act on an agent (teams.2), as plan.py's
    commands decide them in one process; acting on the agents is the teams journey's (t-journey-teams)."""

    def test_named_roles_are_acted_on_and_none_named_is_every_standing_role(self):
        assert crew.roles_picked(["ops"], ("conductor", "ops")) == ["ops"]
        assert crew.roles_picked([], ("conductor", "ops")) == ["conductor", "ops"]

    def test_a_role_the_scope_has_not_is_refused_naming_its_roles(self):
        with pytest.raises(crew.Refusal) as e:
            crew.roles_picked(["fable"], ("conductor", "ops"))
        assert str(e.value) == "no role 'fable' here; roles: conductor ops"

    def test_a_team_with_an_agent_up_is_not_brought_up_over_it(self):
        assert crew.already_up_said("swb-1-conductor", "swb-1") == "swb-1-conductor is already up; use: crew restart swb-1"

    @pytest.mark.parametrize("status, force, said", [
        (None, False, "swb-1-ops is not up."),
        ("working", False, "swb-1-ops is working; add --force to clear it anyway."),
        ("working", True, None), ("idle", False, None), ("blocked", False, None)])
    def test_clear_is_sent_only_to_an_agent_that_is_up_and_not_working_unless_forced(self, status, force, said):
        assert crew.clear_refusal("swb-1-ops", status, force) == said

    @pytest.mark.parametrize("who, found", [
        ("swb-1-unit-4", ("swb-1", "unit-4")), ("swb-1-ops", ("swb-1", "ops")), ("swb-1-conductor", ("swb-1", "conductor")),
        ("swb-2-unit-1", ("swb-2", "unit-1")), ("swb-1-unit-0", None), ("wldn-planner", None), ("chuck@mac-studio", None)])
    def test_needs_reads_its_team_and_slot_from_the_agents_name(self, who, found):
        assert crew.stage_agent(["swb-1", "swb-2", "atl-1"], who) == found

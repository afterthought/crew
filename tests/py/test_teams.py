"""Teams, the main level and their agents (teams.2, teams.6, teams.7, teams.11, plan.15): crew.load for what a team's
session resolves its partition, kit and blueprints to, crew.greet_waits for one look of
a greeting's wait, crew.standing_greeting for what an agent crew starts outside a team is greeted with,
crew.dispatch_place and crew.operator_session for where those run, crew.tab_holds for what an operator's tab holds,
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
                     "madswan-2": sess("mac/agentplot", "business", ["agentplot/blueprints", "agentplot/flywheel-next"])}}}
        part = {"state": "afterthought/crew-state", "review": {"every": 5, "hours": 4}}
        teams = {"version": 2,
                 "partitions": [dict(part, label="wldn", partition="clients/willdan", blueprints=["WilldanGroup/willdan-blueprints"],
                                     machine=BOX, session="wldn-3"),
                                dict(part, label="madswan", partition="business", blueprints=["afterthought/blueprints", "agentplot/blueprints"],
                                     machine="mac-studio", session="madswan-1")],
                 "teams": [{"name": "swb-1", "system": "Switchboard", "machine": BOX, "session": "wldn-1", "units": 4,
                            "repos": ["switchboard-kit", "willdan-blueprints"]},
                           {"name": "apk-1", "system": "Flywheel", "machine": "mac-studio", "session": "madswan-2", "units": 4,
                            "repos": ["flywheel-next", "blueprints"]}]}
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

    def test_a_repos_name_is_resolved_to_owner_and_name_through_the_teams_session(self, fleet, tmp_path):
        t = crew.team_of(fleet, "apk-1")
        assert (t["label"], t["blueprints"]["repo"]) == ("madswan", "agentplot/blueprints")
        assert t["blueprints"]["main"] == f"{tmp_path}/mac/agentplot/blueprints/main"


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
        ("wldn-operator-mac-studio", "what is moving and what waits on me")])
    def test_each_role_has_its_greeting(self, name, says):
        label, text, why, hint = crew.standing_greeting(FLEET, name)
        assert label == "wldn" and says in text

    def test_its_entry_and_its_hint_name_the_main_level_or_the_operator(self):
        assert crew.standing_greeting(FLEET, "wldn-design")[2:] == ("main(wldn): greet wldn-design", "crew main up wldn starts and greets it")
        assert crew.standing_greeting(FLEET, "wldn-operator-mac-studio")[2:] == (
            "operator(wldn): greet wldn-operator-mac-studio", "crew operator up wldn starts and greets it")

    @pytest.mark.parametrize("name, said", [
        ("swb-1-ops", "swb-1-ops is one of team swb-1's agents, not one crew starts outside a team"),
        ("wldn-reviewer", "wldn-reviewer is sent its batch as its prompt by crew review, and is not greeted"),
        ("nobody", "no agent nobody: crew starts none by that name")])
    def test_a_teams_agent_the_reviewer_and_an_unknown_name_are_refused(self, name, said):
        with pytest.raises(crew.Refusal, match=said):
            crew.standing_greeting(FLEET, name)


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
    """What crew operator up finds in a tab's pane it opened before (crew.tab_holds, code.7): its loop running, the
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
        ("wldn-operator-mac-studio", ("wldn", "operator"))])
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

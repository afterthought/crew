"""A host's hold and crew's updates reaching its agents (teams.19): which standing agent an update makes due a restart,
and why; what keeps a held host from being quiet; when a due agent may be restarted, how its exit ends crew's waits at
Claude Code's question, and what it is told; which
background work is one of crew's waits; the hold read from its file; which agents run on a host; and what the agents'
bands say of the crew they run and of the hold. That crew hold, go and update run on each host they name, end and bring
back the agents there, and that the hooks record a start's crew and hand a due agent its restart, is the hold journey's
(t-hold)."""
import json
import types

import pytest

import board
import crew
import hold
import transcript
from facts import FLEET

C1, C2 = "1" * 40, "2" * 40


@pytest.fixture(autouse=True)
def on_mac_studio(monkeypatch):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
STARTED = {"session": "sid-1", "commit": C1, "version": "v0.12.1", "launch": "abc"}


class TestDue:
    def test_an_agent_whose_brief_model_effort_or_folders_changed_is_due(self):
        assert crew.update_due(STARTED, C1, "def", None) == (True, "its brief, model, effort or folders changed")

    def test_an_agent_whose_loaded_plugin_changed_is_due_and_one_whose_crew_code_alone_changed_is_not(self):
        assert crew.update_due(STARTED, C2, "abc", True) == (True, "crew's plugin changed")
        assert crew.update_due(STARTED, C2, "abc", False) == (False, None)

    def test_an_agent_on_crew_as_it_is_is_not_due(self):
        assert crew.update_due(STARTED, C1, "abc", None) == (False, None)

    def test_one_started_before_crew_kept_what_it_loaded_is_due(self):
        assert crew.update_due(dict(STARTED, commit=None, version=None, launch=None), C1, "abc", None) == (True, "it started before crew kept what an agent loads")
        assert crew.update_due(dict(STARTED, launch=None), C1, "abc", None)[0]

    def test_one_that_recorded_its_launch_and_no_commit_is_due_when_its_launch_changed(self):
        released = dict(STARTED, commit=None, version=None)
        assert crew.update_due(released, None, "def", None) == (True, "its brief, model, effort or folders changed")
        assert crew.update_due(released, C1, "def", None) == (True, "its brief, model, effort or folders changed")

    def test_one_that_recorded_its_launch_and_no_commit_is_not_due_and_says_a_pin_bump_needs_a_rebuild(self):
        released = dict(STARTED, commit=None, version=None)
        for commit in (None, C1):
            due, why = crew.update_due(released, commit, "abc", None)
            assert not due and why == crew.NO_COMMIT_SAID
        assert "can't tell whether its plugin changed since it started" in why and "crew rebuild" in why
        assert "until crew reads its release where it runs" in why

    def test_crew_that_cannot_tell_whether_the_plugin_changed_restarts_nothing_and_says_so(self):
        assert crew.update_due(STARTED, C2, "abc", None) == (False, f"crew can't tell whether its plugin changed since {C1[:7]}")

    def test_an_agent_with_no_recorded_start_is_never_due(self):
        assert crew.update_due(None, C1, "abc", True) == (False, None)

    def test_the_launch_digest_follows_the_model_effort_folders_and_brief_and_not_the_folders_order(self):
        l = {"model": "opus", "effort": "high", "dirs": ["/a", "/b"]}
        d = crew.launch_digest(l, "brief")
        assert d == crew.launch_digest(dict(l, dirs=["/b", "/a"]), "brief") and len(d) == 16
        assert len({d, crew.launch_digest(dict(l, model="sonnet"), "brief"), crew.launch_digest(dict(l, effort="max"), "brief"),
                    crew.launch_digest(dict(l, dirs=["/a"]), "brief"), crew.launch_digest(l, "brief, amended")}) == 5


class TestCrossing:
    """A crossed team's conductor and ops are due an end, never a restart (the change
    teams-cross-to-flume-as-their-bolts-land, Decision 3): crew.end_due and crew.due_of read it from the team's path
    (plan.crossing_path), the plan read only when the team's setting names a stream. That crew _renew ends each once
    idle and the last end closes the team and records team.cross is the cross journey's (t-journey-cross)."""
    FLEET = {"teams": {"crw-4": {"name": "crw-4", "flume": "madswan", "label": "madswan", "machine": "mac-studio"},
                       "crw-5": {"name": "crw-5", "flume": False, "label": "madswan", "machine": "mac-studio"}},
             "partitions": {"madswan": {"label": "madswan", "machine": "mac-studio", "teams": ["crw-4", "crw-5"]}}}

    def paths(self, monkeypatch, path):
        """Each team's path as given, or the refusal given; the names of the teams whose plan was read."""
        import plan
        read = []

        def crossing_path(fleet, t):
            read.append(t["name"])
            if isinstance(path, Exception):
                raise path
            return path
        monkeypatch.setattr(plan, "crossing_path", crossing_path)
        monkeypatch.setattr(crew, "load", lambda: self.FLEET)
        return read

    def test_a_crossed_teams_conductor_and_ops_are_due_an_end_and_nothing_else_of_crews_is(self, monkeypatch):
        self.paths(monkeypatch, ("crossed", None))
        for name in ("crw-4-conductor", "crw-4-ops"):
            assert crew.end_due(self.FLEET, name)
            assert crew.due_of(self.FLEET, name, STARTED, C1) == (True, crew.CROSSED_SAID, STARTED)
        assert not crew.end_due(self.FLEET, "crw-4-unit-1") and not crew.end_due(self.FLEET, "madswan-planner")

    @pytest.mark.parametrize("path", [("due", "cross"), ("today", None), ("due", "back")])
    def test_a_team_that_has_not_crossed_keeps_its_agents(self, monkeypatch, path):
        self.paths(monkeypatch, path)
        assert not crew.end_due(self.FLEET, "crw-4-conductor")

    def test_a_team_whose_setting_is_off_has_not_crossed_and_its_plan_is_not_read(self, monkeypatch):
        read = self.paths(monkeypatch, ("crossed", None))
        assert not crew.end_due(self.FLEET, "crw-5-conductor") and read == []

    def test_a_plan_that_cannot_be_read_ends_nothing_and_says_so(self, monkeypatch, capsys):
        self.paths(monkeypatch, crew.Refusal("can't tell whether crw-4 has crossed to Flume: madswan/main could not be read: timed out"))
        assert not crew.end_due(self.FLEET, "crw-4-ops")
        assert "whether crw-4-ops is due an end can't be told: can't tell whether crw-4 has crossed to Flume" in capsys.readouterr().err

    def test_the_dispatchers_are_told_a_crossed_team_takes_bolts_of_its_kits_whenever_one_is_planned(self):
        assert hold.crossed_told("crw-4", ["crew", "weir"]) == (
            "crw-4 has crossed to Flume: it takes a bolt of crew or weir whenever one is planned, never full, its work running in "
            "Flume places. Give it the next planned bolt of its kits.")


class TestStanding:
    @pytest.mark.parametrize("name, role", [
        ("swb-1-conductor", ("swb-1", "conductor")), ("swb-1-ops", ("swb-1", "ops")), ("wldn-design", ("wldn", "design")),
        ("wldn-planner", ("wldn", "planner")), ("wldn-ops", ("wldn", "ops")), ("wldn-operator", ("wldn", "operator")),
        ("wldn-dispatch-chuck-herdr-alpha", ("wldn", "dispatcher")), ("swb-1-unit-2", None), ("wldn-reviewer", None), ("nobody", None)])
    def test_only_a_standing_agent_is_restarted_for_an_update(self, name, role):
        assert crew.standing_role(FLEET, name) == role

    def test_the_agents_on_a_host_are_its_teams_its_main_levels_and_its_dispatchers(self, monkeypatch):
        fleet = {"teams": {"crw-4": {"machine": "deneb", "label": "swancloud"}, "swc-1": {"machine": "mac-studio", "label": "swancloud"},
                           "pay-1": {"machine": "deneb", "label": "madswan"}},
                 "partitions": {"swancloud": {"machine": "deneb", "teams": ["crw-4", "swc-1"]},
                                "madswan": {"machine": "mac-studio", "teams": ["pay-1"]}}}
        monkeypatch.setattr(crew, "this_host", lambda: "deneb")
        assert crew.agents_here(fleet) == ["pay-1-conductor", "pay-1-ops", "madswan-dispatch-deneb", "crw-4-conductor", "crw-4-ops",
                                           "swancloud-design", "swancloud-planner", "swancloud-ops", "swancloud-operator", "swancloud-dispatch-deneb"]
        assert crew.agents_here(fleet, "madswan") == ["pay-1-conductor", "pay-1-ops", "madswan-dispatch-deneb"]


class TestStarts:
    def test_the_newest_session_of_each_agent_is_its_start(self, tmp_path, monkeypatch):
        monkeypatch.setattr(crew, "SESSIONS", tmp_path)
        (tmp_path / "old").write_text("CREW_AGENT=wldn-ops\nCREW_COMMIT=" + C1 + "\n")
        (tmp_path / "new").write_text(f"CREW_AGENT=wldn-ops\nCREW_COMMIT={C2}\nCREW_VERSION=v0.13.0\nCREW_LAUNCH=abc\n")
        (tmp_path / "other").write_text("CREW_AGENT=wldn-design\n")
        import os
        os.utime(tmp_path / "old", (1, 1))
        assert crew.start_of("wldn-ops") == {"session": "new", "commit": C2, "version": "v0.13.0", "launch": "abc", "branch": None}
        assert crew.start_of("wldn-design") == {"session": "other", "commit": None, "version": None, "launch": None, "branch": None}
        assert crew.start_of("wldn-planner") is None


class TestHeld:
    def test_a_host_with_no_hold_file_is_not_held_and_one_crew_cannot_read_is(self, tmp_path, monkeypatch):
        monkeypatch.setattr(crew, "HOLD", tmp_path / "hold")
        assert crew.held() is None
        (tmp_path / "hold").write_text(json.dumps({"by": "fleet-releases", "why": "herdr 0.9.6", "at": "2026-10-21T03:00Z", "now": False}))
        assert crew.held()["why"] == "herdr 0.9.6"
        (tmp_path / "hold").write_text("{")
        assert crew.held() == {"by": "?", "why": f"crew can't read its hold file {tmp_path / 'hold'}", "at": None}

    def test_a_start_refused_by_a_hold_names_who_held_it_since_when_why_and_what_lifts_it(self):
        h = {"by": "fleet-releases", "why": "herdr 0.9.6", "at": "2026-10-21T03:00Z"}
        assert crew.held_said("deneb", h) == ("deneb is held by fleet-releases since 2026-10-21T03:00Z: herdr 0.9.6. "
                                              "crew starts no agent there until crew go deneb")


class TestQuiet:
    def test_a_host_is_quiet_once_nothing_of_crews_works_there(self):
        assert hold.busy_said([{"name": "crw-4-conductor", "status": "idle", "asking": False, "own": [], "owes": None, "unread": None}], 0) == []

    def test_what_still_works_is_said_each_its_own_way(self):
        facts = [{"name": "crw-4-conductor", "status": "working", "asking": False, "own": [], "owes": None, "unread": None},
                 {"name": "crw-4-ops", "status": "blocked", "asking": False, "own": [], "owes": None, "unread": None},
                 {"name": "swancloud-planner", "status": "idle", "asking": True, "own": [], "owes": None, "unread": None},
                 {"name": "swancloud-ops", "status": "idle", "asking": False, "own": ["wt submit main"], "owes": None, "unread": None},
                 {"name": "crw-4-unit-1", "status": "idle", "asking": False, "own": [], "owes": "code of a-unit", "unread": None},
                 {"name": "crw-4-unit-2", "status": "idle", "asking": False, "own": None, "owes": None, "unread": "herdr names no session for it"}]
        assert hold.busy_said(facts, 2) == [
            "crw-4-conductor is working", "crw-4-ops waits on a question to you in its pane",
            "swancloud-planner waits on a question to you in its pane",
            "swancloud-ops runs 1 background task of its own: wt submit main", "crw-4-unit-1's code of a-unit has not ended",
            "crew can't tell what crw-4-unit-2 is doing: herdr names no session for it", "2 of crew's tests are running"]

    @pytest.mark.parametrize("command, wait", [
        ("crew unit wait a-unit --timeout 3600000", True), ("crew chore wait c", True), ("crew card wait batch/3", True),
        ("crew fix crw-4 f --wait", True), ("cd /x && crew review swancloud --wait --timeout 60000", True),
        ("bash /x/plugin/bin/crew unit wait u", True), ("crew bolt submit b", False), ("wt submit main", False),
        ("sleep 600; echo wait", False), (None, False)])
    def test_only_crews_waits_are_background_work_a_restart_may_end(self, command, wait):
        # crew card wait is gone (teams.24), and one still running from before is still read as crew's.
        assert hold.crew_wait(command) is wait


class TestRenew:
    def test_a_due_agent_is_restarted_only_once_it_is_idle_with_nothing_of_its_own_running(self):
        assert hold.renew_ready("idle", False, None, []) == (True, None)
        assert hold.renew_ready("done", False, None, []) == (True, None)
        assert hold.renew_ready("working", False, None, []) == (False, "it is working")
        assert hold.renew_ready("idle", True, None, []) == (False, "it waits on a question to you in its pane")
        assert hold.renew_ready("blocked", False, None, []) == (False, "it waits on a question to you in its pane")
        assert hold.renew_ready("idle", False, None, ["wt submit main"]) == (False, "it runs background work of its own: wt submit main")
        assert hold.renew_ready(None, False, None, []) == (False, "it is not up")
        assert hold.renew_ready("idle", False, "no transcript", []) == (False, "crew can't tell what it is doing: no transcript")

    def test_an_agent_not_up_is_started_with_no_stop_only_when_an_earlier_restarts_keys_ended_it(self):
        # swancloud-operator and fwn-1-conductor exited within a minute of their restarts giving up on deneb, and their
        # panes stood as shells for nine hours (signal 2026-10-23-chuck-mac-studio-8d53f475/01).
        assert hold.renew_exited(False, None, "sid-1", "sid-1", False) == (True, None)

    def test_an_agent_no_restart_gave_up_on_is_not_up_and_left_to_crew_revive(self):
        assert hold.renew_exited(False, None, None, "sid-1", False) == (False, "it is not up")
        assert hold.renew_exited(False, None, "", "sid-1", False) == (False, "it is not up")

    def test_a_mark_of_another_session_is_stale_and_read_as_not_up(self):
        assert hold.renew_exited(False, None, "sid-0", "sid-1", False) == (False, "it is not up")
        assert hold.renew_exited(False, None, "sid-1", None, False) == (False, "it is not up")

    def test_a_pane_herdr_lists_an_agent_in_is_not_started_over(self):
        assert hold.renew_exited(True, None, "sid-1", "sid-1", False) == (False, "it is not up")

    def test_a_restarts_mark_names_the_session_its_exit_was_typed_into_and_a_stale_one_goes_as_it_is_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hold, "RENEW", tmp_path)
        mark = tmp_path / "swb-1-ops.exiting"
        assert hold.marked_exit("swb-1-ops", "sid-1") is None
        mark.write_text("sid-1\n")
        assert hold.marked_exit("swb-1-ops", "sid-1") == "sid-1" and mark.exists()
        assert hold.marked_exit("swb-1-ops", "sid-2") == "sid-1" and not mark.exists()
        assert hold.EXITING * 5 == 600

    def test_an_agent_taken_down_stays_down(self):
        assert hold.renew_exited(False, None, "sid-1", "sid-1", True) == (False, "it was taken down; it stays down")

    def test_a_pane_crew_cannot_read_starts_nothing_and_says_why(self):
        assert hold.renew_exited(None, "herdr lists no pane w1:p2, which crew keeps for swb-1-ops", "sid-1", "sid-1", False) == (
            False, "crew can't tell whether its pane holds it: herdr lists no pane w1:p2, which crew keeps for swb-1-ops")

    def test_a_restarted_agent_is_told_the_crew_it_started_on_the_one_it_runs_now_and_what_changed(self):
        said = hold.renew_notice("v0.12.1", "v0.13.0", ["feat(teams): a host is held", "fix(board): x"])
        assert said.startswith("crew restarted you on crew v0.13.0 (you started on v0.12.1), so your brief and crew's plugin are as they now stand. "
                               "What changed: feat(teams): a host is held; fix(board): x.")
        assert "start again any wait you still need" in said
        assert hold.renew_notice(None, None, []).startswith("crew restarted you on crew as it now is, so")

    def test_claude_codes_question_at_an_exit_with_background_work_is_read_from_the_panes_screen(self):
        assert crew.exit_asks(EXIT_SCREEN)
        assert not crew.exit_asks("❯ \n  ? for shortcuts")
        assert not crew.exit_asks(" Exiting worktree session\n ❯ 1. Keep worktree")
        assert not crew.exit_asks("") and not crew.exit_asks(None)

    def test_a_restart_ends_crews_waits_at_the_exits_question_and_any_other_stop_leaves_it_asked(self, tmp_path, monkeypatch):
        # swc-3's and swc-4's conductors, restarted at a give beside their bolts waiting to land, stopped at the question
        # on their landing-card waits and read as blocked (signal 2026-10-22-swancloud-dispatch-deneb-bddc208d/01).
        monkeypatch.setattr(crew, "nap", lambda seconds: None)
        for waits in (True, False):
            agents = crew.Agents(None, "team", "swc-4", "swancloud", "swancloud", tmp_path / str(waits), None, "/w", None)
            agents.herdr = Exiting()
            agents.ensure()
            agents.put("panes", "conductor", "w8:p1")
            why = agents.stop("conductor", waits=waits)
            enters = [a for a in agents.herdr.acts if a[:2] == ("agent", "send-keys")]
            if waits:
                assert why is None and agents.ended == ["conductor"]
                assert enters == [("agent", "send-keys", "w8:p1", "enter")]
            else:
                assert why == "swc-4-conductor did not exit (busy or waiting on the user); it was left running"
                assert enters == [] and agents.herdr.state == "blocked"

    def lingering(self, tmp_path, monkeypatch, reads):
        monkeypatch.setattr(crew, "nap", lambda seconds: None)
        agents = crew.Agents(None, "main", "swancloud", "swancloud", "swancloud", tmp_path, None, "/w", None)
        agents.herdr = Lingering(reads)
        agents.ensure()
        agents.put("panes", "operator", "w2:p3")
        return agents

    def test_an_agent_slow_to_exit_is_watched_after_its_stop_gives_up_and_ended_once_it_goes(self, tmp_path, monkeypatch):
        # swancloud-operator exited within a minute of its restart giving up on deneb (signal 2026-10-23-chuck-mac-studio-8d53f475/01).
        agents = self.lingering(tmp_path, monkeypatch, STOP_LOOKS + 3)
        assert agents.stop("operator", waits=True) == "swancloud-operator did not exit (busy or waiting on the user); it was left running"
        assert agents.ended == []
        typed = list(agents.herdr.acts)
        assert agents.exited("operator", 10) is True
        assert agents.ended == ["operator"] and agents.herdr.reads == STOP_LOOKS + 3
        assert agents.herdr.acts == typed

    def test_an_agent_that_never_exits_is_left_running_with_nothing_more_typed_to_it(self, tmp_path, monkeypatch):
        agents = self.lingering(tmp_path, monkeypatch, None)
        assert agents.stop("operator", waits=True)
        typed = list(agents.herdr.acts)
        assert agents.exited("operator", 10) is False
        assert agents.ended == [] and agents.herdr.state == "idle"
        assert agents.herdr.acts == typed


EXIT_SCREEN = """ Background work is running
 The following will stop when you exit:

 crew card wait land/the-bolt
 ❯ 1. Exit and stop tasks
   2. Move to background and exit
   3. Stay
"""


class Exiting:
    """herdr's side of a Claude Code session told /exit while a background task of its own runs: the question shows and
    the agent reads blocked, Enter on the question's first option ends it, and Ctrl+C leaves it asked."""

    def __init__(self):
        self.state, self.acts = "idle", []

    def status(self, pane, fresh=False):
        return self.state

    def run(self, *args):
        self.acts.append(args)
        out = ""
        if args[:2] == ("agent", "prompt") and args[3] == "/exit":
            self.state = "blocked"
        elif args[:2] == ("pane", "read"):
            out = EXIT_SCREEN if self.state == "blocked" else ""
        elif args[:2] == ("agent", "send-keys") and args[3:] == ("enter",) and self.state == "blocked":
            self.state = None
        return types.SimpleNamespace(returncode=0, stdout=out, stderr="")


# How many times a stop reads an agent afresh before it gives up: once a second for 30 seconds, and once after Ctrl+C.
STOP_LOOKS = 31


class Lingering:
    """herdr's side of a Claude Code session slow to exit: told /exit and Ctrl+C it stays up and idle, and herdr reads it
    gone only after `reads` fresh reads of it in all, never when reads is None."""

    def __init__(self, reads):
        self.state, self.acts, self.told, self.reads, self.gone_at = "idle", [], False, 0, reads

    def status(self, pane, fresh=False):
        if fresh and self.told:
            self.reads += 1
            if self.gone_at is not None and self.reads >= self.gone_at:
                self.state = None
        return self.state

    def run(self, *args):
        self.acts.append(args)
        if args[:2] == ("agent", "prompt") and args[3] == "/exit":
            self.told = True
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")


class TestHosts:
    def test_all_is_every_host_crew_runs_agents_on_and_one_named_must_be_a_host(self):
        fleet = {"teams": {"a": {"machine": "deneb"}, "b": {"machine": "box"}}, "partitions": {"l": {"machine": "mac-studio"}},
                 "hosts": {"deneb": {}, "box": {}, "mac-studio": {}, "macbook-pro": {}}}
        assert hold.hosts_named(fleet, "--all") == ["box", "deneb", "mac-studio"]
        assert hold.hosts_named(fleet, "macbook-pro") == ["macbook-pro"]
        with pytest.raises(crew.Refusal, match="nowhere is no host of the fleet's hosts file. hosts: box deneb mac-studio macbook-pro"):
            hold.hosts_named(fleet, "nowhere")


class TestTranscript:
    def test_each_background_tasks_command_is_read_from_the_call_that_started_it(self, tmp_path):
        rows = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tu1", "name": "Bash",
                                                                "input": {"command": "crew unit wait u", "run_in_background": True}}]}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "tu1"}]}, "toolUseResult": {"backgroundTaskId": "b1"}},
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tu2", "name": "Bash", "input": {"command": "wt submit main"}}]}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "tu2"}]}, "toolUseResult": {"backgroundTaskId": "b2"}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "gone"}]}, "toolUseResult": {"backgroundTaskId": "b3"}}]
        path = tmp_path / "s.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        assert transcript.started_commands(path) == {"b1": "crew unit wait u", "b2": "wt submit main", "b3": None}
        assert transcript.started_commands(tmp_path / "none.jsonl") is None


class TestBands:
    HERE = {"host": "deneb", "version": "v0.13.0", "held": None,
            "agents": {"wldn-planner": {"version": "v0.12.1", "due": True}, "wldn-dispatch-deneb": {"version": "v0.13.0", "due": False},
                       "wldn-ops": {"version": None, "due": True}}}

    def test_each_agent_says_the_crew_it_started_on_and_the_one_it_takes_at_its_next_stop(self):
        assert board.crew_said({"version": "v0.12.1", "due": False}, "v0.13.0") == "crew v0.12.1"
        assert board.crew_said({"version": "v0.12.1", "due": True}, "v0.13.0") == "crew v0.12.1 → v0.13.0 at its next stop"
        assert board.crew_said({"version": None, "due": True}, None) == "an older crew → crew as it now is at its next stop"

    def test_a_band_ends_its_first_line_with_its_crew_and_an_agent_with_no_view_has_its_crew_alone(self):
        from test_board import data
        v = board.agent_views(dict(data(), here=self.HERE))["views"]
        first = "".join(s for s, _ in v["wldn-planner"][0])
        assert first.endswith("  crew v0.12.1 → v0.13.0 at its next stop")
        assert v["wldn-dispatch-deneb"] == [[("crew v0.13.0", "dim")]]
        assert "".join(s for s, _ in v["wldn-ops"][0]).endswith("an older crew → v0.13.0 at its next stop")
        assert v["swb-1-conductor"] == board.agent_views(data())["views"]["swb-1-conductor"]

    def test_every_band_on_a_held_host_opens_with_the_hold(self):
        from test_board import data
        h = {"by": "fleet-releases", "why": "herdr 0.9.6", "at": "2026-10-21T03:00Z"}
        v = board.agent_views(dict(data(), here=dict(self.HERE, held=h)))["views"]
        line = [("deneb is held", "bold"), (" by fleet-releases since 2026-10-21T03:00Z: herdr 0.9.6. Start nothing new; crew go deneb lifts it", None)]
        assert all(lines[0] == line for lines in v.values())

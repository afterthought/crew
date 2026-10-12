"""Teams, the main level and their agents (teams.6, teams.7, teams.11, plan.15): crew.greet_waits for one look of a
greeting's wait, crew.standing_greeting for what an agent crew starts outside a team is greeted with, crew.dispatch_place
and crew.operator_session for where those run, crew.last_conversation for where a role resumes, and
plan.amended_said for what a conductor brought back is told. Starting, greeting, reviving and taking them down through
the command are the teams journey's (t-journey-teams, t-journey-main)."""
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

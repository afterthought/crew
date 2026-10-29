"""What a wait on a stage says, look by look, until the stage ends (teams.4): plan.look on one look's facts,
plan.ended_words for a stage whose end something else recorded, Owed.phrase for how a stage is named, and
plan.owed_of for the stage crew needs ends short, and how the agent of that stage is then ended in fact (plan.short_end,
plan.short_taken, crew.Agents.stop's over). That a wait records the end it sees, and that a stop-short reaches the
waiting wait or the conductor and ends its agent, are the journey's (t-journey-slots, t-journey-prompts)."""
import datetime
import types

import pytest

from facts import START, owed

import crew
import plan

WORKING, QUIET = (False, "is working", None), (False, "has been quiet for 3 minutes, under the limit of 15 minutes", None)
# What a wait read of a stuck agent that wrote nothing and committed nothing since its stage began (stuck_report).
SILENT = {"words": ("", None), "commits": [], "head": "abc1234", "where": "/home/.claude/projects/-w/s1.jsonl"}


def look(o=None, words=None, owed_=True, gone=False, got=None, missing="", quiet=WORKING, out_of_time=False, over=False, report=SILENT):
    return plan.look(o or owed("construct"), "swb-1-unit-1", 0, words, owed_, gone, got, missing, quiet, out_of_time, over, report)


class TestLook:
    def test_a_stop_short_handed_to_the_wait_is_its_answer(self):
        assert look(words="a decision on which table holds tenants") == (
            "short", "swb-1-unit-1 stopped short in construct on a. It needs: a decision on which table holds tenants")

    def test_a_stage_no_longer_owed_has_ended_by_another_hand(self):
        assert look(owed_=False) == ("ended", None)

    def test_a_deliverable_ends_it(self):
        assert look(got="unit/a@abc1234", missing="its change is committed at abc1234") == (
            "delivered", "swb-1-unit-1 delivered construct on a: its change is committed at abc1234")

    def test_an_agent_gone_before_it_delivered(self):
        assert look(gone=True, missing="nothing committed") == (
            "gone", "swb-1-unit-1 is no longer running: construct on a delivered nothing and said nothing it needs")

    def test_a_quiet_agent_past_the_limit_is_stuck_saying_what_it_lacks_and_what_it_said_and_did(self):
        assert look(o=owed("merge"), missing="bolt/b not yet holding it", quiet=(True, "quiet for 0 minutes", None)) == (
            "stuck", "swb-1-unit-1 is stuck in merge on a: quiet for 0 minutes, with bolt/b not yet holding it and nothing it "
                     "needs said through crew.\nSince it began, unit/a holds no commit; its head is abc1234.\n"
                     "It has written nothing since the stage began.")
        assert look(o=owed("settle"), missing="nothing committed since it began", quiet=(True, "quiet for 0 minutes", None))[1].startswith(
            "swb-1-unit-1 is stuck in settle on a: quiet for 0 minutes, with nothing committed since it began and nothing it "
            "needs said through crew.\n")

    def test_no_stage_is_called_stuck_before_what_it_said_and_did_is_read(self):
        with pytest.raises(plan.Refusal, match="with nothing read of what it said or did"):
            look(missing="nothing committed", quiet=(True, "quiet for 20 minutes", None), report=None)

    def test_a_verify_whose_agent_ended_its_turn_with_no_report_has_not_ended_and_is_never_called_stuck(self):
        # crw-4, 2026-10-23: a verify whose agent ended its turn with no report saved where crew reads it was called
        # stuck at the limit, and its unit's merge started (signal 2026-10-23-crw-4-conductor-8de4d1fb/01).
        missing = "no report verify-a-<YYYYMMDD-HHMM>.md saved in /home/.local/state/swb-1-team/reports since it began"
        for quiet in (QUIET, (True, "quiet for 15 minutes", None)):
            assert look(o=owed("verify"), missing=missing, quiet=quiet, over=True) == (
                "unended", f"swb-1-unit-1 ended its turn in verify on a with {missing}: the verify has not ended, since a "
                           "verify ends only at its report; nothing is recorded")

    def test_a_report_saved_ends_a_verify_however_its_agent_ended(self):
        assert look(o=owed("verify"), got="report/verify-a-20261012-1001.md", missing="the report is /r/verify-a-20261012-1001.md", over=True)[0] == "delivered"
        assert look(o=owed("verify"), got="report/verify-a-20261012-1001.md", missing="the report is /r/verify-a-20261012-1001.md", gone=True)[0] == "delivered"

    def test_stuck_names_what_crew_could_not_read_of_its_own_work_on_its_first_line(self):
        assert look(missing="nothing committed", quiet=(True, "quiet for 20 minutes", "no transcript for its session s1"))[1].split("\n")[0].endswith(
            "nothing it needs said through crew; crew could not read whether it waits on work of its own (no transcript for "
            "its session s1).")

    @pytest.mark.parametrize("quiet, doing", [(WORKING, "is working"), (QUIET, QUIET[1])])
    def test_out_of_time_it_is_still_running_and_nothing_is_recorded(self, quiet, doing):
        assert look(quiet=quiet, out_of_time=True) == (
            "running", f"construct on a is still running after the wait's 0 ms: swb-1-unit-1 {doing}; nothing is recorded yet")

    def test_else_it_looks_again(self):
        assert look(quiet=QUIET) == (None, QUIET[1])


def at(hhmm, day=START.date()):
    h, m = map(int, hhmm.split(":"))
    return datetime.datetime(day.year, day.month, day.day, h, m, tzinfo=datetime.timezone.utc)


def commit(sha, hhmm, subject, day="2026-10-12"):
    return sha, f"{day}T{hhmm}:00Z", subject


class TestStuckSaid:
    """What a stuck report carries (teams.4, record 0007 as amended 2026-10-23): what the agent last wrote and what its
    branch holds since the stage began, so nobody opens its pane to learn it. slc-1's fix round, 2026-10-23, committed
    its fix and went quiet; its wait said only "nothing it needs said", and the conductor asked the user (signal
    2026-10-23-slc-1-conductor-a4b46840/01)."""

    def said(self, words=("", None), commits=(), head="abc1234", unread=None, o=None, where="/home/.claude/projects/-w/s1.jsonl"):
        return plan.stuck_said(o or owed("code"), "swb-1-unit-1", "quiet for 20 minutes", "2 of 4 tasks ticked at its head",
                               unread, words, list(commits) if not isinstance(commits, str) else commits, "unit/a", head, START, where)

    def test_the_commits_since_it_began_and_its_last_words_with_their_time(self):
        words = ("I stopped: tests/py/test_tenants.py fails the same way after two attempts.\n"
                 "The second task is committed; the third needs the table's name decided.", at("11:06"))
        assert self.said(words, [commit("def5678", "11:02", "feat(a): the second task"), commit("abc1234", "10:51", "feat(a): the first task")]) == (
            "swb-1-unit-1 is stuck in code on a: quiet for 20 minutes, with 2 of 4 tasks ticked at its head and nothing it "
            "needs said through crew.\n"
            "Since it began, unit/a holds 2 commits, newest first:\n"
            "  def5678 11:02Z feat(a): the second task\n"
            "  abc1234 10:51Z feat(a): the first task\n"
            "Its last words, at 11:06Z:\n"
            "  > I stopped: tests/py/test_tenants.py fails the same way after two attempts.\n"
            "  > The second task is committed; the third needs the table's name decided.")

    def test_none_committed_since_it_began_names_its_head(self):
        assert "\nSince it began, unit/a holds no commit; its head is abc1234.\n" in self.said()
        assert "\nSince it began, unit/a holds no commit; crew could not read its head.\n" in self.said(head=None)

    def test_commits_from_before_it_began_are_left_out(self):
        got = self.said(commits=[commit("def5678", "10:05", "fix(a): the finding"), commit("abc1234", "09:59", "feat(a): from before")])
        assert "Since it began, unit/a holds 1 commit, newest first:\n  def5678 10:05Z fix(a): the finding\n" in got
        assert "abc1234" not in got

    def test_nothing_written_since_it_began(self):
        assert self.said().endswith("\nIt has written nothing since the stage began.")

    def test_what_crew_could_not_read_is_said_and_the_rest_still_reported(self):
        got = self.said(words="no transcript for its session s1", commits="git could not read unit/a in /kit/main")
        assert got.split("\n")[1:] == ["crew could not read what unit/a holds since it began: git could not read unit/a in /kit/main.",
                                        "crew could not read its last words: no transcript for its session s1."]
        assert self.said(words="herdr names no session for it").endswith("crew could not read its last words: herdr names no session for it.")

    def test_at_most_ten_commits_are_listed_and_the_rest_counted(self):
        got = self.said(commits=[commit(f"c{n:06d}", f"10:{50 - n:02d}", f"feat(a): {n}") for n in range(13)]).split("\n")
        assert got[1] == "Since it began, unit/a holds 13 commits, newest first:"
        assert got[2] == "  c000000 10:50Z feat(a): 0" and got[11] == "  c000009 10:41Z feat(a): 9" and got[12] == "  and 3 more"

    def test_a_long_message_is_cut_on_a_lines_end_with_how_much_more_and_where(self):
        lines = [f"{n:03d} " + "x" * 95 for n in range(30)]  # 30 lines of 99 characters, 100 with their line break
        text = "\n".join(lines)
        got = self.said(words=(text, at("11:06"))).split("\n")
        quoted = [l for l in got if l.startswith("  > ")]
        assert quoted == [f"  > {l}" for l in lines[:20]]
        assert got[-1] == f"  ({len(text) - 1999} more characters in /home/.claude/projects/-w/s1.jsonl)"

    def test_a_time_on_another_day_than_its_start_is_said_in_full(self):
        assert "Its last words, at 2026-10-13T00:10Z:" in self.said(words=("Still here.", at("00:10", datetime.date(2026, 10, 13))))
        assert "  d1 2026-10-13T00:05Z fix(a): late" in self.said(commits=[commit("d1", "00:05", "fix(a): late", day="2026-10-13")])

    def test_a_blank_line_of_its_words_is_quoted_bare(self):
        assert "  > First.\n  >\n  > Second." in self.said(words=("First.\n\nSecond.", at("11:06")))


class TestPhrase:
    @pytest.mark.parametrize("stage, name, obj, said", [
        ("code", "a", "unit/a", "code on a"),
        ("fix", "fix/tenant-environments/tidy", "fix/tenant-environments/tidy", "fix fix/tenant-environments/tidy"),
        ("merge", "fix/tenant-environments/tidy", "fix/tenant-environments/tidy", "merge of fix/tenant-environments/tidy")])
    def test_a_stage_is_named_by_what_it_is_of(self, stage, name, obj, said):
        assert owed(stage, name=name, slot="unit-1", obj=obj).phrase() == said


class TestEnded:
    def end(self, ended, on=("stage/a/code", "unit/a", "agent/swb-1-unit-1"), **f):
        return plan.ended_words("swb-1", "swb-1-unit-1", dict(Act="stage.end", Ended=ended, On=list(on), **f))

    def test_delivered_names_what_it_delivered_and_whether_it_was_seen_late(self):
        assert self.end("delivered", Delivered="unit/a@abc1234") == "code on a has ended: swb-1-unit-1 delivered unit/a@abc1234"
        assert self.end("delivered", Delivered="unit/a@abc1234", Observed="late") == (
            "code on a has ended: swb-1-unit-1 delivered unit/a@abc1234 (observed late)")

    def test_a_stop_short_was_told_to_the_conductor(self):
        assert self.end("short", on=("stage/b/settle", "unit/b", "agent/swb-1-unit-1")) == (
            "settle on b has ended: swb-1-unit-1 stopped short, and swb-1-conductor was told what it needs")

    def test_a_stage_crew_ended_first(self):
        assert self.end("stopped") == "code on a has ended: crew ended swb-1-unit-1 before it delivered"

    def test_a_fix(self):
        assert self.end("delivered", on=("fix/t/tidy", "agent/swb-1-unit-1"), Delivered="bolt/t@abc1234", Why="fix(tidy): merge ended") == (
            "merge of fix/t/tidy has ended: swb-1-unit-1 delivered bolt/t@abc1234")

    def test_with_no_end_recorded(self):
        assert plan.ended_words("swb-1", "swb-1-unit-1", None) == (
            "swb-1-unit-1 owes no stage's end, and none is recorded for it on this host")


class TestNeeds:
    T = {"name": "swb-1"}
    HELD = {"unit-2": ["unit-2", "unit", "b", "/kit/places/b"]}

    def test_the_slots_owed_stage_ends_short(self):
        o, = plan.owed_of(self.T, "unit-2", [["unit-2", "b", "construct", "20261012T100000Z-h-1-1", "unit/b"]], self.HELD)
        assert (o.agent, o.phrase()) == ("swb-1-unit-2", "construct on b")

    def test_ops_owes_no_proof(self):
        # A bolt's proof is its verification (record 0025): a line ops's proof left from before is owed nothing.
        with pytest.raises(plan.Refusal, match="swb-1-ops runs no stage crew is waiting on"):
            plan.owed_of(self.T, "ops", [["ops", "t", "proof", "20261012T100000Z-h-1-1", "bolt/t"]], {})

    @pytest.mark.parametrize("slot, lines", [
        ("unit-2", []),
        ("conductor", [["unit-2", "b", "construct", "x", "unit/b"]]),
        ("unit-2", [["unit-2", "c", "construct", "x", "unit/c"]])])
    def test_an_agent_that_owes_no_stage_is_refused(self, slot, lines):
        with pytest.raises(plan.Refusal, match=f"swb-1-{slot} runs no stage crew is waiting on"):
            plan.owed_of(self.T, slot, lines, self.HELD)


class TestShortEnd:
    """The agent of a stage that stopped short, ended in fact (record 0007): signal 2026-10-23-crw-5-conductor-ff91959f/01,
    crw-5-unit-4 going on working after its crew needs while its conductor's wait had read the stage ended."""

    @pytest.mark.parametrize("up, status, session, looked, how", [
        (False, None, None, 0, "gone"),
        (True, "idle", "s1", 0, "end"), (True, "done", "s1", 0, "end"), (True, "blocked", "s1", 0, "end"),
        (True, "working", "s1", 0, "wait"), (True, "working", "s1", plan.SHORT_GRACE - 1, "wait"),
        (True, "working", "s1", plan.SHORT_GRACE, "end"),
        (True, "idle", "s2", 0, "other"), (True, "working", "s2", plan.SHORT_GRACE, "other"),
        (True, None, "s1", 0, "wait"), (True, "idle", None, 0, "wait"), (True, "idle", None, plan.SHORT_GRACE, "unread")])
    def test_its_agent_is_ended_once_its_turn_ends_or_its_grace_is_spent_and_only_in_the_session_that_said_it(
            self, up, status, session, looked, how):
        assert plan.short_end("s1", up, status, session, looked) == how

    def test_what_herdr_gives_of_an_agent_is_read_guarded(self):
        assert plan.agent_facts(None) == (False, None, None)
        assert plan.agent_facts({"agent_status": "working", "agent_session": {"value": "s1"}}) == (True, "working", "s1")
        assert plan.agent_facts({"agent_status": 3, "agent_session": "s1"}) == (True, None, None)
        assert plan.agent_facts({"agent_session": {"value": ""}}) == (True, None, None)

    def test_each_end_is_said(self):
        assert plan.short_said("swb-1-unit-2", "end") == "swb-1-unit-2 is ended: its stage stopped short"
        assert plan.short_said("swb-1-unit-2", "other") == (
            "swb-1-unit-2 runs another session than the one that stopped short: crew leaves it be")
        assert plan.short_said("swb-1-unit-2", "unread") == "crew could not read which session swb-1-unit-2 runs, so it ends none"

    def team(self, tmp_path, monkeypatch, info, stopped=None):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setattr(crew, "agent_get", lambda fleet, name, fresh=True: info)
        stops = []

        def stop(slot, ending=None, waits=False, over=False):
            stops.append((slot, over))
            return stopped
        return types.SimpleNamespace(t={"name": "swb-1"}, agent_of=lambda s: f"swb-1-{s}", stop=stop), stops

    def mark(self, t, session):
        f = plan.short_path(t, "unit-2")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"20261023T014000Z-deneb-1-1\n{session}\n")
        return f

    def test_the_next_start_ends_the_working_agent_of_a_stage_that_stopped_short_with_no_force(self, tmp_path, monkeypatch):
        team, stops = self.team(tmp_path, monkeypatch, {"agent_status": "working", "agent_session": {"value": "s1"}})
        f = self.mark(team.t, "s1")
        assert plan.short_taken(None, team, "unit-2") is None
        assert stops == [("unit-2", True)] and not f.exists()

    def test_the_next_start_leaves_another_session_be_and_takes_the_mark(self, tmp_path, monkeypatch):
        team, stops = self.team(tmp_path, monkeypatch, {"agent_status": "working", "agent_session": {"value": "s2"}})
        f = self.mark(team.t, "s1")
        assert plan.short_taken(None, team, "unit-2") is None
        assert stops == [] and not f.exists()

    def test_with_no_mark_the_next_start_ends_nothing_of_its_own(self, tmp_path, monkeypatch):
        team, stops = self.team(tmp_path, monkeypatch, {"agent_status": "working", "agent_session": {"value": "s1"}})
        assert plan.short_taken(None, team, "unit-2") is None and stops == []

    def test_an_agent_that_did_not_exit_keeps_its_mark_and_refuses_the_start(self, tmp_path, monkeypatch):
        said = "swb-1-unit-2 did not exit (busy or waiting on the user); it was left running"
        team, stops = self.team(tmp_path, monkeypatch, {"agent_status": "idle", "agent_session": {"value": "s1"}}, stopped=said)
        f = self.mark(team.t, "s1")
        assert plan.short_taken(None, team, "unit-2") == said and f.exists()

    def test_a_stage_that_is_over_ends_its_working_agent_without_force_and_answers_its_exits_question(self, tmp_path, monkeypatch):
        monkeypatch.setattr(crew, "nap", lambda seconds: None)
        for over in (True, False):
            agents = crew.Agents(None, "team", "swb-1", "wldn", "wldn-1", tmp_path / str(over), None, "/w", None)
            agents.herdr = Busy()
            agents.ensure()
            agents.put("panes", "unit-2", "w2:p2")
            why = agents.stop("unit-2", over=over)
            if over:
                assert why is None and agents.ended == ["unit-2"]
                assert ("agent", "send-keys", "w2:p2", "enter") in agents.herdr.acts
            else:
                assert why == crew.working_said("swb-1-unit-2") and agents.herdr.acts == []


class Busy:
    """herdr's side of a Claude Code session working after its stage stopped short, a background task of its own
    running: told /exit it asks whether to stop the task and reads blocked, and Enter on the first option ends it."""

    def __init__(self):
        self.state, self.acts = "working", []

    def status(self, pane, fresh=False):
        return self.state

    def run(self, *args):
        self.acts.append(args)
        out = ""
        if args[:2] == ("agent", "prompt") and args[3] == "/exit":
            self.state = "blocked"
        elif args[:2] == ("pane", "read"):
            out = " Background work is running\n ❯ 1. Exit and stop tasks\n" if self.state == "blocked" else ""
        elif args[:2] == ("agent", "send-keys") and args[3:] == ("enter",) and self.state == "blocked":
            self.state = None
        return types.SimpleNamespace(returncode=0, stdout=out, stderr="")

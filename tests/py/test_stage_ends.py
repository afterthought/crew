"""A stage ends at its deliverable, never at a quiet pane (teams.4, teams.14): plan.delivered on the facts
deliverable_facts reads; when a quiet agent is stuck, plan.quiet_verdict; and when a verify's agent has ended its turn
with nothing running, plan.ended_turn (record 0007). The wait's loop and the records it writes are t-stage-ends'."""
import datetime

import pytest

from facts import AFTER, BEFORE, owed, plan_of, saved

import plan

MIN = datetime.timedelta(minutes=1)


def test_a_start_crew_cannot_read_delivers_nothing():
    assert plan.delivered(owed("construct", start=None), {}) == (None, "no start crew can read in its entry unreadable")


class TestConstruct:
    def test_a_commit_since_it_began_with_planning_complete_delivers_the_change(self):
        assert plan.delivered(owed("construct"), {"head": "abc1234", "at": AFTER, "planned": True}) == (
            "unit/a@abc1234", "its change is committed at abc1234")

    def test_planning_not_complete_delivers_nothing(self):
        assert plan.delivered(owed("construct"), {"head": "abc1234", "at": AFTER, "planned": False}) == (None, "its planning not complete")

    def test_a_commit_from_before_it_began_is_not_its(self):
        assert plan.delivered(owed("construct"), {"head": "abc1234", "at": BEFORE}) == (None, "nothing committed")

    def test_no_branch_delivers_nothing(self):
        assert plan.delivered(owed("construct"), {"head": "", "at": None}) == (None, "nothing committed")


class TestCode:
    def test_every_task_ticked_at_a_commit_since_it_began_delivers(self):
        assert plan.delivered(owed("code"), {"head": "abc1234", "at": AFTER, "ticks": (2, 2)}) == (
            "unit/a@abc1234", "every task is ticked (2/2) at abc1234")

    def test_a_task_open_has_not_ended(self):
        assert plan.delivered(owed("code"), {"head": "abc1234", "at": AFTER, "ticks": (1, 2)}) == (None, "1 of 2 tasks ticked at its head")

    def test_code_run_again_on_a_ticked_change_ends_only_at_a_commit_since_it_began(self):
        assert plan.delivered(owed("code"), {"head": "abc1234", "at": BEFORE, "ticks": (2, 2)}) == (None, "no commit since it began")

    def test_with_no_task_list_at_its_head_a_commit_since_it_began_delivers(self):
        assert plan.delivered(owed("code"), {"head": "abc1234", "at": AFTER, "ticks": (0, 0)}) == (
            "unit/a@abc1234", "its branch is at abc1234, with no task list at its head")

    def test_with_no_task_list_and_nothing_committed_since_it_began_it_lacks_a_commit_never_tasks(self):
        assert plan.delivered(owed("code"), {"head": "abc1234", "at": BEFORE, "ticks": (0, 0)}) == (None, "no commit since it began")
        assert plan.delivered(owed("code"), {"head": "", "at": None, "ticks": (0, 0)}) == (None, "no commit since it began")


    def test_a_fix_round_on_a_change_archived_at_its_head_delivers_at_its_commit(self, monkeypatch):
        # slc-1, 2026-10-23: a unit's fix round committed its fix on a branch whose change was archived at its head, and
        # its wait, owing it every task ticked where no task list stood, called it stuck after fifteen minutes (signal
        # 2026-10-23-slc-1-conductor-a4b46840/01). The head is read once, git show finds no tasks.md at it,
        # ticks reads 0 of 0, and the commit since it began delivers it (teams.4).
        t = {"name": "slc-1", "kit": {"main": "/kit/main", "dir": "/kit"}}

        def run(argv, cwd):
            if argv[:2] == ["git", "rev-parse"]:
                return "def5678\n"
            if argv[:3] == ["git", "log", "-1"]:
                return AFTER.isoformat() + "\n"
            if argv[:2] == ["git", "show"] and argv[2] == "def5678:openspec/changes/a/tasks.md":
                return None  # git exits 128: the path does not exist at that commit
            raise AssertionError(f"an unexpected read: {argv}")
        monkeypatch.setattr(plan.gather, "run", run)
        o = owed("code", team="slc-1")
        f = plan.deliverable_facts({}, t, o)
        assert f == {"head": "def5678", "at": AFTER, "ticks": (0, 0)}
        assert plan.delivered(o, f) == ("unit/a@def5678", "its branch is at def5678, with no task list at its head")


class TestVerify:
    def test_a_report_saved_since_it_began_ends_it(self):
        report = saved("verify-a-20261012-1001.md")
        assert plan.delivered(owed("verify"), {"saved": report}) == ("report/verify-a-20261012-1001.md", f"the report is {report}")

    def test_no_report_saved_since_it_began_is_named_with_the_folder_crew_reads(self):
        assert plan.delivered(owed("verify"), {"saved": None, "folder": "/home/.local/state/swb-1-team/reports"}) == (
            None, "no report verify-a-<YYYYMMDD-HHMM>.md saved in /home/.local/state/swb-1-team/reports since it began")
        assert plan.delivered(owed("verify"), {"saved": None}) == (None, "no report saved")


class TestEndedTurn:
    """plan.ended_turn: whether a verify's agent has ended its turn since the stage began with nothing of its own still
    running, so that a verify with no report is said not to have ended then, never stuck by its clock (record 0007)."""

    @pytest.mark.parametrize("status", ["idle", "done"])
    def test_a_verify_agent_idle_or_done_its_turn_over_since_it_began_and_nothing_running_has_ended_its_turn(self, status):
        assert plan.ended_turn(owed("verify"), status, [], AFTER)

    @pytest.mark.parametrize("stage, status, pending, over", [
        ("code", "idle", [], AFTER),  # only a verify: another stage's quiet agent goes by the clock
        ("verify", "blocked", [], AFTER),  # a question in its pane
        ("verify", "idle", ["b8y1gomwj"], AFTER),  # suites it started in the background still run
        ("verify", "idle", None, AFTER),  # crew could not read whether it waits on work of its own
        ("verify", "idle", [], None),  # its turn goes on, or crew can't read it
        ("verify", "idle", [], BEFORE)])  # its turn ended before the stage began
    def test_otherwise_it_has_not(self, stage, status, pending, over):
        assert not plan.ended_turn(owed(stage), status, pending, over)

    def test_a_start_crew_cannot_read_is_no_turn_ended_since(self):
        assert not plan.ended_turn(owed("verify", start=None), "idle", [], AFTER)


class TestMerge:
    def test_a_units_merge_ends_once_the_bolt_holds_its_change_archived(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "holds": True, "archived": True, "bolt_head": "1234567"}) == (
            "bolt/b@1234567", "bolt/b holds it at 1234567")

    def test_a_change_merged_open_is_not_its_deliverable_since_the_merge_archives_it_first(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "holds": True, "archived": False, "bolt_head": "1234567"}) == (
            None, "bolt/b holds its change open: its merge did not archive it first")

    def test_a_bolt_not_yet_holding_it(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "holds": False, "archived": False, "bolt_head": "1234567"}) == (
            None, "bolt/b not yet holding it")


def test_a_commit_between_the_reads_never_pairs_its_ticks_or_time_with_the_earlier_head(monkeypatch):
    # Under load the unit's agent commits its last tick between crew's reads (t-journey-units, 2026-10-12: "every task
    # is ticked (2/2) at 3138801" while the branch was at 7402611). The head is read once; its time and ticks are read
    # at that commit, so the branch moving after the first read changes nothing deliverable_facts returns.
    t = {"name": "swb-1", "kit": {"main": "/kit/main", "dir": "/kit"}}
    moved = []
    tasks = {"abc1234": "- [x] 1.1\n- [ ] 1.2\n", "def5678": "- [x] 1.1\n- [x] 1.2\n"}
    times = {"abc1234": "2026-10-12T10:01:00+00:00", "def5678": "2026-10-12T10:02:00+00:00"}

    def run(argv, cwd):
        tip = "def5678" if moved else "abc1234"
        if argv[:2] == ["git", "rev-parse"]:
            moved.append(True)  # the agent's next tick lands just after crew read the head
            return tip + "\n"
        ref = argv[-1].split(":")[0]
        rev = tip if ref.startswith("refs/heads/") or ref.startswith("unit/") else ref
        if argv[:3] == ["git", "log", "-1"]:
            return times[rev] + "\n"
        if argv[:2] == ["git", "show"]:
            return tasks[rev]
        raise AssertionError(f"an unexpected read: {argv}")
    monkeypatch.setattr(plan.gather, "run", run)
    o = owed("code")
    f = plan.deliverable_facts({}, t, o)
    assert f == {"head": "abc1234", "at": AFTER, "ticks": (1, 2)}
    assert plan.delivered(o, f) == (None, "1 of 2 tasks ticked at its head")


class TestSettle:
    def test_a_commit_since_it_began_is_ready_to_merge(self):
        assert plan.delivered(owed("settle"), {"head": "abc1234", "at": AFTER}) == (
            "unit/a@abc1234", "its branch is at abc1234, ready to merge")

    def test_nothing_since_it_began(self):
        assert plan.delivered(owed("settle"), {"head": "abc1234", "at": BEFORE}) == (None, "nothing committed since it began")


class TestMerge:
    def test_the_bolt_holding_the_change_ends_a_units_merge(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "holds": True, "bolt_head": "def5678"}) == (
            "bolt/b@def5678", "bolt/b holds it at def5678")

    def test_a_bolt_not_yet_holding_it(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "holds": False, "bolt_head": "def5678"}) == (None, "bolt/b not yet holding it")

    def test_no_bolt_crew_can_read(self):
        assert plan.delivered(owed("merge"), {"bolt": None}) == (None, "no bolt crew can read for it")


class TestFix:
    FIX = dict(name="fix/b/footer", obj="fix/b/footer")

    def test_a_commit_since_it_began_ends_a_fix(self):
        assert plan.delivered(owed("fix", **self.FIX), {"head": "abc1234", "at": AFTER}) == ("fix/b/footer@abc1234", "its branch is at abc1234")

    def test_nothing_since_it_began(self):
        assert plan.delivered(owed("fix", **self.FIX), {"head": "abc1234", "at": BEFORE}) == (None, "nothing committed since it began")

    def test_the_bolt_holding_its_commits_ends_its_merge(self):
        assert plan.delivered(owed("merge", **self.FIX), {"bolt": "b", "holds": True, "bolt_head": "def5678"}) == (
            "bolt/b@def5678", "bolt/b holds it at def5678")


class TestStuck:
    NOW = AFTER + 30 * MIN

    def verdict(self, stuck=15 * MIN, pending=(), last=None, unread=None, seen_quiet=None, seen_working=None):
        return plan.quiet_verdict(self.NOW, stuck, list(pending), last, unread, seen_quiet or self.NOW, seen_working)

    def test_an_agent_waiting_on_background_tasks_of_its_own_is_never_stuck(self):
        assert self.verdict(stuck=0 * MIN, pending=["b8y1gomwj"]) == (False, "is waiting on 1 background task of its own")

    def test_its_clock_runs_from_its_transcripts_last_record(self):
        assert self.verdict(stuck=MIN, last=AFTER) == (True, "quiet for 30 minutes")

    def test_under_the_limit_it_is_not_stuck(self):
        assert self.verdict(last=self.NOW - 5 * MIN) == (False, "has been quiet for 5 minutes, under the limit of 15 minutes")

    def test_with_no_transcript_its_clock_runs_from_when_the_wait_saw_it_quiet(self):
        assert self.verdict(stuck=0 * MIN, unread="no transcript for its session s", last=AFTER) == (True, "quiet for 0 minutes")

    def test_its_clock_never_starts_before_the_wait_last_saw_it_working(self):
        assert self.verdict(last=AFTER, seen_working=self.NOW - 2 * MIN) == (False, "has been quiet for 2 minutes, under the limit of 15 minutes")


class TestSavedSince:
    """plan.newest_saved, which reads a verify's report or a proof by the file's time: one saved before the stage
    began is not its."""

    def test_only_a_file_saved_since_the_start_is_the_stages(self, tmp_path, monkeypatch):
        import os
        from facts import START
        monkeypatch.setattr(plan, "team_state", lambda t: tmp_path)
        (tmp_path / "reports").mkdir()
        old = tmp_path / "reports" / "verify-a-20260101-0000.md"
        old.write_text("an old report")
        os.utime(old, (START.timestamp() - 3600,) * 2)
        assert plan.newest_saved({}, gather_report(), "a", START) is None
        new = tmp_path / "reports" / "verify-a-20261012-1001.md"
        new.write_text("the report")
        os.utime(new, (START.timestamp() + 60,) * 2)
        assert plan.newest_saved({}, gather_report(), "a", START) == new


def gather_report():
    import gather
    return gather.REPORT


class TestMergeLookFetches:
    """bolt-plan "A wait on a merge sees it at once" (plan.19, design Decision 3): each look a wait takes at a merge
    fetches the kit's GitHub before it reads the bolt, and reads the bolt where it lives; a fetch that fails delivers
    nothing and says why, reading nothing from the host's copy."""
    T = {"name": "swb-1", "label": "wldn", "kit": {"main": "/kit/main", "dir": "/kit"}}
    POLICY = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'

    def look(self, monkeypatch, fetch=(0, "", "")):
        calls = []

        def run(argv, cwd):
            calls.append(argv)
            if argv[:3] == ["git", "remote", "get-url"]:
                return "https://github.com/o/k.git\n"
            if argv[:2] == ["git", "rev-parse"] and argv[-1].endswith("^{commit}"):
                return "d" * 40 + "\n"
            if argv[:2] == ["git", "show"] and argv[-1] == "refs/remotes/origin/bolt/b:.config/sluice.toml":
                return self.POLICY
            if argv[:2] == ["git", "log"] and argv[-2] == "refs/remotes/origin/bolt/b":
                return "c\n"
            if argv[:3] == ["git", "rev-parse", "--short"] and argv[-1] == "refs/remotes/origin/bolt/b":
                return "def5678\n"
            raise AssertionError(f"an unexpected read: {argv}")

        def ran(argv, cwd):
            calls.append(argv)
            return fetch
        monkeypatch.setattr(plan.gather, "run", run)
        monkeypatch.setattr(plan.gather, "ran", ran)
        monkeypatch.setattr(plan, "plans", lambda fleet, labels, errors=None: [("wldn", "o/state", "tip", plan_of({"b": "swb-1"}, {"c": "b"}))])
        o = owed("merge", name="c", obj="chore/c")
        return calls, o, plan.deliverable_facts({}, self.T, o)

    def test_a_merge_look_fetches_before_it_reads_the_bolt_and_reads_it_on_github(self, monkeypatch):
        calls, o, f = self.look(monkeypatch)
        fetched = calls.index(["git", "fetch", "-q", "origin"])
        assert not any("bolt/b" in " ".join(c) for c in calls[:fetched])
        assert not any("refs/heads/bolt/b" in a for c in calls for a in c if not a.endswith("^{commit}"))
        assert plan.delivered(o, f) == ("bolt/b@def5678", "bolt/b holds it at def5678")

    def test_a_fetch_that_fails_delivers_nothing_and_says_why(self, monkeypatch):
        calls, o, f = self.look(monkeypatch, fetch=(128, "", "fatal: unable to access 'https://github.com/o/k.git/': Could not resolve host\n"))
        assert calls[-1] == ["git", "fetch", "-q", "origin"]
        assert plan.delivered(o, f) == (None, "can't fetch bolt/b from GitHub: fatal: unable to access 'https://github.com/o/k.git/': "
                                              "Could not resolve host")

    def test_a_bolt_crew_cant_read_delivers_nothing_and_says_why(self):
        assert plan.delivered(owed("merge"), {"bolt": "b", "unread": "this host has neither bolt/b nor origin/bolt/b"}) == (
            None, "can't read bolt/b: this host has neither bolt/b nor origin/bolt/b")

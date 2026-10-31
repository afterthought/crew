"""crew's side of the runner's interface (the change teams-cross-to-flume-as-their-bolts-land, Decision 4): the requests
crew appends to requests.rec on the flywheel's branch, numbered once and never changed or removed, each checked by
crew's own rules (runner.request_refusal, runner.append_refusal) as well as recfix, and written by a plan write's change
function (plan.request). recfix's side and the commit are the contract tier's (tests/contract/test_recfix.py)."""
import pytest

from crew import Refusal
from facts import FactsWrite
import plan
import runner

AT, BY = "2026-10-31T12:00:00Z", "madswan-dispatch-deneb"
LAUNCH = dict(Repo="afterthought/crew", Kind="change", Base="bolt/b", Stream="madswan", Priority=2, Intent="madswan/b",
              Recipient="madswan/planner", Brief="Build it.")


def rec(n, act, work="unit/a", host="deneb", **given):
    """A request as plan.request makes it, a launch carrying every field a launch needs unless given otherwise."""
    if act == "launch":
        given = dict(dict(LAUNCH, Name=work.split("/")[-1]), **given)
    return plan.Rec("Request", runner.request_fields(n, act, host, work, given, AT, BY))


def held(*recs):
    """requests.rec holding these requests, as the plan's records."""
    return plan.Plan(runner.REQUESTS + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)).recs("Request")


class TestRequests:
    """A request is numbered once, carries what its act needs and names what it acts on (Decision 4)."""

    def test_a_requests_fields_are_written_in_the_files_order_and_a_flag_as_yes(self):
        r = rec(3, "retry", Words="Read the plan again.", Submission=True, Of=1, Stage=None)
        assert r.fields == [("Request", "3"), ("Act", "retry"), ("Host", "deneb"), ("Work", "unit/a"), ("Of", "1"),
                            ("Submission", "yes"), ("Words", "Read the plan again."), ("Date", AT), ("By", BY)]
        assert rec(2, "launch", "unit/b", After=[1, "4"]).all("After") == ["1", "4"]

    def test_never_renumbered(self):
        """requests.rec holds requests 1 to 7 and a drop is written: it is request 8."""
        seven = held(rec(1, "launch"), *[rec(n, "priority", Of=1, Priority=n) for n in range(2, 8)])
        assert runner.next_request(seven) == 8
        assert runner.request_refusal(seven, rec(8, "drop", Of=1)) is None
        assert runner.request_refusal(seven, rec(7, "drop", Of=1)) == (
            "request 7 is not the next in requests.rec: it holds requests 1 to 7, so the next is 8")
        assert runner.request_refusal([], rec(2, "launch")) == "request 2 is not the next in requests.rec: it holds none, so the next is 1"

    def test_a_launch_with_no_stream_is_refused(self):
        why = runner.request_refusal([], rec(1, "launch", Stream=None))
        assert why.startswith("launch 1 for unit/a names no Stream: a launch carries Request, Act, Host, Work, Date, By, Repo, Kind, "
                              "Name, Base, Stream")

    def test_a_retry_of_nothing_is_refused_naming_the_request(self):
        """A retry would name request 9, which is no launch."""
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "retry", Of=9)) == (
            "retry 2 for unit/a names request 9, which is no launch: requests.rec does not hold it")
        have = held(rec(1, "launch"), rec(2, "drop", Of=1))
        assert runner.request_refusal(have, rec(3, "retry", Of=2)) == "retry 3 for unit/a names request 2, which is no launch"

    def test_a_retry_drop_or_priority_names_a_launch_of_its_own_work_on_its_own_host(self):
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "drop", "unit/b", Of=1)) == (
            "drop 2 for unit/b on deneb names launch 1, which is unit/a's on deneb")
        assert runner.request_refusal(have, rec(2, "priority", host="alpha", Of=1, Priority=3)) == (
            "priority 2 for unit/a on alpha names launch 1, which is unit/a's on deneb")
        assert runner.request_refusal(have, rec(2, "priority", Of=1)).startswith("priority 2 for unit/a names no Priority")

    def test_a_request_carries_nothing_its_act_does_not_take(self):
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "drop", Of=1, Words="Gone.", Stream="madswan")) == (
            "drop 2 for unit/a carries Stream, Words, which a drop does not take")
        assert runner.request_refusal([], rec(1, "reorder")) == "request 1 is a reorder, and a request is a launch, a retry, a drop or a priority"

    def test_the_work_is_named_as_crew_names_it(self):
        for work in ("unit/a", "chore/bump", "fix/b/tidy", "fix/main/crew/red"):
            assert runner.WORK.match(work)
        assert runner.request_refusal([], rec(1, "launch", "unit/A")) == (
            "launch 1 serves unit/A, and a request serves unit/<unit>, chore/<chore>, fix/<bolt>/<name> or fix/main/<kit>/<name>")
        assert runner.request_refusal([], rec(1, "launch", "bolt/b")).startswith("launch 1 serves bolt/b")

    def test_an_after_names_launches_of_the_same_bolt_written_before_it(self):
        have = held(rec(1, "launch"), rec(2, "launch", "unit/c", Base="bolt/other"), rec(3, "priority", Of=1, Priority=1))
        assert runner.request_refusal(have, rec(4, "launch", "unit/b", After=[1])) is None
        assert runner.request_refusal(have, rec(4, "launch", "unit/b", After=[2])) == (
            "launch 4 of unit/b on bolt/b comes after launch 2, which is on bolt/other: an After names work of the same bolt")
        assert runner.request_refusal(have, rec(4, "launch", "unit/b", After=[3])) == "launch 4 of unit/b comes after request 3, which is no launch"
        assert runner.request_refusal(have, rec(4, "launch", "unit/b", After=[5])) == "launch 4 of unit/b comes after request 5, which is no launch"

    def test_a_fix_of_main_holds_its_submission(self):
        fix = dict(Base="main", Intent="madswan/main/crew", Recipient="madswan/ops", Name="main--red")
        assert runner.request_refusal([], rec(1, "launch", "fix/main/crew/red", Hold="submission", **fix)) is None
        assert runner.request_refusal([], rec(1, "launch", "fix/main/crew/red", **fix)) == (
            "launch 1 of fix/main/crew/red is a fix of main, which is launched with its submission held (Hold: submission) until the "
            "user's send (state.3)")

    def test_a_retry_starts_a_stage_or_submits_again(self):
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "retry", Of=1, Stage="code", Words="Yes.")) is None
        assert runner.request_refusal(have, rec(2, "retry", Of=1, Submission=True)) is None
        assert runner.request_refusal(have, rec(2, "retry", Of=1, Stage="code", Submission=True)) == (
            "retry 2 of unit/a names stage code and the submission: a retry starts a stage again or submits again")


class TestAppended:
    """A request is never changed or removed: a write only appends (Decision 4)."""

    def test_a_write_that_appends_passes_and_one_that_changes_or_removes_a_request_is_refused(self):
        one, two = rec(1, "launch"), rec(2, "drop", Of=1)
        assert runner.append_refusal([one.fields], [one.fields, two.fields]) is None
        changed = rec(1, "launch", Stream="other")
        assert runner.append_refusal([one.fields, two.fields], [changed.fields, two.fields]).startswith(
            "request 1 would be changed in requests.rec, and a request is never changed or removed")
        assert runner.append_refusal([one.fields, two.fields], [one.fields]).startswith("request 2 would be removed from requests.rec")
        assert runner.append_refusal([one.fields, two.fields], [two.fields, one.fields]).startswith("request 1 would be changed")


class TestPlanRequest:
    """plan.request appends a request from inside a write's change function, so it reaches the branch in the write's own
    commit (state.1): numbered the next, by the writer, refused whole by crew's rules."""

    def test_two_requests_of_one_write_are_numbered_in_turn_after_those_the_branch_holds(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        w = FactsWrite("%rec: Bolt\n%key: Bolt\n")
        assert plan.request(w, "launch", "deneb", "unit/a", Name="a", **LAUNCH) == 1
        assert plan.request(w, "launch", "deneb", "unit/b", Name="b", After=[1], **LAUNCH) == 2
        rs = plan.Plan(w.files["requests.rec"]).recs("Request")
        assert [(r.get("Request"), r.get("Work"), r.all("After"), r.get("By")) for r in rs] == [
            ("1", "unit/a", [], BY), ("2", "unit/b", ["1"], BY)]
        assert w.files["requests.rec"].startswith(runner.REQUESTS)
        w2 = FactsWrite("%rec: Bolt\n%key: Bolt\n", files={"requests.rec": w.files["requests.rec"]})
        assert plan.request(w2, "drop", "deneb", "unit/b", Of=2) == 3

    def test_a_refused_request_leaves_the_writes_files_as_they_were(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        w = FactsWrite("%rec: Bolt\n%key: Bolt\n")
        plan.request(w, "launch", "deneb", "unit/a", Name="a", **LAUNCH)
        text = w.files["requests.rec"]
        with pytest.raises(Refusal, match="^retry 2 for unit/a names request 9, which is no launch"):
            plan.request(w, "retry", "deneb", "unit/a", Of=9, Words="Go on.")
        assert w.files["requests.rec"] == text

    def test_a_branch_whose_file_was_made_before_a_field_was_allowed_takes_crews_descriptor(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        old = runner.REQUESTS.replace(" Hold After Brief", " After Brief") + "\n" + "\n".join(rec(1, "launch").lines()) + "\n"
        w = FactsWrite("%rec: Bolt\n%key: Bolt\n", files={"requests.rec": old})
        plan.request(w, "drop", "deneb", "unit/a", Of=1)
        assert w.files["requests.rec"].startswith(runner.REQUESTS)

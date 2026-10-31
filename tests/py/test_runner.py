"""crew's side of the runner's interface (the change teams-cross-to-flume-as-their-bolts-land, Decision 4): the requests
crew appends to requests.rec on the flywheel's branch, numbered once and never changed or removed, each checked by
crew's own rules (runner.request_refusal, runner.append_refusal) as well as recfix, and written by a plan write's change
function (plan.request); each host's runner as crew reads it from its own branch (runner.host_read); and a crossed
piece's stage from its launch, the runner's answer and Flume's status of its place (runner.stage_of, Decision 8), on
flume 0.3.6's own status (tests/py/flume-0.3.6/). recfix's side, the commit and the fetch are the contract tier's
(tests/contract/test_recfix.py, tests/contract/test_git.py)."""
import json
import pathlib

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


TIP = "5e1f0c2a" + "0" * 32
STATUS = {"status": {"places": [{"place": "/crew/places/change--a", "phase": "live"}], "host": {}}}


def branch(host="deneb", runner_rec=None, answers="", places=""):
    """A runner's branch's files parsed as plan.runners parses them, each given as the records after its descriptor."""
    run = runner.RUNNER + (f"\nHost: {host}\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n" if runner_rec is None else runner_rec)
    return {"runner.rec": plan.Plan(run), "answers.rec": plan.Plan(runner.ANSWERS + answers), "places.rec": plan.Plan(runner.PLACES + places)}


def answer(n, outcome, place=None, words=None):
    return f"\nRequest: {n}\nOutcome: {outcome}\n" + (f"Place: {place}\n" if place else "") + (f"Words: {words}\n" if words else "") + "At: 2026-10-31T12:01:00Z\n"


def placed(n, status, place="/crew/places/change--a"):
    return f"\nRequest: {n}\nPlace: {place}\nAt: 2026-10-31T12:02:00Z\nStatus: {status if isinstance(status, str) else json.dumps(status)}\n"


class TestHostRead:
    """A host's runner is read from <label>/runner/<host> at its tip; one that can't be read hides that host's work
    alone, named (read.1, read.3)."""

    def test_a_runners_answers_and_places_are_read_by_their_requests_numbers(self):
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", "/crew/places/change--a") + answer(4, "held"),
                                                            places=placed(3, STATUS)), {})
        assert (r["host"], r["branch"], r["tip"], r["why"]) == ("deneb", "madswan/runner/deneb", TIP, None)
        assert r["runner"].get("Version") == "0.1.0"
        assert {n: a.get("Outcome") for n, a in r["answers"].items()} == {3: "launched", 4: "held"}
        assert r["places"] == {3: {"place": "/crew/places/change--a", "at": "2026-10-31T12:02:00Z", "status": STATUS, "why": None}}

    def test_a_runner_that_has_answered_nothing_reads_no_answers_and_no_places(self):
        files = dict(branch(), **{"answers.rec": None, "places.rec": None})
        r = runner.host_read("madswan", "deneb", TIP, files, {})
        assert (r["why"], r["answers"], r["places"]) == (None, {}, {})

    def test_a_host_with_no_branch_is_named(self):
        assert runner.of_host({}, "madswan", "alpha") == {
            "host": "alpha", "branch": "madswan/runner/alpha", "tip": None, "why": "no runner answers on alpha: madswan/runner/alpha does not exist"}

    def test_a_file_recfix_refused_hides_the_host_naming_the_file(self):
        r = runner.host_read("madswan", "deneb", TIP, dict(branch(), **{"places.rec": None}),
                             {"places.rec": "places.rec fails recfix --check: places.rec: 4: error: invalid integer"})
        assert r["why"] == "deneb's runner can't be read: madswan/runner/deneb at 5e1f0c2: places.rec fails recfix --check: places.rec: 4: error: invalid integer"
        assert "answers" not in r

    @pytest.mark.parametrize("files, why", [
        (dict(branch(), **{"runner.rec": None}), "it holds no runner.rec"),
        (branch(runner_rec="\nHost: alpha\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n"), "runner.rec names host alpha"),
        (branch(runner_rec=""), "runner.rec holds 0 Runner records, and names one"),
        (dict(branch(), **{"answers.rec": plan.Plan("Request: 3\nOutcome: launched\n")}), "answers.rec holds a record before its %rec: Answer"),
        (branch(answers=answer(3, "held") + answer(3, "launched")), "answers.rec holds request 3 twice"),
        (branch(places=placed("x", STATUS)), "places.rec holds a record with no request's number")])
    def test_a_branch_crew_cant_read_names_what(self, files, why):
        assert runner.host_read("madswan", "deneb", TIP, files, {})["why"] == f"deneb's runner can't be read: madswan/runner/deneb at 5e1f0c2: {why}"

    def test_a_status_that_is_no_json_marks_its_place_alone(self):
        r = runner.host_read("madswan", "deneb", TIP, branch(places=placed(3, "{not json") + placed(4, STATUS, "/crew/places/chore-b")), {})
        assert r["why"] is None and r["places"][4]["status"] == STATUS
        assert r["places"][3]["status"] is None
        assert r["places"][3]["why"].startswith("madswan/runner/deneb at 5e1f0c2: places.rec's status of the place of request 3 is no JSON (")


FLUME = pathlib.Path(__file__).parent / "flume-0.3.6"
CODE = "/Users/chuck/Code/github_afterthought/crew/places/change--teams-cross-to-flume-as-their-bolts-land"
WORDS = ("check-full failed on bolt/crew-runs-its-work-through-flume with change/teams-cross-to-flume-as-their-bolts-land "
         "merged: tests:logic (1 failed: tests/py/test_runner.py::TestStageOf::test_a_crossed_piece_reads_its_stage)")


def fixture(name):
    return (FLUME / f"{name}.json").read_text()


def path_of(name):
    """The place's location in a fixture, the runner's Place, without a tidied place's @<when>."""
    return json.loads(fixture(name))["status"]["places"][0]["place"].split("@")[0]


def stage(name=None, outcome="launched", base="bolt/crew-runs-its-work-through-flume", work="unit/teams-cross-to-flume-as-their-bolts-land"):
    """A piece's stage as stage_of reads it, its launch request 3 on deneb answered as given and its place's status
    the fixture named, carried on one line in places.rec and read back by host_read."""
    where = path_of(name) if name else None
    r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, outcome, where) if outcome else "",
                                                        places=placed(3, json.dumps(json.loads(fixture(name))), where) if name else ""), {})
    launch = held(rec(1, "launch", "unit/x"), rec(2, "launch", "chore/y"), rec(3, "launch", work, Base=base, After=[1, 2]))[2]
    return runner.stage_of(work, launch, r["answers"].get(3), r["places"].get(3), r["why"] or True, ["unit/x", "chore/y"])


class TestStageOf:
    """A crossed piece reads its stage from its launch, the runner's answer and Flume's status of its place, in Decision
    8's order, every field of Flume's guarded (read.2)."""

    def test_a_host_unread_or_a_piece_with_no_launch_is_unknown_naming_why(self):
        assert runner.stage_of("unit/a", None, None, None, "no runner answers on alpha: madswan/runner/alpha does not exist") == {
            "stage": "unknown", "why": "no runner answers on alpha: madswan/runner/alpha does not exist"}
        assert runner.stage_of("unit/a", None, None, None, True) == {"stage": "unknown", "why": "unit/a has no launch in requests.rec"}

    def test_unanswered_it_is_launching_and_answered_but_not_yet_placed_too(self):
        assert stage(None, outcome=None) == {"stage": "launching"}
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", "/crew/places/change--a")), {})
        assert runner.stage_of("unit/a", rec(3, "launch"), r["answers"][3], None, True) == {"stage": "launching", "place": "/crew/places/change--a"}

    def test_held_for_its_after_work_it_is_waiting_on_that_work(self):
        assert stage(None, outcome="held") == {"stage": "waiting", "after": ["unit/x", "chore/y"]}

    def test_refused_by_the_runner_it_is_refused_with_its_words(self):
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "refused", words="no repository afterthought/crew in this runner's configuration")), {})
        assert runner.stage_of("unit/a", rec(3, "launch"), r["answers"][3], None, True) == {
            "stage": "refused", "words": "no repository afterthought/crew in this runner's configuration"}

    def test_a_launch_answered_done_is_an_answer_crew_cant_read(self):
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "done")), {})
        assert runner.stage_of("unit/a", rec(3, "launch"), r["answers"][3], None, True)["why"] == (
            "the runner answered launch 3 of unit/a done, and a launch is answered held, launched or refused")

    def test_a_stage_waiting_for_room_is_queued(self):
        assert stage("queued") == {"stage": "queued", "of": "construct", "place": path_of("queued"), "tasks": (0, 0)}

    def test_a_stage_begun_is_its_name_and_code_says_its_tasks(self):
        assert stage("construct") == {"stage": "construct", "place": path_of("construct"), "tasks": (0, 0)}
        assert stage("code") == {"stage": "code", "place": CODE, "tasks": (6, 26)}

    def test_stopped_short_asking_it_needs_an_answer_with_the_agents_words_and_says_it_stalled(self):
        got = stage("stopped-short")
        question = json.loads(fixture("stopped-short"))["status"]["places"][0]["stages"][1]["end"]["words"]
        assert (got["stage"], got["of"], got["words"], got["found"], got["stalled"]) == ("needs", "code", question, False, True)
        assert got["words"].startswith("Head 118ec46 is ready for your flume:live run (6.1).")

    def test_waiting_on_its_caller_it_waits_with_flumes_words(self):
        got = stage("on-hold")
        assert got == {"stage": "waits", "of": "code", "why": "on_hold", "words": "Wait for the user's approval of the proposal on its Pending You card.",
                       "held": False, "place": path_of("on-hold"), "tasks": (0, 28)}

    def test_left_waiting_past_flumes_bound_it_is_stalled(self):
        got = stage("stalled")
        assert (got["stage"], got["of"], got["why"], got["words"]) == ("stalled", "code", "lost", None)

    def test_sent_back_after_a_failed_submission_it_is_at_its_stage_with_sluices_words(self):
        assert stage("sent-back") == {"stage": "code", "words": WORDS, "sent_back": 1, "verdict": "failed", "place": CODE, "tasks": (26, 26)}

    def test_submitted_it_names_sluices_number(self):
        assert stage("submitted") == {"stage": "submitted", "submission": "413", "place": CODE, "tasks": (26, 26)}

    def test_landed_on_its_bolt_it_is_merged_and_on_main_landed_with_the_commit(self):
        assert stage("landed") == {"stage": "merged", "commit": "d185a879b51dba33555c036392b50443f4dfc5e8", "place": CODE}
        main = stage("landed", base="main", work="fix/main/crew/red")
        assert (main["stage"], main["commit"]) == ("landed", "d185a879b51dba33555c036392b50443f4dfc5e8")

    def test_dropped_it_is_dropped(self):
        assert stage("dropped") == {"stage": "dropped", "place": CODE}

    def test_a_status_with_no_entry_for_its_place_or_no_json_is_unknown(self):
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", "/elsewhere"), places=placed(3, fixture("code").replace("\n", " "), "/elsewhere")), {})
        assert runner.stage_of("unit/a", rec(3, "launch"), r["answers"][3], r["places"][3], True) == {
            "stage": "unknown", "place": "/elsewhere", "why": "Flume's status of unit/a's place, as the runner carried it, holds no place /elsewhere"}
        r = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", "/p"), places=placed(3, "[", "/p")), {})
        got = runner.stage_of("unit/a", rec(3, "launch"), r["answers"][3], r["places"][3], True)
        assert got["stage"] == "unknown" and "places.rec's status of the place of request 3 is no JSON" in got["why"]

    @pytest.mark.parametrize("change", [
        lambda p: p.pop("phase"), lambda p: p.update(phase={"tidied": "soon"}), lambda p: p.update(stages="all"),
        lambda p: p.update(tasks=[{"text": "1.1", "ticked": "yes"}]), lambda p: p.update(submission=["x"]),
        lambda p: p.update(waiting_on="answer"), lambda p: p.update(current=3)])
    def test_a_field_of_another_shape_reads_none_and_never_becomes_text(self, change):
        status = json.loads(fixture("code"))
        change(status["status"]["places"][0])
        f = runner.flume_facts(status, CODE)
        assert f is not None and all(v is None or isinstance(v, (str, int, tuple, dict)) for v in f.values())
        got = runner.stage_of("unit/a", rec(3, "launch"), plan.Rec("Answer", [("Request", "3"), ("Outcome", "launched")]),
                              {"place": CODE, "status": status, "why": None}, True)
        assert got["stage"] in ("code", "unknown") and "None" not in (got.get("why") or "")

    def test_two_hosts_one_silent(self):
        """madswan/runner/deneb holds an answer and a place for request 3, and madswan/runner/alpha does not exist:
        request 3's work reads its stage from deneb's place, and alpha's work reads unknown, naming that no runner branch
        exists for alpha."""
        reads = {"deneb": runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", CODE), places=placed(3, json.loads(fixture("code")), CODE)), {})}
        requests = held(rec(1, "launch", "unit/b", host="alpha"), rec(2, "launch", "chore/c", host="alpha"),
                        rec(3, "launch", "unit/teams-cross-to-flume-as-their-bolts-land"))
        def of(work):
            launch = runner.launch_of(requests, work)
            r = runner.of_host(reads, "madswan", launch.get("Host"))
            n = int(launch.get("Request"))
            return runner.stage_of(work, launch, (r.get("answers") or {}).get(n), (r.get("places") or {}).get(n), r["why"] or True,
                                   runner.after_work(requests, launch))
        assert of("unit/teams-cross-to-flume-as-their-bolts-land")["stage"] == "code"
        assert of("unit/b") == of("chore/c") == {"stage": "unknown", "why": "no runner answers on alpha: madswan/runner/alpha does not exist"}


class TestLaunchOf:
    """A piece's stage is read from its newest launch that no drop names (Decision 8): an amendment of a held launch is
    a drop and a launch anew (Decision 7)."""

    def test_the_newest_launch_not_dropped_is_the_ones_read(self):
        rs = held(rec(1, "launch"), rec(2, "launch", "unit/b", After=[1]), rec(3, "drop", Of=1), rec(4, "launch", Brief="Build it, amended."))
        assert runner.launch_of(rs, "unit/a").get("Request") == "4"
        assert runner.launch_of(rs, "unit/b").get("Request") == "2"
        assert runner.launch_of(rs, "chore/c") is None
        assert runner.launch_of(held(rec(1, "launch"), rec(2, "drop", Of=1)), "unit/a") is None
        assert runner.after_work(rs, rs[1]) == ["unit/a"]


def test_a_place_over_as_done_or_in_a_phase_crew_does_not_read_is_unknown_saying_so():
    """A kind that lands ends landed or dropped; a place Flume says is done, or in a phase crew does not know, is unknown,
    in Flume's words (read.1)."""
    for phase, why in (({"tidied": {"over": "done", "at": 1, "pending_for": []}}, "says its work is done, and a place of a kind that lands ends landed or dropped"),
                       ({"resting": {}}, "gives phase resting, which crew does not read")):
        status = json.loads(fixture("code"))
        status["status"]["places"][0]["phase"] = phase
        got = runner.stage_of("unit/a", rec(3, "launch"), plan.Rec("Answer", [("Request", "3"), ("Outcome", "launched")]),
                              {"place": CODE, "status": status, "why": None}, True)
        assert got["stage"] == "unknown" and got["why"] == f"Flume's status of unit/a's place {CODE} {why}"

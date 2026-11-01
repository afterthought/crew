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
from facts import FactsWrite, crossed_fleet, flume_plan
import plan
import runner

AT, BY = "2026-10-31T12:00:00Z", "madswan-dispatch-deneb"
LAUNCH = dict(Repo="afterthought/crew", Kind="change", Base="bolt/b", Priority=2, Intent="madswan/b", Recipient="madswan/planner",
              Brief="Build it.")


def rec(n, act, work="unit/a", **given):
    """A request as plan.request makes it, a launch carrying every field a launch needs unless given otherwise: a kit's
    work names no host or stream, the runner whose configuration names its repository taking it (the user's ruling of
    2026-11-01)."""
    if act == "launch":
        given = dict(dict(LAUNCH, Name=work.split("/")[-1]), **given)
    return plan.Rec("Request", runner.request_fields(n, act, work, given, AT, BY))


def held(*recs):
    """requests.rec holding these requests, as the plan's records."""
    return plan.Plan(runner.REQUESTS + "".join("\n" + "\n".join(r.lines()) + "\n" for r in recs)).recs("Request")


class TestRequests:
    """A request is numbered once, carries what its act needs and names what it acts on (Decision 4)."""

    def test_a_requests_fields_are_written_in_the_files_order_and_a_flag_as_yes(self):
        r = rec(3, "retry", Words="Read the plan again.", Submission=True, Of=1, Stage=None)
        assert r.fields == [("Request", "3"), ("Act", "retry"), ("Work", "unit/a"), ("Of", "1"),
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

    def test_a_launch_with_no_brief_is_refused(self):
        why = runner.request_refusal([], rec(1, "launch", Brief=None))
        assert why.startswith("launch 1 for unit/a names no Brief: a launch carries Request, Act, Work, Date, By, Repo, Kind, "
                              "Name, Base, Priority")

    def test_a_kits_launch_names_no_host_or_stream_and_a_roles_names_both(self):
        """The runner whose configuration names a kit's repository takes its work in the stream it gives, and crew
        names neither (the user's ruling of 2026-11-01); a role's work runs on its main level's host in its stream."""
        kit = ("launch 1 of unit/a names a Host or a Stream: a kit's work is taken by the runner whose configuration names its "
               "repository, in the stream that configuration gives, and crew names neither")
        assert runner.request_refusal([], rec(1, "launch", Host="deneb")) == kit
        assert runner.request_refusal([], rec(1, "launch", Stream="madswan")) == kit
        role = dict(Repo="afterthought/blueprints", Kind="chore", Base="main", Intent="madswan-design", Recipient="madswan/design")
        assert runner.request_refusal([], rec(1, "launch", "role/design/r", Host="deneb", Stream="madswan", **role)) is None
        assert runner.request_refusal([], rec(1, "launch", "role/design/r", **role)) == (
            "launch 1 of role/design/r names no Host or no Stream: a role's work runs on the host and in the stream its role runs in")

    def test_a_retry_of_nothing_is_refused_naming_the_request(self):
        """A retry would name request 9, which is no launch."""
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "retry", Of=9)) == (
            "retry 2 for unit/a names request 9, which is no launch: requests.rec does not hold it")
        have = held(rec(1, "launch"), rec(2, "drop", Of=1))
        assert runner.request_refusal(have, rec(3, "retry", Of=2)) == "retry 3 for unit/a names request 2, which is no launch"

    def test_a_retry_drop_or_priority_names_a_launch_of_its_own_work_and_no_host(self):
        """It is taken by the runner that took the launch it names, so it names no host of its own."""
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "drop", "unit/b", Of=1)) == "drop 2 for unit/b names launch 1, which is unit/a's"
        assert runner.request_refusal(have, rec(2, "priority", Of=1, Priority=3, Host="alpha")) == (
            "priority 2 for unit/a carries Host, which a priority does not take")
        assert runner.request_refusal(have, rec(2, "priority", Of=1)).startswith("priority 2 for unit/a names no Priority")

    def test_a_request_carries_nothing_its_act_does_not_take(self):
        have = held(rec(1, "launch"))
        assert runner.request_refusal(have, rec(2, "drop", Of=1, Words="Gone.", Stream="madswan")) == (
            "drop 2 for unit/a carries Stream, Words, which a drop does not take")
        assert runner.request_refusal([], rec(1, "reorder")) == "request 1 is a reorder, and a request is a launch, a retry, a drop or a priority"

    def test_the_work_is_named_as_crew_names_it(self):
        for work in ("unit/a", "chore/bump", "fix/b/tidy", "fix/main/crew/red", "role/design/record-0053"):
            assert runner.WORK.match(work)
        assert runner.request_refusal([], rec(1, "launch", "unit/A")) == (
            "launch 1 serves unit/A, and a request serves unit/<unit>, chore/<chore>, fix/<bolt>/<name>, fix/main/<kit>/<name> or "
            "role/<role>/<name>")
        assert runner.request_refusal([], rec(1, "launch", "role/design")).startswith("launch 1 serves role/design")
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
        changed = rec(1, "launch", Brief="Build it otherwise.")
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
        assert plan.request(w, "launch", "unit/a", Name="a", **LAUNCH) == 1
        assert plan.request(w, "launch", "unit/b", Name="b", After=[1], **LAUNCH) == 2
        rs = plan.Plan(w.files["requests.rec"]).recs("Request")
        assert [(r.get("Request"), r.get("Work"), r.all("After"), r.get("By")) for r in rs] == [
            ("1", "unit/a", [], BY), ("2", "unit/b", ["1"], BY)]
        assert w.files["requests.rec"].startswith(runner.REQUESTS)
        w2 = FactsWrite("%rec: Bolt\n%key: Bolt\n", files={"requests.rec": w.files["requests.rec"]})
        assert plan.request(w2, "drop", "unit/b", Of=2) == 3

    def test_a_refused_request_leaves_the_writes_files_as_they_were(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        w = FactsWrite("%rec: Bolt\n%key: Bolt\n")
        plan.request(w, "launch", "unit/a", Name="a", **LAUNCH)
        text = w.files["requests.rec"]
        with pytest.raises(Refusal, match="^retry 2 for unit/a names request 9, which is no launch"):
            plan.request(w, "retry", "unit/a", Of=9, Words="Go on.")
        assert w.files["requests.rec"] == text

    def test_a_branch_whose_file_was_made_before_a_field_was_allowed_takes_crews_descriptor(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        old = runner.REQUESTS.replace(" Hold After Brief", " After Brief") + "\n" + "\n".join(rec(1, "launch").lines()) + "\n"
        w = FactsWrite("%rec: Bolt\n%key: Bolt\n", files={"requests.rec": old})
        plan.request(w, "drop", "unit/a", Of=1)
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

    def test_a_launch_is_read_from_the_runner_that_took_it(self):
        """madswan/runner/deneb holds an answer and a place for request 3, and madswan/runner/alpha can't be read: request
        3's work reads its stage from deneb's place, since crew names no host on a launch and the runner that took it is
        the one whose answers hold it; requests 1 and 2, which deneb has not taken, read unknown naming alpha's runner,
        which may have; with alpha read and holding neither they read launching; and a launch two runners took reads
        unknown naming both (the user's ruling of 2026-11-01; read.1)."""
        deneb = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", CODE),
                                                                 places=placed(3, json.loads(fixture("code")), CODE)), {})
        silent = runner.host_read("madswan", "alpha", TIP, {}, {"runner.rec": "recfix refused it"})
        requests = held(rec(1, "launch", "unit/b"), rec(2, "launch", "chore/c"), rec(3, "launch", "unit/teams-cross-to-flume-as-their-bolts-land"))

        def of(work, reads):
            return runner.piece_stage(requests, reads, runner.launch_of(requests, work))
        reads = {"deneb": deneb, "alpha": silent}
        assert of("unit/teams-cross-to-flume-as-their-bolts-land", reads)["stage"] == "code"
        why = "no runner crew read has taken request 1, and alpha's runner can't be read: madswan/runner/alpha at 5e1f0c2: recfix refused it"
        assert of("unit/b", reads) == {"stage": "unknown", "why": why}
        quiet = {"deneb": deneb, "alpha": runner.host_read("madswan", "alpha", TIP, branch("alpha"), {})}
        assert of("unit/b", quiet) == of("chore/c", quiet) == {"stage": "launching"}
        both = {"deneb": deneb, "alpha": runner.host_read("madswan", "alpha", TIP, branch("alpha", answers=answer(3, "launched", CODE)), {})}
        assert of("unit/teams-cross-to-flume-as-their-bolts-land", both) == {"stage": "unknown", "why": (
            "request 3 was taken by the runners on alpha and deneb, whose configurations each name its repository, so crew "
            "can't tell which place is its work")}
        assert of("unit/b", {})["why"].startswith("no runner answers for the partition")


class TestWhere:
    """Where a bolt's or a kit's work runs is what the runner that took it reported (the user's ruling of 2026-11-01;
    runner.where): the host whose runner took its newest launch taken, the kit's folder and stream as Flume's status of
    its place there names them."""

    def test_the_host_folder_and_stream_of_the_newest_launch_taken(self):
        code = json.loads(fixture("code"))
        deneb = runner.host_read("madswan", "deneb", TIP, branch(answers=answer(3, "launched", CODE), places=placed(3, code, CODE)), {})
        alpha = runner.host_read("madswan", "alpha", TIP, branch("alpha", answers=answer(1, "launched", "/old")), {})
        launches = held(rec(1, "launch"), rec(2, "launch", "unit/b"), rec(3, "launch", "unit/c"))
        assert runner.where({"deneb": deneb, "alpha": alpha}, launches, "bolt b") == (
            {"host": "deneb", "dir": "/Users/chuck/Code/github_afterthought/crew", "stream": "default"}, None)
        assert runner.where({"alpha": alpha}, launches, "bolt b") == ({"host": "alpha", "dir": None, "stream": None}, None)

    def test_work_no_runner_has_taken_is_nowhere_and_two_runners_are_told_apart_by_none(self):
        silent = runner.host_read("madswan", "alpha", TIP, {}, {"runner.rec": "recfix refused it"})
        assert runner.where({"alpha": silent}, held(rec(1, "launch")), "bolt b") == (None, (
            "no runner has reported taking bolt b's work yet, so crew can't tell where it runs; alpha's runner can't be read: "
            "madswan/runner/alpha at 5e1f0c2: recfix refused it"))
        two = {h: runner.host_read("madswan", h, TIP, branch(h, answers=answer(1, "launched", CODE)), {}) for h in ("alpha", "deneb")}
        assert runner.where(two, held(rec(1, "launch")), "bolt b") == (None, (
            "crew can't tell where bolt b's work runs: request 1 was taken by the runners on alpha and deneb, whose "
            "configurations each name its repository"))


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


class TestPriorities:
    """A launch's priority is its bolt's place among the plan's started bolts, counted from the end, and a write that
    launches or reorders bolts sends each priority the plan's order changed (Decision 6)."""
    FLEET = crossed_fleet()

    @staticmethod
    def write(*bolts):
        """madswan's plan with each bolt (name, Path or None) holding one unit named after it, its work built by crw-4."""
        return FactsWrite(flume_plan([(b, None, p) for b, p in bolts], [(f"{b}-unit", b, [], "unit", []) for b, _ in bolts]),
                          label="madswan")

    @staticmethod
    def priorities(w):
        """Each launch's work and the priority its requests last set, in the order launched."""
        rs = plan.Plan(w.files["requests.rec"]).recs("Request")
        last = {}
        for r in rs:
            if r.get("Act") == "launch":
                last[r.get("Request")] = [r.get("Work"), r.get("Priority")]
            elif r.get("Act") == "priority":
                last[r.get("Of")][1] = r.get("Priority")
        return [tuple(v) for v in last.values()]

    def start(self, w, bolt):
        w.plan.bolt(bolt).set("Path", "flume")
        plan.reach_places(self.FLEET, w, bolt)

    def test_the_first_bolt_in_the_plan_has_the_highest(self):
        """x and y are started, t between them and z after them planned: a planned bolt has no priority."""
        p = plan.Plan(flume_plan([("x", None, "flume"), ("t", None, None), ("y", None, "flume"), ("z", None, None)]))
        assert [runner.priority_of(p, b) for b in ("x", "t", "y", "z", "gone")] == [2, None, 1, None, None]

    def test_two_bolts_started_in_order(self, monkeypatch):
        """x is started and then y, x above y in the plan: x's launches carry a higher priority than y's, each naming
        crew's repository and no host or stream, intent madswan/<bolt> and recipient madswan/planner."""
        monkeypatch.setenv("CREW_AGENT", BY)
        w = self.write(("x", None), ("y", None))
        self.start(w, "x")
        self.start(w, "y")
        assert self.priorities(w) == [("unit/x-unit", "2"), ("unit/y-unit", "1")]
        launches = [r for r in plan.Plan(w.files["requests.rec"]).recs("Request") if r.get("Act") == "launch"]
        assert [(r.get("Repo"), r.get("Host"), r.get("Stream"), r.get("Intent"), r.get("Recipient")) for r in launches] == [
            ("crew", None, None, "madswan/x", "madswan/planner"), ("crew", None, None, "madswan/y", "madswan/planner")]

    def test_a_third_started_raises_those_above_it(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", BY)
        w = self.write(("x", None), ("y", None), ("z", None))
        for b in ("x", "y", "z"):
            self.start(w, b)
        assert self.priorities(w) == [("unit/x-unit", "3"), ("unit/y-unit", "2"), ("unit/z-unit", "1")]

    def test_a_reorder_sends_only_what_changed(self, monkeypatch):
        """crew bolt order puts z above y: requests.rec gains a priority for each launched place of y and z, whose
        priorities changed, and none for x's."""
        from facts import apply, known
        monkeypatch.setenv("CREW_AGENT", BY)
        w = self.write(("x", None), ("y", None), ("z", None))
        for b in ("x", "y", "z"):
            self.start(w, b)
        n = len(plan.Plan(w.files["requests.rec"]).recs("Request"))
        apply(w, "bolt order z --before y", ctx=known(w, fleet=self.FLEET))
        new = plan.Plan(w.files["requests.rec"]).recs("Request")[n:]
        assert [(r.get("Act"), r.get("Work"), r.get("Priority")) for r in new] == [
            ("priority", "unit/y-unit", "1"), ("priority", "unit/z-unit", "2")]
        apply(w, "bolt order z --before y", ctx=known(w, fleet=self.FLEET))
        assert len(plan.Plan(w.files["requests.rec"]).recs("Request")) == n + 2

    def test_a_reorder_on_a_branch_with_no_requests_writes_none(self):
        from facts import apply, known
        w = self.write(("x", None), ("y", None))
        apply(w, "bolt order y --first", ctx=known(w, fleet=self.FLEET))
        assert "requests.rec" not in w.files

    def test_a_dropped_launch_a_fix_of_main_and_a_bolt_gone_take_no_priority(self):
        p = plan.Plan(flume_plan([("x", None, "flume"), ("y", None, "flume")]))
        fix = dict(Base="main", Intent="madswan/main/crew", Recipient="madswan/ops", Name="main--red", Hold="submission")
        rs = held(rec(1, "launch", Base="bolt/x"), rec(2, "drop", Of=1), rec(3, "launch", "unit/b", Base="bolt/gone"),
                  rec(4, "launch", "fix/main/crew/red", **fix), rec(5, "launch", "unit/c", Base="bolt/y", Priority=7),
                  rec(6, "priority", "unit/c", Of=5, Priority=1))
        assert runner.priorities(p, rs) == []
        assert [(r.get("Request"), n) for r, n in runner.priorities(p, rs[:5])] == [("5", 1)]

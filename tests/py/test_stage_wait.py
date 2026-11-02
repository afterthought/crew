"""What a stage's wait reads of sluice beyond the refs (record 0032, point 4; read.1, read.2): plan.overview_look, one
look at `sluice overview --json`, which learns where each submission it lists came from and asks `sluice status <id>
--json` of a conflict or blamed line whose submission it has not seen, since sluice records a conflict within seconds of
its submission; plan.overview_facts and plan.submission_from, the facts read of each document; and plan.sluice_said,
the line the conductor reads. The documents under sluice-0.18.0/ were recorded from sluice 0.18.0 on mac-studio,
2026-10-17, in a scratch kit whose places a to e submitted to bolt/tenant-environments as swb-1-unit-1 to -5: a landed
(#1), b conflicted on shared.txt (#2), c failed its check (#3), then d (#4) and e (#5) queued (overview-queued.json)
and stepped until d landed and e was blamed (overview-blamed.json); status-9.json is sluice's answer for no such
submission. That the wait prints these lines before its answer, and the read itself, are the journey's
(t-journey-units)."""
import datetime
import json
import pathlib

import pytest

from facts import owed

import plan

RECORDED = pathlib.Path(__file__).parent / "sluice-0.18.0"
BOLT = "bolt/tenant-environments"


def doc(name):
    return json.loads((RECORDED / f"{name}.json").read_text())


PLACES = pathlib.Path(doc("overview-queued")["repository"]).parent.parent / "places"


def place(name):
    return str(PLACES / name)


def at(t):
    return datetime.datetime.fromisoformat(f"2026-10-17T{t}+00:00")


class Status:
    """sluice status <id> --json as the wait reads it, from the recorded documents, counting what it was asked."""

    def __init__(self):
        self.asked = []

    def __call__(self, sid):
        self.asked.append(sid)
        f = RECORDED / f"status-{sid}.json"
        if not f.exists():
            return None, "it exited 1: no submission 9"
        d = json.loads(f.read_text())
        return (None, f"it exited 1: {d['error']['message']}") if "error" in d else (d, None)


def look(seen, name, since, status, why=None):
    return plan.overview_look(seen, doc(name) if name else None, why, place(since[0]), at(since[1]), status)


class TestFacts:
    def test_the_overview_gives_each_branchs_version_the_paths_of_what_is_queued_and_its_conflicts_and_blames(self):
        versions, paths, outcomes = plan.overview_facts(doc("overview-queued"))
        assert versions == {BOLT: 18}
        assert paths == {4: place("d"), 5: place("e")}
        assert [(b, r["event"], r["id"], t) for b, r, t in outcomes] == [
            (BOLT, "conflict", 2, at("16:04:11")), (BOLT, "blamed", 3, at("16:04:14"))]

    def test_a_conflict_or_a_blame_names_its_id_and_never_where_it_came_from(self):
        _, _, outcomes = plan.overview_facts(doc("overview-blamed"))
        assert all("from" not in r and "path" not in r for _, r, _ in outcomes)
        assert plan.overview_facts(doc("overview-blamed"))[1] == {}

    @pytest.mark.parametrize("d", [
        {}, doc("status-9"), doc("status-2"), dict(doc("overview-queued"), schema="sluice/overview@2"),
        dict(doc("overview-queued"), branches=[{k: v for k, v in doc("overview-queued")["branches"][0].items() if k != "version"}])])
    def test_a_document_sluice_0_18_0_would_not_print_is_no_overview(self, d):
        assert plan.overview_facts(d) is None

    def test_a_submission_names_the_path_it_came_from_or_none(self):
        assert plan.submission_from(doc("status-2")) == place("b")
        pulled = dict(doc("status-2"), **{"from": {"agent": "recovery", "worktree": "pull/19", "head": "recovery/cards-4"}})
        assert plan.submission_from(pulled) is None
        with pytest.raises(ValueError, match="sluice/submission@1"):
            plan.submission_from(doc("status-9"))


class TestLook:
    def test_a_conflict_recorded_before_any_look_saw_its_submission_is_found_by_asking_sluice_status_once(self):
        status, seen = Status(), {}
        assert look(seen, "overview-queued", ("b", "16:04:00"), status) == ([(BOLT, doc("overview-queued")["branches"][0]["recent"][1])], [])
        assert status.asked == [2, 3]

    def test_a_blame_of_a_submission_a_look_saw_queued_needs_no_status(self):
        status, seen = Status(), {}
        assert look(seen, "overview-queued", ("e", "16:04:20"), status) == ([], [])
        lines, notes = look(seen, "overview-blamed", ("e", "16:04:20"), status)
        assert [(b, r["event"], r["id"]) for b, r in lines] == [(BOLT, "blamed", 5)] and notes == []
        assert status.asked == []

    def test_an_unchanged_version_reads_nothing_more(self):
        status, seen = Status(), {}
        look(seen, "overview-queued", ("d", "16:04:00"), status)
        asked = list(status.asked)
        assert look(seen, "overview-queued", ("d", "16:04:00"), status) == ([], [])
        assert status.asked == asked

    def test_a_line_is_told_once_a_wait_and_a_submission_asked_of_once(self):
        status, seen = Status(), {}
        assert look(seen, "overview-queued", ("b", "16:04:00"), status)[0]
        seen["versions"] = {BOLT: 17}
        assert look(seen, "overview-queued", ("b", "16:04:00"), status) == ([], [])
        assert status.asked == [2, 3]

    def test_another_places_conflict_is_not_the_stages(self):
        status, seen = Status(), {}
        assert look(seen, "overview-queued", ("d", "16:04:00"), status) == ([], [])
        assert status.asked == [2, 3]

    def test_a_line_from_before_the_stage_began_is_not_its(self):
        status, seen = Status(), {}
        assert look(seen, "overview-queued", ("b", "16:04:12"), status) == ([], [])
        assert status.asked == [3]

    def test_an_overview_that_cant_be_read_is_said_once_and_the_wait_goes_on_by_refs(self):
        status, seen = Status(), {}
        why = "it exited 64: error: unrecognized subcommand 'overview'"
        assert look(seen, None, ("b", "16:04:00"), status, why) == ([], [
            "sluice's overview can't be read (it exited 64: error: unrecognized subcommand 'overview'): the wait goes on "
            "by refs alone, and says nothing of a conflict or a failed check sluice finds"])
        assert look(seen, None, ("b", "16:04:00"), status, why) == ([], [])
        assert look(seen, "overview-queued", ("b", "16:04:00"), status)[0]

    def test_a_document_that_is_no_overview_is_said_the_same_way(self):
        lines, notes = look({}, "status-9", ("b", "16:04:00"), Status())
        assert lines == [] and notes == [
            "sluice's overview can't be read (it is not the sluice/overview@1 sluice 0.18.0 prints): the wait goes on by "
            "refs alone, and says nothing of a conflict or a failed check sluice finds"]

    def test_a_submission_sluice_status_cant_give_is_named_and_not_taken_as_the_stages(self):
        status, seen = Status(), {}
        recent = doc("overview-queued")["branches"][0]["recent"]
        d = doc("overview-queued")
        d["branches"][0]["recent"] = recent + [dict(recent[1], id=9, at="2026-10-17T16:04:16Z")]
        lines, notes = plan.overview_look(seen, d, None, place("b"), at("16:04:12"), status)
        assert lines == [] and notes == [
            "crew can't tell whether sluice's #9 came from this stage's place: sluice status 9 --json: it exited 1: no submission 9"]
        d["branches"][0]["version"] = 19
        assert plan.overview_look(seen, d, None, place("b"), at("16:04:12"), status) == ([], [])
        assert status.asked == [3, 9]


class TestSaid:
    @pytest.mark.parametrize("name, n, said", [
        ("overview-queued", 1, "merge on b: sluice says of swb-1-unit-2's submission to bolt/tenant-environments: conflict #2 on shared.txt; "
                               "the wait goes on until the stage ends"),
        ("overview-queued", 2, "merge on b: sluice says of swb-1-unit-2's submission to bolt/tenant-environments: blamed #3 on 3d44d6b; "
                               "the wait goes on until the stage ends")])
    def test_the_conductor_reads_the_line_as_sluices_overview_says_it(self, name, n, said):
        r = doc(name)["branches"][0]["recent"][n]
        assert plan.sluice_said(owed("merge", name="b", slot="unit-2"), "swb-1-unit-2", BOLT, r) == said

    def test_an_absent_field_is_left_out_never_printed(self):
        assert plan.sluice_words({"event": "conflict", "id": 2}) == "conflict #2"
        assert plan.sluice_words({"event": "blamed", "id": 3, "combination": None}) == "blamed #3"

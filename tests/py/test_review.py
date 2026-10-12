"""A batch's review and who a write tells (briefs.12, teams.7, teams.11): plan.review_prompt and reading_command for
what the reviewer is sent, plan.batch_due_said for what the planner is told, plan.notices for whom a write to the plan
tells, and crew.tell_refusal for a tell that types nothing. Which changes are due, and when a batch is, are
test_batches'; starting the reviewer, recording the batch and the tells themselves, the review journey's
(t-journey-review)."""
import pytest

import crew
import plan

BOX = "chuck-herdr-alpha"
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": BOX}},
         "teams": {"swb-1": {"name": "swb-1", "machine": BOX, "ssh": BOX, "kit": {"name": "switchboard-kit", "main": "/kit/main"}},
                   "atl-1": {"name": "atl-1", "machine": "mac-studio", "ssh": "mac-studio", "kit": {"name": "atlas-kit", "main": "/atlas/main"}}}}


def test_the_reviewer_is_sent_each_change_due_and_how_to_read_it_at_its_commit_from_the_main_levels_host():
    said = plan.review_prompt(FLEET, "wldn", 1, "/h/reports/batch-wldn-1.md", [("x1", "swb-1", "abc1234", None), ("z1", "atl-1", "def5678", None)])
    assert said.startswith("Review batch 1 of wldn, 2 changes, and write its summary to /h/reports/batch-wldn-1.md. ")
    assert ("x1 (swb-1, switchboard-kit on chuck-herdr-alpha, at abc1234): list its files with `git -C /kit/main ls-tree -r --name-only "
            "abc1234 openspec/changes/x1/` and read each with `git -C /kit/main show abc1234:<path>`.") in said
    assert "z1 (atl-1, atlas-kit on mac-studio, at def5678): list its files with `ssh -o BatchMode=yes mac-studio git -C /atlas/main ls-tree" in said
    assert "[crew]" not in said


def test_the_planner_is_told_which_changes_are_due_and_why():
    assert plan.batch_due_said("wldn", [("x1", "swb-1", "a", None), ("y1", "swb-2", "b", None)], ["2 changes are due, and a batch is every 2"]) == (
        "A batch of wldn's changes is due: x1 (swb-1), y1 (swb-2); 2 changes are due, and a batch is every 2. Start its reviewer with crew "
        "review wldn, wait for the summary with crew review wldn --wait, then post its cards.")


class TestNotices:
    TEAMS = {"swb-1": {}, "swb-2": {}}

    def notices(self, before, after, touched, me="chuck@mac-studio", lost=None, quiet=()):
        seen = dict(before=before, after=after, touched=touched, lost=lost or {}, quiet=set(quiet), label="wldn")
        return plan.notices(self.TEAMS, seen, me, "plan(te): add u (chuck@mac-studio)")

    def test_a_write_to_a_held_bolt_tells_its_conductor_the_subject(self):
        assert self.notices({"te": "swb-1"}, {"te": "swb-1"}, ["te"]) == ([("swb-1-conductor", "plan(te): add u (chuck@mac-studio)")], [], False)

    def test_the_conductors_own_write_tells_it_nothing_and_a_bolt_no_team_holds_tells_no_one(self):
        assert self.notices({"te": "swb-1"}, {"te": "swb-1"}, ["te"], me="swb-1-conductor") == ([], [], False)
        assert self.notices({}, {}, ["apex"]) == ([], [], False)

    def test_a_move_tells_both_conductors_and_the_one_it_left_to_close_its_cards(self):
        tells, shown, _ = self.notices({"te": "swb-1", "cp": "swb-2"}, {"te": "swb-1", "cp": "swb-2"}, ["te", "cp"], lost={"swb-1": ["verify/a"]})
        assert tells == [("swb-1-conductor", "plan(te): add u (chuck@mac-studio). Close any Pending You card you have open for verify/a."),
                         ("swb-2-conductor", "plan(te): add u (chuck@mac-studio)")]
        assert self.notices({"te": "swb-1"}, {"te": "swb-1"}, ["te"], me="swb-1-conductor", lost={"swb-1": ["verify/a"]})[1] == [
            "Close any Pending You card you have open for verify/a."]

    def test_a_bolt_added_or_one_a_team_held_dropped_tells_the_dispatchers(self):
        assert self.notices({}, {"edge": None}, ["edge"])[2] is True
        assert self.notices({"cp": "swb-2"}, {}, ["cp"])[2] is True
        assert self.notices({"later": None}, {}, ["later"])[2] is False

    def test_a_team_the_write_greets_itself_is_not_also_told(self):
        assert self.notices({"te": None}, {"te": "swb-1"}, ["te"], quiet=["swb-1"])[0] == []


class TestTell:
    WAIT = "swb-1-conductor is waiting on a question in its pane: nothing was sent; tell it again once the question is answered"

    @pytest.mark.parametrize("status, asking, unread, said", [
        ("blocked", True, None, WAIT), ("idle", True, None, WAIT),
        (None, False, None, f"could not tell swb-1-conductor on {BOX}: it is not up"),
        ("idle", False, "herdr names no session for it",
         f"could not tell swb-1-conductor on {BOX}: herdr names no session for it, so crew can't tell whether it is waiting on a question; nothing was sent"),
        ("idle", False, None, None)])
    def test_a_tell_reaches_its_agent_as_a_prompt_or_not_at_all(self, status, asking, unread, said):
        assert crew.tell_refusal("swb-1-conductor", BOX, status, asking, unread) == said


def test_a_tell_herdr_refused_to_type_says_why_in_crews_words():
    blocked = '{"error": {"code": "agent_blocked", "message": "blocked"}}'
    assert crew.typed_refusal("swb-1-conductor", BOX, blocked) == TestTell.WAIT
    assert crew.typed_refusal("swb-1-conductor", BOX, "") == f"could not tell swb-1-conductor on {BOX}: it is not up"


def test_an_agent_crew_starts_none_by_that_name_is_refused():
    fleet = {"teams": {}, "partitions": {"wldn": {"label": "wldn", "machine": BOX, "session": "wldn-3"}}}
    assert crew.place_of_agent(fleet, "wldn-planner") == (BOX, "wldn-3")
    with pytest.raises(crew.Refusal, match="no agent somebody: crew starts none by that name"):
        crew.place_of_agent(fleet, "somebody")

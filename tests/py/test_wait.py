"""What a wait on a stage says, look by look, until the stage ends (teams.4): plan.look on one look's facts,
plan.ended_words for a stage whose end something else recorded, Owed.phrase for how a stage is named, and
plan.owed_of for the stage crew needs ends short. That a wait records the end it sees, and that a stop-short reaches
the waiting wait or the conductor, are the journey's (t-journey-units, t-journey-prompts)."""
import pytest

from facts import owed

import plan

WORKING, QUIET = (False, "is working", None), (False, "has been quiet for 3 minutes, under the limit of 15 minutes", None)


def look(o=None, words=None, owed_=True, gone=False, got=None, missing="", quiet=WORKING, out_of_time=False):
    return plan.look(o or owed("construct"), "swb-1-unit-1", 0, words, owed_, gone, got, missing, quiet, out_of_time)


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

    def test_a_quiet_agent_past_the_limit_is_stuck_saying_what_it_lacks(self):
        assert look(o=owed("merge"), missing="bolt/b not yet holding it", quiet=(True, "quiet for 0 minutes", None)) == (
            "stuck", "swb-1-unit-1 is stuck in merge on a: quiet for 0 minutes, with bolt/b not yet holding it and nothing it needs said")
        assert look(o=owed("settle"), missing="nothing committed since it began", quiet=(True, "quiet for 0 minutes", None)) == (
            "stuck", "swb-1-unit-1 is stuck in settle on a: quiet for 0 minutes, with nothing committed since it began and nothing it needs said")

    def test_stuck_names_what_crew_could_not_read_of_its_own_work(self):
        assert look(missing="nothing committed", quiet=(True, "quiet for 20 minutes", "no transcript for its session s1"))[1].endswith(
            "; crew could not read whether it waits on work of its own (no transcript for its session s1)")

    @pytest.mark.parametrize("quiet, doing", [(WORKING, "is working"), (QUIET, QUIET[1])])
    def test_out_of_time_it_is_still_running_and_nothing_is_recorded(self, quiet, doing):
        assert look(quiet=quiet, out_of_time=True) == (
            "running", f"construct on a is still running after the wait's 0 ms: swb-1-unit-1 {doing}; nothing is recorded yet")

    def test_else_it_looks_again(self):
        assert look(quiet=QUIET) == (None, QUIET[1])


class TestPhrase:
    @pytest.mark.parametrize("stage, name, obj, said", [
        ("code", "a", "unit/a", "code on a"),
        ("fix", "fix/tenant-environments/tidy", "fix/tenant-environments/tidy", "fix fix/tenant-environments/tidy"),
        ("merge", "fix/tenant-environments/tidy", "fix/tenant-environments/tidy", "merge of fix/tenant-environments/tidy"),
        ("proof", "tenant-environments", "bolt/tenant-environments", "the proof of tenant-environments")])
    def test_a_stage_is_named_by_what_it_is_of(self, stage, name, obj, said):
        assert owed(stage, name=name, slot="ops" if stage == "proof" else "unit-1", obj=obj).phrase() == said


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

    def test_a_fix_and_a_proof(self):
        assert self.end("delivered", on=("fix/t/tidy", "agent/swb-1-unit-1"), Delivered="bolt/t@abc1234", Why="fix(tidy): merge ended") == (
            "merge of fix/t/tidy has ended: swb-1-unit-1 delivered bolt/t@abc1234")
        assert self.end("stopped", on=("stage/t/proof", "bolt/t", "agent/swb-1-ops")) == (
            "the proof of t has ended: crew ended swb-1-unit-1 before it delivered")

    def test_with_no_end_recorded(self):
        assert plan.ended_words("swb-1", "swb-1-unit-1", None) == (
            "swb-1-unit-1 owes no stage's end, and none is recorded for it on this host")


class TestNeeds:
    T = {"name": "swb-1"}
    HELD = {"unit-2": ["unit-2", "unit", "b", "/kit/places/b"]}

    def test_the_slots_owed_stage_ends_short(self):
        o, = plan.owed_of(self.T, "unit-2", [["unit-2", "b", "construct", "20261012T100000Z-h-1-1", "unit/b"]], self.HELD)
        assert (o.agent, o.phrase()) == ("swb-1-unit-2", "construct on b")

    def test_ops_owes_its_proof(self):
        o, = plan.owed_of(self.T, "ops", [["ops", "t", "proof", "20261012T100000Z-h-1-1", "bolt/t"]], {})
        assert o.phrase() == "the proof of t"

    @pytest.mark.parametrize("slot, lines", [
        ("unit-2", []),
        ("conductor", [["unit-2", "b", "construct", "x", "unit/b"]]),
        ("unit-2", [["unit-2", "c", "construct", "x", "unit/c"]])])
    def test_an_agent_that_owes_no_stage_is_refused(self, slot, lines):
        with pytest.raises(plan.Refusal, match=f"swb-1-{slot} runs no stage crew is waiting on"):
            plan.owed_of(self.T, slot, lines, self.HELD)

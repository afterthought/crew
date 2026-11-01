"""A bolt's landing as the run record holds it (bolt-teams "A landing queued holds its bolt's work", plan.8): queued while
sluice's submission has no outcome recorded, rejected once sluice refused it for the bolt's own content, landing again
once it is submitted after a rejection, each a state of its own (plan.landing_phase); what a line says of each
(plan.phase_said); and what work joining the bolt is refused for (plan.landing_hold). That crew bolts, the rail and the
board show them is test_rail's and test_board's; that the plan writes and crew fix refuse by them, test_cross's and
test_fix's."""
import plan

H1, H2 = "a" * 40, "b" * 40
CONFLICT = "#412 conflict: sluice could not merge bolt/x into main: README.md"


def submit(bolt="x", **f):
    return dict(Act="bolt.submit", On=[f"bolt/{bolt}"], **f)


QUEUED = [submit(Outcome="queued", Submission="412", Head=H1, Base="c" * 40)]
REJECTED = QUEUED + [submit(Refused=CONFLICT, Submission="412", Head=H1)]
AGAIN = REJECTED + [submit(Outcome="queued", Submission="415", Head=H2)]


class TestLandingPhase:
    def test_queued_until_sluices_outcome_is_recorded(self):
        assert plan.landing_phase(QUEUED, "x") == dict(state="queued", n="412", head=H1)

    def test_rejected_once_sluice_refused_it_for_the_bolts_own_content_with_its_words(self):
        assert plan.landing_phase(REJECTED, "x") == dict(state="rejected", n="412", head=H1, words=CONFLICT)

    def test_landing_again_once_submitted_after_a_rejection_naming_the_rejection(self):
        assert plan.landing_phase(AGAIN, "x") == dict(state="again", n="415", head=H2, rejected=("412", H1))

    def test_rejected_again_after_landing_again_is_rejected_at_its_new_head(self):
        again_refused = AGAIN + [submit(Refused="#415 failed: tests:logic", Submission="415", Head=H2)]
        assert plan.landing_phase(again_refused, "x") == dict(state="rejected", n="415", head=H2, words="#415 failed: tests:logic")

    def test_one_sluice_refused_in_its_answer_is_rejected_with_no_number(self):
        assert plan.landing_phase([submit(Refused="conflict: README.md", Head=H1)], "x") == dict(
            state="rejected", n=None, head=H1, words="conflict: README.md")

    def test_landed_stopped_or_never_submitted_holds_no_state(self):
        assert plan.landing_phase(AGAIN + [submit(Outcome="landed", Submission="415", Head=H2)], "x") is None
        assert plan.landing_phase(QUEUED + [submit(Outcome="stopped", Submission="412", Head=H1, Why="sluice itself failed")], "x") is None
        assert plan.landing_phase([], "x") is None
        assert plan.landing_phase(QUEUED, "y") is None

    def test_a_wait_sluice_failed_on_leaves_the_submission_queued_for_a_later_read(self):
        """landing_ended's stop with no Submission: the outcome is left to a later read (landing_pending)."""
        stopped = QUEUED + [submit(Outcome="stopped", Head=H1, Why="sluice itself failed each of the 3 times")]
        assert plan.landing_phase(stopped, "x")["state"] == "queued"

    def test_crews_own_refusal_before_submitting_leaves_the_rejection_standing(self):
        """A refusal of crew's before anything was submitted names no head, so the bolt's landing stays rejected."""
        assert plan.landing_phase(REJECTED + [submit(Refused="bolt/x was not submitted: main could not be read")], "x")["state"] == "rejected"

    def test_landing_again_names_the_newest_rejection_before_it(self):
        twice = AGAIN + [submit(Refused="#415 failed", Submission="415", Head=H2), submit(Outcome="queued", Submission="420", Head="d" * 40)]
        assert plan.landing_phase(twice, "x")["rejected"] == ("415", H2)

    def test_each_bolt_submitted_has_its_state(self):
        both = QUEUED + [submit(bolt="y", Refused="conflict", Head=H2)] + [submit(bolt="z", Outcome="landed", Submission="9", Head=H1)]
        assert {b: p["state"] for b, p in plan.landing_phases(both).items()} == {"x": "queued", "y": "rejected"}


class TestPhaseSaid:
    def test_queued_names_the_number_unless_sluices_queue_shows_it_standing(self):
        phase = plan.landing_phase(QUEUED, "x")
        assert plan.phase_said(phase, H1) == "landing queued as #412"
        assert plan.phase_said(phase, H1, live=True) is None

    def test_landing_again_names_the_rejection_it_follows(self):
        phase = plan.landing_phase(AGAIN, "x")
        assert plan.phase_said(phase, H2) == "landing again as #415, after #412 was rejected"
        assert plan.phase_said(phase, H2, live=True) == "landing again, after #412 was rejected"

    def test_rejected_says_the_bolt_is_open_for_work_with_sluices_words_while_at_that_head(self):
        phase = plan.landing_phase(REJECTED, "x")
        assert plan.phase_said(phase, H1) == f"landing #412 rejected at aaaaaaa, open for work: {CONFLICT}"
        assert plan.phase_said(phase, H1[:7]) == f"landing #412 rejected at aaaaaaa, open for work: {CONFLICT}"
        assert plan.phase_said(phase, H2) is None  # a fix moved its head: the rejection holds nothing
        assert plan.phase_said(plan.landing_phase([submit(Refused="conflict", Head=H1)], "x"), H1) == (
            "landing rejected at aaaaaaa, open for work: conflict")

    def test_no_landing_says_nothing(self):
        assert plan.phase_said(None, H1) is None


class TestLandingHold:
    def test_work_joining_a_bolt_whose_landing_is_queued_is_refused_naming_it(self):
        assert plan.landing_hold(plan.landing_phase(QUEUED, "x"), "x", "unit b") == (
            "bolt x has its landing queued on main as #412, so unit b does not join it until sluice decides: sluice lands the "
            "head it was given, and work merged into the bolt meanwhile would be left out of main; put it on another bolt, or "
            "into this one once sluice has rejected the landing")

    def test_work_joining_a_bolt_landing_again_is_refused_naming_both(self):
        assert plan.landing_hold(plan.landing_phase(AGAIN, "x"), "x", "fix x--logic").startswith(
            "bolt x is landing again as #415, after #412 was rejected, so fix x--logic does not join it until sluice decides")

    def test_a_rejected_landing_or_none_holds_nothing(self):
        assert plan.landing_hold(plan.landing_phase(REJECTED, "x"), "x", "unit b") is None
        assert plan.landing_hold(None, "x", "unit b") is None

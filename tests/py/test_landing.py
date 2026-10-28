"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host, read from main now (plan.18), and of
sluice's own record of the submission when sluice itself failed with the bolt not on main (plan.submission_of); what
plan.deleted_said makes of sluice's delete of the bolt's branch at crew bolt land (plan.19); and its landing card,
raised by crew once the bolt reads proven, held by a fix and closed at the landing (record 0031 §1)."""
import argparse
import base64
import contextlib
import datetime
import io
import json
import pathlib

import pytest

from facts import START, at

import plan

OLD, NEW, TIP = "a" * 40, "b" * 40, "c" * 40
SIGNAL = "sluice: releasing try/abc1234: its command failed"
SLUICE = pathlib.Path(__file__).parent / "sluice-0.36.4"
STATUS = json.loads((SLUICE / "status-all.json").read_text())
CONFLICT = STATUS["submissions"][0]  # #137, in conflict, as sluice 0.36.4 recorded it
RAN = json.loads((SLUICE / "wait-failed-ran.json").read_text())  # #214, tests:logic ran and failed
NOT_RUN = json.loads((SLUICE / "wait-failed-not-run.json").read_text())  # #216, every check left without a result
ENGINE = "the Dagger engine did not answer: dial unix /run/dagger/engine.sock: connect: connection refused"


def said(rc, new=NEW, kept="''", why="''", level="yes", sluice="", github=None, fetched="ok", held="yes", tip=TIP):
    """What LANDING prints after sluice's outcome: the kit's mains after a fresh fetch (MAINS), whether each holds the
    tip that was submitted, then its assignments, sluice's last line base64. With github, a kit with an origin whose
    GitHub main is then at github, judged by HELD_GITHUB, the host's own main at new; else one with none, its own main at
    new, judged by HELD_OWN."""
    mains = (f"ORIGIN=yes\nFETCHED={fetched}\nGITHUB={github}\nOWN={new}\nHELD_GITHUB={held}\nHELD_OWN=no\n" if github else
             f"ORIGIN=no\nGITHUB=-\nOWN={new}\nHELD_GITHUB=-\nHELD_OWN={held}\n")
    words = base64.b64encode(sluice.encode()).decode()
    return mains + f"RC={rc} TIP={tip} OLD={OLD} KEPT={kept} WHY={why} LEVEL={level} SAID={words}\n"


def landing(out, marked="", name="k", sub=None, again=0, doc=None):
    return plan.landing_said("b", name, "h", out, OLD, marked, sub, again, doc=doc)


AGAIN_WORDS = plan.submit_again("b")


def test_a_landing_says_where_main_is_and_what_comes_next():
    assert landing(said(0), name="switchboard-kit") == (
        True, "bolt/b landed on switchboard-kit's main at bbbbbbb: now crew bolt land b.")


def test_a_main_checkout_not_brought_level_is_named_with_the_command():
    landed, words = landing(said(0, level="'git read-tree could not bring it level'"))
    assert landed and words.endswith("k's main checkout was not brought level (git read-tree could not bring it level): "
                                     "git read-tree -m -u aaaaaaa main there.")


def test_a_bolt_branch_with_no_mark_of_crews_is_named_and_lands_all_the_same():
    """bolt-teams "A landing leaves only what main lacks" (record 0003, read.4): the landing marks the bolt's branch
    landed only when it carries crew's mark, and says when it could not; a landing is a landing either way."""
    assert landing(said(0), "no") == (
        True, "bolt/b landed on k's main at bbbbbbb: now crew bolt land b. crew could not mark bolt/b landed: its branch "
              "carries no mark of crew's.")
    assert landing(said(0), "git config could not set it")[1].endswith(
        "crew could not mark bolt/b landed: git config could not set it.")
    assert landing(said(0), "yes") == landing(said(0))


def test_a_landing_that_did_not_land_says_nothing_of_the_mark():
    assert "mark" not in landing(said(2, new=OLD))[1]
    assert "mark" not in landing(said(0))[1]


def test_a_conflict_lands_nothing_and_is_the_bolts_to_take():
    landed, words = landing(said(2, new=OLD), doc=CONFLICT)
    assert not landed
    assert words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
    assert "the team takes main into it by a submission to the bolt" in words


def test_checks_that_failed_land_nothing():
    assert landing(said(1, new=OLD), doc=RAN)[1].startswith("bolt/b did not land: main's checks failed on it")


def test_a_worktree_git_could_not_remove_is_named_with_gits_words_and_goes_with_the_bolt():
    """read.1, plan.19: the landing's place git could not remove is said by name, in git's words, never kept silently,
    and crew bolt land sweeps it with the bolt or names it there."""
    why = "\"fatal: '/k/places/land-b' contains modified or untracked files, use --force to delete it\""
    for rc, new in ((2, OLD), (0, NEW)):
        assert landing(said(rc, new=new, kept="/k/places/land-b", why=why))[1].endswith(
            "Its worktree /k/places/land-b is kept, git refusing to remove it: fatal: '/k/places/land-b' contains modified "
            "or untracked files, use --force to delete it. crew bolt land removes it with the bolt, or names it with why it stays.")
    assert landing(said(0))[1].endswith("now crew bolt land b.")


def test_words_crew_cannot_read_land_nothing():
    assert landing("wt: command not found\n") == (
        False, "crew can't read what the submission of bolt/b to k's main came to: wt: command not found." + AGAIN_WORDS)
    for out in (said(0).replace("HELD_OWN=yes", "HELD_OWN=maybe"), said(0).replace("SAID=", "SAID=%%%"),
                f"RC=0 OLD={OLD} NEW={NEW} KEPT='' LEVEL=yes MARKED=yes\n"):
        assert landing(out)[1].startswith("crew can't read what the submission of bolt/b to k's main came to: "), out


class TestARefusedLandingIsRecordedInSluicesWords:
    """rail-cards "A refused landing is held on its row", crew-rail "A refused landing", Decision 6: what a bolt.submit
    that did not land is recorded refused with, which its row, its rail line and the card's close say, is sluice's own
    last line when it exited non-zero and said any; else crew's for why and where main is. Never what crew tells ops
    in its terminal, "sluice's words above" pointing at nothing on a card, nor the worktree it kept."""

    def recorded(self, out, doc=CONFLICT):
        return plan.landing_said("b", "k", "h", out, OLD, recorded=True, doc=doc)

    def test_sluices_words_are_recorded(self):
        conflict = "sluice: bolt/b conflicts with main"
        for out in (said(2, new=OLD, sluice=conflict), said(2, new=OLD, github=OLD, held="no", level="''", sluice=conflict),
                    said(2, new=OLD, sluice=conflict, kept="/k/places/land-b", why="busy")):
            assert self.recorded(out) == (False, conflict), out
        assert self.recorded(said(1, new=OLD, sluice="sluice: bolt/b failed main's checks: t-cards"), RAN)[1] == (
            "sluice: bolt/b failed main's checks: t-cards")

    def test_crews_words_when_sluice_said_nothing(self):
        assert self.recorded(said(1, new=OLD), RAN) == (False, "bolt/b did not land: main's checks failed on it, and main is where it was.")
        assert self.recorded(said(2, new=OLD, kept="/k/places/land-b", why="busy"))[1] == (
            "bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")

    def test_crews_words_when_sluice_exited_0(self):
        """sluice's words of a submission it ended well are no refusal: main moving without the bolt is a stop, in
        crew's words, or in sluice's record's when it gave one."""
        assert self.recorded(said(0, held="no", sluice="sluice: #7 bolt/b landed on main"), None)[1] == (
            "the submission exited 0; k's main moved to bbbbbbb without it")
        assert self.recorded(said(0, held="no"), STATUS["submissions"][2])[1] == "sluice's record has #153 landed"

    def test_crews_words_when_it_cant_tell(self):
        assert self.recorded(said(3, new=OLD, github="-", level="''", sluice=SIGNAL, kept="/k/places/land-b"))[1] == (
            "crew can't tell whether bolt/b landed on k's main: k's GitHub has no main, fetched on h; the submission exited 3.")

    def test_a_landing_is_said_as_ever(self):
        assert self.recorded(said(0)) == landing(said(0))


def test_the_anchor_is_detached_and_the_landing_says_nothing_of_levelling_it():
    """bolt-teams "The anchor is detached" (plan.18): the fleet's timer moves a detached main checkout, so a landing
    neither levels it nor says anything of it."""
    landed, words = landing(said(0, level="detached"))
    assert landed and "level" not in words and "read-tree" not in words


class TestALandingIsReadFromGitHubsMain:
    """bolt-teams "A landing is read from GitHub's main" (plan.18, plan.16, code.7): whether the bolt landed is read
    from main now after sluice's outcome, moved from where it was before and holding the bolt's tip, whatever sluice
    exited; sluice's exit only shapes the words."""

    def test_sluice_fails_after_its_push(self):
        """"sluice fails after its push": swancloud's a-landed-places-preview-is-released landed on GitHub's main at
        bf8ae5d, and crew bolt submit said "did not land: the submission exited 3, and main is where it was", having read
        only the host's own main, which sluice had not moved, and trusted only an exit of 0 (signal
        2026-10-22-swancloud-ops-b237b51b/01)."""
        assert landing(said(3, new=OLD, github=NEW, level="''", sluice=SIGNAL), "yes") == (
            True, f"bolt/b landed on k's main at bbbbbbb: now crew bolt land b. sluice exited 3 after its push: {SIGNAL}. "
                  "That is sluice's to report, apart from the landing.")

    def test_sluice_saying_nothing_after_its_push_is_named_so(self):
        assert "sluice exited 3 after its push: sluice said nothing." in landing(said(3, new=OLD, github=NEW, level="''"))[1]

    def test_sluice_lands_it_and_exits_0(self):
        """"sluice lands it and exits 0": the words name no exit."""
        assert landing(said(0, github=NEW), "yes") == (True, "bolt/b landed on k's main at bbbbbbb: now crew bolt land b.")

    def test_the_host_lagging_github_levels_nothing_and_says_nothing_of_it(self):
        """The host's own main unmoved by sluice has nothing to level (LEVEL empty), and the landing says nothing of it."""
        words = landing(said(0, new=OLD, github=NEW, level="''"))[1]
        assert "level" not in words and "read-tree" not in words

    @pytest.mark.parametrize("rc, doc, why", [(1, "ran", "main's checks failed on it"), (2, "conflict", "sluice refused it or found a conflict")])
    def test_githubs_main_did_not_move(self, rc, doc, why):
        """"GitHub's main did not move": the bolt did not land and main is where it was, whatever sluice exited but 3,
        sluice itself failing, which its record of the submission decides (TestSluiceItselfFailed); the bolt's to fix
        when the record the wait printed says so (landing_blame)."""
        landed, words = landing(said(rc, new=OLD, github=OLD, held="no", level="''"), doc=dict(ran=RAN, conflict=CONFLICT)[doc])
        assert not landed and words.startswith(f"bolt/b did not land: {why}, and main is where it was. Tell the bolt's conductor")

    @pytest.mark.parametrize("rc, doc, why", [
        (0, None, "the submission exited 0"), (1, None, "the submission exited 1, and sluice gave no record of it crew reads"),
        (1, "not run", f"check:dagger could not run: {ENGINE}; check:image could not run: {ENGINE}"),
        (2, None, "the submission exited 2, and sluice gave no record of it crew reads"),
        (4, "withdrawn", "sluice's record has #148 withdrawn"), (64, None, "sluice could not read its command line"),
        (130, None, "the submission was stopped"), (5, None, "the submission exited 5, and sluice gave no record of it crew reads")])
    def test_githubs_main_did_not_move_and_nothing_of_the_bolts_stopped_it(self, rc, doc, why):
        """bolt-teams "A landing stopped by sluice or its host is recorded stopped": any end not the bolt's by sluice's
        record says nothing of the bolt's stopped it, and tells ops to submit it again once that is cleared."""
        doc = {"not run": NOT_RUN, "withdrawn": STATUS["submissions"][1]}.get(doc)
        landed, words = landing(said(rc, new=OLD, github=OLD, held="no", level="''"), doc=doc)
        assert (landed, words) == (False, f"bolt/b did not land, and nothing of the bolt's stopped it: {why}, and main is where it "
                                          f"was.{AGAIN_WORDS}")

    def test_main_moved_but_not_with_the_bolt(self):
        """"Main moved, but not with the bolt": another landing moved it; where main is now is named, and not that it
        is where it was."""
        landed, words = landing(said(2, new=OLD, github=NEW, held="no", level="''"), doc=CONFLICT)
        assert not landed
        assert words.startswith("bolt/b did not land: sluice refused it or found a conflict; k's main moved to bbbbbbb without it. "
                                "Tell the bolt's conductor why")
        assert "main is where it was" not in words

    def test_github_cant_be_read_after_the_submission(self):
        """"GitHub can't be read after the submission": crew can't tell, naming the fetch's words and sluice's exit,
        and says neither that the bolt landed nor that main is where it was."""
        fetched = "fatal: unable to access 'https://github.com/o/k/': Could not resolve host: github.com"
        landed, words = landing(said(3, new=OLD, github=OLD, fetched=fetched, level="''"))
        assert (landed, words) == (False, f"crew can't tell whether bolt/b landed on k's main: cannot fetch k from GitHub on h, "
                                          f"so cannot read its main now: {fetched}; the submission exited 3.{AGAIN_WORDS}")
        assert landing(said(3, new=OLD, github="-", level="''"))[1] == (
            "crew can't tell whether bolt/b landed on k's main: k's GitHub has no main, fetched on h; the submission exited 3."
            + AGAIN_WORDS)

    def test_a_kit_with_no_origin_is_judged_by_its_own_main(self):
        """"A kit with no origin": its own main, before and after, and whether it holds the bolt's tip."""
        assert landing(said(0))[0]
        assert landing(said(3, sluice=SIGNAL))[1].startswith(
            f"bolt/b landed on k's main at bbbbbbb: now crew bolt land b. sluice exited 3 after its push: {SIGNAL}.")
        assert landing(said(0, held="no"))[1].startswith(
            "bolt/b did not land, and nothing of the bolt's stopped it: the submission exited 0; k's main moved to bbbbbbb without it.")


HEADS = {s["state"]: s["head"] for s in STATUS["submissions"]}  # one recorded submission in each state sluice held
# sluice itself failing under --json (main.rs, told.rs): its error document on standard output, its message the failure,
# and the same failure on standard error, after "sluice: "
FAILED = "a round of main failed: its lock could not be taken"
FAILED_DOC = json.dumps({"error": {"kind": "internal", "message": FAILED, "next": []}})


def listing(*subs):
    """What SUBMISSIONS prints when sluice 0.36.4 lists main's submissions: the recorded listing, with subs added."""
    return json.dumps(dict(STATUS, submissions=STATUS["submissions"] + list(subs)))


NONE_YET = json.dumps(dict(STATUS, submissions=[]))  # sluice's listing of a main it has recorded no submission to
# sluice 0.51.3's overview of a repository with nothing standing in its queue (tests/py/sluice-0.51.3/), as QUEUE
# prints it before a landing.
STANDING = json.loads((pathlib.Path(__file__).parent / "sluice-0.51.3" / "overview-standing.json").read_text())
EMPTY_QUEUE = json.dumps(dict(STANDING, branches=[dict(b, submissions=[]) for b in STANDING["branches"]]))


# sluice 0.36.4's answer to a landing's submission to a main that takes pull requests, as submit_pull prints it under
# --no-wait --json once intake has queued it (lib.rs, serde_json's keys in their order; pulls.rs queued), and the
# submission intake made for it from the pull request's place, pull/113, at the tip submitted: the recorded #153, made
# from pull/106, as it stood queued.
PULLED = '{"branch":"main","pull_request":113,"state":"queued: next on main"}'
MADE = dict({k: v for k, v in STATUS["submissions"][2].items() if k not in ("landed_as", "result", "tested")}, id=170, head=TIP,
            state="queued", **{"from": dict(STATUS["submissions"][2]["from"], head="bolt/b", worktree="pull/113")})
# The signal's case (2026-10-23-madswan-ops-5023c5ba/01 on madswan/main): the pull request's submission sluice blamed
# on the tip before the landing, #171, and sluice 0.36.4's answer to the landing's --no-wait submission of that tip, its
# intake not having read the pull request marked ready since: #171's own record, pretty, its exit 1, nothing queued
# (lib.rs submit_pull, Reached::Before, report; pulls.rs consider), SUBMIT's ID read from it.
SENT_BACK = dict(MADE, id=171, state="failed")
SENT_BACK_ANSWER = base64.b64encode(json.dumps(SENT_BACK, indent=2).encode()).decode()


class TestAPullRequestsSubmission:
    """A landing sluice queued through a pull request is waited on as the submission sluice made for it (plan.16):
    found in sluice's record from the pull request's place at the tip that was submitted (plan.submission_of with the
    pull request), its outcome read from the state of the record sluice's wait prints (plan.wait_outcome)."""

    def test_the_submission_is_the_last_sluice_made_from_the_pull_requests_place_at_the_tip(self):
        assert plan.submission_of(TIP, 0, listing(MADE), "", 113) == {"id": 170, "state": "queued"}
        assert plan.submission_of(TIP, 0, listing(MADE, dict(MADE, id=175, state="testing")), "", 113) == {"id": 175, "state": "testing"}
        for other in (dict(MADE, head="d" * 40), dict(MADE, **{"from": dict(MADE["from"], worktree="pull/99")})):
            assert plan.submission_of(TIP, 0, listing(other), "", 113) == (
                "sluice records no submission of ccccccc to main from pull request #113")
        assert plan.submission_of(TIP, 0, listing(dict(MADE, **{"from": dict(MADE["from"], worktree="pull/99")})), "") == (
            {"id": 170, "state": "queued"})  # with no pull request, any submission of the tip

    def test_the_submission_is_only_ever_one_made_since_the_landing_began(self):
        """Not the pull request's last, nor any older one: only one newer than the last sluice recorded before."""
        assert plan.submission_of(TIP, 0, listing(SENT_BACK), "", 113, 171) == (
            "sluice records no submission of ccccccc to main from pull request #113 newer than #171")
        assert plan.submission_of(TIP, 0, listing(SENT_BACK, dict(MADE, id=172)), "", 113, 171) == {"id": 172, "state": "queued"}
        assert plan.submission_of(TIP, 0, listing(dict(SENT_BACK, head=TIP)), "", None, 171) == (
            "sluice records no submission of ccccccc to main newer than #171")
        assert plan.submission_of(TIP, 0, listing(SENT_BACK), "", 113) == {"id": 171, "state": "failed"}

    def test_an_answer_naming_a_submission_sluice_recorded_before_the_landing_is_not_its_own(self):
        f = dict(RC="1", TIP=TIP, OLD=OLD, ID="171", PULL="", ANSWER=SENT_BACK_ANSWER, SAID="")
        assert plan.answered_before(f, 171) == {"id": 171, "state": "failed", "pull": "113"}
        assert plan.answered_before(f, 175) == {"id": 171, "state": "failed", "pull": "113"}
        assert plan.answered_before(f, 170) is None  # one sluice made since
        assert plan.answered_before(dict(f, RC="0", ID="", PULL="113"), 171) is None  # no submission named
        plain = base64.b64encode(b'{"id":171,"branch":"main","ahead":[]}').decode()
        assert plan.answered_before(dict(f, ANSWER=plain), 180) == {"id": 171, "state": None, "pull": None}

    @pytest.mark.parametrize("state, rc", [("landed", "0"), ("failed", "1"), ("conflict", "2"), ("withdrawn", "4")])
    def test_the_outcome_is_the_state_the_waits_record_has_it_out_in(self, state, rc):
        """With the record itself, which landing_blame judges."""
        doc = dict(MADE, state=state)
        assert plan.wait_outcome(170, 0 if state == "landed" else 1, json.dumps(doc)) == (rc, doc)

    def test_a_wait_that_printed_no_record_of_it_out_is_its_exit(self):
        assert plan.wait_outcome(170, 130, json.dumps(MADE)) == ("130", MADE)
        assert plan.wait_outcome(170, 3, json.dumps({"error": {"message": "its lock could not be taken"}})) == ("3", None)
        assert plan.wait_outcome(170, 0, json.dumps(dict(MADE, id=171, state="conflict"))) == ("0", None)
        assert plan.wait_outcome(170, 3, "") == ("3", None)


class TestSluicesVerdict:
    """What a refused landing holds its row with is sluice's verdict on the submission (plan.verdict_of), read from the
    record it prints under --json, in the words its own report gives it (sluice 0.36.4 lib.rs report, detail), a
    conflict's paths among them; never what it says on standard error, only what its rounds did beside and its own
    warnings (exec.rs tell_abandoned, main.rs), which crew says beside it (plan.beside_of)."""
    RECORDED = {s["state"]: s for s in STATUS["submissions"]}

    def test_a_conflict_names_its_paths_and_what_it_conflicts_with(self):
        assert plan.verdict_of(self.RECORDED["conflict"]) == (
            "#137 conflict: README.md, plugin/bin/crew, plugin/lib/plan.py, plugin/skills/crew/SKILL.md")
        met = {"paths": ["plugin/lib/plan.py"], "with": [{"id": 12, "from": {"agent": "crw-1-unit-2", "head": "unit/u", "worktree": "/c/places/u"}}]}
        assert plan.verdict_of(dict(self.RECORDED["conflict"], conflict=met)) == (
            "#137 conflict: plugin/lib/plan.py; conflicts with #12 (crw-1-unit-2, /c/places/u)")
        assert plan.verdict_of(dict(self.RECORDED["conflict"], conflict={"paths": "README.md", "with": None})) == "#137 conflict"

    def test_a_failure_names_its_checks_and_the_combination_it_failed_on(self):
        failed = dict(MADE, id=171, state="failed", result="failed", tested={"combination": "e" * 40, "on": OLD, "submissions": [171]},
                      failed=[{"task": "tests:t-cards", "hash": "h1", "log": "/k/logs/t-cards"},
                              {"task": "tests:logic", "hash": "h2", "flaky": {"other": {}}, "system": "aarch64-darwin"},
                              {"task": "tests:mod", "not_run": "no claude on its path"}])
        assert plan.verdict_of(failed) == (
            "#171 failed: tests:t-cards, tests:logic (aarch64-darwin) (flaky); not run: tests:mod on eeeeeee")
        assert plan.verdict_of(dict(failed, failed=[], result="timed out")) == "#171 timed out on eeeeeee"
        assert plan.verdict_of({k: v for k, v in failed.items() if k not in ("failed", "result", "tested")}) == "#171 failed"

    def test_a_withdrawal_and_a_landing_are_named_as_sluice_records_them(self):
        assert plan.verdict_of(self.RECORDED["withdrawn"]) == "#148 withdrawn by swancloud-ops at 2026-10-23T03:49:32Z"
        assert plan.verdict_of(self.RECORDED["landed"]) == "#153 landed as 52c7427"

    def test_a_submission_still_standing_or_a_document_crew_does_not_read_has_none(self):
        for doc in (self.RECORDED["testing"], dict(MADE, state="parked"), {"id": 7, "state": "conflict"}, None, [], "conflict"):
            assert plan.verdict_of(doc) == "", doc

    def test_sluices_error_document_is_its_message(self):
        assert plan.verdict_of(json.loads(FAILED_DOC)) == FAILED
        assert plan.verdict_of({"error": {"kind": "refused"}}) == ""

    def test_the_verdict_is_read_from_what_sluice_printed_on_standard_output(self):
        conflict = self.RECORDED["conflict"]
        assert plan.verdict_printed(json.dumps(conflict, indent=2), 137).startswith("#137 conflict: README.md")
        assert plan.verdict_printed(json.dumps(conflict), 138) == ""  # another submission's record is not its verdict
        assert plan.verdict_printed(json.dumps(conflict)).startswith("#137 conflict")  # SUBMIT's answer, any submission
        assert plan.verdict_printed(listing(), 148) == "#148 withdrawn by swancloud-ops at 2026-10-23T03:49:32Z"
        assert plan.verdict_printed(listing(), 999) == "" and plan.verdict_printed(listing()) == ""
        assert plan.verdict_printed(FAILED_DOC, 7) == FAILED
        for out in ("", "{}", "not json", PULLED):
            assert plan.verdict_printed(out, 7) == "", out

    def test_what_sluice_said_on_standard_error_is_beside_its_verdict_never_it(self):
        tidying = "could not release /k/places/old-unit, whose worktree no longer exists: its release command failed"
        assert plan.beside_of(f"\n{tidying}\n  sluice: warning: telemetry off: no endpoint \n", "#7 conflict: README.md") == (
            f"{tidying}; sluice: warning: telemetry off: no endpoint")
        assert plan.beside_of(f"{tidying}\nsluice: {FAILED}\n", FAILED) == tidying  # sluice's failure is its verdict
        assert plan.beside_of("", "#7 conflict") == "" and plan.beside_of(None) == ""


class TestSluiceItselfFailed:
    """A landing whose submission found sluice itself failing, exiting 3, with the bolt's tip not on main now, is read
    from sluice's own record of the submission (plan.16, plan.18): while it stands queued or under test crew says so
    and waits on it again, and it did not land only when the record has it out, blamed, in conflict or withdrawn."""
    TESTING = said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=HEADS["testing"])

    def test_the_submission_is_read_from_sluices_record_only_when_sluice_failed_and_main_lacks_the_tip(self):
        assert plan.sluice_failed(self.TESTING, OLD) == HEADS["testing"]
        assert plan.sluice_failed(said(3, new=OLD, github=NEW, level="''", sluice=SIGNAL), OLD) is None  # landed all the same
        assert plan.sluice_failed(said(2, new=OLD, github=OLD, held="no"), OLD) is None
        assert plan.sluice_failed(said(3, new=OLD, github=OLD, held="no", fetched="fatal: no network"), OLD) is None
        assert plan.sluice_failed("wt: command not found\n", OLD) is None

    def test_sluices_record_of_the_submission_is_the_last_of_its_tip(self):
        """read.2, against sluice 0.36.4's own listing (tests/py/sluice-0.36.4/status-all.json)."""
        out = (pathlib.Path(__file__).parent / "sluice-0.36.4" / "status-all.json").read_text()
        assert {state: plan.submission_of(head, 0, out, "") for state, head in HEADS.items()} == {
            "conflict": {"id": 137, "state": "conflict", "conflict": CONFLICT["conflict"]}, "withdrawn": {"id": 148, "state": "withdrawn"},
            "landed": {"id": 153, "state": "landed", "result": "passed"}, "testing": {"id": 160, "state": "testing"}}
        blamed = dict(RAN, id=171, head=TIP)
        assert plan.submission_of(TIP, 0, listing(blamed), "") == {"id": 171, "state": "failed", "result": "failed", "failed": RAN["failed"]}
        again = dict(STATUS["submissions"][1], id=170, state="queued")
        assert plan.submission_of(HEADS["withdrawn"], 0, listing(again), "") == {"id": 170, "state": "queued"}

    def test_a_record_crew_has_none_of_is_said_why(self):
        assert plan.submission_of(TIP, 0, listing(), "") == "sluice records no submission of ccccccc to main"
        assert plan.submission_of(TIP, 3, json.dumps({"error": {"message": "its records are locked"}}), "") == (
            "sluice status main --all exited 3: its records are locked")
        assert plan.submission_of(TIP, 255, "", "ssh: connect to host box port 22: timed out\n") == (
            "sluice status main --all exited 255: ssh: connect to host box port 22: timed out")
        assert plan.submission_of(TIP, 0, "nope", "").startswith("sluice status main --all printed no listing of submissions crew reads: nope")
        odd = dict(STATUS["submissions"][0], id=171, head=TIP, state="parked")
        assert plan.submission_of(TIP, 0, listing(odd), "") == 'sluice records #171 in a state crew does not read: "parked"'

    @pytest.mark.parametrize("state, words", [("queued", "queued"), ("waiting", "waiting on a submission it comes after"),
                                              ("testing", "under test"), ("passed", "passed, to land next"), ("landing", "landing")])
    def test_a_submission_its_record_has_standing_is_waited_on_again(self, state, words):
        sub = {"id": 160, "state": state}
        assert landing(self.TESTING, sub=sub) == (False, (
            f"sluice itself failed ({FAILED}), but its record has bolt/b's submission, #160, {words} on k's main, which does "
            "not hold it yet: crew waits on it again (sluice wait 160)."))
        assert plan.wait_again(sub, 0) == 160 and plan.wait_again(sub, plan.AGAIN - 1) == 160

    @pytest.mark.parametrize("sub, words", [(dict(id=160, state="failed", result="failed", failed=RAN["failed"]), "blamed for a check that failed"),
                                            (dict(id=160, state="conflict"), "in conflict")])
    def test_it_did_not_land_for_its_own_content_only_when_its_record_has_it_blamed(self, sub, words):
        landed, said_ = landing(self.TESTING, sub=sub)
        assert not landed and said_.startswith(f"bolt/b did not land: sluice itself failed, and its record has #160 {words}, and "
                                               "main is where it was. Tell the bolt's conductor why")
        assert plan.wait_again(sub, 0) is None

    @pytest.mark.parametrize("sub, words", [
        (dict(id=160, state="failed", result="failed", failed=NOT_RUN["failed"]), f"check:dagger could not run: {ENGINE}; check:image could not run: {ENGINE}"),
        (dict(id=160, state="failed"), "every required check was left without a result"),
        (dict(id=160, state="withdrawn"), "sluice's record has #160 withdrawn")])
    def test_any_other_end_its_record_has_is_a_stop(self, sub, words):
        """bolt-teams "sluice itself fails": out, but for nothing of the bolt's, it is a stop in sluice's own failure and
        the record's words."""
        assert landing(self.TESTING, sub=sub) == (False, (
            f"bolt/b did not land, and nothing of the bolt's stopped it: sluice itself failed ({FAILED}), and {words}, and main is "
            f"where it was.{AGAIN_WORDS}"))
        assert plan.landing_said("b", "k", "h", self.TESTING, OLD, sub=sub, recorded=True)[1] == f"sluice itself failed ({FAILED}), and {words}"
        assert plan.wait_again(sub, 0) is None

    def test_its_records_verdict_is_what_is_recorded_and_sluices_own_failure_is_not(self):
        """The record's verdict on the submission holds the row, never sluice's own failure on the wait, which ops reads
        beside it (rail-cards "A refused landing is held on its row")."""
        sub = {"id": 137, "state": "conflict", "verdict": "#137 conflict: plugin/lib/plan.py"}
        assert plan.landing_said("b", "k", "h", self.TESTING, OLD, sub=sub, recorded=True) == (False, "#137 conflict: plugin/lib/plan.py")
        assert "sluice's verdict: #137 conflict: plugin/lib/plan.py." in landing(self.TESTING, sub=sub)[1]
        assert plan.landing_said("b", "k", "h", self.TESTING, OLD, sub=dict(sub, verdict=""), recorded=True)[1] == (
            "bolt/b did not land: sluice itself failed, and its record has #137 in conflict, and main is where it was.")
    def test_crew_cant_tell_when_the_record_has_it_landed_has_none_or_cant_be_read(self):
        tip = HEADS["testing"][:7]
        assert landing(self.TESTING, sub={"id": 160, "state": "landed"}) == (False, (
            f"crew can't tell whether bolt/b landed: sluice itself failed ({FAILED}), its record has #160 landed, and k's main "
            f"now, aaaaaaa, does not hold bolt/b's tip {tip}.{AGAIN_WORDS}"))
        assert landing(self.TESTING, sub=f"sluice records no submission of {tip} to main") == (False, (
            f"crew can't tell whether bolt/b will land on k's main: sluice itself failed ({FAILED}), k's main now, aaaaaaa, does "
            f"not hold bolt/b's tip {tip}, and sluice records no submission of {tip} to main.{AGAIN_WORDS}"))
        assert landing(self.TESTING)[1].endswith("and crew has not read sluice's record of the submission." + AGAIN_WORDS)
        assert plan.landing_said("b", "k", "h", self.TESTING, OLD, sub=f"sluice records no submission of {tip} to main", recorded=True)[1] == (
            f"sluice itself failed ({FAILED}), and sluice records no submission of {tip} to main")
        for sub in ({"id": 160, "state": "landed"}, "sluice status main --all exited 255", None):
            assert "did not land" not in landing(self.TESTING, sub=sub)[1] and plan.wait_again(sub, 0) is None

    def test_a_submission_still_standing_after_crew_waited_again_each_time_sluice_failed_is_said_so(self):
        sub = {"id": 160, "state": "testing"}
        assert plan.wait_again(sub, plan.AGAIN) is None
        assert landing(self.TESTING, sub=sub, again=plan.AGAIN) == (False, (
            f"crew can't tell whether bolt/b will land on k's main: sluice itself failed again each of the {plan.AGAIN} times "
            f"crew waited on #160, which its record still has under test, and k's main now, aaaaaaa, does not hold bolt/b's tip "
            f"{HEADS['testing'][:7]}.{AGAIN_WORDS}"))
        assert plan.landing_said("b", "k", "h", self.TESTING, OLD, sub=sub, again=plan.AGAIN, recorded=True)[1] == (
            f"sluice itself failed ({FAILED}) each of the {plan.AGAIN} times crew waited on #160, which its record still has under test")


class TestTheBolts:
    """bolt-teams "A landing that did not land is the bolt's only for its own content": judged from sluice 0.36.4's
    own record of the submission alone (plan.landing_blame, tests/py/sluice-0.36.4/wait-failed-*.json), the bolt's for
    a conflict or a check that ran and failed or was cut off; anything else a stop, with words saying what stopped it."""

    def test_a_conflict_is_the_bolts(self):
        assert plan.landing_blame(CONFLICT) == ("bolt", None)

    def test_a_check_that_ran_and_failed_is_the_bolts(self):
        assert plan.landing_blame(RAN) == ("bolt", None)
        one_ran = dict(NOT_RUN, failed=NOT_RUN["failed"] + RAN["failed"])
        assert plan.landing_blame(one_ran) == ("bolt", None)

    def test_a_run_its_time_limit_ended_is_the_bolts(self):
        cut_off = dict(RAN, result="timed out", failed=[{"task": "t-journey-land"}])
        assert plan.landing_blame(cut_off) == ("bolt", None)

    def test_checks_that_could_not_run_are_a_stop_naming_each_and_why(self):
        assert plan.landing_blame(NOT_RUN) == ("stop", f"check:dagger could not run: {ENGINE}; check:image could not run: {ENGINE}")

    def test_checks_left_without_a_result_and_no_reason_are_a_stop(self):
        assert plan.landing_blame(dict(NOT_RUN, failed=[{"task": "tests:logic"}])) == (
            "stop", "every required check was left without a result")
        no_list = {k: v for k, v in NOT_RUN.items() if k != "failed"}
        assert plan.landing_blame(no_list) == ("stop", "every required check was left without a result")

    def test_a_withdrawn_landed_or_standing_record_is_a_stop(self):
        assert plan.landing_blame(STATUS["submissions"][1]) == ("stop", "sluice's record has #148 withdrawn")
        assert plan.landing_blame(STATUS["submissions"][2]) == ("stop", "sluice's record has #153 landed")
        assert plan.landing_blame(STATUS["submissions"][3]) == ("stop", "sluice's record still has #160 under test")

    def test_a_record_crew_cant_read_is_a_stop_saying_so(self):
        assert plan.landing_blame(dict(NOT_RUN, failed="check:dagger")) == (
            "stop", "crew can't read the checks sluice's record of #216 blames: \"check:dagger\"")
        assert plan.landing_blame(dict(NOT_RUN, failed=[{"task": "check:dagger", "hash": 7}]))[0] == "stop"
        assert plan.landing_blame(dict(NOT_RUN, result=["timed out"]))[0] == "stop"
        for doc in (None, {}, {"state": 1}, "failed"):
            assert plan.landing_blame(doc) == ("stop", "crew can't read sluice's record of the submission"), doc
        assert plan.landing_blame(dict(RAN, state="parked")) == (
            "stop", "sluice's record has #214 in a state crew does not read: \"parked\"")


class TestWhatALandingCameTo:
    """bolt-teams "A landing that did not land is the bolt's only for its own content" and "A landing stopped by sluice
    or its host is recorded stopped", Decision 4: landing_end says whether it was stopped, from the record the wait
    printed or sluice answered with (doc) or, once sluice itself failed, its listing's (sub); the bolt's words to ops
    are as ever, sluice's verdict among them, and a stop's tell ops to report it and submit it again once it is cleared,
    with no new word, what sluice said beside its verdict said apart and never recorded."""
    NOT_HELD = said(1, new=OLD, github=OLD, held="no", level="''", sluice=plan.verdict_of(NOT_RUN))

    def end(self, out, **k):
        return plan.landing_end("b", "k", "h", out, OLD, **k)

    def test_a_check_that_ran_is_the_bolts(self):
        verdict = plan.verdict_of(RAN)
        landed, words, kept_as, stopped = self.end(said(1, new=OLD, github=OLD, held="no", level="''", sluice=verdict), doc=RAN)
        assert (landed, kept_as, stopped) == (False, verdict, False)
        assert words.startswith(f"bolt/b did not land: main's checks failed on it, and main is where it was. sluice's verdict: "
                                f"{verdict}. Tell the bolt's conductor why")

    def test_checks_the_host_could_not_run_are_a_stop(self):
        landed, words, kept_as, stopped = self.end(self.NOT_HELD, doc=NOT_RUN)
        cause = f"check:dagger could not run: {ENGINE}; check:image could not run: {ENGINE}"
        assert (landed, kept_as, stopped) == (False, cause, True)
        assert words == (f"bolt/b did not land, and nothing of the bolt's stopped it: {cause}, and main is where it was. Its row keeps "
                         "its box and the user's word stands: report what stopped it, and once it is cleared crew bolt submit b "
                         "submits it again, with no new word.")

    def test_sluice_itself_failing_after_crews_waits_again_is_a_stop(self):
        out = said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=HEADS["testing"])
        _, words, kept_as, stopped = self.end(out, sub={"id": 160, "state": "testing"}, again=plan.AGAIN)
        assert stopped and kept_as.startswith(f"sluice itself failed ({FAILED})") and words.endswith(AGAIN_WORDS)

    def test_a_conflict_sluice_refused_at_once_with_its_record_is_the_bolts(self):
        verdict = plan.verdict_of(CONFLICT)
        out = said(2, new=OLD, github=OLD, held="no", level="''", sluice=verdict)
        f = dict(RC="2", ID="137", ANSWER=base64.b64encode(json.dumps(CONFLICT).encode()).decode())
        assert plan.answer_record(f) == CONFLICT
        assert self.end(out, doc=plan.answer_record(f))[2:] == (verdict, False)

    def test_a_refusal_at_once_with_no_record_is_a_stop_in_sluices_verdict(self):
        """sluice's error document is its verdict (verdict_printed), and what it warned beside it on standard error is
        said to ops apart, never recorded."""
        no_gate = "main has no gate for bolt/b"
        error = base64.b64encode(b'{"error":{"message":"main has no gate for bolt/b"}}').decode()
        assert plan.verdict_printed(base64.b64decode(error).decode()) == no_gate
        out = said(2, new=OLD, github=OLD, held="no", level="''", sluice=no_gate)
        assert plan.answer_record(dict(RC="2", ID="", ANSWER=error)) is None
        assert plan.answer_record(dict(RC="2", ID="7", ANSWER=base64.b64encode(json.dumps(CONFLICT).encode()).decode())) is None
        warned = "sluice: warning: branch protection not installed: no hooks directory"
        landed, words, kept_as, stopped = self.end(out, beside=warned)
        assert (landed, kept_as, stopped) == (False, no_gate, True)
        assert words == (f"bolt/b did not land, and nothing of the bolt's stopped it: {no_gate}, and main is where it was.{AGAIN_WORDS}"
                         f" Beside its verdict, and not why it did not land, sluice said: {warned}.")

    def test_a_landing_is_neither(self):
        assert self.end(said(0))[::3] == (True, False)


def ran_as(code, out="", err=""):
    return type("R", (), {"returncode": code, "stdout": out, "stderr": err})()


QUEUED = ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID=7 PULL= ANSWER= SAID={base64.b64encode(b'sluice: queued #7').decode()} LEVEL=\n", "sluice: queued #7\n")


class TestTheSubmission:
    """crew bolt submit <bolt>... (plan.16, plan.18, Decision 6, bolt-teams): each bolt's main now read before its
    submission and its landing pull request made live, the submission queued (SUBMIT), its outcome waited on a call at
    a time (WAIT) and its end read (LANDED), the bolt decided by landing_said against main now, its branch marked only
    once it landed, the landing recorded at main now and the bolt closed as it lands; one that did not land has its pull
    request drafted and is recorded at the head submitted, the rest going on, and the command exits non-zero naming
    it."""
    T = {"name": "swb-1", "machine": "box", "kit": {"name": "k", "main": "/k/main", "dir": "/k", "repo": "o/k"}}
    BEFORE = f"ORIGIN=yes\nFETCHED=ok\nGITHUB={OLD}\nOWN={OLD}\nSUBMISSION_GITHUB=\nSUBMISSION_OWN=\n"

    @pytest.fixture(autouse=True)
    def _state(self, tmp_path):
        self.tmp = tmp_path

    def submit(self, monkeypatch, before, outs, bolts=("b",), teams=None, close=None, said=None, record=None, copies=None, overview=None, statuses=None):
        """bolt_submit of the bolts on mac-studio, held by swb-1 on box unless teams says otherwise, MAIN saying before on
        each host and POLICY said, a policy at main taking no pull requests unless given, the bolt's two copies read
        right after MAIN (LAND_COPIES) answering copies, a bolt that lives on its host unless given, sluice's
        queue read right after them (QUEUE) answering overview, nothing standing unless given, its record of main read right after
        it (SUBMISSIONS) answering record, none of main's submissions unless given, and each
        other script crew runs there answering in turn from outs; the landing's read (crew _landing-read) run on the
        team's host, in this process, its team state under tmp_path and the run record what was recorded, sluice's
        record of the submission (SUBMISSION_STATUS) answering from statuses in turn, else as its last wait did, the
        record it printed or one in the state its exit gives; what ran (the script and its bolt, the submission's number,
        gh's act or the main checkout), what was recorded of each landing's outcome, its entry as sluice queued it kept
        apart (self.queued), and which bolts crew bolt land closed, kept on self."""
        ran_, emitted, closed, argvs = self.ran, self.emitted, self.closed, self.argvs = [], [], [], []
        self.order = []  # the scripts run and the entries recorded, in turn
        statuses, waited = list(statuses or []), [None]
        said, record = said or policy(TAKES_NONE), record or ran_as(0, NONE_YET)
        copies, overview = copies or ran_as(0, "THERE=-\n"), overview or ran_as(0, EMPTY_QUEUE)
        here = ["mac-studio"]
        monkeypatch.setattr(plan, "CONTEXT", {})
        monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
        bolt = lambda s, n: {"Bolt": n, "Team": "swb-1", "Repo": "k"}
        monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, type("P", (), {"bolt": bolt})()))
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: type("P", (), {"bolt": bolt})())
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: (teams or {}).get(b["Bolt"], self.T))
        monkeypatch.setattr(plan, "READ", type("R", (), {"drop_kit": lambda s, h, m: None})())
        monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: ran_.append(("MAIN" if script == plan.MAIN else "POLICY", host))
                            or (before if script == plan.MAIN else said))
        monkeypatch.setattr(plan.crew, "this_host", lambda: here[0])
        monkeypatch.setattr(plan.crew, "crew_argv", lambda fleet, host, *args: ["crew", *args])
        monkeypatch.setattr(plan, "team_state", lambda t: self.tmp / f"{t['name']}-team")
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("o/state", f"{label}/main"))
        monkeypatch.setattr(plan, "fetch", lambda repo, ref, fresh=False: "tip")
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: [
            dict({k: v for k, v in f.items() if v not in (None, "")}, Act=act, On=on, **({"Refused": f["refused"]} if f.get("refused") else {}))
            for act, on, f in emitted])
        names = {plan.SUBMIT: "SUBMIT", plan.WAIT: "WAIT", plan.LANDED: "LANDED", plan.LANDED_MARK: "MARK", plan.PULL: "PULL",
                 plan.PULL_MARK: "PULL_MARK", plan.SUBMISSIONS: "SUBMISSIONS", plan.LAND_COPIES: "COPIES", plan.QUEUE: "OVERVIEW", plan.SUBMISSION_STATUS: "STATUS"}
        at = {plan.SUBMIT: 6, plan.WAIT: 5, plan.LANDED: 6, plan.LANDED_MARK: 5, plan.PULL: 5, plan.PULL_MARK: 6, plan.SUBMISSIONS: 4,
              plan.LAND_COPIES: 5, plan.QUEUE: 4, plan.SUBMISSION_STATUS: 5}

        def status(n):
            """sluice's record of #n: as its last wait printed it, or in the state that wait's exit gives."""
            w = waited[0]
            try:
                doc = json.loads(w.stdout)
            except ValueError:
                doc = None
            if not (isinstance(doc, dict) and doc.get("schema") == plan.SUBMISSION):
                doc = {"schema": plan.SUBMISSION, "id": int(n), "head": TIP,
                       "state": {0: "landed", 1: "failed", 2: "conflict", 4: "withdrawn"}[w.returncode]}
            return ran_as(0, json.dumps(doc), w.stderr)

        def read(host, label, b):  # crew _landing-read on the team's host
            out, err, was = io.StringIO(), io.StringIO(), here[0]
            here[0] = host
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    landed, _ = plan.landing_read({"teams": {}}, label, b)
            finally:
                here[0] = was
            return ran_as(0 if landed else 1, out.getvalue(), err.getvalue())

        def on_machine(fleet, host, argv):
            if argv[:2] == ["crew", "_landing-read"]:
                ran_.append(("READ", argv[3]))
                return read(host, argv[2], argv[3])
            first = argv[2] == plan.SUBMISSIONS and ran_[-1][0] == "OVERVIEW"  # sluice's record before the landing
            argvs.append(argv)
            ran_.append((names[argv[2]], argv[at[argv[2]]]))
            if argv[2] == plan.SUBMISSION_STATUS:
                return statuses.pop(0) if statuses else status(argv[-1])
            got = copies if argv[2] == plan.LAND_COPIES else overview if argv[2] == plan.QUEUE else record if first else outs.pop(0)
            if argv[2] == plan.WAIT:
                waited[0] = got
            return got
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: self.order.append(
            "READ" if argv[0] == "crew" else names[argv[2]]) or on_machine(fleet, host, argv))
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on, **f: self.order.append(f.get("Outcome") or act) or emitted.append((act, on, f)))
        monkeypatch.setattr(plan.record, "who", lambda: "wldn-ops")
        monkeypatch.setattr(plan, "may_write", lambda fleet, key, a: None)
        monkeypatch.setattr(plan, "bolt_land", close or (lambda fleet, a, **k: closed.append(a.bolt)))
        self.handed = []
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None: self.handed.append(kit))
        try:
            plan.bolt_submit({}, argparse.Namespace(bolt=list(bolts), label=None))
        finally:
            self.queued = [e for e in emitted if e[2].get("Outcome") == "queued"]
            emitted[:] = [e for e in emitted if e[2].get("Outcome") != "queued"]
        return ran_, emitted

    def scripts(self):
        return [r for r, _ in self.ran]

    def test_github_cant_be_read_before_the_submission(self, monkeypatch, capsys):
        """"GitHub can't be read before the submission": the bolt is not submitted, said and recorded in the fetch's
        words, no landing worktree made, and the command exits non-zero."""
        before = f"ORIGIN=yes\nFETCHED=fatal: could not read from remote repository\nGITHUB={OLD}\nOWN={OLD}\n"
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, before, [])
        assert self.ran == [("MAIN", "box")]
        (act, on, f), = self.emitted
        assert (act, on) == ("bolt.submit", ["bolt/b"]) and f["refused"].startswith(
            "bolt/b was not submitted: cannot fetch k from GitHub on box, so cannot read its main now")
        assert "b did not land, as said above; none landed" in capsys.readouterr().err

    def test_a_bolt_that_landed_is_marked_recorded_at_main_now_and_closed(self, monkeypatch, capsys):
        """The signal's case through the command (bolt-teams "sluice fails after its push"): sluice's wait exits 3
        after its push, its record has #7 landed, so the read records it, the mark set once crew has read the bolt
        landed, the landing recorded at GitHub's commit, not the host's own, the bolt closed, and sluice's exit and words
        said as what came after."""
        landed = ran_as(0, json.dumps({"schema": plan.SUBMISSION, "id": 7, "head": TIP, "state": "landed", "landed_as": NEW}))
        ran_, emitted = self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(3, "{}", f"{SIGNAL}\n"),
                                                               ran_as(0, said(0, new=OLD, github=NEW, level="''")), ran_as(0, "MARKED=yes\n")],
                                    statuses=[landed, landed])
        assert ran_ == [("MAIN", "box"), ("COPIES", "b"), ("OVERVIEW", "/k/main"), ("SUBMISSIONS", "/k/main"), ("POLICY", "box"), ("SUBMIT", "b"), ("WAIT", "7"),
                        ("STATUS", "7"), ("READ", "b"), ("STATUS", "7"), ("LANDED", "b"), ("MARK", "b")]
        assert emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Outcome": "landed", "Submission": "7",
                                                         "Head": TIP})]
        out = capsys.readouterr().out
        assert "bolt/b submitted to k's main, sluice's #7" in out
        assert out.endswith("bolt/b landed on k's main at bbbbbbb: now crew bolt land b.\n"
                            f"sluice exited 3 after its push: {SIGNAL}. That is sluice's to report, apart from the landing.\n")
        assert self.closed == ["b"]

    def test_the_submission_is_recorded_queued_with_its_number_before_any_wait(self, monkeypatch):
        """bolt-teams "The number is recorded before the wait": once sluice has queued it as #7, the bolt.submit names
        the bolt and its team, Outcome queued, sluice's number, the head submitted and main before, and the kit, before
        crew waits on #7."""
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")])
        (act, on, f), = self.queued
        assert (act, on) == ("bolt.submit", ["bolt/b", "team/swb-1"])
        assert {k: f[k] for k in ("Outcome", "Submission", "Head", "Base", "Repo")} == dict(Outcome="queued", Submission="7", Head=TIP, Base=OLD, Repo="k")
        assert not f.get("frm") and "Chars" not in f
        assert self.order.index("queued") < self.order.index("WAIT")

    def test_a_wait_that_is_still_undecided_is_waited_on_again(self, monkeypatch):
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(5, "{}"), ran_as(5, "{}"), ran_as(0, "{}"),
                                               ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "WAIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]

    def test_a_mark_crew_could_not_set_is_named_in_the_hosts_words_and_the_landing_stands(self, monkeypatch, capsys):
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)),
                                               ran_as(255, "", "ssh: connect to host box port 22: timed out\n")])
        assert ("bolt/b landed on k's main at bbbbbbb: now crew bolt land b. crew could not mark bolt/b landed: ssh: connect to "
                "host box port 22: timed out.") in capsys.readouterr().out
        assert self.emitted and self.closed == ["b"]

    def handed_landed(self):
        """What crew handed LANDED as sluice's verdict, decoded."""
        return base64.b64decode([a for a in self.argvs if a[2] == plan.LANDED][-1][-1]).decode()

    def test_a_bolt_that_did_not_land_is_recorded_in_sluices_verdict_at_its_head_and_the_command_exits_non_zero(self, monkeypatch, capsys):
        """The chore's case (a-holds-reason-is-sluices-verdict-not-a-side-warning): sluice's wait on #7 prints its record
        in conflict, with the paths it names, and says on standard error only what its round did beside, a place it could
        not release (exec.rs tell_abandoned). The record's verdict is handed to LANDED and recorded, which holds the row
        (rail-cards "A refused landing is held on its row"), so the conductor reads a conflict, the bolt's to take main
        in for; the place sluice could not release is said to ops beside it, as not why, and is never recorded."""
        record = json.dumps(dict(STATUS["submissions"][0], id=7, head=TIP), indent=2)
        verdict = "#7 conflict: README.md, plugin/bin/crew, plugin/lib/plan.py, plugin/skills/crew/SKILL.md"
        tidying = "could not release /k/places/old-unit, whose worktree no longer exists: its release command failed"
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(2, record, f"{tidying}\n"),
                                                   ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''", sluice=verdict))])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "POLICY"] and self.closed == [] and self.handed == ["k"]
        assert self.handed_landed() == verdict
        (act, on, f), = self.emitted
        assert (act, on, f["Head"], f["refused"]) == ("bolt.submit", ["bolt/b"], TIP, verdict)
        err = capsys.readouterr().err
        assert (f"bolt/b did not land: sluice refused it or found a conflict, and main is where it was. sluice's verdict: {verdict}. "
                "Tell the bolt's conductor why: a conflict is the bolt's") in err
        assert f"Beside its verdict, and not why it did not land, sluice said: {tidying}." in err

    def test_checks_the_host_could_not_run_are_recorded_stopped_at_the_head_and_hold_nothing(self, monkeypatch, capsys):
        """bolt-teams "Checks the host could not run": the command fails, saying nothing of the bolt's stopped it, which
        checks could not run and that ops submits it again with no new word; recorded with no refusal, its Outcome
        stopped, its Why those checks and its Head, the pull request drafted and the kit's card raised all the same."""
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(1, json.dumps(dict(NOT_RUN, id=7)), "sluice: the host could not run check:dagger\n"),
                                                   ran_as(0, said(1, new=OLD, github=OLD, held="no", level="''", sluice="sluice: the host could not run check:dagger"))])
        cause = f"check:dagger could not run: {ENGINE}; check:image could not run: {ENGINE}"
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": cause, "Outcome": "stopped", "Submission": "7", "Head": TIP})]
        assert self.handed == ["k"] and self.closed == []
        err = capsys.readouterr().err
        assert (f"bolt/b did not land, and nothing of the bolt's stopped it: {cause}, and main is where it was. Its row keeps its box and "
                "the user's word stands: report what stopped it, and once it is cleared crew bolt submit b submits it again, with no "
                "new word.") in err and "b did not land, as said above; none landed" in err

    def test_a_submission_sluice_refused_at_once_is_recorded_in_its_words(self, monkeypatch, capsys):
        """sluice refused the submission itself, so there is no wait: its refusal is its error document on standard
        output (told.rs), handed to LANDED as its verdict, and, with no record of a conflict or a failed check, recorded
        stopped in it, holding nothing (bolt-teams "A refusal at once with no record of a conflict"); its warning on
        standard error is beside it."""
        no_gate = "main has no gate for bolt/b"
        answer = base64.b64encode(json.dumps({"error": {"kind": "refused", "message": no_gate, "next": []}}).encode()).decode()
        warned = "sluice: warning: branch protection not installed: no hooks directory"
        refused = ran_as(0, f"RC=2 TIP={TIP} OLD={OLD} ID= PULL= ANSWER={answer} SAID={base64.b64encode(f'{warned}\n'.encode()).decode()} LEVEL=\n",
                         f"{warned}\n")
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [refused, ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''", sluice=no_gate))])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "LANDED", "POLICY"] and self.handed_landed() == no_gate
        (_, _, f), = self.emitted
        assert (f["Head"], f["why"], f["Outcome"], "refused" in f) == (TIP, no_gate, "stopped", False)
        out, err = capsys.readouterr()
        assert "bolt/b submitted to k's main, sluice queueing nothing" in out
        assert (f"bolt/b did not land, and nothing of the bolt's stopped it: {no_gate}, and main is where it was. Its row keeps its "
                "box and the user's word stands") in err
        assert f"sluice said: {warned}." in err

    def test_a_refused_landing_leaves_its_pull_request_a_draft(self, monkeypatch):
        """bolt-teams "A refused landing leaves its pull request a draft": the one sluice's submission left ready is
        drafted before the command answers, its link named with what makes it live again."""
        outs = [ran(0, gh_list()), QUEUED, ran_as(2, json.dumps(dict(CONFLICT, id=7))), ran(0, said(2, new=OLD, github=OLD, held="no", level="''")),
                ran(0, gh_list(READY)), ran(0, gh_marked(0, "✓"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["refused"].startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
        assert f["refused"].endswith(" Its pull request https://github.com/o/k/pull/99 is a draft, so no merge into bolt/b "
                                     "lands it; the next crew bolt submit b, on the user's word, makes it live again.")
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "POLICY", "PULL", "PULL_MARK"]

    def test_a_landing_whose_submission_failed_leaves_it_a_draft_too(self, monkeypatch):
        outs = [ran(0, gh_list(DRAFT)), ran(0, gh_marked(0, "✓")), ran(2, "", "wt submit needs sluice's wt-submit, which is not on box's path\n"),
                ran(0, gh_list(READY)), ran(0, gh_marked(0, "✓"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["why"].startswith("bolt/b was not submitted on box: wt submit needs sluice's wt-submit, which is not on "
                                   "box's path. Its pull request ")
        assert (f["Outcome"], f.get("Head"), "refused" in f) == ("stopped", None, False)  # no tip named, so it holds nothing
        assert self.scripts()[-2:] == ["PULL", "PULL_MARK"]

    def test_the_next_landing_readies_its_draft_before_it_submits(self, monkeypatch, capsys):
        """bolt-teams "The next landing readies the pull request": readied before SUBMIT runs, said, and the landing
        goes on as any landing does."""
        outs = [ran(0, gh_list(DRAFT)), ran(0, gh_marked(0, "✓")), QUEUED, ran_as(0, "{}"), ran(0, said(0, github=NEW)),
                ran(0, "MARKED=yes\n")]
        _, emitted = self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "PULL_MARK", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert capsys.readouterr().out.splitlines() == [
            "Its pull request https://github.com/o/k/pull/99 is ready for review again, so sluice takes it at the head bolt/b has now.",
            "bolt/b submitted to k's main, sluice's #7", "bolt/b landed on k's main at bbbbbbb: now crew bolt land b."]
        assert emitted and self.closed == ["b"]

    def test_a_pull_request_crew_cant_ready_submits_nothing(self, monkeypatch):
        """bolt-teams "A pull request crew can't ready submits nothing"."""
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [ran(0, gh_list(DRAFT)), ran(0, gh_marked(1, "HTTP 403: Resource not accessible"))],
                        said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["refused"] == ("bolt/b was not submitted: crew could not make bolt/b's pull request https://github.com/o/k/pull/99 "
                                "ready for review: HTTP 403: Resource not accessible; sluice takes no draft into main's queue, so "
                                "nothing is submitted.")
        assert "SUBMIT" not in self.scripts()

    def test_one_crew_could_not_draft_is_named_first(self, monkeypatch):
        """Decision 5: the next merge into the bolt would land it, so the refusal says so first, with the command."""
        outs = [ran(0, gh_list()), QUEUED, ran_as(1, json.dumps(dict(RAN, id=7))), ran(0, said(1, new=OLD, github=OLD, held="no", level="''")),
                ran(0, gh_list(READY)), ran(0, gh_marked(1, "HTTP 502: Bad Gateway"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["refused"].startswith(
            "crew could not make bolt/b's pull request https://github.com/o/k/pull/99 a draft: HTTP 502: Bad Gateway; until "
            "it is one, the next merge into bolt/b lands it: gh pr ready 99 -R o/k --undo makes it one. bolt/b did not land: "
            "main's checks failed on it")

    def test_a_landing_that_lands_marks_nothing(self, monkeypatch, capsys):
        """bolt-teams "A landing that lands marks nothing": a landed pull request is merged, so it is never drafted."""
        outs = [ran(0, gh_list()), QUEUED, ran_as(0, "{}"), ran(0, said(0, github=NEW)), ran(0, "MARKED=yes\n")]
        self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        assert "PULL_MARK" not in self.scripts()
        assert capsys.readouterr().out.endswith("bolt/b landed on k's main at bbbbbbb: now crew bolt land b.\n")

    def test_three_bolts_on_one_host_are_queued_in_order_and_one_refused_holds_back_none(self, monkeypatch, capsys):
        """bolt-teams "Three bolts queued as one chain" and "One refused, the rest go on"."""
        q = lambda n: ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID={n} PULL= ANSWER= SAID= LEVEL=\n")
        outs = [q(1), q(2), q(3),
                ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n"),
                ran_as(2, json.dumps(dict(CONFLICT, id=2)), "sluice: bolt/z conflicts with main\n"), ran_as(0, said(2, new=NEW, github=NEW, held="no")),
                ran_as(0, "{}"), ran_as(0, said(0, github="d" * 40)), ran_as(0, "MARKED=yes\n")]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, bolts=("y", "z", "w"))
        assert [r for r in self.ran if r[0] != "POLICY"] == [
            ("MAIN", "box"), ("COPIES", "y"), ("OVERVIEW", "/k/main"), ("SUBMISSIONS", "/k/main"), ("SUBMIT", "y"), ("MAIN", "box"), ("COPIES", "z"), ("OVERVIEW", "/k/main"), ("SUBMISSIONS", "/k/main"), ("SUBMIT", "z"), ("MAIN", "box"), ("COPIES", "w"), ("OVERVIEW", "/k/main"), ("SUBMISSIONS", "/k/main"), ("SUBMIT", "w"),
            ("WAIT", "1"), ("READ", "y"), ("STATUS", "1"), ("LANDED", "y"), ("MARK", "y"), ("WAIT", "2"), ("READ", "z"), ("STATUS", "2"), ("LANDED", "z"), ("WAIT", "3"), ("READ", "w"), ("STATUS", "3"), ("LANDED", "w"), ("MARK", "w")]
        assert self.closed == ["y", "w"]
        assert [("refused" in f) for _, _, f in self.emitted] == [False, True, False]
        assert capsys.readouterr().err.endswith("z did not land, as said above; y and w landed\n")

    def test_bolts_on_two_hosts_submit_the_second_only_once_the_first_has_ended(self, monkeypatch):
        """bolt-teams "Bolts on two hosts"."""
        other = dict(self.T, name="swb-2", machine="mac-studio")
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n"),
                                               QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github="d" * 40)), ran_as(0, "MARKED=yes\n")],
                    bolts=("y", "z"), teams={"z": other})
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK", "MAIN", "COPIES",
                                  "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "STATUS", "LANDED", "MARK"]  # z read in this process, its host this one

    def test_a_landed_bolt_crew_could_not_close_is_named_and_recorded(self, monkeypatch, capsys):
        """bolt-teams "A landed bolt crew could not close": the read closes it in main-level ops's name, and its refusal
        is said with that crew's next read closes it once it is mended, and recorded as a refused bolt.land, the command
        going on and the bolt read landed."""
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")],
                    close=lambda fleet, a, **k: plan.fail("wldn/main could not be read"))
        assert capsys.readouterr().err.endswith("bolt/b landed and was not closed: wldn/main could not be read; crew's next read of the "
                                                "bolt closes it once that is mended\n")
        assert self.emitted[-1] == ("bolt.land", ["bolt/b"], {"refused": "wldn/main could not be read", "by": "wldn-ops"})

    def failing(self):
        """sluice's wait on #7 failing in sluice itself, its error document on standard output (told.rs)."""
        return ran_as(3, FAILED_DOC, f"sluice: {FAILED}\n")

    def record_of(self, state, n=7, **f):
        """sluice's record of #n in state, as sluice status <n> --json prints it."""
        return ran_as(0, json.dumps(dict(RAN, id=n, head=TIP, **{"state": state, **f})))

    def test_a_submission_sluice_failed_on_is_waited_on_again_and_lands(self, monkeypatch, capsys):
        """sluice itself fails while the submission waits: its record of #7, read on the team's host, has it under test,
        so crew says so and waits on it again, SUBMIT given its id and the tip it submitted, which keeps the landing's
        waiter, and the bolt lands from that wait, read, marked, recorded and closed as any landing."""
        self.submit(monkeypatch, self.BEFORE, [QUEUED, self.failing(), ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID=7 PULL= ANSWER= SAID= LEVEL=\n"),
                                               ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")],
                    statuses=[self.record_of("testing")])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "STATUS", "SUBMIT", "WAIT", "READ", "STATUS",
                                  "LANDED", "MARK"]
        assert [a[4:] for a in self.argvs if a[2] == plan.SUBMIT] == [  # its waiter's read run by crew there with the label
            ["/k/main", "/k/places/land-b", "b", "wldn-ops", "", "", "", "", "wldn", "crew"],
            ["/k/main", "/k/places/land-b", "b", "wldn-ops", "", "", "7", TIP, "wldn", "crew"]]
        out = capsys.readouterr().out
        assert (f"sluice itself failed ({FAILED}), but its record has bolt/b's submission, #7, under test on k's main: crew waits on it "
                "again (sluice wait 7).\n") in out and "bolt/b landed on k's main at bbbbbbb: now crew bolt land b.\n" in out
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Outcome": "landed", "Submission": "7",
                                                             "Head": TIP})] and self.closed == ["b"]

    def test_a_submission_sluice_failed_on_that_its_record_has_out_is_the_reads(self, monkeypatch, capsys):
        """Its record has it in conflict: the read records it in its record's verdict, the paths it names, never
        sluice's own failure on the wait, and it did not land."""
        conflict = ran_as(0, json.dumps(dict(CONFLICT, id=7, head=TIP)))
        verdict = "#7 conflict: README.md, plugin/bin/crew, plugin/lib/plan.py, plugin/skills/crew/SKILL.md"
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, self.failing(), ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''",
                                                                                          sluice=verdict))],
                        statuses=[conflict, conflict])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "STATUS", "READ", "STATUS", "LANDED", "POLICY"]
        assert self.closed == []
        assert self.handed_landed() == verdict
        (_, _, f), = self.emitted
        assert (f["Head"], f["Submission"], f["refused"]) == (TIP, "7", verdict)
        assert "bolt/b did not land: sluice refused it or found a conflict, and main is where it was" in capsys.readouterr().err

    def test_a_submission_sluice_fails_on_each_time_is_waited_on_again_as_many_times_as_crew_allows(self, monkeypatch):
        """bolt-teams "sluice itself fails": then recorded stopped at the head submitted, in sluice's words, with no
        Submission, so a later read records what sluice's record then has of #7."""
        again = ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID=7 PULL= ANSWER= SAID= LEVEL=\n")
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, self.failing()] + [again, self.failing()] * plan.AGAIN,
                        statuses=[self.record_of("testing")] * (plan.AGAIN + 1))
        assert self.scripts().count("SUBMIT") == plan.AGAIN + 1 and self.scripts().count("STATUS") == plan.AGAIN + 1
        assert "READ" not in self.scripts()
        (_, _, f), = self.emitted
        assert (f["why"], f["Outcome"], f["Head"], "Submission" in f and f["Submission"]) == (
            f"sluice itself failed ({FAILED}) each of the {plan.AGAIN} times crew waited on #7, which its record still has under "
            "test", "stopped", TIP, None)
        assert plan.landing_pending([dict(Act="bolt.submit", On=on, **{k: v for k, v in g.items() if v})
                                     for _, on, g in self.queued + self.emitted], "b")["Submission"] == "7"

    def test_a_submission_sluice_failed_on_at_once_is_found_recorded_queued_and_read(self, monkeypatch, capsys):
        """sluice itself fails answering the submission, the bolt's tip not on main now: its record of main, read on the
        team's host, has the tip's #160 under test, so crew waits on it, recording it queued, and its outcome is the
        read's, as any queued one's."""
        tip = HEADS["testing"]
        self.submit(monkeypatch, self.BEFORE, [ran_as(0, f"RC=3 TIP={tip} OLD={OLD} ID= PULL= ANSWER= SAID= LEVEL=\n"),
                                               ran_as(0, said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=tip)),
                                               ran_as(0, listing()), ran_as(0, f"RC=0 TIP={tip} OLD={OLD} ID=160 PULL= ANSWER= SAID= LEVEL=\n"),
                                               ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=tip)), ran_as(0, "MARKED=yes\n")])
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "LANDED", "SUBMISSIONS", "SUBMIT", "WAIT", "READ",
                                  "STATUS", "LANDED", "MARK"]
        (_, on, q), = self.queued
        assert (on, q["Submission"], q["Head"]) == (["bolt/b", "team/swb-1"], "160", tip)
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Outcome": "landed", "Submission": "160",
                                                             "Head": tip})] and self.closed == ["b"]

    def test_a_record_crew_cant_read_once_sluice_itself_failed_is_a_stop_naming_it(self, monkeypatch):
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, self.failing()],
                        statuses=[ran_as(1, '{"error":{"kind":"not_found","message":"no submission 7","next":[]}}')])
        (_, _, f), = self.emitted
        assert (f["why"], f["Outcome"]) == (f"sluice itself failed ({FAILED}), and sluice status 7 exited 1: no submission 7", "stopped")

    def test_a_wait_again_crew_could_not_start_is_said_and_lands_nothing(self, monkeypatch):
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, self.failing(), ran_as(255, "", "ssh: connect to host box port 22: timed out\n")],
                        statuses=[self.record_of("testing")])
        (_, _, f), = self.emitted
        assert f["why"] == ("crew can't tell whether bolt/b will land on k's main: crew could not wait on #7 again on box: "
                            "ssh: connect to host box port 22: timed out") and f["Outcome"] == "stopped" and self.closed == []

    def answered(self, answer=PULLED, pull="113"):
        """SUBMIT's report of sluice's answer naming no submission: its pull request's number, or none."""
        return ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID= PULL={pull} ANSWER={base64.b64encode(answer.encode()).decode()} SAID= LEVEL=\n")

    def test_a_landing_sluice_queued_as_a_pull_request_is_waited_on_as_the_submission_it_made(self, monkeypatch, capsys):
        """sluice answers with its pull request's number, as 0.36.4 does on a main that takes pull requests: crew finds
        the submission sluice made for it in sluice's record and waits on it as on any other, its outcome the state of
        the record the wait prints, and the bolt lands, nothing drafted, never taken for sluice queueing nothing."""
        outs = [ran(0, gh_list()), self.answered(), ran_as(0, listing(MADE)), ran_as(5, json.dumps(MADE)),
                ran_as(0, json.dumps(dict(MADE, state="landed"))), ran(0, said(0, github=NEW)), ran(0, "MARKED=yes\n")]
        _, emitted = self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "SUBMIT", "SUBMISSIONS", "WAIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert [n for s, n in self.ran if s == "WAIT"] == ["170", "170"]
        assert capsys.readouterr().out.splitlines() == [
            "bolt/b submitted to k's main, sluice's #170 from pull request #113", "bolt/b landed on k's main at bbbbbbb: now crew bolt land b."]
        assert emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Outcome": "landed", "Submission": "170",
                                                        "Head": TIP})] and self.closed == ["b"]

    def test_its_submission_sluice_found_in_conflict_did_not_land_and_its_pull_request_is_drafted(self, monkeypatch):
        """sluice's own outcome, read from the record's state: the conflict is the bolt's (plan.8), and its pull
        request is drafted as any refused landing's is."""
        outs = [ran(0, gh_list()), self.answered(), ran_as(0, listing(MADE)), ran_as(2, json.dumps(dict(MADE, state="conflict"))),
                ran(0, said(2, new=OLD, github=OLD, held="no", level="''")), ran(0, gh_list(READY)), ran(0, gh_marked(0, "✓"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        assert [a for a in self.argvs if a[2] == plan.LANDED][-1][9] == "2"
        (_, _, f), = self.emitted
        assert f["refused"].startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
        assert self.scripts()[-2:] == ["PULL", "PULL_MARK"]

    def test_a_pull_request_whose_submission_sluice_records_none_of_is_left_standing(self, monkeypatch, capsys):
        """Said by name, its pull request left as sluice has it, nothing drafted or waited on, and recorded with no
        refusal, so its row on the landings card is held for no fix (refusals)."""
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [ran(0, gh_list()), self.answered(), ran_as(0, listing(dict(MADE, head="d" * 40)))],
                        said=policy(TAKES))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "SUBMIT", "SUBMISSIONS"] and self.closed == [] and self.handed == []
        words = ("crew can't tell whether bolt/b will land on k's main: sluice holds it as pull request #113 (queued: next on "
                 "main), and sluice records no submission of ccccccc to main from pull request #113. crew withdraws nothing: the "
                 "pull request stands as sluice has it, and sluice wait main from /k/places/land-b follows it.")
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": words, "Head": TIP})]
        out, err = capsys.readouterr()
        assert "bolt/b submitted to k's main as pull request #113" in out and words in err

    def test_an_earlier_submission_sluice_answers_with_is_never_the_landings_outcome(self, monkeypatch, capsys):
        """The signal's case: sluice answers the landing with #171, the pull request's submission it blamed on the tip
        before the landing began, and #171's exit, and has made none for the landing: crew reads no outcome from it,
        names it with how sluice takes the pull request again, drafts and waits on nothing, and records no refusal, so
        no row is held for a fix the bolt does not need."""
        sent_back = ran_as(0, f"RC=1 TIP={TIP} OLD={OLD} ID=171 PULL= ANSWER={SENT_BACK_ANSWER} SAID= LEVEL=\n")
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [ran(0, gh_list()), sent_back, ran_as(0, listing(SENT_BACK))],
                        said=policy(TAKES), record=ran_as(0, listing(SENT_BACK)))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "SUBMIT", "SUBMISSIONS"]
        assert self.closed == [] and self.handed == [] and "LANDED" not in self.scripts()
        words = ("crew can't tell whether bolt/b will land on k's main: sluice answered its submission with #171, an earlier one "
                 "from pull request #113, blamed for a check that failed, and sluice records no submission of ccccccc to main from "
                 "pull request #113 newer than #171. crew withdraws nothing: the pull request stands as sluice has it, which sluice "
                 "takes again on that head only once it is marked a draft and then ready for review, and sluice wait main from "
                 "/k/places/land-b follows it.")
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": words, "Head": TIP})]
        out, err = capsys.readouterr()
        assert "bolt/b submitted to k's main as pull request #113" in out and words in err and "checks failed" not in err

    def test_one_sluice_made_since_the_landing_began_is_waited_on_as_its_own(self, monkeypatch, capsys):
        """sluice answers with the earlier one while its record has one made since from the pull request, as when its
        intake read the pull request readied in a round beside: that one is the landing's, and the bolt lands from it."""
        made = dict(MADE, id=172)
        outs = [ran(0, gh_list()), ran_as(0, f"RC=1 TIP={TIP} OLD={OLD} ID=171 PULL= ANSWER={SENT_BACK_ANSWER} SAID= LEVEL=\n"),
                ran_as(0, listing(SENT_BACK, made)), ran_as(0, json.dumps(dict(made, state="landed"))), ran(0, said(0, github=NEW)),
                ran(0, "MARKED=yes\n")]
        self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES), record=ran_as(0, listing(SENT_BACK)))
        assert [n for s, n in self.ran if s == "WAIT"] == ["172"] and [a for a in self.argvs if a[2] == plan.LANDED][-1][9] == "0"
        assert "bolt/b submitted to k's main, sluice's #172 from pull request #113" in capsys.readouterr().out
        assert self.closed == ["b"]

    def test_a_record_crew_cant_read_before_the_landing_submits_nothing(self, monkeypatch):
        """read.1: with no record of what sluice held before, no submission it answers with could be told from one made
        before the landing, so nothing is readied or submitted, and nothing drafted."""
        locked = ran_as(3, json.dumps({"error": {"message": "its records are locked"}}))
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [], said=policy(TAKES), record=locked)
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS"]
        (_, _, f), = self.emitted
        assert f["refused"] == ("bolt/b was not submitted: crew can't read sluice's record of k's main on box, so could not tell "
                                "its submission from any made before it: sluice status main --all exited 3: its records are locked")

    def copies(self, own, held, ahead, lacks, beyond):
        """What LAND_COPIES says of bolt/b on box once it has fetched GitHub's, whose policy names origin for it."""
        return ran_as(0, f"OWN={own}\nTHERE={GITHUBS}\nAT_THERE={base64.b64encode(ON_GITHUB.encode()).decode()}\n"
                         f"HELD={held}\nAHEAD={ahead}\nLACKS={lacks}\nBEYOND={beyond}\n")

    def test_a_copy_that_lags_githubs_is_levelled_and_githubs_head_submitted(self, monkeypatch, capsys):
        """bolt-teams "The host's copy lags GitHub's" (plan.19, design Decision 4): SUBMIT is given GitHub's head and
        the copy's value as read, and once it says it levelled the copy the command says so, naming both commits."""
        levelled = ran_as(0, f"RC=0 TIP={GITHUBS} OLD={OLD} ID=7 PULL= ANSWER= SAID= LEVEL={HOSTS}\n")
        self.submit(monkeypatch, self.BEFORE, [levelled, ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=GITHUBS)),
                                               ran_as(0, "MARKED=yes\n")], copies=self.copies(HOSTS, "yes", "no", 0, 2))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert [a[4:10] for a in self.argvs if a[2] == plan.SUBMIT] == [
            ["/k/main", "/k/places/land-b", "b", "wldn-ops", GITHUBS, HOSTS]]
        assert "levelled box's copy of bolt/b from 1111111 to GitHub's 2222222, 2 merges it lacked\n" in capsys.readouterr().out
        assert self.emitted[0][2]["Head"] == GITHUBS and self.closed == ["b"]

    def test_a_level_submit_did_not_need_to_make_is_not_said(self, monkeypatch, capsys):
        """The copy already at GitHub's head when SUBMIT ran, levelled by another hand since the read: SUBMIT writes
        nothing and says LEVEL empty, so the command says nothing of levelling."""
        self.submit(monkeypatch, self.BEFORE, [ran_as(0, f"RC=0 TIP={GITHUBS} OLD={OLD} ID=7 PULL= ANSWER= SAID= LEVEL=\n"),
                                               ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=GITHUBS)), ran_as(0, "MARKED=yes\n")],
                    copies=self.copies(HOSTS, "yes", "no", 0, 2))
        assert "levelled" not in capsys.readouterr().out

    def test_a_diverged_bolt_submits_nothing_and_leaves_its_pull_request_as_it_was(self, monkeypatch, capsys):
        """bolt-teams "The two copies have diverged": refused before its pull request is readied, so gh is never asked,
        SUBMIT never runs, the refusal is recorded naming both commits, and the command exits non-zero."""
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [], said=policy(TAKES), copies=self.copies(HOSTS, "no", "no", 1, 2))
        assert self.scripts() == ["MAIN", "COPIES"] and self.closed == [] and self.handed == []
        words = ("bolt/b was not submitted: its two copies have diverged: box's 1111111 holds 1 merge GitHub's 2222222 lacks, "
                 "and GitHub's holds 2 merges box's lacks, so either submission would drop merges. The bolt is its branch "
                 "on GitHub, so the way on is its team's: its conductor starts a fix (crew fix), whose place is cut from "
                 "GitHub's head, that takes box's merges in (git merge bolt/b) and merges into the bolt through sluice; the "
                 "landing then submits GitHub's head, levelling box's copy to it")
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"refused": words})]
        assert words in capsys.readouterr().err

    def test_copies_crew_cannot_read_submit_nothing(self, monkeypatch, capsys):
        """bolt-teams "GitHub's copy cannot be read": the fetch's words, and a host that does not answer, each refuse
        before anything is readied or submitted (read.1)."""
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [], copies=ran_as(0, "READ=fatal: Could not read from remote repository.\n"))
        assert self.emitted[0][2] == {"refused": "bolt/b was not submitted: crew can't read bolt/b on GitHub: fatal: Could not "
                                                 "read from remote repository."}
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [], copies=ran_as(255, "", "ssh: connect to host box port 22: timed out\n"))
        assert self.scripts() == ["MAIN", "COPIES"]
        assert self.emitted[0][2] == {"refused": "bolt/b was not submitted: crew can't read bolt/b's copies on box: ssh: "
                                                 "connect to host box port 22: timed out"}

    def test_an_answer_crew_cant_read_is_named_and_left_standing(self, monkeypatch, capsys):
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [ran(0, gh_list()), self.answered("queued,\n  somewhere", pull="")], said=policy(TAKES))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "PULL", "SUBMIT"] and self.closed == [] and self.handed == []
        words = ("crew can't tell whether bolt/b will land on k's main: sluice answered its submission with what crew can't read, "
                 "queued, somewhere. crew withdraws nothing: what sluice queued stands, its place /k/places/land-b kept, and sluice "
                 "status main says where it is.")
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": words, "Head": TIP})]
        out, err = capsys.readouterr()
        assert "bolt/b submitted to k's main, sluice's answer naming no submission crew reads" in out and words in err


class TestAStandingLanding:
    """bolt-teams "A landing standing in sluice is waited on again, not submitted again": crew bolt submit reads sluice's
    queue on the team's host first (QUEUE), and a landing of the bolt standing at the head it submits is waited on
    again, SUBMIT handed its number and head, nothing submitted and no pull request readied; one at another head is
    said, and the bolt submitted as before. On TestTheSubmission's stand-ins."""
    T, BEFORE = TestTheSubmission.T, TestTheSubmission.BEFORE
    submit, scripts, copies, _state = TestTheSubmission.submit, TestTheSubmission.scripts, TestTheSubmission.copies, TestTheSubmission._state

    def standing(self, head, n=355, worktree="pull/198", pull_head="bolt/b", state="queued"):
        doc = dict(STANDING, branches=[{"branch": "main", "submissions": [
            {"schema": "sluice/submission@1", "id": n, "branch": "main", "head": head, "state": state,
             "from": {"agent": "wldn-ops", "worktree": worktree, "head": pull_head}}]}])
        return ran_as(0, json.dumps(doc))

    def test_a_landing_standing_at_the_head_it_submits_is_waited_on_again_and_nothing_is_submitted(self, monkeypatch, capsys):
        """bolt-teams "Ops restarted while its landing stood": no SUBMISSIONS read, no pull request readied, SUBMIT given
        #355 and its head, and the landing's end recorded as any landing's is."""
        again = ran_as(0, f"RC=0 TIP={GITHUBS} OLD={OLD} ID=355 PULL= ANSWER= SAID= LEVEL=\n")
        self.submit(monkeypatch, self.BEFORE, [again, ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=GITHUBS)), ran_as(0, "MARKED=yes\n")],
                    said=policy(TAKES), copies=self.copies(GITHUBS, "yes", "no", 0, 0), overview=self.standing(GITHUBS))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert [a[4:] for a in self.argvs if a[2] == plan.SUBMIT] == [
            ["/k/main", "/k/places/land-b", "b", "wldn-ops", GITHUBS, GITHUBS, "355", GITHUBS, "wldn", "crew"]]
        assert [a[4:] for a in self.argvs if a[2] == plan.WAIT] == [["/k/main", "355"]]
        out = capsys.readouterr().out
        assert "bolt/b's landing #355 stands in sluice at 2222222, its head: crew waits on #355 again and submits nothing" in out
        (_, _, q), = self.queued  # recorded queued, so any later read reads #355 (plan.21)
        assert (q["Submission"], q["Head"]) == ("355", GITHUBS)
        assert self.emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Outcome": "landed", "Submission": "355",
                                                             "Head": GITHUBS})]
        assert self.closed == ["b"]

    def test_a_landing_standing_from_the_bolts_branch_itself_is_its_own(self, monkeypatch, capsys):
        again = ran_as(0, f"RC=0 TIP={GITHUBS} OLD={OLD} ID=12 PULL= ANSWER= SAID= LEVEL=\n")
        self.submit(monkeypatch, self.BEFORE, [again, ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=GITHUBS)), ran_as(0, "MARKED=yes\n")],
                    copies=self.copies(GITHUBS, "yes", "no", 0, 0), overview=self.standing(GITHUBS, 12, "bolt/b", None, "testing"))
        assert "SUBMISSIONS" not in self.scripts() and "crew waits on #12 again" in capsys.readouterr().out

    def test_a_landing_standing_at_another_head_is_said_and_the_bolt_submitted_as_before(self, monkeypatch, capsys):
        """bolt-teams "A standing landing at an older head"."""
        levelled = ran_as(0, f"RC=0 TIP={GITHUBS} OLD={OLD} ID=356 PULL= ANSWER= SAID= LEVEL=\n")
        self.submit(monkeypatch, self.BEFORE, [levelled, ran_as(0, "{}"), ran_as(0, said(0, github=NEW, tip=GITHUBS)), ran_as(0, "MARKED=yes\n")],
                    copies=self.copies(GITHUBS, "yes", "no", 0, 0), overview=self.standing(HOSTS, 350))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert [a[4:10] for a in self.argvs if a[2] == plan.SUBMIT] == [["/k/main", "/k/places/land-b", "b", "wldn-ops", GITHUBS, GITHUBS]]
        assert "bolt/b's landing #350 stands in sluice at 1111111, not its head 2222222: crew submits 2222222 as before" in capsys.readouterr().out

    def test_a_queue_that_cant_be_read_is_said_and_the_bolt_submitted_as_before(self, monkeypatch, capsys):
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")],
                    overview=ran_as(2, '{"error":{"kind":"refused","message":"no repository here"}}'))
        assert self.scripts() == ["MAIN", "COPIES", "OVERVIEW", "SUBMISSIONS", "POLICY", "SUBMIT", "WAIT", "READ", "STATUS", "LANDED", "MARK"]
        assert ("crew can't read sluice's queue on box, so whether a landing of bolt/b stands there can't be told: sluice "
                "overview exited 2: no repository here; it submits bolt/b as before") in capsys.readouterr().err


def test_a_landing_is_waited_on_again_only_at_the_head_it_submits():
    def sub(n, head, worktree="pull/1", pull_head="bolt/y"):
        return {"id": n, "branch": "main", "head": head, "state": "queued", "worktree": worktree, "pull_head": pull_head}
    assert plan.landing_standing([sub(355, TIP)], "y", TIP) == ("again", 355, TIP)
    assert plan.landing_standing([sub(350, OLD)], "y", TIP) == ("past", 350, OLD)
    assert plan.landing_standing([sub(350, OLD)], "y", None) == ("past", 350, OLD)
    assert plan.landing_standing([sub(350, TIP, pull_head="bolt/z")], "y", TIP) == ("none", None, None)
    assert plan.landing_standing([], "y", TIP) == ("none", None, None)
    assert plan.standing_words("y", "past", 350, OLD, None) == (
        "bolt/y's landing #350 stands in sluice at aaaaaaa, and crew can't tell the head this landing submits: it submits bolt/y as before")


def test_a_queue_read_says_why_it_cant_be_read():
    assert plan.queue_read(255, "", "ssh: connect to host box port 22: timed out\n") == (
        None, "sluice overview exited 255: ssh: connect to host box port 22: timed out")
    assert plan.queue_read(0, "nope", "") == (None, "sluice overview printed no JSON")
    assert plan.queue_read(0, EMPTY_QUEUE, "") == ([], None)


def submitted(bolt, head=TIP, **f):
    return dict({"Act": "bolt.submit", "On": [f"bolt/{bolt}"], **({"Head": head} if head else {})}, **f)


class TestTheStops:
    """Decision 2: a stop is a bolt.submit marked Outcome stopped with its Head and Why and no Refused, read from each
    bolt's last one (plan.stops), and holds nothing of a refusal (plan.refusals); at another head it says nothing
    (plan.stopped_at)."""
    STOP = submitted("b", Why="sluice itself failed (its lock could not be taken)", Outcome="stopped")

    def test_each_bolts_last_stop_is_read(self):
        entries = [submitted("b", Why="tests:logic could not run: no engine", Outcome="stopped"), self.STOP,
                   submitted("c", head="d" * 40, Why="sluice's record has #9 withdrawn", Outcome="stopped")]
        assert plan.stops(entries) == {"b": (TIP, "sluice itself failed (its lock could not be taken)"),
                                       "c": ("d" * 40, "sluice's record has #9 withdrawn")}
        assert plan.refusals(entries) == {}

    def test_a_later_landing_or_refusal_supersedes_it(self):
        landed = submitted("b", Why="bolt(b): landed on main at bbbbbbb")
        refused = submitted("b", Refused="sluice: bolt/b conflicts with main")
        assert plan.stops([self.STOP, landed]) == {} and plan.stops([self.STOP, refused]) == {}
        assert plan.refusals([self.STOP, refused]) == {"b": (TIP, "sluice: bolt/b conflicts with main")}
        assert plan.stops([refused, self.STOP]) == {"b": (TIP, self.STOP["Why"])} and plan.refusals([refused, self.STOP]) == {}

    def test_a_stop_with_no_head_gives_none(self):
        assert plan.stops([submitted("b", head=None, Why="bolt/b was not submitted on box: wt-submit is missing", Outcome="stopped")]) == {}

    def test_a_stop_says_its_words_only_at_its_head(self):
        got = plan.stops([self.STOP])
        assert plan.stopped_at(got, "b", TIP[:7]) == self.STOP["Why"]
        assert plan.stopped_at(got, "b", "e" * 40) is None and plan.stopped_at(got, "c", TIP) is None


class TestWhatSluicesRecordMeans:
    """Decision 2: what sluice's record of a landing's submission, #n, as `sluice status <n> --json` prints it on the
    team's host, means for the landing (plan.landing_due): standing, out with sluice's exit for its state, or unread."""

    @pytest.mark.parametrize("state", sorted(plan.STANDING))
    def test_a_submission_in_the_queue_or_under_test_is_standing(self, state):
        assert plan.landing_due(214, 0, json.dumps(dict(RAN, state=state))) == ("standing", state)

    @pytest.mark.parametrize("state, rc", [("landed", "0"), ("failed", "1"), ("conflict", "2"), ("withdrawn", "4")])
    def test_one_out_is_out_with_the_exit_its_wait_gives_it_and_its_record(self, state, rc):
        doc = dict(RAN, state=state)
        assert plan.landing_due(214, 0, json.dumps(doc)) == ("out", rc, doc)

    def test_sluices_error_is_said_in_its_words(self):
        assert plan.landing_due(412, 1, '{"error":{"kind":"not_found","message":"no submission 412","next":[]}}') == (
            "unread", "sluice status 412 exited 1: no submission 412")
        assert plan.landing_due(412, 255, "") == ("unread", "sluice status 412 exited 255")

    def test_a_record_crew_does_not_read_is_unread(self):
        assert plan.landing_due(412, 0, json.dumps(RAN)) == (
            "unread", f"sluice status 412 printed no record of #412 crew reads: {plan.cut(' '.join(json.dumps(RAN).split()), 200)}")
        assert plan.landing_due(214, 0, "queued") == ("unread", "sluice status 214 printed no record of #214 crew reads: queued")
        assert plan.landing_due(214, 0, json.dumps(dict(RAN, state="paused"))) == (
            "unread", "sluice's record has #214 in a state crew does not read: \"paused\"")


class APlan:
    """A plan holding the named bolts, each held by swb-1 and of kit k."""
    def __init__(self, *bolts):
        self.bolts_ = set(bolts)

    def bolt(self, name):
        return {"Bolt": name, "Team": "swb-1", "Repo": "k"} if name in self.bolts_ else None


class TestTheLandingsRead:
    """crew _landing-read <label> <bolt> (Decision 2, bolt-teams "A landing is recorded by whatever reads the bolt after
    it"): on the team's host, one at a time, the bolt's queued submission read from sluice's own record and its outcome
    recorded once, as crew bolt submit records it; nothing recorded while it stands or can't be read."""
    T = TestTheSubmission.T
    F = {"teams": {"swb-1": T}}
    Q = dict(submitted("b", Outcome="queued", Submission="412", Base=OLD, Repo="k"), On=["bolt/b", "team/swb-1"])

    @pytest.fixture(autouse=True)
    def host(self, monkeypatch, tmp_path):
        """box, the team's host: its team state under tmp_path, the run record holding entries, the plan holding b, and
        each script crew runs there answering in turn from outs, what ran and what was recorded kept on self."""
        self.entries, self.outs, self.ran, self.emitted, self.closed = [dict(self.Q)], [], [], [], []
        self.plan = APlan("b")
        monkeypatch.setattr(plan.crew, "this_host", lambda: "box")
        monkeypatch.setattr(plan.crew, "with_kit", lambda t, repo: self.T)
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: self.plan)
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: list(self.entries))
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: self.T if b else None)
        monkeypatch.setattr(plan, "team_state", lambda t: tmp_path / f"{t['name']}-team")
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("o/state", f"{label}/main"))
        monkeypatch.setattr(plan, "fetch", lambda repo, ref, fresh=False: "tip")
        monkeypatch.setattr(plan, "READ", type("R", (), {"drop_kit": lambda s, h, m: None})())
        monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: policy(TAKES_NONE))
        names = {plan.SUBMISSION_STATUS: "STATUS", plan.LANDED: "LANDED", plan.LANDED_MARK: "MARK"}

        def on_machine(fleet, host, argv):
            self.ran.append((names[argv[2]], argv[-1] if argv[2] == plan.SUBMISSION_STATUS else argv[5]))
            return self.outs.pop(0)
        monkeypatch.setattr(plan.crew, "on_machine", on_machine)
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on, **f: self.emitted.append((act, on, f)) or self.entries.append(
            dict({k: v for k, v in f.items() if v not in (None, "")}, Act=act, On=on, **({"Refused": f["refused"]} if f.get("refused") else {}))))
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None: None)
        monkeypatch.setattr(plan, "bolt_land", lambda fleet, a, **k: self.closed.append((a.bolt, k)) or self.plan.bolts_.discard(a.bolt))
        monkeypatch.setattr(plan.record, "who", lambda: "swb-1-conductor")

    def record_of(self, state, **f):
        return ran_as(0, json.dumps(dict(RAN, id=412, head=TIP, **{"state": state, **f})))

    def test_it_runs_only_on_the_teams_host(self, monkeypatch):
        monkeypatch.setattr(plan.crew, "this_host", lambda: "mac-studio")
        with pytest.raises(plan.Refusal, match=r"^bolt b's landing is read on box, where swb-1, which holds it, runs, not on mac-studio$"):
            plan.landing_read(self.F, "wldn", "b")
        assert self.ran == [] and self.emitted == []

    def test_a_submission_still_standing_records_nothing(self, capsys):
        """"Still standing": the bolt's last bolt.submit stays queued."""
        self.outs = [self.record_of("testing")]
        assert plan.landing_read(self.F, "wldn", "b") == (False, "bolt/b's landing is still queued: sluice's record has #412 under test "
                                                              "on k's main, so nothing of it is recorded yet")
        assert self.ran == [("STATUS", "412")] and self.emitted == []
        assert plan.submit_queued(self.entries, "b") == self.Q

    def test_one_sluice_landed_is_recorded_landed_from_its_record_once(self, capsys):
        """"The submitter is gone before sluice decides": the read records it landed at the commit main holds, with
        sluice's number, and a second read says so again from what the host kept, reading and recording nothing."""
        self.outs = [self.record_of("landed", landed_as=NEW), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")]
        landed, words = plan.landing_read(self.F, "wldn", "b")
        assert (landed, words) == (True, "bolt/b landed on k's main at bbbbbbb: now crew bolt land b.")
        assert [r for r, _ in self.ran] == ["STATUS", "LANDED", "MARK"]
        (act, on, f), = self.emitted
        assert (act, on, f["Outcome"], f["Submission"], f["Head"]) == ("bolt.submit", ["bolt/b"], "landed", "412", TIP)
        self.ran, self.emitted, self.entries = [], [], [dict(self.Q)]  # its entry not yet on the branch
        assert plan.landing_read(self.F, "wldn", "b") == (True, words)
        assert self.ran == [] and self.emitted == [] and words in capsys.readouterr().out
        assert self.closed == [("b", {"by": "wldn-ops", "close_why": "plan(b): land the bolt, its landing #412 read from sluice's record by "
                                                              "swb-1-conductor"})]  # by the first read alone, the plan then holding it no more

    def test_a_read_waiting_on_one_that_closed_the_bolt_says_its_close_and_closes_nothing(self, monkeypatch, tmp_path, capsys):
        """"Two reads at once": the second waits on the first's lock, and reads the plan afresh under it, so it says
        what the first said of the outcome and of its close, recording and closing nothing."""
        mark = tmp_path / "swb-1-team" / "landings" / "b.412"
        mark.parent.mkdir(parents=True)
        mark.write_text(json.dumps({"landed": True, "words": "bolt/b landed", "out": "bolt/b landed\n", "err": "",
                                    "closed_out": "b has landed at k's bbbbbbb; swb-1 holds no bolt\n", "closed_err": ""}))
        plans = [APlan("b"), APlan()]  # before its lock, the first read not yet done; under it, done
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plans.pop(0) if len(plans) > 1 else plans[0])
        assert plan.landing_read(self.F, "wldn", "b") == (True, "bolt/b landed")
        assert self.closed == [] and self.emitted == [] and self.ran == []
        assert capsys.readouterr().out == "bolt/b landed\nb has landed at k's bbbbbbb; swb-1 holds no bolt\n"

    def test_its_landing_reads_the_head_and_main_before_from_the_queued_entry(self):
        self.outs = [self.record_of("landed"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")]
        recorded = []
        monkeypatch = pytest.MonkeyPatch()
        ran = plan.crew.on_machine
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: recorded.append(argv) or ran(fleet, host, argv))
        try:
            plan.landing_read(self.F, "wldn", "b")
        finally:
            monkeypatch.undo()
        landed = next(a for a in recorded if a[2] == plan.LANDED)
        assert landed[4:10] == ["/k/main", "/k/places/land-b", "b", TIP, OLD, "0"]

    def test_a_conflict_is_recorded_refused_at_the_head_in_sluices_verdict(self, capsys):
        """"A conflict recorded by a later read"."""
        verdict = "#412 conflict: README.md, plugin/bin/crew, plugin/lib/plan.py, plugin/skills/crew/SKILL.md"
        handed = []
        ran = plan.crew.on_machine
        self.outs = [ran_as(0, json.dumps(dict(CONFLICT, id=412, head=TIP))),
                     ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''", sluice=verdict))]
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: (argv[2] == plan.LANDED and handed.append(
            base64.b64decode(argv[-1]).decode())) or ran(fleet, host, argv))
        try:
            assert plan.landing_read(self.F, "wldn", "b")[0] is False
        finally:
            monkeypatch.undo()
        assert handed == [verdict]  # sluice's verdict, from its record, handed to the landing's end
        (act, on, f), = self.emitted
        assert (f["refused"], f["Submission"], f["Head"]) == (verdict, "412", TIP)
        assert "bolt/b did not land: sluice refused it or found a conflict" in capsys.readouterr().err

    def test_a_record_that_cant_be_read_records_nothing_naming_the_host(self, capsys):
        """"sluice's record can't be read"."""
        self.outs = [ran_as(1, '{"error":{"kind":"not_found","message":"no submission 412","next":[]}}')]
        words = "crew can't read sluice's record of #412 on box, so nothing of bolt/b's landing is recorded: sluice status 412 exited 1: no submission 412"
        assert plan.landing_read(self.F, "wldn", "b") == (False, words)
        assert self.emitted == [] and words in capsys.readouterr().err

    def test_a_submission_whose_outcome_is_recorded_is_not_read_again(self):
        self.entries.append(submitted("b", Outcome="landed", Submission="412"))
        assert plan.landing_read(self.F, "wldn", "b") == (True, "bolt/b landed as #412, as wldn's run record has it")
        self.entries[-1] = submitted("b", Refused="#412 conflict: a.txt", Submission="412")
        assert plan.landing_read(self.F, "wldn", "b") == (False, "bolt/b did not land: #412 conflict: a.txt, as wldn's run record has it")
        self.entries[:], self.plan.bolts_ = [], {"b"}
        assert plan.landing_read(self.F, "wldn", "b") == (False, "no landing of bolt b is queued in wldn's run record")
        assert self.ran == []

    def test_a_stop_crew_bolt_submits_wait_recorded_leaves_the_submission_to_a_later_read(self):
        self.entries.append(submitted("b", Why="sluice itself failed", Outcome="stopped"))
        self.outs = [self.record_of("landed"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")]
        assert plan.landing_read(self.F, "wldn", "b")[0] is True

    def refusing(self, *words):
        """crew bolt land's code refusing in each of words in turn."""
        said = list(words)
        def close(fleet, a, **k):
            self.closed.append((a.bolt, k))
            plan.fail(said.pop(0))
        return close

    def test_a_refused_close_is_said_each_time_and_recorded_once_for_its_words(self, monkeypatch, capsys):
        """"A chore still at ready" and "The same refusal is recorded once": the read after the landing, and two team
        reads after it, each try the close and say why it was refused; the run record holds one refused bolt.land for
        those words, in main-level ops's name, and one more once the words change."""
        ready = "chore tidy-b has not landed on main: it is ready"
        monkeypatch.setattr(plan, "bolt_land", self.refusing(ready, ready, ready, "wldn/main could not be read"))
        self.outs = [self.record_of("landed"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")]
        for _ in range(4):
            assert plan.landing_read(self.F, "wldn", "b")[0] is True
        assert len(self.closed) == 4
        assert [(a, f.get("refused"), f.get("by")) for a, _, f in self.emitted if a == "bolt.land"] == [
            ("bolt.land", ready, "wldn-ops"), ("bolt.land", "wldn/main could not be read", "wldn-ops")]
        err = capsys.readouterr().err
        assert err.count(f"bolt/b landed and was not closed: {ready}; crew's next read of the bolt closes it once that is mended") == 3

    def test_a_close_refused_before_is_lifted_by_a_later_read(self, monkeypatch):
        """"Lifted": once what it named is mended, the next read closes the bolt."""
        monkeypatch.setattr(plan, "bolt_land", self.refusing("chore tidy-b has not landed on main: it is ready"))
        self.outs = [self.record_of("landed"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")]
        plan.landing_read(self.F, "wldn", "b")
        monkeypatch.setattr(plan, "bolt_land", lambda fleet, a, **k: self.closed.append((a.bolt, k)) or self.plan.bolts_.discard(a.bolt))
        assert plan.landing_read(self.F, "wldn", "b")[0] is True and len(self.closed) == 2 and self.plan.bolt("b") is None

    def test_a_bolt_that_did_not_land_is_not_closed(self):
        self.outs = [ran_as(0, json.dumps(dict(CONFLICT, id=412, head=TIP))), ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''"))]
        plan.landing_read(self.F, "wldn", "b")
        assert self.closed == []

    def test_a_bolt_the_plan_no_longer_holds_is_read_on_the_team_its_queued_entry_names(self, tmp_path):
        self.plan = APlan()
        mark = tmp_path / "swb-1-team" / "landings" / "b.412"
        mark.parent.mkdir(parents=True)
        mark.write_text(json.dumps({"landed": True, "words": "bolt/b landed on k's main at bbbbbbb"}))
        assert plan.landing_read(self.F, "wldn", "b") == (True, "bolt/b landed on k's main at bbbbbbb")
        assert self.closed == [] and self.ran == []


class TestWhoReads:
    """Decision 3: the team's read runs the landing's read of a bolt whose landing worktree stands with no waiter alive,
    or whose every unit and chore reads landed, its branch marked landed when none is left (plan.landing_read_due), and
    of no other; crew bolt land reads a queued landing first."""
    PATH = "/k/places/land-b"

    @pytest.mark.parametrize("now, stages, marked, due", [
        ((PATH, True, False), ["merged"], False, True),  # its waiter stopped before sluice decided
        ((PATH, True, True), ["merged"], False, False),  # its waiter still waits
        ((PATH, False, False), ["landed", "landed"], False, True),  # landed, a close refused
        ((PATH, False, False), ["landed", "ready"], False, False),  # a chore still at ready
        ((PATH, False, False), [], True, True),  # its last chore dropped after a refused close
        ((PATH, False, False), [], False, False),  # a bolt given with nothing in it yet
        ((PATH, False, False), ["code"], False, False)])  # an idle team's read reads nothing
    def test_which_bolts_a_teams_read_reads(self, now, stages, marked, due):
        assert plan.landing_read_due(now, stages, marked) is due

    def test_the_teams_read_reads_only_the_bolts_due(self, monkeypatch):
        t = dict(TestTheSubmission.T, label="wldn")
        bolts = {"b": ["landed"], "c": ["code"], "d": []}
        pl = type("P", (), {"work_of": lambda s, b: [type("U", (), {"name": lambda s, n=f"{b}-{i}": n})() for i in range(len(bolts[b]))]})()
        read = []
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: pl)
        monkeypatch.setattr(plan, "held_by", lambda p, team: [type("B", (), {"name": lambda s, n=b: n, "get": lambda s, k: None})() for b in bolts])
        monkeypatch.setattr(plan, "stages_for", lambda fleet, p, bs: type("S", (), {"of": lambda s, u: {"stage": bolts[u.split("-")[0]][int(u.split("-")[1])]}})())
        monkeypatch.setattr(plan, "landing_now", lambda t, b: (f"/k/places/land-{b}", False, False))
        monkeypatch.setattr(plan, "landing_marked", lambda t, b: b == "d")
        monkeypatch.setattr(plan, "landing_read", lambda fleet, label, b: read.append(b) or plan.fail("crew can't read b's landing") if b == "d" else read.append(b))
        plan.reap_landings({}, t)
        assert read == ["b", "d"]

    def test_crew_bolt_land_reads_a_queued_landing_first_and_says_when_the_read_closed_it(self, monkeypatch, capsys):
        held = {"b"}
        P = type("P", (), {"bolt": lambda s, n: {"Bolt": n, "Team": "swb-1", "Repo": "k"} if n in held else None})
        monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, P()))
        monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: TestTheSubmission.T)
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: [TestTheLandingsRead.Q])
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("o/state", f"{label}/main"))
        monkeypatch.setattr(plan, "fetch", lambda repo, ref, fresh=False: "tip")
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: P())
        monkeypatch.setattr(plan, "landing_read_on", lambda fleet, t, label, b: held.discard(b) or True)
        monkeypatch.setattr(plan, "host_run", lambda *a: pytest.fail("crew bolt land went on after the read closed the bolt"))
        plan.bolt_land({}, argparse.Namespace(bolt="b", label=None))
        assert capsys.readouterr().out == "bolt b is closed: crew's read of its landing closed it\n"

    def test_a_landing_nothing_queued_or_a_close_by_a_read_reads_nothing_first(self, monkeypatch):
        P = type("P", (), {"bolt": lambda s, n: {"Bolt": n, "Team": "swb-1", "Repo": "k"}, "work_of": lambda s, b: []})
        monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, P()))
        monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: TestTheSubmission.T)
        monkeypatch.setattr(plan, "landing_read_on", lambda *a: pytest.fail("a read ran"))
        monkeypatch.setattr(plan, "host_run", lambda *a: plan.fail("went on to read main"))
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: [submitted("b", Outcome="landed", Submission="412")])
        with pytest.raises(plan.Refusal, match="went on to read main"):
            plan.bolt_land({}, argparse.Namespace(bolt="b", label=None))
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: [TestTheLandingsRead.Q])
        with pytest.raises(plan.Refusal, match="went on to read main"):
            plan.bolt_land({}, argparse.Namespace(bolt="b", label=None), by="wldn-ops")


def test_a_close_by_a_read_records_its_bolt_land_in_ops_name_with_its_why(monkeypatch):
    """Decision 4: crew bolt land's code, run by a read, writes its bolt.land by main-level ops with the Why the read
    gives it, whatever names the command uses for its own reads on the way, and with the bolt's age and split as any
    landing of a held bolt carries them (plan.20)."""
    P = type("P", (), {"bolt": lambda s, n: {"Bolt": n, "Team": "swb-1", "Repo": "k"}, "work_of": lambda s, b: [], "units": lambda s: []})
    wrote = []
    monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, P()))
    monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
    monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: TestTheSubmission.T)
    monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: TestTheSubmission.BEFORE)
    monkeypatch.setattr(plan, "stages_for", lambda fleet, pl, bs: type("S", (), {"of": lambda s, u: {"stage": "landed"}})())
    monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: [])
    monkeypatch.setattr(plan, "write", lambda fleet, label, change, subject, **k: wrote.append((subject, k.get("by"), k.get("why"))))
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: None)
    monkeypatch.setattr(plan, "landed_line", lambda *a: "landed")
    monkeypatch.setattr(plan, "tidy_after", lambda *a, **k: None)
    spent = dict(Age="200", Split="team 150, kit 20, user 0, hold 0, nobody 30")
    monkeypatch.setattr(plan, "landing_time", lambda fleet, t, pl, b, entries, now: spent)
    fields = []
    write = plan.write
    monkeypatch.setattr(plan, "write", lambda fleet, label, change, subject, **k: (fields.append(k.get("fields")), write(fleet, label, change, subject, **k)))
    plan.bolt_land({}, argparse.Namespace(bolt="b", label=None), by="wldn-ops", close_why="plan(b): land the bolt, its landing #412 read")
    assert wrote == [("plan(b): land the bolt", "wldn-ops", "plan(b): land the bolt, its landing #412 read")]
    assert fields[0]["Age"] == "200" and fields[0]["Split"] == spent["Split"]


class TestARefusedClose:
    """Decision 4: a refused close is recorded only when no bolt.land refused since the bolt's landing carries the same
    words (plan.close_refused_new)."""
    LANDED = submitted("b", Outcome="landed", Submission="412")
    WORDS = "chore tidy-b has not landed on main: it is ready"

    def refused(self, words, bolt="b"):
        return {"Act": "bolt.land", "On": [f"bolt/{bolt}"], "Refused": words}

    def test_the_first_refusal_since_the_landing_is_new(self):
        assert plan.close_refused_new([self.LANDED], "b", self.WORDS)
        assert plan.close_refused_new([self.refused(self.WORDS), self.LANDED], "b", self.WORDS)  # one before the landing

    def test_the_same_words_again_are_not(self):
        assert not plan.close_refused_new([self.LANDED, self.refused(self.WORDS)], "b", self.WORDS)
        assert not plan.close_refused_new([self.LANDED, self.refused(self.WORDS), self.refused("x", bolt="z")], "b", self.WORDS)

    def test_other_words_are(self):
        assert plan.close_refused_new([self.LANDED, self.refused(self.WORDS)], "b", "wldn/main could not be read")
        assert plan.close_refused_new([self.LANDED, self.refused("other"), self.refused("x"), ], "b", "other")


class TestTheQueuedLanding:
    """Decision 1: a landing sluice has queued is its bolt's last bolt.submit marked Outcome queued (plan.submit_queued),
    in flight: no refusal, no stop and no landing, until an outcome follows it."""
    QUEUED = submitted("b", Outcome="queued", Submission="412", Base=OLD)

    def test_a_bolts_last_submission_queued_is_its_landing_in_flight(self):
        assert plan.submit_queued([self.QUEUED], "b") == self.QUEUED
        assert plan.submit_queued([self.QUEUED], "z") is None and plan.submit_queued([], "b") is None

    def test_an_outcome_after_it_ends_it(self):
        for outcome in (submitted("b", Outcome="landed", Submission="412"), submitted("b", Refused="#412 conflict: a.txt"),
                        submitted("b", Why="sluice itself failed", Outcome="stopped")):
            assert plan.submit_queued([self.QUEUED, outcome], "b") is None

    def test_it_holds_no_refusal_and_no_stop_of_an_earlier_landing(self):
        entries = [submitted("b", Refused="#400 conflict: a.txt"), submitted("b", Why="stopped", Outcome="stopped"), self.QUEUED]
        assert plan.refusals(entries) == {} and plan.stops(entries) == {}
        assert plan.refused_at(entries, "b", TIP) is None


class TestSubmitDecisions:
    def test_bolts_on_one_host_are_each_queued_behind_the_one_before(self):
        assert plan.submit_order(["y", "z", "w"], {"y": "box", "z": "box", "w": "box"}) == [
            ("y", "first"), ("z", "queued"), ("w", "queued")]

    def test_a_bolt_on_another_host_waits_for_the_one_before_to_end(self):
        assert plan.submit_order(["y", "z", "w"], {"y": "deneb", "z": "mac-studio", "w": "mac-studio"}) == [
            ("y", "first"), ("z", "ended"), ("w", "queued")]

    def test_bolts_of_two_kits_are_refused_before_anything_is_submitted(self):
        """bolt-teams "Bolts of two kits"."""
        assert plan.submit_refusal(["y", "w"], {"y": "crew", "w": "swancloud"}, {"y": "crw-1", "w": "swc-1"}) == (
            "crew bolt submit lands one kit's bolts at a time, and y is crew's and w is swancloud's: submit each kit's in a "
            "command of its own")

    def test_a_bolt_named_twice_or_held_by_no_team_is_refused(self):
        assert plan.submit_refusal(["y", "z", "y"], {"y": "k", "z": "k"}, {"y": "t", "z": "t"}) == (
            "crew bolt submit names y twice: each bolt lands once, in the order given")
        assert plan.submit_refusal(["y", "z"], {"y": "k", "z": "k"}, {"y": "t", "z": None}) == (
            "bolt z is held by no team, so it has no branch to submit")
        assert plan.submit_refusal(["y", "z"], {"y": "k", "z": "k"}, {"y": "t", "z": "t"}) is None

    def test_a_refusal_before_anything_is_submitted_is_recorded_on_each_bolt_named(self):
        assert plan.named(argparse.Namespace(cmd="bolt", sub="submit", bolt=["y", "z"])) == ["bolt/y", "bolt/z"]


HOSTS, GITHUBS = "1" * 40, "2" * 40


def copies(own=HOSTS, there=GITHUBS, remote="origin", held="yes", ahead="no", lacks=0, beyond=2, read=None):
    """What kit.land_copies reads of a bolt's two copies, a host's copy two merges behind GitHub's unless given."""
    return dict(own=own, there=there, remote=remote, held=held, ahead=ahead, lacks=lacks, beyond=beyond, read=read)


class TestTheHeadALandingSubmits:
    """The head a landing submits, read after one fetch of the bolt (plan.landing_head, plan.19, design Decision 2):
    the bolt where it lives, the host's copy levelled to GitHub's first."""

    def test_a_copy_that_lags_githubs_is_levelled_and_githubs_head_submitted(self):
        """bolt-teams "The host's copy lags GitHub's"."""
        assert plan.landing_head("b", "box", copies()) == dict(
            head=GITHUBS, level=True, said="levelled box's copy of bolt/b from 1111111 to GitHub's 2222222, 2 merges it lacked")
        assert plan.landing_head("b", "box", copies(beyond=1))["said"].endswith(", 1 merge it lacked")

    def test_a_copy_level_with_githubs_writes_nothing_and_says_nothing(self):
        """bolt-teams "The host's copy is level with GitHub's"."""
        assert plan.landing_head("b", "box", copies(own=GITHUBS, ahead="yes", beyond=0)) == dict(head=GITHUBS, level=False, said=None)

    def test_a_host_with_no_copy_has_one_made_at_githubs_head(self):
        """bolt-teams "The host has no copy"."""
        assert plan.landing_head("b", "box", copies(own="-", ahead=None, lacks=None, beyond=None)) == dict(
            head=GITHUBS, level=True, said="made box's copy of bolt/b at GitHub's 2222222")

    def test_a_legacy_tip_ahead_of_githubs_is_submitted_as_it_stands(self):
        """bolt-teams "A legacy bolt's host tip is ahead of GitHub's copy"."""
        assert plan.landing_head("b", "box", copies(held="no", ahead="yes", lacks=1, beyond=0)) == dict(
            head=HOSTS, level=False, said=("bolt/b is split: box's tip 1111111 holds 1 merge GitHub's 2222222 lacks; the "
                                           "landing submits that tip, its push moving GitHub's branch forward"))

    def test_two_copies_that_have_diverged_submit_nothing_and_name_the_fix_as_the_way_on(self):
        """bolt-teams "The two copies have diverged", and plan.19 as read for batch 34's reviewer: the bolt is its branch
        on GitHub, so the host copy's merges are carried by the team's fix, cut from GitHub's head, and the landing then
        submits GitHub's head."""
        assert plan.landing_head("b", "box", copies(held="no", ahead="no", lacks=1, beyond=2)) == (
            "bolt/b was not submitted: its two copies have diverged: box's 1111111 holds 1 merge GitHub's 2222222 lacks, "
            "and GitHub's holds 2 merges box's lacks, so either submission would drop merges. The bolt is its branch "
            "on GitHub, so the way on is its team's: its conductor starts a fix (crew fix), whose place is cut from "
            "GitHub's head, that takes box's merges in (git merge bolt/b) and merges into the bolt through sluice; the "
            "landing then submits GitHub's head, levelling box's copy to it")

    def test_a_bolt_that_lives_on_its_host_is_submitted_from_its_copy(self):
        """bolt-teams "A bolt that lives on its host": no origin, GitHub without the branch, or GitHub's copy naming no
        remote for it."""
        absent = dict(copies(), own=None, there="-", remote=None, held=None, ahead=None, lacks=None, beyond=None)
        assert plan.landing_head("b", "box", absent) == dict(head=None, level=False, said=None)
        assert plan.landing_head("b", "box", copies(remote=None)) == dict(head=None, level=False, said=None)

    def test_a_copy_on_github_crew_cannot_read_submits_nothing(self):
        """bolt-teams "GitHub's copy cannot be read"."""
        unread = dict(copies(), own=None, there=None, remote=None, held=None, ahead=None, lacks=None, beyond=None,
                      read="fatal: Could not read from remote repository.")
        assert plan.landing_head("b", "box", unread) == (
            "bolt/b was not submitted: crew can't read bolt/b on GitHub: fatal: Could not read from remote repository.")


def test_a_landing_while_the_laptop_is_off_reads_the_branch_alone_and_names_no_host(monkeypatch):
    """review-batches, "A landing while the laptop is off": crew bolt land's guard reads which changes have been in a
    batch from the partition's branch, asking no host, so a host off the tailnet holds back no landing."""
    from facts import FLEET, constructed, plan_of, reviewed
    fleet = dict(FLEET, partitions={"wldn": dict(FLEET["partitions"]["wldn"], state="WilldanGroup/crew-state")})
    entries = [dict(constructed("a", "aaa1"), Id="20261012T100000Z-000000-chuck-herdr-alpha-1-1"),
               dict(reviewed(4, [("a", "swb-1", "aaa1")], 5), Id="20261012T100500Z-000000-mac-studio-1-1")]
    monkeypatch.setattr(plan.crew, "on_machine", lambda *a, **k: pytest.fail(f"a host was asked for the run record: {a}"))
    monkeypatch.setattr(plan.record, "on_branch", lambda fleet, label, since, tips=None: entries)
    p = plan_of(bolts={"y": "swb-1"}, units={"a": "y"})
    outside = [u for u, *_ in plan.due_changes(p, plan.partition_entries(fleet, "wldn")) if u in ["a"]]
    assert outside == [] and plan.land_refusal("y", ["a"], lambda u: {"stage": "landed"}, outside, "wldn") is None


def test_what_the_mark_said_is_its_value_or_the_hosts_words():
    assert [plan.mark_said(0, f"MARKED={v}\n", "") for v in ("yes", "no", "'git config could not set it'")] == [
        "yes", "no", "git config could not set it"]
    assert plan.mark_said(255, "", "ssh: connect to host box port 22: timed out\n") == "ssh: connect to host box port 22: timed out"
    assert plan.mark_said(2, "", "") == "exit 2"


def test_the_hosts_main_lags_githubs_and_nothing_is_refused_for_it():
    """bolt-teams "Main is behind GitHub's" (plan.8, plan.18): the landing reads only the commit GitHub's main holds
    after a fetch, which it records, and a host's own main lagging it refuses nothing."""
    github, own = "d" * 40, "e" * 40
    assert plan.main_held("k", "chuck-herdr-alpha", f"ORIGIN=yes\nFETCHED=ok\nGITHUB={github}\nOWN={own}\n") == (github, None)


RECORDED = pathlib.Path(__file__).parent / "sluice-0.36.4"
ON_GITHUB = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'
ON_HOST = '[branches."bolt/*"]\nrequired = ["#check-full"]\n'


def deleted(name, policy=ON_GITHUB):
    """What BOLT_DELETE prints when sluice says what sluice 0.36.4 recorded under name: where the bolt lives, by the
    policy at the host's own branch, then sluice's exit and document."""
    out = (RECORDED / name).read_text()
    code = int(next(l for l in (RECORDED / "README").read_text().splitlines() if l.startswith(f"{name}\t")).split("\t")[1].split()[1])
    return (f"LOCAL={'a' * 40}\nTRACKED={'a' * 40}\nAT_LOCAL={base64.b64encode(policy.encode()).decode()}\nAT_TRACKED=-\n"
            f"RC={code}\nSAID={base64.b64encode(out.encode()).decode()}\n")


class TestTheBranchIsDeleted:
    """bolt-plan "A bolt is created, given, dropped and landed through crew" (plan.19): crew bolt land has sluice delete
    the bolt's branch after its plan write, by the tidy on the team's host once the landing's place is gone, wherever
    the policy at its tip keeps it; what it says of it."""

    def test_the_bolts_branch_is_deleted_at_its_land(self):
        """bolt-plan "The bolt's branch is deleted at its land"."""
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete.json"), "") == (
            "sluice deleted bolt/b from GitHub at 22eef85")

    def test_a_bolt_made_before_is_deleted_where_its_tip_keeps_it(self):
        """bolt-plan "A bolt made before lands": a tip whose policy names no remote is the host's own branch."""
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete.json", ON_HOST), "") == (
            "sluice deleted bolt/b from chuck-herdr-alpha at 22eef85")

    def test_a_delete_sluice_refuses_names_the_branch_kept_in_its_words(self):
        """bolt-plan "A delete sluice refuses": the bolt has left the plan, and the branch stays on GitHub."""
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete-queued.json"), "") == (
            "bolt/b is kept on GitHub: sluice did not delete it: #1 still queued on bolt/b; wait for them to land, or withdraw them")
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete-not-landed.json"), "").startswith(
            "bolt/b is kept on GitHub: sluice did not delete it: bolt/b at 22eef85")

    def test_a_branch_already_gone_refuses_nothing(self):
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete-not-found.json"), "") == (
            "bolt/b is gone already: no branch bolt/b")

    def test_a_host_that_does_not_answer_or_words_crew_cannot_read_leave_the_branch_named(self):
        assert plan.deleted_said("b", "chuck-herdr-alpha", 255, "", "ssh: connect to host") == (
            "chuck-herdr-alpha did not answer, so sluice was not asked to delete bolt/b: sluice branch delete bolt/b --into main there")
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, deleted("delete.json").replace("RC=0", "RC=x"), "").startswith(
            "bolt/b may still stand on GitHub: crew can't read what sluice's branch delete said from:")

    def test_a_branch_a_worktree_still_holds_is_not_asked_of_sluice(self):
        """plan.19: sluice 0.36.4's delete removes a branch a worktree holds, leaving the worktree on no branch (read
        2026-10-22), so a landing's place kept for its changes keeps the branch, named with the command for after it."""
        assert plan.deleted_said("b", "chuck-herdr-alpha", 0, "", "", "/kit/places/land-b") == (
            "bolt/b is kept: /kit/places/land-b holds it, so sluice was not asked to delete it: sluice branch delete bolt/b "
            "--into main on chuck-herdr-alpha, once that worktree is gone")


class TestTheCardsClose:
    """crew bolt land closes the bolt's landing card on its team's host (plan.16, record 0032 §3): with where GitHub's
    main holds the landing and that every host's folder follows by the timer, under whichever landing key the conductor
    holds one."""

    def test_the_card_closes_naming_githubs_main_sluices_submission_and_the_timer(self):
        assert plan.landed_words("c" * 40, "46") == (
            "landed on GitHub's main at ccccccc (#46); every host's folder follows by swancloud's timer within minutes")

    def test_a_head_sluice_did_not_make_is_named_without_a_number(self):
        for n in ("", None, "46 47", "x"):
            assert plan.landed_words("c" * 40, n) == (
                "landed on GitHub's main at ccccccc; every host's folder follows by swancloud's timer within minutes")

    def test_a_landing_on_the_users_words_sends_the_word_and_the_words_first_and_records_neither(self):
        """main-level spec, "The card closes with the user's words": the word comes first, since Pending You's close is
        cut from its end, and the run record keeps the outcome without the user's words (record.3)."""
        landed = plan.landed_words("c" * 40, "46")
        recorded, sent = plan.pane_landed(landed, "swancloud-ops", "2026-10-22T21:04:09Z", "Land crw-5's bolt")
        assert recorded == f"Landed on the user's word in swancloud-ops's pane; {landed}"
        assert "Land crw-5's bolt" not in recorded
        assert sent == f'Landed on the user\'s word in swancloud-ops\'s pane, "Land crw-5\'s bolt"; {landed}'

    def test_words_not_read_back_close_naming_the_pane_and_the_time(self):
        """main-level spec, "Closed on another host"."""
        landed = plan.landed_words("c" * 40, "46")
        recorded, sent = plan.pane_landed(landed, "swancloud-ops", "2026-10-22T21:04:09Z", None)
        assert recorded == f"Landed on the user's word in swancloud-ops's pane; {landed}"
        assert sent == f"Landed on the user's word in swancloud-ops's pane at 21:04Z; {landed}"

    def test_the_conductors_open_cards_under_the_bolts_landing_keys_old_and_new(self):
        post = lambda key, card, by="swb-1-conductor": {"Act": "card.post", "Key": key, "Card": card, "By": by}
        entries = [post("land/b/abc1234", "req_1"), post("land/b", "req_2"), post("land/b/abc9999", "req_3"),
                   {"Act": "card.close", "Card": "req_3", "Key": "land/b/abc9999", "By": "swb-1-conductor"},
                   post("land/b", "req_4", by="swb-2-conductor"), post("land/bb", "req_5"), post("proposal/1", "req_6")]
        assert plan.landing_card_keys(entries, "b", "swb-1-conductor") == ["land/b", "land/b/abc1234"]
        assert plan.landing_card_keys(entries, "c", "swb-1-conductor") == []


class TestTheLandingsPoint:
    """crew raises a bolt's landing card once the bolt reads proven (rail-cards, record 0031 §1, record 0025): every
    unit and chore merged, sluice green at its head, no fix in flight on it, and every unit's latest change in a
    batch; then which act follows each event."""
    GREEN = "passed (3 run, 1 replayed)"
    WORK = [("a", "unit", "merged"), ("b", "unit", "merged"), ("c", "chore", "merged")]

    def unready(self, work=WORK, verdict=GREEN, fixes=()):
        return plan.landing_unready(work, "abc1234" + "0" * 33, verdict, list(fixes))

    def test_a_green_bolt_whose_every_unit_and_chore_merged_reads_proven(self):
        assert self.unready() is None
        assert self.unready(self.WORK + [("d", "unit", "landed")]) is None

    @pytest.mark.parametrize("work, verdict, fixes, why", [
        ([("a", "unit", "verify")] + WORK[1:], GREEN, (), "unit a has not merged: it is verify"),
        ([], GREEN, (), "it holds no units or chores"),
        ([("a", "unit", "landed")], GREEN, (), "every unit and chore of it has landed"),
        (WORK, "", (), "its verification is not green: its head abc1234 is no landing of sluice's, so it has no verdict"),
        (WORK, GREEN, ("fix/y/zone-gap",), "fix/y/zone-gap is in flight on it")])
    def test_until_then_no_card_is_raised(self, work, verdict, fixes, why):
        assert self.unready(work, verdict, fixes) == why

    def test_a_fix_is_in_flight_from_its_start_until_it_merges_or_is_dropped(self):
        """The landing's point waits for no fix of the bolt in flight: a fix place of the bolt that has neither merged
        nor been dropped; one of another bolt is not the bolt's."""
        fixes = [{"fix": "fix/y/gap", "bolt": "y", "merged": False, "dropped": False},
                 {"fix": "fix/y/done", "bolt": "y", "merged": True, "dropped": False},
                 {"fix": "fix/y/gone", "bolt": "y", "merged": False, "dropped": True},
                 {"fix": "fix/z/gap", "bolt": "z", "merged": False, "dropped": False}]
        assert plan.fixes_in_flight(fixes, "y") == ["fix/y/gap"]
        assert self.unready(fixes=plan.fixes_in_flight(fixes, "y")) == "fix/y/gap is in flight on it"
        assert self.unready(fixes=plan.fixes_in_flight(fixes[1:], "y")) is None

    def test_its_facts_wait_for_every_units_latest_change_to_have_been_in_a_batch(self):
        pr = plan.pull_of("swb-1-unit-2 (pull/23)", "WilldanGroup/switchboard-kit")
        facts = plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", "2026-10-17T10:00:00Z", set(), {}, {"a": 4, "b": 5}, 2, pr)
        assert facts == dict(bolt="y", kit="switchboard-kit", units=["a", "b"], chores=["c"], batches={"a": 4, "b": 5}, head="abc1234",
                             at="2026-10-17T10:00:00Z", moved=2, pr={"number": 23, "url": "https://github.com/WilldanGroup/switchboard-kit/pull/23"},
                             frees=None)
        frees = {"team": "swc-1", "next": "d"}
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, set(), {}, {}, 0, None, frees)["frees"] == frees
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, {"b"}, {}, {"a": 4}, 0, None) is None

    def test_its_facts_wait_for_the_users_answer_on_each_batch_card_that_holds_a_units_latest_change(self):
        """briefs.12: the user, 2026-10-19, on card req_5ff4d31d: "Wait for my answer on the batch card", after crew's
        small-leftovers-of-crew landed (#71) while batch 7's card, which held its unit, was unanswered."""
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, set(), {"b": 7}, {"a": 6, "b": 7}, 0, None) is None
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, set(), {"q": 7}, {"a": 6, "b": 7}, 0, None)["units"] == ["a", "b"]

    def test_a_chore_is_in_no_batch_and_holds_no_landing(self):
        facts = plan.landing_facts("y", "switchboard-kit", [("c", "chore", "merged")], "abc1234", None, set(), {}, {}, 0, None)
        assert (facts["units"], facts["chores"], facts["batches"]) == ([], ["c"], {})

    def test_sluices_pull_request_is_the_one_its_submission_at_the_head_went_through(self):
        assert plan.pull_of("swb-1-unit-2 (unit/a)", "o/k") is None and plan.pull_of("", "o/k") is None

    def test_a_landing_reading_is_its_cover_each_units_change_in_the_plans_order_then_the_diff(self):
        """card-sessions "A landing's session opens what the bolt brings to main, as one review": two units and a chore,
        each unit's Markdown named for it in a change's reading order, the diff numbered after the last unit."""
        a = [("tasks.md", "a's tasks"), ("specs/x/spec.md", "a's spec"), ("proposal.md", "a's proposal"), ("design.md", "a's design")]
        b = [("proposal.md", "b's proposal")]
        files = plan.landing_reading("y", "switchboard-kit", "def5678" + "0" * 33, ["a", "b"], ["c"], [("a", a), ("b", b)],
                                     "diff --git a/x b/x\n")
        assert [n for n, _ in files] == ["00-y.md", "01-a-proposal.md", "01-a-design.md", "01-a-specs-x-spec.md", "01-a-tasks.md",
                                         "02-b-proposal.md", "03-y-diff.txt"]
        assert files[1][1] == "a's proposal" and files[-1][1] == "diff --git a/x b/x\n"

    def test_a_bolt_of_chores_alone_reads_as_its_cover_and_its_diff(self):
        files = plan.landing_reading("y", "k", "def5678", [], ["c", "d"], [], "diff --git a/x b/x\n")
        assert [n for n, _ in files] == ["00-y.md", "01-y-diff.txt"]
        assert plan.landing_reading("y", "k", "def5678", [], ["c"], [], "")[-1][1] == (
            "The bolt changes nothing against main outside its change folders.\n")

    def test_the_cover_names_every_unit_and_chore_and_says_the_reading_lands_nothing(self):
        cover = plan.landing_reading("y", "switchboard-kit", "def5678" + "0" * 33, ["a", "b"], ["c"],
                                     [("a", [("proposal.md", "")]), ("b", [("proposal.md", "")])], "")[0][1]
        assert cover.startswith("# Bolt y, landing on switchboard-kit's main\n\nWhat lands, at its head def5678:\n\n- a\n- b\n- c (chore)\n")
        assert "This reading lands nothing: approving the landing card is the word to land" in cover
        assert "reaches the bolt's conductor as notes on the landing card, and a note naming a defect holds the landing for a fix" in cover

    def test_a_landings_reading_is_written_into_its_heads_folder_from_the_kit_at_the_head(self, monkeypatch, tmp_path):
        """card-sessions "A bolt of two units and a chore": each unit's change read at the head, and the diff from where
        the bolt last met main to its head, less the change folders."""
        held = {"a": [("proposal.md", "a's proposal")], "b": [("tasks.md", "b's tasks"), ("proposal.md", "b's proposal")]}
        asked = []
        monkeypatch.setattr(plan, "change_held", lambda main, ref, u: asked.append((main, ref, u)) or held.get(u))
        monkeypatch.setattr(plan, "kit_git", lambda fleet, t, where, *args: asked.append((where, *args)) or (0, "diff --git a/x b/x"))
        fleet = {"teams": {"swb-1": {"name": "swb-1", "machine": "box", "kit": {"main": "/kit/main"}}}}
        f = dict(bolt="y", kit="switchboard-kit", units=["a", "b"], chores=["c"], head="def5678" + "0" * 33, base="abc1234",
                 team="swb-1", host="box")
        folder = tmp_path / "def5678"
        folder.mkdir()
        (folder / "01-old-proposal.md").write_text("an older head's")
        paths = plan.landing_write(fleet, f, folder)
        assert [pathlib.Path(p).name for p in paths] == ["00-y.md", "01-a-proposal.md", "02-b-proposal.md", "02-b-tasks.md", "03-y-diff.txt"]
        assert sorted(p.name for p in folder.iterdir()) == sorted(pathlib.Path(p).name for p in paths)
        assert (folder / "03-y-diff.txt").read_text() == "diff --git a/x b/x\n"
        assert asked[:2] == [("/kit/main", f["head"], "a"), ("/kit/main", f["head"], "b")]
        assert asked[2] == ("/kit/main", "diff", "--no-color", "--no-ext-diff", "abc1234", f["head"], "--", ".", ":(exclude)openspec/changes")

    def test_a_unit_whose_change_the_head_does_not_hold_refuses_and_nothing_is_written(self, monkeypatch, tmp_path):
        monkeypatch.setattr(plan, "change_held", lambda main, ref, u: None)
        monkeypatch.setattr(plan, "kit_git", lambda *a: pytest.fail("the diff was read after a change crew could not read"))
        fleet = {"teams": {"swb-1": {"name": "swb-1", "machine": "box", "kit": {"main": "/kit/main"}}}}
        f = dict(bolt="y", kit="k", units=["a"], chores=[], head="def5678" + "0" * 33, base="abc1234", team="swb-1", host="box")
        with pytest.raises(plan.Refusal, match="unit a's change is not on bolt y at def5678, open or archived, in /kit/main on box"):
            plan.landing_write(fleet, f, tmp_path / "def5678")
        assert not (tmp_path / "def5678").exists()

    def test_a_proven_bolts_card_waits_on_its_batches_and_says_which(self):
        """briefs.12, as crew card session land/<bolt> says why the bolt has no card yet."""
        assert plan.batch_waits(["a", "b", "c"], {"a"}, {"b": 7, "c": 8}) == (
            "a has not been in a batch, which is due; the user has not answered batches 7 and 8")
        assert plan.batch_waits(["a", "b"], {"a", "b"}, {}) == "a or b have not been in a batch, which is due"
        assert plan.batch_waits(["a"], set(), {"a": 7}) == "the user has not answered batch 7"
        assert plan.batch_waits(["a"], set(), {"q": 7}) is None

    FRESH = dict(bolt="y", head="def5678", host="mac-studio")

    def test_a_first_refused_reading_is_tried_again_with_the_landing_read_afresh(self):
        """card-sessions "The first start fails and the second opens": the fresh facts are the card's from then."""
        assert plan.landing_retry("plannotator did not list land/y's session within 10 seconds", (self.FRESH, None), None) == (
            "again", self.FRESH)

    def test_a_bolt_that_no_longer_reads_proven_raises_nothing(self):
        """card-sessions "The bolt no longer reads proven at the second try"."""
        assert plan.landing_retry("plannotator ended before land/y's session was ready", (None, "fix/y/gap is in flight on it"),
                                  None) == ("none", None)

    def test_a_fresh_read_that_is_refused_leaves_the_first_reason_standing(self):
        """read.1: what the second read could not read is not guessed past."""
        why = "plannotator did not list land/y's session within 10 seconds"
        assert plan.landing_retry(why, None, "bolt y's kit could not be read: ssh: timed out") == ("stand", why)

    def test_which_act_follows_each_event(self):
        assert plan.landing_act("proven", head="abc1234" + "0" * 33) == ("change", "Its head is now abc1234")
        assert plan.landing_act("fix", words="The zone list misses one zone.") == ("close", None, "held for a fix: The zone list misses one zone.")
        assert plan.landing_act("landed", words="landed on GitHub's main at c0ffee1 (#3); every host's folder follows") == (
            "close", "landed on GitHub's main at c0ffee1 (#3); every host's folder follows", None)


class TestThePreview:
    """A landing's card lists the addresses of a preview of the bolt's head when the kit declares one, follows the head
    with it, says one that failed, and releases it when the card closes (rail-cards, record 0031 §3)."""
    HEAD, NEW = "abc1234" + "0" * 33, "def5678" + "0" * 33

    @pytest.mark.parametrize("declared, recorded, listed, alive, step", [
        (False, None, False, False, "none"),
        (True, None, False, False, "ask"),
        (True, HEAD, True, False, "keep"),
        (True, HEAD, False, True, "keep"),
        (True, HEAD, False, False, "ask"),
        (True, NEW, True, True, "replace"),
        (False, HEAD, True, False, "release"),
        (False, NEW, False, False, "release"),
    ])
    def test_what_crew_does_with_the_preview_at_each_raise(self, declared, recorded, listed, alive, step):
        """"Asked again with nothing changed": the recorded preview of the head kept, nothing asked; "The head moves":
        the old head's replaced; a kit that declares none asks nothing."""
        assert plan.preview_step(declared, recorded, self.HEAD, listed, alive) == step

    @pytest.mark.parametrize("shown, outcome, note", [
        ("addresses", "failed", "Its preview of abc1234 did not come up"),
        ("reason", "up", "Its preview of abc1234 is up"),
        ("addresses", "up", None),
        ("reason", "failed", None),
    ])
    def test_a_previews_end_changes_the_card_only_when_it_changes_what_the_card_says(self, shown, outcome, note):
        """"The stack fails to come up" and "The host is busy when the card is raised"."""
        assert plan.preview_change(shown, outcome, self.HEAD) == note

    def test_a_previews_end_is_a_change_of_the_card_in_its_words(self):
        assert plan.landing_act("preview", head=self.HEAD, words="Its preview of abc1234 is up") == ("change", "Its preview of abc1234 is up")

    LISTED = [
        {"name": "preview/0123456789ab", "branch": "main", "revision": HEAD, "state": "up", "addresses": {"web": "http://w"}},
        {"name": "preview/aaaaaaaaaaaa", "branch": "bolt/y", "revision": NEW, "state": "up", "addresses": {"web": "http://n"}},
        {"name": "preview/bbbbbbbbbbbb", "branch": "bolt/y", "revision": HEAD, "state": "starting", "made": "2026-10-19T10:00:00Z",
         "addresses": {"web": "http://web-abc1234--bolt-y--kit.localhost:4321", "api": "http://api-abc1234--bolt-y--kit.localhost:4322"}},
    ]

    def test_the_heads_preview_is_the_entry_sluice_lists_for_the_bolts_branch_and_its_head(self):
        assert plan.preview_listed(self.LISTED, "bolt/y", self.HEAD) == dict(
            head=self.HEAD, name="preview/bbbbbbbbbbbb", state="starting",
            addresses={"web": "http://web-abc1234--bolt-y--kit.localhost:4321", "api": "http://api-abc1234--bolt-y--kit.localhost:4322"})
        assert plan.preview_listed(self.LISTED, "bolt/z", self.HEAD) is None and plan.preview_listed([], "bolt/y", self.HEAD) is None

    def test_a_failed_preview_carries_sluices_output(self):
        failed = [dict(self.LISTED[2], state="failed", output="building web\nerror: port 4321 in use\n")]
        assert plan.preview_listed(failed, "bolt/y", self.HEAD)["output"] == "building web\nerror: port 4321 in use\n"
        assert plan.preview_listed([dict(failed[0], output=None)], "bolt/y", self.HEAD)["output"] == ""

    @pytest.mark.parametrize("doc, said", [
        ({"previews": []}, "sluice's previews are no list crew reads"),
        (["preview/0123456789ab"], "sluice lists a preview crew can't read"),
        ([LISTED[0], None], "sluice lists a preview crew can't read"),
        ([dict(LISTED[2], state="booting")], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
        ([dict(LISTED[2], name=7)], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
        ([dict(LISTED[2], addresses={"web": None})], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
    ])
    def test_a_list_crew_cannot_read_is_refused(self, doc, said):
        with pytest.raises(plan.Refusal) as e:
            plan.preview_listed(doc, "bolt/y", self.HEAD)
        assert str(e.value).startswith(said)

    @pytest.mark.parametrize("code, out, err, ended", [
        (0, '{"name": "preview/0123456789ab", "state": "up", "addresses": {"web": "http://w"}}', "", {"state": "up"}),
        (1, '{"name": "preview/0123456789ab", "state": "failed", "output": "building\\nerror: port 4321 in use\\n"}', "",
         {"state": "failed", "why": "building / error: port 4321 in use"}),
        (2, '{"error": {"kind": "refused", "message": "abc1234 has no [preview] table in .config/sluice.toml", "next": []}}', "",
         {"state": "failed", "why": "abc1234 has no [preview] table in .config/sluice.toml"}),
        (2, "", "error: unrecognized subcommand 'preview'\n\nUsage: sluice <COMMAND>\n", {"state": "failed", "why": "Usage: sluice <COMMAND>"}),
        (137, "", "", {"state": "failed", "why": "sluice exited 137"}),
    ])
    def test_how_sluices_preview_ended_is_read_from_its_exit_and_its_words(self, code, out, err, ended):
        """"The stack fails to come up" and "The host's sluice has no preview command"."""
        assert plan.preview_ended(code, out, err) == ended


class TestAMergeFreesTheTeam:
    """A team is free for its next bolt once every bolt it holds reads proven and it holds fewer than two (teams.16):
    the merge's end tells the dispatchers then, when a bolt is planned for it (plan.free_now)."""

    def test_the_dispatchers_are_told_once_the_give_would_pass_and_a_bolt_is_planned(self):
        assert plan.free_now(None, "ssh-fix")

    def test_nothing_planned_or_a_give_still_refused_tells_no_one(self):
        assert not plan.free_now(None, None)
        assert not plan.free_now("bolt doctor-rows's unit a has not merged (code)", "ssh-fix")

    def test_the_other_bolts_card_says_what_a_yes_now_frees(self):
        assert plan.frees_note("swc-1", "d") == "A yes now frees swc-1 for d"
        assert plan.frees_note("swc-1", None) == "A yes now frees swc-1, and nothing is planned for it"


class TestWhatAYesFrees:
    """What a yes to a landing frees of its team (teams.16, plan.yes_frees), shared by its rail row and its card."""

    def test_a_team_holding_no_other_bolt_is_free_already(self):
        assert plan.yes_frees("doctor-rows", [], "d") is None
        assert plan.yes_frees("doctor-rows", [("doctor-rows", True)], "d") is None

    def test_while_the_other_is_not_proven_the_team_builds_it(self):
        assert plan.yes_frees("doctor-rows", [("ssh-fix", False)], "d") == ("builds", "ssh-fix")

    def test_once_the_other_is_proven_a_yes_frees_the_team_for_its_next_planned_bolt_or_for_none(self):
        assert plan.yes_frees("doctor-rows", [("ssh-fix", True)], "d") == ("frees", "d")
        assert plan.yes_frees("doctor-rows", [("ssh-fix", True)], None) == ("frees", None)


DRAFT = dict(number=99, draft=True, head=TIP, url="https://github.com/o/k/pull/99")
READY = dict(DRAFT, draft=False)
TAKES = '[branches.main]\nrequired = ["#check-full"]\nremote = "origin"\n\n[branches.main.pull_requests]\nreviews = 0\n'
TAKES_NONE = '[branches.main]\nrequired = ["#check-full"]\nremote = "origin"\n'


def policy(text, origin="yes"):
    """What POLICY prints of a kit's main: GitHub's main holding text, or, with origin "no", its own main holding it."""
    b = base64.b64encode(text.encode()).decode() if text is not None else "-"
    if origin == "no":
        return f"ORIGIN=no\nGITHUB=-\nOWN={OLD}\nAT_GITHUB=-\nAT_OWN={b}\n"
    return f"ORIGIN=yes\nFETCHED=ok\nGITHUB={OLD}\nOWN={OLD}\nAT_GITHUB={b}\nAT_OWN=-\n"


def ran(code, out="", err=""):
    return type("R", (), {"returncode": code, "stdout": out, "stderr": err})()


def gh_list(*pulls):
    import json
    return "RC=0\n" + json.dumps([{"headRefOid": p["head"], "isDraft": p["draft"], "number": p["number"], "url": p["url"]}
                                  for p in pulls]) + "\n"


def gh_marked(rc, words):
    return f"RC={rc}\nSAID={base64.b64encode(words.encode()).decode()}\n"


class TestThePullRequest:
    """A landing's pull request is live only on the user's word (bolt-teams "A landing's pull request is a draft
    whenever the user's word does not stand", "The next landing on the user's word readies the pull request"): what
    crew does to it, decided from facts alone (plan.pull_act), what it says (plan.pull_said), and its reads and marks on
    the team's host, only in a kit whose main takes pull requests (plan.pull_hold)."""
    T = {"name": "crw-5", "machine": "box", "kit": {"name": "k", "main": "/k/main", "dir": "/k", "repo": "o/k"}}

    @pytest.mark.parametrize("pull, want, act", [
        (None, "held", None), (None, "live", None),
        (READY, "held", "draft"), (DRAFT, "held", None),
        (DRAFT, "live", "ready"), (READY, "live", None),
    ])
    def test_what_crew_does_to_it(self, pull, want, act):
        assert plan.pull_act(pull, want) == act

    def test_a_drafted_pull_request_names_its_link_and_what_makes_it_live_again(self):
        assert plan.pull_said("b", READY, "draft", True, "o/k") == (
            "Its pull request https://github.com/o/k/pull/99 is a draft, so no merge into bolt/b lands it; the next crew "
            "bolt submit b, on the user's word, makes it live again.")

    def test_a_readied_pull_request_is_taken_at_the_bolts_head(self):
        assert plan.pull_said("b", DRAFT, "ready", True, "o/k") == (
            "Its pull request https://github.com/o/k/pull/99 is ready for review again, so sluice takes it at the head "
            "bolt/b has now.")

    def test_nothing_marked_says_nothing(self):
        assert plan.pull_said("b", DRAFT, None, True, "o/k") == ""
        assert plan.pull_said("b", None, None, True, "o/k") == ""

    def test_one_gh_could_not_mark_is_named_with_its_words_and_the_command_that_drafts_it(self):
        assert plan.pull_said("b", READY, "draft", "HTTP 403: Resource not accessible", "o/k") == (
            "crew could not make bolt/b's pull request https://github.com/o/k/pull/99 a draft: HTTP 403: Resource not "
            "accessible; until it is one, the next merge into bolt/b lands it: gh pr ready 99 -R o/k --undo makes it one.")
        assert plan.pull_said("b", DRAFT, "ready", "HTTP 403: Resource not accessible", "o/k") == (
            "crew could not make bolt/b's pull request https://github.com/o/k/pull/99 ready for review: HTTP 403: Resource "
            "not accessible; sluice takes no draft into main's queue, so nothing is submitted.")

    def hold(self, monkeypatch, said, outs, want="held"):
        """pull_hold of bolt b, POLICY saying said on the team's host box and each script crew runs there answering in
        turn from outs; what ran kept as self.ran."""
        self.ran = []
        monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: self.ran.append((script, host, args)) or said)
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: self.ran.append((argv[2], host, tuple(argv[4:]))) or outs.pop(0))
        return plan.pull_hold({}, self.T, "b", want)

    def test_a_ready_one_is_drafted_on_the_teams_host(self, monkeypatch):
        got = self.hold(monkeypatch, policy(TAKES), [ran(0, gh_list(READY)), ran(0, gh_marked(0, '✓ Pull request o/k#99 is converted to "draft"'))])
        assert got == (READY, "draft")
        assert self.ran == [(plan.POLICY, "box", ("/k/main", ".config/sluice.toml")), (plan.PULL, "box", ("o/k", "b")),
                            (plan.PULL_MARK, "box", ("o/k", "99", "draft"))]

    def test_a_draft_is_readied_when_the_users_word_stands(self, monkeypatch):
        assert self.hold(monkeypatch, policy(TAKES), [ran(0, gh_list(DRAFT)), ran(0, gh_marked(0, "✓"))], "live") == (DRAFT, "ready")
        assert self.ran[-1] == (plan.PULL_MARK, "box", ("o/k", "99", "ready"))

    def test_one_already_as_wanted_or_none_marks_nothing(self, monkeypatch):
        assert self.hold(monkeypatch, policy(TAKES), [ran(0, gh_list(DRAFT))]) == (DRAFT, None)
        assert self.hold(monkeypatch, policy(TAKES), [ran(0, gh_list())], "live") == (None, None)
        assert [s for s, _, _ in self.ran] == [plan.POLICY, plan.PULL]

    @pytest.mark.parametrize("said", [policy(TAKES_NONE), policy(None), policy(TAKES, origin="no")])
    def test_a_kit_that_takes_no_pull_requests_or_has_no_github_is_asked_nothing(self, monkeypatch, said):
        """bolt-teams "A kit that takes no pull requests is asked nothing": no policy, no table, or no origin."""
        assert self.hold(monkeypatch, said, []) == (None, None)
        assert [s for s, _, _ in self.ran] == [plan.POLICY]

    def test_a_listing_gh_refuses_is_refused_with_the_command_that_drafts_it(self, monkeypatch):
        with pytest.raises(plan.Refusal) as e:
            self.hold(monkeypatch, policy(TAKES), [ran(0, "RC=1\n", "HTTP 401: Bad credentials (https://api.github.com/graphql)\n")])
        assert str(e.value) == (
            "crew can't read o/k's open pull request from bolt/b into main: gh exited 1: HTTP 401: Bad credentials "
            "(https://api.github.com/graphql); until bolt/b's pull request into main is a draft, the next merge into bolt/b "
            "may land it: gh pr ready bolt/b -R o/k --undo makes it one")
        with pytest.raises(plan.Refusal, match="; nothing is submitted$"):
            self.hold(monkeypatch, policy(TAKES), [ran(0, "RC=1\n", "HTTP 401: Bad credentials\n")], "live")

    def test_a_host_that_does_not_answer_is_named(self, monkeypatch):
        with pytest.raises(plan.Refusal, match="^crew can't list o/k's pull requests on box: ssh: connect to host box port 22: timed out; "):
            self.hold(monkeypatch, policy(TAKES), [ran(255, "", "ssh: connect to host box port 22: timed out\n")])

    def test_a_mark_gh_refuses_is_refused_naming_the_pull_request(self, monkeypatch):
        with pytest.raises(plan.Refusal) as e:
            self.hold(monkeypatch, policy(TAKES), [ran(0, gh_list(READY)), ran(0, gh_marked(1, "HTTP 403: Resource not accessible"))])
        assert str(e.value) == plan.pull_said("b", READY, "draft", "HTTP 403: Resource not accessible", "o/k")

    def test_a_policy_crew_cannot_read_marks_nothing(self, monkeypatch):
        with pytest.raises(plan.Refusal, match="cannot fetch k from GitHub on box"):
            self.hold(monkeypatch, "ORIGIN=yes\nFETCHED=fatal: could not read\nGITHUB=-\nOWN=-\n", [])
        assert [s for s, _, _ in self.ran] == [plan.POLICY]


class TestAgeAndSplit:
    """run-record "A bolt's landing entry records its time by holder" (plan.20): what plan.landing_split gives the
    bolt.land entry of a bolt a team held, from the run record and sluice's record of its submissions as HISTORY prints
    it on the team's host (plan.history_read), recorded by sluice 0.51.3 (tests/py/sluice-0.51.3/)."""

    RECORDED = pathlib.Path(__file__).parent / "sluice-0.51.3"

    @staticmethod
    def printed(*lines):
        return "\n".join(f"{rc} x{base64.b64encode(out.encode()).decode()} x{base64.b64encode(err.encode()).decode()}" for rc, out, err in lines)

    def test_sluices_record_of_the_bolt_and_its_landing_on_main_is_read_as_the_gather_reads_it(self):
        out = self.printed((0, (self.RECORDED / "status-bolt-all.json").read_text(), ""), (0, (self.RECORDED / "status-main-all.json").read_text(), ""))
        subs, why = plan.history_read(out, "crew-costs-an-idle-host-nothing")
        assert why is None and [(s["id"], s["branch"], s["state"]) for s in subs] == [
            (356, "bolt/crew-costs-an-idle-host-nothing", "landed"), (357, "bolt/crew-costs-an-idle-host-nothing", "landed"),
            (358, "bolt/crew-costs-an-idle-host-nothing", "withdrawn"), (359, "bolt/crew-costs-an-idle-host-nothing", "withdrawn"),
            (361, "bolt/crew-costs-an-idle-host-nothing", "landed"), (362, "bolt/crew-costs-an-idle-host-nothing", "landed"),
            (363, "main", "landed")]

    def test_a_branch_sluice_holds_no_record_of_is_none_and_one_it_refuses_or_a_print_crew_cant_read_says_why(self):
        missing = (self.RECORDED / "status-not-found.json").read_text().replace("bolt/no-such-bolt-here", "bolt/b")
        assert plan.history_read(self.printed((1, missing, ""), (0, '{"branch": "main", "submissions": []}', "")), "b") == ([], None)
        refused = self.printed((0, '{"branch": "bolt/b", "submissions": []}', ""), (2, "", "error: unexpected argument '--all' found\n"))
        assert plan.history_read(refused, "b") == (None, "sluice status main exited 2: error: unexpected argument '--all' found")
        assert plan.history_read("", "b")[1] == "sluice's record of bolt/b and main was not printed whole on the team's host"
        assert plan.history_read(self.printed((0, '{"submissions": []}', "")) + "\n0 nonsense", "b")[1] == (
            "sluice's record of main was printed as crew can't read it: 0 nonsense")

    # b, given to swb-1: its code ran 200 minutes, its landing card was open 125, nothing of it was held 20, and its
    # landing #9 stood in sluice 25 minutes until sluice landed it, 6h 10m after the give.
    PLAN = plan.Plan("%rec: Bolt\n\nBolt: b\nRepo: switchboard-kit\nTeam: swb-1\n\n%rec: Unit\n\nUnit: a\nRepo: switchboard-kit\nBolt: b\n")
    ENTRIES = [{"Act": "bolt.give", "On": ["bolt/b", "team/swb-1"], "At": at(0)},
               {"Act": "stage.start", "On": ["stage/a/code", "unit/a", "agent/swb-1-unit-1"], "At": at(0)},
               {"Act": "stage.end", "On": ["stage/a/code", "unit/a", "agent/swb-1-unit-1"], "At": at(200)},
               {"Act": "card.post", "On": ["bolt/b"], "Card": "req_l", "Key": "land/b", "By": "swb-1-conductor", "At": at(200)},
               {"Act": "card.close", "On": ["land/b"], "Card": "req_l", "Key": "land/b", "State": "closed", "At": at(325)}]
    LANDED = [{"id": 9, "branch": "main", "head": None, "state": "landed", "submitted": at(345), "told": at(370), "worktree": "pull/4",
               "pull_head": "bolt/b"}]

    def test_a_bolt_lands_with_its_age_and_split_to_sluices_landing(self):
        later = START + datetime.timedelta(hours=9)
        assert plan.landing_split(self.ENTRIES, self.PLAN, self.PLAN.bolt("b"), "chuck-herdr-alpha", "switchboard-kit", (self.LANDED, None), later) == {
            "Age": "370", "Split": "team 200, kit 25, user 125, hold 0, nobody 20"}

    def test_a_bolt_no_landing_of_which_landed_is_timed_to_the_entry(self):
        now = START + datetime.timedelta(minutes=330)
        got = plan.landing_split(self.ENTRIES, self.PLAN, self.PLAN.bolt("b"), "chuck-herdr-alpha", "switchboard-kit", ([], None), now)
        assert got == {"Age": "330", "Split": "team 200, kit 0, user 125, hold 0, nobody 5"}

    def test_sluices_record_that_cant_be_read_or_a_give_that_cant_leaves_both_off(self):
        """sluice status fails on the team's host as b's landing is recorded."""
        later = START + datetime.timedelta(hours=9)
        b = self.PLAN.bolt("b")
        assert plan.landing_split(self.ENTRIES, self.PLAN, b, "chuck-herdr-alpha", "switchboard-kit",
                                  (None, "sluice status main exited 1: sluice is not running here"), later) == {}
        assert plan.landing_split(self.ENTRIES[1:], self.PLAN, b, "chuck-herdr-alpha", "switchboard-kit", (self.LANDED, None), later) == {}

"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host, read from main now (plan.18), and of
sluice's own record of the submission when sluice itself failed with the bolt not on main (plan.submission_of); what
plan.deleted_said makes of sluice's delete of the bolt's branch at crew bolt land (plan.19); and its landing card,
raised by crew once the bolt reads proven, held by a fix and closed at the landing (record 0031 §1)."""
import base64
import json
import pathlib

import pytest

import plan

OLD, NEW, TIP = "a" * 40, "b" * 40, "c" * 40
SIGNAL = "sluice: releasing try/abc1234: its command failed"


def said(rc, new=NEW, kept="''", why="''", level="yes", sluice="", github=None, fetched="ok", held="yes", tip=TIP):
    """What LANDING prints after sluice's outcome: the kit's mains after a fresh fetch (MAINS), whether each holds the
    tip that was submitted, then its assignments, sluice's last line base64. With github, a kit with an origin whose
    GitHub main is then at github, judged by HELD_GITHUB, the host's own main at new; else one with none, its own main at
    new, judged by HELD_OWN."""
    mains = (f"ORIGIN=yes\nFETCHED={fetched}\nGITHUB={github}\nOWN={new}\nHELD_GITHUB={held}\nHELD_OWN=no\n" if github else
             f"ORIGIN=no\nGITHUB=-\nOWN={new}\nHELD_GITHUB=-\nHELD_OWN={held}\n")
    words = base64.b64encode(sluice.encode()).decode()
    return mains + f"RC={rc} TIP={tip} OLD={OLD} KEPT={kept} WHY={why} LEVEL={level} SAID={words}\n"


def landing(out, marked="", name="k", sub=None, again=0):
    return plan.landing_said("b", name, "h", out, OLD, marked, sub, again)


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
    landed, words = landing(said(2, new=OLD))
    assert not landed
    assert words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
    assert "the team takes main into it by a submission to the bolt" in words


def test_checks_that_failed_land_nothing():
    assert landing(said(1, new=OLD))[1].startswith("bolt/b did not land: main's checks failed on it")


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
        False, "crew can't read what the submission of bolt/b to k's main came to: wt: command not found")
    for out in (said(0).replace("HELD_OWN=yes", "HELD_OWN=maybe"), said(0).replace("SAID=", "SAID=%%%"),
                f"RC=0 OLD={OLD} NEW={NEW} KEPT='' LEVEL=yes MARKED=yes\n"):
        assert landing(out)[1].startswith("crew can't read what the submission of bolt/b to k's main came to: "), out


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

    @pytest.mark.parametrize("rc, why", [
        (0, "the submission exited 0"), (1, "main's checks failed on it"), (2, "sluice refused it or found a conflict"),
        (4, "it was withdrawn while it waited"), (64, "sluice could not read its command line"),
        (130, "the submission was stopped"), (5, "the submission exited 5")])
    def test_githubs_main_did_not_move(self, rc, why):
        """"GitHub's main did not move": the bolt did not land and main is where it was, whatever sluice exited but 3,
        sluice itself failing, which its record of the submission decides (TestSluiceItselfFailed)."""
        landed, words = landing(said(rc, new=OLD, github=OLD, held="no", level="''"))
        assert not landed and words.startswith(f"bolt/b did not land: {why}, and main is where it was. Tell the bolt's conductor")

    def test_main_moved_but_not_with_the_bolt(self):
        """"Main moved, but not with the bolt": another landing moved it; where main is now is named, and not that it
        is where it was."""
        landed, words = landing(said(2, new=OLD, github=NEW, held="no", level="''"))
        assert not landed
        assert words.startswith("bolt/b did not land: sluice refused it or found a conflict; k's main moved to bbbbbbb without it. "
                                "Tell the bolt's conductor sluice's words above")
        assert "main is where it was" not in words

    def test_github_cant_be_read_after_the_submission(self):
        """"GitHub can't be read after the submission": crew can't tell, naming the fetch's words and sluice's exit,
        and says neither that the bolt landed nor that main is where it was."""
        fetched = "fatal: unable to access 'https://github.com/o/k/': Could not resolve host: github.com"
        landed, words = landing(said(3, new=OLD, github=OLD, fetched=fetched, level="''"))
        assert (landed, words) == (False, f"crew can't tell whether bolt/b landed on k's main: cannot fetch k from GitHub on h, "
                                          f"so cannot read its main now: {fetched}; the submission exited 3.")
        assert landing(said(3, new=OLD, github="-", level="''"))[1] == (
            "crew can't tell whether bolt/b landed on k's main: k's GitHub has no main, fetched on h; the submission exited 3.")

    def test_a_kit_with_no_origin_is_judged_by_its_own_main(self):
        """"A kit with no origin": its own main, before and after, and whether it holds the bolt's tip."""
        assert landing(said(0))[0]
        assert landing(said(3, sluice=SIGNAL))[1].startswith(
            f"bolt/b landed on k's main at bbbbbbb: now crew bolt land b. sluice exited 3 after its push: {SIGNAL}.")
        assert landing(said(0, held="no"))[1].startswith("bolt/b did not land: the submission exited 0; k's main moved to bbbbbbb without it.")


STATUS = json.loads((pathlib.Path(__file__).parent / "sluice-0.36.4" / "status-all.json").read_text())
HEADS = {s["state"]: s["head"] for s in STATUS["submissions"]}  # one recorded submission in each state sluice held
FAILED = "sluice: a round of main failed: its lock could not be taken"


def listing(*subs):
    """What SUBMISSIONS prints when sluice 0.36.4 lists main's submissions: the recorded listing, with subs added."""
    return json.dumps(dict(STATUS, submissions=STATUS["submissions"] + list(subs)))


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
            "conflict": {"id": 137, "state": "conflict"}, "withdrawn": {"id": 148, "state": "withdrawn"},
            "landed": {"id": 153, "state": "landed"}, "testing": {"id": 160, "state": "testing"}}
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

    @pytest.mark.parametrize("state, words", [("failed", "blamed for a check that failed"), ("conflict", "in conflict"),
                                              ("withdrawn", "withdrawn")])
    def test_it_did_not_land_only_when_its_record_has_it_out(self, state, words):
        sub = {"id": 160, "state": state}
        landed, said_ = landing(self.TESTING, sub=sub)
        assert not landed and said_.startswith(f"bolt/b did not land: sluice itself failed, and its record has #160 {words}, and "
                                               "main is where it was. Tell the bolt's conductor sluice's words above")
        assert plan.wait_again(sub, 0) is None

    def test_crew_cant_tell_when_the_record_has_it_landed_has_none_or_cant_be_read(self):
        tip = HEADS["testing"][:7]
        assert landing(self.TESTING, sub={"id": 160, "state": "landed"}) == (False, (
            f"crew can't tell whether bolt/b landed: sluice itself failed ({FAILED}), its record has #160 landed, and k's main "
            f"now, aaaaaaa, does not hold bolt/b's tip {tip}."))
        assert landing(self.TESTING, sub=f"sluice records no submission of {tip} to main") == (False, (
            f"crew can't tell whether bolt/b will land on k's main: sluice itself failed ({FAILED}), k's main now, aaaaaaa, does "
            f"not hold bolt/b's tip {tip}, and sluice records no submission of {tip} to main."))
        assert landing(self.TESTING)[1].endswith("and crew has not read sluice's record of the submission.")
        for sub in ({"id": 160, "state": "landed"}, "sluice status main --all exited 255", None):
            assert "did not land" not in landing(self.TESTING, sub=sub)[1] and plan.wait_again(sub, 0) is None

    def test_a_submission_still_standing_after_crew_waited_again_each_time_sluice_failed_is_said_so(self):
        sub = {"id": 160, "state": "testing"}
        assert plan.wait_again(sub, plan.AGAIN) is None
        assert landing(self.TESTING, sub=sub, again=plan.AGAIN) == (False, (
            f"crew can't tell whether bolt/b will land on k's main: sluice itself failed again each of the {plan.AGAIN} times "
            f"crew waited on #160, which its record still has under test, and k's main now, aaaaaaa, does not hold bolt/b's tip "
            f"{HEADS['testing'][:7]}. That is sluice's to report; crew bolt submit b submits it again."))


class TestTheSubmission:
    """crew bolt submit (plan.16, plan.18): main now read before the submission, refusing when it can't be, the bolt
    decided by landing_said against it, its branch marked only once it landed, and the landing recorded at main now."""
    T = {"name": "swb-1", "machine": "box", "kit": {"name": "k", "main": "/k/main", "dir": "/k"}}
    BEFORE = f"ORIGIN=yes\nFETCHED=ok\nGITHUB={OLD}\nOWN={OLD}\nSUBMISSION_GITHUB=\nSUBMISSION_OWN=\n"

    def submit(self, monkeypatch, before, outs):
        """bolt_submit of bolt b on the team's host box, MAIN saying before there, and each script crew runs there
        answering in turn from outs; what ran, and what was recorded, kept as self.ran and self.emitted when it refuses,
        and the words each script was given after its own, as self.words."""
        ran, emitted, words = self.ran, self.emitted, self.words = [], [], []
        monkeypatch.setattr(plan, "CONTEXT", {})
        monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
        monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, type("P", (), {"bolt": lambda s, n: {"Bolt": n}})()))
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: self.T)
        monkeypatch.setattr(plan, "READ", type("R", (), {"drop_kit": lambda s, h, m: None})())
        monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: ran.append(("host_run", script, host)) or before)
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: ran.append(("on_machine", argv[2], host))
                            or words.append(argv[4:]) or outs.pop(0))
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on, why: emitted.append((label, act, on, why)))
        monkeypatch.setenv("CREW_AGENT", "wldn-ops")
        plan.bolt_submit({}, type("A", (), {"bolt": "b"})())
        return ran, emitted

    def test_github_cant_be_read_before_the_submission(self, monkeypatch):
        """"GitHub can't be read before the submission": refused with the fetch's words, nothing submitted and no
        landing worktree made, since LANDING never runs."""
        before = f"ORIGIN=yes\nFETCHED=fatal: could not read from remote repository\nGITHUB={OLD}\nOWN={OLD}\n"
        ran = []
        monkeypatch.setattr(plan.crew, "on_machine", lambda *a: ran.append(a) or pytest.fail("crew ran a script past the refusal"))
        with pytest.raises(plan.Refusal, match="cannot fetch k from GitHub on box, so cannot read its main now: fatal: could not "
                                               "read from remote repository"):
            self.submit(monkeypatch, before, [])
        assert ran == []

    def test_a_bolt_that_landed_is_marked_and_recorded_at_main_now(self, monkeypatch, capsys):
        """The signal's case through the command: the mark is set once crew has read the bolt landed, and the landing
        recorded at GitHub's commit, not the host's own."""
        out = said(3, new=OLD, github=NEW, level="''", sluice=SIGNAL)
        done = lambda o: type("R", (), {"returncode": 0, "stdout": o, "stderr": ""})()
        ran, emitted = self.submit(monkeypatch, self.BEFORE, [done(out), done("MARKED=yes\n")])
        assert ran == [("host_run", plan.MAIN, "box"), ("on_machine", plan.LANDING, "box"), ("on_machine", plan.LANDED_MARK, "box")]
        assert emitted == [("wldn", "bolt.submit", ["bolt/b"], "bolt(b): landed on main at bbbbbbb")]
        assert capsys.readouterr().out.startswith("bolt/b landed on k's main at bbbbbbb: now crew bolt land b. sluice exited 3")

    def test_a_mark_crew_could_not_set_is_named_in_the_hosts_words_and_the_landing_stands(self, monkeypatch, capsys):
        out = said(0, github=NEW)
        r = lambda code, o, e="": type("R", (), {"returncode": code, "stdout": o, "stderr": e})()
        _, emitted = self.submit(monkeypatch, self.BEFORE, [r(0, out), r(255, "", "ssh: connect to host box port 22: timed out\n")])
        assert capsys.readouterr().out.strip() == (
            "bolt/b landed on k's main at bbbbbbb: now crew bolt land b. crew could not mark bolt/b landed: ssh: connect to host "
            "box port 22: timed out.")
        assert emitted

    def test_a_bolt_that_did_not_land_is_neither_marked_nor_recorded(self, monkeypatch):
        done = type("R", (), {"returncode": 0, "stdout": said(2, new=OLD, github=OLD, held="no", level="''"), "stderr": ""})()
        with pytest.raises(plan.Refusal, match="bolt/b did not land: sluice refused it or found a conflict, and main is where it was"):
            self.submit(monkeypatch, self.BEFORE, [done])
        assert [s for _, s, _ in self.ran] == [plan.MAIN, plan.LANDING] and self.emitted == []

    def test_a_submission_sluice_failed_on_is_waited_on_again_and_lands(self, monkeypatch, capsys):
        """sluice itself fails while the submission waits, GitHub's main not holding the bolt's tip: its record, read
        on the team's host, has it under test, so crew says so and waits on it again by LANDING with its id and the tip
        it submitted, and the bolt lands from that wait, marked and recorded as any landing."""
        r = lambda o: type("R", (), {"returncode": 0, "stdout": o, "stderr": ""})()
        failed = said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=HEADS["testing"])
        ran, emitted = self.submit(monkeypatch, self.BEFORE, [r(failed), r(listing()), r(said(0, github=NEW, tip=HEADS["testing"])),
                                                              r("MARKED=yes\n")])
        assert [s for _, s, _ in ran] == [plan.MAIN, plan.LANDING, plan.SUBMISSIONS, plan.LANDING, plan.LANDED_MARK]
        assert self.words[:3] == [["/k/main", "/k/places/land-b", "b", "wldn-ops"], ["/k/main"],
                                   ["/k/main", "/k/places/land-b", "b", "wldn-ops", "160", HEADS["testing"]]]
        assert capsys.readouterr().out == (
            f"sluice itself failed ({FAILED}), but its record has bolt/b's submission, #160, under test on k's main, which does "
            "not hold it yet: crew waits on it again (sluice wait 160).\nbolt/b landed on k's main at bbbbbbb: now crew bolt land b.\n")
        assert emitted == [("wldn", "bolt.submit", ["bolt/b"], "bolt(b): landed on main at bbbbbbb")]

    def test_a_submission_sluice_failed_on_that_its_record_has_out_did_not_land(self, monkeypatch):
        r = lambda o: type("R", (), {"returncode": 0, "stdout": o, "stderr": ""})()
        failed = said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=HEADS["conflict"])
        with pytest.raises(plan.Refusal, match=r"bolt/b did not land: sluice itself failed, and its record has #137 in conflict, and main is where it was"):
            self.submit(monkeypatch, self.BEFORE, [r(failed), r(listing())])
        assert [s for _, s, _ in self.ran] == [plan.MAIN, plan.LANDING, plan.SUBMISSIONS] and self.emitted == []

    def test_a_submission_sluice_fails_on_each_time_is_waited_on_again_as_many_times_as_crew_allows(self, monkeypatch):
        r = lambda o: type("R", (), {"returncode": 0, "stdout": o, "stderr": ""})()
        failed = said(3, new=OLD, github=OLD, held="no", level="''", sluice=FAILED, tip=HEADS["testing"])
        with pytest.raises(plan.Refusal, match=f"sluice itself failed again each of the {plan.AGAIN} times crew waited on #160"):
            self.submit(monkeypatch, self.BEFORE, [r(failed), r(listing())] * (plan.AGAIN + 1))
        assert [s for _, s, _ in self.ran].count(plan.LANDING) == plan.AGAIN + 1 and self.emitted == []


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

"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host, read from main now (plan.18); what
plan.deleted_said makes of sluice's delete of the bolt's branch at crew bolt land (plan.19); and its landing card,
raised by crew once the bolt reads proven, held by a fix and closed at the landing (record 0031 §1)."""
import argparse
import base64
import pathlib

import pytest

import plan

OLD, NEW, TIP = "a" * 40, "b" * 40, "c" * 40
SIGNAL = "sluice: releasing try/abc1234: its command failed"


def said(rc, new=NEW, kept="''", why="''", level="yes", sluice="", github=None, fetched="ok", held="yes"):
    """What LANDING prints after sluice's outcome: the kit's mains after a fresh fetch (MAINS), whether each holds the
    tip that was submitted, then its assignments, sluice's last line base64. With github, a kit with an origin whose
    GitHub main is then at github, judged by HELD_GITHUB, the host's own main at new; else one with none, its own main at
    new, judged by HELD_OWN."""
    mains = (f"ORIGIN=yes\nFETCHED={fetched}\nGITHUB={github}\nOWN={new}\nHELD_GITHUB={held}\nHELD_OWN=no\n" if github else
             f"ORIGIN=no\nGITHUB=-\nOWN={new}\nHELD_GITHUB=-\nHELD_OWN={held}\n")
    words = base64.b64encode(sluice.encode()).decode()
    return mains + f"RC={rc} TIP={TIP} OLD={OLD} KEPT={kept} WHY={why} LEVEL={level} SAID={words}\n"


def landing(out, marked="", name="k"):
    return plan.landing_said("b", name, "h", out, OLD, marked)


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


class TestARefusedLandingIsRecordedInSluicesWords:
    """rail-cards "A refused landing is held on its row", crew-rail "A refused landing", Decision 6: what a bolt.submit
    that did not land is recorded refused with, which its row, its rail line and the card's close say, is sluice's own
    last line when it exited non-zero and said any; else crew's for why and where main is. Never what crew tells ops
    in its terminal, "sluice's words above" pointing at nothing on a card, nor the worktree it kept."""

    def recorded(self, out):
        return plan.landing_said("b", "k", "h", out, OLD, recorded=True)

    def test_sluices_words_are_recorded(self):
        conflict = "sluice: bolt/b conflicts with main"
        for out in (said(2, new=OLD, sluice=conflict), said(2, new=OLD, github=OLD, held="no", level="''", sluice=conflict),
                    said(2, new=OLD, sluice=conflict, kept="/k/places/land-b", why="busy")):
            assert self.recorded(out) == (False, conflict), out
        assert self.recorded(said(1, new=OLD, sluice="sluice: bolt/b failed main's checks: t-cards"))[1] == (
            "sluice: bolt/b failed main's checks: t-cards")

    def test_crews_words_when_sluice_said_nothing(self):
        assert self.recorded(said(1, new=OLD)) == (False, "bolt/b did not land: main's checks failed on it, and main is where it was.")
        assert self.recorded(said(2, new=OLD, kept="/k/places/land-b", why="busy"))[1] == (
            "bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")

    def test_crews_words_when_sluice_exited_0(self):
        """sluice's words of a submission it ended well are no refusal: main moving without the bolt is crew's to say."""
        assert self.recorded(said(0, held="no", sluice="sluice: #7 bolt/b landed on main"))[1] == (
            "bolt/b did not land: the submission exited 0; k's main moved to bbbbbbb without it.")

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

    @pytest.mark.parametrize("rc, why", [
        (0, "the submission exited 0"), (1, "main's checks failed on it"), (2, "sluice refused it or found a conflict"),
        (3, "sluice itself failed"), (4, "it was withdrawn while it waited"), (64, "sluice could not read its command line"),
        (130, "the submission was stopped"), (5, "the submission exited 5")])
    def test_githubs_main_did_not_move(self, rc, why):
        """"GitHub's main did not move": the bolt did not land and main is where it was, whatever sluice exited."""
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


def ran_as(code, out="", err=""):
    return type("R", (), {"returncode": code, "stdout": out, "stderr": err})()


QUEUED = ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID=7 SAID={base64.b64encode(b'sluice: queued #7').decode()}\n", "sluice: queued #7\n")


class TestTheSubmission:
    """crew bolt submit <bolt>... (plan.16, plan.18, Decision 6, bolt-teams): each bolt's main now read before its
    submission and its landing pull request made live, the submission queued (SUBMIT), its outcome waited on a call at
    a time (WAIT) and its end read (LANDED), the bolt decided by landing_said against main now, its branch marked only
    once it landed, the landing recorded at main now and the bolt closed as it lands; one that did not land has its pull
    request drafted and is recorded at the head submitted, the rest going on, and the command exits non-zero naming
    it."""
    T = {"name": "swb-1", "machine": "box", "kit": {"name": "k", "main": "/k/main", "dir": "/k", "repo": "o/k"}}
    BEFORE = f"ORIGIN=yes\nFETCHED=ok\nGITHUB={OLD}\nOWN={OLD}\nSUBMISSION_GITHUB=\nSUBMISSION_OWN=\n"

    def submit(self, monkeypatch, before, outs, bolts=("b",), teams=None, close=None, said=None):
        """bolt_submit of the bolts, held by swb-1 on box unless teams says otherwise, MAIN saying before on each host
        and POLICY said, a policy at main taking no pull requests unless given, and each script crew runs there
        answering in turn from outs; what ran (the script and its bolt, the submission's number or gh's act), what was
        recorded, and which bolts crew bolt land closed, kept on self."""
        ran_, emitted, closed, argvs = self.ran, self.emitted, self.closed, self.argvs = [], [], [], []
        said = said or policy(TAKES_NONE)
        monkeypatch.setattr(plan, "CONTEXT", {})
        monkeypatch.setattr(plan, "default_label", lambda fleet, a: "wldn")
        bolt = lambda s, n: {"Bolt": n, "Repo": "k"}
        monkeypatch.setattr(plan, "locate", lambda *a: ("wldn", None, None, type("P", (), {"bolt": bolt})()))
        monkeypatch.setattr(plan, "bolt_team", lambda fleet, b: (teams or {}).get(b["Bolt"], self.T))
        monkeypatch.setattr(plan, "READ", type("R", (), {"drop_kit": lambda s, h, m: None})())
        monkeypatch.setattr(plan, "host_run", lambda fleet, host, script, *args: ran_.append(("MAIN" if script == plan.MAIN else "POLICY", host))
                            or (before if script == plan.MAIN else said))
        names = {plan.SUBMIT: "SUBMIT", plan.WAIT: "WAIT", plan.LANDED: "LANDED", plan.LANDED_MARK: "MARK", plan.PULL: "PULL",
                 plan.PULL_MARK: "PULL_MARK"}
        at = {plan.SUBMIT: 6, plan.WAIT: 5, plan.LANDED: 6, plan.LANDED_MARK: 5, plan.PULL: 5, plan.PULL_MARK: 6}
        monkeypatch.setattr(plan.crew, "on_machine", lambda fleet, host, argv: argvs.append(argv) or ran_.append((names[argv[2]], argv[at[argv[2]]]))
                            or outs.pop(0))
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on, **f: emitted.append((act, on, f)))
        monkeypatch.setattr(plan.record, "who", lambda: "wldn-ops")
        monkeypatch.setattr(plan, "may_write", lambda fleet, key, a: None)
        monkeypatch.setattr(plan, "bolt_land", close or (lambda fleet, a: closed.append(a.bolt)))
        self.handed = []
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None: self.handed.append(kit))
        plan.bolt_submit({}, argparse.Namespace(bolt=list(bolts), label=None))
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
        """The signal's case through the command: sluice exits 3 after its push, the mark is set once crew has read
        the bolt landed, the landing recorded at GitHub's commit, not the host's own, and the bolt closed."""
        ran_, emitted = self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(3, "{}", f"{SIGNAL}\n"),
                                                               ran_as(0, said(3, new=OLD, github=NEW, level="''", sluice=SIGNAL)),
                                                               ran_as(0, "MARKED=yes\n")])
        assert ran_ == [("MAIN", "box"), ("POLICY", "box"), ("SUBMIT", "b"), ("WAIT", "7"), ("LANDED", "b"), ("MARK", "b")]
        assert emitted == [("bolt.submit", ["bolt/b"], {"why": "bolt(b): landed on main at bbbbbbb", "Head": TIP})]
        out = capsys.readouterr().out
        assert "bolt/b submitted to k's main, sluice's #7" in out
        assert "bolt/b landed on k's main at bbbbbbb: now crew bolt land b. sluice exited 3" in out
        assert self.closed == ["b"]

    def test_a_wait_that_is_still_undecided_is_waited_on_again(self, monkeypatch):
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(5, "{}"), ran_as(5, "{}"), ran_as(0, "{}"),
                                               ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")])
        assert self.scripts() == ["MAIN", "POLICY", "SUBMIT", "WAIT", "WAIT", "WAIT", "LANDED", "MARK"]

    def test_a_mark_crew_could_not_set_is_named_in_the_hosts_words_and_the_landing_stands(self, monkeypatch, capsys):
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)),
                                               ran_as(255, "", "ssh: connect to host box port 22: timed out\n")])
        assert ("bolt/b landed on k's main at bbbbbbb: now crew bolt land b. crew could not mark bolt/b landed: ssh: connect to "
                "host box port 22: timed out.") in capsys.readouterr().out
        assert self.emitted and self.closed == ["b"]

    def handed_landed(self):
        """What crew handed LANDED as sluice's last line, decoded."""
        return base64.b64decode([a for a in self.argvs if a[2] == plan.LANDED][-1][-1]).decode()

    def test_a_bolt_that_did_not_land_is_recorded_at_its_head_and_the_command_exits_non_zero(self, monkeypatch, capsys):
        """Recorded in sluice's words from its wait, which hold its row (rail-cards "A refused landing is held on its
        row"); ops's terminal has crew's, after sluice's own."""
        conflict = "sluice: bolt/b conflicts with main"
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(2, "{}", f"{conflict}\n"),
                                                   ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''", sluice=conflict))])
        assert self.scripts() == ["MAIN", "POLICY", "SUBMIT", "WAIT", "LANDED", "POLICY"] and self.closed == [] and self.handed == ["k"]
        assert self.handed_landed() == conflict
        (act, on, f), = self.emitted
        assert (act, on, f["Head"], f["refused"]) == ("bolt.submit", ["bolt/b"], TIP, conflict)
        err = capsys.readouterr().err
        assert conflict in err and "bolt/b did not land: sluice refused it or found a conflict, and main is where it was. Tell" in err

    def test_a_submission_sluice_refused_at_once_is_recorded_in_its_words(self, monkeypatch, capsys):
        """sluice refused the submission itself, so there is no wait: SUBMIT's last line of what it said is handed to
        LANDED as sluice's, and recorded so."""
        no_gate = "sluice: main has no gate for bolt/b"
        refused = ran_as(0, f"RC=2 TIP={TIP} OLD={OLD} ID= SAID={base64.b64encode(f'{no_gate}\n'.encode()).decode()}\n", f"{no_gate}\n")
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, [refused, ran_as(0, said(2, new=OLD, github=OLD, held="no", level="''", sluice=no_gate))])
        assert self.scripts() == ["MAIN", "POLICY", "SUBMIT", "LANDED", "POLICY"] and self.handed_landed() == no_gate
        (_, _, f), = self.emitted
        assert (f["Head"], f["refused"]) == (TIP, no_gate)
        assert "bolt/b submitted to k's main, sluice queueing nothing" in capsys.readouterr().out

    def test_a_refused_landing_leaves_its_pull_request_a_draft(self, monkeypatch):
        """bolt-teams "A refused landing leaves its pull request a draft": the one sluice's submission left ready is
        drafted before the command answers, its link named with what makes it live again."""
        outs = [ran(0, gh_list()), QUEUED, ran_as(2, "{}"), ran(0, said(2, new=OLD, github=OLD, held="no", level="''")),
                ran(0, gh_list(READY)), ran(0, gh_marked(0, "✓"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["refused"].startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
        assert f["refused"].endswith(" Its pull request https://github.com/o/k/pull/99 is a draft, so no merge into bolt/b "
                                     "lands it; the next crew bolt submit b, on the user's word, makes it live again.")
        assert self.scripts() == ["MAIN", "POLICY", "PULL", "SUBMIT", "WAIT", "LANDED", "POLICY", "PULL", "PULL_MARK"]

    def test_a_landing_whose_submission_failed_leaves_it_a_draft_too(self, monkeypatch):
        outs = [ran(0, gh_list(DRAFT)), ran(0, gh_marked(0, "✓")), ran(2, "", "wt submit needs sluice's wt-submit, which is not on box's path\n"),
                ran(0, gh_list(READY)), ran(0, gh_marked(0, "✓"))]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        (_, _, f), = self.emitted
        assert f["refused"].startswith("bolt/b was not submitted on box: wt submit needs sluice's wt-submit, which is not on "
                                       "box's path. Its pull request ")
        assert self.scripts()[-2:] == ["PULL", "PULL_MARK"]

    def test_the_next_landing_readies_its_draft_before_it_submits(self, monkeypatch, capsys):
        """bolt-teams "The next landing readies the pull request": readied before SUBMIT runs, said, and the landing
        goes on as any landing does."""
        outs = [ran(0, gh_list(DRAFT)), ran(0, gh_marked(0, "✓")), QUEUED, ran_as(0, "{}"), ran(0, said(0, github=NEW)),
                ran(0, "MARKED=yes\n")]
        _, emitted = self.submit(monkeypatch, self.BEFORE, outs, said=policy(TAKES))
        assert self.scripts() == ["MAIN", "POLICY", "PULL", "PULL_MARK", "SUBMIT", "WAIT", "LANDED", "MARK"]
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
        outs = [ran(0, gh_list()), QUEUED, ran_as(1, "{}"), ran(0, said(1, new=OLD, github=OLD, held="no", level="''")),
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
        q = lambda n: ran_as(0, f"RC=0 TIP={TIP} OLD={OLD} ID={n} SAID=\n")
        outs = [q(1), q(2), q(3),
                ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n"),
                ran_as(2, "{}", "sluice: bolt/z conflicts with main\n"), ran_as(0, said(2, new=NEW, github=NEW, held="no")),
                ran_as(0, "{}"), ran_as(0, said(0, github="d" * 40)), ran_as(0, "MARKED=yes\n")]
        with pytest.raises(plan.Stopped):
            self.submit(monkeypatch, self.BEFORE, outs, bolts=("y", "z", "w"))
        assert [r for r in self.ran if r[0] != "POLICY"] == [
            ("MAIN", "box"), ("SUBMIT", "y"), ("MAIN", "box"), ("SUBMIT", "z"), ("MAIN", "box"), ("SUBMIT", "w"),
            ("WAIT", "1"), ("LANDED", "y"), ("MARK", "y"), ("WAIT", "2"), ("LANDED", "z"), ("WAIT", "3"), ("LANDED", "w"), ("MARK", "w")]
        assert self.closed == ["y", "w"]
        assert [("refused" in f) for _, _, f in self.emitted] == [False, True, False]
        assert capsys.readouterr().err.endswith("z did not land, as said above; y and w landed\n")

    def test_bolts_on_two_hosts_submit_the_second_only_once_the_first_has_ended(self, monkeypatch):
        """bolt-teams "Bolts on two hosts"."""
        other = dict(self.T, name="swb-2", machine="mac-studio")
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n"),
                                               QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github="d" * 40)), ran_as(0, "MARKED=yes\n")],
                    bolts=("y", "z"), teams={"z": other})
        assert self.scripts() == ["MAIN", "POLICY", "SUBMIT", "WAIT", "LANDED", "MARK", "MAIN", "POLICY", "SUBMIT", "WAIT", "LANDED", "MARK"]

    def test_a_landed_bolt_crew_could_not_close_is_named_with_the_act_that_closes_it(self, monkeypatch, capsys):
        """bolt-teams "A landed bolt crew could not close"."""
        self.submit(monkeypatch, self.BEFORE, [QUEUED, ran_as(0, "{}"), ran_as(0, said(0, github=NEW)), ran_as(0, "MARKED=yes\n")],
                    close=lambda fleet, a: plan.fail("wldn/main could not be read"))
        assert capsys.readouterr().err.endswith("bolt/b landed and was not closed: wldn/main could not be read; crew bolt land b closes it\n")


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

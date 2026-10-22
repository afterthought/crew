"""crew bolt new|order|drop on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given; which bolt a give hands a team (plan.to_give, plan.holding), and when a bolt lands (plan.land_refusal),
held by a team or by none (plan.unheld_stages, plan.unheld_refusal, plan.builder); and what a give checks and says
around sluice's create of the bolt's branch (plan.give_check, plan.made_said, plan.given_said, plan.ungiven_said).
The branch and worktree give makes and land removes, and the commits every write makes, are the journey's
(t-journey-units and t-journey-land)."""
import base64
import pathlib

import pytest
from facts import FactsWrite, apply, known, plan_text, units_of

import plan

KIT, BOARD = "switchboard-kit", "breadboard-kit"


def fresh():
    return FactsWrite(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("console-pages", KIT, None), ("board-builds", BOARD, None)],
                                units=[("a-console-page", KIT, "console-pages", []), ("a-console-filter", KIT, "console-pages", ["a-console-page"]),
                                       ("lint-once", KIT, "tenant-environments", [])]))


def bolts(w):
    return [b.name() for b in w.plan.bolts()]


def run(w, *dos, stages=None):
    return apply(w, *dos, ctx=known(w, stages=stages))


def refusal(w, do, **kw):
    with pytest.raises(plan.Refusal) as e:
        run(w, do, **kw)
    return str(e.value)


class TestNew:
    def test_adds_a_bolt_last_or_before_one_named_with_its_sources(self):
        w = run(fresh(), 'bolt new apex-zones "Each apex is a zone." --repo switchboard-kit --before console-pages',
                'bolt new last-one "Last." --repo switchboard-kit --source books/x.md')
        assert bolts(w) == ["tenant-environments", "apex-zones", "console-pages", "board-builds", "last-one"]
        assert w.plan.bolt("last-one").all("Source") == ["books/x.md"]

    def test_refuses_a_name_the_plan_has_and_a_kit_no_team_builds(self):
        assert refusal(fresh(), 'bolt new console-pages "again" --repo switchboard-kit') == "wldn/main already has bolt console-pages"
        assert refusal(fresh(), 'bolt new rocs "x" --repo rocs-kit') == "no team of wldn builds rocs-kit, so no plan holds its work"


class TestOrder:
    @pytest.mark.parametrize("how, order", [
        ("--first", ["board-builds", "tenant-environments", "console-pages"]),
        ("--before console-pages", ["tenant-environments", "board-builds", "console-pages"]),
        ("--last", ["tenant-environments", "console-pages", "board-builds"])])
    def test_moves_a_bolt(self, how, order):
        assert bolts(run(fresh(), f"bolt order board-builds {how}")) == order

    def test_a_bolt_never_goes_before_itself(self):
        assert refusal(fresh(), "bolt order console-pages --before console-pages") == "a bolt can't go before itself"


class TestDrop:
    def test_removes_a_bolt_and_its_units(self):
        w = run(fresh(), 'bolt drop console-pages "folded into the portal"')
        assert bolts(w) == ["tenant-environments", "board-builds"]
        assert [u.name() for u in w.plan.units()] == ["lint-once"]

    def test_requeue_queues_its_units_without_their_after(self):
        w = run(fresh(), 'bolt drop console-pages "folded into the portal" --requeue')
        assert units_of(w, repo=KIT) == ["a-console-page", "a-console-filter"]
        assert w.plan.unit("a-console-filter").all("After") == []

    def test_requeue_is_refused_while_a_unit_of_a_held_bolt_has_a_worktree(self):
        assert refusal(fresh(), 'bolt drop tenant-environments "x" --requeue', stages={"lint-once": "construct"}) == (
            "unit lint-once has a worktree at /kit/places/lint-once, and a queued unit has none")

    def test_requeue_is_refused_while_a_units_stage_cannot_be_told(self):
        assert refusal(fresh(), 'bolt drop tenant-environments "x" --requeue', stages={"lint-once": "unknown"}) == (
            "cannot tell unit lint-once's stage: its host did not answer")


class TestGive:
    def test_the_team_gets_its_kits_first_bolt_no_team_holds_or_the_one_named(self):
        p = fresh().plan
        assert plan.to_give(p, None, "swb-2", [KIT], "wldn").name() == "console-pages"
        assert plan.to_give(p, p.bolt("board-builds"), "brd-1", [BOARD], "wldn").name() == "board-builds"

    def test_a_team_holding_two_kits_takes_a_bolt_of_either_the_first_free_in_the_plans_order(self):
        """A team holds its kits (record 0035): slc-1 and flm-1 both hold agentplot/weir."""
        p = fresh().plan
        first = next(b.name() for b in p.bolts() if b.get("Repo") in (KIT, BOARD) and not b.get("Team"))
        assert plan.to_give(p, None, "swb-2", [KIT, BOARD], "wldn").name() == first
        assert plan.to_give(p, p.bolt("board-builds"), "swb-2", [KIT, BOARD], "wldn").name() == "board-builds"

    @pytest.mark.parametrize("bolt, team, said", [
        ("board-builds", "swb-2", "bolt board-builds is in breadboard-kit, and swb-2 builds switchboard-kit"),
        ("tenant-environments", "swb-2", "bolt tenant-environments is held by swb-1")])
    def test_a_bolt_of_another_kit_or_held_is_refused(self, bolt, team, said):
        p = fresh().plan
        with pytest.raises(plan.Refusal, match=said):
            plan.to_give(p, p.bolt(bolt), team, [KIT], "wldn")

    def test_with_none_free_it_says_so(self):
        with pytest.raises(plan.Refusal, match="wldn/main has no planned bolt in rocs-kit for rcs-1"):
            plan.to_give(fresh().plan, None, "rcs-1", ["rocs-kit"], "wldn")

    def test_a_team_holding_a_bolt_is_given_none_until_it_lands(self):
        p = fresh().plan
        held = p.bolt("tenant-environments")
        assert plan.holding("swb-1", held, p, lambda u: "ready") == (
            "swb-1 holds bolt tenant-environments, whose unit lint-once has not landed (ready)")
        assert plan.holding("swb-1", held, p, lambda u: "landed") == (
            "swb-1 holds bolt tenant-environments, landed but still in the plan: crew bolt land tenant-environments")
        assert plan.holding("swb-1", p.bolt("board-builds"), p, lambda u: "ready") == "swb-1 holds bolt board-builds, which has no units yet"


RECORDED = pathlib.Path(__file__).parent / "sluice-0.36.4"
WHERE = "/kit/main/.config/sluice.toml"
POLICY = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'


def recorded(name):
    """What sluice 0.36.4 printed for a branch command, and its exit, as the folder's README lists them."""
    codes = dict(l.split("\t")[:2] for l in (RECORDED / "README").read_text().splitlines() if "\texit " in l)
    return (RECORDED / name).read_text(), int(codes[name].split()[1])


def deleted(name, policy=POLICY):
    """What BOLT_DELETE prints when sluice says what it recorded: a bolt on GitHub, or on the host for a policy naming
    no remote, its own branch at aaaaaaa."""
    out, code = recorded(name)
    return (f"LOCAL={'a' * 40}\nTRACKED={'a' * 40}\nAT_LOCAL={base64.b64encode(policy.encode()).decode()}\nAT_TRACKED=-\n"
            f"RC={code}\nSAID={base64.b64encode(out.encode()).decode()}\n")


class TestDropDeletes:
    """bolt-plan "A bolt is created, given, dropped and landed through crew" (plan.19, record 0003): a drop of a bolt a
    team holds has sluice delete its branch, asked on the team's host once its worktrees are gone; what is said of it
    (plan.dropped_said). That it is marked dropped and recorded once is the journey's (t-journey-land)."""
    HOST = "chuck-herdr-alpha"
    KEPT = "it is the drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip"

    def said(self, name, policy=POLICY, again=False):
        return plan.dropped_said("b", self.HOST, 0, deleted(name, policy), "", again)

    def test_a_dropped_bolt_whose_tip_main_holds_is_deleted_from_github(self):
        """bolt-plan "Dropping a bolt a team holds"."""
        assert self.said("delete.json") == "sluice deleted bolt/b from GitHub at 22eef85"

    def test_a_dropped_bolt_made_before_is_deleted_from_its_host(self):
        assert self.said("delete.json", '[branches."bolt/*"]\nrequired = ["#check-full"]\n') == (
            "sluice deleted bolt/b from chuck-herdr-alpha at 22eef85")

    def test_a_branch_already_gone_refuses_nothing(self):
        assert self.said("delete-not-found.json") == "bolt/b is gone already: no branch bolt/b"

    def test_a_dropped_bolt_holding_work_main_lacks_is_kept_and_named_as_the_users(self):
        """bolt-plan "A dropped bolt holds work main lacks"."""
        assert self.said("delete-not-landed.json") == (
            "bolt/b is kept on GitHub at aaaaaaa: bolt b was dropped, and sluice did not delete it: bolt/b at "
            f"22eef8585855b2ef8feb0e08177e34d15f131182 has not landed into main; submit it there first; {self.KEPT}")
        assert self.said("delete-not-landed.json", '[branches."bolt/*"]\nrequired = ["#check-full"]\n').startswith(
            "bolt/b is kept on chuck-herdr-alpha at aaaaaaa: bolt b was dropped")

    def test_one_with_a_submission_queued_is_kept_in_sluices_words(self):
        assert self.said("delete-queued.json") == (
            "bolt/b is kept on GitHub at aaaaaaa: bolt b was dropped, and sluice did not delete it: #1 still queued on "
            f"bolt/b; wait for them to land, or withdraw them; {self.KEPT}")

    def test_a_host_that_does_not_answer_names_the_command_for_the_next_read(self):
        """bolt-plan "The drop's host does not answer"."""
        assert plan.dropped_said("b", self.HOST, 255, "", "ssh: connect to host") == (
            "chuck-herdr-alpha did not answer, so sluice was not asked to delete bolt/b: sluice branch delete bolt/b "
            "--into main there; the team's next read asks it")

    def test_words_crew_cannot_read_leave_it_to_the_next_read(self):
        """read.2: what is not sluice's document decides nothing."""
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").startswith(
            "bolt/b may still stand on GitHub: crew can't read what sluice's branch delete said from:")
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").endswith(
            "; the team's next read asks sluice again")

    def test_asked_again_once_main_holds_its_tip(self):
        """bolt-plan "Main comes to hold a dropped bolt's work"."""
        assert self.said("delete.json", again=True) == (
            "bolt/b is removed: main now holds bolt b's tip, and sluice deleted it from GitHub at 22eef85")
        assert self.said("delete-queued.json", again=True) == (
            "bolt/b is still kept: #1 still queued on bolt/b; wait for them to land, or withdraw them")


class TestGiveThroughSluice:
    """bolt-plan "A bolt is created, given, dropped and landed through crew" (plan.19): what a give checks before sluice
    makes the branch, every refusal coming before the plan write, so the plan is unchanged and no branch made; what
    sluice's create says; and a write refused after it, which has sluice delete the branch again."""

    def check(self, text=POLICY, version="sluice 0.36.4 "):
        return plan.give_check(KIT, WHERE, "origin/main", text, "b", version, "chuck-herdr-alpha")

    def test_a_kit_on_github_with_a_sluice_that_makes_branches_gives_on_its_remote(self):
        assert self.check() == "origin"

    def test_a_kit_whose_bolts_have_no_remote_is_refused_naming_the_file_and_the_key(self):
        with pytest.raises(plan.Refusal) as e:
            self.check('[branches."bolt/*"]\nrequired = ["#check-full"]\n')
        assert str(e.value).startswith(f"{KIT} gives bolts only on GitHub, and its {WHERE} on origin/main names no remote")

    def test_a_kit_with_no_bolt_checks_is_refused_first(self):
        with pytest.raises(plan.Refusal, match="names no checks for its bolt branches"):
            self.check('[branches."bolt/*"]\nremote = "origin"\n')

    @pytest.mark.parametrize("version, said", [("sluice 0.18.0 ", "sluice 0.18.0"), ("", "nothing")])
    def test_a_host_whose_sluice_is_older_or_unread_is_refused(self, version, said):
        with pytest.raises(plan.Refusal) as e:
            self.check(version=version)
        assert str(e.value) == ("a bolt is given through sluice 0.20.0 or later, which has `branch create`, and sluice "
                                f"--version on chuck-herdr-alpha said: {said}")

    def test_sluices_create_is_the_commit_it_made_the_branch_at(self):
        assert plan.made_said("b", KIT, "chuck-herdr-alpha", *recorded("create.json")) == "c0da39bae0a5d89da0febc3f46f58607c2ad08a7"

    def test_a_create_sluice_refuses_is_refused_in_its_words(self):
        with pytest.raises(plan.Refusal) as e:
            plan.made_said("b", KIT, "chuck-herdr-alpha", *recorded("create-present.json"))
        assert str(e.value) == (f"sluice did not make bolt/b for {KIT} on chuck-herdr-alpha: bolt/b is already there, at "
                                "c0da39bae0a5d89da0febc3f46f58607c2ad08a7")

    def test_a_give_names_github_the_commit_and_the_teams_host(self):
        assert plan.given_said("swb-1", "b", KIT, "origin", "c0da39bae0a5d89da0febc3f46f58607c2ad08a7", "chuck-herdr-alpha") == (
            f"swb-1 holds b: sluice made bolt/b on GitHub (origin) from {KIT}'s main at c0da39b, built on chuck-herdr-alpha "
            "and merged into only through sluice")

    def test_a_write_refused_after_the_create_has_sluice_delete_the_branch_again(self):
        why = "swb-1 holds bolt c since 1234567"
        assert plan.ungiven_said("b", why, deleted("delete.json"), 0) == (
            f"{why}; sluice deleted bolt/b again, so nothing of the give is left")

    def test_a_delete_sluice_refuses_then_names_the_branch_left_standing(self):
        why = "swb-1 holds bolt c since 1234567"
        assert plan.ungiven_said("b", why, deleted("delete-queued.json"), 0) == (
            f"{why}; and bolt/b, which sluice made for the give, still stands, since sluice did not delete it: #1 still "
            "queued on bolt/b; wait for them to land, or withdraw them")
        assert plan.ungiven_said("b", why, "", 255).endswith("since sluice did not delete it: its delete exited 255: nothing was said")


class TestLand:
    def land(self, stages, outside=(), of=None):
        return plan.land_refusal("console-pages", ["a-console-page", "a-console-filter"],
                                 of or (lambda u: {"stage": stages[u], "why": "its host did not answer"}), list(outside), "wldn")

    def test_lands_once_every_unit_has_landed_and_been_in_a_batch(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "landed"}) is None

    def test_a_unit_not_landed_on_main_refuses_it(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "merged"}) == "unit a-console-filter has not landed on main: it is merged"
        assert self.land({"a-console-page": "unknown", "a-console-filter": "landed"}) == (
            "cannot tell whether unit a-console-page has landed: its host did not answer")

    def test_the_landing_records_the_commit_main_holds_now(self):
        """plan.14, plan.18: the landing records the commit GitHub's main holds after the command's fetch, for a kit with
        an origin, and nothing is refused for the host's own main lagging it (plan.8); what can't be read refuses."""
        github, own = "c" * 40, "d" * 40
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", f"ORIGIN=yes\nFETCHED=ok\nGITHUB={github}\nOWN={own}\n") == (github, None)
        for said in (f"{github} 0 1\n", "", "fatal: bad\n"):
            assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", said) == (
                None, f"crew can't read what switchboard-kit's main on chuck-herdr-alpha holds: {said.strip() or 'nothing was said'}")

    def test_a_bolt_no_team_holds_lands_once_each_units_change_is_on_its_kits_main(self):
        planned = lambda u: {"stage": "ready"}
        of = plan.unheld_stages({"main": ["a-console-page", "a-console-filter"]}, None, planned)
        assert self.land({}, of=of) is None
        of = plan.unheld_stages({"main": ["a-console-page"]}, None, planned)
        assert self.land({}, of=of) == "unit a-console-filter has not landed on main: it is ready"
        of = plan.unheld_stages({"main": ["a-console-page", "a-console-filter"], "chores": []}, None, planned, ["a-console-filter"])
        assert self.land({}, of=of) == "chore a-console-filter has not landed on main: it is ready"
        of = plan.unheld_stages({"main": ["a-console-page"], "chores": ["a-console-filter"]}, None, planned, ["a-console-filter"])
        assert self.land({}, of=of) is None
        of = plan.unheld_stages(None, "chuck-herdr-alpha did not answer", planned)
        assert self.land({}, of=of) == "cannot tell whether unit a-console-page has landed: chuck-herdr-alpha did not answer"

    def test_a_bolt_no_team_holds_is_read_where_a_team_of_the_partition_builds_its_kit(self):
        swb, brd = {"name": "swb-2", "kit": {"name": KIT}}, {"name": "brd-1", "kit": {"name": BOARD}}
        fleet = {"partitions": {"wldn": {"teams": ["swb-2", "brd-1"]}}, "teams": {"swb-2": swb, "brd-1": brd}}
        assert plan.builder(fleet, "wldn", BOARD) is brd and plan.builder(fleet, "wldn", "rocs-kit") is None
        assert plan.unheld_refusal("console-pages", ["a-console-page"], KIT, swb, "wldn") is None
        assert plan.unheld_refusal("console-pages", ["a-console-page"], "rocs-kit", None, "wldn") == (
            "bolt console-pages is held by no team, and no team of wldn builds rocs-kit, so crew can't read its main")
        assert plan.unheld_refusal("console-pages", [], KIT, swb, "wldn") == (
            "bolt console-pages is held by no team and holds no units or chores, so nothing of it has landed")

    def test_a_change_no_batch_has_held_refuses_it(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "landed"}, ["a-console-page", "a-console-filter"]) == (
            "bolt console-pages lands only once every unit's latest change has been in a batch, and a-console-page or "
            "a-console-filter have not: a batch is due for them (crew review wldn)")


class TestQueuedLanding:
    """bolt-teams "A unit during a queued landing" (plan.8, record 0032 §3): no construct, code or merge starts on a
    bolt while its landing's worktree stands with LANDING's process alive in it, the submission in sluice's queue."""
    PATH = "/kit/places/land-b"

    def refusal(self, stage="construct", standing=True, alive=True, kind="unit"):
        return plan.landing_refusal(kind, "u", stage, "b", self.PATH, standing, alive)

    @pytest.mark.parametrize("stage", ["construct", "code", "merge"])
    def test_a_unit_during_a_queued_landing_is_refused_naming_the_landing(self, stage):
        assert self.refusal(stage) == (
            f"bolt b's landing is queued in sluice, submitted from /kit/places/land-b: unit u's {stage} starts once it has "
            "landed or been refused, since what merges into bolt/b meanwhile is left out of main's landing")

    def test_a_chores_code_and_merge_wait_alike(self):
        assert self.refusal("code", kind="chore").startswith("bolt b's landing is queued in sluice, submitted from /kit/places/land-b: chore u's code")

    @pytest.mark.parametrize("stage", ["verify", "settle"])
    def test_a_stage_that_moves_nothing_toward_the_bolt_starts(self, stage):
        assert self.refusal(stage) is None

    def test_once_sluices_outcome_is_in_a_worktree_left_standing_holds_nothing(self):
        # A landing git could not remove, or one stopped, leaves its worktree with no process: the fix that takes main
        # into a refused bolt starts, as does every unit.
        assert self.refusal(alive=False) is None
        assert self.refusal(standing=False, alive=False) is None

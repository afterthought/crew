"""crew bolt new|order|drop on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given; which bolt a give hands a team (plan.to_give, plan.holding), and when a bolt lands (plan.land_refusal),
held by a team or by none (plan.unheld_stages, plan.unheld_refusal, plan.builder).
The branch and worktree give makes and land removes, and the commits every write makes, are the journey's
(t-journey-units and t-journey-land)."""
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
        assert plan.to_give(p, None, "swb-2", KIT, "wldn").name() == "console-pages"
        assert plan.to_give(p, p.bolt("board-builds"), "brd-1", BOARD, "wldn").name() == "board-builds"

    @pytest.mark.parametrize("bolt, team, said", [
        ("board-builds", "swb-2", "bolt board-builds is in breadboard-kit, and swb-2 builds switchboard-kit"),
        ("tenant-environments", "swb-2", "bolt tenant-environments is held by swb-1")])
    def test_a_bolt_of_another_kit_or_held_is_refused(self, bolt, team, said):
        p = fresh().plan
        with pytest.raises(plan.Refusal, match=said):
            plan.to_give(p, p.bolt(bolt), team, KIT, "wldn")

    def test_with_none_free_it_says_so(self):
        with pytest.raises(plan.Refusal, match="wldn/main has no planned bolt in rocs-kit for rcs-1"):
            plan.to_give(fresh().plan, None, "rcs-1", "rocs-kit", "wldn")

    def test_a_team_holding_a_bolt_is_given_none_until_it_lands(self):
        p = fresh().plan
        held = p.bolt("tenant-environments")
        assert plan.holding("swb-1", held, p, lambda u: "ready") == (
            "swb-1 holds bolt tenant-environments, whose unit lint-once has not landed (ready)")
        assert plan.holding("swb-1", held, p, lambda u: "landed") == (
            "swb-1 holds bolt tenant-environments, landed but still in the plan: crew bolt land tenant-environments")
        assert plan.holding("swb-1", p.bolt("board-builds"), p, lambda u: "ready") == "swb-1 holds bolt board-builds, which has no units yet"


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

    def test_the_landing_records_the_commit_main_holds_and_is_refused_on_a_main_behind_githubs(self):
        sha = "c" * 40
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", f"{sha}\n") == (sha, None)
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", f"{sha} 2 0\n") == (sha, None)
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", f"{sha} 0 1\n") == (None, (
            "switchboard-kit's main on chuck-herdr-alpha is 1 commit behind GitHub's (with 0 of its own): rebase it onto "
            "origin/main, check it again, then land; never push it with force"))
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", "") == (
            None, "crew can't read what switchboard-kit's main on chuck-herdr-alpha holds: nothing was said")

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

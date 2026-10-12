"""crew bolt new|order|drop on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given. give and land, which make and remove a bolt's branch and worktree, and the commits every write makes,
are t-bolt's."""
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

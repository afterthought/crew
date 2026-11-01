"""crew unit add|after|order|split|move|drop on the plan (bolt-plan spec): each command applied to a plan in memory,
the stages it reads given, and every refusal it makes there, work a bolt in flight needs (--unblocks, plan.5) among them.
A write to a started bolt launches its work as test_cross.py's cases show. Rebasing a moved unit's branch, removing a dropped unit's place and the commits the writes make are the journey's
(t-journey-fix and t-journey-land)."""
import pytest
from facts import FactsWrite, apply, known, plan_text, units_of

import plan

KIT = "switchboard-kit"
BOLTS = [("tenant-environments", KIT, "swb-1"), ("console-pages", KIT, "swb-2"), ("apex-zones", KIT, None)]
PLANNED = [(b, r, None) for b, r, _ in BOLTS]
TE = "tenant-environments"


@pytest.fixture(autouse=True)
def writer(monkeypatch):
    """A write to a started bolt appends its launches, which name their writer."""
    monkeypatch.setenv("CREW_AGENT", "wldn-planner")


def fresh(units=None, bolts=BOLTS):
    """wldn's plan, tenant-environments and console-pages started and apex-zones planned unless bolts says otherwise."""
    return FactsWrite(plan_text(bolts=bolts, units=units if units is not None else [
        ("a", KIT, TE, []), ("b", KIT, TE, ["a"]), ("c", KIT, TE, []), ("elsewhere", KIT, "console-pages", []), ("later", KIT, None, [])]))


def run(w, *dos, stages=None, taken=()):
    return apply(w, *dos, ctx=known(w, stages=stages, taken=taken))


def refusal(w, do, **kw):
    with pytest.raises(plan.Refusal) as e:
        run(w, do, **kw)
    return str(e.value)


class TestAdd:
    def test_a_unit_goes_at_the_end_of_its_bolt_or_before_one_named(self):
        w = run(fresh(), f'unit add d "Unit d." --bolt {TE} --before b', f'unit add e "Unit e." --bolt {TE}')
        assert units_of(w, TE) == ["a", "d", "b", "c", "e"]

    def test_a_unit_with_no_bolt_goes_in_its_repos_queue(self):
        w = run(fresh(), f'unit add q "Queued." --repo {KIT}')
        assert units_of(w, repo=KIT) == ["later", "q"]

    def test_its_sources_and_after_are_recorded(self):
        w = run(fresh(), f'unit add d "Unit d." --bolt {TE} --after a --source books/x.md')
        assert w.plan.unit("d").all("After") == ["a"] and w.plan.unit("d").all("Source") == ["books/x.md"]

    def test_a_name_the_kits_main_has_or_the_plan_has_is_refused(self):
        assert refusal(fresh(), f'unit add taken "x" --bolt {TE}', taken={"taken"}) == (
            "switchboard-kit's main already has a change named taken, open or archived; pick another name")
        assert refusal(fresh(), f'unit add a "again" --bolt {TE}') == "wldn/main already has unit a"


class TestAfter:
    """On a bolt not started: a started bolt's launched work keeps the After of its launch (test_cross.py, TestReach)."""

    def test_sets_and_clears_a_dependency(self):
        w = run(fresh(bolts=PLANNED), "unit after c a")
        assert w.plan.unit("c").all("After") == ["a"]
        assert run(w, "unit after c --none").plan.unit("c").all("After") == []

    def test_refuses_a_cycle(self):
        assert "cycle" in refusal(run(fresh(bolts=PLANNED), "unit after c a"), "unit after a c")

    def test_refuses_a_unit_of_another_bolt(self):
        assert refusal(fresh(bolts=PLANNED), "unit after c elsewhere").endswith(
            "comes after elsewhere, which is in console-pages, not tenant-environments")


class TestOrder:
    @pytest.mark.parametrize("how, order", [("--first", ["c", "a", "b"]), ("--before b", ["a", "c", "b"]), ("--last", ["a", "b", "c"])])
    def test_moves_a_unit_within_its_bolt(self, how, order):
        assert units_of(run(fresh(), f"unit order c {how}"), TE) == order

    def test_refuses_a_unit_of_another_bolt(self):
        assert "is not in tenant-environments with a" in refusal(fresh(), "unit order a --before elsewhere")


class TestSplit:
    def test_narrows_a_unit_and_adds_the_rest_right_after_it(self):
        w = run(fresh(), 'unit split c "Unit c, narrowed." --into c-rest "The rest of c." --into c-more "More of c."')
        assert units_of(w, TE) == ["a", "b", "c", "c-rest", "c-more"]
        assert w.plan.unit("c").get("Intent") == "Unit c, narrowed."

    @pytest.mark.parametrize("st, said", [("code", "unit a is in code, so it is no longer split; add the remainder as a new unit instead"),
                                          ("merged", "unit a is in merged")])
    def test_is_refused_once_the_unit_is_in_code(self, st, said):
        assert said in refusal(fresh(), 'unit split a "Narrower." --into a-rest "The rest."', stages={"a": st})


class TestMove:
    def test_a_unit_with_no_worktree_goes_to_the_end_of_another_bolt_and_loses_its_after(self):
        w = run(fresh(), "unit move b apex-zones")
        assert w.plan.unit("b").get("Bolt") == "apex-zones" and w.plan.unit("b").all("After") == []
        assert units_of(run(w, f"unit move later {TE}"), TE)[-1] == "later"

    def test_a_unit_already_in_the_bolt_is_refused(self):
        assert "is already in tenant-environments" in refusal(fresh(), f"unit move a {TE}")

    def test_merged_work_does_not_move(self):
        assert "unit c has merged into tenant-environments, so it can't move" in refusal(fresh(), "unit move c console-pages", stages={"c": "merged"})


class TestDrop:
    def test_removes_the_unit(self):
        w = run(fresh(), 'unit drop c "not wanted"')
        assert units_of(w, TE) == ["a", "b"]

    def test_merged_work_is_not_dropped(self):
        assert "unit c has merged into its bolt, so it can't be dropped" in refusal(fresh(), 'unit drop c "not wanted"', stages={"c": "merged"})


class TestUnblocks:
    def test_work_a_started_bolt_needs_goes_ahead_of_its_first_open_unit(self):
        w = run(fresh(), 'unit add zone-first "The zone exists." --bolt tenant-environments --unblocks tenant-environments',
                stages={"a": "merged"})
        assert units_of(w, TE) == ["a", "zone-first", "b", "c"]

    @pytest.mark.parametrize("do, said", [
        ('unit add zone-first "The zone exists." --repo switchboard-kit --unblocks tenant-environments',
         "zone-first unblocks bolt tenant-environments, so it goes into that bolt, ahead of what waits on it, not into the queue"),
        ('unit add zone-first "The zone exists." --bolt console-pages --unblocks tenant-environments', "not into bolt console-pages"),
        ('unit add zone-first "The zone exists." --bolt apex-zones --unblocks apex-zones',
         "zone-first unblocks bolt apex-zones, which is not started, so nothing waits on it: --unblocks names a bolt in flight")])
    def test_anywhere_else_or_for_a_bolt_not_started_is_refused(self, do, said):
        assert said in refusal(fresh(), do)

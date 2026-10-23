"""A proposal's commands (plan.3, plan.4): how its Do lines parse (plan.do_args), which conductors must agree
(plan.touched_by, plan.held_teams), the units the user may leave out and what is applied without them (plan.new_units,
plan.kept), and the plan its commands leave, applied in order to the plan in memory. Writing, recording and telling
the planner are the proposals journey's (t-journey-plan)."""
import pytest
from facts import FactsWrite, apply, plan_text, units_of

import plan

KIT = "switchboard-kit"


def args(*dos):
    return [plan.do_args("wldn", d) for d in dos]


def refused(fn, *a):
    with pytest.raises(plan.Refusal) as e:
        fn(*a)
    return str(e.value), getattr(e.value, "recorded", None)


class TestDoLines:
    def test_a_do_line_that_does_not_parse_is_named_in_shlexs_words(self):
        said, recorded = refused(plan.do_args, "wldn", 'unit add y "Typed ZQXC.')
        assert said == '`unit add y "Typed ZQXC.`: No closing quotation'
        assert "ZQXC" not in recorded

    def test_a_proposal_holds_only_the_plans_commands(self):
        said, recorded = refused(plan.do_args, "wldn", "bolt give swb-1 b")
        assert said.startswith("a proposal holds only the plan's commands (") and said.endswith(", not `bolt give swb-1 b`")

    def test_a_command_naming_another_partition_is_refused_without_its_typed_words(self):
        said, recorded = refused(plan.do_args, "wldn", f'unit add y "Typed ZQXD." --repo {KIT} --label nope')
        assert "names partition nope, and the proposal is wldn's" in said
        assert recorded == "`unit add y` names partition nope, and the proposal is wldn's"

    def test_crew_in_front_is_read_as_the_command(self):
        a = plan.do_args("wldn", f'crew unit add y "Y." --repo {KIT}')
        assert (a.cmd, a.sub, a.unit, a.label) == ("unit", "add", "y", "wldn")


class TestAgreement:
    PLAN = plan.Plan(plan_text(bolts=[("held", KIT, "swb-1"), ("free", KIT, None), ("other", KIT, "swb-2")],
                               units=[("h1", KIT, "held", []), ("f1", KIT, "free", []), ("q1", KIT, None, [])]))

    def test_each_command_touches_the_bolts_it_changes(self):
        touched = plan.touched_by(self.PLAN, args(f'unit add n "N." --bolt free', "unit move q1 held", "unit move h1 queue",
                                                  'bolt new b "B." --repo switchboard-kit', 'unit drop f1 "Gone."'))
        assert touched == [["free"], ["held"], ["held"], [], ["free"]]

    def test_only_the_conductors_of_held_bolts_it_touches_must_agree(self):
        assert plan.held_teams(self.PLAN, plan.flat(plan.touched_by(self.PLAN, args("unit move q1 held", 'unit add n "N." --bolt free')))) == ["swb-1"]


class TestLeftOut:
    DOS = args('unit drop a-drop "Replaced."', 'unit add b-keep "Kept." --bolt clears', 'unit add c-clear "Cleared." --bolt clears',
               "unit order c-clear --first", "unit move q-queued clears")

    def test_the_units_it_makes_new_to_a_bolt_are_those_it_adds_or_moves_in(self):
        assert plan.new_units(self.DOS) == ["b-keep", "c-clear", "q-queued"]

    def test_every_command_concerning_only_a_cleared_unit_is_left_out(self):
        kept = plan.kept(self.DOS, ["c-clear", "q-queued"], 7)
        assert [a.do for a in kept] == ['unit drop a-drop "Replaced."', 'unit add b-keep "Kept." --bolt clears']

    def test_a_kept_command_naming_a_cleared_unit_refuses_the_whole(self):
        dos = args('unit add e-b "First." --bolt clears', 'unit add e-c "Second." --bolt clears --after e-b')
        said, recorded = refused(plan.kept, dos, ["e-b"], 9)
        assert said == '`unit add e-c "Second." --bolt clears --after e-b` names e-b, which the user left out: write the proposal again without it'
        assert recorded == "`unit add e-c` names e-b, which the user left out"
        assert [a.unit for a in plan.kept(dos, ["e-c"], 9)] == ["e-b"]

    def test_a_cleared_unit_the_proposal_does_not_make_new_is_refused(self):
        dos = args('unit add e-b "First." --bolt clears', 'unit amend d-keep "Amended."')
        assert refused(plan.kept, dos, ["d-keep"], 9)[0] == (
            "proposal 9 neither adds nor moves into a bolt d-keep, so the user can't leave it out: the units it may leave out are e-b")


class TestApplied:
    def write(self):
        return FactsWrite(plan_text(bolts=[("clears", KIT, None)],
                                    units=[("a-drop", KIT, "clears", []), ("q-queued", KIT, None, [])]))

    def test_what_the_user_kept_is_applied_in_order(self):
        w = self.write()
        apply(w, *[a.do for a in plan.kept(TestLeftOut.DOS, ["c-clear"], 7)])
        assert units_of(w, "clears") == ["b-keep", "q-queued"]

    def test_a_unit_moved_in_and_left_out_stays_in_the_queue_as_it_was(self):
        w = self.write()
        apply(w, *[a.do for a in plan.kept(TestLeftOut.DOS, ["q-queued", "c-clear"], 7)])
        assert units_of(w, "clears") == ["b-keep"]
        assert units_of(w, repo=KIT) == ["q-queued"]

    def test_a_bolt_made_and_added_to_is_one_plan(self):
        w = apply(self.write(), 'bolt new fresh "Fresh." --repo switchboard-kit', 'unit add f1 "F1." --bolt fresh',
                  'unit add f2 "F2." --bolt fresh --after f1')
        assert units_of(w, "fresh") == ["f1", "f2"]
        assert w.plan.unit("f2").all("After") == ["f1"]

    def test_a_unit_added_twice_is_refused(self):
        w = self.write()
        assert refused(apply, w, 'unit add q-queued "Again." --repo switchboard-kit')[0] == "wldn/main already has unit q-queued"


class TestRecordSources:
    """The decision records a source names (plan.record_refs): by their docs/adr/<number> path, of the kit's repository
    or of the <owner>/<name> right before it, and none named only in words."""
    KIT_REPO = "WilldanGroup/switchboard-kit"

    def refs(self, source):
        return plan.record_refs(source, self.KIT_REPO)

    def test_a_path_with_its_file_name_names_a_record_of_the_kit(self):
        assert self.refs("docs/adr/0033-a-unit-waiting-to-merge-yields-its-slot.md") == [(self.KIT_REPO, 33)]

    def test_a_bare_path_names_it_too(self):
        assert self.refs("docs/adr/0032") == [(self.KIT_REPO, 32)]

    def test_only_the_record_of_a_source_holding_other_pages_is_named(self):
        assert self.refs("docs/adr/0029 (accepted 2026-10-14); docs/architecture/core.md read.5") == [(self.KIT_REPO, 29)]

    def test_a_page_before_a_record_is_no_repository(self):
        assert self.refs("docs/architecture/core.md docs/adr/0001") == [(self.KIT_REPO, 1)]

    def test_owner_and_name_before_it_name_the_repository(self):
        assert self.refs("afterthought/crew:docs/adr/0010-the-plan.md") == [("afterthought/crew", 10)]
        assert self.refs("agentplot/sluice docs/adr/0026 (branch create and delete)") == [("agentplot/sluice", 26)]

    def test_words_other_pages_signals_and_another_folder_name_none(self):
        for source in ("record 0026 point 4", "docs/architecture/plan.md plan.16", "signals/2026-10-19-swancloud-planner-e269e093/01",
                       "other/docs/adr/0001", "docs/adr/00123"):
            assert self.refs(source) == [], source

    def test_a_source_may_name_several_each_once(self):
        assert self.refs("docs/adr/0031 §1; agentplot/sluice:docs/adr/0017; docs/adr/0031 §2") == [
            (self.KIT_REPO, 31), ("agentplot/sluice", 17)]


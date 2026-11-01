"""A proposal's commands (plan.3, plan.4): how its Do lines parse (plan.do_args), the bolts each touches
(plan.touched_by), the units the user may leave out and what is applied without them (plan.new_units, plan.kept), the
plan its commands leave, applied in order to the plan in memory, and a start it holds checked and approved
(plan.check_ops, plan.apply_all). Writing, recording and telling the planner are the proposals journey's
(t-journey-plan)."""
import pytest
from facts import FLEET, FactsWrite, apply, keeping, plan_text, units_of

import plan
import runner

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


class TestTouched:
    PLAN = plan.Plan(plan_text(bolts=[("held", KIT, True), ("free", KIT, None), ("other", KIT, True)],
                               units=[("h1", KIT, "held", []), ("f1", KIT, "free", []), ("q1", KIT, None, [])]))

    def test_each_command_touches_the_bolts_it_changes(self):
        touched = plan.touched_by(self.PLAN, args(f'unit add n "N." --bolt free', "unit move q1 held", "unit move h1 queue",
                                                  'bolt new b "B." --repo switchboard-kit', 'unit drop f1 "Gone."'))
        assert touched == [["free"], ["held"], ["held"], [], ["free"]]


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


class TestRestsOnAccepted:
    """A proposal's new work and the records it rests on (plan.record_items, plan.unaccepted): each named record not
    accepted on its main refuses the proposal with one line naming the work, the record and what main holds."""
    FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio"}},
             "hosts": {"mac-studio": keeping("/w", "WilldanGroup/switchboard-kit")}}
    REPO = "WilldanGroup/switchboard-kit"
    FILE = "docs/adr/0033-a-record.md"

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        """Work moved into a started bolt is launched, and a launch names its writer."""
        monkeypatch.setenv("CREW_AGENT", "wldn-planner")

    def said(self, status="proposed", marked=False, files=(FILE,), kit=KIT, repo=REPO):
        return plan.unaccepted([("unit", "u", kit, repo, 33)], {(repo, 33): {"files": list(files), "status": status, "marked": marked}})

    def test_a_proposed_record_is_refused_naming_the_unit_the_record_and_what_main_holds(self):
        assert self.said() == (
            "crew refuses the proposal: it rests on records the user has not accepted.\n"
            f"  unit u names record 0033 of {KIT}: {KIT}'s main holds it proposed\n"
            "Propose it once each record is accepted on its kit's main.")

    def test_a_rejected_record_is_refused(self):
        assert f"record 0033 of {KIT}: {KIT}'s main holds it rejected" in self.said("rejected")

    def test_an_accepted_record_with_an_amendment_still_proposed_is_refused(self):
        assert "holds it accepted, with an amendment still marked proposed" in self.said("accepted", True)

    def test_a_record_with_no_status_is_refused(self):
        assert "holds it with no status in its frontmatter" in self.said("")

    def test_a_record_main_does_not_hold_is_refused(self):
        assert f"{KIT}'s main holds no record 0033 in docs/adr/" in self.said(files=())

    def test_two_files_by_one_number_are_refused(self):
        assert f"{KIT}'s main holds 2 records numbered 0033: {self.FILE}, docs/adr/0033-another.md" in self.said(
            files=(self.FILE, "docs/adr/0033-another.md"))

    def test_a_record_crew_could_not_read_is_refused_with_why(self):
        why = f"could not fetch main of {self.REPO} over https: fatal: unable to access"
        said = plan.unaccepted([("unit", "u", KIT, self.REPO, 33)], {(self.REPO, 33): {"why": why}})
        assert f"  unit u names record 0033 of {KIT}: {why}" in said

    def test_every_record_accepted_refuses_nothing(self):
        assert self.said("accepted") is None
        assert plan.unaccepted([], {}) is None

    def test_a_unit_and_a_bolt_naming_one_record_are_both_named(self):
        held = {(self.REPO, 33): {"files": [self.FILE], "status": "proposed", "marked": False}}
        said = plan.unaccepted([("bolt", "b", KIT, self.REPO, 33), ("unit", "u", KIT, self.REPO, 33)], held)
        assert f"  bolt b names record 0033 of {KIT}" in said and f"  unit u names record 0033 of {KIT}" in said

    def test_the_status_is_read_as_crew_record_reads_it(self):
        md = "---\nstatus: accepted\n---\n# 33. A record\n\nStatus: accepted\n\nAn amendment. Status: proposed, on the card.\n"
        status, marked = plan.record_status_held(md)
        held = {(self.REPO, 33): {"files": [self.FILE], "status": status, "marked": bool(marked)}}
        assert "with an amendment still marked proposed" in plan.unaccepted([("unit", "u", KIT, self.REPO, 33)], held)

    def items(self, *dos, units=()):
        w = apply(FactsWrite(plan_text(bolts=[("held", KIT, "swb-1")], units=list(units))), *dos)
        return plan.record_items(self.FLEET, "wldn", w.plan, args(*dos))

    def test_new_bolts_and_units_name_their_records_by_kit_or_by_repository(self):
        assert self.items(f'bolt new fresh "Fresh." --repo {KIT} --source docs/adr/0034-x.md',
                          f'unit add n "N." --bolt fresh --source docs/adr/0033 --source agentplot/sluice:docs/adr/0022') == [
            ("bolt", "fresh", KIT, self.REPO, 34), ("unit", "n", KIT, self.REPO, 33), ("unit", "n", "agentplot/sluice", "agentplot/sluice", 22)]

    def test_a_queued_unit_moved_into_a_bolt_is_read_from_the_plan(self):
        text = plan_text(bolts=[("held", KIT, "swb-1")], units=[("q", KIT, None, [])]).replace(
            "Intent: Unit q.\n", "Intent: Unit q.\nSource: docs/adr/0033\n")
        w = apply(FactsWrite(text), "unit move q held")
        assert plan.record_items(self.FLEET, "wldn", w.plan, args("unit move q held")) == [("unit", "q", KIT, self.REPO, 33)]

    def test_work_the_proposal_does_not_make_new_is_not_read(self):
        """A planned bolt, since work launched in a started one is never moved out."""
        text = plan_text(bolts=[("held", KIT, None)], units=[("h1", KIT, "held", []), ("h2", KIT, "held", [])]).replace(
            "Intent: Unit h1.\n", "Intent: Unit h1.\nSource: docs/adr/0033\n")
        dos = ("unit order h2 --first", 'unit amend h1 "Amended."', "unit move h2 queue")
        w = apply(FactsWrite(text), *dos)
        assert plan.record_items(self.FLEET, "wldn", w.plan, args(*dos)) == []

    def test_work_of_a_kit_its_main_level_host_keeps_no_checkout_of_naming_a_record_is_refused(self):
        said, _ = refused(self.items, 'unit add n "N." --repo breadboard-kit --source docs/adr/0001')
        assert said == ("unit n names a decision record, and wldn's main level runs on mac-studio, and no space there keeps "
                        "breadboard-kit, so crew can't tell whose it is")
        assert self.items('unit add m "M." --repo breadboard-kit --source docs/architecture/core.md') == []


class TestStartProposed:
    """A proposal may hold crew bolt start (bolt-plan "A bolt is started"; Decision 14 of the-team-machinery-leaves,
    roles.1): its Do parses by the command's grammar and touches the bolt; it is checked as the proposal's card is drawn,
    reading no kit (Drawn); and its approval, the kit read on its partition's main-level host as a direct start reads it
    (plan.start_check), marks the bolt Path: flume and launches each unit of it in its repository, naming no host or
    stream, starting no agent. One naming a bolt started already is refused whole. sluice's branch and the commit are
    the cross journey's (t-journey-cross)."""
    FLEET = FLEET  # wldn's main level on mac-studio, whose spaces keep its kits
    DOS = ("bolt start pages",)

    @pytest.fixture(autouse=True)
    def host(self, monkeypatch):
        """mac-studio, wldn's main-level host, free, a runner answering, and switchboard-kit's policy making bolts on GitHub."""
        import crew
        self.read = []
        monkeypatch.setenv("CREW_AGENT", "chuck@mac-studio")
        monkeypatch.setattr(plan, "recfix", lambda text, what: None)
        monkeypatch.setattr(crew, "held_on", lambda fleet, host: None)
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("WilldanGroup/crew-state", f"{label}/main"))
        monkeypatch.setattr(plan, "runner_tips", lambda repo, label: {"chuck-herdr-alpha": "a" * 40})
        monkeypatch.setattr(plan, "kit_policy", lambda fleet, t: self.read.append(t["machine"]) or (
            '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n', "origin/main", "c" * 40, "sluice 0.36.4"))

    def write(self):
        return FactsWrite(plan_text(bolts=[("deploys", KIT, "started"), ("pages", KIT, None)],
                                    units=[("d1", KIT, "deploys", []), ("p1", KIT, "pages", []), ("p2", KIT, "pages", ["p1"])]),
                          files={"requests.rec": runner.REQUESTS})

    def test_its_do_parses_and_touches_the_bolt(self):
        a, = args(*self.DOS)
        assert (a.cmd, a.sub, a.bolt) == ("bolt", "start", "pages")
        assert plan.touched_by(self.write().plan, [a]) == [["pages"]]
        assert plan.summary([a]) == "start bolt pages"

    def test_its_card_is_checked_reading_no_kit(self):
        after = plan.check_ops(self.FLEET, "wldn", self.write(), args(*self.DOS), 1, plan.Drawn).plan
        assert plan.started(after.bolt("pages")) and self.read == []

    def test_its_approval_starts_the_bolt_and_launches_its_work_in_its_repository(self):
        w = self.write()
        ops, _ = plan.apply_all(self.FLEET, "wldn", w, args(*self.DOS), 1)
        assert [op.act for op in ops] == ["bolt.start"] and self.read == ["mac-studio"]
        assert plan.started(w.plan.bolt("pages")) and w.plan.bolt("pages").get("Team") is None
        assert [(r.get("Act"), r.get("Host"), r.get("Stream"), r.get("Work"), r.get("Base"), r.all("After"))
                for r in plan.Plan(w.files["requests.rec"]).recs("Request") if r.get("Act") == "launch"] == [
            ("launch", None, None, "unit/p1", "bolt/pages", []), ("launch", None, None, "unit/p2", "bolt/pages", ["1"])]

    def test_one_naming_a_bolt_started_already_is_refused_whole(self):
        said, _ = refused(plan.check_ops, self.FLEET, "wldn", self.write(), args("bolt start pages", "bolt start deploys"), 1, plan.Drawn)
        assert said == "`bolt start deploys`: bolt deploys is started already"

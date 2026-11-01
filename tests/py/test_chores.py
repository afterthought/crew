"""The chore kind (the chores spec, plan.11, signals.7): a Unit record marked Kind: chore, written by the unit's commands
and hands, its stage read as a unit's is, counted wherever work in a bolt is, and carried by a proposal whose card lets
each be left out. That git reads a chore's trailer as crew assumes is the contract tier's."""
import argparse

import pytest

from facts import FLEET, FactsWrite, apply, crew_read, crossed_fleet_read, known, launched, plan_text, ran, units_of

import cards
import plan

KIT = "switchboard-kit"
TE = "tenant-environments"
BOLTS = [(TE, KIT, "swb-1"), ("console-pages", KIT, "swb-2"), ("apex-zones", KIT, None)]
PLANNED = [(b, r, None) for b, r, _ in BOLTS]


@pytest.fixture(autouse=True)
def writer(monkeypatch):
    """A write to a started bolt appends its launches, which name their writer."""
    monkeypatch.setenv("CREW_AGENT", "wldn-planner")


def fresh(bolts=BOLTS):
    """A started bolt of a unit, a chore and a unit, a chore queued, and a unit in another bolt; the bolts started as
    bolts says."""
    return FactsWrite(plan_text(bolts=bolts, units=[("a", KIT, TE, []), ("bump", KIT, TE, [], "chore"), ("b", KIT, TE, []),
                                                    ("tidy", KIT, None, [], "chore"), ("c", KIT, "console-pages", [])]))


def run(w, *dos, stages=None, taken=(), chores_taken=()):
    return apply(w, *dos, ctx=known(w, stages=stages, taken=taken, chores_taken=chores_taken))


def refusal(w, do, **kw):
    with pytest.raises(plan.Refusal) as e:
        run(w, do, **kw)
    return str(e.value)


class TestThePlan:
    def test_a_chore_is_a_unit_record_marked_kind_chore_and_read_apart_from_the_units(self):
        p = fresh().plan
        assert [u.name() for u in p.units()] == ["a", "b", "c"] and [u.name() for u in p.chores()] == ["bump", "tidy"]
        assert [u.name() for u in p.work_of(TE)] == ["a", "bump", "b"] and [u.name() for u in p.queue(KIT)] == ["tidy"]
        assert p.unit("bump") is None and p.chore("bump").get("Kind") == "chore" and p.item("bump") is p.chore("bump")

    def test_the_schema_allows_kind_as_a_chore_alone(self):
        assert "%type: Kind enum chore" in plan.HEADER and "%allowed: Unit Repo Bolt Kind Intent After Source Amended" in plan.HEADER

    def test_after_crosses_kinds_within_a_bolt_and_a_chore_is_never_amended(self):
        """On a bolt not started: a started bolt's launched work keeps the After of its launch (test_cross.py)."""
        w = run(fresh(PLANNED), "unit after b bump", "chore after bump a")
        assert w.plan.unit("b").all("After") == ["bump"] and w.plan.chore("bump").all("After") == ["a"]
        w.plan.chore("bump").set("Amended", "intent")
        with pytest.raises(plan.Refusal, match="chore bump is marked amended, and a chore has no amendment"):
            plan.check(w.plan)


class TestCommands:
    def test_add_writes_the_kind_where_a_unit_would_go(self):
        w = run(fresh(), f'chore add pin "Pin the shell." --bolt {TE} --before b --source books/x.md')
        assert units_of(w, TE) == ["a", "bump", "pin", "b"]
        assert w.plan.chore("pin").fields == [("Unit", "pin"), ("Repo", KIT), ("Bolt", TE), ("Kind", "chore"), ("Intent", "Pin the shell."),
                                             ("Source", "books/x.md")]
        assert units_of(run(fresh(), f'chore add q "Queued." --repo {KIT}'), repo=KIT) == ["tidy", "q"]

    def test_order_after_move_and_drop_act_on_a_chore(self):
        w = run(fresh(), "chore order bump --first", "chore move tidy apex-zones", "chore drop bump \"Not now.\"")
        assert units_of(w, TE) == ["a", "b"] and units_of(w, "apex-zones") == ["tidy"]

    def test_a_drop_takes_its_name_out_of_what_comes_after_it(self):
        assert run(fresh(), "unit after b bump", 'chore drop bump "Not now."').plan.unit("b").all("After") == []

    @pytest.mark.parametrize("do, said", [
        ('unit drop bump "x"', "bump is a chore, not a unit: crew chore drop acts on it"),
        ("unit order bump --first", "bump is a chore, not a unit: crew chore order acts on it"),
        ('chore drop a "x"', "a is a unit, not a chore: crew unit drop acts on it"),
        ('unit split bump "x" --into bump-rest "y"', "bump is a chore, which is never split: a chore's words change by a proposal "
                                                    "that drops it and adds it again (crew chore drop, crew chore add)"),
        ('unit amend bump "x"', "bump is a chore, which is never amended: a chore's words change by a proposal that drops it and "
                                "adds it again (crew chore drop, crew chore add)")])
    def test_a_command_of_the_other_kind_is_refused_naming_the_one_that_takes_it(self, do, said):
        assert refusal(fresh(), do) == said

    def test_a_chore_has_no_split_or_amend_to_propose(self):
        with pytest.raises(plan.Refusal, match="a proposal holds only the plan's commands"):
            plan.do_args("wldn", 'chore amend bump "x"')

    @pytest.mark.parametrize("taken, chores, said", [
        ({"pin"}, (), "switchboard-kit's main already has a change named pin, open or archived; pick another name"),
        ((), {"pin"}, "switchboard-kit's main already holds a chore named pin; pick another name")])
    def test_a_name_is_taken_once_in_a_kit_by_a_change_or_a_landed_chore(self, taken, chores, said):
        assert refusal(fresh(), f'chore add pin "x" --bolt {TE}', taken=taken, chores_taken=chores) == said
        assert refusal(fresh(), f'unit add pin "x" --bolt {TE}', taken=taken, chores_taken=chores) == said

    def test_the_plan_refuses_a_name_either_kind_holds(self):
        assert refusal(fresh(), f'unit add bump "x" --bolt {TE}') == "wldn/main already has chore bump"
        assert refusal(fresh(), f'chore add a "x" --bolt {TE}') == "wldn/main already has unit a"

    def test_name_taken_reads_a_kit_whose_crew_reads_no_chores_as_holding_none(self):
        assert plan.name_taken(KIT, "pin", [], None) is None
        assert plan.name_taken(KIT, "Pin", [], []) == "a unit's or chore's name is lowercase words with dashes, not Pin"

    def test_unblocks_puts_a_chore_ahead_of_the_first_unmerged_work(self):
        w = run(fresh(), f'chore add fix-pin "Pin." --bolt {TE} --unblocks {TE}', stages={"a": "merged"})
        assert units_of(w, TE) == ["a", "fix-pin", "bump", "b"]

    def test_a_signal_routes_to_the_chore_in_the_same_write(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "chuck@mac-studio")
        w = FactsWrite(plan_text(bolts=BOLTS, units=[]), files={"moves.rec": plan.MOVES, "signals/s/01-x.md": "---\nsignal: s/01-x\n---\n"})
        op = plan.op_unit_add(known(w), plan.do_args("wldn", f'chore add pin "Pin." --bolt {TE} --signal s/01-x'))
        op.change(w)
        assert "Target: chore/pin" in w.files["moves.rec"] and op.act == "chore.add"
        assert (op.on, op.frm, op.subject) == (["chore/pin", f"bolt/{TE}"], ["signals/s/01-x"], f"plan({TE}): add chore pin")

    def test_a_signals_short_id_routes_the_signal_it_numbers_by_its_full_id(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "chuck@mac-studio")
        w = FactsWrite(plan_text(bolts=BOLTS, units=[]), files={"moves.rec": plan.MOVES, "signals/s/01-x.md": "---\nsignal: s/01-x\n---\n"})
        op = plan.op_unit_add(known(w), plan.do_args("wldn", f'chore add pin "Pin." --bolt {TE} --signal s/01'))
        op.change(w)
        assert "Signal: s/01-x\nMove: route\nTarget: chore/pin" in w.files["moves.rec"] and "Source: signals/s/01-x" in w.plan.text()
        assert op.frm == ["signals/s/01-x"]


class TestWho:
    def may(self, monkeypatch, agent, key, bolt=None):
        monkeypatch.setenv("CREW_AGENT", agent)
        try:
            plan.may_write(FLEET, key, argparse.Namespace(bolt=bolt))
            return None
        except plan.Refusal as e:
            return str(e)

    @pytest.mark.parametrize("agent, key, bolt", [("wldn-design", ("chore", "add"), None), ("chuck@mac-studio", ("chore", "drop"), None)])
    def test_a_chore_is_written_by_the_hands_that_write_a_unit(self, monkeypatch, agent, key, bolt):
        assert self.may(monkeypatch, agent, key, bolt) is None

    @pytest.mark.parametrize("agent, key, bolt, said", [
        ("wldn-planner", ("chore", "add"), None, "the planner changes the plan through a proposal: crew plan propose, not crew chore add"),
        ("wldn-design", ("chore", "add"), TE, "wldn-design does not write the plan with crew chore add --bolt: tell wldn-planner, who proposes it"),
        ("wldn-ops", ("chore", "move"), None, "wldn-ops does not write the plan with crew chore move: tell wldn-planner, who proposes it")])
    def test_any_other_chore_write_is_refused_naming_the_planner(self, monkeypatch, agent, key, bolt, said):
        assert self.may(monkeypatch, agent, key, bolt) == said


class TestStage:
    def test_work_of_a_bolt_not_started_is_ready_or_waiting_by_its_after(self):
        """A chore after a unit, and a unit after the chore, in a bolt not started: each waits until what it comes after
        has something committed to build on (plan.13), which nothing of a planned bolt has."""
        p = plan.Plan(plan_text(bolts=PLANNED, units=[("a", KIT, TE, []), ("bump", KIT, TE, ["a"], "chore"), ("b", KIT, TE, ["bump"])]))
        st = plan.Stages(FLEET, p, {})
        assert [st.of(n)["stage"] for n in ("a", "bump", "b")] == ["ready", "waiting", "waiting"]
        assert st.bolt_state(p.bolt(TE)) == "planned"

    @pytest.mark.parametrize("deps, met", [
        ([("unit", "construct")], False), ([("unit", "planned")], True), ([("unit", "merged"), ("chore", "landed")], True),
        ([("chore", "code")], False), ([("chore", "verify")], True), ([("chore", "ready")], False), ([("unit", "unknown")], None)])
    def test_after_met(self, deps, met):
        assert plan.after_met(deps) is met

    def test_a_bolt_lands_once_every_unit_and_chore_has(self):
        """Started bolt x of unit a and chore bump, both landed on x by the runner: active while crew's main holds a's change
        and not bump's trailer, landed once it holds both."""
        fleet = crossed_fleet_read()
        p, requests = launched(["x"], work=[("a", "x", [], "unit", []), ("bump", "x", [], "chore", [])], fleet=fleet)
        runs = {"madswan": (requests, ran({1: "landed", 2: "landed"}))}
        st = plan.Stages(fleet, p, crew_read(main=["a"], bolts={"x": {}}), runs=runs, label="madswan")
        assert st.bolt_state(p.bolt("x")) == "active"
        st = plan.Stages(fleet, p, crew_read(main=["a"], chores=["bump"], bolts={"x": {}}), runs=runs, label="madswan")
        assert st.bolt_state(p.bolt("x")) == "landed"


class TestBolts:
    def test_a_landing_waits_for_its_chores_to_land(self):
        stage = {"a": "landed", "bump": "merged"}
        of = lambda u: {"stage": stage[u], "kind": "chore" if u == "bump" else "unit"}
        assert plan.land_refusal(TE, ["a", "bump"], of, [], "wldn") == "chore bump has not landed on main: it is merged"

    def test_crew_bolts_marks_a_chore_and_its_queue(self):
        data = {"partitions": [{"label": "wldn", "plans": [{"repo": "r", "plan": "abcdef0", "queue": [
            {"unit": "tidy", "kind": "chore", "repo": KIT, "stage": "queued", "sources": []}],
            "bolts": [{"bolt": TE, "repo": KIT, "team": "swb-1", "host": "box", "state": "active", "fixes": [], "units": [
                {"unit": "bump", "kind": "chore", "stage": "verify", "tasks": None, "worktree": "/kit/places/chore-bump"}]}]}]}], "unreachable": {}}
        text = plan.bolts_text(data)
        assert "  bump                                     chore verify places/chore-bump" in text
        assert "  tidy                                     chore queued" in text


def proposal_card(*dos):
    """A proposal's card as crew raises it (cards.proposal_card), on the plan at the tip and the plan its commands leave."""
    pl = plan.Plan(plan.PROPOSALS)
    plan.open_proposal(pl, 1, "Upkeep.", list(dos), "wldn-planner", "2026-10-12")
    p = plan.proposal(pl, 1, "wldn")
    base = lambda: FactsWrite(plan_text(bolts=[("deploys", KIT, None)], units=[("a-first", KIT, "deploys", [])]))
    return p, cards.proposal_card(dict(n=1, state="open", case="Upkeep.", before=base().plan, after=apply(base(), *dos).plan,
                                       argvs=[plan.do_args("wldn", d) for d in dos], session=None))


class TestProposals:
    DOS = ['bolt new upkeep "Upkeep." --repo switchboard-kit', 'chore add bump "Biome follows the shell." --bolt upkeep',
           'chore add pin "Pin the lock." --bolt upkeep', 'chore add tidy "Tidy the docs." --bolt upkeep']

    def test_a_batch_of_chores_is_one_bolt_whose_every_chore_the_user_keeps_or_clears(self):
        _, b = proposal_card(*self.DOS)
        c = b["card"]
        assert [(o["id"], o["detail"], o["consequence"]) for o in c["options"]] == [
            (f"add:{u}", f"Chore: {said}", "Cleared: not added; the rest still applies")
            for u, said in (("bump", "Biome follows the shell."), ("pin", "Pin the lock."), ("tidy", "Tidy the docs."))]
        assert c["recommendedIds"] == ["add:bump", "add:pin", "add:tidy"]
        assert "CHORE  bump" in "\n".join(c["artifacts"][-1]["lines"])

    def test_the_approval_leaves_a_cleared_chore_out(self):
        argvs = [plan.do_args("wldn", d) for d in self.DOS]
        assert [plan.do_named(a) for a in plan.kept(argvs, ["pin"], 1)] == ["bolt new upkeep", "chore add bump", "chore add tidy"]

    def test_it_reads_as_chores_and_names_chore_objects(self):
        argvs = [plan.do_args("wldn", d) for d in self.DOS[:2] + ['chore move bump queue', 'chore drop bump "Not now."']]
        assert plan.summary(argvs) == "new bolt upkeep, add chore bump to upkeep, move chore bump to the queue, drop chore bump"
        assert plan.objects(argvs) == ["bolt/upkeep", "chore/bump"]
        w = FactsWrite(plan_text(bolts=[("deploys", KIT, None)], units=[]))
        p, _ = proposal_card(*self.DOS[:2])
        d = plan.describe(FLEET, "wldn", w.plan, p, alone=True)
        assert d["changes"][1]["lines"] == ["**New chore `bump`** in bolt `upkeep` (new in this proposal)", "Chore: Biome follows the shell.",
                                            "Bolt's goal: Upkeep."]

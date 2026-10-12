"""The chore kind (the chores spec, plan.11, signals.7): a Unit record marked Kind: chore, written by the unit's commands
and hands, its stage read from its kit, its stages decided, ended and freed, counted wherever work in a bolt is, and
carried by a proposal whose card lets each be left out. That crew chore run takes a slot, makes the place and sends the
prompt, and that a chore's waits, merge and trace go through the command, is the chores journey's (t-journey-chores);
that git reads a chore's trailer as crew assumes, the contract tier's."""
import argparse
import datetime

import pytest

from facts import FLEET, START, FactsWrite, apply, known, owed, plan_text, units_of

import plan

KIT = "switchboard-kit"
TE = "tenant-environments"
BOLTS = [(TE, KIT, "swb-1"), ("console-pages", KIT, "swb-2"), ("apex-zones", KIT, None)]


def fresh():
    """A held bolt of a unit, a chore and a unit, a chore queued, and a unit in another bolt."""
    return FactsWrite(plan_text(bolts=BOLTS, units=[("a", KIT, TE, []), ("bump", KIT, TE, [], "chore"), ("b", KIT, TE, []),
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
        w = run(fresh(), "unit after b bump", "chore after bump a")
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


class TestWho:
    def may(self, monkeypatch, agent, key, bolt=None):
        monkeypatch.setenv("CREW_AGENT", agent)
        try:
            plan.may_write(FLEET, key, argparse.Namespace(bolt=bolt))
            return None
        except plan.Refusal as e:
            return str(e)

    @pytest.mark.parametrize("agent, key, bolt", [("swb-1-conductor", ("chore", "order"), None), ("swb-1-conductor", ("chore", "after"), None),
                                                  ("wldn-design", ("chore", "add"), None), ("chuck@mac-studio", ("chore", "drop"), None)])
    def test_a_chore_is_written_by_the_hands_that_write_a_unit(self, monkeypatch, agent, key, bolt):
        assert self.may(monkeypatch, agent, key, bolt) is None

    @pytest.mark.parametrize("agent, key, bolt, said", [
        ("wldn-planner", ("chore", "add"), None, "the planner changes the plan through a proposal: crew plan propose, not crew chore add"),
        ("swb-1-conductor", ("chore", "add"), TE, "swb-1-conductor does not write the plan with crew chore add --bolt: tell wldn-planner, who proposes it"),
        ("wldn-design", ("chore", "add"), TE, "wldn-design does not write the plan with crew chore add --bolt: tell wldn-planner, who proposes it"),
        ("swb-1-conductor", ("chore", "move"), None, "swb-1-conductor does not write the plan with crew chore move: tell wldn-planner, who proposes it")])
    def test_any_other_chore_write_is_refused_naming_the_planner(self, monkeypatch, agent, key, bolt, said):
        assert self.may(monkeypatch, agent, key, bolt) == said

    def test_a_conductor_orders_only_the_chores_of_its_own_bolt(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "swb-2-conductor")
        w = fresh()
        with pytest.raises(plan.Refusal, match="swb-2-conductor writes only units and chores of the bolt swb-2 holds, and bump is in bolt "
                                               "tenant-environments"):
            apply(w, "chore order bump --first", ctx=known(w))


def kit(chores=(), bolt_chores=(), places=None, changes=()):
    """A kit as gathered: the chores main and the bolt hold, and chore places."""
    return {"ok": True, "main": list(changes), "chores": list(chores), "places": {}, "chore_places": places or {}, "fixes": [], "reports": {},
            "bolts": {TE: {"head": "d" * 40, "head_at": "2026-10-12T09:00:00Z", "changes": [], "chores": list(bolt_chores)}}}


def place(ahead, bolt=TE):
    return {"path": "/kit/places/chore-bump", "head": "e" * 40, "head_at": "2026-10-12T10:00:00Z", "ahead": ahead, "bolt": bolt,
            "branch": "chore/bump"}


STAGE_FLEET = {"partitions": FLEET["partitions"],
               "teams": {t: {"name": t, "label": "wldn", "machine": "box", "kit": {"main": "/kit/main", "dir": "/kit", "name": KIT}}
                         for t in ("swb-1", "swb-2")}}


def stages(k, text=None):
    p = plan.Plan(text or plan_text(bolts=BOLTS, units=[("a", KIT, TE, []), ("bump", KIT, TE, [], "chore"), ("b", KIT, TE, ["bump"])]))
    return plan.Stages(STAGE_FLEET, p, {"box": {"ok": True, "kits": {"/kit/main": k}}})


class TestStage:
    @pytest.mark.parametrize("k, stage", [
        (kit(chores=["bump"], bolt_chores=["bump"]), "landed"),
        (kit(bolt_chores=["bump"]), "merged"),
        (kit(places={"bump": place(2)}), "verify"),
        (kit(places={"bump": place(0)}), "code"),
        (kit(), "ready")], ids=["landed", "merged", "coded", "placed", "no place"])
    def test_a_chores_stage_is_read_from_its_kit(self, k, stage):
        assert stages(k).of("bump")["stage"] == stage

    def test_a_place_that_tracks_no_bolt_is_unknown(self):
        s = stages(kit(places={"bump": place(None)})).of("bump")
        assert (s["stage"], s["why"]) == ("unknown", "chore bump's place /kit/places/chore-bump tracks no bolt crew can read")

    def test_a_chore_waits_for_each_after_to_merge_and_a_unit_after_a_chore_for_its_merge(self):
        text = plan_text(bolts=BOLTS, units=[("a", KIT, TE, []), ("bump", KIT, TE, ["a"], "chore"), ("b", KIT, TE, ["bump"])])
        assert stages(kit(places={"bump": place(1)}), text).of("b")["stage"] == "waiting"
        assert stages(kit(bolt_chores=["bump"]), text).of("b")["stage"] == "ready"
        assert stages(kit(), text).of("bump")["stage"] == "waiting"

    @pytest.mark.parametrize("chore, deps, met", [
        (True, [("unit", "verify")], False), (True, [("unit", "merged"), ("chore", "landed")], True),
        (False, [("unit", "planned")], True), (False, [("chore", "verify")], False), (False, [("chore", "merged")], True),
        (False, [("unit", "unknown")], None)])
    def test_after_met(self, chore, deps, met):
        assert plan.after_met(chore, deps) is met

    def test_a_bolt_lands_once_every_unit_and_chore_has(self):
        p = plan.Plan(plan_text(bolts=BOLTS, units=[("a", KIT, TE, []), ("bump", KIT, TE, [], "chore")]))
        st = plan.Stages(STAGE_FLEET, p, {"box": {"ok": True, "kits": {"/kit/main": kit(changes=["a"])}}})
        assert st.bolt_state(p.bolt(TE)) == "active"
        st = plan.Stages(STAGE_FLEET, p, {"box": {"ok": True, "kits": {"/kit/main": kit(chores=["bump"], changes=["a"])}}})
        assert st.bolt_state(p.bolt(TE)) == "landed"


class TestRun:
    @pytest.mark.parametrize("stage, st, after, verified, said", [
        ("code", "ready", {}, False, None),
        ("code", "verify", {}, False, None),
        ("verify", "verify", {}, False, None),
        ("merge", "verify", {"a": "merged"}, True, None),
        ("code", "waiting", {"a": "verify"}, False, f"chore bump comes after a, not yet merged into bolt/{TE}"),
        ("verify", "code", {}, False, f"chore bump has nothing committed beyond bolt/{TE} yet: verify waits for its code"),
        ("verify", "ready", {}, False, "chore bump has not been coded yet: crew chore run bump code"),
        ("merge", "code", {}, False, f"chore bump has nothing committed beyond bolt/{TE} yet: it merges once its code is committed and verify has run"),
        ("merge", "verify", {}, False, "chore bump merges once verify has run on its code since it was last coded: crew chore run bump verify"),
        ("code", "merged", {}, False, "chore bump has merged into its bolt: a defect in it is a fix (crew fix), and new maintenance a new chore"),
        ("construct", "ready", {}, False, "a chore has no construct: its stages are code, verify and merge (crew chore run bump code)")])
    def test_chore_refusal(self, stage, st, after, verified, said):
        assert plan.chore_refusal("bump", TE, stage, st, after, verified) == said

    @pytest.mark.parametrize("kind, chore, stage, said", [
        ("chore", False, "construct", "bump is a chore, which has no construct: its stages are code, verify and merge (crew chore run bump code)"),
        ("chore", False, "code", "bump is a chore: crew chore run bump code"),
        ("unit", True, "code", "bump is a unit: crew unit run bump code"),
        ("chore", True, "code", None), ("unit", False, "construct", None)])
    def test_a_stage_asked_of_the_other_kind_is_refused(self, kind, chore, stage, said):
        assert plan.run_kind_refusal(kind, chore, "bump", stage) == said

    @pytest.mark.parametrize("stage, words, prompt", [
        ("code", "", "Chore bump: Biome follows the shell."),
        ("code", "Fix the finding: x.", "Chore bump: Biome follows the shell. Fix the finding: x."),
        ("verify", "", "Verify chore bump: Biome follows the shell."),
        ("merge", "", f"Merge bump into bolt/{TE}: wt merge bolt/{TE} --no-squash --no-remove")])
    def test_its_prompts(self, stage, words, prompt):
        assert plan.chore_prompt(stage, "bump", "Biome follows the shell.", words, TE, f"wt merge bolt/{TE} --no-squash --no-remove") == prompt

    def test_a_merge_is_refused_for_each_commit_without_the_trailer(self):
        commits = [("a1b2c3d", "chore: bump biome", ["bump"]), ("e4f5a6b", "chore: and its lock", []), ("c7d8e9f", "chore: other", ["pin"])]
        assert plan.untrailed(commits, "bump") == [("e4f5a6b", "chore: and its lock"), ("c7d8e9f", "chore: other")]

    def test_a_unit_waiting_on_a_chore_names_it(self):
        assert plan.stage_refusal("b", TE, "construct", "waiting", None, {"bump": "verify", "a": "construct"}, ("user", None), "swb-1", [],
                                  False, False, chores={"bump"}) == (
            f"unit b is waiting: it comes after a, whose change is not committed yet; and chore bump, not yet merged into bolt/{TE}")


class TestEnds:
    def test_a_chores_stage_is_owed_on_its_own_objects(self):
        o = owed("code", name="bump", obj="chore/bump")
        assert (o.chore, o.fix, o.branch(), o.phrase()) == (True, False, "chore/bump", "code on chore bump")
        assert o.on() == ["stage/bump/code", "chore/bump", "agent/swb-1-unit-1"] and o.why("delivered") == "chore(bump): code ended"

    def test_code_delivers_a_commit_on_its_branch_since_it_began(self):
        o = owed("code", name="bump", obj="chore/bump")
        later = START + datetime.timedelta(minutes=3)
        assert plan.delivered(o, {"head": "abc1234", "at": later}) == ("chore/bump@abc1234", "its branch is at abc1234")
        assert plan.delivered(o, {"head": "abc1234", "at": START - datetime.timedelta(minutes=3)}) == (None, "nothing committed since it began")

    def test_merge_delivers_the_bolt_holding_its_trailer(self):
        o = owed("merge", name="bump", obj="chore/bump")
        assert plan.delivered(o, {"bolt": TE, "holds": True, "bolt_head": "1234567"}) == (f"bolt/{TE}@1234567", f"bolt/{TE} holds it at 1234567")


class TestSlotsAndPlaces:
    def plan(self):
        return plan.Plan(plan_text(bolts=BOLTS, units=[("bump", KIT, TE, [], "chore"), ("gone", KIT, "console-pages", [], "chore")]))

    @pytest.mark.parametrize("k, name, stage", [
        (kit(chores=["bump"]), "bump", "landed"), (kit(bolt_chores=["bump"]), "bump", "merged"),
        (kit(places={"bump": place(1)}), "bump", "verify"), (kit(), "dropped-one", "dropped"), (kit(), "gone", "left")])
    def test_a_slot_holding_a_chore_reads_its_stage(self, k, name, stage):
        assert plan.slot_stage("chore", name, k, self.plan(), {TE}, {})[0] == stage

    def test_a_chores_place_is_crews_and_over_once_merged_landed_or_planned_no_more(self):
        on = {"main": {"landed-one"}, f"bolt/{TE}": {"merged-one"}}
        over = lambda name, chores=("live",): plan.tidy_over(f"/kit/places/chore-{name}", f"chore/{name}", "/kit", f"bolt/{TE}", {TE}, set(),
                                                             set(), lambda b: [], lambda f, b: False, set(chores), lambda ref: on.get(ref, set()))
        assert over("landed-one") == ("landed-one", "chore landed-one has landed on main")
        assert over("merged-one") == ("merged-one", f"chore merged-one has merged into bolt/{TE}")
        assert over("live") == ("live", None)
        assert over("gone", ()) == ("gone", "chore gone is in no plan")
        assert plan.tidy_over("/kit/places/bump", "chore/bump", "/kit", f"bolt/{TE}", {TE}, set(), set(), lambda b: [],
                              lambda f, b: False, set(), lambda ref: set()) is None


class TestBolts:
    def test_a_team_holds_its_bolt_until_its_chores_land_and_a_landing_waits_for_them(self):
        p = plan.Plan(plan_text(bolts=BOLTS, units=[("a", KIT, TE, []), ("bump", KIT, TE, [], "chore")]))
        stage = {"a": "landed", "bump": "merged"}
        assert plan.holding("swb-1", p.bolt(TE), p, stage.get) == "swb-1 holds bolt tenant-environments, whose chore bump has not landed (merged)"
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
    pl = plan.Plan(plan.PROPOSALS)
    plan.open_proposal(pl, 1, "Upkeep.", list(dos), "wldn-planner", "2026-10-12")
    p = plan.proposal(pl, 1, "wldn")
    base = lambda: FactsWrite(plan_text(bolts=[("deploys", KIT, None)], units=[("a-first", KIT, "deploys", [])]))
    return p, plan.card_model(FLEET, "wldn", base(), p, after=apply(base(), *dos).plan)


class TestProposals:
    DOS = ['bolt new upkeep "Upkeep." --repo switchboard-kit', 'chore add bump "Biome follows the shell." --bolt upkeep',
           'chore add pin "Pin the lock." --bolt upkeep', 'chore add tidy "Tidy the docs." --bolt upkeep']

    def test_a_batch_of_chores_is_one_bolt_whose_every_chore_the_user_keeps_or_clears(self):
        _, m = proposal_card(*self.DOS)
        assert m["new"] == ["bump", "pin", "tidy"]
        q = m["card"]["questions"][1]
        assert q["title"] == "Which chores go in? Clear one to leave it out."
        assert q["rationale"] == "A cleared chore is not added; the rest of the proposal still applies."
        assert [o["detail"] for o in q["options"]] == ["Chore: Biome follows the shell.", "Chore: Pin the lock.", "Chore: Tidy the docs."]
        assert "CHORE  bump" in "\n".join(m["card"]["artifacts"][1]["lines"])

    def test_the_approval_leaves_a_cleared_chore_out(self):
        argvs = [plan.do_args("wldn", d) for d in self.DOS]
        assert [plan.do_named(a) for a in plan.kept(argvs, ["pin"], 1)] == ["bolt new upkeep", "chore add bump", "chore add tidy"]

    def test_new_work_says_what_a_question_holds(self):
        assert plan.new_work(["a", "b"], set()) == "new units"
        assert plan.new_work(["a", "b"], {"a", "b"}) == "chores"
        assert plan.new_work(["a", "b"], {"b"}) == "new units and chores"

    def test_it_reads_as_chores_and_names_chore_objects(self):
        argvs = [plan.do_args("wldn", d) for d in self.DOS[:2] + ['chore move bump queue', 'chore drop bump "Not now."']]
        assert plan.summary(argvs) == "new bolt upkeep, add chore bump to upkeep, move chore bump to the queue, drop chore bump"
        assert plan.objects(argvs) == ["bolt/upkeep", "chore/bump"]
        w = FactsWrite(plan_text(bolts=[("deploys", KIT, None)], units=[]))
        p, _ = proposal_card(*self.DOS[:2])
        d = plan.describe(FLEET, "wldn", w.plan, p, alone=True)
        assert d["changes"][1]["lines"] == ["**New chore `bump`** in bolt `upkeep` (new in this proposal)", "Chore: Biome follows the shell.",
                                            "Bolt's goal: Upkeep."]

"""Who writes the plan directly (roles.1): plan.may_write for each kind of agent and command, and plan.conductor_scope,
which keeps a conductor to the bolt its team holds. The user writes everything; the planner only through proposals; a
dispatcher gives bolts; a conductor narrows, orders and sets dependencies within its own bolt; the design agent queues;
the main level's ops lands. A role's run, named from its Flume place, writes as its role, and any other place names
nobody (role-runs "A run is named as its role"). That a refused write leaves a Refused entry is the proposals journey's
(t-journey-plan)."""
import argparse
import getpass

import pytest

from facts import FLEET, FactsWrite, apply, known, plan_text

import crew
import plan
import record

KIT = "switchboard-kit"


def may(monkeypatch, agent, key, bolt=None):
    monkeypatch.setenv("CREW_AGENT", agent)
    try:
        plan.may_write(FLEET, key, argparse.Namespace(bolt=bolt))
        return None
    except plan.Refusal as e:
        return str(e)


@pytest.mark.parametrize("agent, key, bolt", [
    ("chuck@mac-studio", ("bolt", "new"), None), ("wldn-dispatch-chuck-herdr-alpha", ("bolt", "give"), None),
    ("swb-1-conductor", ("unit", "order"), None), ("swb-1-conductor", ("unit", "after"), None), ("swb-1-conductor", ("unit", "split"), None),
    ("wldn-design", ("unit", "add"), None), ("wldn-ops", ("bolt", "land"), None)])
def test_each_writes_what_its_role_writes(monkeypatch, agent, key, bolt):
    assert may(monkeypatch, agent, key, bolt) is None


@pytest.mark.parametrize("key", [("unit", "add"), ("bolt", "new")])
def test_the_planner_writes_through_a_proposal(monkeypatch, key):
    assert may(monkeypatch, "wldn-planner", key) == f"the planner changes the plan through a proposal: crew plan propose, not crew {' '.join(key)}"


@pytest.mark.parametrize("agent, key, bolt, said", [
    ("swb-1-conductor", ("unit", "add"), "tenant-environments", "swb-1-conductor does not write the plan with crew unit add --bolt: tell wldn-planner, who proposes it"),
    ("swb-1-conductor", ("unit", "move"), None, "swb-1-conductor does not write the plan with crew unit move: tell wldn-planner, who proposes it"),
    ("wldn-design", ("unit", "add"), "console-pages", "wldn-design does not write the plan with crew unit add --bolt: tell wldn-planner, who proposes it"),
    ("wldn-design", ("bolt", "new"), None, "wldn-design does not write the plan with crew bolt new: tell wldn-planner, who proposes it"),
    ("swb-1-unit-1", ("unit", "order"), None, "swb-1-unit-1 does not write the plan with crew unit order: tell wldn-planner, who proposes it"),
    ("wldn-operator", ("unit", "drop"), None, "wldn-operator does not write the plan with crew unit drop: tell wldn-planner, who proposes it"),
    ("wldn-ops", ("bolt", "new"), None, "wldn-ops does not write the plan with crew bolt new: tell wldn-planner, who proposes it")])
def test_any_other_write_is_refused_naming_the_planner(monkeypatch, agent, key, bolt, said):
    assert may(monkeypatch, agent, key, bolt) == said


def test_a_conductor_writes_only_units_of_its_own_bolt(monkeypatch):
    monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
    w = FactsWrite(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("console-pages", KIT, "swb-2")],
                             units=[("a", KIT, "tenant-environments", []), ("b", KIT, "tenant-environments", []), ("c", KIT, "console-pages", [])]))
    apply(w, "unit order b --first", "unit after a b", ctx=known(w))
    assert [u.name() for u in w.plan.units_of("tenant-environments")] == ["b", "a"]
    with pytest.raises(plan.Refusal, match="swb-1-conductor writes only units and chores of the bolt swb-1 holds, and c is in bolt console-pages: tell wldn-planner"):
        apply(w, "unit order c --first", ctx=known(w))


# wldn running its planner, design agent and ops as their kinds, and its reviewer and operator standing.
RUNS = dict(FLEET, partitions={"wldn": dict(FLEET["partitions"]["wldn"], flume=dict(
    dict.fromkeys(crew.KIND_ROLES, False), planner="wldn-main", design="wldn-main", ops="wldn-main"))})
PLACES = "/Users/chuck/.local/state/flume/places/Users%chuck%Code%github_afterthought%blueprints"


def in_place(monkeypatch, place, fleet=RUNS):
    """A crew command in a Flume place, with nothing of crew's in its environment, the teams file read as fleet."""
    monkeypatch.setenv("CREW_AGENT", "")
    monkeypatch.setenv("CREW_LABEL", "")
    monkeypatch.setenv("FLUME_PLACE", place)
    monkeypatch.setattr(crew, "load", lambda: fleet)
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setattr(plan, "CONTEXT", {})


class TestARunIsItsRole:
    def test_the_planners_run_writes_cards_and_entries_as_the_planner(self, monkeypatch):
        """role-runs, The planner's run proposes: its proposal and card are the planner's, and a direct write is refused
        as the planner's is."""
        in_place(monkeypatch, f"{PLACES}/crew-planner--wldn")
        assert (plan.agent(), record.who(), plan.role(RUNS, crew.caller(RUNS))) == ("wldn-planner", "wldn-planner", ("planner", "wldn"))
        assert plan.default_label(RUNS, argparse.Namespace(label=None)) == "wldn"
        assert plan.card_asker(RUNS, argparse.Namespace(label=None, sub="list")) == ("wldn", "wldn-planner")
        with pytest.raises(plan.Refusal, match="the planner changes the plan through a proposal: crew plan propose, not crew unit add"):
            plan.may_write(RUNS, ("unit", "add"), argparse.Namespace(bolt=None))

    @pytest.mark.parametrize("role, key, bolt", [("design", ("unit", "add"), None), ("ops", ("bolt", "land"), None)])
    def test_each_run_writes_what_its_role_writes(self, monkeypatch, role, key, bolt):
        in_place(monkeypatch, f"{PLACES}/crew-{role}--wldn")
        plan.may_write(RUNS, key, argparse.Namespace(bolt=bolt))

    def test_a_runs_write_beyond_its_role_is_refused_in_its_roles_name(self, monkeypatch):
        in_place(monkeypatch, f"{PLACES}/crew-design--wldn/")
        with pytest.raises(plan.Refusal, match="wldn-design does not write the plan with crew unit add --bolt: tell wldn-planner"):
            plan.may_write(RUNS, ("unit", "add"), argparse.Namespace(bolt="console-pages"))

    @pytest.mark.parametrize("place", ["/kit/places/fix-console-pages--one", "/kit/places/change--a", "/kit/places/chore--record-0053", ""])
    def test_a_place_of_another_kind_names_nobody_and_reads_no_teams_file(self, monkeypatch, place):
        """role-runs, A place of another kind: a fix's place with no CREW_AGENT names no role as its caller."""
        in_place(monkeypatch, place)
        monkeypatch.setattr(crew, "load", lambda: pytest.fail("the teams file read for a place no run is named by"))
        assert (crew.caller(), crew.caller_label(), plan.agent()) == (None, None, f"{getpass.getuser()}@mac-studio")

    @pytest.mark.parametrize("place", ["crew-reviewer--wldn", "crew-operator--wldn", "crew-planner--madswan", "crew-boss--wldn", "crew-planner--wldn-x"])
    def test_a_place_named_as_a_run_whose_role_stands_or_is_none_names_nobody(self, monkeypatch, place):
        in_place(monkeypatch, f"{PLACES}/{place}")
        assert crew.caller() is None and crew.caller_label() is None and plan.may_write(RUNS, ("bolt", "new"), argparse.Namespace(bolt=None)) is None

    def test_crew_agent_names_the_caller_before_the_place(self, monkeypatch):
        in_place(monkeypatch, f"{PLACES}/crew-planner--wldn")
        monkeypatch.setenv("CREW_AGENT", "wldn-design")
        monkeypatch.setenv("CREW_LABEL", "wldn")
        assert (plan.agent(), crew.caller_label()) == ("wldn-design", "wldn")

    def test_a_command_forwarded_from_a_run_carries_its_name_and_partition(self, monkeypatch):
        """code.3: plugin/bin/crew sets them from crew.py run-name before it forwards, and crew_argv carries them."""
        in_place(monkeypatch, f"{PLACES}/crew-planner--wldn")
        monkeypatch.setattr(record, "_session", None)
        assert crew.crew_argv(RUNS, "mac-studio", "bolts")[:3] == ["env", "CREW_AGENT=wldn-planner", "CREW_LABEL=wldn"]
        assert crew.run_exports(crew.run_of(RUNS, f"{PLACES}/crew-ops--wldn")) == "export CREW_AGENT=wldn-ops CREW_LABEL=wldn CREW_SESSION=''"
        assert crew.run_exports(crew.run_of(RUNS, f"{PLACES}/crew-reviewer--wldn")) == ""

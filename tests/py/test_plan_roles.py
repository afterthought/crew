"""Who writes the plan directly (roles.1): plan.may_write for each kind of agent and command, and plan.conductor_scope,
which keeps a conductor to the bolt its team holds. The user writes everything; the planner only through proposals; a
dispatcher gives bolts; a conductor narrows, orders and sets dependencies within its own bolt; the design agent queues;
the main level's ops lands. That a refused write leaves a Refused entry is the proposals journey's (t-journey-plan)."""
import argparse

import pytest

from facts import FLEET, FactsWrite, apply, known, plan_text

import plan

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
    ("wldn-operator-mac-studio", ("unit", "drop"), None, "wldn-operator-mac-studio does not write the plan with crew unit drop: tell wldn-planner, who proposes it"),
    ("wldn-ops", ("bolt", "new"), None, "wldn-ops does not write the plan with crew bolt new: tell wldn-planner, who proposes it")])
def test_any_other_write_is_refused_naming_the_planner(monkeypatch, agent, key, bolt, said):
    assert may(monkeypatch, agent, key, bolt) == said


def test_a_conductor_writes_only_units_of_its_own_bolt(monkeypatch):
    monkeypatch.setenv("CREW_AGENT", "swb-1-conductor")
    w = FactsWrite(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("console-pages", KIT, "swb-2")],
                             units=[("a", KIT, "tenant-environments", []), ("b", KIT, "tenant-environments", []), ("c", KIT, "console-pages", [])]))
    apply(w, "unit order b --first", "unit after a b", ctx=known(w))
    assert [u.name() for u in w.plan.units_of("tenant-environments")] == ["b", "a"]
    with pytest.raises(plan.Refusal, match="swb-1-conductor writes only units of the bolt swb-1 holds, and c is in bolt console-pages: tell wldn-planner"):
        apply(w, "unit order c --first", ctx=known(w))

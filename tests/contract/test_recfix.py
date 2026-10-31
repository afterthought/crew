"""What crew assumes of recfix --check, each case naming what assumes it: plan.checked runs it on every file a write
commits, a signal's and a capture's markdown by its frontmatter as one record, so a value that breaks the record is
refused, named by its file and line, and nothing is pushed (plan.1, signals.4); a Move the moves file's enum does not
allow is refused (the route a unit add --signal writes); a hand edit that duplicates a key is refused by name
(read.1, crew bolts naming the commit); and a bolt given to a crossed team is marked Path: flume, the one Path the
plan takes."""
import re

import pytest

from crew import Refusal
import plan

SIG = "2026-10-12-chuck-mac-studio-abcd1234/01-tiles-split"


def test_a_signal_and_its_capture_pass_by_their_frontmatter():
    plan.checked({f"signals/{SIG}.md": plan.signal_md(SIG, "ask", "user", "tiles, seams", "Tiles split.", plan.quoted("Tiles split.", "14:00:00Z")),
                  "signals/2026-10-12-chuck-mac-studio-abcd1234/capture.md": "---\ncapture: x\nsource: operator\nsignals: 1\n---\n\n# x\n"})


def test_a_value_that_breaks_a_signals_frontmatter_is_refused_naming_the_file_and_its_line():
    text = plan.signal_md(SIG, "ask", "user", "tiles\nseams", "Tiles split at the seam.", plan.quoted("Tiles split.", "14:00:00Z"))
    with pytest.raises(Refusal, match=re.escape(f"signals/{SIG}.md fails recfix --check: 01-tiles-split.md: 6: error")):
        plan.checked({f"signals/{SIG}.md": text})


def test_a_route_the_moves_files_enum_does_not_allow_is_refused():
    route = "\n".join(plan.Rec("Move", [("Signal", SIG), ("Move", "route"), ("Target", "unit/u"), ("Date", "2026-10-12"), ("By", "d")]).lines())
    assert " drop route" in plan.MOVES
    plan.checked({"moves.rec": plan.MOVES + "\n" + route + "\n"})
    with pytest.raises(Refusal, match="^moves.rec fails recfix --check"):
        plan.checked({"moves.rec": plan.MOVES.replace(" drop route", " drop") + "\n" + route + "\n"})


def test_a_plan_with_a_duplicated_key_is_refused_by_name():
    text = "%rec: Unit\n%key: Unit\n\nUnit: a\nRepo: switchboard-kit\nIntent: once\n\nUnit: a\nRepo: switchboard-kit\nIntent: twice\n"
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check: .*duplicated key"):
        plan.recfix(text, "plan.rec")


def test_the_plan_takes_a_chore_among_its_units_and_refuses_any_other_kind():
    """op_unit_add's chore and plan.checked: a Unit record marked Kind: chore sits among the units, between two of them,
    and passes the plan's schema; a Kind the schema's enum does not hold is refused (plan.1, plan.11)."""
    unit = lambda name, kind=None: f"Unit: {name}\nRepo: crew\nBolt: b\n" + (f"Kind: {kind}\n" if kind else "") + f"Intent: {name} is done.\n\n"
    bolt = "Bolt: b\nRepo: crew\nGoal: Upkeep.\n\n"
    text = plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit") + "\n" + unit("a") + unit("bump", "chore") + unit("c")
    plan.recfix(text, "plan.rec")
    assert [u.name() for u in plan.Plan(text).chores()] == ["bump"]
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(text.replace("Kind: chore", "Kind: spike"), "plan.rec")


def test_a_bolt_given_to_a_crossed_team_is_marked_flume_and_no_other_path_passes():
    """A give to a crossed team marks its bolt Path: flume beside Team (the change teams-cross-to-flume-as-their-bolts-land,
    Decision 2): plan.checked takes it, and refuses a Path the Bolt set's enum does not hold (plan.1)."""
    bolt = "Bolt: x\nRepo: crew\nGoal: Cross.\nTeam: crw-4\nPath: flume\n\n"
    text = plan.HEADER.replace("%rec: Unit", bolt + "%rec: Unit")
    plan.recfix(text, "plan.rec")
    assert [b.get("Path") for b in plan.Plan(text).bolts()] == ["flume"]
    with pytest.raises(Refusal, match="^plan.rec fails recfix --check"):
        plan.recfix(text.replace("Path: flume", "Path: other"), "plan.rec")

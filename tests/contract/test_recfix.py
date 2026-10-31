"""What crew assumes of recfix --check, each case naming what assumes it: plan.checked runs it on every file a write
commits, a signal's and a capture's markdown by its frontmatter as one record, so a value that breaks the record is
refused, named by its file and line, and nothing is pushed (plan.1, signals.4); a Move the moves file's enum does not
allow is refused (the route a unit add --signal writes); and a hand edit that duplicates a key is refused by name
(read.1, crew bolts naming the commit)."""
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


MADSWAN = {"partitions": {"madswan": {"label": "madswan", "machine": "deneb", "blueprints": ["afterthought/blueprints"], "roles": {},
                                      "flume": {"design": False, "planner": "madswan-main", "reviewer": False, "ops": "madswan-main",
                                                "operator": False}}}}


def an_asks_write():
    """A write of the flywheel holding no asks.rec or roles.rec yet, as a branch before its first ask."""
    class W(plan.Write):
        def text(self, path):
            return self.files.get(path)
    return W(None, "madswan", None, plan.Plan(""))


def test_the_asks_turns_and_role_records_crew_writes_pass_recfix():
    """plan.ask_rec and plan.roles_lines, checked as land() checks every file a commit holds (plan.checked; plan.1,
    state.1): asks.rec with its two record sets, an ask with words over two lines and one keyed naming a card, a turn
    that took both and ended and one superseded, and roles.rec with the planner's and ops's records."""
    w = an_asks_write()
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "tell", "madswan-design", words="record 0053 is accepted\nand its rule amended")
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "card", "crew", names="proposal/12", key="card/req_1/2026-10-31T10:04:00Z")
    plan.roles_lines(w, MADSWAN, "madswan")
    pl = plan.Plan(w.files["asks.rec"])
    for n, end in ((1, [("Superseded", "2")]), (2, [("Ended", "2026-10-31T10:20:00Z"), ("Said", "proposed the fix bolt")])):
        pl.insert(plan.Rec("Turn", [("Turn", str(n)), ("Role", "planner"), ("Run", "madswan-planner"), ("Place", "crew-planner--madswan"),
                                    ("Host", "deneb"), ("Took", "ask/1"), ("Took", "place/7@1793440000"), ("Began", "2026-10-31T10:10:00Z")] + end))
    plan.checked({"asks.rec": pl.text(), "roles.rec": w.files["roles.rec"]})
    assert [r.get("Role") for r in plan.Plan(w.files["roles.rec"]).recs("Role")] == ["planner", "ops"]


@pytest.mark.parametrize("path, drop, field, value", [
    ("asks.rec", "Role", None, None), ("asks.rec", None, "What", "nudge"), ("asks.rec", None, "Id", "one"), ("asks.rec", "At", None, None),
    ("roles.rec", "Stream", None, None), ("roles.rec", None, "Effort", "fast"), ("roles.rec", None, "Role", "dispatcher")])
def test_an_ask_or_a_role_record_the_headers_do_not_allow_is_refused(path, drop, field, value):
    """role-runs, A malformed ask: an ask with no Role, of a kind the enum does not hold, numbered with no number or with
    no time, and a role record with no stream, an effort or a role crew has no kind for, each refused by recfix, so the
    write commits nothing (plan.1)."""
    w = an_asks_write()
    plan.ask_rec(w, MADSWAN, "madswan", "planner", "tell", "madswan-design", words="Go.")
    pl = plan.Plan(w.files[path])
    rec = pl.recs("Ask" if path == "asks.rec" else "Role")[0]
    if drop:
        rec.drop(drop)
    else:
        rec.set(field, value)
    with pytest.raises(Refusal, match=f"^{path} fails recfix --check"):
        plan.checked({path: pl.text()})

"""One landings card per kit's main (rail-cards, record 0031 as amended 2026-10-23, plan.16): what a land/ key names,
a kit's or a bolt's, and the run record's object for it; a bolt refused a kit's name; the card's rows in the plan's
order, a bolt held for a fix or a landing sluice refused at its head; the conflicts forecast between each row and main
and each row above it; and the one decision of what the raise does with the kit's card. Each on plain facts (code.7);
the raise's act on a stand-in for what it reaches beyond them. Its wiring is t-journey-land's and t-cards'."""
import argparse

import pytest

import cards
import crew
import plan

KITS = ("crew", "swancloud")
FLEET = {"partitions": {"swancloud": {"label": "swancloud", "machine": "mac-studio", "teams": ["swc-1", "crw-1"]}},
         "teams": {"swc-1": {"name": "swc-1", "label": "swancloud", "machine": "deneb",
                             "kit": {"name": "swancloud", "repo": "afterthought/swancloud", "main": "/s/main", "dir": "/s"}},
                   "crw-1": {"name": "crw-1", "label": "swancloud", "machine": "mac-studio",
                             "kits": [{"name": "crew", "repo": "afterthought/crew", "main": "/c/main", "dir": "/c"}],
                             "kit": {"name": "crew", "repo": "afterthought/crew", "main": "/c/main", "dir": "/c"}}}}


# ------------------------------------------------------------------------------------- what a land/ key names

def test_a_kits_key_is_its_landings_card():
    assert plan.land_key("land/crew", KITS) == ("kit", "crew")


def test_any_other_land_key_is_a_bolts():
    assert plan.land_key("land/doctor-rows", KITS) == ("bolt", "doctor-rows")


def test_an_old_key_with_the_head_is_the_bolts_even_when_named_as_a_kit():
    assert plan.land_key("land/doctor-rows/abc1234", KITS) == ("bolt", "doctor-rows")
    assert plan.land_key("land/crew/abc1234", KITS) == ("bolt", "crew")


@pytest.mark.parametrize("key", ["batch/7", "land/", "land/Crew", "proposal/3", None])
def test_a_key_that_is_no_landings_names_nothing(key):
    assert plan.land_key(key, KITS) is None


def test_a_kits_card_is_on_the_kit_and_a_bolts_on_the_bolt_in_the_run_record():
    assert cards.row_object("land/crew", KITS) == "kit/crew"
    assert cards.row_object("land/doctor-rows", KITS) == "bolt/doctor-rows"
    assert cards.row_object("land/crew") == "bolt/crew"  # no kit named: as before, a bolt's


def test_the_partitions_kits_are_read_from_the_teams_file():
    assert plan.partition_kits(FLEET, "swancloud") == ["crew", "swancloud"]


def test_a_bolt_named_as_a_kit_of_its_partition_is_refused():
    assert plan.kit_named("crew", KITS, "swancloud") == (
        "a bolt of swancloud may not be named crew: that is the name of a kit swancloud's teams build, whose landings "
        "card is land/crew")
    assert plan.kit_named("doctor-rows", KITS, "swancloud") is None


def test_the_plan_write_that_adds_a_bolt_named_as_a_kit_refuses_it_writing_nothing():
    class Ctx:
        fleet = FLEET

        def kit(self, kit):
            return "swancloud"
    a = argparse.Namespace(repo="swancloud", bolt="crew", goal="x", source=[], before=None)
    with pytest.raises(crew.Refusal, match="may not be named crew"):
        plan.op_bolt_new(Ctx(), a)
    assert plan.op_bolt_new(Ctx(), argparse.Namespace(**dict(vars(a), bolt="doctor-rows"))).act == "bolt.new"


# ---------------------------------------------------------------------------------------------- the card's rows

def facts(bolt, head="a" * 40, fixes=None):
    return dict(bolt=bolt, kit="crew", head=head, fixes=fixes or {})


def submitted(bolt, head, refused=None):
    return dict(Act="bolt.submit", On=[f"bolt/{bolt}"], Head=head, **({"Refused": refused} if refused else {}))


def test_the_rows_are_the_proven_bolts_in_the_plans_order_each_a_box():
    rows = plan.landing_rows(["w", "y", "x", "z"], {"z": facts("z"), "y": facts("y"), "w": facts("w")}, {})
    assert [(r["bolt"], r["box"]) for r in rows] == [("w", True), ("y", True), ("z", True)]


def test_a_fix_in_flight_holds_its_row_in_its_words_with_no_box():
    rows = plan.landing_rows(["y", "z"], {"y": facts("y", fixes={"fix/y/gap": "The zone list misses one zone."}),
                                          "z": facts("z", fixes={"fix/z/old": None})}, {})
    assert [(r["bolt"], r["box"], r["why"]) for r in rows] == [
        ("y", False, "held for a fix: The zone list misses one zone. (fix/y/gap)"),
        ("z", False, "held for fix/z/old until it merges or is dropped")]


def test_a_landing_refused_at_the_bolts_present_head_holds_its_row():
    head = "d" * 40
    held = plan.refusals([submitted("y", "c" * 40), submitted("y", head, "bolt/y did not land: sluice found a conflict")])
    row, = plan.landing_rows(["y"], {"y": facts("y", head)}, held)
    assert (row["box"], row["why"]) == (False, "held: sluice refused its landing at ddddddd, and it waits for its team's "
                                               "fix: bolt/y did not land: sluice found a conflict")
    assert plan.refused_at([submitted("y", head, "no")], "y", head) == "no"


def test_a_refusal_at_an_older_head_holds_nothing_once_the_fix_moved_it():
    held = plan.refusals([submitted("y", "c" * 40, "bolt/y did not land")])
    row, = plan.landing_rows(["y"], {"y": facts("y", "d" * 40)}, held)
    assert row["box"]
    assert plan.refused_at([submitted("y", "c" * 40, "no")], "y", "d" * 40) is None


def test_a_landing_after_a_refusal_holds_nothing():
    assert plan.refusals([submitted("y", "c" * 40, "no"), submitted("y", "c" * 40)]) == {}


# ---------------------------------------------------------------------------------------------- the forecasts

def test_two_bolts_on_one_file_the_lower_row_names_the_one_above():
    paths = {("z", "y"): ["plugin/lib/plan.py"]}
    got = plan.row_forecasts(["y", "z"], lambda ours, theirs: paths.get((ours, theirs), []))
    assert got == {"y": [], "z": [("y", ["plugin/lib/plan.py"])]}


def test_a_bolt_behind_main_names_main_first():
    paths = {("y", "main"): ["README.md"], ("z", "main"): ["a"], ("z", "y"): ["b"]}
    got = plan.row_forecasts(["y", "z"], lambda ours, theirs: paths.get((ours, theirs), []))
    assert got == {"y": [("main", ["README.md"])], "z": [("main", ["a"]), ("y", ["b"])]}


def test_a_forecast_git_could_not_tell_is_kept_as_not_made():
    got = plan.row_forecasts(["y", "z"], lambda ours, theirs: None if "y" in (ours, theirs) else [])
    assert got == {"y": [("main", None)], "z": [("y", None)]}


def test_merge_trees_words_are_read_as_its_paths():
    assert plan.tree_paths(0, "abc\n") == []
    assert plan.tree_paths(1, "abc\nREADME.md\nplan.py\nREADME.md\n") == ["README.md", "plan.py"]
    assert plan.tree_paths(128, "fatal") is None


def test_a_bolt_branch_crew_cannot_read_is_said_and_its_box_kept(monkeypatch):
    """rail-cards "A bolt branch crew cannot read": the row's forecast is said as not made, with why, and holds
    nothing, since the rows' boxes are landing_rows' alone."""
    calls = []

    def git(fleet, t, where, *args, ok=(0,)):
        calls.append(args)
        if args[:2] == ("rev-parse", "--verify"):
            return (0, "f" * 40) if "bolt/z" in args[3] else (1, "")
        return (0, "tree\n") if args[0] == "merge-tree" else (0, "")
    monkeypatch.setattr(plan, "kit_git", git)
    got, why = plan.forecast_rows(FLEET, "swancloud", "crew", ["y", "z"])
    assert got == {"y": [("main", None)], "z": [("y", None)]}
    assert why == {"y": "bolt/y is on no branch crew can read in /c/main on mac-studio, GitHub's or the host's",
                   "z": "bolt/y is on no branch crew can read in /c/main on mac-studio, GitHub's or the host's"}
    assert ("fetch", "-q", "origin") in calls
    assert [r for r in plan.landing_rows(["y", "z"], {"y": facts("y"), "z": facts("z")}, {}) if r["box"]] != []

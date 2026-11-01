"""One landings card per kit's main (rail-cards, record 0031 as amended 2026-10-23, plan.16): what a land/ key names,
a kit's or a bolt's, and the run record's object for it; a bolt refused a kit's name; the card's rows in the plan's
order, a bolt held for a fix or a landing sluice refused at its head; the conflicts forecast between each row and main
and each row above it; and the one decision of what the raise does with the kit's card. Each on plain facts (code.7);
the raise's act on a stand-in for what it reaches beyond them. Its wiring is t-journey-land's and t-cards'."""
import argparse
import base64
import contextlib
import fcntl
import json

import pytest

import cards
import crew
import plan

KITS = ("crew", "swancloud")
FLEET = {"partitions": {"swancloud": {"label": "swancloud", "machine": "mac-studio", "teams": ["swc-1", "crw-1"]}},
         "teams": {"swc-1": {"name": "swc-1", "label": "swancloud", "machine": "deneb", "flume": "swancloud",
                             "kit": {"name": "swancloud", "repo": "afterthought/swancloud", "main": "/s/main", "dir": "/s"}},
                   "crw-1": {"name": "crw-1", "label": "swancloud", "machine": "mac-studio", "flume": "swancloud",
                             "kits": [{"name": "crew", "repo": "afterthought/crew", "main": "/c/main", "dir": "/c"}],
                             "kit": {"name": "crew", "repo": "afterthought/crew", "main": "/c/main", "dir": "/c"}}}}


@pytest.fixture(autouse=True)
def kits(monkeypatch):
    """swancloud's kits as its plan and landings name them (plan.kits_read), with no branch read."""
    monkeypatch.setattr(plan, "kits_read", lambda fleet, label: list(KITS))


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


def test_a_bolt_named_as_a_kit_of_its_partition_is_refused():
    assert plan.kit_named("crew", KITS, "swancloud") == (
        "a bolt of swancloud may not be named crew: that is the name of a kit swancloud's plan or landings name, whose landings "
        "card is land/crew")
    assert plan.kit_named("doctor-rows", KITS, "swancloud") is None


def test_the_plan_write_that_adds_a_bolt_named_as_a_kit_refuses_it_writing_nothing():
    class Ctx:
        fleet = FLEET

        def kit(self, kit):
            return "swancloud"

        def kits(self, label):
            return KITS
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


def test_a_holds_reason_is_sluices_verdict_with_the_conflicts_paths_never_a_place_it_could_not_release():
    """The chore a-holds-reason-is-sluices-verdict-not-a-side-warning: sluice's wait on the landing's submission prints
    its record in conflict and says on standard error only that its round could not release another place (sluice
    0.36.4 exec.rs tell_abandoned); the hold carries the record's verdict, its paths, so the conductor reads a
    conflict, the team's to take main in for, and not the release, which is said to ops beside it."""
    head, old = "d" * 40, "a" * 40
    record = {"schema": "sluice/submission@1", "id": 7, "branch": "main", "head": head, "state": "conflict",
              "conflict": {"paths": ["plugin/lib/plan.py"], "with": []}}
    tidying = "could not release /c/places/old-unit, whose worktree no longer exists: its release command failed"
    verdict = plan.verdict_printed(json.dumps(record), 7)
    landed = (f"ORIGIN=yes\nFETCHED=ok\nGITHUB={old}\nOWN={old}\nHELD_GITHUB=no\nHELD_OWN=no\nRC=2 TIP={head} OLD={old} KEPT='' "
              f"WHY='' LEVEL='' SAID={base64.b64encode(verdict.encode()).decode()}\n")  # LANDED's report, handed the verdict
    _, refused = plan.landing_said("y", "crew", "h", landed, old, recorded=True)
    row, = plan.landing_rows(["y"], {"y": facts("y", head)}, plan.refusals([submitted("y", head, refused)]))
    assert row["why"] == ("held: sluice refused its landing at ddddddd, and it waits for its team's fix: #7 conflict: "
                          "plugin/lib/plan.py")
    told = plan.landing_said("y", "crew", "h", landed, old, beside=plan.beside_of(f"{tidying}\n", verdict))[1]
    assert "release" not in refused and f"sluice said: {tidying}." in told


def test_a_refusal_at_an_older_head_holds_nothing_once_the_fix_moved_it():
    held = plan.refusals([submitted("y", "c" * 40, "bolt/y did not land")])
    row, = plan.landing_rows(["y"], {"y": facts("y", "d" * 40)}, held)
    assert row["box"]
    assert plan.refused_at([submitted("y", "c" * 40, "no")], "y", "d" * 40) is None


def test_a_landing_after_a_refusal_holds_nothing():
    assert plan.refusals([submitted("y", "c" * 40, "no"), submitted("y", "c" * 40)]) == {}


def test_a_landing_left_standing_in_sluice_holds_its_row_for_no_fix():
    """A landing whose submission sluice answered with nothing crew can wait on, a pull request crew found no
    submission of, is recorded with its words and no refusal (plan.left_standing), since what sluice queued stands: its
    row keeps its box, never held for a fix the bolt does not need."""
    head = "d" * 40
    f = dict(RC="0", ID="", PULL="113", ANSWER="")
    standing = dict(submitted("y", head), Why=plan.left_standing("y", "crew", "/c/places/land-y", f, "sluice records none"))
    row, = plan.landing_rows(["y"], {"y": facts("y", head)}, plan.refusals([submitted("y", head, "no"), standing]))
    assert row["box"] and plan.refused_at([standing], "y", head) is None


def test_a_landing_stopped_at_the_bolts_present_head_keeps_its_box_saying_what_stopped_it():
    """rail-cards "A landing sluice or its host stopped keeps its box": recorded stopped, its row a box whose facts
    carry the head it was stopped at and what stopped it; once its head moves, its row says nothing of it."""
    head = "d" * 40
    stop = dict(submitted("y", head), Why="check:dagger could not run: the Dagger engine did not answer", Outcome="stopped")
    entries = [submitted("y", "c" * 40, "bolt/y did not land: sluice found a conflict"), stop]
    row, = plan.landing_rows(["y"], {"y": facts("y", head)}, plan.refusals(entries), plan.stops(entries))
    assert (row["box"], row["facts"]["stopped"]) == (True, (head, "check:dagger could not run: the Dagger engine did not answer"))
    moved, = plan.landing_rows(["y"], {"y": facts("y", "e" * 40)}, plan.refusals(entries), plan.stops(entries))
    assert moved["box"] and "stopped" not in moved["facts"]
    assert "stopped" not in plan.landing_rows(["y"], {"y": facts("y", head)}, {})[0]["facts"]


def test_a_bolt_forecast_to_conflict_with_main_takes_main_first_with_no_box():
    """rail-cards "Main landed a change the bolt also made"."""
    rows = plan.landing_rows(["y", "z"], {"y": facts("y"), "z": facts("z")}, {},
                             takes_main={"y": ("e4f5a6b", ["openspec/specs/artifact-buckets/spec.md"])})
    assert [(r["bolt"], r["box"], r.get("why"), r.get("takes_main")) for r in rows] == [
        ("y", False, "takes main first: forecast to conflict with main on openspec/specs/artifact-buckets/spec.md at "
                     "e4f5a6b, until a fix taking main in moves its head", True),
        ("z", True, None, None)]


def test_a_conflict_a_wait_recorded_holds_the_row_when_the_cards_own_forecast_was_not_made():
    """rail-cards "Raised again at the same heads": the record's conflict at the bolt's present head (main_conflict)."""
    head = "d" * 40
    recorded = [dict(Act="forecast", On=["bolt/y"], Heads=f"bolt/y@{head[:7]} main@2222222", Paths="README.md", Reached="wait")]
    row, = plan.landing_rows(["y"], {"y": facts("y", head)}, {}, takes_main={"y": plan.main_conflict(recorded, "y", head)})
    assert (row["box"], row["why"], row["takes_main"]) == (
        False, "takes main first: forecast to conflict with main on README.md at 2222222, until a fix taking main in moves its head", True)


def test_a_conflict_only_with_a_row_above_holds_nothing():
    """rail-cards "Only a bolt above it": a forecast against a row above is said on the row, not held."""
    rows = plan.landing_rows(["y", "z"], {"y": facts("y"), "z": dict(facts("z"), forecast=[("y", ["plan.py"])])}, {}, takes_main={})
    assert [r["box"] for r in rows] == [True, True]


def test_a_take_main_fix_in_flight_holds_its_row_as_taking_main_first_in_its_words():
    """rail-cards "The conductor started the fix"; any other fix holds the row in its words as ever."""
    words = "Take main into the bolt: it is forecast to conflict on README.md"
    y, z = plan.landing_rows(["y", "z"], {"y": facts("y", fixes={"fix/y/take-main-e4f5a6b": words}),
                                          "z": facts("z", fixes={"fix/z/take-main-e4f5a6b": words, "fix/z/gap": "A zone is missing."})}, {})
    assert (y["box"], y["why"], y["takes_main"]) == (False, f'takes main first: take-main-e4f5a6b taking main in: "{words}"', True)
    assert (z["box"], z.get("takes_main")) == (False, None)
    assert z["why"] == f'held for a fix: A zone is missing. (fix/z/gap); takes main first: take-main-e4f5a6b taking main in: "{words}"'


class TestCrossedTakesMain:
    """A crossed team's landing refused for a conflict with main launches its take-main fix with sluice's words, once,
    and its row says it takes main first (Decision 10 of teams-cross-to-flume-as-their-bolts-land, plan.8)."""
    MAIN, WORDS = "4d3d9be" + "0" * 33, "#137 conflict: README.md, plugin/lib/plan.py"

    @pytest.fixture(autouse=True)
    def ops(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-ops")

    def launched(self):
        """crossed crw-4's x, its unit a launched as a give launches it."""
        from facts import FactsWrite, crossed_fleet, flume_plan
        fleet = crossed_fleet()
        w = FactsWrite(flume_plan([("x", "crw-4", "flume")], [("a", "x", [], "unit", [])]), label="madswan")
        plan.reach_places(fleet, w, "x", fleet["teams"]["crw-4"])
        return w, fleet["teams"]["crw-4"]

    def test_a_landing_refused_for_a_conflict_launches_one_take_main_fix_with_sluices_words(self):
        """main-level ops's crew bolt submit x reads sluice refusing x for a conflict with main at 4d3d9be."""
        import runner
        w, t = self.launched()
        act, host, work, given = runner.take_main(w.plan, plan.requests_of(w).recs("Request"), "x", t, self.MAIN, self.WORDS)
        assert (act, host, work, given["Kind"], given["Name"], given["Base"], given["Recipient"]) == (
            "launch", "deneb", "fix/x/take-main-4d3d9be", "fix", "x--take-main-4d3d9be", "bolt/x", "madswan/planner")
        assert given["Brief"] == (
            "Take main into the bolt: merge origin/main, at 4d3d9be, into this place, cut from bolt/x, resolving each conflicting "
            "path keeping both intents, main's and the bolt's; sluice refused the bolt's landing for its conflict with main: "
            "#137 conflict: README.md, plugin/lib/plan.py")
        assert given["Brief"].startswith(plan.TAKE_MAIN)

    def test_read_twice_it_launches_nothing_more(self):
        """A later read of the same refusal finds x--take-main-4d3d9be standing."""
        import runner
        w, t = self.launched()
        act, host, work, given = runner.take_main(w.plan, plan.requests_of(w).recs("Request"), "x", t, self.MAIN, self.WORDS)
        plan.request(w, act, host, work, **given)
        assert runner.take_main(w.plan, plan.requests_of(w).recs("Request"), "x", t, self.MAIN, self.WORDS) is None

    def test_its_row_says_it_takes_main_first(self):
        import runner
        w, t = self.launched()
        brief = runner.take_main(w.plan, plan.requests_of(w).recs("Request"), "x", t, self.MAIN, self.WORDS)[3]["Brief"]
        held = plan.refusals([submitted("x", "a" * 40, "#137 conflict: README.md, plugin/lib/plan.py")])
        x, = plan.landing_rows(["x"], {"x": facts("x", fixes={"fix/x/take-main-4d3d9be": brief})}, held)
        assert (x["box"], x["takes_main"], x["why"]) == (False, True, f'takes main first: take-main-4d3d9be taking main in: "{brief}"')


def test_a_bolt_the_user_left_forecast_to_conflict_with_main_keeps_its_box_marked_that_it_would_take_main_first():
    """rail-cards "A bolt the user left" and "Left, and main conflicts with it": no fix is started for it, so it is not
    held taking main first."""
    rows = plan.landing_rows(["y", "z"], {"y": facts("y"), "z": facts("z")}, {}, takes_main={"z": ("e4f5a6b0", ["README.md"])},
                             left={"z"})
    assert [(r["bolt"], r["box"], r["facts"].get("would_main")) for r in rows] == [
        ("y", True, None), ("z", True, ("e4f5a6b", ["README.md"]))]
    # a left bolt forecast clean is a row as any
    assert plan.landing_rows(["z"], {"z": facts("z")}, {}, takes_main={}, left={"z"})[0] == dict(bolt="z", box=True, facts=facts("z"))


def test_a_left_bolt_whose_landing_was_stopped_keeps_both_marks():
    """A stop holds nothing (rail-cards "A landing sluice or its host stopped keeps its box"), and a left bolt forecast
    to conflict with main keeps its box: its row says both."""
    head = "a" * 40
    entries = [dict(submitted("z", head), Why="sluice exited 3", Outcome="stopped")]
    row, = plan.landing_rows(["z"], {"z": facts("z", head)}, {}, plan.stops(entries),
                             takes_main={"z": ("e4f5a6b0", ["README.md"])}, left={"z"})
    assert row["box"] and row["facts"]["would_main"] == ("e4f5a6b", ["README.md"])
    assert row["facts"]["stopped"] == (head, "sluice exited 3")


def test_a_left_bolt_with_a_fix_in_flight_or_sluices_refusal_is_held_as_before():
    """Those hold whatever the user chose (Decision 2)."""
    takes = {"y": ("e4f5a6b", ["README.md"]), "z": ("e4f5a6b", ["README.md"])}
    held = plan.refusals([submitted("z", "a" * 40, "bolt/z did not land: sluice found a conflict")])
    y, z = plan.landing_rows(["y", "z"], {"y": facts("y", fixes={"fix/y/gap": "A zone is missing."}), "z": facts("z")}, held,
                             takes_main=takes, left={"y", "z"})
    assert (y["box"], y["why"]) == (False, "held for a fix: A zone is missing. (fix/y/gap)")
    assert (z["box"], z["why"]) == (False, "held: sluice refused its landing at aaaaaaa, and it waits for its team's fix: "
                                           "bolt/z did not land: sluice found a conflict")


def test_a_new_head_with_no_conflict_forecast_has_its_box_again():
    """rail-cards "The fix merges": the record's conflict was at the head the fix moved the bolt from."""
    recorded = [dict(Act="forecast", On=["bolt/y"], Heads="bolt/y@ccccccc main@2222222", Paths="README.md", Reached="told")]
    takes = {b: c for b in ["y"] for c in [plan.main_conflict(recorded, b, "d" * 40)] if c}
    row, = plan.landing_rows(["y"], {"y": facts("y", "d" * 40)}, {}, takes_main=takes)
    assert row["box"] and "takes_main" not in row


# ---------------------------------------------------------------------------------------------- the forecasts

def test_two_bolts_on_one_file_the_lower_row_names_the_one_above():
    paths = {("z", "y"): ["plugin/lib/plan.py"]}
    got = plan.row_forecasts(["y", "z"], lambda ours, theirs: paths.get((ours, theirs), []))
    assert got == {"y": [], "z": [("y", ["plugin/lib/plan.py"])]}


def test_a_bolt_behind_main_names_main_first_and_alone():
    """A bolt forecast to conflict with main takes main first (landing_rows), so it is forecast against main alone and
    no row below is forecast against it."""
    paths = {("y", "main"): ["README.md"], ("z", "main"): ["a"], ("z", "y"): ["b"], ("w", "y"): ["c"], ("w", "x"): ["d"]}
    got = plan.row_forecasts(["y", "z", "x", "w"], lambda ours, theirs: paths.get((ours, theirs), []))
    assert got == {"y": [("main", ["README.md"])], "z": [("main", ["a"])], "x": [], "w": [("x", ["d"])]}


def test_a_bolt_the_record_holds_taking_main_first_is_forecast_against_main_alone():
    """rail-cards "Raised again at the same heads": a row the run record holds taking main first is no row above another."""
    asked = []
    got = plan.row_forecasts(["y", "z"], lambda ours, theirs: asked.append((ours, theirs)) or (["b"] if (ours, theirs) == ("z", "y") else []),
                             held=["y"])
    assert got == {"y": [], "z": []} and ("z", "y") not in asked


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
            return (0, "f" * 40) if "bolt/z" in args[3] or "/main^" in args[3] else (1, "")
        return (0, "tree\n") if args[0] == "merge-tree" else (0, "")
    monkeypatch.setattr(plan, "kit_git", git)
    got, why, at = plan.forecast_rows(FLEET, "swancloud", "crew", ["y", "z"])
    assert got == {"y": [("main", None)], "z": [("y", None)]}
    assert why == {"y": "bolt/y is on no branch crew can read in /c/main on mac-studio, GitHub's or the host's",
                   "z": "bolt/y is on no branch crew can read in /c/main on mac-studio, GitHub's or the host's"}
    assert ("fetch", "-q", "origin") in calls
    assert [r for r in plan.landing_rows(["y", "z"], {"y": facts("y"), "z": facts("z")}, {}) if r["box"]] != []


def where_read(monkeypatch, policy):
    """forecast_rows over bolt y, whose GitHub copy is at 1… and the host's at 2…, GitHub's copy holding policy (None
    for no policy file): the commit each merge-tree was given for y."""
    trees = []

    def git(fleet, t, where, *args, ok=(0,)):
        if args[:2] == ("rev-parse", "--verify"):
            return 0, ("1" if "refs/remotes/origin/" in args[3] else "2") * 40
        if args[0] == "show":
            return (128, "fatal: path does not exist") if policy is None else (0, policy)
        if args[0] == "merge-tree":
            trees.append(args[-1])
        return (0, "tree\n") if args[0] == "merge-tree" else (0, "")
    monkeypatch.setattr(plan, "kit_git", git)
    return plan.forecast_rows(FLEET, "swancloud", "crew", ["y"]), trees


def test_a_bolt_on_github_is_forecast_where_it_lives(monkeypatch):
    """bolt-plan "A bolt on GitHub is read where it lives": GitHub's copy, whose policy names origin for the bolt, not
    the host's lagging copy."""
    (got, why, at), trees = where_read(monkeypatch, '[branches."bolt/*"]\nremote = "origin"\n')
    assert why == {} and trees == ["1" * 40]


def test_a_bolt_kept_on_its_host_is_forecast_at_the_hosts_branch(monkeypatch):
    """bolt-plan "A bolt kept on its host": GitHub's copy names no remote for the bolt, or has no policy."""
    for policy in ("[branches.main]\nremote = \"origin\"\n", None):
        (got, why, at), trees = where_read(monkeypatch, policy)
        assert why == {} and trees == ["2" * 40]


def test_a_policy_crew_cannot_read_at_githubs_copy_is_said_and_forecasts_nothing(monkeypatch):
    (got, why, at), trees = where_read(monkeypatch, "[branches\n")
    assert got == {"y": [("main", None)]} and trees == []
    assert why["y"].startswith(".config/sluice.toml at origin/bolt/y is not TOML, so crew can't read bolt y: ")


def test_the_forecast_hands_back_the_revision_of_main_it_forecast_against(monkeypatch):
    """rail-cards "Main moves under an open card": the commit origin/main names after the fetch, which the merge-trees
    are made onto and the raise keeps."""
    (got, why, at), trees = where_read(monkeypatch, None)
    assert at == {"main": "1" * 40}


def test_a_forecast_whose_fetch_or_read_of_main_failed_hands_back_no_revision(monkeypatch):
    def fetch_refused(fleet, t, where, *args, ok=(0,)):
        if args[0] == "fetch":
            raise crew.Refusal("git fetch in /c/main on mac-studio failed: could not read from remote")
        return 0, ""
    monkeypatch.setattr(plan, "kit_git", fetch_refused)
    got, why, at = plan.forecast_rows(FLEET, "swancloud", "crew", ["y"])
    assert at is None and got == {"y": [("main", None)]} and why["y"].endswith("could not read from remote")

    def no_main(fleet, t, where, *args, ok=(0,)):
        return (1, "") if args[0] == "rev-parse" else (0, "")
    monkeypatch.setattr(plan, "kit_git", no_main)
    got, why, at = plan.forecast_rows(FLEET, "swancloud", "crew", ["y"])
    assert at is None and why == {"y": "/c/main on mac-studio has no origin/main to forecast against"}
    assert plan.forecast_rows(FLEET, "swancloud", "atlas-kit", ["y"])[2] is None


# ------------------------------------------------------------------------------------ when main moved under a card

M1, M2 = "a1b2c3d" + "0" * 33, "e4f5a6b" + "0" * 33


def test_a_card_main_moved_under_is_due_a_raise_and_one_it_did_not_is_not():
    """rail-cards "Main moves under an open card" and "Main has not moved"."""
    cards_ = [("swancloud", "crew"), ("swancloud", "swancloud")]
    mains = {("swancloud", "crew"): M2, ("swancloud", "swancloud"): M1}
    assert plan.landings_moved(cards_, mains, {("swancloud", "crew"): M1, ("swancloud", "swancloud"): M1}) == (
        [("swancloud", "crew")], [])


def test_a_card_with_no_revision_kept_is_due_a_raise():
    """A lost note costs one more raise."""
    assert plan.landings_moved([("swancloud", "crew")], {("swancloud", "crew"): M1}, {}) == ([("swancloud", "crew")], [])


def test_a_kit_whose_read_names_no_revision_is_unread_and_not_judged_moved():
    """read.2: an older gather leaves main_at out, and a kit not read has none."""
    cards_ = [("swancloud", "crew"), ("swancloud", "swancloud")]
    assert plan.landings_moved(cards_, {("swancloud", "crew"): None}, {("swancloud", "crew"): M1}) == (
        [], [("swancloud", "crew"), ("swancloud", "swancloud")])


def test_no_open_card_is_nothing_due():
    assert plan.landings_moved([], {("swancloud", "crew"): M2}, {("swancloud", "crew"): M1}) == ([], [])


# ------------------------------------------------------------------- a bolt's own work between two heads

def work_read(monkeypatch, moves, fetch=0, known=("abc1234", "d" * 40, "e" * 40), logs=None):
    """bolt_work over moves, git answering where the kit's forecasts are made: the fetch exiting fetch, rev-parse
    finding the commits known and each bolt on GitHub at e…, and each log its lines in logs, by (from, not); the git
    calls made."""
    calls = []

    def git(fleet, t, where, *args, ok=(0,)):
        calls.append(args)
        if args[0] == "fetch" and fetch:
            plan.fail(f"git fetch in {where} on {t['machine']} failed: fatal: unable to access GitHub")
        if args[:2] == ("rev-parse", "--verify"):
            rev = args[3].split("^")[0]
            return (0, "e" * 40) if rev.startswith("refs/remotes/origin/bolt/") else (0, rev) if rev in known else (1, "")
        if args[0] == "show":
            return 0, '[branches."bolt/*"]\nremote = "origin"\n'
        if args[0] == "log":
            return 0, (logs or {}).get((args[3], args[4]), "")
        return 0, ""
    monkeypatch.setattr(plan, "kit_git", git)
    return plan.bolt_work(FLEET, "swancloud", "crew", moves), calls


def test_a_bolts_own_work_is_its_non_merge_commits_main_lacks_gained_and_lost_between_the_heads(monkeypatch):
    """rail-cards "A ticked bolt's approval stands while its own work is unchanged", Decision 1: one fetch, main read
    at GitHub's, each log both ways."""
    logs = {("d" * 40, "^abc1234"): "1a2b3c4 fix: keep the lease\n", ("abc1234", "^" + "d" * 40): ""}
    got, calls = work_read(monkeypatch, {"z": ("abc1234", "d" * 40)}, logs=logs)
    assert got == {"z": dict(head="d" * 40, gained=[("1a2b3c4", "fix: keep the lease")], lost=[], why=None)}
    assert calls.count(("fetch", "-q", "origin")) == 1
    assert ("log", "--no-merges", "--format=%h %s", "d" * 40, "^abc1234", "^refs/remotes/origin/main") in calls
    # a head now not given is read where the bolt lives, GitHub's copy, as the forecasts read it
    got, _ = work_read(monkeypatch, {"z": ("abc1234", None)})
    assert got == {"z": dict(head="e" * 40, gained=[], lost=[], why=None)}


def test_a_kit_no_team_builds_reads_no_work_and_says_why(monkeypatch):
    monkeypatch.setattr(plan, "kit_git", lambda *a, **k: plan.fail("no git"))
    assert plan.bolt_work(FLEET, "swancloud", "flywheel", {"z": ("abc1234", "d" * 40)}) == {"z": dict(
        head="d" * 40, gained=[], lost=[], why="no team of swancloud builds flywheel, so crew reads no checkout of it")}


def test_a_fetch_refused_reads_no_work_in_gits_words(monkeypatch):
    """rail-cards "crew cannot compare the heads"."""
    got, calls = work_read(monkeypatch, {"z": ("abc1234", "d" * 40)}, fetch=1)
    assert got["z"]["why"] == "git fetch in /c/main on mac-studio failed: fatal: unable to access GitHub"
    assert not [c for c in calls if c[0] == "log"]


def test_a_sent_head_that_names_no_one_commit_reads_no_work_and_says_so(monkeypatch):
    got, calls = work_read(monkeypatch, {"z": ("0f0f0f0", "d" * 40)})
    assert got == {"z": dict(head="d" * 40, gained=[], lost=[],
                             why="your send's head, 0f0f0f0, names no one commit in /c/main on mac-studio")}
    assert not [c for c in calls if c[0] == "log"]


# ------------------------------------------------------------------------------------- what the raise does

H1, H2 = "abc1234" + "0" * 33, "def5678" + "0" * 33
TIMER = " every host's folder follows by swancloud's timer within minutes."


def box(bolt, head=H1):
    return dict(bolt=bolt, box=True, facts=facts(bolt, head))


def hold(bolt, why="held for a fix: one zone is missing (fix/y/gap)", head=H1):
    return dict(bolt=bolt, box=False, why=why, facts=facts(bolt, head))


def waiting(*heads):
    return {"status": "waiting", "heads": plan.card_heads(" ".join(heads))}


def answered(*heads):
    return {"status": "answered", "heads": plan.card_heads(" ".join(heads))}


def work(gained=(), lost=(), why=None, head=H2):
    """A bolt's own work between the head sent and its head now, as bolt_work reads it."""
    return dict(head=head, gained=list(gained), lost=list(lost), why=why)


LEASE = ("1a2b3c4", "fix: keep the lease")


def test_a_send_stands_at_the_head_sent_or_where_the_bolts_own_work_is_the_same():
    """rail-cards "A ticked bolt's approval stands while its own work is unchanged"."""
    assert plan.send_stands("abc1234", H1, None)
    assert plan.send_stands("abc1234", H2, work())
    assert not plan.send_stands("abc1234", H2, work([LEASE]))
    assert not plan.send_stands("abc1234", H2, work(lost=[LEASE]))
    assert not plan.send_stands("abc1234", H2, work(why="git log in /c/main on mac-studio failed: fatal: bad object"))
    assert not plan.send_stands("abc1234", H2, None)


def test_a_bolt_asked_again_is_said_with_the_work_it_gained_or_lost_or_why_crew_cant_tell():
    """rail-cards "A ticked bolt whose own work changed is asked again, saying what changed"."""
    assert plan.work_said("z", "abc1234", H2, work([LEASE])) == (
        "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease")
    assert plan.work_said("z", "abc1234", H2, work(lost=[LEASE])) == (
        "z's head is now def5678, no longer holding work of its own your send at abc1234 held: fix: keep the lease")
    assert plan.work_said("z", "abc1234", H2, work([LEASE], [("9f8e7d6", "test: wait for the lock")])) == (
        "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease, and no longer "
        "holding: test: wait for the lock")
    assert plan.work_said("z", "abc1234", H2, work(why="git fetch in /c/main on mac-studio failed: fatal: no route")) == (
        "z's head is now def5678, but crew could not tell whether z's own work changed since your send at abc1234: "
        "git fetch in /c/main on mac-studio failed: fatal: no route")


def test_a_bolt_asked_again_names_five_commits_of_each_list_and_how_many_more():
    six = [(f"{n}000000", f"fix: part {n}") for n in range(1, 7)]
    assert plan.work_said("z", "abc1234", H2, work(six)) == (
        "z's head is now def5678, with work of its own since your send at abc1234: fix: part 1; fix: part 2; "
        "fix: part 3; fix: part 4; fix: part 5; and 1 more")


def test_no_row_that_can_land_and_no_card_is_nothing():
    assert plan.landings_step([hold("y")], None, None, {"y"}) == ("none",)
    assert plan.landings_step([], None, None, set()) == ("none",)


def test_a_waiting_card_with_no_row_that_can_land_is_withdrawn_saying_why():
    assert plan.landings_step([hold("y")], waiting("y@abc1234"), None, {"y"}) == (
        "withdraw", "every bolt waiting to land is held: y, held for a fix: one zone is missing (fix/y/gap)")
    assert plan.landings_step([], waiting("y@abc1234"), None, set()) == ("withdraw", "no bolt waits to land on its main")


def test_rows_that_can_land_and_no_card_post_one():
    assert plan.landings_step([box("y"), hold("z")], None, None, {"y", "z"}) == ("post", [])


def test_a_waiting_card_whose_rows_head_moved_is_changed_in_place():
    step = plan.landings_step([box("y"), box("z", H2)], waiting("y@abc1234", "z@abc1234"), None, {"y", "z"})
    assert step == ("change", "z's head is now def5678", False, [])


def test_a_second_bolt_proven_changes_the_cards_form_so_it_is_followed():
    step = plan.landings_step([box("y"), box("z")], waiting("y@abc1234"), None, {"y", "z"})
    assert step == ("change", "z reads proven and joins the card", True, [])


def test_a_row_held_or_gone_is_named_and_the_events_own_note_comes_first():
    step = plan.landings_step([box("y"), hold("z")], waiting("y@abc1234", "z@abc1234", "w@abc1234"), None, {"y", "z"},
                              note=f"y: {plan.RELINKED}")
    assert step == ("change", f"y: {plan.RELINKED}; z is held for a fix: one zone is missing (fix/y/gap); "
                              "w no longer waits to land", True, [])


def test_a_waiting_card_nothing_changed_is_left():
    assert plan.landings_step([box("y")], waiting("y@abc1234"), None, {"y"}) == ("leave",)


def test_a_bolt_left_on_the_last_send_stays_unticked_while_its_head_stands():
    assert plan.landings_step([box("y"), box("z")], waiting("y@abc1234", "z@abc1234:left"), None, {"y", "z"},
                              note="x")[3] == ["z"]
    assert plan.landings_step([box("y"), box("z", H2)], waiting("y@abc1234", "z@abc1234:left"), None, {"y", "z"})[3] == []


def test_an_answered_card_is_left_while_a_ticked_bolt_is_still_in_the_plan_and_not_held():
    assert plan.landings_step([box("y"), box("z")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z"}) == ("leave",)
    assert plan.landings_step([box("z")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"z"}) == ("leave",)
    # z landed and not yet closed: in the plan, no row now, and still waited for
    assert plan.landings_step([hold("y")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z"}) == ("leave",)


def test_once_every_ticked_bolt_landed_it_is_closed_naming_where_and_nothing_follows():
    step = plan.landings_step([], answered("y@abc1234", "z@abc1234"), ["y", "z"], set(), landed={"y": "1" * 40, "z": "2" * 40})
    assert step == ("close", "Landed on GitHub's main: y at 1111111 and z at 2222222; every host's folder follows by "
                             "swancloud's timer within minutes.", None, [])


def test_one_left_out_is_closed_saying_so_and_a_new_card_follows_with_it_unticked():
    step = plan.landings_step([box("z")], answered("y@abc1234", "z@abc1234"), ["y"], {"z"}, landed={"y": "1" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z.", ["z"], [])


def test_a_landing_whose_entry_is_still_in_flight_is_read_as_still_landing_and_its_card_left():
    """read.5, plan.2: bolt.land's plan write reaches the branch a commit before its entry, and a close read between
    the two read the bolt gone with no landing recorded, saying 'Landed or left the plan' of a bolt that landed. The
    branch is read at the parent of the oldest commit whose entry it lacks, so that close reads y still landing and
    leaves the card, even when another host's entry lands between the write and its own, as a push refused under load
    leaves it; once the entry arrives it says where y landed; and a bolt that left by an act whose entry is there and
    is no landing is the one said to have landed or left the plan."""
    before, land, other, drop = ("20261030T140025Z-933437-deneb-8163-114", "20261030T140103Z-263678-deneb-74395-2",
                                 "20261030T140104Z-101010-mac-studio-512-1", "20261030T235959Z-000001-mac-studio-9-1")
    deneb, studio = "runs/deneb/2026-10-30.rec", "runs/mac-studio/2026-10-30.rec"
    record, theirs = f"Id: {before}\nAct: x\n\n", f"Id: {other}\nAct: stage.start\n\n"
    o, a, b, c, d, x = "0" * 40, "a" * 40, "b" * 40, "c" * 40, "d" * 40, "e" * 40
    half = [(b, a, [land]), (a, o, [before])]  # the plan's commit pushed, its entry not yet
    assert plan.decision_at(half, {deneb: record}) == a
    assert plan.landings_step([], answered("y@abc1234"), ["y"], {"y"}) == ("leave",)  # y in the plan at a
    between = [(x, b, [other])] + half  # another host's entry, its own commit holding it, lands first
    assert plan.decision_at(between, {deneb: record, studio: theirs}) == a
    assert plan.decision_at([(d, b, [drop])] + half, {deneb: record, "runs/mac-studio/2026-10-31.rec":
                                                     f"Id: {drop}\nAct: plan.drop\n\n"}) == a
    whole = [(c, x, [land])] + between  # the entry's own commit follows
    assert plan.decision_at(whole, {deneb: record + f"Id: {land}\nAct: bolt.land\n\n", studio: theirs}) == c
    assert plan.landings_step([], answered("y@abc1234"), ["y"], set(), landed={"y": "1" * 40}) == (
        "close", f"Landed on GitHub's main: y at 1111111;{TIMER}", None, [])
    # a write recorded past midnight is found in its host's file of the next day; a commit naming none is read
    assert plan.decision_at([(d, a, [drop]), (a, o, [before])], {"runs/mac-studio/2026-10-31.rec":
                                                                f"Id: {drop}\nAct: plan.drop\n\n", deneb: record}) == d
    assert plan.landings_step([], answered("y@abc1234"), ["y"], set()) == ("close", "Landed or left the plan: y.", None, [])
    assert plan.decision_at([(d, a, []), (a, o, [before])], {deneb: record}) == d
    assert plan.decision_at(half, {}) == o  # none of them holds its entry: the branch is read below them all
    assert plan.decision_at([(a, None, [before])], {}) == a and plan.decision_at([], {}) is None


STANDS = ("your send stands for it: it lands once its team's fix has only taken main in and sluice has proven it, with "
          "nothing asked.")
REFUSED = "held: sluice refused its landing at abc1234, and it waits for its team's fix: x"


def test_a_ticked_bolt_sluice_refused_is_held_and_the_rest_close_the_card():
    """rail-cards "A ticked bolt held at the close": the close keeps the send for z, saying so."""
    step = plan.landings_step([hold("z", REFUSED)], answered("y@abc1234", "z@abc1234", "w@abc1234"), ["y", "z", "w"], {"z"},
                              landed={"y": "1" * 40, "w": "3" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111 and w at 3333333;{TIMER} Held: z, {REFUSED}; {STANDS}",
                    None, [("z", "abc1234")])


def test_a_send_holding_only_a_held_bolt_closes_keeping_it_and_one_whose_work_changed_is_not_kept():
    step = plan.landings_step([hold("z", REFUSED)], answered("z@abc1234"), ["z"], {"z"})
    assert step == ("close", f"Held: z, {REFUSED}; {STANDS}", None, [("z", "abc1234")])
    held = "held for a fix: the lease (fix/z/lease)"
    step = plan.landings_step([hold("z", held, H2)], answered("z@abc1234"), ["z"], {"z"}, work={"z": work([LEASE])})
    assert step == ("close", f"Held: z, {held}; z's head is now def5678, with work of its own since your send at abc1234: "
                             "fix: keep the lease, so a card asks for it again once it reads proven.", None, [])
    # held at a new head its own work is the same at: kept
    step = plan.landings_step([hold("z", held, H2)], answered("z@abc1234"), ["z"], {"z"}, work={"z": work()})
    assert step[3] == [("z", "abc1234")]
    # followed while y still lands: the follow's send keeps the held z beside y
    step = plan.landings_step([box("y"), hold("z", REFUSED), box("w")], answered("y@abc1234", "z@abc1234"), ["y", "z"],
                              {"y", "z", "w"})
    assert (step[0], step[3]) == ("follow", [("y", "abc1234"), ("z", "abc1234")]) and f"Held: z, {REFUSED}; {STANDS}" in step[1]


def taking_main(bolt):
    return dict(hold(bolt, MAIN_FIRST), takes_main=True)


def test_a_ticked_bolt_then_taking_main_first_leaves_the_card_its_send_standing():
    """rail-cards "Ticked, then forecast to conflict" and "Ticked beside one that lands"."""
    assert plan.landings_step([taking_main("y")], answered("y@abc1234"), ["y"], {"y"}) == ("leave",)
    assert plan.landings_step([taking_main("y")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y"},
                              landed={"z": "2" * 40}) == ("leave",)


def test_a_ticked_bolt_taking_main_first_is_kept_on_the_send_when_a_new_card_follows():
    step = plan.landings_step([taking_main("y"), box("w")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z", "w"})
    assert step == ("follow", "Landing as you ticked: z. Taking main in first, your send standing for it: y. Since your "
                              "send, w reads proven, and the card that follows asks for it.", [], [("y", "abc1234"), ("z", "abc1234")])


def test_a_ticked_bolt_taking_main_first_whose_own_work_changed_keeps_no_send():
    """A send stands while the bolt takes main in only for the work the user sent (send_stands): one that gained work
    of its own is held, and asked for again once it reads proven."""
    y = dict(taking_main("y"), facts=facts("y", H2))
    work = {"y": dict(head=H2, gained=[("1a2b3c4", "fix: keep the lease")], lost=[], why=None)}
    step = plan.landings_step([y], answered("y@abc1234"), ["y"], {"y"}, work=work)
    assert step == ("close", f"Held: y, {MAIN_FIRST}; y's head is now def5678, with work of its own since your send at "
                             "abc1234: fix: keep the lease, so a card asks for it again once it reads proven.", None, [])


def test_a_ticked_bolt_held_for_any_other_fix_is_held_and_the_card_closed_keeping_its_send():
    """Only a bolt taking main in leaves the card; one held for another fix closes it, its send kept on the close."""
    step = plan.landings_step([hold("y")], answered("y@abc1234"), ["y"], {"y"})
    assert step == ("close", "Held: y, held for a fix: one zone is missing (fix/y/gap); your send stands for it: it lands "
                             "once its team's fix has only taken main in and sluice has proven it, with nothing asked.", None,
                    [("y", "abc1234")])


def test_a_landing_on_the_users_word_in_ops_pane_closes_a_waiting_card_no_row_of_which_can_land_as_answered_there():
    """main-level "A landing said in ops's pane closes its card naming the user's words": the word answers the card."""
    assert plan.landings_step([], waiting("y@abc1234"), None, set(), here=True) == ("answered", "no bolt waits to land on its main")
    assert plan.landings_step([hold("z")], waiting("y@abc1234", "z@abc1234"), None, {"z"}, here=True)[0] == "answered"
    step = plan.landings_step([box("z")], waiting("y@abc1234", "z@abc1234"), None, {"z"}, note="Landed on the user's word", here=True)
    assert step[:2] == ("change", "Landed on the user's word; y no longer waits to land")


def test_a_bolt_proven_after_the_answer_is_no_row_of_it_and_a_new_card_follows_it_with_the_rest():
    step = plan.landings_step([box("y"), box("z"), box("w")], answered("y@abc1234", "z@abc1234"), ["y"], {"y", "z", "w"})
    assert step == ("follow", "Landing as you ticked: y. Left: z. Since your send, w reads proven, and the card that "
                              "follows asks for it.", ["z"], [("y", "abc1234")])


STOP = "check:dagger could not run: the Dagger engine did not answer"


def stopped_box(bolt, head=H1, words=STOP):
    """A row that can land whose last landing at its head sluice or its host stopped (landing_rows)."""
    return dict(bolt=bolt, box=True, facts=dict(facts(bolt, head), stopped=(head, words)))


def test_an_answered_card_is_left_while_a_ticked_bolt_whose_landing_was_stopped_still_lands_on_the_send():
    """rail-cards "Checks that never ran": the stop holds nothing, so the user's send still lands it, and the card
    they answered is left as it is."""
    assert plan.landings_step([stopped_box("z")], answered("z@abc1234"), ["z"], {"z"}) == ("leave",)


def test_a_card_that_follows_names_a_stopped_bolt_as_still_landing_with_what_stopped_it_and_has_no_row_for_it():
    """rail-cards "A new card while it is stopped": the closed card's outcome names z as still landing on the send,
    with what stopped it, and the card that follows does not ask for z again."""
    step = plan.landings_step([stopped_box("z"), box("w")], answered("z@abc1234"), ["z"], {"z", "w"})
    assert step == ("follow", f"Landing as you ticked: z. z's last landing at abc1234 was stopped, nothing of the bolt's: {STOP}; "
                              "it lands on your send once that is cleared. Since your send, w reads proven, and the card that "
                              "follows asks for it.", [], [("z", "abc1234")])
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="z@abc1234")]
    assert plan.rows_unsent([stopped_box("z"), box("w")], plan.landings_sent(closes, "land/crew", "swancloud-ops")) == (
        [box("w")], ["z"], [])


def test_crew_card_read_says_what_stopped_a_bolt_the_send_lands_beside_the_command_that_lands_it():
    """rail-cards "Checks that never ran": crew card read land/crew names z as still landing on the send, saying what
    stopped its last landing and at which head, with the command that lands it; a bolt it does not land says nothing,
    nor does one whose last landing was not stopped."""
    sent = {"status": "answered", "turn": "agent", "answer": {"choiceIds": ["land:y", "land:z"]}}
    heads = plan.card_heads("y@abc1234 z@abc1234")
    stopped = plan.stops([dict(submitted("z", H2), Why=STOP, Outcome="stopped"), dict(submitted("w", H1), Why="x", Outcome="stopped"),
                          dict(submitted("y", H1), Why="x", Outcome="stopped"), submitted("y", H1, "sluice: y conflicts")])
    assert plan.landing_lines("swancloud", sent, heads, [], [], stopped) == [
        "  to land, in the card's order: y and z",
        f"  z's last landing at def5678 was stopped, nothing of the bolt's: {STOP}; once that is cleared, the submit below "
        "lands it on the user's send",
        "  lands them: crew bolt submit y z --label swancloud"]
    assert plan.landing_lines("swancloud", sent, heads) == plan.landing_lines("swancloud", sent, heads, [], [], {})
    assert plan.landing_lines("swancloud", {}, [], ["z"], [], stopped)[1].startswith("  z's last landing at def5678 was stopped")


def test_a_ticked_bolt_proven_again_at_a_new_head_is_asked_again_rather_than_waited_for():
    """rail-cards "A fix adds a commit": the card that follows asks for y, saying what it gained."""
    gained = {"y": work([LEASE])}
    step = plan.landings_step([box("y", H2), box("z")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z"}, work=gained)
    assert step == ("follow", "Landing as you ticked: z. Since your send, y's head is now def5678, with work of its own "
                              "since your send at abc1234: fix: keep the lease, and the card that follows asks for it.",
                    [], [("z", "abc1234")])
    step = plan.landings_step([box("y", H2)], answered("y@abc1234"), ["y"], {"y"}, work=gained)
    assert step == ("close", "Since your send, y's head is now def5678, with work of its own since your send at abc1234: "
                             "fix: keep the lease, and the card that follows asks for it.", [], [])


def test_a_ticked_bolt_that_only_took_main_in_is_waited_for_on_the_same_send():
    """rail-cards "The head moves by taking main in before the landing": the card is left as it is."""
    step = plan.landings_step([box("y"), box("z", H2)], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z"},
                              work={"z": work()})
    assert step == ("leave",)
    # once y has landed and z is still to be submitted, the send still lands z: left too
    assert plan.landings_step([box("z", H2)], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"z"},
                              work={"z": work()}) == ("leave",)
    # and once z lands too, the card closes, nothing asked again
    assert plan.landings_step([], answered("y@abc1234", "z@abc1234"), ["y", "z"], set(),
                              landed={"y": "1" * 40, "z": "2" * 40})[0] == "close"


def test_a_ticked_bolt_whose_work_crew_cannot_read_is_asked_again_saying_why():
    """rail-cards "crew cannot compare the heads"."""
    why = "git fetch -q origin in /c/main on mac-studio failed: fatal: unable to access GitHub"
    step = plan.landings_step([box("z", H2)], answered("z@abc1234"), ["z"], {"z"}, work={"z": work(why=why)})
    assert step == ("close", f"Since your send, z's head is now def5678, but crew could not tell whether z's own work "
                             f"changed since your send at abc1234: {why}, and the card that follows asks for it.", [], [])


def test_a_bolt_left_on_the_send_is_ticked_on_the_card_that_follows_once_its_head_moved():
    step = plan.landings_step([box("z", H2)], answered("y@abc1234", "z@abc1234"), ["y"], {"z"}, landed={"y": "1" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z. Since your send, z's head is now "
                             "def5678, and the card that follows asks for it.", [], [])


def test_the_bolts_a_followed_send_still_lands_are_no_row_of_any_card_after_it_while_their_head_stands():
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234"),
              dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k2", Heads="z@def5678"),
              dict(Act="card.close", Key="land/crew", By="crw-1-conductor", Card="req_b1", Heads="w@abc1234"),
              dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k3", Heads="w@abc1234", Refused="x")]
    sent = plan.landings_sent(closes, "land/crew", "swancloud-ops")
    assert sent == {"y": "abc1234", "z": "def5678"}
    rows = [box("y"), box("z"), hold("x"), box("w")]
    # z moved from the head sent with its own work unread, which holds no send (read.1); x is held, a row with no box
    unread = "but crew could not tell whether {b}'s own work changed since your send at {at}: crew read none of its work"
    assert plan.rows_unsent(rows, sent) == ([box("z"), hold("x"), box("w")], ["y"], [
        ("z", "z's head is now abc1234, " + unread.format(b="z", at="def5678"))])
    assert plan.rows_unsent([box("y", H2), hold("z")], sent) == ([box("y", H2), hold("z")], [], [
        ("y", "y's head is now def5678, " + unread.format(b="y", at="abc1234"))])
    assert plan.landings_sent([], "land/crew", "swancloud-ops") == {}


def test_a_sent_bolt_that_only_took_main_in_is_no_row_and_one_whose_work_changed_is_a_row_saying_so():
    """rail-cards "A refused bolt takes main in" and "A fix adds a commit"."""
    sent = {"y": "abc1234", "z": "abc1234"}
    rows = [box("y", H2), box("z", H2)]
    assert plan.rows_unsent(rows, sent, {"y": work(), "z": work([LEASE])}) == ([box("z", H2)], ["y"], [
        ("z", "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease")])


def test_a_send_whose_card_followed_before_ops_read_it_is_read_beside_the_card_that_followed():
    """The card ops reads under land/<kit> is the one that followed: the send it closed still lands its bolts first."""
    waits = {"status": "pending", "turn": "you"}
    heads = plan.card_heads("w@abc1234")
    assert plan.landing_lines("swancloud", waits, heads, ["y"]) == [
        "  to land on the user's send of an earlier card: y", "  lands them: crew bolt submit y --label swancloud"]
    sent = {"status": "answered", "turn": "agent", "answer": {"approved": True}}
    assert plan.landing_lines("swancloud", sent, heads, ["y", "z"]) == [
        "  to land on the user's send of an earlier card: y and z", "  to land, in the card's order: w",
        "  lands them: crew bolt submit y z w --label swancloud"]
    none = {"status": "answered", "turn": "agent", "answer": {"choiceIds": []}}
    assert plan.landing_lines("swancloud", none, plan.card_heads("w@abc1234 v@abc1234"), ["y"]) == [
        "  to land on the user's send of an earlier card: y", "  no bolt ticked on this card: nothing of it lands",
        "  lands them: crew bolt submit y --label swancloud"]


def test_what_an_earlier_send_still_lands_leaves_out_the_landed_the_asked_again_and_the_refused_at_its_head():
    sent = {"y": "abc1234", "z": "abc1234", "x": "abc1234", "v": "abc1234", "u": "abc1234"}
    refused = {"x": ("abc1234" + "0" * 33, "sluice: conflict in a.py"), "u": ("def5678", "sluice: a check failed")}
    # v landed and left the plan, z's own work changed at its new head, x was refused at its head now, the head sent;
    # u's refusal was at another head, which holds nothing
    now = {"y": H1, "z": H2, "x": H1, "u": H1}
    assert plan.sent_left(sent, now, {"y", "z", "x", "u"}, refused, {"z": work([LEASE])}) == (["y", "u"], [])
    assert plan.sent_left({}, {}, {"y"}, {}) == ([], [])


def test_an_earlier_send_lands_a_refused_bolt_once_its_fix_only_took_main_in_and_names_one_it_cant_tell_of():
    """main-level "Ops lands a bolt on a send that still stands": "No card open" and "A head crew cannot read"."""
    sent = {"z": "abc1234", "w": "abc1234", "q": "abc1234"}
    refused = {"z": ("abc1234" + "0" * 33, "sluice: conflict in plugin/lib/plan.py")}
    unread = "bolt/w is on no branch crew can read in /c/main on mac-studio, GitHub's or the host's"
    fetch = "git fetch -q origin in /c/main on mac-studio failed: fatal: unable to access GitHub"
    got = plan.sent_left(sent, {"z": H2, "w": None, "q": H2}, {"z", "w", "q"}, refused,
                         {"z": work(), "w": work(why=unread, head=None), "q": work(why=fetch)})
    assert got == (["z"], [("w", unread), ("q", fetch)])


class WorkActs:
    """A stand-in for the work read (CardActs.work): each bolt's head now and its own work as heads gives them, the
    moves it was asked for recorded."""

    def __init__(self, heads):
        self.heads, self.asked = heads, []

    def work(self, label, kit, moves):
        self.asked.append(moves)
        return {b: self.heads.get(b) or work(why=f"bolt/{b} is on no branch crew can read", head=None) for b in moves}


def test_the_read_of_an_earlier_send_reads_the_plan_only_when_one_stands_and_refuses_when_it_cant(monkeypatch):
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 q@abc1234")]
    read, acts = [], WorkActs({"y": work(head=H1)})
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: read.append(label))
    assert plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", [], [], acts) == ([], []) and not read
    with pytest.raises(crew.Refusal, match="^swancloud/main could not be read, so what an earlier send on land/crew still lands"):
        plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", closes, [], acts)
    bolts = [plan.Rec("Bolt", [("Bolt", "y"), ("Repo", "crew")]), plan.Rec("Bolt", [("Bolt", "q"), ("Repo", "swancloud")])]
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: argparse.Namespace(bolts=lambda: bolts))
    assert plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", closes, [], acts) == (["y"], [])
    assert acts.asked == [{"y": ("abc1234", None)}]  # one read, of the sent bolts the plan holds of the kit
    # a bolt on a row of the card read now is that card's to ask for
    assert plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", closes,
                                 plan.card_heads("y@def5678"), acts) == ([], [])


def read_unopened(monkeypatch, capsys, closes, works, json=False):
    """crew card read land/crew as swancloud-ops, who holds no card under it on this host, after closes, the plan
    holding y and z of crew, each bolt's head now and own work as works gives them: what it printed."""
    bolts = [plan.Rec("Bolt", [("Bolt", b), ("Repo", "crew")]) for b in ("y", "z")]
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: argparse.Namespace(bolts=lambda: bolts))
    monkeypatch.setattr(plan, "card_asker", lambda fleet, a: ("swancloud", "swancloud-ops"))
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setattr(cards, "host_entries", lambda record, label, host: closes)
    monkeypatch.setattr(plan, "bolt_work", lambda fleet, label, kit, moves: WorkActs(works).work(label, kit, moves))
    plan.card_read(FLEET, argparse.Namespace(key="land/crew", label=None, json=json, sub="read"))
    return capsys.readouterr().out


def test_with_no_card_open_ops_reads_what_an_earlier_send_still_lands_and_the_command_that_lands_it(monkeypatch, capsys):
    """main-level "Ops lands a bolt on a send that still stands", "No card open": refuses nothing."""
    closes = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234"),
              dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="z@abc1234")]
    assert read_unopened(monkeypatch, capsys, closes, {"z": work()}) == (
        "card land/crew: no landings card of crew is open\n"
        "  to land on the user's send of an earlier card: z\n"
        "  lands them: crew bolt submit z --label swancloud\n")


def test_with_no_card_open_a_sent_bolt_whose_head_crew_cant_read_is_named_and_left_out_of_the_command(monkeypatch, capsys):
    """main-level "A head crew cannot read"."""
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    assert read_unopened(monkeypatch, capsys, closes, {"y": work(head=H1)}) == (
        "card land/crew: no landings card of crew is open\n"
        "  can't tell whether the user's earlier send still lands z: bolt/z is on no branch crew can read\n"
        "  to land on the user's send of an earlier card: y\n"
        "  lands them: crew bolt submit y --label swancloud\n")
    assert json.loads(read_unopened(monkeypatch, capsys, closes, {"y": work(head=H1)}, json=True)) == {
        "key": "land/crew", "card": None, "earlier": ["y"], "unknown": {"z": "bolt/z is on no branch crew can read"}}
    # with no send standing, it says only that no card is open
    assert read_unopened(monkeypatch, capsys, [], {}) == "card land/crew: no landings card of crew is open\n"


class TestLandReadingRead:
    """crew card read land/<bolt>, the bolt's conductor's on its team's host (card-sessions "The session's decision
    reaches the owner as the card's answer"): the reading's decision alone, its annotations as notes on the bolt's row,
    an approval as landing nothing, then set aside so crew card session starts it anew; the kit's card untouched."""
    S = {"pid": 42, "document": "/c/00-y.md", "url": "http://mac-studio:19432/y", "started": "2026-10-23T10:00:00Z"}

    def read(self, monkeypatch, tmp_path, result=None, session=True, who="crw-1-conductor", team="crw-1", key="land/y"):
        d = tmp_path / "swancloud" / key
        d.mkdir(parents=True, exist_ok=True)
        if session:
            (d / "session.json").write_text(json.dumps(self.S))
        if result:
            (d / "result.json").write_text(json.dumps(result))
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        monkeypatch.setattr(plan, "card_asker", lambda fleet, a: ("swancloud", who))
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        monkeypatch.setattr(plan, "land_held", lambda fleet, label, bolt: (None, plan.Rec("Bolt", [("Bolt", bolt), ("Repo", "crew")]),
                                                                           FLEET["teams"].get(team)))
        monkeypatch.setattr(cards, "host_entries", lambda record, label, host: [])
        monkeypatch.setattr(cards, "Bridge", lambda *a, **k: pytest.fail("the read of a bolt's reading reached Pending You"))
        plan.card_read(FLEET, argparse.Namespace(key=key, label=None, json=False, sub="read"))
        return d

    def test_annotations_print_word_for_word_as_notes_on_its_row_and_the_reading_is_set_aside(self, monkeypatch, tmp_path, capsys):
        """card-sessions "Annotated in a landing's session"."""
        d = self.read(monkeypatch, tmp_path, {"decision": "annotated", "feedback": "1. 03-y-diff.txt: this drops the retry\n",
                                              "annotationCount": 1})
        assert capsys.readouterr().out == (
            "land/y: notes from its reading, as notes on the landing card:\n1. 03-y-diff.txt: this drops the retry\n"
            "land/y: its card is left as it is; crew card session land/y opens its reading again\n")
        assert sorted(p.name for p in d.iterdir()) == [".lock", "result.20261023T100000Z.json"]

    def test_an_approval_lands_nothing(self, monkeypatch, tmp_path, capsys):
        """card-sessions "Approved in a landing's session"."""
        self.read(monkeypatch, tmp_path, {"decision": "approved", "annotationCount": 0})
        assert capsys.readouterr().out.splitlines()[0] == (
            "land/y: approved in its reading, which lands nothing: the card's approval is the word to land")

    def test_nothing_sent_waits_on_the_user_and_forgets_nothing(self, monkeypatch, tmp_path, capsys):
        """card-sessions "Nothing decided yet"."""
        d = self.read(monkeypatch, tmp_path)
        assert capsys.readouterr().out == "land/y: its reading waits on the user, who has sent nothing from it\n"
        assert sorted(p.name for p in d.iterdir()) == ["session.json"]
        self.read(monkeypatch, tmp_path / "none", session=False)
        assert capsys.readouterr().out == "land/y: no reading of it runs on this host: crew card session land/y starts it\n"

    def test_any_agent_but_its_conductor_and_a_bolt_no_team_holds_are_refused(self, monkeypatch, tmp_path):
        with pytest.raises(crew.Refusal, match="^land/y's reading is crw-1-conductor's to read, not swc-1-conductor's$"):
            self.read(monkeypatch, tmp_path, who="swc-1-conductor")
        with pytest.raises(crew.Refusal, match="^bolt y is held by no team"):
            self.read(monkeypatch, tmp_path, team=None)

    def test_an_old_card_of_the_bolts_own_under_its_head_is_still_read_as_a_card(self, monkeypatch):
        monkeypatch.setattr(plan, "card_asker", lambda fleet, a: ("swancloud", "crw-1-conductor"))
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        monkeypatch.setattr(cards, "host_entries", lambda record, label, host: [])
        with pytest.raises(crew.Refusal, match="^crw-1-conductor holds no open card under land/y/abc1234 on mac-studio"):
            plan.card_read(FLEET, argparse.Namespace(key="land/y/abc1234", label=None, json=False, sub="read"))


def test_a_send_ticking_none_closes_it_at_once_landing_nothing():
    step = plan.landings_step([box("y"), box("z")], answered("y@abc1234", "z@abc1234"), [], {"y", "z"})
    assert step == ("close", "Sent with no bolt ticked, so nothing lands. Left: y and z.", ["y", "z"], [])


def test_the_ticked_bolts_are_read_in_the_cards_order_from_each_form_of_answer():
    heads = plan.card_heads("y@abc1234 z@abc1234:left w@def5678")
    assert heads == [("y", "abc1234", False), ("z", "abc1234", True), ("w", "def5678", False)]
    got = lambda answer: {"status": "answered", "turn": "agent", "answer": answer}
    assert plan.ticked_of(got({"choiceIds": ["land:w", "land:y"]}), heads) == ["y", "w"]
    assert plan.ticked_of(got({"answers": {"rows-1": {"choiceIds": ["land:z"]}, "rows-2": {"choiceIds": ["land:w"]}}}), heads) == ["z", "w"]
    assert plan.ticked_of(got({"approved": True}), heads[:1]) == ["y"]
    assert plan.ticked_of(got({"approved": False}), heads[:1]) == []
    assert plan.ticked_of({"status": "pending", "turn": "you"}, heads) is None


# ------------------------------------------------------------------------------------- which bolts are left

def left_set(heads, at="2026-10-24T10:00:00Z"):
    """A raise's record of the bolts the user left on land/crew, as landing.left."""
    return dict(Act="landing.left", On=["kit/crew"], Key="land/crew", At=at, **({"Heads": heads} if heads else {}))


def stop(bolt, head=H1):
    """main-level ops's record of the user's words stopping a bolt's landing, as bolt.leave."""
    return dict(Act="bolt.leave", On=[f"bolt/{bolt}"], Head=head, From=["session/s-1/u-7"], Chars=38)


def pane_landed(bolt):
    return dict(Act="bolt.submit", On=[f"bolt/{bolt}"], Head=H1, From=["session/s-1/u-9"], Chars=20)


NOW = {"y": H1, "z": H1}


class TestWhichBoltsAreLeft:
    """rail-cards "A bolt the user left stays left until they tick it" and "A bolt stopped in ops's pane is shown as
    left": plan.left_now at a raise, from the card held, the ticks, the heads and the run record; plan.left_of from the
    run record alone, as a conductor's wait and the rail read it."""

    def test_a_bolt_marked_left_on_a_waiting_card_is_left_at_its_head(self):
        assert plan.left_now(waiting("y@abc1234", "z@abc1234:left"), None, NOW, {}, []) == {"z": "abc1234"}

    def test_a_bolt_the_user_did_not_tick_on_an_answered_card_is_left(self):
        assert plan.left_now(answered("y@abc1234", "z@abc1234"), ["y"], NOW, {}, []) == {"z": "abc1234"}
        assert plan.left_now(answered("y@abc1234", "z@abc1234"), [], NOW, {}, []) == {"y": "abc1234", "z": "abc1234"}

    def test_a_left_bolt_stays_left_across_the_close_of_one_card_and_the_post_of_the_next(self):
        assert plan.left_now(None, None, NOW, {"z": "abc1234"}, []) == {"z": "abc1234"}
        assert plan.left_now(waiting("y@abc1234", "z@abc1234"), None, NOW, {"z": "abc1234"}, []) == {"z": "abc1234"}

    def test_a_stop_in_ops_pane_is_left(self):
        assert plan.left_now(waiting("y@abc1234", "z@abc1234"), None, NOW, {}, [("z", H1)]) == {"z": "abc1234"}
        assert plan.left_now(None, None, NOW, {}, [("z", H1)]) == {"z": "abc1234"}

    def test_a_tick_on_the_card_held_ends_it(self):
        assert plan.left_now(answered("y@abc1234", "z@abc1234"), ["y", "z"], NOW, {"z": "abc1234"}, [("y", H1)]) == {}

    def test_a_moved_head_ends_it(self):
        moved = {"y": H1, "z": H2}
        assert plan.left_now(waiting("y@abc1234", "z@abc1234:left"), None, moved, {"z": "abc1234"}, [("z", H1)]) == {}
        assert plan.left_now(answered("y@abc1234", "z@abc1234"), ["y"], moved, {}, []) == {}

    def test_a_bolt_that_is_no_row_now_is_not_left(self):
        assert plan.left_now(waiting("z@abc1234:left"), None, {"y": H1}, {"z": "abc1234"}, [("z", H1)]) == {}

    def test_the_record_gives_the_last_set_and_each_stop_since_at_the_bolts_head_now(self):
        entries = [left_set("y@abc1234"), stop("w"), left_set("z@abc1234"), stop("y"), stop("v", H2)]
        assert plan.left_marks(entries, "land/crew") == ({"z": "abc1234"}, [("y", H1), ("v", H2)])
        assert plan.left_of(entries, "land/crew", {"y": H1, "z": H1, "v": H1, "w": H1}) == {"z": "abc1234", "y": "abc1234"}
        assert plan.left_of(entries, "land/swancloud", {"y": H1, "z": H1}) == {"y": "abc1234"}

    def test_a_set_with_none_left_ends_every_one_before_it_and_a_refused_one_ends_none(self):
        assert plan.left_of([left_set("z@abc1234"), left_set("")], "land/crew", NOW) == {}
        assert plan.left_of([left_set("z@abc1234"), dict(left_set(""), Refused="no")], "land/crew", NOW) == {"z": "abc1234"}

    def test_a_landing_on_the_users_words_in_ops_pane_ends_a_stop_and_one_before_it_ends_none(self):
        assert plan.left_of([stop("z"), pane_landed("z")], "land/crew", NOW) == {}
        assert plan.left_of([left_set("z@abc1234"), pane_landed("z")], "land/crew", NOW) == {}
        assert plan.left_of([pane_landed("z"), stop("z")], "land/crew", NOW) == {"z": "abc1234"}
        refused = dict(pane_landed("z"), Refused="sluice refused it", From=[])
        assert plan.left_of([stop("z"), refused], "land/crew", NOW) == {"z": "abc1234"}


# ------------------------------------------------------------- the raise on the main machine, from each row's host

import json  # noqa: E402
import types  # noqa: E402

PLAN = ("%rec: Bolt\n\n" + "".join(f"Bolt: {b}\nRepo: {k}\nPath: flume\n\n" for b, k in
                                    [("y", "crew"), ("w", "swancloud"), ("z", "crew")]) + "%rec: Unit\n\n")


MAIN = "e4f5a6b" + "0" * 33


def row(bolt, head=H1, **more):
    return dict(bolt=bolt, box=True, facts=dict(dict(bolt=bolt, kit="crew", units=["a"], chores=[], batches={}, head=head, at=None,
                                                     moved=0, pr=None, team="crw-1", conductor="crw-1-conductor", preview=None,
                                                     link=f"http://mac-studio:19432/{bolt}"), **more))


class LandActs:
    """A stand-in for what the raise reaches (plan.CardActs) on the main machine: each bolt's row as its team's host
    gives it (rows, a missing one's host not answering), the forecasts, this host's run record (entries) and the
    partition's (partition), and Pending You's tools answered from answers."""

    def __init__(self, rows, entries=(), partition=(), answers=None, here="mac-studio", against_main=None, main=MAIN, works=None):
        self.rows, self.held, self.whole, self.answers, self.here = rows, list(entries), list(partition), dict(answers or {}), here
        self.calls, self.emitted, self.told, self.asked, self.works, self.worked = [], [], [], [], dict(works or {}), []
        # The forecast: each bolt's conflicts with main ({bolt: [("main", paths)]}) at the revision main (None, unread).
        self.against_main, self.main, self.forecasts, self.kept = dict(against_main or {}), main, [], {}
        # The kit's card's lock: each taking of it, and the kit it is held for while the raise is inside it.
        self.locked, self.holding = [], None

    @contextlib.contextmanager
    def raising(self, label, kit):
        self.locked.append((label, kit))
        self.holding = kit
        try:
            yield
        finally:
            self.holding = None

    def land_row(self, label, bolt, host):
        self.asked.append((bolt, host))
        got = self.rows.get(bolt)
        return (got, None) if got else (None, "ssh: connect to host deneb: timed out")

    def forecast(self, label, kit, bolts, held=()):
        self.forecasts.append((list(bolts), list(held)))
        return {b: self.against_main.get(b) or [] for b in bolts}, {}, self.main and {"main": self.main}

    def keep_main(self, label, kit, sha):
        self.kept[kit] = sha

    def kept_main(self, label, kit):
        return self.kept.get(kit)

    def work(self, label, kit, moves):
        self.worked.append(moves)
        return {b: self.works.get(b) or work(why="git log in /c/main on mac-studio failed: fatal: bad object") for b in moves}

    def entries(self, label):
        return self.held

    def partition(self, label):
        return self.whole

    def bridge(self, name, later, held=None):
        acts = self

        class Py:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

            def answer(self, tool, args):
                acts.calls.append((tool, args))
                return acts.answers.get(tool, ({"ok": True}, None))

            def call(self, tool, args):
                got, words = self.answer(tool, args)
                if words is not None:
                    raise crew.Refusal(f"Pending You refused {tool}: {words}")
                return got
        return Py()

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act, On=on))
        self.held.append(dict(fields, Act=act, On=on, By=fields.get("by")))

    def tell(self, name, text):
        self.told.append((name, text))
        return True

    def put(self, url, data, kind):
        return None

    def host(self):
        return self.here

    def caller(self):
        return "crw-1-conductor"

    def kits(self, label):
        return KITS


POSTED = {"match_area": ({"decision": "use", "suggestions": [{"areaId": "prj_crew"}]}, None),
          "post_request": ({"requestId": "req_k1", "version": 1}, None)}


def raised(monkeypatch, acts, note=None):
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(PLAN))
    return plan.raise_landings(FLEET, "swancloud", "crew", acts, note=note)


def test_two_proven_bolts_post_one_card_in_ops_name_with_two_boxes(monkeypatch, capsys):
    acts = LandActs({"y": row("y"), "z": row("z")}, answers=POSTED)
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.asked == [("y", "mac-studio"), ("z", "mac-studio")]  # w is swancloud's, no row of crew's card
    post = next(a for t, a in acts.calls if t == "post_request")
    assert (post["idempotencyKey"], post["session"]["label"], post["kind"], post["highStakes"]) == (
        "land/crew@swancloud", "swancloud-ops", "multi", True)
    assert [o["label"] for o in post["options"]] == ["1. y", "2. z"]
    assert acts.emitted == [dict(Act="card.post", On=["kit/crew"], by="swancloud-ops", Card="req_k1", Key="land/crew",
                                 Heads="y@abc1234 z@abc1234")]
    assert acts.told == [("swancloud-ops", "Your card land/crew is up for the user: call get_request (requestId req_k1, "
                                           "name swancloud-ops), to hear their answer.")]


def test_a_kits_card_is_raised_under_its_lock_every_read_and_act_inside_it(monkeypatch):
    """Two bolts landing at once each raise their kit's card as they close (t-journey-land, sluice's #402 on deneb,
    2026-10-30: both read the card open and closed it, the second recording "ended in Pending You already"): the raise
    holds the kit's lock over the plan, the rows, the record and Pending You, so the second reads the first's close."""
    acts = LandActs({"y": row("y"), "z": row("z")}, answers=POSTED)
    seen = []
    for name in ("land_row", "entries", "partition", "forecast", "bridge", "emit", "tell"):
        monkeypatch.setattr(acts, name, lambda *a, f=getattr(acts, name), n=name, **k: seen.append((n, acts.holding)) or f(*a, **k))
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: seen.append(("plan", acts.holding)) or plan.Plan(PLAN))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    assert acts.locked == [("swancloud", "crew")]
    assert {n for n, _ in seen} >= {"plan", "land_row", "entries", "partition", "bridge", "emit"}
    assert [(n, h) for n, h in seen if h != "crew"] == []


def test_the_kits_card_lock_is_held_by_one_raise_and_fetches_the_plan_afresh_under_it(monkeypatch, tmp_path):
    monkeypatch.setattr(plan, "CARDS", tmp_path)
    monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("/state", f"{label}/main"))
    lock = plan.landings_lock("swancloud", "crew")
    fetched = []

    def fetch(repo, ref, fresh=False):
        with open(lock, "w") as other, pytest.raises(BlockingIOError):  # fetched with the lock held
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fetched.append((ref, fresh))
    monkeypatch.setattr(plan, "fetch", fetch)
    with plan.CardActs(FLEET).raising("swancloud", "crew"):
        with open(lock, "w") as other, pytest.raises(BlockingIOError):  # a second raise of the kit's card waits
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with open(plan.landings_lock("swancloud", "swancloud"), "w") as other:  # another kit's card's does not
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
    with open(lock, "w") as other:  # and the kit's is free once the raise is done
        fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert fetched == [("swancloud/main", True)]
    assert lock.parent == tmp_path / "swancloud" / "land" and not (tmp_path / "swancloud" / "land" / "crew").exists()


def test_a_rows_head_moved_changes_the_waiting_card_in_place_naming_it(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    acts = LandActs({"y": row("y"), "z": row("z", H2)}, held,
                    answers={"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)})
    assert raised(monkeypatch, acts) == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    assert (change["requestId"], change["changeNote"], change["expectedVersion"]) == ("req_k1", "z's head is now def5678", 2)
    assert acts.emitted[-1]["Heads"] == "y@abc1234 z@def5678"


def test_a_moved_heads_row_names_the_new_head_as_what_brings_its_preview_up_and_says_the_old_one_went(monkeypatch):
    """rail-cards "A row's head moves while the card waits" and "The head moves with a preview up" (record 0043): the
    row as its team's host read it, nothing asked of sluice for the new head."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    moved = {"branch": "bolt/z", "head": H2, "state": "ask", "released": H1}
    acts = LandActs({"y": row("y", preview={"head": H1, "none": True}), "z": row("z", H2, preview=moved)}, held,
                    answers={"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)})
    assert raised(monkeypatch, acts) == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    face = "\n".join(change["artifacts"][0]["lines"])
    assert change["changeNote"] == "z's head is now def5678"
    assert ("Try it running from bolt/z at def5678: write on this card to bring it up, and that you are done to put it "
            "away. It is not held while the card waits. Its preview of abc1234 was released as the head moved.") in face
    assert "No preview." in face.split("**2. z**")[0]


def test_a_host_that_does_not_answer_is_named_and_the_rest_raised(monkeypatch, capsys):
    acts = LandActs({"y": row("y")}, answers=POSTED)
    raised(monkeypatch, acts)
    assert "card land/crew: mac-studio did not answer for bolt z (ssh: connect to host deneb: timed out), so its row is left off" in capsys.readouterr().err
    post = next(a for t, a in acts.calls if t == "post_request")
    assert (post["kind"], post["title"]) == ("approve", "Land the bolt y on crew's main")


def test_off_the_partitions_main_machine_the_raise_is_refused_naming_it(monkeypatch):
    with pytest.raises(crew.Refusal, match="crew's landings card is raised on mac-studio, where swancloud-ops's cards are"):
        raised(monkeypatch, LandActs({}, here="deneb"))


def test_an_answered_card_whose_ticked_bolts_all_landed_is_closed_naming_where_with_no_row_left(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    landed = [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40), dict(Act="bolt.land", On=["bolt/z"], Head="2" * 40)]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    acts = LandActs({}, held, landed, answers={"get_request": (answer, None)})
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan("%rec: Bolt\n\n%rec: Unit\n\n"))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    ack = next(a for t, a in acts.calls if t == "ack_answer")
    said = f"Landed on GitHub's main: y at 1111111 and z at 2222222;{TIMER}"
    assert ack["outcome"] == said
    assert acts.emitted[-1] == dict(Act="card.close", On=["kit/crew"], by="swancloud-ops", Card="req_k1", Key="land/crew",
                                    State="closed", Outcome=said, Rows="0", Answer="ticked y and z")
    assert not [t for t, _ in acts.calls if t == "post_request"]


def test_one_left_out_closes_the_card_and_a_new_one_follows_it_with_that_bolt_unticked(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y"]}}
    answers = dict(POSTED, get_request=(answer, None), post_request=({"requestId": "req_k2", "version": 1}, None))
    acts = LandActs({"z": row("z")}, held, [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40)], answers)
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan("%rec: Bolt\n\nBolt: z\nRepo: crew\nPath: flume\n\n%rec: Unit\n\n"))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k2"
    close = next(e for e in acts.emitted if e["Act"] == "card.close")
    assert (close["Outcome"], close["Rows"]) == (f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z.", "1")
    post = next(a for t, a in acts.calls if t == "post_request")
    opening, said = post["summary"].split("\n\n")[:2]
    assert post["follows"] == "req_k1" and said.startswith("Left on your last send.")
    assert opening.startswith("You answered the card before this one") and opening.endswith(
        f": ticked y, left z. Since then: landed on GitHub's main: y at 1111111;{TIMER} Left: z. z, which you left, waits on this card.")
    assert acts.emitted[-1]["Heads"] == "z@abc1234:left"


def test_a_send_ticking_none_closes_the_card_and_the_card_that_follows_says_every_row_was_left(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": []}}
    answers = dict(POSTED, get_request=(answer, None), post_request=({"requestId": "req_k2", "version": 1}, None))
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers=answers)
    assert raised(monkeypatch, acts) == "req_k2"
    assert next(e for e in acts.emitted if e["Act"] == "card.close")["Answer"] == "ticked none, left y and z"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["follows"] == "req_k1" and post["summary"].startswith(
        "You answered the card before this one: ticked none, left y and z. Since then: sent with no bolt ticked, so nothing lands. "
        "Left: y and z. y and z, which you left, wait on this card.")


def test_a_card_posted_after_the_kits_last_one_says_which_bolts_joined_moved_or_still_wait_since_the_send(monkeypatch):
    """The send's follow-on was refused by Pending You, so the next raise posts the kit's card afresh, following the
    card the user sent: y landed, z they left still waits, w reads proven since."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234", At="2026-10-23T13:10:00Z"),
            dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", State="closed", Rows="1", At="2026-10-23T14:02:00Z",
                 Answer="ticked y, left z")]
    acts = LandActs({"z": row("z"), "w": row("w", H2)}, held, [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40)], POSTED)
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(
        "%rec: Bolt\n\n" + "".join(f"Bolt: {b}\nRepo: crew\nPath: flume\n\n" for b in ("z", "w")) + "%rec: Unit\n\n"))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["follows"] == "req_k1" and post["summary"].startswith(
        "You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: ticked y, left z. Since then: w reads proven and "
        "joins the card. z, which you left, waits on this card.\n\n")
    assert plan.landings_since(plan.card_heads("y@abc1234 z@abc1234"), [box("z"), box("w", H2)]) == [
        "w reads proven and joins the card.", "z, which you left, waits on this card."]
    assert plan.landings_since(plan.card_heads("z@abc1234"), [box("z", H2)]) == ["z's head is now def5678."]


def test_a_bolt_proven_after_the_answer_gets_a_new_card_following_it_and_the_send_still_lands_the_rest(monkeypatch, capsys):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"approved": True}}
    answers = dict(POSTED, get_request=(answer, None), post_request=({"requestId": "req_k2", "version": 1}, None))
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers=answers)
    assert raised(monkeypatch, acts) == "req_k2"
    said = "Landing as you ticked: y. Since your send, z reads proven, and the card that follows asks for it."
    assert next(a for t, a in acts.calls if t == "ack_answer")["outcome"] == said
    assert not [t for t, _ in acts.calls if t == "update_request"]
    close = next(e for e in acts.emitted if e["Act"] == "card.close")
    assert (close["Card"], close["Outcome"], close["Heads"], close["Rows"]) == ("req_k1", said, "y@abc1234", "1")
    post = next(a for t, a in acts.calls if t == "post_request")
    assert (post["follows"], post["title"]) == ("req_k1", "Land the bolt z on crew's main")
    assert acts.emitted[-1]["Heads"] == "z@abc1234"
    # y still lands on that send: the card that followed is left as it is, and y joins no card while its head stands
    again = LandActs({"y": row("y"), "z": row("z")}, acts.held,
                     answers={"get_request": ({"status": "pending", "turn": "you", "version": 1}, None)})
    assert raised(monkeypatch, again) == "req_k2"
    assert [t for t, _ in again.calls] == ["get_request"]
    assert "card land/crew: y lands on the user's send of an earlier card, so it is no row of this one" in capsys.readouterr().out


LEFT = dict(Act="landing.left", On=["kit/crew"], by="swancloud-ops", Key="land/crew", Heads="z@abc1234")


def test_the_bolts_the_user_left_are_recorded_once_and_not_again_while_unchanged(monkeypatch):
    """rail-cards "A bolt the user left stays left until they tick it": the raise records the kit's left set when it
    changes, and a raise that changes nothing writes nothing (state.1)."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234:left")]
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers=dict(POSTED, **WAITING))
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.emitted == [LEFT]
    again = LandActs({"y": row("y"), "z": row("z")}, acts.held, answers=dict(POSTED, **WAITING))
    raised(monkeypatch, again)
    assert again.emitted == []


def test_a_bolt_left_on_a_closed_card_is_unticked_on_the_card_posted_after_it(monkeypatch):
    """rail-cards "Left again": the record carries what the user left across the close of one card and the post of
    the next."""
    acts = LandActs({"y": row("y"), "z": row("z")}, [LEFT], answers=POSTED)
    assert raised(monkeypatch, acts) == "req_k1"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["recommendedIds"] == ["land:y"]
    assert [e["Act"] for e in acts.emitted] == ["card.post"] and acts.emitted[0]["Heads"] == "y@abc1234 z@abc1234:left"


def test_a_left_bolt_whose_host_did_not_answer_stays_left_as_recorded(monkeypatch):
    """read.1: a row crew could not read ends nothing the user left."""
    acts = LandActs({"y": row("y")}, [LEFT], answers=POSTED)
    raised(monkeypatch, acts)
    assert not [e for e in acts.emitted if e["Act"] == "landing.left"]


def test_a_bolt_left_whose_head_moved_is_left_no_more_and_recorded_so(monkeypatch):
    """rail-cards "Its head moves": the card asks for it as a row at its new head."""
    acts = LandActs({"y": row("y"), "z": row("z", H2)}, [LEFT], answers=POSTED)
    raised(monkeypatch, acts)
    assert [e for e in acts.emitted if e["Act"] == "landing.left"] == [dict(LEFT, Heads="")]  # none left: the run record writes no Heads
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["recommendedIds"] == ["land:y", "land:z"]


def test_a_stop_in_ops_pane_shows_the_bolt_unticked_on_the_waiting_card_and_is_recorded(monkeypatch):
    """rail-cards "A bolt stopped in ops's pane is shown as left": crew bolt leave's note changes the card in place."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    acts = LandActs({"y": row("y"), "z": row("z")}, held, partition=[stop("z")], answers=dict(POSTED, **WAITING))
    assert raised(monkeypatch, acts, note="z was stopped on your words in swancloud-ops's pane") == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    assert change["changeNote"] == "z was stopped on your words in swancloud-ops's pane"
    assert change["recommendedIds"] == ["land:y"]
    assert acts.emitted[0] == LEFT and acts.emitted[-1]["Heads"] == "y@abc1234 z@abc1234:left"


def test_a_tick_on_a_send_ends_what_the_user_left_and_is_recorded(monkeypatch):
    """rail-cards "Ticked after a stop": the answered card ticks z, and the raise records none left."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234:left"), LEFT]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers={"get_request": (answer, None)})
    raised(monkeypatch, acts)
    assert [e for e in acts.emitted if e["Act"] == "landing.left"] == [dict(LEFT, Heads="")]  # none left: the run record writes no Heads


WAITING = {"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)}
MAIN_FIRST = "takes main first: forecast to conflict with main on README.md at e4f5a6b, until a fix taking main in moves its head"


def test_main_moving_so_one_of_two_conflicts_follows_the_card_with_the_other_as_its_one_box(monkeypatch):
    """rail-cards "One of two": every row forecast against main first; a list of two becomes an approval of one."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers=dict(POSTED, **WAITING), against_main={"z": [("main", ["README.md"])]})
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.forecasts == [(["y", "z"], [])] and acts.kept == {"crew": MAIN}
    assert next(a for t, a in acts.calls if t == "cancel_request")["reason"] == f"z {MAIN_FIRST}"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert (post["kind"], post["follows"]) == ("approve", "req_k1")
    assert next(a for a in post["artifacts"] if a["ref"] == "held-crew.md")["lines"] == [f"**z**: {MAIN_FIRST}"]
    assert acts.emitted[-1]["Heads"] == "y@abc1234"


def test_main_moving_so_one_of_three_conflicts_changes_the_card_in_place_saying_why(monkeypatch):
    """rail-cards "One of three"."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234 w@abc1234")]
    acts = LandActs({"y": row("y"), "z": row("z"), "w": row("w")}, held, answers=WAITING, against_main={"w": [("main", ["README.md"])]})
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(PLAN.replace("Bolt: w\nRepo: swancloud\n", "Bolt: w\nRepo: crew\n")))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    assert change["changeNote"] == f"w {MAIN_FIRST}"
    assert acts.emitted[-1]["Heads"] == "y@abc1234 z@abc1234"


def test_a_conflict_the_record_holds_at_the_rows_head_holds_it_with_no_forecast_against_it(monkeypatch):
    """rail-cards "Raised again at the same heads": the row is handed to the forecast as held, and held taking main first in the
    recorded files though the card's own forecast says nothing of it."""
    recorded = [dict(Act="forecast", On=["bolt/y"], Heads="bolt/y@abc1234 main@2222222", Paths="docs/a.md", Reached="wait")]
    acts = LandActs({"y": row("y"), "z": row("z")}, partition=recorded, answers=POSTED, main=None)
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.forecasts == [(["y", "z"], ["y"])] and acts.kept == {}
    post = next(a for t, a in acts.calls if t == "post_request")
    assert next(a for a in post["artifacts"] if a["ref"] == "held-crew.md")["lines"] == [
        "**y**: takes main first: forecast to conflict with main on docs/a.md at 2222222, until a fix taking main in moves its head"]
    assert acts.emitted[-1]["Heads"] == "z@abc1234"


HELD = dict(Act="forecast", On=["bolt/z"], why="bolt(z): forecast to conflict with main", Heads="bolt/z@abc1234 main@e4f5a6b",
            Paths="README.md", Reached="held")


def test_a_row_newly_taking_main_first_is_recorded_held_once_and_nobody_is_told(monkeypatch):
    """rail-cards "A row forecast to conflict with main takes main first until a fix takes main in" (Task notes 2.2 of the-team-machinery-leaves):
    the raise holds z's forecast on its row and starts nothing, and raised again at the same heads records nothing more,
    z still held by the record and the forecast."""
    acts = LandActs({"y": row("y"), "z": row("z")}, answers=POSTED, against_main={"z": [("main", ["README.md"])]})
    raised(monkeypatch, acts)
    assert [n for n, _ in acts.told] == ["swancloud-ops"]  # the card's owner, told it is up; no one told of z
    assert [e for e in acts.emitted if e["Act"] == "forecast"] == [HELD]
    post = next(a for t, a in acts.calls if t == "post_request")
    assert next(a for a in post["artifacts"] if a["ref"] == "held-crew.md")["lines"] == [f"**z**: {MAIN_FIRST}"]
    again = LandActs({"y": row("y"), "z": row("z")}, partition=[HELD], answers=dict(POSTED, **WAITING),
                     against_main={"z": [("main", ["README.md"])]})
    raised(monkeypatch, again)
    assert {n for n, _ in again.told} == {"swancloud-ops"} and not [e for e in again.emitted if e["Act"] == "forecast"]
    assert again.forecasts == [(["y", "z"], ["z"])]


def test_a_forecast_recorded_first_at_the_same_heads_is_not_recorded_again(monkeypatch):
    """A forecast the record holds at the same bolt head and revision of main, a conductor's wait's from before among
    them, is not recorded again."""
    acts = LandActs({"y": row("y"), "z": row("z")}, partition=[dict(HELD, Reached="wait")], answers=POSTED,
                    against_main={"z": [("main", ["README.md"])]})
    raised(monkeypatch, acts)
    assert not [e for e in acts.emitted if e["Act"] == "forecast"] and [n for n, _ in acts.told] == ["swancloud-ops"]


WOULD = "z, which you left, would take main first: forecast to conflict with main on README.md at e4f5a6b"


def test_a_left_bolt_main_conflicts_with_is_told_nothing_and_the_waiting_card_says_so_once(monkeypatch):
    """bolt-teams "A left bolt"; rail-cards "Left, and main conflicts with it" and "Raised again at the same heads"."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234:left")]
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers=dict(POSTED, **WAITING), against_main={"z": [("main", ["README.md"])]})
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.told == []
    assert [e for e in acts.emitted if e["Act"] == "forecast"] == [dict(HELD, Reached="left")]
    change = next(a for t, a in acts.calls if t == "update_request")
    assert change["changeNote"] == WOULD and change["recommendedIds"] == ["land:y"]
    assert change["options"][1]["consequence"].startswith("It would take main first if you tick it")
    assert acts.emitted[-1]["Heads"] == "y@abc1234 z@abc1234:left"
    again = LandActs({"y": row("y"), "z": row("z")}, acts.held, answers=dict(POSTED, **WAITING),
                     against_main={"z": [("main", ["README.md"])]})
    raised(monkeypatch, again)
    assert again.told == [] and again.emitted == [] and [t for t, _ in again.calls] == ["get_request"]


def test_a_left_bolt_ticked_at_the_same_heads_is_recorded_held_and_takes_main_first_nobody_told(monkeypatch):
    """rail-cards "Ticked after being left": the send stands for it, and nothing is started for it."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234:left"), LEFT,
            dict(HELD, Reached="left")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    acts = LandActs({"y": row("y"), "z": row("z")}, held, answers={"get_request": (answer, None)},
                    against_main={"z": [("main", ["README.md"])]})
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.told == []
    assert [e for e in acts.emitted if e["Act"] == "forecast"] == [HELD]
    assert [t for t, _ in acts.calls] == ["get_request"]  # the card is left as it is, the send standing for z


ONLY_Z = "%rec: Bolt\n\nBolt: z\nRepo: crew\nPath: flume\n\n%rec: Unit\n\n"


def refused_and_closed(monkeypatch):
    """The user sent land/crew with y and z ticked, y landed and sluice refused z at abc1234: the raise closes the
    card, keeping z's send; the run record's entries after it."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    z = dict(row("z"), box=False, why=REFUSED)
    acts = LandActs({"z": z}, held, [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40)], {"get_request": (answer, None)})
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(ONLY_Z))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    close = acts.emitted[-1]
    assert (close["Act"], close["Heads"]) == ("card.close", "z@abc1234")
    assert close["Outcome"] == f"Landed on GitHub's main: y at 1111111;{TIMER} Held: z, {REFUSED}; {STANDS}"
    assert not [t for t, _ in acts.calls if t == "post_request"]
    return acts.held


def test_a_refused_bolt_whose_fix_only_took_main_in_lands_on_the_same_send_with_no_card(monkeypatch, capsys):
    """rail-cards "A refused bolt takes main in" and "The fix merges": z reads proven at def5678, its own work the
    same, and no card asks for it."""
    entries = refused_and_closed(monkeypatch)
    acts = LandActs({"z": row("z", H2)}, entries, answers=POSTED, works={"z": work()})
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) is None
    assert acts.worked == [{"z": ("abc1234", H2)}] and not acts.calls
    assert "card land/crew: z lands on the user's send of an earlier card, so it is no row of this one" in capsys.readouterr().out


def test_a_refused_bolt_whose_fix_committed_a_change_is_asked_again_on_a_card_naming_it(monkeypatch):
    """rail-cards "A fix that changes the bolt's work merges": z has a box again, the card naming the fix's commit."""
    entries = refused_and_closed(monkeypatch)
    acts = LandActs({"z": row("z", H2)}, entries, answers=POSTED, works={"z": work([LEASE])})
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["title"] == "Land the bolt z on crew's main"
    assert post["summary"].startswith("z's head is now def5678, with work of its own since your send at abc1234: fix: "
                                      "keep the lease.\n\n")
    assert acts.emitted[-1]["Heads"] == "z@def5678"


def test_a_card_following_the_users_send_says_what_changed_of_a_bolt_asked_again_once_in_its_opening(monkeypatch):
    """rail-cards "A card that follows one the user answered says so first" and "A ticked bolt whose own work changed is
    asked again, saying what changed": the user ticked y and z, y is landing, and a fix committed to z: the card that
    follows opens with what they answered and what changed of z's work, said there once."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    answers = dict(POSTED, get_request=(answer, None), post_request=({"requestId": "req_k2", "version": 1}, None))
    acts = LandActs({"y": row("y"), "z": row("z", H2)}, held, answers=answers, works={"z": work([LEASE])})
    assert raised(monkeypatch, acts) == "req_k2"
    changed = "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["follows"] == "req_k1" and post["summary"].startswith(
        f"You answered the card before this one: ticked y and z. Since then: landing as you ticked: y. Since your send, {changed}, "
        "and the card that follows asks for it.\n\n")
    assert post["summary"].count(changed) == 1


def test_a_card_posted_after_the_users_send_opens_with_what_changed_of_a_bolt_asked_again_and_what_joined(monkeypatch):
    """The user's send kept z's yes as it closed, and a fix committed to z since: the kit's card posted afresh follows
    the card they sent, opening with what changed of z's work, once, and that w joined."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234", At="2026-10-23T13:10:00Z"),
            dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", State="closed", Rows="1", Heads="z@abc1234",
                 At="2026-10-23T14:02:00Z", Answer="ticked y and z")]
    acts = LandActs({"z": row("z", H2), "w": row("w")}, held, [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40)], POSTED,
                    works={"z": work([LEASE])})
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(
        "%rec: Bolt\n\n" + "".join(f"Bolt: {b}\nRepo: crew\nPath: flume\n\n" for b in ("z", "w")) + "%rec: Unit\n\n"))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k1"
    changed = "z's head is now def5678, with work of its own since your send at abc1234: fix: keep the lease"
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["follows"] == "req_k1" and post["summary"].startswith(
        f"You answered the card before this one, posted 2026-10-23 13:10 UTC, by 14:02 UTC: ticked y and z. Since then: {changed}. "
        "w reads proven and joins the card.\n\n")
    assert post["summary"].count(changed) == 1


def test_a_ticked_bolt_whose_head_moved_on_an_answered_card_is_read_once_and_waited_for_when_its_work_stands(monkeypatch, capsys):
    """rail-cards "The head moves by taking main in before the landing": the card the user answered is left."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y", "land:z"]}}
    acts = LandActs({"y": row("y"), "z": row("z", H2)}, held, answers={"get_request": (answer, None)}, works={"z": work()})
    assert raised(monkeypatch, acts) == "req_k1"
    assert acts.worked == [{"z": ("abc1234", H2)}] and [t for t, _ in acts.calls] == ["get_request"]
    assert "card land/crew: req_k1 is left as it is, the user having answered it" in capsys.readouterr().out


def test_the_raise_is_handed_to_the_main_machine_as_the_one_asking(monkeypatch, capsys):
    ran = []
    monkeypatch.setattr(crew, "this_host", lambda: "deneb")
    monkeypatch.setattr(crew, "crew_argv", lambda fleet, host, *args: ["crew-on", host, *args])
    monkeypatch.setattr(crew, "on_machine", lambda fleet, host, argv: ran.append((host, argv)) or types.SimpleNamespace(
        returncode=1, stdout="card land/crew: req_k1 changed\n", stderr="ssh: refused\n"))
    plan.land_hand(FLEET, "swancloud", "crew", "y is held for a fix: x")
    assert ran == [("mac-studio", ["crew-on", "mac-studio", "_land-card", "swancloud", "crew", "--note", "y is held for a fix: x"])]
    out, err = capsys.readouterr()
    assert out == "card land/crew: req_k1 changed\n" and err.endswith("crew's landings card is not raised on mac-studio: ssh: refused\n")


def test_on_the_main_machine_the_raise_runs_in_this_process_and_a_refusal_refuses_nothing(monkeypatch, capsys):
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setattr(plan, "raise_landings", lambda fleet, label, kit, note=None, pane=None: plan.fail(f"no plan, {note}"))
    plan.land_hand(FLEET, "swancloud", "crew", "x")
    assert capsys.readouterr().err == "crew's landings card is not raised: no plan, x\n"


def test_a_row_read_on_another_host_is_its_crew_land_row_and_one_crew_cannot_read_is_said(monkeypatch):
    acts = plan.CardActs(FLEET)
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setattr(crew, "crew_argv", lambda fleet, host, *args: list(args))
    out = {"y": json.dumps(row("y")), "z": "not a row"}
    monkeypatch.setattr(crew, "on_machine", lambda fleet, host, argv: types.SimpleNamespace(
        returncode=0, stdout=f"{out[argv[2]]}\n", stderr=""))
    assert acts.land_row("swancloud", "y", "deneb") == (row("y"), None)
    assert acts.land_row("swancloud", "z", "deneb") == (None, "crew _land-row printed no row crew reads: not a row")


def test_crew_land_row_prints_the_row_as_one_line_of_json(monkeypatch, capsys):
    monkeypatch.setattr(plan, "land_row", lambda fleet, label, bolt: print("ended land/y's session") or dict(bolt=bolt, why="no"))
    plan.land_row_cmd(FLEET, argparse.Namespace(label="swancloud", bolt="y", json=True))
    out, err = capsys.readouterr()
    assert (out, err) == ('{"bolt": "y", "why": "no"}\n', "ended land/y's session\n")


# --------------------------------------------------------------------- a row's reading ends with its row, not a card

class OldCardActs(LandActs):
    """LandActs where a reading and a preview would end: each end and release asked, recorded."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.ended, self.released = [], []

    def end(self, label, key):
        self.ended.append(key)
        return f"ended {key}'s session"

    def release_preview(self, label, key):
        self.released.append(key)
        return f"released {key}'s preview"


@pytest.mark.parametrize("key", ["land/y", "land/y/abc1234"])
@pytest.mark.parametrize("answers", [{"get_request": ({"status": "pending", "version": 1}, None)},
                                     {"get_request": ({"status": "answered", "version": 2}, None)}])
def test_an_old_card_of_a_bolts_own_closed_ends_neither_its_rows_reading_nor_its_preview(key, answers, capsys):
    """A closed card of the old per-bolt form is no word on the bolt's row: its reading and preview end with the row
    (land_end), whether crew withdrew the card waiting on the user or closed one they answered."""
    acts = OldCardActs({}, entries=[dict(Act="card.post", Key=key, By="crw-1-conductor", Card="req_l1", On=["bolt/y"])], answers=answers)
    assert plan.row_card_close(None, "swancloud", "crw-1-conductor", key, reason="y is now a row of crew's landings card", acts=acts) == "req_l1"
    assert (acts.ended, acts.released) == ([], [])
    assert "ended" not in capsys.readouterr().out


def test_the_sweep_keeps_a_rows_reading_live_though_a_card_of_the_bolts_own_was_closed_under_its_key():
    """sweep_judgment: y is a row of crew's landings card and its old land/y card was withdrawn, no card open under it;
    a batch closed with no card open is still taken out, and so is a reading whose bolt is no row."""
    closed = {"closed": {"land/y", "land/w", "batch/3"}}
    assert plan.sweep_judgment("swancloud", {"land/crew", "land/y", "batch/3"}, [], None, closed, {"land/y"}) == {
        "live": ["land/crew", "land/y"], "blind": []}
    assert plan.sweep_judgment("swancloud", {"land/crew"}, [], None, closed, set())["live"] == ["land/crew"]


def test_a_wait_whose_reading_crew_ended_says_it_ended_with_its_row_or_crew_card_end():
    assert plan.land_waited("land/y", None, False) == (
        "land/y: crew ended its reading, as its row was held or left its kit's landings card, or crew card end was run")


# ------------------------------------------------------------------- a landing in ops's pane, a card left elsewhere

PANE = "Landed on the user's word in swancloud-ops's pane; landed on GitHub's main at 1111111"
SAID = 'Landed on the user\'s word in swancloud-ops\'s pane, "Land crw-1\'s bolt"; landed on GitHub\'s main at 1111111'
WAITING = {"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)}


def test_a_pane_landing_closes_the_waiting_kits_card_no_row_of_which_can_land_as_answered_with_the_users_words(monkeypatch):
    """main-level "The card closes with the user's words": Pending You is sent the words, the run record keeps none."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234")]
    acts = LandActs({}, held, answers=WAITING)
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(PLAN))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts, note=SAID, pane=PANE) == "req_k1"
    tool, args = acts.calls[-1]
    assert (tool, args["answeredHere"], args["reason"]) == ("cancel_request", True, f"{SAID}; no bolt waits to land on its main")
    close = acts.emitted[-1]
    assert (close["Act"], close["State"], close["Outcome"]) == ("card.close", "closed", f"{PANE}; no bolt waits to land on its main")
    assert "Land crw-1's bolt" not in repr(acts.emitted)


def test_a_pane_landing_changes_the_kits_card_naming_the_users_words_while_another_row_can_land(monkeypatch):
    """main-level "Another row still waits"."""
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234 v@abc1234")]
    acts = LandActs({"z": row("z"), "v": row("v")}, held, answers=WAITING)
    three = PLAN.replace("%rec: Unit", "Bolt: v\nRepo: crew\nPath: flume\n\n%rec: Unit")
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(three))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts, note=SAID, pane=PANE) == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    assert change["changeNote"].startswith(SAID) and not [t for t, _ in acts.calls if t == "cancel_request"]


def test_the_sweeps_raise_of_a_kits_card_handed_an_older_copy_posts_it_saying_that_copy_is_dead(monkeypatch):
    """rail-cards "A landings card left on the host the main level left"."""
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan(PLAN))
    r = {"label": "swancloud", "key": "land/crew", "group": "land"}
    acts, plain = LandActs({"y": row("y")}, answers=POSTED), LandActs({"y": row("y")}, answers=POSTED)
    assert plan.raise_landings_row(FLEET, dict(r, dead="req_k0"), acts) == "req_k1"
    assert plan.raise_landings_row(FLEET, r, plain) == "req_k1"
    dead, bare = [next(a for t, a in x.calls if t == "post_request")["summary"] for x in (acts, plain)]
    assert dead == f"{cards.DEAD}\n\n{bare}"

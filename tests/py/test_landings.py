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
    (got, why), trees = where_read(monkeypatch, '[branches."bolt/*"]\nremote = "origin"\n')
    assert why == {} and trees == ["1" * 40]


def test_a_bolt_kept_on_its_host_is_forecast_at_the_hosts_branch(monkeypatch):
    """bolt-plan "A bolt kept on its host": GitHub's copy names no remote for the bolt, or has no policy."""
    for policy in ("[branches.main]\nremote = \"origin\"\n", None):
        (got, why), trees = where_read(monkeypatch, policy)
        assert why == {} and trees == ["2" * 40]


def test_a_policy_crew_cannot_read_at_githubs_copy_is_said_and_forecasts_nothing(monkeypatch):
    (got, why), trees = where_read(monkeypatch, "[branches\n")
    assert got == {"y": [("main", None)]} and trees == []
    assert why["y"].startswith(".config/sluice.toml at origin/bolt/y is not TOML, so crew can't read bolt y: ")


# ------------------------------------------------------------------------------------- what the raise does

H1, H2 = "abc1234" + "0" * 33, "def5678" + "0" * 33
TIMER = " every host's folder follows by swancloud's timer within minutes."


def box(bolt, head=H1):
    return dict(bolt=bolt, box=True, facts=facts(bolt, head))


def hold(bolt, why="held for a fix: one zone is missing (fix/y/gap)"):
    return dict(bolt=bolt, box=False, why=why, facts=facts(bolt))


def waiting(*heads):
    return {"status": "waiting", "heads": plan.card_heads(" ".join(heads))}


def answered(*heads):
    return {"status": "answered", "heads": plan.card_heads(" ".join(heads))}


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
                              note="A yes now frees swc-1 for d")
    assert step == ("change", "A yes now frees swc-1 for d; z is held for a fix: one zone is missing (fix/y/gap); "
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
                             "swancloud's timer within minutes.", None)


def test_one_left_out_is_closed_saying_so_and_a_new_card_follows_with_it_unticked():
    step = plan.landings_step([box("z")], answered("y@abc1234", "z@abc1234"), ["y"], {"z"}, landed={"y": "1" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z.", ["z"])


def test_a_ticked_bolt_sluice_refused_is_held_and_the_rest_close_the_card():
    step = plan.landings_step([hold("z", "held: sluice refused its landing at abc1234, and it waits for its team's fix: x")],
                              answered("y@abc1234", "z@abc1234", "w@abc1234"), ["y", "z", "w"], {"z"},
                              landed={"y": "1" * 40, "w": "3" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111 and w at 3333333;{TIMER} Held: z, held: sluice "
                             "refused its landing at abc1234, and it waits for its team's fix: x.", None)


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


def test_a_ticked_bolt_proven_again_at_a_new_head_is_asked_again_rather_than_waited_for():
    step = plan.landings_step([box("y", H2), box("z")], answered("y@abc1234", "z@abc1234"), ["y", "z"], {"y", "z"})
    assert step == ("follow", "Landing as you ticked: z. Since your send, y's head is now def5678, and the card that "
                              "follows asks for it.", [], [("z", "abc1234")])
    step = plan.landings_step([box("y", H2)], answered("y@abc1234"), ["y"], {"y"})
    assert step == ("close", "Since your send, y's head is now def5678, and the card that follows asks for it.", [])


def test_a_bolt_left_on_the_send_is_ticked_on_the_card_that_follows_once_its_head_moved():
    step = plan.landings_step([box("z", H2)], answered("y@abc1234", "z@abc1234"), ["y"], {"z"}, landed={"y": "1" * 40})
    assert step == ("close", f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z. Since your send, z's head is now "
                             "def5678, and the card that follows asks for it.", [])


def test_the_bolts_a_followed_send_still_lands_are_no_row_of_any_card_after_it_while_their_head_stands():
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234"),
              dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k2", Heads="z@def5678"),
              dict(Act="card.close", Key="land/crew", By="crw-1-conductor", Card="req_b1", Heads="w@abc1234"),
              dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k3", Heads="w@abc1234", Refused="x")]
    sent = plan.landings_sent(closes, "land/crew", "swancloud-ops")
    assert sent == {"y": "abc1234", "z": "def5678"}
    rows = [box("y"), box("z"), hold("x"), box("w")]
    assert plan.rows_unsent(rows, sent) == ([box("z"), hold("x"), box("w")], ["y"])
    assert plan.rows_unsent([box("y", H2), hold("z")], sent) == ([box("y", H2), hold("z")], [])  # moved, or held
    assert plan.landings_sent([], "land/crew", "swancloud-ops") == {}


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
    # v landed and left the plan, z is a row of the card read now at its new head, x was refused at the head sent;
    # u's refusal was at another head, which holds nothing
    assert plan.sent_left(sent, plan.card_heads("z@def5678"), {"y", "z", "x", "u"}, refused) == ["y", "u"]
    assert plan.sent_left({}, [], {"y"}, {}) == []


def test_the_read_of_an_earlier_send_reads_the_plan_only_when_one_stands_and_refuses_when_it_cant(monkeypatch):
    closes = [dict(Act="card.close", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234")]
    read = []
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: read.append(label))
    assert plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", [], []) == [] and not read
    with pytest.raises(crew.Refusal, match="^swancloud/main could not be read, so what an earlier send on land/crew still lands"):
        plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", closes, [])
    bolts = [plan.Rec("Bolt", [("Bolt", "y"), ("Repo", "crew")]), plan.Rec("Bolt", [("Bolt", "q"), ("Repo", "swancloud")])]
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: argparse.Namespace(bolts=lambda: bolts))
    assert plan.landings_earlier(FLEET, "swancloud", "crew", "land/crew", "swancloud-ops", closes, []) == ["y"]


def test_a_send_ticking_none_closes_it_at_once_landing_nothing():
    step = plan.landings_step([box("y"), box("z")], answered("y@abc1234", "z@abc1234"), [], {"y", "z"})
    assert step == ("close", "Sent with no bolt ticked, so nothing lands. Left: y and z.", ["y", "z"])


def test_the_ticked_bolts_are_read_in_the_cards_order_from_each_form_of_answer():
    heads = plan.card_heads("y@abc1234 z@abc1234:left w@def5678")
    assert heads == [("y", "abc1234", False), ("z", "abc1234", True), ("w", "def5678", False)]
    got = lambda answer: {"status": "answered", "turn": "agent", "answer": answer}
    assert plan.ticked_of(got({"choiceIds": ["land:w", "land:y"]}), heads) == ["y", "w"]
    assert plan.ticked_of(got({"answers": {"rows-1": {"choiceIds": ["land:z"]}, "rows-2": {"choiceIds": ["land:w"]}}}), heads) == ["z", "w"]
    assert plan.ticked_of(got({"approved": True}), heads[:1]) == ["y"]
    assert plan.ticked_of(got({"approved": False}), heads[:1]) == []
    assert plan.ticked_of({"status": "pending", "turn": "you"}, heads) is None


# ------------------------------------------------------------- the raise on the main machine, from each row's host

import json  # noqa: E402
import types  # noqa: E402

PLAN = ("%rec: Bolt\n\n" + "".join(f"Bolt: {b}\nRepo: {k}\nTeam: {t}\n\n" for b, k, t in
                                    [("y", "crew", "crw-1"), ("w", "swancloud", "swc-1"), ("z", "crew", "crw-1")]) + "%rec: Unit\n\n")


def row(bolt, head=H1, **more):
    return dict(bolt=bolt, box=True, facts=dict(bolt=bolt, kit="crew", units=["a"], chores=[], batches={}, head=head, at=None,
                                                moved=0, pr=None, team="crw-1", conductor="crw-1-conductor", preview=None,
                                                link=f"http://mac-studio:19432/{bolt}", **more))


class LandActs:
    """A stand-in for what the raise reaches (plan.CardActs) on the main machine: each bolt's row as its team's host
    gives it (rows, a missing one's host not answering), the forecasts, this host's run record (entries) and the
    partition's (partition), and Pending You's tools answered from answers."""

    def __init__(self, rows, entries=(), partition=(), answers=None, here="mac-studio"):
        self.rows, self.held, self.whole, self.answers, self.here = rows, list(entries), list(partition), dict(answers or {}), here
        self.calls, self.emitted, self.told, self.asked = [], [], [], []

    def land_row(self, label, bolt, host):
        self.asked.append((bolt, host))
        got = self.rows.get(bolt)
        return (got, None) if got else (None, "ssh: connect to host deneb: timed out")

    def forecast(self, label, kit, bolts):
        return {b: [] for b in bolts}, {}

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
        "land/crew", "swancloud-ops", "multi", True)
    assert [o["label"] for o in post["options"]] == ["1. y", "2. z"]
    assert acts.emitted == [dict(Act="card.post", On=["kit/crew"], by="swancloud-ops", Card="req_k1", Key="land/crew",
                                 Heads="y@abc1234 z@abc1234")]
    assert acts.told == [("swancloud-ops", "Your card land/crew is up for the user: call get_request (requestId req_k1, "
                                           "name swancloud-ops), to hear their answer.")]


def test_a_rows_head_moved_changes_the_waiting_card_in_place_naming_it(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    acts = LandActs({"y": row("y"), "z": row("z", H2)}, held,
                    answers={"get_request": ({"status": "pending", "turn": "you", "version": 2}, None)})
    assert raised(monkeypatch, acts) == "req_k1"
    change = next(a for t, a in acts.calls if t == "update_request")
    assert (change["requestId"], change["changeNote"], change["expectedVersion"]) == ("req_k1", "z's head is now def5678", 2)
    assert acts.emitted[-1]["Heads"] == "y@abc1234 z@def5678"


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
                                    State="closed", Outcome=said, Rows="0")
    assert not [t for t, _ in acts.calls if t == "post_request"]


def test_one_left_out_closes_the_card_and_a_new_one_follows_it_with_that_bolt_unticked(monkeypatch):
    held = [dict(Act="card.post", Key="land/crew", By="swancloud-ops", Card="req_k1", Heads="y@abc1234 z@abc1234")]
    answer = {"status": "answered", "turn": "agent", "version": 3, "answer": {"choiceIds": ["land:y"]}}
    answers = dict(POSTED, get_request=(answer, None), post_request=({"requestId": "req_k2", "version": 1}, None))
    acts = LandActs({"z": row("z")}, held, [dict(Act="bolt.land", On=["bolt/y"], Head="1" * 40)], answers)
    monkeypatch.setattr(plan, "plan_of", lambda fleet, label: plan.Plan("%rec: Bolt\n\nBolt: z\nRepo: crew\nTeam: crw-1\n\n%rec: Unit\n\n"))
    assert plan.raise_landings(FLEET, "swancloud", "crew", acts) == "req_k2"
    close = next(e for e in acts.emitted if e["Act"] == "card.close")
    assert (close["Outcome"], close["Rows"]) == (f"Landed on GitHub's main: y at 1111111;{TIMER} Left: z.", "1")
    post = next(a for t, a in acts.calls if t == "post_request")
    assert post["follows"] == "req_k1" and post["summary"].startswith("Left on your last send.")
    assert acts.emitted[-1]["Heads"] == "z@abc1234:left"


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


class TestWaitAcrossAnOldCardsClose:
    """crew card wait land/y while y is a row of crew's landings card, its reading recorded, and y's old land/y card is
    withdrawn by the rail's sweep meanwhile: the wait goes on, and returns the notes the user then sends."""
    FLEET = {"partitions": {"swancloud": {"label": "swancloud", "machine": "mac-studio", "teams": ["crw-1"]}},
             "teams": {"crw-1": FLEET["teams"]["crw-1"]}, "hosts": {}}
    S = {"pid": 42, "document": "/c/00-y.md", "url": "http://mac-studio:19432/y", "started": "2026-10-23T10:00:00Z"}

    def test_the_wait_outlasts_the_close_and_returns_the_readings_notes(self, monkeypatch, tmp_path, capsys):
        d = tmp_path / "swancloud" / "land/y"
        d.mkdir(parents=True)
        (d / "session.json").write_text(json.dumps(self.S))
        monkeypatch.setattr(plan, "CARDS", tmp_path)
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
        monkeypatch.setattr(plan, "plannotator_sessions", lambda: (None, "plannotator sessions did not answer in 8 seconds"))
        acts = LandActs({}, entries=[dict(Act="card.post", Key="land/y", By="crw-1-conductor", Card="req_l1", On=["bolt/y"])],
                        answers={"get_request": ({"status": "pending", "version": 1}, None)})
        acts.end = lambda label, key: plan.end_session(label, key)[0]
        acts.release_preview = lambda label, key: plan.fail(f"{key}'s preview released at its old card's close")
        polls = []

        def poll(seconds):
            polls.append(seconds)
            if len(polls) == 1:
                plan.row_card_close(None, "swancloud", "crw-1-conductor", "land/y", reason="y is now a row of crew's landings card", acts=acts)
            else:
                (d / "result.json").write_text(json.dumps({"decision": "annotated", "feedback": "y: say what the zone is."}))
        monkeypatch.setattr(plan.time, "sleep", poll)
        plan.card_wait(self.FLEET, argparse.Namespace(key="land/y", unit=None, label="swancloud", sub="wait"))
        assert capsys.readouterr().out.splitlines()[-2:] == [
            "land/y: notes from its reading, as notes on the landing card:", "y: say what the zone is."]
        assert len(polls) == 2 and not (d / "session.json").exists() and (d / "result.20261023T100000Z.json").exists()


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
    three = PLAN.replace("%rec: Unit", "Bolt: v\nRepo: crew\nTeam: crw-1\n\n%rec: Unit")
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

"""A partition's kits (Decision 3 of the-team-machinery-leaves): the repositories its plan and its landings name, with no
registry of repositories in crew (plan.partition_kits), and the run record's landings found in its files by their act
(record.acts_in). The landings card's key, a bolt's name check, the card hook's areas and the board's Inception lane read
the kits so; where a kit's work runs is not read here."""
import plan
import record

from facts import plan_text


def landing(repo, refused=None, act="bolt.land"):
    """A bolt.land entry as record.parse gives it."""
    return dict({"Id": "20261031T100000Z-1-deneb-1-1", "At": "2026-10-31T10:00:00Z", "Act": act, "On": ["bolt/b"], "From": [],
                 "Commit": []}, **({"Repo": repo} if repo else {}), **({"Refused": refused} if refused else {}))


def the_plan(bolts=(), units=()):
    return plan.Plan(plan_text(bolts, units))


class TestPartitionKits:
    def test_the_plan_alone_names_its_bolts_and_units_repositories(self):
        p = the_plan([("console-pages", "switchboard-kit", True)], [("a", "switchboard-kit", "console-pages", []),
                                                                     ("q", "breadboard-kit", None, [])])
        assert plan.partition_kits(p, []) == ["breadboard-kit", "switchboard-kit"]

    def test_the_landings_alone_name_a_kit_whose_last_bolt_has_landed(self):
        assert plan.partition_kits(the_plan(), [landing("atlas-kit")]) == ["atlas-kit"]

    def test_the_plan_and_the_landings_together(self):
        p = the_plan([("console-pages", "switchboard-kit", False)])
        assert plan.partition_kits(p, [landing("atlas-kit"), landing("switchboard-kit")]) == ["atlas-kit", "switchboard-kit"]

    def test_none_where_neither_names_one_or_the_branch_is_not_started(self):
        assert plan.partition_kits(the_plan(), []) == []
        assert plan.partition_kits(None, []) == []

    def test_a_kit_named_twice_is_one_kit(self):
        p = the_plan([("b1", "crew", True), ("b2", "crew", False)], [("a", "crew", "b1", []), ("q", "crew", None, [])])
        assert plan.partition_kits(p, [landing("crew"), landing("crew")]) == ["crew"]

    def test_a_refused_landing_or_another_act_names_no_kit(self):
        assert plan.partition_kits(the_plan(), [landing("atlas-kit", refused="it conflicts"), landing("atlas-kit", act="bolt.drop"),
                                                landing(None)]) == []


class TestKitIn:
    def test_a_kit_is_named_by_its_name_or_its_forge_address_either_way_round(self):
        assert plan.kit_in("switchboard-kit", ["switchboard-kit"])
        assert plan.kit_in("WilldanGroup/switchboard-kit", ["switchboard-kit"])
        assert plan.kit_in("flywheel-web", ["agentplot/flywheel-web"])
        assert not plan.kit_in("atlas-kit", ["switchboard-kit"])


class TestKeys:
    """The partition's kits tell a kit's landings card from a bolt's, refuse a bolt under a kit's name, and say which
    kit's area an asker may make."""

    def test_a_landings_key_names_a_kit_of_the_plan_or_the_landings(self):
        kits = plan.partition_kits(the_plan([("b", "crew", True)]), [landing("atlas-kit")])
        assert plan.land_key("land/crew", kits) == ("kit", "crew")
        assert plan.land_key("land/atlas-kit", kits) == ("kit", "atlas-kit")
        assert plan.land_key("land/b", kits) == ("bolt", "b")

    def test_a_bolt_is_not_named_as_a_kit_the_landings_name(self):
        assert plan.kit_named("atlas-kit", plan.partition_kits(the_plan(), [landing("atlas-kit")]), "wldn") == (
            "a bolt of wldn may not be named atlas-kit: that is the name of a kit wldn's plan or landings name, whose landings "
            "card is land/atlas-kit")

    def test_an_area_is_made_for_a_kit_the_partition_names_and_none_other(self):
        fleet = {"partitions": {"wldn": {"label": "wldn", "machine": "chuck-herdr-alpha"}}, "teams": {}, "hosts": {}}
        kits = ["agentplot/flywheel-web", "switchboard-kit"]
        refused = lambda key: plan.card_refusal(fleet, "wldn-ops", "wldn", "create_area", key, kits)
        assert refused("create-area:WilldanGroup/switchboard-kit") is None
        assert refused("create-area:agentplot/flywheel-web") is None
        assert refused("create-area:WilldanGroup/atlas-kit") == (
            "crew refuses an area under create-area:WilldanGroup/atlas-kit: wldn-ops makes a kit's area only under "
            "create-area:agentplot/flywheel-web or create-area:<owner>/switchboard-kit.")
        assert plan.card_refusal(fleet, "wldn-ops", "wldn", "create_area", "create-area:a/b", []) == (
            "crew refuses an area under create-area:a/b: no kit's area is wldn-ops's to make: wldn's plan and landings name no kit.")


class TestActsIn:
    """A partition's run record is megabytes, so its landings are found by their Act line before anything is parsed."""
    TEXT = ("%rec: Entry\n\n"
            "Id: 1\nAt: 2026-10-30T10:00:00Z\nAct: bolt.give\nOn: bolt/b\nRepo: crew\n\n"
            "Id: 2\nAt: 2026-10-30T11:00:00Z\nAct: bolt.land\nOn: bolt/b\nRepo: crew\nHead: abc\n\n"
            "Id: 3\nAt: 2026-10-30T12:00:00Z\nAct: bolt.landing\nOn: bolt/c\n\n"
            "Id: 4\nAt: 2026-10-30T13:00:00Z\nAct: bolt.land\nOn: bolt/c\nRefused: it conflicts")

    def test_each_entry_of_the_act_and_no_other(self):
        assert [(e["Id"], e.get("Repo"), e.get("Refused")) for e in record.acts_in(self.TEXT, "bolt.land")] == [
            ("2", "crew", None), ("4", None, "it conflicts")]

    def test_an_entry_ending_the_file_at_its_act_is_found(self):
        assert [e["Id"] for e in record.acts_in("Id: 5\nAt: 2026-10-30T14:00:00Z\nRepo: crew\nAct: bolt.land", "bolt.land")] == ["5"]

    def test_a_file_with_none_gives_none(self):
        assert record.acts_in("", "bolt.land") == [] and record.acts_in("%rec: Entry\n", "bolt.land") == []

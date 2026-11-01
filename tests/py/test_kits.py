"""A partition's kits (Decision 3 of the-team-machinery-leaves): the repositories its plan and its landings name, with no
registry of repositories in crew (plan.partition_kits), and the run record's landings found in its files by their act
(record.acts_in). The landings card's key, a bolt's name check, the card hook's areas and the board's Inception lane read
the kits so. Where a kit's work runs (Decisions 4 and 5, the user's ruling of 2026-11-01): crew looks up no kit's host,
and reads where a bolt's or a kit's work runs from what the runner that took it reported (plan.bolt_at, plan.kit_at,
runner.where), a partition's hosts its main level's and its runners' (plan.hosts_of); and what crew does before any runner
has taken a kit's work, it does in the checkout its partition's main-level host keeps of the kit (plan.main_kit,
crew.kit_kept, crew.kits_on)."""
import json

import pytest

import plan
import record
import runner

from facts import FLUME, flume_plan, plan_text


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
        fleet = {"partitions": {"wldn": {"label": "wldn", "machine": "chuck-herdr-alpha"}}, "hosts": {}}
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


# ------------------------------------------------------------------------------- where a kit's work runs

TIP = "5e1f0c2a" + "0" * 32
FLEET = {"partitions": {"madswan": {"label": "madswan", "machine": "deneb"}}, "hosts": {}}


def launch(n, work, base, repo="crew"):
    """A launch as a start writes it: in its repository, naming no host or stream."""
    return plan.Rec("Request", [("Request", str(n)), ("Act", "launch"), ("Work", work), ("Repo", repo), ("Base", base)])


def took(host, *ns, repository="/w/crew", stream="madswan"):
    """A host's runner as crew reads it, having taken each launch numbered ns, its place's status naming the kit's folder
    on host (repository) and its stream."""
    status = json.loads((FLUME / "code.json").read_text())
    p = status["status"]["places"][0]
    p.update(repository=repository, stream={"name": stream, "from": "intent"})
    answers = "".join(f"\nRequest: {n}\nOutcome: launched\nPlace: /p{n}\nAt: 2026-10-31T12:01:00Z\n" for n in ns)
    places = "".join(f"\nRequest: {n}\nPlace: {p['place']}\nAt: 2026-10-31T12:02:00Z\nStatus: {json.dumps(status)}\n" for n in ns)
    files = {"runner.rec": plan.Plan(runner.RUNNER + f"\nHost: {host}\nVersion: 0.1.0\nSince: 2026-10-31T11:00:00Z\n"),
             "answers.rec": plan.Plan(runner.ANSWERS + answers), "places.rec": plan.Plan(runner.PLACES + places)}
    return runner.host_read("madswan", host, TIP, files, {})


class TestWhereABoltRuns:
    BOLT = plan.Plan(flume_plan([("x", None, "flume"), ("y", None, None)])).bolt("x")
    LAUNCHES = [launch(1, "unit/a", "bolt/x"), launch(2, "unit/b", "bolt/x"), launch(3, "unit/c", "bolt/z")]

    def test_its_host_folder_and_stream_are_the_runners_that_took_its_work(self):
        """x's work taken by deneb's runner, the main level's host, which reported crew in /w/crew."""
        at = plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"deneb": took("deneb", 1, 2)}))
        assert at == {"label": "madswan", "machine": "deneb", "stream": "madswan",
                      "kit": {"name": "crew", "repo": "crew", "main": "/w/crew", "dir": "/w/crew"}}

    def test_on_another_host_it_runs_there(self):
        at = plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"alpha": took("alpha", 1, repository="/a/crew"), "deneb": took("deneb")}))
        assert (at["machine"], at["kit"]["main"]) == ("alpha", "/a/crew")

    def test_taken_by_two_runners_it_is_refused_naming_both(self):
        with pytest.raises(plan.Refusal, match="^crew can't tell where bolt x's work runs: request 2 was taken by the runners on alpha "
                                               "and deneb, whose configurations each name its repository$"):
            plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"alpha": took("alpha", 2), "deneb": took("deneb", 2)}))

    def test_taken_by_no_runner_it_is_refused_and_one_crew_cant_read_is_named(self):
        silent = runner.host_read("madswan", "alpha", TIP, {}, {"runner.rec": "recfix refused it"})
        with pytest.raises(plan.Refusal, match="^no runner has reported taking bolt x's work yet, so crew can't tell where it runs; "
                                               "alpha's runner can't be read"):
            plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"alpha": silent, "deneb": took("deneb", 3)}))

    def test_a_bolt_none_of_whose_own_work_is_taken_is_read_where_its_kits_work_runs(self):
        """x's own launches not yet taken, crew's work on bolt z taken by deneb: x is read and landed in crew's folder
        there (plan.kit_at); with no work of crew's taken at all, crew can't tell."""
        at = plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"deneb": took("deneb", 3)}))
        assert (at["machine"], at["kit"]["main"]) == ("deneb", "/w/crew")
        with pytest.raises(plan.Refusal, match="^no runner has reported taking crew's work yet"):
            plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"deneb": took("deneb")}))
        assert plan.bolt_taken(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"deneb": took("deneb", 3)})) == (None, None)

    def test_taken_with_no_place_carried_crew_cant_tell_its_folder(self):
        read = took("deneb", 1)
        read["places"] = {}
        with pytest.raises(plan.Refusal, match="^the runner on deneb took bolt x's work and has carried no place of it yet"):
            plan.bolt_at(FLEET, "madswan", self.BOLT, (self.LAUNCHES, {"deneb": read}))

    def test_a_bolt_not_started_runs_nowhere(self):
        assert plan.bolt_at(FLEET, "madswan", plan.Plan(flume_plan([("y", None, None)])).bolt("y"), ([], {})) is None

    def test_a_kits_work_is_where_its_newest_launch_taken_ran(self):
        """crew's launches on bolt x and on z, the newest taken by alpha: the kit runs there now."""
        at = plan.kit_at(FLEET, "madswan", "crew", (self.LAUNCHES, {"deneb": took("deneb", 1), "alpha": took("alpha", 3, repository="/a/crew")}))
        assert (at["machine"], at["kit"]["main"]) == ("alpha", "/a/crew")
        with pytest.raises(plan.Refusal, match="^no runner has reported taking atlas-kit's work yet"):
            plan.kit_at(FLEET, "madswan", "atlas-kit", (self.LAUNCHES, {"deneb": took("deneb", 1)}))


def test_a_partitions_hosts_are_its_main_levels_and_its_runners():
    """Decision 5: deneb, madswan's main level's, and alpha, where a runner answers for it, each once."""
    assert plan.hosts_of(FLEET, "madswan", {"madswan": ([], {"alpha": took("alpha"), "deneb": took("deneb")})}) == ["alpha", "deneb"]
    assert plan.hosts_of(FLEET, "madswan", {}) == ["deneb"]


class TestBeforeARunnerTookIt:
    """The user's ruling of 2026-11-01: a start's branch and checks, a unit name's check, a bolt never started landed,
    the design agent's records, the board's explorations and the main level's kit folders run on the partition's
    main-level host, in the checkout its spaces keep of the kit (plan.main_kit, crew.kit_kept), refused where they keep
    none; nothing is asked of a runner."""
    SPACES = {"deneb": {"sessions": {
        "madswan": {"dir": "/d/madswan", "repos": ["afterthought/blueprints", "afterthought/crew"]},
        "madswan-2": {"dir": "/d/agentplot", "repos": ["agentplot/blueprints", "agentplot/sluice", "agentplot/flume"]}}},
        "alpha": {"sessions": {"willdan": {"dir": "/a/willdan", "repos": ["afterthought/crew", "WilldanGroup/switchboard-kit"]}}}}
    FLEET = dict(FLEET, hosts=SPACES)

    def test_a_kit_is_its_main_level_hosts_checkout_by_its_name_or_its_forge_address(self):
        for kit in ("crew", "afterthought/crew"):
            assert plan.main_kit(self.FLEET, "madswan", kit) == {"label": "madswan", "machine": "deneb", "stream": None, "kit": {
                "name": "crew", "repo": "afterthought/crew", "dir": "/d/madswan/crew", "main": "/d/madswan/crew/main"}}
        assert plan.main_kit(self.FLEET, "madswan", "sluice")["kit"]["main"] == "/d/agentplot/sluice/main"

    def test_a_kit_the_host_keeps_none_of_is_none_and_said_so_where_it_is_acted_on(self):
        """A kit another host keeps, or one kept under another owner, is not the main-level host's."""
        assert plan.main_kit(self.FLEET, "madswan", "switchboard-kit") is None
        assert plan.main_kit(self.FLEET, "madswan", "agentplot/crew") is None
        assert plan.main_kit_said(self.FLEET, "madswan", "switchboard-kit", "make bolt/b") == (
            "madswan's main level runs on deneb, and no space there keeps switchboard-kit, so crew can't make bolt/b")

    def test_two_repositories_by_a_kits_name_are_refused_unless_its_owner_tells_them_apart(self):
        spaces = dict(self.SPACES, deneb={"sessions": {"x": {"dir": "/x", "repos": ["afterthought/blueprints", "agentplot/blueprints"]}}})
        fleet = dict(FLEET, hosts=spaces)
        with pytest.raises(plan.Refusal, match="^deneb's spaces keep afterthought/blueprints and agentplot/blueprints by the name "
                                               "blueprints, so crew can't tell which is meant$"):
            plan.main_kit(fleet, "madswan", "blueprints")
        assert plan.main_kit(fleet, "madswan", "agentplot/blueprints")["kit"]["repo"] == "agentplot/blueprints"
        assert plan.main_kit_read(fleet, "madswan", "blueprints") is None

    def test_the_main_levels_kit_folders_are_its_partitions_kits_its_host_keeps(self, monkeypatch):
        """crew.kits_on: the partition's kits (plan.kits_read) its host keeps, each once, as crew's cache holds the branch
        unless fetched; a kit it keeps none of is left out."""
        import crew
        asked = []
        monkeypatch.setattr(plan, "kits_read", lambda fleet, label, fresh=True: asked.append((label, fresh)) or
                            ["afterthought/crew", "crew", "flume", "switchboard-kit"])
        assert crew.kits_on(self.FLEET, "madswan", "deneb") == ["/d/madswan/crew/main", "/d/agentplot/flume/main"]
        assert crew.kits_on(self.FLEET, "madswan", "deneb", fetch=True) == ["/d/madswan/crew/main", "/d/agentplot/flume/main"]
        assert asked == [("madswan", False), ("madswan", True)]

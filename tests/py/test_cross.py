"""A team crossing to Flume, one team at a time (record 0050 parts 2 and 3, the change
teams-cross-to-flume-as-their-bolts-land): a team's path from its setting and the bolts it holds (runner.team_path,
runner.path_of). The commands that act on it, a give's refusal and a crossed team's end, are the cross journey's
(t-journey-cross)."""
import pytest

from facts import crossed_fleet, flume_plan
import plan
import runner

CREW = "crew"


def plan_with(bolts):
    """A plan whose bolts are given as (name, team or None, Path or None), in order."""
    return plan.Plan("%rec: Bolt\n%key: Bolt\n\n" + "".join(
        f"Bolt: {b}\nRepo: {CREW}\nGoal: Goal of {b}.\n" + (f"Team: {t}\n" if t else "") + (f"Path: {p}\n" if p else "") + "\n"
        for b, t, p in bolts) + "%rec: Unit\n%key: Unit\n")


def team(flume, name="crw-4"):
    return {"name": name, "flume": flume, "label": "madswan", "machine": "deneb"}


class TestPath:
    """A team's path is today's, due or crossed, from its setting and the Path of each bolt it holds (Decision 2)."""

    @pytest.mark.parametrize("setting, held, path", [
        (False, [], ("today", None)),
        (False, [None], ("today", None)),
        (False, [None, None], ("today", None)),
        ("madswan", [], ("crossed", None)),
        ("madswan", ["flume"], ("crossed", None)),
        ("madswan", ["flume", "flume"], ("crossed", None)),
        ("madswan", [None], ("due", "cross")),
        ("madswan", ["flume", None], ("due", "cross")),
        (False, ["flume"], ("due", "back")),
        (False, [None, "flume"], ("due", "back"))])
    def test_the_setting_and_each_bolt_held_give_the_path(self, setting, held, path):
        assert runner.team_path(setting, held) == path

    def test_the_setting_turned_on_while_the_team_builds_a_bolt_of_todays_path_makes_it_due_to_cross(self):
        p = plan_with([("x", "crw-4", None), ("y", None, None)])
        assert runner.path_of(p, team("madswan")) == ("due", "cross")

    def test_a_team_holding_nothing_when_its_setting_turns_on_is_crossed(self):
        assert runner.path_of(plan_with([("x", "crw-5", None)]), team("madswan")) == ("crossed", None)

    def test_turned_back_while_it_holds_a_bolt_given_through_flume_it_is_due_back(self):
        assert runner.path_of(plan_with([("y", "crw-4", "flume")]), team(False)) == ("due", "back")

    def test_only_the_teams_own_bolts_count(self):
        p = plan_with([("x", "crw-5", None), ("y", "crw-4", "flume")])
        assert runner.path_of(p, team("madswan")) == ("crossed", None)
        assert runner.path_of(p, team("madswan", "crw-5")) == ("due", "cross")


class TestDue:
    """A team due to cross is given no new bolt, and no dispatcher is told it can take one (Decision 2)."""

    def test_a_give_to_a_due_team_is_refused_naming_each_bolt_and_the_path_it_was_given_on(self):
        assert runner.due_refusal("crw-4", ("due", "cross"), [("x", None)]) == (
            "crw-4 is due to cross to Flume, so it is given no bolt now: it holds x, given on today's path, and is given its next "
            "bolt once x has landed or been dropped")

    def test_two_bolts_of_todays_path_are_both_named_and_both_finished_first(self):
        assert runner.due_refusal("crw-4", ("due", "cross"), [("x", None), ("z", None)]).endswith(
            "it holds x and z, given on today's path, and is given its next bolt once x and z have landed or been dropped")

    def test_due_back_names_the_bolts_given_through_flume_as_the_ones_it_finishes_first(self):
        assert runner.due_refusal("crw-4", ("due", "back"), [("y", "flume"), ("x", None)]) == (
            "crw-4 is due back to today's path, so it is given no bolt now: it holds y, given through Flume and x, given on "
            "today's path, and is given its next bolt once y has landed or been dropped")

    @pytest.mark.parametrize("path", [("today", None), ("crossed", None)])
    def test_a_team_that_is_not_due_is_not_refused_for_it(self, path):
        assert runner.due_refusal("crw-4", path, [("x", None)]) is None

    def test_a_proven_bolt_waiting_to_land_on_a_due_team_tells_no_dispatcher_it_is_free(self):
        p = plan_with([("x", "crw-4", None), ("next", None, None)])
        assert not plan.free_now(plan.give_due(p, team("madswan")) or plan.give_refusal("crw-4", []), "next")
        assert plan.free_now(plan.give_due(p, team(False)) or plan.give_refusal("crw-4", []), "next")

    def test_a_bolt_landed_by_a_team_the_write_leaves_due_tells_no_dispatcher(self):
        teams = {"crw-4": team("madswan"), "crw-5": team(False, "crw-5")}
        after = plan_with([("z", "crw-4", None), ("w", "crw-5", None)])
        assert plan.due_teams({"teams": teams}, after) == {"crw-4"}

        def told(freed_by):
            seen = dict(before={"x": freed_by}, after={}, touched=["x"], quiet=set(), due=plan.due_teams({"teams": teams}, after))
            return plan.notices(teams, seen, "madswan-ops", "plan(x): land the bolt (madswan-ops)")[2]
        assert not told("crw-4")
        assert told("crw-5")


class TestCrossing:
    """Once a team has crossed, its conductor and ops are due an end, and the crossing is whole once neither is up
    (Decision 3)."""

    def test_once_crossed_every_role_up_is_due_an_end_and_the_crossing_is_whole_once_none_is(self):
        assert runner.cross_due(("crossed", None), ["conductor", "ops"]) == (["conductor", "ops"], False)
        assert runner.cross_due(("crossed", None), ["ops"]) == (["ops"], False)
        assert runner.cross_due(("crossed", None), []) == ([], True)

    @pytest.mark.parametrize("path", [("today", None), ("due", "cross"), ("due", "back")])
    def test_a_team_that_has_not_crossed_owes_its_agents_nothing(self, path):
        assert runner.cross_due(path, ["conductor", "ops"]) == ([], False)
        assert runner.cross_due(path, []) == ([], False)


class TestNoStandingAgent:
    """A crossed team runs no standing agent: every standing-agent or slot command of it is refused at once, naming
    where its work runs (Decision 15)."""
    FLEET = {"teams": {}, "partitions": {"madswan": {"label": "madswan"}}}

    def test_a_crossed_teams_command_is_refused_naming_flume_its_host_its_stream_and_crew_bolts(self):
        assert runner.crossed_refusal("crw-4", ("crossed", None), "madswan", "deneb", "up crw-4") == (
            "crw-4 has crossed to Flume: its work runs in Flume places on deneb, in stream madswan, and crew bolts shows them; it "
            "runs no conductor, ops or slot, so crew up crw-4 has nothing of it to act on")

    @pytest.mark.parametrize("path", [("today", None), ("due", "cross"), ("due", "back")])
    def test_a_team_that_has_not_crossed_is_not_refused_for_it(self, path):
        assert runner.crossed_refusal("crw-4", path, "madswan", "deneb", "up crw-4") is None

    def reads(self, monkeypatch, found, errors=None):
        read = []

        def plans(fleet, labels, errs=None):
            read.append(labels)
            errs.update(errors or {})
            return [] if errors else [("madswan", "afterthought/crew-state", "a" * 40 if found else None, found)]
        monkeypatch.setattr(plan, "plans", plans)
        return read

    def test_a_team_whose_setting_is_off_is_not_refused_and_its_plan_is_not_read(self, monkeypatch):
        read = self.reads(monkeypatch, plan_with([("x", "crw-4", None)]))
        plan.not_crossed(self.FLEET, team(False), "up crw-4")
        assert read == []

    def test_a_crossed_team_is_refused_from_its_plan_and_a_due_one_is_not(self, monkeypatch):
        self.reads(monkeypatch, plan_with([("x", "crw-4", "flume")]))
        with pytest.raises(plan.Refusal, match="^crw-4 has crossed to Flume: its work runs in Flume places on deneb"):
            plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")
        self.reads(monkeypatch, plan_with([("x", "crw-4", None)]))
        plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")

    def test_a_branch_not_started_holds_no_bolt_of_the_team_so_it_has_crossed(self, monkeypatch):
        self.reads(monkeypatch, None)
        assert plan.crossing_path(self.FLEET, team("madswan")) == ("crossed", None)

    def test_a_plan_that_cannot_be_read_refuses_naming_it(self, monkeypatch):
        self.reads(monkeypatch, None, {"madswan/main of afterthought/crew-state": "timed out"})
        with pytest.raises(plan.Refusal, match="^can't tell whether crw-4 has crossed to Flume: madswan/main of "
                                               "afterthought/crew-state could not be read: timed out$"):
            plan.not_crossed(self.FLEET, team("madswan"), "up crw-4")


# ------------------------------------------------------------------------------------- a crossed team's bolt launched

FLEET = crossed_fleet()


def unit(name, bolt="x", after=(), kind="unit", sources=()):
    return (name, bolt, list(after), kind, list(sources))


@pytest.fixture(autouse=True)
def writer(monkeypatch):
    monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")


def requests(w):
    """requests.rec as the write leaves it: each request's fields but its Date and By, as {field: value or [values]}."""
    out = []
    for r in plan.Plan(w.files.get("requests.rec") or runner.REQUESTS).recs("Request"):
        d = {}
        for f, v in r.fields:
            if f not in ("Date", "By"):
                d[f] = d[f] + [v] if f == "After" and f in d else [v] if f == "After" else v
        out.append(d)
    return out


def launch(n, work, name, after=(), kind="change", bolt="x", priority="1", brief=None):
    """A launch request as a give writes it for crw-4 on deneb."""
    d = {"Request": str(n), "Act": "launch", "Host": "deneb", "Work": work, "Repo": "afterthought/crew", "Kind": kind, "Name": name,
         "Base": f"bolt/{bolt}", "Stream": "madswan", "Priority": priority, "Intent": f"madswan/{bolt}", "Recipient": "madswan/planner"}
    if after:
        d["After"] = [str(a) for a in after]
    d["Brief"] = brief or f"Build {name}."
    return d


def given(*bolts, work=(), files=None, runners=None):
    """A write over madswan's plan, each bolt given as (name, team or None, Path or None)."""
    from facts import FactsWrite
    return FactsWrite(flume_plan(bolts, work), files=files, runners=runners, label="madswan")


def give(w, bolt, team="crw-4"):
    """What a give's change function does for a crossed team once sluice made the branch: Team and Path: flume set,
    and the bolt's work launched (plan.reach_places)."""
    b = w.plan.bolt(bolt)
    b.set("Team", team)
    b.set("Path", "flume", after="Team")
    return plan.reach_places(FLEET, w, bolt, FLEET["teams"][team])


class TestGive:
    """A give to a crossed team launches its bolt whole (Decision 5): a launch per unit and chore, in the file's order,
    each after the launches of its After work, and no bound for the bolts the team holds."""

    def test_a_bolt_of_three(self):
        """crew bolt give crw-4 x, x holding units a and b, b after a, and chore c: three launches of change, change and
        chore on bolt/x, b's naming a's as its After."""
        w = given(("x", None, None), work=[unit("a", sources=["signals/s1", "README.md"]), unit("b", after=["a"]), unit("c", kind="chore")])
        assert give(w, "x") == [(1, "unit/a"), (2, "unit/b"), (3, "chore/c")]
        assert requests(w) == [launch(1, "unit/a", "a", brief="Build a. Sources: signals/s1; README.md."),
                               launch(2, "unit/b", "b", after=[1]), launch(3, "chore/c", "c", kind="chore")]
        assert (w.plan.bolt("x").get("Team"), w.plan.bolt("x").get("Path")) == ("crw-4", "flume")

    def test_a_dependent_listed_first_is_launched_after_its_after_work(self):
        w = given(("x", None, None), work=[unit("b", after=["a"]), unit("a")])
        assert give(w, "x") == [(1, "unit/a"), (2, "unit/b")]
        assert requests(w)[1]["After"] == ["1"]

    def test_a_chores_brief_is_its_words_alone(self):
        w = given(("x", None, None), work=[unit("c", kind="chore", sources=["signals/s1"])])
        give(w, "x")
        assert requests(w)[0]["Brief"] == "Build c."

    def test_a_crossed_team_takes_a_third_bolt_and_its_launches_follow_the_requests_already_written(self):
        """crw-4 holds x and y, each with work launched, and is given z: z is launched, nothing refused for x and y."""
        w = given(("x", None, None), ("y", None, None), ("z", None, None),
                  work=[unit("a"), unit("b", bolt="y"), unit("c", bolt="z")])
        give(w, "x")
        give(w, "y")
        assert give(w, "z") == [(4, "unit/c")]
        assert [r["Act"] for r in requests(w)] == ["launch", "launch", "priority", "launch", "priority", "priority"]

    def test_a_give_with_no_runner_on_the_host_is_refused_naming_it(self):
        """crw-4 is crossed on deneb and the state repository has no madswan/runner/deneb."""
        assert runner.runnerless("madswan", "deneb", {"alpha": "a" * 40}) == (
            "no runner answers on deneb: madswan/runner/deneb does not exist, so nothing would launch the bolt's work there; a "
            "give to a team crossed to Flume waits for the runner (flywheel-runner) to serve the partition there")
        assert runner.runnerless("madswan", "deneb", {"deneb": "a" * 40}) is None

    def test_what_the_give_says_names_each_launch_and_that_no_agent_starts(self):
        assert plan.launched_said(FLEET["teams"]["crw-4"], "x", [(1, "unit/a"), (2, "chore/c")]) == (
            "crw-4 has crossed to Flume, so no agent of it starts: the runner on deneb launches unit/a (request 1), chore/c "
            "(request 2) in stream madswan, and crew bolts shows their places")


def ops(w, *dos, stages=None, n=None):
    """Plan commands applied to the write as a proposal holds them, in madswan's partition (facts.apply)."""
    from facts import apply, known
    return apply(w, *dos, ctx=known(w, stages=stages, n=n, fleet=FLEET))


def launched(*bolts, work=(), runners=None):
    """A write over a plan whose bolts are each given to crw-4 through Flume, their work launched as the give launches it."""
    w = given(*[(b, None, None) for b in bolts], work=work, runners=runners)
    for b in bolts:
        give(w, b)
    return w


class TestReach:
    """A plan write reaches a crossed team's places as its own act (Decision 7): added or moved-in work launched, dropped
    work and a dropped bolt's places dropped, and a move out, a split or a change of After of launched work refused."""

    def test_a_unit_added_to_a_crossed_bolt_is_launched_after_the_launch_of_its_after_work(self):
        w = launched("x", work=[unit("a")])
        ops(w, 'unit add b "Build b." --bolt x --after a', 'chore add c "Build c." --bolt x')
        assert requests(w)[1:] == [launch(2, "unit/b", "b", after=[1]), launch(3, "chore/c", "c", kind="chore")]

    def test_work_added_to_a_bolt_of_todays_path_or_the_queue_is_not_launched(self):
        w = given(("x", "crw-5", None), work=[unit("a")])
        ops(w, 'unit add b "Build b." --bolt x', f'unit add q "Build q." --repo {CREW}')
        assert "requests.rec" not in w.files

    def test_a_unit_moved_in_from_the_queue_is_launched(self):
        w = launched("x", work=[unit("a"), unit("q", bolt=None)])
        ops(w, "unit move q x")
        assert requests(w)[1] == launch(2, "unit/q", "q")

    def test_launched_work_moved_out_is_refused_naming_its_place_and_drop_then_add(self):
        """A proposal moves a, launched on crossed crw-4's x, to bolt y."""
        w = launched("x", work=[unit("a")])
        w.plan.insert(plan.Rec("Bolt", [("Bolt", "y"), ("Repo", CREW), ("Goal", "Goal of y.")]))
        with pytest.raises(plan.Refusal, match=r"^unit a is launched as Flume place a on bolt/x \(request 1\), whose base and order are fixed "
                                               r"at its launch, so it is not moved to y: drop it \(crew unit drop a\) and add it again as it "
                                               r"should be \(crew unit add\)$"):
            ops(w, "unit move a y")

    def test_work_with_a_place_on_todays_path_does_not_move_into_a_crossed_bolt(self):
        w = given(("x", "crw-4", "flume"), ("t", "crw-5", None), work=[unit("a", bolt="t")])
        with pytest.raises(plan.Refusal, match="^unit a has a place at /kit/places/a on today's path, and bolt x is built through Flume"):
            ops(w, "unit move a x", stages={"a": "code"})

    def test_a_split_of_launched_work_is_refused(self):
        w = launched("x", work=[unit("a")])
        with pytest.raises(plan.Refusal, match=r"^unit a is launched as Flume place a .* so it is not split: drop it"):
            ops(w, 'unit split a "Half of a." --into a2 "The other half."')

    def test_a_change_of_after_of_launched_work_is_refused_and_one_that_changes_nothing_passes(self):
        def bolt():
            return launched("x", work=[unit("a"), unit("b", after=["a"]), unit("c")])
        with pytest.raises(plan.Refusal, match=r"^unit b is launched as Flume place b .* so it is not put after a, c: drop it"):
            ops(bolt(), "unit after b a c")
        with pytest.raises(plan.Refusal, match=r"so it is not put after nothing"):
            ops(bolt(), "unit after b --none")
        w = bolt()
        before = w.files["requests.rec"]
        ops(w, "unit after b a")
        assert w.files["requests.rec"] == before

    def test_a_unit_dropped_drops_its_launch_and_a_dependent_held_for_it_is_launched_again_without_it(self):
        """The user approves dropping c, launched on crossed crw-4's x."""
        w = launched("x", work=[unit("a"), unit("c"), unit("b", after=["a", "c"])])
        ops(w, 'unit drop c "Not needed."')
        assert [(r["Request"], r["Act"], r["Work"], r.get("Of"), r.get("After")) for r in requests(w)[3:]] == [
            ("4", "drop", "unit/c", "2", None), ("5", "drop", "unit/b", "3", None), ("6", "launch", "unit/b", None, ["1"])]

    def test_a_dropped_bolt_drops_every_place_it_launched_and_requeued_too(self):
        w = launched("x", work=[unit("a"), unit("c", kind="chore")])
        w.files["requests.rec"] += "\n" + "\n".join(plan.Rec("Request", runner.request_fields(
            3, "launch", "deneb", "fix/x/tidy", dict(launch(3, "fix/x/tidy", "x--tidy"), Kind="fix"), "2026-10-31T12:00:00Z", "madswan-planner")).lines()) + "\n"
        ops(w, 'bolt drop x "Not needed."')
        assert [(r["Act"], r["Work"], r.get("Of")) for r in requests(w)[3:]] == [
            ("drop", "unit/a", "1"), ("drop", "chore/c", "2"), ("drop", "fix/x/tidy", "3")]
        w = launched("x", work=[unit("a")])
        ops(w, 'bolt drop x "Later." --requeue')
        assert [(r["Act"], r.get("Of")) for r in requests(w)[1:]] == [("drop", "1")]

    def test_a_unit_added_to_a_crossed_bolt_of_a_team_turned_back_runs_on_in_the_stream_its_launches_named(self):
        w = launched("x", work=[unit("a")])
        back = dict(FLEET["teams"]["crw-4"], flume=False)
        w.plan.insert(plan.Rec("Unit", [("Unit", "b"), ("Repo", CREW), ("Bolt", "x"), ("Intent", "Build b.")]))
        plan.reach_places(FLEET, w, "x", back)
        assert requests(w)[1]["Stream"] == "madswan"

    def test_a_bolt_given_to_a_team_the_teams_file_does_not_name_is_refused(self):
        w = given(("x", "crw-9", "flume"), work=[unit("a")])
        with pytest.raises(plan.Refusal, match="^bolt x is given to crw-9, which .*teams.json does not name, so crew can't tell where its work runs$"):
            plan.reach_places(FLEET, w, "x")


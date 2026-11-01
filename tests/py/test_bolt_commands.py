"""crew bolt new|order|drop|start on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given; when a bolt lands (plan.land_refusal), started or not (plan.unheld_stages, plan.unheld_refusal,
plan.builder); and what a start checks and says around sluice's create of the bolt's branch (plan.kit_team,
plan.start_check, plan.give_check, plan.made_said, plan.started_said, plan.unstarted_said). The branch a start makes
and land removes, and the commits every write makes, are the journey's (t-journey-units and t-journey-land)."""
import base64
import pathlib

import pytest
from facts import FLEET, FactsWrite, apply, known, plan_text, units_of

import plan

KIT, BOARD = "switchboard-kit", "breadboard-kit"


def fresh():
    return FactsWrite(plan_text(bolts=[("tenant-environments", KIT, "swb-1"), ("console-pages", KIT, None), ("board-builds", BOARD, None)],
                                units=[("a-console-page", KIT, "console-pages", []), ("a-console-filter", KIT, "console-pages", ["a-console-page"]),
                                       ("lint-once", KIT, "tenant-environments", [])]))


def bolts(w):
    return [b.name() for b in w.plan.bolts()]


def run(w, *dos, stages=None):
    return apply(w, *dos, ctx=known(w, stages=stages))


def refusal(w, do, **kw):
    with pytest.raises(plan.Refusal) as e:
        run(w, do, **kw)
    return str(e.value)


class TestNew:
    def test_adds_a_bolt_last_or_before_one_named_with_its_sources(self):
        w = run(fresh(), 'bolt new apex-zones "Each apex is a zone." --repo switchboard-kit --before console-pages',
                'bolt new last-one "Last." --repo switchboard-kit --source books/x.md')
        assert bolts(w) == ["tenant-environments", "apex-zones", "console-pages", "board-builds", "last-one"]
        assert w.plan.bolt("last-one").all("Source") == ["books/x.md"]

    def test_refuses_a_name_the_plan_has(self):
        assert refusal(fresh(), 'bolt new console-pages "again" --repo switchboard-kit') == "wldn/main already has bolt console-pages"

    def test_a_kit_the_plan_does_not_name_enters_it_with_its_first_bolt(self):
        """Decision 3 of the-team-machinery-leaves: there is no registry of repositories in crew."""
        w = run(fresh(), 'bolt new rocs "x" --repo rocs-kit')
        assert w.plan.bolt("rocs").get("Repo") == "rocs-kit"


class TestOrder:
    @pytest.mark.parametrize("how, order", [
        ("--first", ["board-builds", "tenant-environments", "console-pages"]),
        ("--before console-pages", ["tenant-environments", "board-builds", "console-pages"]),
        ("--last", ["tenant-environments", "console-pages", "board-builds"])])
    def test_moves_a_bolt(self, how, order):
        assert bolts(run(fresh(), f"bolt order board-builds {how}")) == order

    def test_a_bolt_never_goes_before_itself(self):
        assert refusal(fresh(), "bolt order console-pages --before console-pages") == "a bolt can't go before itself"


class TestDrop:
    def test_removes_a_bolt_and_its_units(self):
        w = run(fresh(), 'bolt drop console-pages "folded into the portal"')
        assert bolts(w) == ["tenant-environments", "board-builds"]
        assert [u.name() for u in w.plan.units()] == ["lint-once"]

    def test_requeue_queues_its_units_without_their_after(self):
        w = run(fresh(), 'bolt drop console-pages "folded into the portal" --requeue')
        assert units_of(w, repo=KIT) == ["a-console-page", "a-console-filter"]
        assert w.plan.unit("a-console-filter").all("After") == []

RECORDED = pathlib.Path(__file__).parent / "sluice-0.36.4"
WHERE = "/kit/main/.config/sluice.toml"
POLICY = '[branches."bolt/*"]\nrequired = ["#check-full"]\nremote = "origin"\n'


def recorded(name):
    """What sluice 0.36.4 printed for a branch command, and its exit, as the folder's README lists them."""
    codes = dict(l.split("\t")[:2] for l in (RECORDED / "README").read_text().splitlines() if "\texit " in l)
    return (RECORDED / name).read_text(), int(codes[name].split()[1])


def deleted(name, policy=POLICY):
    """What BOLT_DELETE prints when sluice says what it recorded: a bolt on GitHub, or on the host for a policy naming
    no remote, its own branch at aaaaaaa."""
    out, code = recorded(name)
    return (f"LOCAL={'a' * 40}\nTRACKED={'a' * 40}\nAT_LOCAL={base64.b64encode(policy.encode()).decode()}\nAT_TRACKED=-\n"
            f"RC={code}\nSAID={base64.b64encode(out.encode()).decode()}\n")


class TestDropDeletes:
    """bolt-plan "A bolt is created, dropped and landed through crew" (plan.19, record 0003): a drop of a started bolt
    has sluice delete its branch, asked on its kit's host; what is said of it
    (plan.dropped_said). That it is marked dropped and recorded once is the journey's (t-journey-land)."""
    HOST = "chuck-herdr-alpha"
    KEPT = "it is the drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip"

    def said(self, name, policy=POLICY, again=False):
        return plan.dropped_said("b", self.HOST, 0, deleted(name, policy), "", again)

    def test_a_dropped_bolt_whose_tip_main_holds_is_deleted_from_github(self):
        """bolt-plan "Dropping a bolt in flight"."""
        assert self.said("delete.json") == "sluice deleted bolt/b from GitHub at 22eef85"

    def test_a_dropped_bolt_made_before_is_deleted_from_its_host(self):
        assert self.said("delete.json", '[branches."bolt/*"]\nrequired = ["#check-full"]\n') == (
            "sluice deleted bolt/b from chuck-herdr-alpha at 22eef85")

    def test_a_branch_already_gone_refuses_nothing(self):
        assert self.said("delete-not-found.json") == "bolt/b is gone already: no branch bolt/b"

    def test_a_dropped_bolt_holding_work_main_lacks_is_kept_and_named_as_the_users(self):
        """bolt-plan "A dropped bolt holds work main lacks"."""
        assert self.said("delete-not-landed.json") == (
            "bolt/b is kept on GitHub at aaaaaaa: bolt b was dropped, and sluice did not delete it: bolt/b at "
            f"22eef8585855b2ef8feb0e08177e34d15f131182 has not landed into main; submit it there first; {self.KEPT}")
        assert self.said("delete-not-landed.json", '[branches."bolt/*"]\nrequired = ["#check-full"]\n').startswith(
            "bolt/b is kept on chuck-herdr-alpha at aaaaaaa: bolt b was dropped")

    def test_one_with_a_submission_queued_is_kept_in_sluices_words(self):
        assert self.said("delete-queued.json") == (
            "bolt/b is kept on GitHub at aaaaaaa: bolt b was dropped, and sluice did not delete it: #1 still queued on "
            f"bolt/b; wait for them to land, or withdraw them; {self.KEPT}")

    def test_a_host_that_does_not_answer_names_the_command_for_the_next_read(self):
        """bolt-plan "The drop's host does not answer"."""
        assert plan.dropped_said("b", self.HOST, 255, "", "ssh: connect to host") == (
            "chuck-herdr-alpha did not answer, so sluice was not asked to delete bolt/b: sluice branch delete bolt/b "
            "--into main there; the kit's next read asks it")

    def test_words_crew_cannot_read_leave_it_to_the_next_read(self):
        """read.2: what is not sluice's document decides nothing."""
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").startswith(
            "bolt/b may still stand on GitHub: crew can't read what sluice's branch delete said from:")
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").endswith(
            "; the kit's next read asks sluice again")

    def test_asked_again_once_main_holds_its_tip(self):
        """bolt-plan "Main comes to hold a dropped bolt's work"."""
        assert self.said("delete.json", again=True) == (
            "bolt/b is removed: main now holds bolt b's tip, and sluice deleted it from GitHub at 22eef85")
        assert self.said("delete-queued.json", again=True) == (
            "bolt/b is still kept: #1 still queued on bolt/b; wait for them to land, or withdraw them")


def kitted(**flume):
    """wldn's fleet (facts.FLEET) with each team's kit checked out on its host, each team in the stream given (flume,
    {team: stream or False}), else in wldn's."""
    teams = {n: dict(t, flume=flume.get(n, t["flume"]), kit=dict(t["kit"], main=f"/w/{t['kit']['name']}/main", dir=f"/w/{t['kit']['name']}"))
             for n, t in FLEET["teams"].items()}
    return dict(FLEET, teams=teams)


class TestStart:
    """bolt-plan "A bolt's work starts by crew bolt start" (Decision 14 of the-team-machinery-leaves; plan.19): the start
    makes the bolt's branch on the host of a team building its kit (plan.building_team) until where crew acts on a kit no
    runner has reported is ruled, and is refused, with the plan unchanged and no branch made, for a bolt started already,
    a kit no team builds, a held host, or a partition no runner answers for (plan.start_check), before the kit's policy
    and sluice are read. Its launches are the
    cross tests' (test_cross.py); its commit and branch the cross journey's (t-journey-cross)."""
    HOST = "chuck-herdr-alpha"

    @pytest.fixture
    def reads(self, monkeypatch):
        """What start_check reads, each answered as the case sets it (self.held, self.tips, self.policy), every read
        recorded in order."""
        import crew
        self.read, self.held, self.tips = [], None, {self.HOST: "a" * 40}
        self.policy = (POLICY, "origin/main", "c" * 40, "sluice 0.36.4")
        monkeypatch.setattr(crew, "held_on", lambda fleet, host: self.read.append(("hold", host)) or self.held)
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("WilldanGroup/crew-state", f"{label}/main"))
        monkeypatch.setattr(plan, "runner_tips", lambda repo, label: self.read.append(("runners", repo, label)) or self.tips)
        monkeypatch.setattr(plan, "kit_policy", lambda fleet, t: self.read.append(("policy", t["kit"]["main"])) or self.policy)

    def checked(self, fleet=None):
        fleet = fleet or kitted()
        return plan.start_check(fleet, "wldn", plan.building_team(fleet, "wldn", KIT), "b")

    def test_a_bolts_branch_is_made_on_the_host_of_a_team_building_its_kit(self):
        assert [(t["name"], t["machine"], t["kit"]["name"]) for t in (plan.building_team(kitted(), "wldn", k) for k in (KIT, BOARD))] == [
            ("swb-1", self.HOST, KIT), ("swb-2", self.HOST, BOARD)]

    def test_a_bolt_started_already_is_refused(self):
        assert refusal(fresh(), "bolt start tenant-environments") == "bolt tenant-environments is started already"

    def test_a_kit_no_team_builds_is_refused_naming_it(self):
        w = fresh()
        fleet = kitted()
        fleet = dict(fleet, teams={n: t for n, t in fleet["teams"].items() if n != "swb-1"})
        with pytest.raises(plan.Refusal) as e:
            apply(w, "bolt start console-pages", ctx=known(w, fleet=fleet))
        assert str(e.value) == f"no team of wldn builds {KIT}, so crew has no host to make bolt/console-pages on"
        assert not plan.started(w.plan.bolt("console-pages"))

    def test_a_held_host_is_refused_before_anything_else_is_read(self, reads):
        self.held = {"by": "chuck", "why": "upgrading herdr", "at": "2026-10-31T10:00:00Z"}
        with pytest.raises(plan.Refusal) as e:
            self.checked()
        assert str(e.value) == (f"{self.HOST} is held by chuck since 2026-10-31T10:00:00Z: upgrading herdr. crew starts no agent there "
                                f"until crew go {self.HOST}")
        assert self.read == [("hold", self.HOST)]

    def test_a_partition_no_runner_answers_for_is_refused_before_the_kit_is_read(self, reads):
        self.tips = {}
        with pytest.raises(plan.Refusal) as e:
            self.checked()
        assert str(e.value).startswith("no runner answers for wldn: its state repository holds no wldn/runner/<host>, so nothing "
                                       "would take the bolt's work")
        assert self.read == [("hold", self.HOST), ("runners", "WilldanGroup/crew-state", "wldn")]

    def test_a_free_host_with_its_runner_answering_has_the_kits_policy_and_sluice_checked(self, reads):
        assert self.checked() == "origin"
        assert self.read[-1] == ("policy", f"/w/{KIT}/main")
        self.policy = ('[branches."bolt/*"]\nrequired = ["#check-full"]\n', "origin/main", "c" * 40, "sluice 0.36.4")
        with pytest.raises(plan.Refusal, match=f"^{KIT} starts bolts only on GitHub"):
            self.checked()


class TestStartThroughSluice:
    """bolt-plan "A bolt's work starts by crew bolt start" (plan.19): what a start checks of the kit before sluice makes
    the branch, every refusal coming before the plan write, so the plan is unchanged and no branch made; what sluice's
    create says; and a write refused after it, which has sluice delete the branch again."""

    def check(self, text=POLICY, version="sluice 0.36.4 "):
        return plan.give_check(KIT, WHERE, "origin/main", text, "b", version, "chuck-herdr-alpha")

    def test_a_kit_on_github_with_a_sluice_that_makes_branches_starts_on_its_remote(self):
        assert self.check() == "origin"

    def test_a_kit_whose_bolts_have_no_remote_is_refused_naming_the_file_and_the_key(self):
        with pytest.raises(plan.Refusal) as e:
            self.check('[branches."bolt/*"]\nrequired = ["#check-full"]\n')
        assert str(e.value).startswith(f"{KIT} starts bolts only on GitHub, and its {WHERE} on origin/main names no remote")

    def test_a_kit_with_no_bolt_checks_is_refused_first(self):
        with pytest.raises(plan.Refusal, match="names no checks for its bolt branches"):
            self.check('[branches."bolt/*"]\nremote = "origin"\n')

    @pytest.mark.parametrize("version, said", [("sluice 0.18.0 ", "sluice 0.18.0"), ("", "nothing")])
    def test_a_host_whose_sluice_is_older_or_unread_is_refused(self, version, said):
        with pytest.raises(plan.Refusal) as e:
            self.check(version=version)
        assert str(e.value) == ("a bolt is started through sluice 0.20.0 or later, which has `branch create`, and sluice "
                                f"--version on chuck-herdr-alpha said: {said}")

    MADE = "c0da39bae0a5d89da0febc3f46f58607c2ad08a7"
    OWN = "22eef8585855b2ef8feb0e08177e34d15f131182"
    PRESENT = f"sluice did not make bolt/b for {KIT} on chuck-herdr-alpha: bolt/b is already there, at {MADE}"

    def made(self, name="create-present.json", **found):
        return plan.made_said("b", KIT, "chuck-herdr-alpha", *recorded(name), found and {"read": None, **found}, "origin")

    def refused(self, **found):
        with pytest.raises(plan.Refusal) as e:
            self.made(**found)
        return str(e.value)

    def test_sluices_create_is_the_commit_it_made_the_branch_at(self):
        assert self.made("create.json") == (self.MADE, False)

    def test_a_create_sluice_refuses_is_refused_in_its_words(self):
        assert self.refused() == self.PRESENT

    @pytest.mark.parametrize("own", [MADE, None])
    def test_a_branch_a_start_left_at_mains_tip_with_no_commit_of_its_own_is_taken_and_the_start_goes_on(self, own):
        """A start that failed after sluice made the branch leaves it on GitHub at main's tip, and the host's own copy
        there too or none: the start run again takes it rather than refuse it as already there."""
        assert self.made(own=own, there=self.MADE, main=self.MADE) == (self.MADE, True)

    def test_a_branch_with_commits_of_its_own_is_still_refused_by_name(self):
        assert self.refused(own=self.OWN, there=self.OWN, main=self.MADE) == (
            f"{self.PRESENT}; bolt/b on origin is at 22eef85 and origin's main at c0da39b, so it is no branch a start left "
            "empty at main, and crew starts no bolt onto it")

    def test_a_branch_whose_hosts_copy_stands_elsewhere_is_refused_by_name(self):
        assert self.refused(own=self.OWN, there=self.MADE, main=self.MADE) == (
            f"{self.PRESENT}; chuck-herdr-alpha's own bolt/b is at 22eef85, not at origin's c0da39b, and crew starts no "
            "bolt onto it")
        assert self.refused(own=self.OWN, there=None, main=self.MADE) == (
            f"{self.PRESENT}; chuck-herdr-alpha's own bolt/b is at 22eef85 and origin has none, and crew starts no bolt "
            "onto it")

    def test_a_branch_crew_cannot_read_on_its_remote_is_refused_with_gits_words(self):
        assert self.refused(read="fatal: could not read from remote repository") == (
            f"{self.PRESENT}; and crew could not read bolt/b on origin: fatal: could not read from remote repository")

    def test_a_refusal_that_finds_no_branch_is_sluices_words_alone(self):
        assert self.refused(own=None, there=None, main=self.MADE) == self.PRESENT

    def test_a_start_names_github_the_commit_and_the_kits_host(self):
        assert plan.started_said("b", KIT, "origin", self.MADE, "chuck-herdr-alpha") == (
            f"b is started: sluice made bolt/b on GitHub (origin) from {KIT}'s main at c0da39b, built on chuck-herdr-alpha "
            "and merged into only through sluice")

    def test_a_start_that_took_the_branch_says_so(self):
        assert plan.started_said("b", KIT, "origin", self.MADE, "chuck-herdr-alpha", adopted=True) == (
            "b is started: crew took bolt/b, which sluice made on GitHub (origin) for a start that did not finish, at "
            f"{KIT}'s main c0da39b, built on chuck-herdr-alpha and merged into only through sluice")

    def test_a_write_refused_after_the_create_has_sluice_delete_the_branch_again(self):
        assert plan.unstarted_said("b", deleted("delete.json"), 0) == "sluice deleted bolt/b again, so nothing of the start is left"

    def test_a_delete_sluice_refuses_then_names_the_branch_left_standing(self):
        assert plan.unstarted_said("b", deleted("delete-queued.json"), 0) == (
            "bolt/b, which sluice made for the start, still stands, since sluice did not delete it: #1 still queued on "
            "bolt/b; wait for them to land, or withdraw them")
        assert plan.unstarted_said("b", "", 255).endswith("since sluice did not delete it: its delete exited 255: nothing was said")


class TestLand:
    def land(self, stages, outside=(), of=None):
        return plan.land_refusal("console-pages", ["a-console-page", "a-console-filter"],
                                 of or (lambda u: {"stage": stages[u], "why": "its host did not answer"}), list(outside), "wldn")

    def test_lands_once_every_unit_has_landed_and_been_in_a_batch(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "landed"}) is None

    def test_a_unit_not_landed_on_main_refuses_it(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "merged"}) == "unit a-console-filter has not landed on main: it is merged"
        assert self.land({"a-console-page": "unknown", "a-console-filter": "landed"}) == (
            "cannot tell whether unit a-console-page has landed: its host did not answer")

    def test_the_landing_records_the_commit_main_holds_now(self):
        """plan.14, plan.18: the landing records the commit GitHub's main holds after the command's fetch, for a kit with
        an origin, and nothing is refused for the host's own main lagging it (plan.8); what can't be read refuses."""
        github, own = "c" * 40, "d" * 40
        assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", f"ORIGIN=yes\nFETCHED=ok\nGITHUB={github}\nOWN={own}\n") == (github, None)
        for said in (f"{github} 0 1\n", "", "fatal: bad\n"):
            assert plan.main_held("switchboard-kit", "chuck-herdr-alpha", said) == (
                None, f"crew can't read what switchboard-kit's main on chuck-herdr-alpha holds: {said.strip() or 'nothing was said'}")

    def test_a_bolt_no_team_holds_lands_once_each_units_change_is_on_its_kits_main(self):
        planned = lambda u: {"stage": "ready"}
        of = plan.unheld_stages({"main": ["a-console-page", "a-console-filter"]}, None, planned)
        assert self.land({}, of=of) is None
        of = plan.unheld_stages({"main": ["a-console-page"]}, None, planned)
        assert self.land({}, of=of) == "unit a-console-filter has not landed on main: it is ready"
        of = plan.unheld_stages({"main": ["a-console-page", "a-console-filter"], "chores": []}, None, planned, ["a-console-filter"])
        assert self.land({}, of=of) == "chore a-console-filter has not landed on main: it is ready"
        of = plan.unheld_stages({"main": ["a-console-page"], "chores": ["a-console-filter"]}, None, planned, ["a-console-filter"])
        assert self.land({}, of=of) is None
        of = plan.unheld_stages(None, "chuck-herdr-alpha did not answer", planned)
        assert self.land({}, of=of) == "cannot tell whether unit a-console-page has landed: chuck-herdr-alpha did not answer"

    def test_a_bolt_no_team_holds_is_read_where_a_team_of_the_partition_builds_its_kit(self):
        swb, brd = {"name": "swb-2", "kit": {"name": KIT}}, {"name": "brd-1", "kit": {"name": BOARD}}
        fleet = {"partitions": {"wldn": {"teams": ["swb-2", "brd-1"]}}, "teams": {"swb-2": swb, "brd-1": brd}}
        assert plan.builder(fleet, "wldn", BOARD) is brd and plan.builder(fleet, "wldn", "rocs-kit") is None
        assert plan.unheld_refusal("console-pages", ["a-console-page"], KIT, swb, "wldn") is None
        assert plan.unheld_refusal("console-pages", ["a-console-page"], "rocs-kit", None, "wldn") == (
            "bolt console-pages is held by no team, and no team of wldn builds rocs-kit, so crew can't read its main")
        assert plan.unheld_refusal("console-pages", [], KIT, swb, "wldn") == (
            "bolt console-pages is held by no team and holds no units or chores, so nothing of it has landed")

    def test_a_change_no_batch_has_held_refuses_it(self):
        assert self.land({"a-console-page": "landed", "a-console-filter": "landed"}, ["a-console-page", "a-console-filter"]) == (
            "bolt console-pages lands only once every unit's latest change has been in a batch, and a-console-page or "
            "a-console-filter have not: a batch is due for them (crew review wldn)")


class TestWhereABoltIsRead:
    """bolt-plan "A bolt on GitHub is read where it lives" (plan.19, design Decision 1): GitHub's copy when the host holds
    it and the policy in it names a remote for the bolt, else the host's own branch, the only copy the host then has."""

    def test_githubs_copy_naming_a_remote_is_where_the_bolt_is_read(self):
        assert plan.gather.bolt_at("b", True, True, "origin") == "refs/remotes/origin/bolt/b"
        assert plan.gather.bolt_at("b", True, False, "origin") == "refs/remotes/origin/bolt/b"

    def test_a_bolt_kept_on_its_host_is_read_at_the_hosts_branch(self):
        """bolt-plan "A bolt kept on its host"."""
        assert plan.gather.bolt_at("b", True, True, None) == "refs/heads/bolt/b"

    def test_a_bolt_whose_github_copy_the_host_has_not_got_is_read_at_the_hosts(self):
        """bolt-plan "A bolt GitHub's copy of which this host has not got"."""
        assert plan.gather.bolt_at("b", False, True, None) == "refs/heads/bolt/b"
        assert plan.gather.bolt_at("b", False, False, None) is None
        assert plan.gather.bolt_at("b", True, False, None) is None

    def test_the_remote_a_policy_names_for_a_bolt(self):
        assert plan.gather.policy_remote(POLICY, "bolt/b") == "origin"
        specific = '[branches."*"]\nremote = "origin"\n[branches."bolt/*"]\nrequired = ["#check-full"]\n'
        assert plan.gather.policy_remote(specific, "bolt/b") is None
        assert plan.gather.policy_remote('[branches."main"]\nremote = "origin"\n', "bolt/b") is None
        assert plan.gather.policy_remote(None, "bolt/b") is None
        assert plan.gather.policy_remote("", "bolt/b") is None

    def test_a_policy_that_is_not_toml_raises(self):
        with pytest.raises(ValueError):
            plan.gather.policy_remote("[branches\n", "bolt/b")

    def test_kit_matches_branches_as_gather_does(self):
        assert plan.kit.branch_table is plan.gather.branch_table

    def test_a_started_bolt_whose_policy_crew_cant_read_is_unknown(self, monkeypatch):
        """bolt-plan "A policy crew can't read": nothing is read from the host's bolt/b in its place, so the bolt's state is
        unknown; its pieces read their stages from the runner's records, landed once main holds them."""
        from facts import crew_read, crossed_fleet_read, launched, ran
        monkeypatch.setenv("CREW_AGENT", "madswan-planner")
        why = ".config/sluice.toml at origin/bolt/b is not TOML, so crew can't read bolt b: Expected ']'"
        fleet = crossed_fleet_read()
        p, requests = launched(["b"], work=[("a", "b", [], "unit", []), ("done", "b", [], "unit", [])], fleet=fleet)
        unread = {"exists": False, "head": None, "head_at": None, "verdict": None, "error": why}
        st = plan.Stages(fleet, p, crew_read(main=["done"], bolts={"b": unread}), runs={"madswan": (requests, ran({1: "code", 2: "landed"}))},
                         label="madswan")
        assert (st.of("a")["stage"], st.of("a")["worktree"]) == ("code", None)
        assert st.of("done")["stage"] == "landed"
        assert st.bolt_state(p.bolt("b")) == "unknown"


class TestWhenABoltIsFetched:
    """bolt-plan "A bolt on GitHub is fetched where a decision rests on it" (plan.18, plan.19, design Decision 3): crew
    bolts asks each kit's GitHub fetched first; every other read fetches nothing. b is started, its work running on box,
    where the runner that took it reported the kit in /kit/main (plan.bolt_at)."""
    FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio", "teams": ["swb-1"]}},
             "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": "box", "flume": "wldn",
                                 "kit": {"main": "/kit/main", "dir": "/kit", "name": KIT}}}}
    KIT_READ = {"ok": True, "main": [], "chores": [], "places": {}, "chore_places": {}, "fixes": [],
                "bolts": {"b": {"exists": True, "at": "origin/bolt/b", "changes": [], "archived": [], "open": {}, "chores": [],
                                "head": "d" * 40, "head_at": "2026-10-23T09:00:00Z", "verdict": ""}}}

    WHERE = {"label": "wldn", "machine": "box", "stream": "wldn", "kit": {"main": "/kit/main", "dir": "/kit/main", "name": KIT, "repo": KIT}}

    def asked(self, monkeypatch, kept=None):
        asks = []
        monkeypatch.setattr(plan, "READ", plan.Reading())
        monkeypatch.setattr(plan, "runner_facts", lambda fleet, label: ([], {}))
        monkeypatch.setattr(plan, "rail_runs", lambda found: {"wldn": ([], {})})
        monkeypatch.setattr(plan, "bolt_at", lambda fleet, label, b, run=None: self.WHERE if plan.started(b) else None)
        if kept:
            plan.READ.keep_kits("box", kept)

        def gathered(fleet, host, req):
            asks.append(req)
            return {k["main"]: self.KIT_READ for k in req["kits"]}, None
        monkeypatch.setattr(plan, "gathered", gathered)
        return asks

    def plan(self):
        return plan.Plan(plan_text(bolts=[("b", KIT, "swb-1")], units=[("a", KIT, "b", [])]))

    def test_crew_bolts_asks_each_kit_fetched(self, monkeypatch):
        """bolt-plan "crew bolts after a landing elsewhere"."""
        import argparse
        asks = self.asked(monkeypatch)
        p = self.plan()
        monkeypatch.setattr(plan, "plans", lambda fleet, labels, errors: [("wldn", "o/state", "f" * 40, p)])
        with pytest.raises(SystemExit) as e:
            plan.bolts_view(self.FLEET, argparse.Namespace(label="wldn", bolt=None, json=True))
        assert e.value.code == 0
        assert [a.get("fetch") for a in asks] == [True]

    def test_a_read_on_every_team_read_fetches_nothing(self, monkeypatch):
        """bolt-plan "The board does not fetch"."""
        asks = self.asked(monkeypatch)
        plan.stages_for(self.FLEET, "wldn", self.plan(), self.plan().bolts())
        assert [("fetch" in a) for a in asks] == [False]

    def test_a_fetching_survey_is_asked_though_the_command_has_read_the_kit(self, monkeypatch):
        asks = self.asked(monkeypatch, kept={"/kit/main": self.KIT_READ})
        plan.stages_for(self.FLEET, "wldn", self.plan(), self.plan().bolts())
        assert asks == []
        st = plan.stages_for(self.FLEET, "wldn", self.plan(), self.plan().bolts(), fetch=True)
        assert [a.get("fetch") for a in asks] == [True]
        assert st.kit(self.plan().bolt("b"))[0]["bolts"]["b"]["at"] == "origin/bolt/b"

    def test_a_fetch_that_fails_reads_the_kit_unknown_with_gits_words(self, monkeypatch):
        """bolt-plan "A fetch that fails"."""
        self.asked(monkeypatch)
        why = "cannot fetch /kit/main from GitHub: fatal: unable to access 'https://github.com/o/k/': Could not resolve host"
        monkeypatch.setattr(plan, "gathered", lambda fleet, host, req: ({"/kit/main": {"ok": False, "error": why}}, None))
        st = plan.stages_for(self.FLEET, "wldn", self.plan(), self.plan().bolts(), fetch=True)
        assert st.kit(self.plan().bolt("b")) == (None, f"box: {why}")
        assert st.bolt_state(self.plan().bolt("b")) == "unknown"


class TestCrewBoltsCrossed:
    """crew bolts, text and JSON, reads a piece's stage from the runner's records and says the host and stream it runs
    in as that runner reported (Decisions 8 and 14 of teams-cross-to-flume-as-their-bolts-land; bolt-plan "A started
    bolt's work reads its stage from the runner's records"; the user's ruling of 2026-11-01): x is started, its work taken
    by deneb's runner in stream madswan, its a in code and b after a held; y is planned, not started."""

    @pytest.fixture(autouse=True)
    def writer(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "madswan-dispatch-deneb")

    def data(self, runners, bolt=None):
        from facts import crew_read, crossed_fleet_read, launched
        fleet = crossed_fleet_read(**{"crw-5": "madswan"})
        p, requests = launched(["x"], work=[("a", "x", [], "unit", []), ("b", "x", ["a"], "unit", []), ("y1", "y", [], "unit", [])],
                               fleet=fleet, held=[("y", "crw-5")])
        return plan.bolts_data(fleet, ["madswan"], [("madswan", "afterthought/crew-state", "abcdef1" + "0" * 33, p)],
                               crew_read(bolts={"x": {}, "y": {}}), {}, bolt, runs={"madswan": (requests, runners)})

    def bolts(self, d):
        return {b["bolt"]: b for b in d["partitions"][0]["plans"][0]["bolts"]}

    def test_a_bolts_json_gives_its_host_and_stream_and_each_pieces_runner_stage(self):
        from facts import ran
        x = self.bolts(self.data(ran({1: "code"}, held=[2])))["x"]
        assert (x["given"], x["host"], x["stream"]) == ("flume", "deneb", "madswan")
        assert [(u["unit"], u["stage"], u["tasks"], u["worktree"]) for u in x["units"]] == [("a", "code", (6, 26), None),
                                                                                           ("b", "waiting", None, None)]
        assert x["units"][1]["flume"] == {"stage": "waiting", "after": ["unit/a"]}

    def test_the_text_names_a_crossed_teams_stream_and_each_pieces_stage_and_place(self):
        """bolt-plan "A unit in code" and "A dependent waits"."""
        from facts import ran
        out = plan.bolts_text(self.data(ran({1: "code"}, held=[2]))).splitlines()
        assert "x  crew  @ deneb, in Flume stream madswan  active" in out
        assert f"  {'a':<40} {'code 6/26':<12} flume/change--teams-cross-to-flume-as-their-bolts-land" in out
        assert f"  {'b':<40} {'waiting':<12}   on a" in out

    def test_a_runner_crew_cant_read_is_named_and_its_work_reads_unknown(self):
        """bolt-plan "The runner's host is silent": deneb's runner can't be read, and then no runner answers at all."""
        import runner
        why = "deneb's runner can't be read: madswan/runner/deneb at 5e1f0c2: recfix refused it"
        d = self.data({"deneb": runner.host_read("madswan", "deneb", "5e1f0c2a" + "0" * 32, {}, {"runner.rec": "recfix refused it"})})
        assert {u["stage"] for u in self.bolts(d)["x"]["units"]} == {"unknown"}
        assert d["runners_unread"] == {"deneb's runner": why}
        assert plan.bolts_text(d).splitlines()[-1] == (
            f"deneb's runner can't be read ({why}): the stages of the work crossed to Flume there are unknown")
        none = "no runner answers for madswan: its state repository holds no madswan/runner/<host>"
        assert self.data({})["runners_unread"] == {"madswan's runners": none}

    def test_a_question_and_sluices_words_are_on_the_pieces_line(self):
        """bolt-plan "A construct that asked" and "Sent back by sluice"."""
        from facts import ran
        out = plan.bolts_text(self.data(ran({1: "stopped-short", 2: "sent-back"})))
        assert f"  {'a':<40} {'needs':<12} flume/change--agent-mode-is-a-layered-setting  asks at code: Head 118ec46 is ready" in out
        assert "code 26/26   flume/change--teams-cross-to-flume-as-their-bolts-land  sent back by sluice: check-full failed" in out

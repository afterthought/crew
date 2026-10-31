"""crew bolt new|order|drop on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given; which bolt a give hands a team (plan.to_give) and when a team may take one (plan.give_refusal), and when a bolt lands (plan.land_refusal),
held by a team or by none (plan.unheld_stages, plan.unheld_refusal, plan.builder); and what a give checks and says
around sluice's create of the bolt's branch (plan.give_check, plan.made_said, plan.given_said, plan.ungiven_said).
The branch and worktree give makes and land removes, and the commits every write makes, are the journey's
(t-journey-units and t-journey-land)."""
import base64
import pathlib

import pytest
from facts import FactsWrite, apply, known, plan_text, units_of

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

    def test_refuses_a_name_the_plan_has_and_a_kit_no_team_builds(self):
        assert refusal(fresh(), 'bolt new console-pages "again" --repo switchboard-kit') == "wldn/main already has bolt console-pages"
        assert refusal(fresh(), 'bolt new rocs "x" --repo rocs-kit') == "no team of wldn builds rocs-kit, so no plan holds its work"


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

    def test_requeue_is_refused_while_a_unit_of_a_held_bolt_has_a_worktree(self):
        assert refusal(fresh(), 'bolt drop tenant-environments "x" --requeue', stages={"lint-once": "construct"}) == (
            "unit lint-once has a worktree at /kit/places/lint-once, and a queued unit has none")

    def test_requeue_is_refused_while_a_units_stage_cannot_be_told(self):
        assert refusal(fresh(), 'bolt drop tenant-environments "x" --requeue', stages={"lint-once": "unknown"}) == (
            "cannot tell unit lint-once's stage: its host did not answer")


class TestGive:
    def test_the_team_gets_its_kits_first_bolt_no_team_holds_or_the_one_named(self):
        p = fresh().plan
        assert plan.to_give(p, None, "swb-2", [KIT], "wldn").name() == "console-pages"
        assert plan.to_give(p, p.bolt("board-builds"), "brd-1", [BOARD], "wldn").name() == "board-builds"

    def test_a_team_holding_two_kits_takes_a_bolt_of_either_the_first_free_in_the_plans_order(self):
        """A team holds its kits (record 0035): slc-1 and flm-1 both hold agentplot/weir."""
        p = fresh().plan
        first = next(b.name() for b in p.bolts() if b.get("Repo") in (KIT, BOARD) and not b.get("Team"))
        assert plan.to_give(p, None, "swb-2", [KIT, BOARD], "wldn").name() == first
        assert plan.to_give(p, p.bolt("board-builds"), "swb-2", [KIT, BOARD], "wldn").name() == "board-builds"

    @pytest.mark.parametrize("bolt, team, said", [
        ("board-builds", "swb-2", "bolt board-builds is in breadboard-kit, and swb-2 builds switchboard-kit"),
        ("tenant-environments", "swb-2", "bolt tenant-environments is held by swb-1")])
    def test_a_bolt_of_another_kit_or_held_is_refused(self, bolt, team, said):
        p = fresh().plan
        with pytest.raises(plan.Refusal, match=said):
            plan.to_give(p, p.bolt(bolt), team, [KIT], "wldn")

    def test_with_none_free_it_says_so(self):
        with pytest.raises(plan.Refusal, match="wldn/main has no planned bolt in rocs-kit for rcs-1"):
            plan.to_give(fresh().plan, None, "rcs-1", ["rocs-kit"], "wldn")


class TestGiveRefusal:
    """A team builds one bolt and holds at most one more, proven and waiting to land (teams.16): a give is refused only
    while a bolt it holds is not proven, or it holds two (plan.give_refusal)."""
    GREEN = "passed (3 run, 1 replayed)"
    HEAD = "abc1234def5678"

    def held(self, *stages, name="tenant-environments", verdict=GREEN, unread=None, kind="unit"):
        return (name, [(f"u{i}", kind, s) for i, s in enumerate(stages)], self.HEAD, verdict, unread)

    def test_a_team_holding_no_bolt_is_given_one(self):
        assert plan.give_refusal("swb-1", []) is None

    def test_a_unit_not_merged_refuses_naming_it_and_its_stage(self):
        assert plan.give_refusal("swb-1", [self.held("merged", "code")]) == "bolt tenant-environments's unit u1 has not merged (code)"

    def test_a_chore_not_merged_and_a_stage_crew_cannot_tell_refuse_too(self):
        assert plan.give_refusal("swb-1", [self.held("verify", kind="chore")]) == "bolt tenant-environments's chore u0 has not merged (verify)"
        assert plan.give_refusal("swb-1", [self.held("unknown")]) == "bolt tenant-environments's unit u0 has not merged (unknown)"

    def test_every_unit_merged_and_the_verdict_passed_is_proven(self):
        assert plan.give_refusal("swb-1", [self.held("merged", "merged")]) is None

    def test_merged_with_a_head_that_is_no_landing_of_sluices_refuses_with_the_verifications_words(self):
        assert plan.give_refusal("swb-1", [self.held("merged", verdict="")]) == (
            "bolt tenant-environments's verification is not green: its head abc1234 is no landing of sluice's, so it has no verdict")

    def test_merged_and_green_with_a_fix_in_flight_is_proven_since_fixes_are_no_input(self):
        """A carrying fix is what the proven bolt keeps of the team, so it refuses nothing (teams.16)."""
        assert plan.give_refusal("swb-1", [self.held("merged", "landed")]) is None

    def test_every_unit_landed_is_proven_whatever_its_head(self):
        assert plan.give_refusal("swb-1", [self.held("landed", "landed", verdict="")]) is None

    def test_a_bolt_with_no_units_refuses(self):
        assert plan.give_refusal("swb-1", [self.held()]) == "bolt tenant-environments holds no units or chores yet"

    def test_a_kit_not_read_refuses_with_why(self):
        assert plan.give_refusal("swb-1", [self.held("merged", unread="sb-1 did not answer")]) == (
            "can't tell whether bolt tenant-environments is proven: sb-1 did not answer")

    def test_two_bolts_held_refuses_naming_the_older_whose_landing_frees_the_team(self):
        held = [self.held("merged", name="doctor-rows"), self.held("merged", name="ssh-fix")]
        assert plan.give_refusal("swc-1", held) == "swc-1 holds doctor-rows and ssh-fix; doctor-rows waits to land, and its landing frees swc-1"


class TestGiveDue:
    """A team due to cross to Flume or back is given no bolt until those of its old path have landed or been dropped
    (plan.give_due; Decision 2 of teams-cross-to-flume-as-their-bolts-land)."""

    def test_a_team_whose_setting_names_a_stream_while_it_holds_a_bolt_of_todays_path_is_refused(self):
        assert plan.give_due(fresh().plan, {"name": "swb-1", "flume": "wldn"}) == (
            "swb-1 is due to cross to Flume, so it is given no bolt now: it holds tenant-environments, given on today's path, "
            "and is given its next bolt once tenant-environments has landed or been dropped")

    def test_a_team_on_todays_path_or_crossed_holding_nothing_is_not(self):
        assert plan.give_due(fresh().plan, {"name": "swb-1", "flume": False}) is None
        assert plan.give_due(fresh().plan, {"name": "swb-2", "flume": "wldn"}) is None

    def test_a_bolt_given_through_flume_to_a_team_turned_back_holds_it_due_back(self):
        text = plan_text(bolts=[("tenant-environments", KIT, "swb-1")]).replace("Team: swb-1\n", "Team: swb-1\nPath: flume\n")
        assert plan.give_due(plan.Plan(text), {"name": "swb-1", "flume": "wldn"}) is None
        assert plan.give_due(plan.Plan(text), {"name": "swb-1", "flume": False}).startswith("swb-1 is due back to today's path")


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
    """bolt-plan "A bolt is created, given, dropped and landed through crew" (plan.19, record 0003): a drop of a bolt a
    team holds has sluice delete its branch, asked on the team's host once its worktrees are gone; what is said of it
    (plan.dropped_said). That it is marked dropped and recorded once is the journey's (t-journey-land)."""
    HOST = "chuck-herdr-alpha"
    KEPT = "it is the drop's unmerged work, the user's to keep or delete, and crew asks sluice again once main holds its tip"

    def said(self, name, policy=POLICY, again=False):
        return plan.dropped_said("b", self.HOST, 0, deleted(name, policy), "", again)

    def test_a_dropped_bolt_whose_tip_main_holds_is_deleted_from_github(self):
        """bolt-plan "Dropping a bolt a team holds"."""
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
            "--into main there; the team's next read asks it")

    def test_words_crew_cannot_read_leave_it_to_the_next_read(self):
        """read.2: what is not sluice's document decides nothing."""
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").startswith(
            "bolt/b may still stand on GitHub: crew can't read what sluice's branch delete said from:")
        assert plan.dropped_said("b", self.HOST, 0, deleted("delete.json").replace("RC=0", "RC=x"), "").endswith(
            "; the team's next read asks sluice again")

    def test_asked_again_once_main_holds_its_tip(self):
        """bolt-plan "Main comes to hold a dropped bolt's work"."""
        assert self.said("delete.json", again=True) == (
            "bolt/b is removed: main now holds bolt b's tip, and sluice deleted it from GitHub at 22eef85")
        assert self.said("delete-queued.json", again=True) == (
            "bolt/b is still kept: #1 still queued on bolt/b; wait for them to land, or withdraw them")


class TestGiveThroughSluice:
    """bolt-plan "A bolt is created, given, dropped and landed through crew" (plan.19): what a give checks before sluice
    makes the branch, every refusal coming before the plan write, so the plan is unchanged and no branch made; what
    sluice's create says; and a write refused after it, which has sluice delete the branch again."""

    def check(self, text=POLICY, version="sluice 0.36.4 "):
        return plan.give_check(KIT, WHERE, "origin/main", text, "b", version, "chuck-herdr-alpha")

    def test_a_kit_on_github_with_a_sluice_that_makes_branches_gives_on_its_remote(self):
        assert self.check() == "origin"

    def test_a_kit_whose_bolts_have_no_remote_is_refused_naming_the_file_and_the_key(self):
        with pytest.raises(plan.Refusal) as e:
            self.check('[branches."bolt/*"]\nrequired = ["#check-full"]\n')
        assert str(e.value).startswith(f"{KIT} gives bolts only on GitHub, and its {WHERE} on origin/main names no remote")

    def test_a_kit_with_no_bolt_checks_is_refused_first(self):
        with pytest.raises(plan.Refusal, match="names no checks for its bolt branches"):
            self.check('[branches."bolt/*"]\nremote = "origin"\n')

    @pytest.mark.parametrize("version, said", [("sluice 0.18.0 ", "sluice 0.18.0"), ("", "nothing")])
    def test_a_host_whose_sluice_is_older_or_unread_is_refused(self, version, said):
        with pytest.raises(plan.Refusal) as e:
            self.check(version=version)
        assert str(e.value) == ("a bolt is given through sluice 0.20.0 or later, which has `branch create`, and sluice "
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
    def test_a_branch_a_give_left_at_mains_tip_with_no_commit_of_its_own_is_taken_and_the_give_goes_on(self, own):
        """A give that failed after sluice made the branch leaves it on GitHub at main's tip, and the host's own copy
        there too or none: the give run again takes it rather than refuse it as already there."""
        assert self.made(own=own, there=self.MADE, main=self.MADE) == (self.MADE, True)

    def test_a_branch_with_commits_of_its_own_is_still_refused_by_name(self):
        assert self.refused(own=self.OWN, there=self.OWN, main=self.MADE) == (
            f"{self.PRESENT}; bolt/b on origin is at 22eef85 and origin's main at c0da39b, so it is no branch a give left "
            "empty at main, and crew gives no bolt onto it")

    def test_a_branch_whose_hosts_copy_stands_elsewhere_is_refused_by_name(self):
        assert self.refused(own=self.OWN, there=self.MADE, main=self.MADE) == (
            f"{self.PRESENT}; chuck-herdr-alpha's own bolt/b is at 22eef85, not at origin's c0da39b, and crew gives no "
            "bolt onto it")
        assert self.refused(own=self.OWN, there=None, main=self.MADE) == (
            f"{self.PRESENT}; chuck-herdr-alpha's own bolt/b is at 22eef85 and origin has none, and crew gives no bolt "
            "onto it")

    def test_a_branch_crew_cannot_read_on_its_remote_is_refused_with_gits_words(self):
        assert self.refused(read="fatal: could not read from remote repository") == (
            f"{self.PRESENT}; and crew could not read bolt/b on origin: fatal: could not read from remote repository")

    def test_a_refusal_that_finds_no_branch_is_sluices_words_alone(self):
        assert self.refused(own=None, there=None, main=self.MADE) == self.PRESENT

    def test_a_give_names_github_the_commit_and_the_teams_host(self):
        assert plan.given_said("swb-1", "b", KIT, "origin", self.MADE, "chuck-herdr-alpha") == (
            f"swb-1 holds b: sluice made bolt/b on GitHub (origin) from {KIT}'s main at c0da39b, built on chuck-herdr-alpha "
            "and merged into only through sluice")

    def test_a_give_that_took_the_branch_says_so(self):
        assert plan.given_said("swb-1", "b", KIT, "origin", self.MADE, "chuck-herdr-alpha", adopted=True) == (
            "swb-1 holds b: crew took bolt/b, which sluice made on GitHub (origin) for a give that did not finish, at "
            f"{KIT}'s main c0da39b, built on chuck-herdr-alpha and merged into only through sluice")

    def test_a_write_refused_after_the_create_has_sluice_delete_the_branch_again(self):
        why = "swb-1 holds bolt c since 1234567"
        assert plan.ungiven_said("b", why, deleted("delete.json"), 0) == (
            f"{why}; sluice deleted bolt/b again, so nothing of the give is left")

    def test_a_delete_sluice_refuses_then_names_the_branch_left_standing(self):
        why = "swb-1 holds bolt c since 1234567"
        assert plan.ungiven_said("b", why, deleted("delete-queued.json"), 0) == (
            f"{why}; and bolt/b, which sluice made for the give, still stands, since sluice did not delete it: #1 still "
            "queued on bolt/b; wait for them to land, or withdraw them")
        assert plan.ungiven_said("b", why, "", 255).endswith("since sluice did not delete it: its delete exited 255: nothing was said")


class TestLand:
    def test_a_landing_says_which_bolt_the_team_still_builds_or_that_it_holds_none(self):
        """A team may hold a bolt beside the one that lands (teams.16)."""
        head = "0123456789abcdef"
        assert plan.landed_line("doctor-rows", "swancloud", head, "swc-1", ["ssh-fix"]) == "doctor-rows has landed at swancloud's 0123456; swc-1 builds ssh-fix"
        assert plan.landed_line("doctor-rows", "swancloud", head, "swc-1", []) == "doctor-rows has landed at swancloud's 0123456 and swc-1 holds no bolt"

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


class TestQueuedLanding:
    """bolt-teams "A unit during a queued landing" (plan.8, record 0032 §3): no construct, code or merge starts on a
    bolt while its landing's worktree stands with LANDING's process alive in it, the submission in sluice's queue."""
    PATH = "/kit/places/land-b"

    def refusal(self, stage="construct", standing=True, alive=True, kind="unit"):
        return plan.landing_refusal(kind, "u", stage, "b", self.PATH, standing, alive)

    @pytest.mark.parametrize("stage", ["construct", "code", "merge"])
    def test_a_unit_during_a_queued_landing_is_refused_naming_the_landing(self, stage):
        assert self.refusal(stage) == (
            f"bolt b's landing is queued in sluice, submitted from /kit/places/land-b: unit u's {stage} starts once it has "
            "landed or been refused, since what merges into bolt/b meanwhile is left out of main's landing")

    def test_a_chores_code_and_merge_wait_alike(self):
        assert self.refusal("code", kind="chore").startswith("bolt b's landing is queued in sluice, submitted from /kit/places/land-b: chore u's code")

    @pytest.mark.parametrize("stage", ["verify", "settle"])
    def test_a_stage_that_moves_nothing_toward_the_bolt_starts(self, stage):
        assert self.refusal(stage) is None

    def test_once_sluices_outcome_is_in_a_worktree_left_standing_holds_nothing(self):
        # A landing git could not remove, or one stopped, leaves its worktree with no process: the fix that takes main
        # into a refused bolt starts, as does every unit.
        assert self.refusal(alive=False) is None
        assert self.refusal(standing=False, alive=False) is None


class TestMergesHoldThePullRequest:
    """A merge into the bolt and a fix's start hold the bolt's landing pull request (bolt-teams "A fix's start holds the
    pull request with the card", "A merge into the bolt does not land it", "A merge that can't hold the pull request
    does not start"), with pull_hold's reads and marks given as facts."""
    T = {"name": "swb-1", "label": "wldn", "machine": "box", "kit": {"name": "k", "main": "/k/main", "repo": "o/k"}}
    READY = dict(number=99, draft=False, head="c" * 40, url="https://github.com/o/k/pull/99")

    def held(self, monkeypatch, got):
        """pull_hold answering got, (pull, act) or a refusal's words, each call kept as self.asked."""
        self.asked = []

        def hold(fleet, t, bolt, want):
            self.asked.append((t["machine"], bolt, want))
            if isinstance(got, str):
                plan.fail(got)
            return got
        monkeypatch.setattr(plan, "pull_hold", hold)

    def test_a_merge_drafts_a_ready_pull_request_before_it_starts_and_says_so(self, monkeypatch, capsys):
        self.held(monkeypatch, (self.READY, "draft"))
        plan.merge_holds({}, self.T, "b", "unit a's merge into bolt/b")
        assert self.asked == [("box", "b", "held")]
        assert capsys.readouterr().out == (
            "Its pull request https://github.com/o/k/pull/99 is a draft, so no merge into bolt/b lands it; the next crew "
            "bolt submit b, on the user's word, makes it live again.\n")

    def test_a_merge_with_nothing_to_mark_says_nothing(self, monkeypatch, capsys):
        self.held(monkeypatch, (dict(self.READY, draft=True), None))
        plan.merge_holds({}, self.T, "b", "unit a's merge into bolt/b")
        self.held(monkeypatch, (None, None))
        plan.merge_holds({}, self.T, "b", "chore c's merge into bolt/b")
        assert capsys.readouterr().out == ""

    def test_a_merge_that_cant_hold_it_does_not_start_naming_it_in_ghs_words(self, monkeypatch):
        why = plan.pull_said("b", self.READY, "draft", "HTTP 403: Resource not accessible", "o/k")
        self.held(monkeypatch, why)
        with pytest.raises(plan.Refusal) as e:
            plan.merge_holds({}, self.T, "b", "fix/b/gap's merge into bolt/b")
        assert str(e.value) == f"fix/b/gap's merge into bolt/b does not start: {why}"

    def row(self, monkeypatch):
        """The bolt's row on its kit's landings card, held by the fix's start: its reading and preview ended on the
        team's host (land_end) and the kit's card raised with the fix's words (land_hand), each kept as done."""
        done = []
        monkeypatch.setattr(plan, "land_end", lambda fleet, label, bolt: done.append(("end", bolt)))
        monkeypatch.setattr(plan, "land_hand", lambda fleet, label, kit, note=None: done.append(("hand", note)))
        return done

    def test_a_fixs_start_drafts_it_then_holds_the_card(self, monkeypatch, capsys):
        self.held(monkeypatch, (self.READY, "draft"))
        closed = []
        monkeypatch.setattr(plan, "landing_card_keys", lambda entries, bolt, owner: ["land/b"])
        monkeypatch.setattr(plan.cards, "host_entries", lambda *a: [])
        monkeypatch.setattr(plan.crew, "this_host", lambda: "box")
        monkeypatch.setattr(plan, "row_card_close", lambda fleet, label, owner, key, **kw: closed.append((owner, key, kw["reason"])))
        handed = self.row(monkeypatch)
        plan.landing_held({}, self.T, "b", "The zone list misses one zone.")
        assert capsys.readouterr().out.startswith("Its pull request https://github.com/o/k/pull/99 is a draft")
        assert closed == [("swb-1-conductor", "land/b", "held for a fix: The zone list misses one zone.")]
        assert handed == [("end", "b"), ("hand", "b is held for a fix: The zone list misses one zone.")]

    def test_a_fixs_start_that_cant_hold_it_says_so_and_the_fix_goes_on(self, monkeypatch, capsys):
        self.held(monkeypatch, "crew can't read o/k's open pull request from bolt/b into main: gh exited 1: HTTP 401: Bad credentials")
        closed = []
        monkeypatch.setattr(plan, "landing_card_keys", lambda entries, bolt, owner: ["land/b"])
        monkeypatch.setattr(plan.cards, "host_entries", lambda *a: [])
        monkeypatch.setattr(plan.crew, "this_host", lambda: "box")
        monkeypatch.setattr(plan, "row_card_close", lambda fleet, label, owner, key, **kw: closed.append(key))
        handed = self.row(monkeypatch)
        plan.landing_held({}, self.T, "b", "The zone list misses one zone.")
        said = capsys.readouterr()
        assert said.out == "" and said.err == (
            "crew can't read o/k's open pull request from bolt/b into main: gh exited 1: HTTP 401: Bad credentials; the fix "
            "goes on, and its merge drafts it before it starts\n")
        assert closed == ["land/b"]


class TestSplitBolt:
    """bolt-teams "A split bolt takes no merge" (plan.19): a merge into a bolt whose host's tip names a remote for it,
    while that remote's bolt/<bolt> lacks the tip, is refused naming both commits, what is lacked and the landing."""
    LOCAL, THERE = "1" * 40, "2" * 40

    def facts(self, there=THERE, held="no", merges=2, carried=None, read=None):
        return dict(local=None if read or there == "-" else self.LOCAL, there=None if read else there,
                    held=None if read or there == "-" else held, merges=None if read or there == "-" else merges,
                    carried=None if read or there == "-" else carried, read=read)

    def refusal(self, kind="unit", name="u", **f):
        return plan.split_refusal(kind, name, "b", "mac-studio", "origin", self.facts(**f))

    def test_a_merge_into_a_split_bolt_is_refused_naming_the_merges_and_the_landing(self):
        assert self.refusal() == (
            "bolt/b is split: its tip on mac-studio, 1111111, names origin for it, so sluice would form unit u's merge "
            "on origin's bolt/b at 2222222, which lacks 2 merges mac-studio holds, and drop them. The bolt takes no "
            "merge until it lands: its landing (crew bolt submit b, main-level ops's on the user's word) pushes "
            "mac-studio's tip to origin and makes the two one")

    def test_one_merge_lacked_is_named_alone(self):
        assert "which lacks 1 merge mac-studio holds, and drop it. " in self.refusal(merges=1)

    def test_a_tip_lacked_with_no_merge_beyond_names_the_tip(self):
        assert "at 2222222, which lacks mac-studio's tip, and drop it. The bolt takes no merge" in self.refusal(merges=0)

    @pytest.mark.parametrize("kind, name", [("chore", "bump-moon"), ("fix", "the-tidy-keeps-a-run")])
    def test_a_chores_or_a_fixs_merge_is_refused_naming_it(self, kind, name):
        assert self.refusal(kind, name).startswith(
            f"bolt/b is split: its tip on mac-studio, 1111111, names origin for it, so sluice would form {kind} {name}'s merge on")

    def test_a_fix_that_took_the_hosts_merges_in_lets_its_merge_through(self):
        """plan.19 as read for batch 34's reviewer: a diverged bolt's way on is a fix cut from GitHub's head that takes
        the host copy's merges in; its head holds the host's tip, so sluice's merge on GitHub's copy drops none."""
        assert self.refusal("fix", "carry-the-hosts-merges", carried="yes") is None

    def test_a_fix_that_did_not_take_them_in_is_refused_naming_the_carry(self):
        assert self.refusal("fix", "f", carried="no").endswith(
            "makes the two one; a fix that takes mac-studio's merges in first (git merge bolt/b in its place) carries "
            "them, and merges")
        assert "git merge" not in self.refusal() and "git merge" not in self.refusal("chore", "c")

    def test_a_copy_that_holds_the_hosts_tip_lets_the_merge_through(self):
        # Equal, or ahead with merges sluice landed there from another host: held either way, nothing dropped.
        assert self.refusal(held="yes", merges=0) is None
        assert self.refusal(there=self.LOCAL, held="yes", merges=0) is None

    def test_a_bolt_github_has_no_copy_of_is_left_to_sluice(self):
        assert self.refusal(there="-") is None

    def test_a_copy_crew_cannot_read_refuses_naming_gits_words(self):
        assert self.refusal("chore", "c", read="fatal: 'gone.git' does not appear to be a git repository") == (
            "crew can't tell whether bolt/b is split, so chore c's merge waits: fatal: 'gone.git' does not appear to be "
            "a git repository")


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

    def test_a_bolt_whose_policy_crew_cant_read_is_unknown_for_all_that_has_not_landed(self):
        """bolt-plan "A policy crew can't read": nothing is read from the host's bolt/b in its place."""
        why = ".config/sluice.toml at origin/bolt/b is not TOML, so crew can't read bolt b: Expected ']'"
        fleet = {"partitions": {"wldn": {"teams": ["swb-1"]}},
                 "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": "box", "kit": {"main": "/kit/main", "dir": "/kit", "name": KIT}}}}
        p = plan.Plan(plan_text(bolts=[("b", KIT, "swb-1")], units=[("a", KIT, "b", []), ("done", KIT, "b", []), ("bump", KIT, "b", [], "chore")]))
        k = {"ok": True, "main": ["done"], "chores": [], "places": {"a": {"path": "/kit/places/a", "tasks": [2, 2], "planning": True, "open": [], "head": "h"}},
             "chore_places": {}, "fixes": [], "bolts": {"b": {"exists": False, "at": None, "changes": [], "archived": [], "open": {}, "chores": [],
                                                              "head": None, "head_at": None, "verdict": None, "error": why}}}
        st = plan.Stages(fleet, p, {"box": {"ok": True, "kits": {"/kit/main": k}}})
        assert (st.of("a")["stage"], st.of("a")["why"]) == ("unknown", why)
        assert (st.of("bump")["stage"], st.of("bump")["why"]) == ("unknown", why)
        assert st.of("done")["stage"] == "landed"
        assert st.bolt_state(p.bolt("b")) == "unknown"


class TestWhenABoltIsFetched:
    """bolt-plan "A bolt on GitHub is fetched where a decision rests on it" (plan.18, plan.19, design Decision 3): crew
    bolts and a give's proven check ask each kit's GitHub fetched first; every other read fetches nothing."""
    FLEET = {"partitions": {"wldn": {"teams": ["swb-1"]}},
             "teams": {"swb-1": {"name": "swb-1", "label": "wldn", "machine": "box",
                                 "kit": {"main": "/kit/main", "dir": "/kit", "name": KIT}}}}
    KIT_READ = {"ok": True, "main": [], "chores": [], "places": {}, "chore_places": {}, "fixes": [],
                "bolts": {"b": {"exists": True, "at": "origin/bolt/b", "changes": [], "archived": [], "open": {}, "chores": [],
                                "head": "d" * 40, "head_at": "2026-10-23T09:00:00Z", "verdict": ""}}}

    def asked(self, monkeypatch, kept=None):
        asks = []
        monkeypatch.setattr(plan, "READ", plan.Reading())
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
        plan.stages_for(self.FLEET, self.plan(), self.plan().bolts())
        assert [("fetch" in a) for a in asks] == [False]

    def test_a_fetching_survey_is_asked_though_the_command_has_read_the_kit(self, monkeypatch):
        asks = self.asked(monkeypatch, kept={"/kit/main": self.KIT_READ})
        plan.stages_for(self.FLEET, self.plan(), self.plan().bolts())
        assert asks == []
        st = plan.stages_for(self.FLEET, self.plan(), self.plan().bolts(), fetch=True)
        assert [a.get("fetch") for a in asks] == [True]
        assert st.kit(self.plan().bolt("b"))[0]["bolts"]["b"]["at"] == "origin/bolt/b"

    def test_a_fetch_that_fails_reads_the_kit_unknown_with_gits_words(self, monkeypatch):
        """bolt-plan "A fetch that fails"."""
        self.asked(monkeypatch)
        why = "cannot fetch /kit/main from GitHub: fatal: unable to access 'https://github.com/o/k/': Could not resolve host"
        monkeypatch.setattr(plan, "gathered", lambda fleet, host, req: ({"/kit/main": {"ok": False, "error": why}}, None))
        st = plan.stages_for(self.FLEET, self.plan(), self.plan().bolts(), fetch=True)
        assert (st.of("a")["stage"], st.of("a")["why"]) == ("unknown", f"box: {why}")
        assert st.bolt_state(self.plan().bolt("b")) == "unknown"

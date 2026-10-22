"""crew bolt new|order|drop on the plan (bolt-plan spec): each applied to a plan in memory, with the stages a drop
reads given; which bolt a give hands a team (plan.to_give) and when a team may take one (plan.give_refusal), and when a bolt lands (plan.land_refusal),
held by a team or by none (plan.unheld_stages, plan.unheld_refusal, plan.builder).
The branch and worktree give makes and land removes, and the commits every write makes, are the journey's
(t-journey-units and t-journey-land)."""
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

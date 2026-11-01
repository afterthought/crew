"""A fix (teams.3, teams.5, plan.8, teams.15): plan.fix_in_slot for what crew fix <name> acts on, plan.leftover and
plan.own_place for a fix refused its place, plan.fix_prompt for what its agent starts with, told of a place that could
not be made ready (record 0028), plan.fix_drop_why and plan.branch_kept for a fix dropped, plan.fix_bolt for the bolt a fix is of, of the two a team may hold (teams.16), and crew.never_started for a fix's or unit's
stage whose prompt was never taken. A fix merges as a unit does, by a submission to sluice (teams.5); the fix's place
and stage through the command are the journey's (t-journey-fix)."""
import pytest


import crew
import kit
import plan

KD = "/kit"


class TestWhich:
    def test_a_new_fix_gets_a_branch_and_place_of_its_bolt(self):
        assert plan.fix_in_slot([], "tenant-environments", "edge-sign-in", KD) == (
            None, "fix/tenant-environments/edge-sign-in", "/kit/places/fix-tenant-environments--edge-sign-in")

    def test_two_teams_fixes_of_one_name_are_each_their_own_bolts(self):
        assert plan.fix_in_slot([], "console-pages", "bolt-takes-main", KD)[1:] == (
            "fix/console-pages/bolt-takes-main", "/kit/places/fix-console-pages--bolt-takes-main")

    def test_a_fix_in_flight_keeps_what_its_slot_recorded(self):
        held = [["unit-1", "fix", "fix/t/edge", "/kit/places/fix-t--edge"], ["unit-2", "fix", "fix/old-sign-in", "/kit/places/fix-old-sign-in"]]
        assert plan.fix_in_slot(held, "t", "edge", KD) == ("unit-1", "fix/t/edge", "/kit/places/fix-t--edge")
        assert plan.fix_in_slot(held, "t", "old-sign-in", KD) == ("unit-2", "fix/old-sign-in", "/kit/places/fix-old-sign-in")

    def test_the_fix_of_its_bolt_comes_before_one_named_before_fixes_held_their_bolt(self):
        held = [["unit-2", "fix", "fix/x", "/kit/places/fix-x"], ["unit-1", "fix", "fix/t/x", "/kit/places/fix-t--x"]]
        assert plan.fix_in_slot(held, "t", "x", KD)[0] == "unit-1"

    def test_a_fix_is_named_as_crew_names_things(self):
        assert crew.NAME.match("edge-sign-in") and not crew.NAME.match("Edge_Sign")

    def test_a_team_holding_no_bolt_has_no_fix(self):
        with pytest.raises(plan.Refusal, match="swb-2 holds no bolt: crew bolt give swb-2"):
            plan.fix_bolt("swb-2", [], None, [], "edge")


class TestFixBolt:
    """A team may hold a bolt that waits to land beside the one it builds (teams.16), so a fix names its bolt."""
    TWO = ["doctor-rows", "ssh-fix"]

    def test_the_bolt_named_and_held(self):
        assert plan.fix_bolt("swc-1", self.TWO, "doctor-rows", [], "take-main") == "doctor-rows"

    def test_a_bolt_named_and_not_held_is_refused(self):
        with pytest.raises(plan.Refusal, match="swc-1 holds no bolt other: it holds doctor-rows and ssh-fix"):
            plan.fix_bolt("swc-1", self.TWO, "other", [], "take-main")

    def test_one_held_and_none_named_is_that_one(self):
        assert plan.fix_bolt("swc-1", ["ssh-fix"], None, [], "gap") == "ssh-fix"

    def test_a_new_fix_naming_no_bolt_while_two_are_held_is_refused_naming_both_and_bolt(self):
        with pytest.raises(plan.Refusal, match="swc-1 holds doctor-rows and ssh-fix: name the fix's bolt with --bolt"):
            plan.fix_bolt("swc-1", self.TWO, None, [], "gap")

    def test_a_fix_in_flight_is_found_by_its_name_among_the_bolts(self):
        assert plan.fix_bolt("swc-1", self.TWO, None, ["unit/a", "fix/doctor-rows/x"], "x") == "doctor-rows"

    def test_a_name_in_flight_on_both_is_refused_without_bolt(self):
        with pytest.raises(plan.Refusal, match="fix x is in flight on doctor-rows and ssh-fix: name its bolt with --bolt"):
            plan.fix_bolt("swc-1", self.TWO, None, ["fix/doctor-rows/x", "fix/ssh-fix/x"], "x")


class TestPlace:
    def test_a_new_fixs_branch_or_place_already_there_is_not_taken_over(self):
        assert plan.leftover("fix/t/stray", "/kit/places/fix-t--stray", "swb-1", True, False) == (
            "fix/t/stray already has a place at /kit/places/fix-t--stray that no slot of swb-1 holds: name this fix differently")
        assert plan.leftover("fix/t/leftover", "/kit/places/fix-t--leftover", "swb-1", False, True) == (
            "fix/t/leftover already has a branch that no slot of swb-1 holds, though no place at /kit/places/fix-t--leftover: "
            "name this fix differently")
        assert plan.leftover("fix/t/new", "/p", "swb-1", False, False) is None

    def test_a_place_on_its_own_branch_from_the_bolt_is_its_own_mid_rebase_too(self):
        assert plan.own_place("/p", "fix/t/x", "bolt/t", "fix/t/x", "t") is None

    def test_a_place_cut_from_the_bolt_on_github_is_its_own(self):
        """plan.19: a fix's place of a bolt on GitHub tracks origin/bolt/<bolt>."""
        assert plan.own_place("/p", "fix/t/x", "origin/bolt/t", "fix/t/x", "t") is None

    @pytest.mark.parametrize("on, up, said", [
        ("elsewhere", "", "/p is on elsewhere, made from no bolt, not fix/t/x from bolt/t"),
        ("fix/t/x", "bolt/other", "/p is on fix/t/x, made from bolt/other, not fix/t/x from bolt/t"),
        ("fix/t/x", "origin/main", "/p is on fix/t/x, made from origin/main, not fix/t/x from bolt/t"),
        ("", "", "/p is on no branch, made from no bolt, not fix/t/x from bolt/t")])
    def test_any_other_is_refused(self, on, up, said):
        assert plan.own_place("/p", on, up, "fix/t/x", "t") == said + ": crew starts a fix only in its own place"
        assert plan.own_place("/p", on, up, "fix/t/x", "t", "drops a fix") == said + ": crew drops a fix only in its own place"


class TestUnready:
    """A fix's agent starts in a place that could not be made ready, told what failed (teams.3, record 0028)."""

    def test_a_ready_place_starts_the_fix_with_its_words_alone(self):
        assert plan.fix_prompt("The banner flickers.", "/kit/places/fix-b--tidy") == "Fix: The banner flickers."

    def test_a_place_not_ready_tells_the_agent_the_step_and_its_last_lines_on_one_line(self):
        why = kit.step_failed("/kit/places/fix-b--tidy", "moon setup", 1, "resolving toolchains\nbun: no such version 1.2.23\n")
        prompt = plan.fix_prompt("Take main into the bolt.", "/kit/places/fix-b--tidy", why)
        assert prompt.startswith("Fix: Take main into the bolt. Your place /kit/places/fix-b--tidy could not be made ready, so the kit's "
                                 "tools may not run in it: /kit/places/fix-b--tidy is made but not ready: moon setup exited 1: / ")
        assert "bun: no such version 1.2.23" in prompt and "\n" not in prompt
        assert prompt.endswith("Repairing that may be part of this fix.")


class TestDrop:
    """A fix is dropped by its conductor (teams.3, record 0028): refused once merged or when nothing of it is there; its
    branch kept when it holds commits beyond the bolt (plan.10)."""

    def test_a_merged_fix_is_not_dropped(self):
        assert plan.fix_drop_why("fix/t/x", "t", "swb-1", "unit-1", True, True, True) == (
            "fix/t/x has merged into bolt/t, so it is not dropped: what it changed is the bolt's, and a new fix undoes it")

    def test_one_no_slot_place_or_branch_holds_is_not_there_to_drop(self):
        assert plan.fix_drop_why("fix/t/x", "t", "swb-1", None, False, False, False) == (
            "swb-1 has no fix fix/t/x: no slot, place or branch holds it")

    @pytest.mark.parametrize("slot, place, branch", [
        ("unit-1", True, True), ("unit-1", False, False), (None, True, True), (None, False, True)])
    def test_one_in_flight_or_standing_with_no_slot_is_dropped(self, slot, place, branch):
        assert plan.fix_drop_why("fix/t/x", "t", "swb-1", slot, place, branch, False) is None

    def test_its_branch_goes_when_git_cherry_finds_nothing_of_its_own(self):
        assert plan.branch_kept("bolt/t", (0, "", "")) is None
        assert plan.branch_kept("bolt/t", (0, "- 1a2b3c\n", "")) is None

    def test_one_holding_patches_the_bolt_lacks_is_kept_and_counted(self):
        assert plan.branch_kept("bolt/t", (0, "- 1a2b3c\n+ 4d5e6f\n", "")) == (
            "it holds 1 commit whose patch bolt/t lacks (git cherry), the user's to keep or delete", 1)
        assert plan.branch_kept("bolt/t", (0, "+ 1a2b3c\n+ 4d5e6f\n", "")) == (
            "it holds 2 commits whose patch bolt/t lacks (git cherry), the user's to keep or delete", 2)

    def test_one_that_cannot_be_compared_is_kept(self):
        assert plan.branch_kept("bolt/gone", (128, "", "fatal: unknown commit bolt/gone\n")) == (
            "git cannot compare it with bolt/gone: fatal: unknown commit bolt/gone", None)

    def test_one_tracking_no_bolt_is_compared_with_nothing_and_kept(self):
        assert plan.branch_target("fix", "", False, False, "refs/remotes/origin/main") is None
        assert plan.branch_kept(None, None) == ("it tracks no bolt to compare it with", None)

    def test_its_bolt_is_its_target_while_it_stands_unlanded_and_main_once_it_has_landed_or_is_gone(self):
        """bolt-teams "A worktree goes when its work is over" (record 0003): a fix's branch whose bolt has landed, or
        whose bolt's branch is gone, is judged against the kit's main as a unit's is."""
        assert plan.branch_target("fix", "bolt/t", True, False, "refs/remotes/origin/main") == "bolt/t"
        assert plan.branch_target("fix", "bolt/t", True, True, "refs/remotes/origin/main") == "refs/remotes/origin/main"
        assert plan.branch_target("fix", "bolt/gone", False, False, "refs/remotes/origin/main") == "refs/remotes/origin/main"


class TestCrossed:
    """A fix on a crossed team's bolt is a Flume place (Decision 10 of teams-cross-to-flume-as-their-bolts-land): a
    launch of the fix kind on the bolt's branch, dropped by a drop, merged and waited on by Flume alone, holding the
    bolt's landing while it is in flight."""
    T = None

    @pytest.fixture(autouse=True)
    def planner(self, monkeypatch):
        from facts import crossed_fleet
        monkeypatch.setenv("CREW_AGENT", "madswan-planner")
        self.FLEET = crossed_fleet()
        self.T = dict(self.FLEET["teams"]["crw-4"])

    def bolt(self, runners=None, work=("a",)):
        """crossed crw-4 given x through Flume, its units launched as the give launches them."""
        from facts import FactsWrite, flume_plan
        w = FactsWrite(flume_plan([("x", None, None)], [(u, "x", [], "unit", []) for u in work]), runners=runners, label="madswan")
        b = w.plan.bolt("x")
        b.set("Team", "crw-4")
        b.set("Path", "flume", after="Team")
        plan.reach_places(self.FLEET, w, "x", self.T)
        return w

    def launches(self, w):
        return [{f: v for f, v in r.fields if f not in ("Date", "By")} for r in plan.Plan(w.files["requests.rec"]).recs("Request")]

    def test_a_review_note_marked_fix_is_a_launch_of_a_fix_on_the_bolts_branch(self):
        """The planner runs crew fix crw-4 rail-word "Say 'land' for a crossed bolt" --bolt x on a batch's note."""
        w = self.bolt()
        assert plan.fix_flume(w, self.T, "x", "start", "rail-word", "Say 'land' for a crossed bolt") == dict(n=2, host="deneb", stream="madswan")
        assert self.launches(w)[1] == {
            "Request": "2", "Act": "launch", "Host": "deneb", "Work": "fix/x/rail-word", "Repo": "afterthought/crew", "Kind": "fix",
            "Name": "x--rail-word", "Base": "bolt/x", "Stream": "madswan", "Priority": "1", "Intent": "madswan/x",
            "Recipient": "madswan/planner", "Brief": "Say 'land' for a crossed bolt"}
        assert w.subject == "plan(x): fix rail-word"

    def test_a_name_in_use_on_the_bolt_is_refused(self):
        w = self.bolt()
        plan.fix_flume(w, self.T, "x", "start", "rail-word", "Say land.")
        with pytest.raises(plan.Refusal, match=r"^fix rail-word is in use on bolt x: it is launched as Flume place x--rail-word \(request 2\), "
                                               r"so name this fix differently$"):
            plan.fix_flume(w, self.T, "x", "start", "rail-word", "Again.")

    def test_a_team_turned_back_launches_its_fix_in_the_stream_the_bolts_launches_named(self):
        w = self.bolt()
        assert plan.fix_flume(w, dict(self.T, flume=False), "x", "start", "rail-word", "Say land.")["stream"] == "madswan"

    def test_drop_drops_its_launch(self):
        from facts import ran
        w = self.bolt(runners=ran({2: "code"}))
        plan.fix_flume(w, self.T, "x", "start", "rail-word", "Say land.")
        assert plan.fix_flume(w, self.T, "x", "drop", "rail-word", "") == dict(n=3, host="deneb", stream="madswan")
        assert self.launches(w)[2] == {"Request": "3", "Act": "drop", "Host": "deneb", "Work": "fix/x/rail-word", "Of": "2"}
        assert w.subject == "plan(x): drop fix rail-word"

    @pytest.mark.parametrize("at, said", [
        ("landed", "^fix/x/rail-word has merged into bolt/x, so it is not dropped: what it changed is the bolt's, and a new fix undoes it$"),
        (None, "^can't tell whether fix/x/rail-word's place has merged into bolt/x, so it is not dropped: no runner answers on deneb")])
    def test_a_merged_fix_or_one_crew_cant_read_is_not_dropped(self, at, said):
        from facts import ran
        w = self.bolt(runners=ran({2: at}) if at else None)
        plan.fix_flume(w, self.T, "x", "start", "rail-word", "Say land.")
        with pytest.raises(plan.Refusal, match=said):
            plan.fix_flume(w, self.T, "x", "drop", "rail-word", "")

    def test_a_fix_with_no_launch_is_not_there_to_drop(self):
        with pytest.raises(plan.Refusal, match="^crw-4 has no fix fix/x/gap: no launch of it stands in requests.rec$"):
            plan.fix_flume(self.bolt(), self.T, "x", "drop", "gap", "")

    def test_a_bolt_of_todays_path_has_no_flume_fix(self):
        from facts import FactsWrite, flume_plan
        w = FactsWrite(flume_plan([("x", "crw-4", None)], [("a", "x", [], "unit", [])]), label="madswan")
        with pytest.raises(plan.Refusal, match="^bolt x is not given through Flume, so its fix is not a Flume place$"):
            plan.fix_flume(w, self.T, "x", "start", "gap", "A gap.")

    @pytest.mark.parametrize("mode", ["merge", "wait"])
    def test_merge_and_wait_are_flumes_and_crew_bolts_shows_the_stage(self, mode):
        import runner
        assert runner.fix_flume_refusal(mode, "crw-4", "x", "rail-word") == (
            "fix/x/rail-word is a Flume place on bolt/x, which Flume submits to the bolt through sluice itself once its code has "
            f"delivered, telling the planner its end, so crew fix crw-4 rail-word --{mode} has nothing to do: crew bolts shows its stage")

    def test_a_fix_in_flight_is_found_by_its_name_among_the_launches_standing(self):
        assert plan.fix_bolt("crw-4", ["x", "y"], None, ["unit/a", "fix/y/rail-word"], "rail-word") == "y"

    def test_a_fix_in_flight_holds_the_bolts_landing_until_it_has_merged_or_been_dropped(self):
        """Fixes rail-word in code, tidy merged, gone dropped by crew and stray on a host crew can't read."""
        import runner
        from facts import ran
        w = self.bolt(runners=ran({2: "code", 3: "landed"}))
        for name in ("rail-word", "tidy", "gone"):
            plan.fix_flume(w, self.T, "x", "start", name, f"Fix {name}.")
        plan.fix_flume(w, self.T, "x", "drop", "gone", "")
        requests = plan.Plan(w.files["requests.rec"]).recs("Request")
        assert runner.fixes_in_flight(requests, ran({2: "code", 3: "landed"}), "madswan", "x") == {"fix/x/rail-word": "Fix rail-word."}
        assert runner.fixes_in_flight(requests, {}, "madswan", "x") == {"fix/x/rail-word": "Fix rail-word.", "fix/x/tidy": "Fix tidy."}
        assert plan.landing_unready([("a", "unit", "merged")], "h" * 40, "passed", ["fix/x/rail-word"]) == "fix/x/rail-word is in flight on it"
        row = plan.landing_rows(["x"], {"x": {"head": "h" * 40, "fixes": {"fix/x/rail-word": "Fix rail-word."}}}, {})[0]
        assert (row["box"], row["why"]) == (False, "held for a fix: Fix rail-word. (fix/x/rail-word)")

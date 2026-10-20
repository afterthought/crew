"""A bolt lands by main-level ops's submission of its branch to main through sluice (plan.16, record 0026): what
plan.landing_said makes of what the landing's submission did on the team's host; and its landing card, raised by crew
once the bolt reads proven, held by a fix and closed at the landing (record 0031 §1)."""
import pathlib

import pytest

import plan

OLD, NEW = "a" * 40, "b" * 40


def said(rc, new=NEW, kept="''", why="''", level="yes", marked="yes"):
    return f"RC={rc} OLD={OLD} NEW={new} KEPT={kept} WHY={why} LEVEL={level} MARKED={marked}\n"


def test_a_landing_says_where_main_is_and_what_comes_next():
    assert plan.landing_said("b", "switchboard-kit", said(0)) == (
        True, "bolt/b landed on switchboard-kit's main at bbbbbbb: now crew bolt land b.")


def test_a_main_checkout_not_brought_level_is_named_with_the_command():
    landed, words = plan.landing_said("b", "k", said(0, level="'git read-tree could not bring it level'"))
    assert landed and words.endswith("k's main checkout was not brought level (git read-tree could not bring it level): "
                                     "git read-tree -m -u aaaaaaa main there.")


def test_a_bolt_branch_with_no_mark_of_crews_is_named_and_lands_all_the_same():
    """bolt-teams "A landing leaves only what main lacks" (record 0003, read.4): the landing marks the bolt's branch
    landed only when it carries crew's mark, and says when it could not; a landing is a landing either way."""
    assert plan.landing_said("b", "k", said(0, marked="no")) == (
        True, "bolt/b landed on k's main at bbbbbbb: now crew bolt land b. crew could not mark bolt/b landed: its branch "
              "carries no mark of crew's.")
    assert plan.landing_said("b", "k", said(0, marked="'git config could not set it'"))[1].endswith(
        "crew could not mark bolt/b landed: git config could not set it.")


def test_a_landing_that_did_not_land_says_nothing_of_the_mark():
    assert "mark" not in plan.landing_said("b", "k", said(2, new=OLD, marked="''"))[1]
    assert "mark" not in plan.landing_said("b", "k", f"RC=0 OLD={OLD} NEW={NEW} KEPT='' LEVEL=yes\n")[1]


def test_a_conflict_lands_nothing_and_is_the_bolts_to_take():
    landed, words = plan.landing_said("b", "k", said(2, new=OLD))
    assert not landed
    assert words.startswith("bolt/b did not land: sluice refused it or found a conflict, and main is where it was.")
    assert "the team takes main into it by a submission to the bolt" in words


def test_checks_that_failed_land_nothing():
    assert plan.landing_said("b", "k", said(1, new=OLD))[1].startswith("bolt/b did not land: main's checks failed on it")


def test_a_worktree_git_could_not_remove_is_named_with_gits_words_and_goes_with_the_bolt():
    """read.1, plan.19: the landing's place git could not remove is said by name, in git's words, never kept silently,
    and crew bolt land sweeps it with the bolt or names it there."""
    why = "\"fatal: '/k/places/land-b' contains modified or untracked files, use --force to delete it\""
    for rc, new in ((2, OLD), (0, NEW)):
        assert plan.landing_said("b", "k", said(rc, new=new, kept="/k/places/land-b", why=why))[1].endswith(
            "Its worktree /k/places/land-b is kept, git refusing to remove it: fatal: '/k/places/land-b' contains modified "
            "or untracked files, use --force to delete it. crew bolt land removes it with the bolt, or names it with why it stays.")
    assert plan.landing_said("b", "k", said(0))[1].endswith("now crew bolt land b.")


def test_words_crew_cannot_read_land_nothing():
    assert plan.landing_said("b", "k", "wt: command not found\n") == (
        False, "crew can't read what the submission of bolt/b to k's main came to: wt: command not found")


def test_the_anchor_is_detached_and_the_landing_says_nothing_of_levelling_it():
    """bolt-teams "The anchor is detached" (plan.18): the fleet's timer moves a detached main checkout, so a landing
    neither levels it nor says anything of it."""
    landed, words = plan.landing_said("b", "k", said(0, level="detached"))
    assert landed and "level" not in words and "read-tree" not in words


def test_the_hosts_main_lags_githubs_and_nothing_is_refused_for_it():
    """bolt-teams "Main is behind GitHub's" (plan.8, plan.18): the landing reads only the commit GitHub's main holds
    after a fetch, which it records, and a host's own main lagging it refuses nothing."""
    github, own = "d" * 40, "e" * 40
    assert plan.main_held("k", "chuck-herdr-alpha", f"ORIGIN=yes\nFETCHED=ok\nGITHUB={github}\nOWN={own}\n") == (github, None)


class TestTheCardsClose:
    """crew bolt land closes the bolt's landing card on its team's host (plan.16, record 0032 §3): with where GitHub's
    main holds the landing and that every host's folder follows by the timer, under whichever landing key the conductor
    holds one."""

    def test_the_card_closes_naming_githubs_main_sluices_submission_and_the_timer(self):
        assert plan.landed_words("c" * 40, "46") == (
            "landed on GitHub's main at ccccccc (#46); every host's folder follows by swancloud's timer within minutes")

    def test_a_head_sluice_did_not_make_is_named_without_a_number(self):
        for n in ("", None, "46 47", "x"):
            assert plan.landed_words("c" * 40, n) == (
                "landed on GitHub's main at ccccccc; every host's folder follows by swancloud's timer within minutes")

    def test_the_conductors_open_cards_under_the_bolts_landing_keys_old_and_new(self):
        post = lambda key, card, by="swb-1-conductor": {"Act": "card.post", "Key": key, "Card": card, "By": by}
        entries = [post("land/b/abc1234", "req_1"), post("land/b", "req_2"), post("land/b/abc9999", "req_3"),
                   {"Act": "card.close", "Card": "req_3", "Key": "land/b/abc9999", "By": "swb-1-conductor"},
                   post("land/b", "req_4", by="swb-2-conductor"), post("land/bb", "req_5"), post("proposal/1", "req_6")]
        assert plan.landing_card_keys(entries, "b", "swb-1-conductor") == ["land/b", "land/b/abc1234"]
        assert plan.landing_card_keys(entries, "c", "swb-1-conductor") == []


class TestTheLandingsPoint:
    """crew raises a bolt's landing card once the bolt reads proven (rail-cards, record 0031 §1, record 0025): every
    unit and chore merged, sluice green at its head, no fix in flight on it, and every unit's latest change in a
    batch; then which act follows each event."""
    GREEN = "passed (3 run, 1 replayed)"
    WORK = [("a", "unit", "merged"), ("b", "unit", "merged"), ("c", "chore", "merged")]

    def unready(self, work=WORK, verdict=GREEN, fixes=()):
        return plan.landing_unready(work, "abc1234" + "0" * 33, verdict, list(fixes))

    def test_a_green_bolt_whose_every_unit_and_chore_merged_reads_proven(self):
        assert self.unready() is None
        assert self.unready(self.WORK + [("d", "unit", "landed")]) is None

    @pytest.mark.parametrize("work, verdict, fixes, why", [
        ([("a", "unit", "verify")] + WORK[1:], GREEN, (), "unit a has not merged: it is verify"),
        ([], GREEN, (), "it holds no units or chores"),
        ([("a", "unit", "landed")], GREEN, (), "every unit and chore of it has landed"),
        (WORK, "", (), "its verification is not green: its head abc1234 is no landing of sluice's, so it has no verdict"),
        (WORK, GREEN, ("fix/y/zone-gap",), "fix/y/zone-gap is in flight on it")])
    def test_until_then_no_card_is_raised(self, work, verdict, fixes, why):
        assert self.unready(work, verdict, fixes) == why

    def test_a_fix_is_in_flight_from_its_start_until_it_merges_or_is_dropped(self):
        """The landing's point waits for no fix of the bolt in flight: a fix place of the bolt that has neither merged
        nor been dropped; one of another bolt is not the bolt's."""
        fixes = [{"fix": "fix/y/gap", "bolt": "y", "merged": False, "dropped": False},
                 {"fix": "fix/y/done", "bolt": "y", "merged": True, "dropped": False},
                 {"fix": "fix/y/gone", "bolt": "y", "merged": False, "dropped": True},
                 {"fix": "fix/z/gap", "bolt": "z", "merged": False, "dropped": False}]
        assert plan.fixes_in_flight(fixes, "y") == ["fix/y/gap"]
        assert self.unready(fixes=plan.fixes_in_flight(fixes, "y")) == "fix/y/gap is in flight on it"
        assert self.unready(fixes=plan.fixes_in_flight(fixes[1:], "y")) is None

    def test_its_facts_wait_for_every_units_latest_change_to_have_been_in_a_batch(self):
        pr = plan.pull_of("swb-1-unit-2 (pull/23)", "WilldanGroup/switchboard-kit")
        facts = plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", "2026-10-17T10:00:00Z", set(), {}, {"a": 4, "b": 5}, 2, pr)
        assert facts == dict(bolt="y", kit="switchboard-kit", units=["a", "b"], chores=["c"], batches={"a": 4, "b": 5}, head="abc1234",
                             at="2026-10-17T10:00:00Z", moved=2, pr={"number": 23, "url": "https://github.com/WilldanGroup/switchboard-kit/pull/23"})
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, {"b"}, {}, {"a": 4}, 0, None) is None

    def test_its_facts_wait_for_the_users_answer_on_each_batch_card_that_holds_a_units_latest_change(self):
        """briefs.12: the user, 2026-10-19, on card req_5ff4d31d: "Wait for my answer on the batch card", after crew's
        small-leftovers-of-crew landed (#71) while batch 7's card, which held its unit, was unanswered."""
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, set(), {"b": 7}, {"a": 6, "b": 7}, 0, None) is None
        assert plan.landing_facts("y", "switchboard-kit", self.WORK, "abc1234", None, set(), {"q": 7}, {"a": 6, "b": 7}, 0, None)["units"] == ["a", "b"]

    def test_a_chore_is_in_no_batch_and_holds_no_landing(self):
        facts = plan.landing_facts("y", "switchboard-kit", [("c", "chore", "merged")], "abc1234", None, set(), {}, {}, 0, None)
        assert (facts["units"], facts["chores"], facts["batches"]) == ([], ["c"], {})

    def test_sluices_pull_request_is_the_one_its_submission_at_the_head_went_through(self):
        assert plan.pull_of("swb-1-unit-2 (unit/a)", "o/k") is None and plan.pull_of("", "o/k") is None

    def test_a_landing_reading_is_its_cover_each_units_change_in_the_plans_order_then_the_diff(self):
        """card-sessions "A landing's session opens what the bolt brings to main, as one review": two units and a chore,
        each unit's Markdown named for it in a change's reading order, the diff numbered after the last unit."""
        a = [("tasks.md", "a's tasks"), ("specs/x/spec.md", "a's spec"), ("proposal.md", "a's proposal"), ("design.md", "a's design")]
        b = [("proposal.md", "b's proposal")]
        files = plan.landing_reading("y", "switchboard-kit", "def5678" + "0" * 33, ["a", "b"], ["c"], [("a", a), ("b", b)],
                                     "diff --git a/x b/x\n")
        assert [n for n, _ in files] == ["00-y.md", "01-a-proposal.md", "01-a-design.md", "01-a-specs-x-spec.md", "01-a-tasks.md",
                                         "02-b-proposal.md", "03-y-diff.txt"]
        assert files[1][1] == "a's proposal" and files[-1][1] == "diff --git a/x b/x\n"

    def test_a_bolt_of_chores_alone_reads_as_its_cover_and_its_diff(self):
        files = plan.landing_reading("y", "k", "def5678", [], ["c", "d"], [], "diff --git a/x b/x\n")
        assert [n for n, _ in files] == ["00-y.md", "01-y-diff.txt"]
        assert plan.landing_reading("y", "k", "def5678", [], ["c"], [], "")[-1][1] == (
            "The bolt changes nothing against main outside its change folders.\n")

    def test_the_cover_names_every_unit_and_chore_and_says_the_reading_lands_nothing(self):
        cover = plan.landing_reading("y", "switchboard-kit", "def5678" + "0" * 33, ["a", "b"], ["c"],
                                     [("a", [("proposal.md", "")]), ("b", [("proposal.md", "")])], "")[0][1]
        assert cover.startswith("# Bolt y, landing on switchboard-kit's main\n\nWhat lands, at its head def5678:\n\n- a\n- b\n- c (chore)\n")
        assert "This reading lands nothing: approving the landing card is the word to land" in cover
        assert "reaches the bolt's conductor as notes on the landing card, and a note naming a defect holds the landing for a fix" in cover

    def test_a_landings_reading_is_written_into_its_heads_folder_from_the_kit_at_the_head(self, monkeypatch, tmp_path):
        """card-sessions "A bolt of two units and a chore": each unit's change read at the head, and the diff from where
        the bolt last met main to its head, less the change folders."""
        held = {"a": [("proposal.md", "a's proposal")], "b": [("tasks.md", "b's tasks"), ("proposal.md", "b's proposal")]}
        asked = []
        monkeypatch.setattr(plan, "change_held", lambda main, ref, u: asked.append((main, ref, u)) or held.get(u))
        monkeypatch.setattr(plan, "kit_git", lambda fleet, t, where, *args: asked.append((where, *args)) or (0, "diff --git a/x b/x"))
        fleet = {"teams": {"swb-1": {"name": "swb-1", "machine": "box", "kit": {"main": "/kit/main"}}}}
        f = dict(bolt="y", kit="switchboard-kit", units=["a", "b"], chores=["c"], head="def5678" + "0" * 33, base="abc1234",
                 team="swb-1", host="box")
        folder = tmp_path / "def5678"
        folder.mkdir()
        (folder / "01-old-proposal.md").write_text("an older head's")
        paths = plan.landing_write(fleet, f, folder)
        assert [pathlib.Path(p).name for p in paths] == ["00-y.md", "01-a-proposal.md", "02-b-proposal.md", "02-b-tasks.md", "03-y-diff.txt"]
        assert sorted(p.name for p in folder.iterdir()) == sorted(pathlib.Path(p).name for p in paths)
        assert (folder / "03-y-diff.txt").read_text() == "diff --git a/x b/x\n"
        assert asked[:2] == [("/kit/main", f["head"], "a"), ("/kit/main", f["head"], "b")]
        assert asked[2] == ("/kit/main", "diff", "--no-color", "--no-ext-diff", "abc1234", f["head"], "--", ".", ":(exclude)openspec/changes")

    def test_a_unit_whose_change_the_head_does_not_hold_refuses_and_nothing_is_written(self, monkeypatch, tmp_path):
        monkeypatch.setattr(plan, "change_held", lambda main, ref, u: None)
        monkeypatch.setattr(plan, "kit_git", lambda *a: pytest.fail("the diff was read after a change crew could not read"))
        fleet = {"teams": {"swb-1": {"name": "swb-1", "machine": "box", "kit": {"main": "/kit/main"}}}}
        f = dict(bolt="y", kit="k", units=["a"], chores=[], head="def5678" + "0" * 33, base="abc1234", team="swb-1", host="box")
        with pytest.raises(plan.Refusal, match="unit a's change is not on bolt y at def5678, open or archived, in /kit/main on box"):
            plan.landing_write(fleet, f, tmp_path / "def5678")
        assert not (tmp_path / "def5678").exists()

    def test_a_proven_bolts_card_waits_on_its_batches_and_says_which(self):
        """briefs.12, as crew card session land/<bolt> says why the bolt has no card yet."""
        assert plan.batch_waits(["a", "b", "c"], {"a"}, {"b": 7, "c": 8}) == (
            "a has not been in a batch, which is due; the user has not answered batches 7 and 8")
        assert plan.batch_waits(["a", "b"], {"a", "b"}, {}) == "a or b have not been in a batch, which is due"
        assert plan.batch_waits(["a"], set(), {"a": 7}) == "the user has not answered batch 7"
        assert plan.batch_waits(["a"], set(), {"q": 7}) is None

    def test_which_act_follows_each_event(self):
        assert plan.landing_act("proven", head="abc1234" + "0" * 33) == ("change", "Its head is now abc1234")
        assert plan.landing_act("fix", words="The zone list misses one zone.") == ("close", None, "held for a fix: The zone list misses one zone.")
        assert plan.landing_act("landed", words="landed on GitHub's main at c0ffee1 (#3); every host's folder follows") == (
            "close", "landed on GitHub's main at c0ffee1 (#3); every host's folder follows", None)


class TestThePreview:
    """A landing's card lists the addresses of a preview of the bolt's head when the kit declares one, follows the head
    with it, says one that failed, and releases it when the card closes (rail-cards, record 0031 §3)."""
    HEAD, NEW = "abc1234" + "0" * 33, "def5678" + "0" * 33

    @pytest.mark.parametrize("declared, recorded, listed, alive, step", [
        (False, None, False, False, "none"),
        (True, None, False, False, "ask"),
        (True, HEAD, True, False, "keep"),
        (True, HEAD, False, True, "keep"),
        (True, HEAD, False, False, "ask"),
        (True, NEW, True, True, "replace"),
        (False, HEAD, True, False, "release"),
        (False, NEW, False, False, "release"),
    ])
    def test_what_crew_does_with_the_preview_at_each_raise(self, declared, recorded, listed, alive, step):
        """"Asked again with nothing changed": the recorded preview of the head kept, nothing asked; "The head moves":
        the old head's replaced; a kit that declares none asks nothing."""
        assert plan.preview_step(declared, recorded, self.HEAD, listed, alive) == step

    @pytest.mark.parametrize("shown, outcome, note", [
        ("addresses", "failed", "Its preview of abc1234 did not come up"),
        ("reason", "up", "Its preview of abc1234 is up"),
        ("addresses", "up", None),
        ("reason", "failed", None),
    ])
    def test_a_previews_end_changes_the_card_only_when_it_changes_what_the_card_says(self, shown, outcome, note):
        """"The stack fails to come up" and "The host is busy when the card is raised"."""
        assert plan.preview_change(shown, outcome, self.HEAD) == note

    def test_a_previews_end_is_a_change_of_the_card_in_its_words(self):
        assert plan.landing_act("preview", head=self.HEAD, words="Its preview of abc1234 is up") == ("change", "Its preview of abc1234 is up")

    LISTED = [
        {"name": "preview/0123456789ab", "branch": "main", "revision": HEAD, "state": "up", "addresses": {"web": "http://w"}},
        {"name": "preview/aaaaaaaaaaaa", "branch": "bolt/y", "revision": NEW, "state": "up", "addresses": {"web": "http://n"}},
        {"name": "preview/bbbbbbbbbbbb", "branch": "bolt/y", "revision": HEAD, "state": "starting", "made": "2026-10-19T10:00:00Z",
         "addresses": {"web": "http://web-abc1234--bolt-y--kit.localhost:4321", "api": "http://api-abc1234--bolt-y--kit.localhost:4322"}},
    ]

    def test_the_heads_preview_is_the_entry_sluice_lists_for_the_bolts_branch_and_its_head(self):
        assert plan.preview_listed(self.LISTED, "bolt/y", self.HEAD) == dict(
            head=self.HEAD, name="preview/bbbbbbbbbbbb", state="starting",
            addresses={"web": "http://web-abc1234--bolt-y--kit.localhost:4321", "api": "http://api-abc1234--bolt-y--kit.localhost:4322"})
        assert plan.preview_listed(self.LISTED, "bolt/z", self.HEAD) is None and plan.preview_listed([], "bolt/y", self.HEAD) is None

    def test_a_failed_preview_carries_sluices_output(self):
        failed = [dict(self.LISTED[2], state="failed", output="building web\nerror: port 4321 in use\n")]
        assert plan.preview_listed(failed, "bolt/y", self.HEAD)["output"] == "building web\nerror: port 4321 in use\n"
        assert plan.preview_listed([dict(failed[0], output=None)], "bolt/y", self.HEAD)["output"] == ""

    @pytest.mark.parametrize("doc, said", [
        ({"previews": []}, "sluice's previews are no list crew reads"),
        (["preview/0123456789ab"], "sluice lists a preview crew can't read"),
        ([LISTED[0], None], "sluice lists a preview crew can't read"),
        ([dict(LISTED[2], state="booting")], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
        ([dict(LISTED[2], name=7)], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
        ([dict(LISTED[2], addresses={"web": None})], "sluice lists a preview of bolt/y at abc1234 crew can't read"),
    ])
    def test_a_list_crew_cannot_read_is_refused(self, doc, said):
        with pytest.raises(plan.Refusal) as e:
            plan.preview_listed(doc, "bolt/y", self.HEAD)
        assert str(e.value).startswith(said)

    @pytest.mark.parametrize("code, out, err, ended", [
        (0, '{"name": "preview/0123456789ab", "state": "up", "addresses": {"web": "http://w"}}', "", {"state": "up"}),
        (1, '{"name": "preview/0123456789ab", "state": "failed", "output": "building\\nerror: port 4321 in use\\n"}', "",
         {"state": "failed", "why": "building / error: port 4321 in use"}),
        (2, '{"error": {"kind": "refused", "message": "abc1234 has no [preview] table in .config/sluice.toml", "next": []}}', "",
         {"state": "failed", "why": "abc1234 has no [preview] table in .config/sluice.toml"}),
        (2, "", "error: unrecognized subcommand 'preview'\n\nUsage: sluice <COMMAND>\n", {"state": "failed", "why": "Usage: sluice <COMMAND>"}),
        (137, "", "", {"state": "failed", "why": "sluice exited 137"}),
    ])
    def test_how_sluices_preview_ended_is_read_from_its_exit_and_its_words(self, code, out, err, ended):
        """"The stack fails to come up" and "The host's sluice has no preview command"."""
        assert plan.preview_ended(code, out, err) == ended

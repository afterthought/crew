"""A flywheel's lineage page and its dev sites (the crew-page and crew-sites specs): page.data on the run record's
entries, page.labelled and page.from_entries for each node's label and status, page.render, page.header and page.nav for
the file; sites.url_of for where a worktree's dev server opens from here. That crew page writes the file whole from the
branch and the board's read, and crew sites reads every host, are the board journey's (t-journey-board)."""
import json
import re

import pytest

from facts import plan_text

import page
import plan
import record
import sites
from crew import Refusal

N = iter(range(1, 1000))


def entry(act, on=(), frm=(), why=None, minutes=0, **f):
    return dict(Id=f"2026101210{next(N):04d}-mac-studio-1-1", At=f"2026-10-12T10:{minutes:02d}:00Z", Act=act, On=list(on), From=list(frm),
                Why=why or f"{act}", **f)


FLOW = [entry("capture", ["signals/a"], minutes=1), entry("signal.move", ["signals/a", "agenda/8"], minutes=2),
        entry("plan.propose", ["proposal/3", "unit/u", "bolt/b"], minutes=3), entry("unit.add", ["unit/u", "bolt/b"], ["agenda/8", "proposal/3"], minutes=4),
        entry("bolt.land", ["bolt/b", "unit/u"], why="plan(b): land the bolt", minutes=5), entry("capture", ["signals/z"], minutes=6),
        entry("tell", ["agent/wldn-planner"], minutes=7, Chars="5")]


class TestData:
    def test_linked_nodes_in_the_flows_order_each_edge_once_with_the_entries_that_made_it(self):
        d = page.data(FLOW)
        assert [n["id"] for n in d["nodes"]] == ["signals/a", "signals/z", "agenda/8", "proposal/3", "unit/u", "bolt/b"]
        assert sorted(f"{e['from']}>{e['to']}" for e in d["edges"]) == ["agenda/8>proposal/3", "proposal/3>unit/u", "signals/a>agenda/8", "unit/u>bolt/b"]
        assert next(len(e["entries"]) for e in d["edges"] if e["from"] == "proposal/3") == 2
        assert len(d["entries"]) == 7 and sorted(d["histories"]) == ["agenda/8", "bolt/b", "proposal/3", "signals/a", "signals/z", "unit/u"]

    def test_a_move_draws_a_line_to_the_bolt_it_moved_to_and_none_from_the_one_it_left(self):
        d = page.data([entry("unit.move", ["unit/v", "bolt/c"], ["bolt/b"])])
        assert [f"{e['from']}>{e['to']}" for e in d["edges"]] == ["unit/v>bolt/c"]

    def test_a_proposals_entries_join_only_the_proposal_to_each_unit_it_names(self):
        es = [entry(a, ["proposal/4", "unit/x", "bolt/e", "unit/y", "bolt/f"]) for a in ("plan.propose", "plan.approve")]
        es += [entry("unit.add", ["unit/x", "bolt/e"], ["proposal/4"]), entry("unit.add", ["unit/y", "bolt/f"], ["proposal/4"])]
        d = page.data(es)
        assert sorted(f"{e['from']}>{e['to']}" for e in d["edges"] if e["to"].startswith("bolt/")) == ["unit/x>bolt/e", "unit/y>bolt/f"]
        assert sorted(f"{e['to']}:{len(e['entries'])}" for e in d["edges"] if e["from"] == "proposal/4") == ["unit/x:3", "unit/y:3"]

    def test_since_keeps_the_entries_from_then_on(self):
        d = page.data(FLOW, "2026-10-12T10:05:00Z")
        assert [n["id"] for n in d["nodes"]] == ["signals/z", "unit/u", "bolt/b"] and len(d["entries"]) == 3


class TestDeploys:
    S1, S2 = "a" * 40, "b" * 40

    def es(self):
        S1, S2 = self.S1, self.S2
        return FLOW[:4] + [entry("bolt.land", ["bolt/b", "unit/u"], minutes=5, Host="box", Repo="switchboard-kit", Head=S1),
                           entry("ops.offer", ["env/mac-studio"], minutes=6, Host="mac-studio", Head=S1, Base="none"),
                           entry("ops.approve", ["env/mac-studio"], minutes=7, Host="mac-studio", Head=S1, By="wldn-ops"),
                           entry("ops.deploy", ["env/mac-studio"], minutes=8, Host="mac-studio", Head=S1, Base="none", Phase="start"),
                           entry("ops.deploy", ["env/mac-studio"], minutes=9, Host="mac-studio", Head=S1, Phase="end", Outcome="done"),
                           entry("ops.offer", ["env/mac-studio"], minutes=10, Host="box", Head=S2, Base=S1)]

    def test_each_environments_deploys_carry_their_bolts_with_their_changes_proposals_as_release_notes(self):
        d = page.data(self.es())
        page.labelled(d, plan.Plan(""), None, {"3": {"Case": "Zones get a bolt.\nWhy: x"}}, {}, {}, lambda name: None)
        env, = page.deploys(d, self.es(), "mac-studio")
        dep, = env["deploys"]
        assert (env["env"], dep["to"], dep["answer"], dep["word"]["by"], dep["outcome"]) == ("mac-studio", self.S1, "approved", "wldn-ops", "done")
        assert dep["notes"] == [{"bolt": "b", "proposals": [{"proposal": "3", "label": "Zones get a bolt."}]}]

    def test_an_ops_entry_only_the_main_levels_host_wrote_is_a_deploy_and_since_keeps_what_moved_from_then_on(self):
        d = page.data(self.es())
        assert [x["to"] for e in page.deploys(d, self.es(), "mac-studio") for x in e["deploys"]] == [self.S1]
        assert [x["to"] for e in page.deploys(d, self.es(), "box") for x in e["deploys"]] == [self.S2]
        assert page.deploys(d, self.es(), "mac-studio", "2026-10-12T10:30:00Z") == [{"env": "mac-studio", "deploys": [], "waiting": []}]


class TestLabels:
    def test_each_node_is_labelled_from_the_state_and_one_the_state_no_longer_holds_from_its_entries(self):
        d = page.data(FLOW + [entry("unit.drop", ["unit/d", "bolt/tenant-environments"], why="plan(tenant-environments): drop d")])
        pl = plan.Plan(plan_text(bolts=[("tenant-environments", "switchboard-kit", "swb-1")], units=[]))

        class St:
            def of(self, name):
                return {"stage": "code"}

            def bolt_state(self, b):
                return "active"
        proposals = {"3": plan.Rec("Proposal", [("Proposal", "3"), ("Case", "The console gets a bolt.\nMore."), ("State", "open")])}
        items = {"8": plan.Rec("Item", [("Item", "8"), ("Lane", "plan"), ("Subject", "Plans are checked."), ("State", "open")])}
        moves = {"a": plan.Rec("Move", [("Signal", "a"), ("Move", "route")])}
        page.labelled(d, pl, St(), proposals, items, moves, lambda name: "Plans should be\nchecked." if name == "a" else None)
        by = {n["id"]: n for n in d["nodes"]}
        assert [by["signals/a"][k] for k in ("label", "status", "facts")] == ["Plans should be checked.", "done", ["route"]]
        assert [by["agenda/8"][k] for k in ("label", "status", "facts")] == ["Plans are checked.", "open", ["plan", "open"]]
        assert [by["proposal/3"][k] for k in ("label", "status")] == ["The console gets a bolt.", "open"]
        assert [by["bolt/b"][k] for k in ("label", "status", "gone")] == ["plan(b): land the bolt", "done", True]
        assert [by["unit/d"][k] for k in ("label", "status")] == ["plan(tenant-environments): drop d", "dropped"]
        assert by["signals/z"]["gone"] is True and by["signals/z"]["status"] is None


class TestFile:
    D = dict(page.data([entry("capture", ["signals/x"], why="Ends </script><b>here</b> & more.")]), label="wldn", partitions=["wldn", "madswan"],
             made={"at": "2026-10-12T10:00:00Z", "label": "wldn", "commit": "a" * 40, "plan": "a" * 40})

    def test_the_data_is_one_block_that_typed_text_cannot_end_and_nothing_loads_from_outside_the_file(self):
        self.D["nodes"][0]["label"] = "Ends </script><b>here</b> & more."
        out = page.render(self.D)
        block, = re.findall(r'<script type="application/json" id="data">(.*?)</script>', out, re.S)
        assert json.loads(block)["nodes"][0]["label"] == "Ends </script><b>here</b> & more."
        rest = out.replace(block, "")
        for no in ("<script src", "<link", "@import", "http://", "https://", "src=", "url(", "{{DATA}}", "innerHTML"):
            assert no not in rest
        assert '<body data-view="board">' in rest and "prefers-color-scheme" in rest

    def test_the_header_names_every_partition_its_own_current_and_each_other_linked(self):
        assert page.nav(["wldn", "madswan"], "wldn") == '<span class="part" aria-current="page">wldn</span><a class="part" href="../madswan/page.html">madswan</a>'

    def test_it_says_as_of_when_and_which_commit_and_both_when_the_board_read_another(self):
        assert page.header(self.D["made"]) == "as of 2026-10-12 10:00Z · wldn/main aaaaaaa"
        assert page.header(dict(self.D["made"], plan="b" * 40)).endswith("for the run record, bbbbbbb for the board and labels")


class TestSites:
    FLEET = {"hosts": {"mac-studio": {"kind": "darwin"}, "chuck-herdr-alpha": {"kind": "nixos"}}}
    SITE = {"here": "https://unit-a--kit.local", "tailnet": "https://unit-a--kit--studio.dev.swancloud.net"}
    ROUTES = [{"name": "unit-a--kit", "url": "https://unit-a--kit.local"}]

    def test_a_server_running_here_opens_by_its_local_name(self):
        assert sites.url_of(self.FLEET, "mac-studio", "mac-studio", self.SITE, self.ROUTES) == ("https://unit-a--kit.local", None)

    def test_another_hosts_opens_by_its_tailnet_name_from_a_mac_only(self):
        assert sites.url_of(self.FLEET, "mac-studio", "chuck-herdr-alpha", self.SITE, self.ROUTES) == (self.SITE["tailnet"], None)
        assert sites.url_of(self.FLEET, "chuck-herdr-alpha", "mac-studio", self.SITE, self.ROUTES) == (self.SITE["tailnet"], "open from a Mac")

    def test_none_where_none_runs_or_is_published(self):
        assert sites.url_of(self.FLEET, "mac-studio", "mac-studio", self.SITE, []) == (None, None)
        assert sites.url_of(self.FLEET, "chuck-herdr-alpha", "mac-studio", {"here": self.SITE["here"]}, self.ROUTES) == (
            None, "running, but mac-studio does not publish its dev servers")
        assert sites.url_of(self.FLEET, "mac-studio", "mac-studio", self.SITE, None) == (None, "portless did not answer")


class TestMore:
    def test_a_unit_and_bolt_whose_host_does_not_answer_have_no_stage_or_status(self):
        d = page.data([entry("unit.add", ["unit/a", "bolt/tenant-environments"])])
        pl = plan.Plan(plan_text(bolts=[("tenant-environments", "switchboard-kit", "swb-1")], units=[("a", "switchboard-kit", "tenant-environments", [])]))

        class Unknown:
            def of(self, name):
                return {"stage": "unknown"}

            def bolt_state(self, b):
                return "unknown"
        page.labelled(d, pl, Unknown(), {}, {}, {}, lambda name: None)
        by = {n["id"]: n for n in d["nodes"]}
        assert [by["unit/a"].get(k) for k in ("label", "stage", "status")] == ["Unit a.", None, None]
        assert [by["bolt/tenant-environments"].get(k) for k in ("status", "team")] == [None, "swb-1"]

    def test_the_page_opens_on_the_board_in_the_mockups_forms_with_a_phone_layout_and_the_teams_to_narrow_it_to(self):
        rest = re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D), flags=re.S)
        for lane in ("Inception", "Bolt plan", "Construction", "Operation"):
            assert f'aria-label="{lane}"' in rest
        for has in ("@media (max-width:759px)", "prefers-color-scheme:dark", ':root[data-theme="dark"]', "repeating-linear-gradient",
                    "design/flywheel-next/mockups/rail-and-board.html", 'id="team"', "history.replaceState", '"crew-page:" + D.label',
                    'id="hide"', 'id="find"', 'id="bars"', "Nothing has been recorded"):
            assert has in rest
        for form in (".quote", ".sheet", ".slip", ".ledger", ".record", ".mark.attention", ".lg-unit.building"):
            assert form in rest
        for deploys in ('aria-label="Deploys"', 'data-view="deploys"', "D.deploys", "B.environments", ".dp-line", "release notes"):
            assert deploys in rest
        for sample in ("atlas", "plan-decisions", "books", "Manrope", "JetBrains Mono"):
            assert sample not in rest

    def test_a_marker_whose_rows_post_was_refused_says_so_with_pending_yous_words_in_its_title(self):
        """board-page "A deploy whose card was refused": the marker says it has no card, its post refused, and pointing
        at it shows the words the board's read gives it (board.marker's refused)."""
        rest = re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D), flags=re.S)
        assert 'k.refused ? "no card, its post refused" : "no card"' in rest
        assert 's.title = !k.card && k.refused ? k.key + ": " + k.refused : k.key;' in rest

    def test_the_page_is_written_whole_over_the_last_one_leaving_no_temporary_file(self, tmp_path):
        out = tmp_path / "wldn" / "page.html"
        page.write(out, "one")
        page.write(out, "two")
        assert out.read_text() == "two" and [p.name for p in out.parent.iterdir()] == ["page.html"]

    def test_since_takes_a_date_a_time_today_or_days_and_refuses_anything_else(self):
        assert record.when("2026-10-06T14:00:00Z") == ("2026-10-06", "2026-10-06T14:00:00Z")
        with pytest.raises(Refusal, match="--since takes a date"):
            record.when("yesterday-ish")


def test_a_chore_stands_in_the_units_column_its_move_drawn_as_a_units_and_labelled_by_its_words():
    """page.data and page.labelled: a chore is work like a unit, so it is in the units' column, where it moved from is not
    what it came from, and its label and stage are read from the plan and its kit (plan.11)."""
    d = page.data([entry("chore.add", ["chore/bump", "queue/switchboard-kit"]), entry("chore.move", ["chore/bump", "bolt/c"], ["bolt/b"])])
    assert page.column("chore/bump") == page.column("unit/u")
    assert [f"{e['from']}>{e['to']}" for e in d["edges"]] == ["chore/bump>bolt/c"]
    pl = plan.Plan(plan_text(bolts=[("c", "switchboard-kit", "swb-1")], units=[("bump", "switchboard-kit", "c", [], "chore")]))

    class St:
        def of(self, name):
            return {"stage": "verify"}

        def bolt_state(self, b):
            return "active"
    page.labelled(d, pl, St(), {}, {}, {}, lambda name: None)
    by = {n["id"]: n for n in d["nodes"]}
    assert [by["chore/bump"][k] for k in ("label", "status", "stage")] == ["Chore bump.", "flight", "verify"]

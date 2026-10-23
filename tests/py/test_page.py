"""A flywheel's lineage page and its dev sites (the crew-page and crew-sites specs): page.data on the run record's
entries, page.labelled and page.from_entries for each node's label and status, page.render, page.header, page.nav and
page.beside for the file; sites.url_of for where a worktree's dev server opens from here. That crew page writes the file
whole from the branch and the board's read, and crew sites reads every host, are the board journey's (t-journey-board)."""
import json
import re
from pathlib import PurePath

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
        out = page.render(self.D, PurePath("/s/wldn/page.html"))
        block, = re.findall(r'<script type="application/json" id="data">(.*?)</script>', out, re.S)
        assert json.loads(block)["nodes"][0]["label"] == "Ends </script><b>here</b> & more."
        rest = out.replace(block, "")
        for no in ("<script src", "<link", "@import", "http://", "https://", "src=", "url(", "{{DATA}}", "innerHTML"):
            assert no not in rest
        assert '<body data-view="board">' in rest and "prefers-color-scheme" in rest

    def test_the_header_names_every_partition_its_own_current_and_each_other_linked_in_crews_layout(self):
        """board-page "Three partitions": a page in crew's folder layout links each other partition's folder beside it."""
        assert page.nav(["wldn", "madswan"], "wldn", PurePath("/s/wldn/page.html")) == (
            '<span class="part" aria-current="page">wldn</span><a class="part" href="../madswan/page.html">madswan</a>')

    def test_a_page_named_for_its_partition_links_the_others_beside_it_as_they_are_served(self):
        """board-page "Pages written side by side as they are served": <label>.html links <other>.html."""
        assert page.beside(PurePath("/w/wldn.html"), "wldn", "madswan") == "madswan.html"
        assert '<a class="part" href="madswan.html">madswan</a>' in page.nav(["wldn", "madswan"], "wldn", PurePath("/w/wldn.html"))

    def test_a_folder_and_a_file_both_named_for_the_partition_swap_both(self):
        """board-page "A folder and a file both named for the partition"."""
        assert page.beside(PurePath("/s/wldn/wldn.html"), "wldn", "madswan") == "../madswan/madswan.html"

    def test_a_page_whose_file_and_folder_name_no_partition_names_the_others_unlinked(self):
        """board-page "A page written where its layout names no partition": crew cannot tell where the others are, so
        it links none (read.1); a name that only contains the label does not name it."""
        for path in ("/s/board.html", "/s/x/page.html", "/s/wldn-board.html"):
            assert page.beside(PurePath(path), "wldn", "madswan") is None
            assert page.nav(["wldn", "madswan"], "wldn", PurePath(path)) == (
                '<span class="part" aria-current="page">wldn</span><span class="part">madswan</span>')

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
        rest = re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D, PurePath("/s/wldn/page.html")), flags=re.S)
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
        rest = re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D, PurePath("/s/wldn/page.html")), flags=re.S)
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


class TestDocks:
    """board-page: every item the page draws opens a dock with what the page's data and lineage hold of it (page.docks),
    on the board of test_board's fixture: a signal, a proposal waiting with its card open, a planned bolt and a queued
    unit, tenant-environments held by swb-1 with a in code and a fix, atlas-maps landed by atl-1 and deployed to
    mac-studio, a newer deploy waiting on the word, and operations waiting on the environment."""
    SIG = "2026-10-01-planning/01-zones"

    @pytest.fixture(autouse=True)
    def here(self, monkeypatch):
        import crew
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")

    def fleet(self):
        import copy
        from test_board import BOX, FLEET
        f = copy.deepcopy(FLEET)
        f["hosts"][BOX]["sessions"] = {"crew-a": {"account": "madswan-2"}, "crew-b": {"account": "madswan-2"}, "brd": {}}
        f["hosts"]["mac-studio"]["sessions"] = {"wldn": {"account": "madswan-2"}, "atlas": {"account": "willdan"}}
        for t, s in (("swb-1", "crew-a"), ("swb-2", "crew-b"), ("brd-1", "brd"), ("atl-1", "atlas")):
            f["teams"][t]["session"] = s
        f["partitions"]["wldn"]["sessions"] = {r: "wldn" for r in ("design", "planner", "ops", "operator", "reviewer")}
        return f

    def paged(self, label=None):
        import datetime
        from test_board import NOW, OPS, SIGS, WAITS, data
        card = dict(label="wldn", card="req_2", key="proposal/2", by="wldn-planner", host="mac-studio", at=NOW)
        landing = dict(label="wldn", bolt="atlas-maps", units=["map-one"], at=NOW - datetime.timedelta(hours=1), by="chuck@mac-studio", host="mac-studio")
        bd = data(signals=SIGS, props=WAITS, cards=[card], entries=OPS, landings=[landing], gives={("wldn", "atlas-maps"): "atl-1"})
        lineage = [entry("capture", [f"signals/{self.SIG}"], why="captured"), entry("plan.propose", ["proposal/2", "unit/d", "bolt/tenant-environments"]),
                   entry("unit.add", ["unit/a", "bolt/tenant-environments"], ["signals/" + self.SIG]), entry("unit.add", ["unit/d", "bolt/tenant-environments"], ["proposal/2"]),
                   entry("bolt.land", ["bolt/atlas-maps", "unit/map-one"], minutes=5), entry("unit.add", ["unit/x", "bolt/c"], ["agenda/8"])]
        d = page.data(lineage + OPS)
        for n in d["nodes"]:
            n["label"] = label if n["id"] == f"signals/{self.SIG}" and label else n.get("label")
        d["board"] = dict(bd["partitions"][0], read_at=bd["read_at"], unread=bd["unread"])
        d["deploys"] = page.deploys(d, OPS, "mac-studio")
        d["docks"] = page.docks(d, self.fleet(), "wldn")
        return d

    def test_every_item_of_each_kind_and_every_team_carries_the_key_of_a_dock_the_page_holds(self):
        """board-page "Every item has its dock"."""
        d = self.paged()
        B = d["board"]
        drawn = list(page.walk(B, d["deploys"]))
        assert drawn and all(x["dock"] in d["docks"] for x in drawn)
        kinds = {d["docks"][x["dock"]]["kind"] for x in drawn}
        assert kinds == {"signal", "proposal", "bolt", "unit", "fix", "landing", "deploy", "operation", "team"}
        assert [t["dock"] for t in B["teams"]] == ["team:swb-1", "team:swb-2", "team:brd-1", "team:atl-1"]
        assert B["bolt_plan"]["planned"][0]["dock"] == "bolt:apex-zones" and B["bolt_plan"]["queue"][0]["dock"] == "unit:zone-two"
        assert B["construction"][0]["fixes"][0]["dock"] == "fix:tenant-environments/edge"

    def test_a_units_dock_in_a_ledger_says_its_bolt_as_a_link_its_stage_its_tasks_and_its_slot(self):
        """board-page "A unit being built"."""
        a = self.paged()["docks"]["unit:a"]
        assert (a["kind"], a["title"], a["tail"], a["form"]) == ("unit", "a", "unit · in tenant-environments", None)
        facts = {f[0]: f[1:] for f in a["facts"]}
        assert facts["bolt"] == ["tenant-environments", "bolt:tenant-environments"]
        assert (facts["stage"], facts["tasks"], facts["slot"]) == (["code"], ["1 of 2 tasks"], ["unit-1"])
        assert facts["server"] == ["https://unit-a--switchboard-kit--box.dev"]

    def test_the_same_deploy_from_the_operation_lane_and_the_deploys_view_has_one_key(self):
        """board-page "A deploy from either view"."""
        from test_board import S1, S2
        d = self.paged()
        lane = [x["dock"] for e in d["board"]["environments"] for x in e["deploys"]]
        view = [x["dock"] for e in d["deploys"] for x in e["deploys"]]
        assert sorted(lane) == sorted(view) and len(set(lane)) == 2
        assert all(k.startswith(f"deploy:mac-studio/{s}/") for k, s in zip(lane, (S2, S1)))

    def test_a_key_names_its_item_not_its_lane(self):
        assert [page.key_of(n) for n in ("signals/2026-10-12-x/01", "proposal/3", "unit/a", "chore/bump", "bolt/b", "agenda/8")] == [
            "signal:2026-10-12-x/01", "proposal:3", "unit:a", "unit:bump", "bolt:b", None]
        d = self.paged()
        queued = d["board"]["bolt_plan"]["queue"].pop()
        d["board"]["bolt_plan"]["planned"][0]["units"].append(dict(queued, stage="ready"))
        assert "unit:zone-two" in page.docks(d, self.fleet(), "wldn") and d["board"]["bolt_plan"]["planned"][0]["units"][-1]["dock"] == "unit:zone-two"

    def test_a_link_is_set_only_where_a_dock_is_and_an_agenda_item_is_named_as_text(self):
        """board-page "A dock links the items it names"."""
        d = self.paged()
        keys = [r["key"] for p in d["docks"].values() for part in p["parts"] for r in part["rows"] if "key" in r]
        keys += [f[2] for p in d["docks"].values() for f in p["facts"] if len(f) > 2]
        assert keys and all(k in d["docks"] for k in keys)
        x = next(n for n in d["nodes"] if n["id"] == "unit/x")
        assert page.key_of(x["id"]) not in d["docks"]

    def test_a_signals_dock_holds_its_whole_assertion_kind_who_captured_it_when_and_its_history_as_crew_trace_walks_it(self):
        """board-page "A signal's history"."""
        d = self.paged(label="Every apex should be a zone of its own, whatever its tenants say.")
        s = d["docks"][f"signal:{self.SIG}"]
        assert (s["title"], s["tail"].split(" · ")[:2]) == ("Every apex should be a zone of its own.", ["ask", "captured by wldn-planner"])
        assert s["tail"].endswith(" ago")
        assert {f[0]: f[1] for f in s["facts"]} == {"signal": self.SIG, "kind": "ask", "captured by": "wldn-planner", "captured": "2026-10-01", "home": "blueprints"}
        assert s["parts"][0] == {"title": "assertion", "rows": [{"text": "Every apex should be a zone of its own, whatever its tenants say."}]}
        assert s["history"] == d["histories"][f"signals/{self.SIG}"] and d["entries"][s["history"][0]]["Act"] == "capture"
        assert {"text": "unit a", "key": "unit:a"} in next(p["rows"] for p in s["parts"] if p["title"] == "linked")

    def test_a_proposal_waiting_is_a_sheet_carrying_its_card_and_no_control_that_approves_it(self):
        """board-page "A proposal waiting"."""
        p = self.paged()["docks"]["proposal:2"]
        assert (p["form"], p["title"], p["tail"]) == ("sheet", "Tenants get d.", "proposal 2 · by wldn-planner · opened 2026-10-12")
        assert p["facts"] == [["waiting on", "swb-1-conductor"]]
        assert [(m["glyph"], m["card"]["by"]) for m in p["markers"]] == [("✓", "wldn-planner")]
        assert {"title": "units and bolts", "rows": [{"text": "unit d"}]} in p["parts"]
        assert {"title": "teams", "rows": [{"text": "swb-1", "key": "team:swb-1"}]} in p["parts"]

    def test_a_held_bolts_dock_is_a_ledger_of_its_units_and_fixes_and_a_planned_ones_says_no_team(self):
        d = self.paged()
        b = d["docks"]["bolt:tenant-environments"]
        assert (b["form"], b["title"], b["tail"]) == ("ledger", "tenant-environments", "switchboard-kit · swb-1 on chuck-herdr-alpha · active")
        assert ["team", "swb-1", "team:swb-1"] in b["facts"]
        units = next(p["rows"] for p in b["parts"] if p["title"] == "units")
        assert units == [{"text": "a · code 1/2", "key": "unit:a"}, {"text": "b · planned", "key": "unit:b"}]
        assert next(p["rows"] for p in b["parts"] if p["title"] == "fixes") == [
            {"text": "fix/tenant-environments/edge · not merged", "key": "fix:tenant-environments/edge"}]
        assert b["history"] == d["histories"]["bolt/tenant-environments"]
        z = d["docks"]["bolt:apex-zones"]
        assert (z["tail"], z["markers"]) == ("switchboard-kit · planned, no team", [])

    def test_a_queued_unit_is_a_slip_with_its_sources(self):
        q = self.paged()["docks"]["unit:zone-two"]
        assert (q["form"], q["tail"]) == ("slip", "unit · queued")
        assert {f[0]: f[1] for f in q["facts"]} == {"repository": "switchboard-kit", "stage": "queued", "sources": "docs/zones.md"}

    def test_a_fix_says_whether_it_merged_its_slot_and_server_and_links_its_bolt(self):
        """board-page "A fix"."""
        f = self.paged()["docks"]["fix:tenant-environments/edge"]
        assert (f["title"], f["tail"]) == ("fix/tenant-environments/edge", "fix of tenant-environments")
        assert {x[0]: x[1] for x in f["facts"]} == {"state": "not merged", "slot": "unit-4", "worktree": "/kit/places/fix-edge"}
        assert f["parts"] == [{"title": "bolt", "rows": [{"text": "tenant-environments", "key": "bolt:tenant-environments"}]}]
        assert f["history"] == []

    def test_a_landing_is_a_record_with_its_team_units_the_deploys_carrying_it_and_its_bolt_land_entry(self):
        d = self.paged()
        o = d["docks"]["landing:atlas-maps"]
        at = d["board"]["operation"][0]["at"]
        assert (o["form"], o["title"], o["tail"]) == ("record", "atlas-maps", f"landed {at} by chuck@mac-studio")
        assert ["team", "atl-1", "team:atl-1"] in o["facts"]
        carried = next(p["rows"] for p in o["parts"] if p["title"] == "carried by")
        assert [r["text"] for r in carried] == ["deploy aaaaaaa to mac-studio"]
        assert [d["entries"][i]["Act"] for i in o["history"]] == ["bolt.land", "bolt.land"]

    def test_a_deploys_dock_holds_its_commits_the_word_its_steps_and_the_bolts_it_carried_with_their_proposals(self):
        """board-page "A deploy's release notes"."""
        from test_board import S1
        d = self.paged()
        key = next(x["dock"] for e in d["deploys"] for x in e["deploys"] if x["to"] == S1)
        x = d["docks"][key]
        facts = {f[0]: f[1] for f in x["facts"]}
        assert (x["form"], x["title"], x["tail"]) == ("record", f"deploy {S1[:7]}", "on mac-studio · done")
        assert (facts["to"], facts["from"], facts["outcome"]) == (S1, "nothing deployed", "done")
        assert facts["word"].startswith("approved by wldn-ops, ")
        assert next(p["rows"] for p in x["parts"] if p["title"] == "carried") == [{"text": "bolt atlas-maps", "key": "landing:atlas-maps"}]
        waits = d["docks"][next(k for k in d["docks"] if k.startswith("deploy:") and k != key)]
        assert (waits["tail"], [m["key"] for m in waits["markers"]]) == ("on mac-studio · waits on your word", ["deploy/mac-studio"])

    def test_an_operation_says_where_it_stands_as_the_board_does(self):
        d = self.paged()
        w = d["docks"]["operation:mac-studio/rotate-key"]
        assert (w["form"], w["title"], w["tail"]) == ("record", "rotate-key", "on mac-studio · waits on you")
        assert w["parts"] == [{"title": "text", "rows": [{"text": "Rotate the key."}]}]
        assert [m["key"] for m in w["markers"]] == ["op/mac-studio/2"]
        assert d["docks"]["operation:mac-studio/restart-teams/1"]["tail"] == "on mac-studio · handed to wldn-dispatch-mac-studio"

    def test_a_team_with_no_bolt_shows_its_kits_host_session_and_account_and_says_it_holds_no_bolt(self):
        """board-page "A team with no bolt"."""
        t = self.paged()["docks"]["team:swb-2"]
        assert (t["title"], t["tail"]) == ("swb-2", "switchboard-kit on chuck-herdr-alpha")
        assert t["facts"] == [["kits", "switchboard-kit"], ["host", "chuck-herdr-alpha"], ["session", "crew-b"], ["account", "madswan-2", "subscription:madswan-2"]]
        assert t["parts"][0] == {"title": "bolts held", "rows": [{"text": "holds no bolt"}]}

    def test_a_teams_dock_names_its_bolts_landings_signals_and_the_environment_on_its_host(self):
        d = self.paged()
        assert d["docks"]["team:swb-1"]["parts"][0] == {"title": "bolts held", "rows": [{"text": "tenant-environments", "key": "bolt:tenant-environments"}]}
        parts = {p["title"]: p["rows"] for p in d["docks"]["team:atl-1"]["parts"]}
        assert parts["landings"][0]["key"] == "landing:atlas-maps"
        assert [r["key"] for r in parts["environment mac-studio"]] == [k for k in d["docks"] if k.startswith(("deploy:", "operation:"))]

    def test_an_account_the_hosts_file_does_not_name_is_said_not_named_never_blank(self):
        t = self.paged()["docks"]["team:brd-1"]
        assert ["account", page.NO_ACCOUNT] in t["facts"] and page.NO_ACCOUNT == "no account named in herdr-hosts"

    def test_a_subscriptions_dock_lists_the_partitions_sessions_on_it_teams_and_main_level_agents(self):
        """board-page "Two teams on one account"."""
        d = self.paged()
        s = d["docks"]["subscription:madswan-2"]
        assert (s["title"], s["tail"]) == ("madswan-2", "Claude account")
        assert s["parts"] == [{"title": "sessions on it", "rows": [
            {"text": "swb-1 · chuck-herdr-alpha session crew-a", "key": "team:swb-1"}, {"text": "swb-2 · chuck-herdr-alpha session crew-b", "key": "team:swb-2"}]
            + [{"text": f"wldn-{r} · mac-studio session wldn"} for r in ("design", "planner", "ops", "operator", "reviewer")]}]
        assert [r["text"] for r in d["docks"]["subscription:willdan"]["parts"][0]["rows"]] == ["atl-1 · mac-studio session atlas"]

    def rest(self):
        return re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D, PurePath("/s/wldn/page.html")), flags=re.S)

    def test_the_dock_is_drawn_over_the_board_in_the_mockups_forms_with_no_foot_and_loads_nothing(self):
        """board-page "The dock opens over the board and the board does not move", "On a phone", "The dock answers
        nothing": the dock slides over the board's right on its own layer, fills the screen under 760 px, and has no
        foot; every item opens it by a click, Enter or space, and Esc, × or the scrim closes it."""
        rest = self.rest()
        for has in ('class="dock"', 'role="dialog"', 'aria-modal="false"', 'aria-labelledby="dk-title"', 'class="scrim"', ".dk-h.dk-sheet", ".dk-h.dk-ledger",
                    ".dk-h.dk-record", ".dk-h.dk-slip", "transform:translateX(102%)", "body.docked .dock{transform:none",
                    ".dock{width:100%;position:fixed;top:0;bottom:0;left:0;right:0}", ".dk-h .back.solo{display:inline-flex}",
                    "D.docks", 'ev.key === "Escape"', 'ev.key === "Enter"', 'ev.key === " "', '$("scrim").addEventListener("click", closeDock)',
                    'x.setAttribute("role", "button")', "x.tabIndex = 0", 'el("span", "host tm")', "preventScroll: true", "opener.focus"):
            assert has in rest
        for no in (".dk-f", "innerHTML", "XMLHttpRequest", "WebSocket", "<script src", "<link", "@import", "url("):
            assert no not in rest

    def test_the_open_dock_is_kept_in_the_address_and_a_key_the_page_no_longer_holds_is_dropped(self):
        """board-page "The page is written again", "The item is gone"."""
        rest = self.rest()
        assert 'keep("dock", key)' in rest and 'keep("dock", "")' in rest
        assert "if (f.dock && DOCKS[f.dock]) {" in rest and "if (f.dock) keep(\"dock\", \"\");" in rest
        assert 'if (k !== "dock") store(k, v);' in rest

    def test_a_signals_typed_words_are_kept_as_they_are_in_the_dock_and_the_pages_block(self):
        """board-page "A dock of typed words"."""
        d = self.paged(label="Ends </script><b>here</b> & more.")
        d.update(label="wldn", partitions=["wldn"], made=TestFile.D["made"])
        out = page.render(d, PurePath("/s/wldn/page.html"))
        block, = re.findall(r'<script type="application/json" id="data">(.*?)</script>', out, re.S)
        assert "</script>" not in block
        assert json.loads(block)["docks"][f"signal:{self.SIG}"]["parts"][0]["rows"] == [{"text": "Ends </script><b>here</b> & more."}]


class TestWord:
    """board-page "A word goes to the agent its item's kind names": every dock page names the agent its word goes to
    (page.word_to), on TestDocks's board."""

    @pytest.fixture(autouse=True)
    def here(self, monkeypatch):
        import crew
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")

    def test_each_kinds_word_goes_to_its_agent(self):
        """board-page "Each kind's agent"."""
        d = TestDocks().paged()
        to = {k: p["to"] for k, p in d["docks"].items()}
        deploy = next(k for k in to if k.startswith("deploy:"))
        assert [to[k] for k in ("bolt:tenant-environments", "unit:a", "fix:tenant-environments/edge")] == ["swb-1-conductor"] * 3
        assert [to[k] for k in ("bolt:apex-zones", "unit:zone-one", "unit:zone-two")] == ["wldn-operator"] * 3
        assert (to["proposal:2"], to[f"signal:{TestDocks.SIG}"]) == ("wldn-planner", "wldn-design")
        assert [to[k] for k in ("landing:atlas-maps", deploy, "operation:mac-studio/rotate-key")] == ["wldn-ops"] * 3
        assert [to[k] for k in ("team:swb-1", "subscription:madswan-2")] == ["wldn-operator"] * 2

    def test_every_dock_page_names_its_agent(self):
        d = TestDocks().paged()
        assert d["docks"] and all(p["to"] for p in d["docks"].values())

    def test_every_dock_ends_with_a_word_to_its_agent_posted_to_the_pages_own_address_as_its_one_request(self):
        """board-page "A unit's dock", "Opened from disk", "The dock says what became of the word" and "Only the word is
        posted": the dock's last section names whom the word goes to and that a card is answered on the rail; Send
        posts it to the page's own address, `word`, and says the listener's answer as text, or that it did not answer;
        a page opened from disk sends nothing."""
        rest = TestDocks().rest()
        for has in ('class="word"', 'maxlength="1000"', 'new URL("word", location.href)', '"POST"', "JSON.stringify({ label: D.label, key: key, to: page.to, text: text })",
                    'location.protocol === "file:"', "a card is answered on the rail", "the board's listener did not answer: nothing was sent",
                    "a word is sent only from the served board", "r.status === 200 || r.status === 422", "wordSend.disabled = true", "wordSaid.textContent = words",
                    "if (ok) wordText.value = \"\";", "dkB.append(wordSec)", 'aria-live="polite"'):
            assert has in rest
        assert rest.count("fetch(") == 1
        for no in ("XMLHttpRequest", "WebSocket", "innerHTML", ".dk-f", "sendBeacon", "<form action", "method=\""):
            assert no not in rest

    def test_a_kind_with_no_dock_yet_goes_to_its_role_and_any_other_to_the_operator(self):
        d = TestDocks().paged()
        assert [page.word_to(k, d, "wldn") for k in ("batch:14", "record:0038", "partition:wldn", "unit:nosuch")] == [
            "wldn-planner", "wldn-design", "wldn-operator", "wldn-operator"]


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

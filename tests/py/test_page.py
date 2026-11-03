"""A flywheel's lineage page and its dev sites (the crew-page and crew-sites specs): page.data on the run record's
entries, page.labelled and page.from_entries for each node's label and status, page.page's account of what it was made
from, the branch's entries alone, page.render, page.header, page.nav and page.beside for the file; sites.url_of for
where a worktree's dev server opens from here. That crew page writes the file
whole from the branch and the board's read, and crew sites reads every host, are the board journey's (t-journey-board)."""
import json
import re
from pathlib import PurePath

import pytest

from facts import FLEET, plan_text

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
            fleet = FLEET

            def of(self, name):
                return {"stage": "code"}

            def at(self, b):  # where a started bolt's work runs, as the runner that took it reported (plan.bolt_at)
                return {"machine": "chuck-herdr-alpha"}, None

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
        """board-page "Three partitions": a page in crew's folder layout links the fleet page beside the folders, then
        each other partition's folder beside it."""
        assert page.nav(["wldn", "madswan"], "wldn", PurePath("/s/wldn/page.html")) == (
            '<a class="part fleet" href="../page.html" title="every partition">fleet</a>'
            '<span class="part" aria-current="page">wldn</span><a class="part" href="../madswan/page.html">madswan</a>')

    def test_a_page_named_for_its_partition_links_the_others_beside_it_as_they_are_served(self):
        """board-page "Pages written side by side as they are served": <label>.html links <other>.html, and the fleet
        page as index.html beside it."""
        assert page.beside(PurePath("/w/wldn.html"), "wldn", "madswan") == "madswan.html"
        assert page.nav(["wldn", "madswan"], "wldn", PurePath("/w/wldn.html")).startswith(
            '<a class="part fleet" href="index.html" title="every partition">fleet</a><span class="part" aria-current="page">wldn</span>')
        assert '<a class="part" href="madswan.html">madswan</a>' in page.nav(["wldn", "madswan"], "wldn", PurePath("/w/wldn.html"))

    def test_a_folder_and_a_file_both_named_for_the_partition_swap_both(self):
        """board-page "A folder and a file both named for the partition": no link to the fleet page."""
        assert page.beside(PurePath("/s/wldn/wldn.html"), "wldn", "madswan") == "../madswan/madswan.html"
        assert "fleet" not in page.nav(["wldn", "madswan"], "wldn", PurePath("/s/wldn/wldn.html"))

    @pytest.mark.parametrize("path, back", [("/f/swancloud.html", "index.html"), ("/h/.local/state/crew/swancloud/page.html", "../page.html"),
                                            ("/f/swancloud/swancloud.html", None), ("/f/board.html", None), ("/f/x/page.html", None),
                                            ("/f/swancloud/board.html", None)])
    def test_the_fleet_page_is_linked_back_in_the_layout_of_the_pages_own_file_and_none_where_crew_cannot_tell(self, path, back):
        """board-page: the header links to the fleet page beside a page served as <label>.html and from crew's
        <label>/page.html, and to none in any other layout (read.1)."""
        assert page.fleet_back(PurePath(path), "swancloud") == back

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


class TestMade:
    """lineage-page, "A host was asleep": the page is drawn from the branch's entries alone, a Mac that wrote some of
    them and does not answer among them, and names a host only for its kits."""
    FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": "mac-studio", "state": "WilldanGroup/crew-state"}},
             "hosts": {"mac-studio": {"kind": "darwin"}, "macbook-pro": {"kind": "darwin"}}}

    def made(self, monkeypatch, capsys, kits):
        import argparse
        import board
        import crew
        monkeypatch.setattr(crew, "on_machine", lambda *a, **k: pytest.fail(f"a host was asked for the run record: {a}"))

        def branch(fleet, label, since, tips=None):
            tips[label] = "a" * 40
            return [dict(e, Host="macbook-pro") for e in FLOW]
        monkeypatch.setattr(record, "on_branch", branch)
        monkeypatch.setattr(board, "flow_read", lambda fleet, labels: {"found": [("wldn", "WilldanGroup/crew-state", "a" * 40, None)], "sv": {}})
        monkeypatch.setattr(board, "board_data", lambda fleet, labels, read, now: {"partitions": [{"plan": "a" * 40}], "read_at": "x", "unread": {}})
        monkeypatch.setattr(page, "describe", lambda *a, **k: kits)
        monkeypatch.setattr(page, "docks", lambda *a, **k: {})
        page.page(self.FLEET, argparse.Namespace(label="wldn", since=None, json=True, out=None))
        return json.loads(capsys.readouterr().out)

    def test_a_page_made_from_the_branchs_entries_names_no_host_for_its_record(self, monkeypatch, capsys):
        d = self.made(monkeypatch, capsys, {})
        assert d["made"]["commit"] == "a" * 40 and d["made"]["unreachable"] == {}
        assert sorted(d["entries"]) == sorted(e["Id"] for e in FLOW) and "macbook-pro" not in json.dumps(d["made"])

    def test_a_host_whose_kits_did_not_answer_is_named_for_them_alone(self, monkeypatch, capsys):
        d = self.made(monkeypatch, capsys, {"chuck-herdr-alpha": "its kits: ssh: timed out"})
        assert d["made"]["unreachable"] == {"chuck-herdr-alpha": "its kits: ssh: timed out"}


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


class TestSitesOfAStartedBolt:
    """crew-sites "A started bolt's work shows no server": x, started, is listed with where its work runs and no
    server, though one runs in a unit's place of crew's naming, since its places are Flume's (_open.md: the runner
    reports a place's addresses)."""

    def listed(self, monkeypatch):
        import crew
        from facts import CREW_AT, crew_read, flume_plan, madswan_fleet
        fleet = dict(madswan_fleet(), hosts={"deneb": {"kind": "nixos"}})
        p = plan.Plan(flume_plan([("x", True, "flume")], [("a", "x", [], "unit", [])]))
        sv = crew_read(bolts={"x": {}})
        k = sv["deneb"]["kits"]["/crew/main"]
        k.update(places={"a": {"path": "/crew/places/unit-a"}}, sites={"/crew/places/unit-a": {"here": "https://unit-a--crew.local"}},
                 routes=[{"name": "unit-a--crew", "url": "https://unit-a--crew.local"}])
        monkeypatch.setattr(plan, "plans", lambda fleet, labels, errors: [("madswan", "afterthought/crew-state", "tip0", p)])
        monkeypatch.setattr(plan, "survey", lambda fleet, held, sites=False: sv)
        monkeypatch.setattr(crew, "this_host", lambda: "deneb")
        # x's work taken by deneb's runner, which reported crew in /crew/main (plan.known_at); madswan's hosts its main
        # level's and its runners' (plan.partition_hosts)
        monkeypatch.setattr(plan, "rail_runs", lambda found: {"madswan": ([], {})})
        monkeypatch.setattr(plan, "known_at", lambda fleet, label, b, run=None: dict(CREW_AT, label=label))
        monkeypatch.setattr(plan, "partition_hosts", lambda fleet, label, fetch=True: ["deneb"])
        return sites.sites(fleet, ["madswan"])

    def test_a_started_bolt_is_listed_with_no_server_saying_why(self, monkeypatch):
        x, = self.listed(monkeypatch)["partitions"][0]["hosts"][0]["bolts"]
        assert (x["bolt"], x["url"], x["units"], x["note"]) == ("x", None, [], sites.FLUME_PLACES)

    def test_its_line_says_where_its_work_runs(self, monkeypatch):
        line = next(l for l in sites.text(self.listed(monkeypatch)).splitlines() if l.strip().startswith("x "))
        assert line.endswith("its work runs in Flume's places, whose servers crew does not show yet  [crew]")


class TestMore:
    def test_a_unit_and_bolt_whose_host_does_not_answer_have_no_stage_or_status(self):
        d = page.data([entry("unit.add", ["unit/a", "bolt/tenant-environments"])])
        pl = plan.Plan(plan_text(bolts=[("tenant-environments", "switchboard-kit", True)], units=[("a", "switchboard-kit", "tenant-environments", [])]))

        class Unknown:
            fleet = FLEET

            def of(self, name):
                return {"stage": "unknown"}

            def at(self, b):  # no runner has reported taking tenant-environments' work
                return None, "no runner has reported taking bolt tenant-environments' work yet"

            def bolt_state(self, b):
                return "unknown"
        page.labelled(d, pl, Unknown(), {}, {}, {}, lambda name: None)
        by = {n["id"]: n for n in d["nodes"]}
        assert [by["unit/a"].get(k) for k in ("label", "stage", "status")] == ["Unit a.", None, None]
        assert [by["bolt/tenant-environments"].get(k) for k in ("status", "facts")] == [None, []] and "team" not in by["bolt/tenant-environments"]

    def test_the_page_opens_on_the_board_in_the_mockups_forms_with_a_phone_layout_and_no_team_to_narrow_it_to(self):
        """board-page, the removed "A viewer narrows every lane to one team", "The team chosen survives a reload" and "The
        strip names the partition's teams" (Decision 11 of the-team-machinery-leaves)."""
        rest = re.sub(r'(<script type="application/json" id="data">).*?(</script>)', r"\1\2", page.render(TestFile.D, PurePath("/s/wldn/page.html")), flags=re.S)
        for lane in ("Inception", "Bolt plan", "Construction", "Operation"):
            assert f'aria-label="{lane}"' in rest
        for has in ("@media (max-width:759px)", "prefers-color-scheme:dark", ':root[data-theme="dark"]', "repeating-linear-gradient",
                    "design/flywheel-next/mockups/rail-and-board.html", "history.replaceState", '"crew-page:" + D.label',
                    'id="hide"', 'id="find"', 'id="bars"', "Nothing has been recorded"):
            assert has in rest
        for form in (".quote", ".sheet", ".slip", ".ledger", ".record", ".mark.attention", ".lg-unit.building"):
            assert form in rest
        for deploys in ('aria-label="Deploys"', 'data-view="deploys"', "D.deploys", "B.environments", ".dp-line", "release notes"):
            assert deploys in rest
        for sample in ("atlas", "plan-decisions", "books", "Manrope", "JetBrains Mono"):
            assert sample not in rest
        for team in ('id="team"', "B.teams", "dataset.teams", "narrow(", "team:", "u.slot", "f.slot"):
            assert team not in rest, team

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
    unit, tenant-environments started, its work taken by the box's runner in stream wldn, with a in code, b at construct
    and a fix, atlas-maps landed and deployed to mac-studio, a newer deploy waiting on the word, and operations waiting
    on the environment; and wldn's main level on mac-studio, its design agent, planner and reviewer in its session wldn
    on account madswan-2, ops in ops on willdan, and its operator in op, which names no account."""
    SIG = "2026-10-01-planning/01-zones"

    @pytest.fixture(autouse=True)
    def here(self, monkeypatch):
        import crew
        monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")

    def fleet(self):
        import copy
        from test_board import BOX, FLEET
        f = copy.deepcopy(FLEET)
        f["hosts"][BOX]["sessions"] = {"crew-a": {"account": "madswan-2"}}  # where the runner takes the work, no agent of crew's
        f["hosts"]["mac-studio"]["sessions"] = {"wldn": {"account": "madswan-2"}, "ops": {"account": "willdan"}, "op": {}}
        f["partitions"]["wldn"]["sessions"] = dict({r: "wldn" for r in ("design", "planner", "reviewer")}, ops="ops", operator="op")
        return f

    def paged(self, label=None):
        import datetime
        from test_board import NOW, OPS, SIGS, WAITS, data
        card = dict(label="wldn", card="req_2", key="proposal/2", by="wldn-planner", host="mac-studio", at=NOW)
        landing = dict(label="wldn", bolt="atlas-maps", units=["map-one"], at=NOW - datetime.timedelta(hours=1), by="chuck@mac-studio", host="mac-studio")
        bd = data(signals=SIGS, props=WAITS, cards=[card], entries=OPS, landings=[landing])
        lineage = [entry("capture", [f"signals/{self.SIG}"], why="captured"), entry("plan.propose", ["proposal/2", "unit/d", "bolt/tenant-environments"]),
                   entry("unit.add", ["unit/a", "bolt/tenant-environments"], ["signals/" + self.SIG]), entry("unit.add", ["unit/d", "bolt/tenant-environments"], ["proposal/2"]),
                   entry("bolt.land", ["bolt/atlas-maps", "unit/map-one"], minutes=5), entry("unit.add", ["unit/x", "bolt/c"], ["agenda/8"])]
        d = page.data(lineage + OPS)
        for n in d["nodes"]:
            n["label"] = label if n["id"] == f"signals/{self.SIG}" and label else n.get("label")
        d["board"] = dict(bd["partitions"][0], read_at=bd["read_at"], unread=bd["unread"])
        # A fix in flight on tenant-environments, a Flume place, as the board draws a started bolt's fix.
        te = next(b for b in d["board"]["construction"] if b["bolt"] == "tenant-environments")
        te["fixes"] = [{"fix": "fix/tenant-environments/edge", "merged": False, "submission": None, "worktree": None,
                        "url": None, "flume": {"stage": "code", "place": "/kit/places/fix--tenant-environments--edge"}}]
        d["deploys"] = page.deploys(d, OPS, "mac-studio")
        d["docks"] = page.docks(d, self.fleet(), "wldn")
        return d

    def test_every_item_of_each_kind_carries_the_key_of_a_dock_the_page_holds_and_no_team_has_one(self):
        """board-page "Every item has its dock"."""
        d = self.paged()
        B = d["board"]
        drawn = list(page.walk(B, d["deploys"]))
        assert drawn and all(x["dock"] in d["docks"] for x in drawn)
        kinds = {d["docks"][x["dock"]]["kind"] for x in drawn}
        assert kinds == {"signal", "proposal", "bolt", "unit", "fix", "landing", "deploy", "operation"}
        assert not [k for k in d["docks"] if k.startswith("team:")]
        assert B["bolt_plan"]["planned"][0]["dock"] == "bolt:apex-zones" and B["bolt_plan"]["queue"][0]["dock"] == "unit:zone-two"
        assert B["construction"][0]["fixes"][0]["dock"] == "fix:tenant-environments/edge"

    def test_a_units_dock_in_a_ledger_says_its_bolt_as_a_link_its_stage_and_its_tasks(self):
        """board-page "A unit being built"."""
        a = self.paged()["docks"]["unit:a"]
        assert (a["kind"], a["title"], a["tail"], a["form"]) == ("unit", "a", "unit · in tenant-environments", None)
        facts = {f[0]: f[1:] for f in a["facts"]}
        assert facts["bolt"] == ["tenant-environments", "bolt:tenant-environments"]
        assert (facts["stage"], facts["tasks"]) == (["code"], ["1 of 2 tasks"]) and "slot" not in facts
        assert "server" not in facts and "worktree" not in facts

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
        assert p["facts"] == [["waiting on", "the user"]]
        assert [(m["glyph"], m["card"]["by"]) for m in p["markers"]] == [("✓", "wldn-planner")]
        assert {"title": "units and bolts", "rows": [{"text": "unit d"}]} in p["parts"]
        assert [x["title"] for x in p["parts"]] == ["units and bolts"]  # naming no team (the-team-machinery-leaves)

    def test_a_started_bolts_dock_is_a_ledger_of_its_units_and_fixes_and_a_planned_ones_says_not_started(self):
        from test_board import BOX
        d = self.paged()
        b = d["docks"]["bolt:tenant-environments"]
        assert (b["form"], b["title"], b["tail"]) == ("ledger", "tenant-environments", f"switchboard-kit · on {BOX} in stream wldn · active")
        assert ["host", BOX] in b["facts"] and ["stream", "wldn"] in b["facts"] and not [f for f in b["facts"] if f[0] == "team"]
        units = next(p["rows"] for p in b["parts"] if p["title"] == "units")
        assert units == [{"text": "a · code 1/2", "key": "unit:a"}, {"text": "b · construct", "key": "unit:b"}]
        assert next(p["rows"] for p in b["parts"] if p["title"] == "fixes") == [
            {"text": "fix/tenant-environments/edge · not merged", "key": "fix:tenant-environments/edge"}]
        assert b["history"] == d["histories"]["bolt/tenant-environments"]
        z = d["docks"]["bolt:apex-zones"]
        assert (z["tail"], z["markers"]) == ("switchboard-kit · planned, not started", [])

    def test_a_queued_unit_is_a_slip_with_its_sources(self):
        q = self.paged()["docks"]["unit:zone-two"]
        assert (q["form"], q["tail"]) == ("slip", "unit · queued")
        assert {f[0]: f[1] for f in q["facts"]} == {"repository": "switchboard-kit", "stage": "queued", "sources": "docs/zones.md"}

    def test_a_fix_says_whether_it_merged_and_links_its_bolt(self):
        """board-page "A fix"."""
        f = self.paged()["docks"]["fix:tenant-environments/edge"]
        assert (f["title"], f["tail"]) == ("fix/tenant-environments/edge", "fix of tenant-environments")
        assert {x[0]: x[1] for x in f["facts"]} == {"state": "not merged", "stage": "code"}  # its stage as the runner's records give it, no slot
        assert f["parts"] == [{"title": "bolt", "rows": [{"text": "tenant-environments", "key": "bolt:tenant-environments"}]}]
        assert f["history"] == []

    def test_a_landing_is_a_record_with_its_units_the_deploys_carrying_it_and_its_bolt_land_entry(self):
        d = self.paged()
        o = d["docks"]["landing:atlas-maps"]
        at = d["board"]["operation"][0]["at"]
        assert (o["form"], o["title"], o["tail"]) == ("record", "atlas-maps", f"landed {at} by chuck@mac-studio")
        assert not [f for f in o["facts"] if f[0] == "team"]
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
        assert d["docks"]["operation:mac-studio/restart-roles/1"]["tail"] == "on mac-studio · handed to wldn-ops"

    def test_a_subscriptions_dock_lists_the_main_levels_sessions_on_it(self):
        """board-page "A subscription's dock lists its sessions": madswan-2's dock lists the design agent, the planner and
        the reviewer in mac-studio's session wldn, and willdan's ops; op names no account, so no dock lists it."""
        d = self.paged()
        s = d["docks"]["subscription:madswan-2"]
        assert (s["title"], s["tail"]) == ("madswan-2", "Claude account")
        assert s["parts"] == [{"title": "sessions on it", "rows": [{"text": f"wldn-{r} · mac-studio session wldn"} for r in ("design", "planner", "reviewer")]}]
        assert [r["text"] for r in d["docks"]["subscription:willdan"]["parts"][0]["rows"]] == ["wldn-ops · mac-studio session ops"]
        assert sorted(k for k in d["docks"] if k.startswith("subscription:")) == ["subscription:madswan-2", "subscription:willdan"]

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
                    'x.setAttribute("role", "button")', "x.tabIndex = 0", "preventScroll: true", "opener.focus"):
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
        assert [to[k] for k in ("bolt:tenant-environments", "unit:a", "fix:tenant-environments/edge")] == ["wldn-planner"] * 3
        assert [to[k] for k in ("bolt:apex-zones", "unit:zone-one", "unit:zone-two")] == ["wldn-planner"] * 3
        assert (to["proposal:2"], to[f"signal:{TestDocks.SIG}"]) == ("wldn-planner", "wldn-design")
        assert [to[k] for k in ("landing:atlas-maps", deploy, "operation:mac-studio/rotate-key")] == ["wldn-ops"] * 3
        assert to["subscription:madswan-2"] == "wldn-operator"

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
        assert [page.word_to(k, "wldn") for k in ("batch:14", "record:0038", "partition:wldn", "unit:nosuch", "nosuch:x")] == [
            "wldn-planner", "wldn-design", "wldn-operator", "wldn-planner", "wldn-operator"]


def test_a_chore_stands_in_the_units_column_its_move_drawn_as_a_units_and_labelled_by_its_words():
    """page.data and page.labelled: a chore is work like a unit, so it is in the units' column, where it moved from is not
    what it came from, and its label and stage are read from the plan and its kit (plan.11)."""
    d = page.data([entry("chore.add", ["chore/bump", "queue/switchboard-kit"]), entry("chore.move", ["chore/bump", "bolt/c"], ["bolt/b"])])
    assert page.column("chore/bump") == page.column("unit/u")
    assert [f"{e['from']}>{e['to']}" for e in d["edges"]] == ["chore/bump>bolt/c"]
    pl = plan.Plan(plan_text(bolts=[("c", "switchboard-kit", True)], units=[("bump", "switchboard-kit", "c", [], "chore")]))

    class St:
        fleet = FLEET

        def of(self, name):
            return {"stage": "verify"}

        def at(self, b):
            return {"machine": "chuck-herdr-alpha"}, None

        def bolt_state(self, b):
            return "active"
    page.labelled(d, pl, St(), {}, {}, {}, lambda name: None)
    by = {n["id"]: n for n in d["nodes"]}
    assert [by["chore/bump"][k] for k in ("label", "status", "stage")] == ["Chore bump.", "flight", "verify"]

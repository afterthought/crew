"""The fleet page (the fleet-page spec): page.fleet_data on the board of every partition, as board.board_data gives it,
and each partition's run-record entries; page.fleet_links and page.linked for its links. That crew page --fleet makes
it from one read of every partition and writes it whole is the board journey's (t-journey-board)."""
import datetime
import json
import re
from pathlib import PurePath

import page

NOW = datetime.datetime(2026, 10, 23, 12, 0, tzinfo=datetime.timezone.utc)
SINCE = "2026-10-16T12:00:00Z"


def sess(partition, account="madswan"):
    return {"dir": "/w", "partition": partition, "repos": [], **({"account": account} if account else {})}


def team(name, label, machine, session, kits, units=4):
    return {"name": name, "label": label, "machine": machine, "session": session, "units": units,
            "kits": [{"name": k} for k in kits], "kit": {"name": kits[0]}}


def main(label, partition, machine, session, teams, sessions=None):
    roles = dict.fromkeys(("design", "planner", "ops", "operator", "reviewer"), session)
    return {"label": label, "partition": partition, "machine": machine, "session": session, "teams": teams,
            "sessions": dict(roles, **(sessions or {}))}


# madswan, swancloud and wldn, in the teams file's order. swancloud's main level runs on deneb in its session swancloud
# and crw-6 beside it in swancloud-2, on another account; crw-7 runs on mac-studio, away from the main level, in a
# session the hosts file names no account for; deneb's swancloud-3 is the partition's, and no agent of it runs there;
# deneb's agentplot-2 is on madswan, and no agent of any partition runs there.
FLEET = {
    "hosts": {"deneb": {"sessions": {"madswan": sess("business"), "swancloud": sess("personal"), "swancloud-2": sess("personal", "madswan-2"),
                                     "swancloud-3": sess("personal"), "agentplot-2": sess("agentplot")}},
              "mac-studio": {"sessions": {"wldn": sess("clients/willdan", "willdan-alex"), "swancloud-4": sess("personal", None)}},
              "chuck-herdr-alpha": {"sessions": {"wldn-1": sess("clients/willdan", "ia")}}},
    "partitions": {"madswan": main("madswan", "business", "deneb", "madswan", ["mad-1"]),
                   "swancloud": main("swancloud", "personal", "deneb", "swancloud", ["crw-6", "crw-7"]),
                   "wldn": main("wldn", "clients/willdan", "mac-studio", "wldn", ["swb-1"])},
    "teams": {"mad-1": team("mad-1", "madswan", "deneb", "madswan", ["blueprints"]),
              "crw-6": team("crw-6", "swancloud", "deneb", "swancloud-2", ["crew"]),
              "crw-7": team("crw-7", "swancloud", "mac-studio", "swancloud-4", ["swancloud", "crew"], units=2),
              "swb-1": team("swb-1", "wldn", "chuck-herdr-alpha", "wldn-1", ["switchboard-kit"])},
}


def unit(name, stage, slot=None, kind="unit"):
    return {"unit": name, "kind": kind, "stage": stage, "tasks": None, "slot": slot, "worktree": None, "url": None}


def ledger(bolt, repo, team, state, units, fixes=(), card=False):
    ms = [{"group": "land", "key": f"land/{repo}", "glyph": "✓", "card": {"by": "swancloud-ops", "host": "deneb", "at": SINCE} if card else None,
           "refused": None}] if state == "waits" else []
    return {"bolt": bolt, "repo": repo, "goal": None, "team": team, "host": None, "state": state, "url": None, "markers": ms,
            "teams": [team], "units": list(units), "fixes": list(fixes)}


def part(label, hosts, construction=(), planned=(), queue=(), attention=(), cards=0, plan="c" * 40):
    teams = [{"team": t, "kit": FLEET["teams"][t]["kit"]["name"], "kits": [k["name"] for k in FLEET["teams"][t]["kits"]],
              "host": FLEET["teams"][t]["machine"]} for t in FLEET["partitions"][label]["teams"]]
    return {"label": label, "plan": plan, "hosts": hosts, "teams": teams, "cards": [{"key": f"k{i}"} for i in range(cards)],
            "construction": list(construction), "attention": list(attention),
            "bolt_plan": {"proposals": [], "planned": [{"bolt": b, "repo": r} for b, r in planned], "queue": [{"unit": u, "repo": r} for u, r in queue]}}


N = iter(range(1, 1000))


def entry(act, on, at, **f):
    return dict(Id=f"{at}-deneb-1-{next(N)}", At=at, Act=act, On=list(on), From=[], **f)


# crew's main last took bolt a, the newer of its two landings in the window, a refused one after it passed over and a
# switchboard-kit landing beside it; crw-6's unit-1 runs code of x, unit-2's verify of y has ended, unit-3 runs a fix,
# and a stage of crw-7's ended; a landing of crew's eight days ago is outside the window.
LOGS = {"swancloud": [
    entry("bolt.land", ["bolt/old"], "2026-10-15T09:00:00Z", Repo="crew", Head="0" * 40, By="swancloud-ops"),
    entry("bolt.land", ["bolt/z", "unit/q"], "2026-10-20T09:00:00Z", Repo="crew", Head="1" * 40, By="swancloud-ops"),
    entry("bolt.land", ["bolt/a", "unit/p"], "2026-10-21T09:00:00Z", Repo="crew", Head="3f2c1d0" + "0" * 33, By="swancloud-ops"),
    entry("bolt.land", ["bolt/s"], "2026-10-21T10:00:00Z", Repo="switchboard-kit", Head="5" * 40, By="wldn-ops"),
    entry("bolt.land", ["bolt/r"], "2026-10-22T09:00:00Z", Repo="crew", Head="9" * 40, By="crw-6-conductor", Refused="the bolt holds a unit not merged"),
    entry("stage.start", ["stage/y/verify", "unit/y", "agent/crw-6-unit-2"], "2026-10-23T09:00:00Z"),
    entry("stage.start", ["stage/x/code", "unit/x", "agent/crw-6-unit-1"], "2026-10-23T10:00:00Z"),
    entry("stage.end", ["stage/y/verify", "unit/y", "agent/crw-6-unit-2"], "2026-10-23T10:30:00Z", Ended="delivered"),
    entry("fix.start", ["fix/b/edge", "bolt/b", "agent/crw-6-unit-3"], "2026-10-23T11:00:00Z"),
    entry("stage.start", ["stage/v/code", "unit/v", "agent/crw-6-unit-4"], "2026-10-23T11:10:00Z", Refused="all 4 of crw-6's slots are in flight"),
    entry("stage.start", ["stage/m/code", "chore/m", "agent/crw-7-unit-1"], "2026-10-23T08:00:00Z"),
    entry("stage.end", ["stage/m/code", "chore/m", "agent/crw-7-unit-1"], "2026-10-23T08:40:00Z", Ended="delivered")]}

BOARD = {"read_at": "2026-10-23T12:00:00Z", "from": "deneb", "unread": {"the plan of madswan": "fetch failed: timed out"},
         "partitions": [
             part("madswan", {"deneb": True}, plan=None,
                  attention=[{"what": "plan", "name": "the plan of madswan", "why": "fetch failed: timed out"}]),
             part("swancloud", {"deneb": True, "mac-studio": "its kits: ssh: timed out"},
                  construction=[ledger("b", "crew", "crw-6", "active", [unit("p", "merged"), unit("x", "code", "unit-1"), unit("y", "verify", "unit-2")],
                                       [{"fix": "fix/b/edge", "merged": False, "slot": "unit-3", "worktree": None, "url": None}]),
                                ledger("w", "crew", "crw-5", "waits", [unit("w1", "merged")], card=True),
                                ledger("c", "swancloud", "crw-7", "active", [unit("m", "verify", "unit-1", "chore")])],
                  planned=[("d", "crew"), ("e", "swancloud")], queue=[("q1", "crew"), ("q2", "swancloud"), ("q3", "swancloud")],
                  attention=[{"what": "host", "name": "mac-studio", "why": "its kits: ssh: timed out"},
                             {"what": "landed", "name": "old", "why": "every unit has landed on main, and the bolt is still in the plan"}], cards=2),
             part("wldn", {"chuck-herdr-alpha": True})]}


def fleet(board=BOARD, logs=LOGS):
    return page.fleet_data(FLEET, board, logs, NOW)


def of(d, label):
    return next(p for p in d["partitions"] if p["label"] == label)


def team_of(p, name):
    return next(t for t in p["teams"] if t["team"] == name)


class TestWhereItRuns:
    def test_every_partition_in_the_teams_files_order_with_its_plans_commit_and_what_could_not_be_read(self):
        """fleet-page "Three partitions": a block for each, in order, as of when and which commit of each plan."""
        d = fleet()
        assert [p["label"] for p in d["partitions"]] == ["madswan", "swancloud", "wldn"]
        assert d["made"] == {"at": "2026-10-23T12:00:00Z", "since": SINCE}
        assert [(p["plan"], p["commit"]) for p in d["partitions"]] == [(None, "madswan/main not read"), ("c" * 40, "swancloud/main ccccccc"),
                                                                       ("c" * 40, "wldn/main ccccccc")]
        assert of(d, "madswan")["unread"] == {"the plan of madswan": "fetch failed: timed out"} and of(d, "wldn")["unread"] == {}
        b = dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True}, plan=None)], unread={})
        assert of(fleet(b), "wldn")["commit"] == "wldn/main not started"
        assert of(d, "madswan")["partition"] == "business"

    def test_a_host_that_did_not_answer_is_named_with_its_why_and_the_rest_shown(self):
        """fleet-page "A host that does not answer"."""
        hosts = {h["host"]: h for h in of(fleet(), "swancloud")["hosts"]}
        assert list(hosts) == ["deneb", "mac-studio"]
        assert (hosts["mac-studio"]["answered"], hosts["mac-studio"]["why"], hosts["mac-studio"]["said"]) == (
            False, "its kits: ssh: timed out", "did not answer (its kits: ssh: timed out)")
        assert (hosts["deneb"]["answered"], hosts["deneb"]["why"], hosts["deneb"]["said"]) == (True, None, "answered")
        assert hosts["mac-studio"]["sessions"]

    def test_each_session_names_its_agents_and_its_account_and_one_no_agent_runs_in_is_left_out(self):
        """fleet-page "Two sessions on two accounts": deneb's swancloud holds the main level, account madswan, and
        swancloud-2 holds crw-6, account madswan-2; swancloud-3, the partition's, holds none of its agents."""
        deneb = next(h for h in of(fleet(), "swancloud")["hosts"] if h["host"] == "deneb")
        assert [(s["session"], s["agents"], s["account"], s["account_said"]) for s in deneb["sessions"]] == [
            ("swancloud", ["swancloud-design", "swancloud-planner", "swancloud-ops", "swancloud-operator", "swancloud-dispatch-deneb"], "madswan", "account madswan"),
            ("swancloud-2", ["crw-6"], "madswan-2", "account madswan-2")]

    def test_a_session_the_hosts_file_names_no_account_for_says_so_and_a_dispatcher_runs_on_a_teams_host_away_from_the_main_level(self):
        """fleet-page "No account named": never blank (read.2); crw-7's host has the partition's dispatcher in its session."""
        mac = next(h for h in of(fleet(), "swancloud")["hosts"] if h["host"] == "mac-studio")
        assert [(s["session"], s["agents"], s["account"], s["account_said"]) for s in mac["sessions"]] == [
            ("swancloud-4", ["crw-7", "swancloud-dispatch-mac-studio"], None, "no account named in herdr-hosts")]
        assert (team_of(of(fleet(), "swancloud"), "crw-7")["account"], team_of(of(fleet(), "swancloud"), "crw-7")["account_said"]) == (
            None, "no account named in herdr-hosts")

    def test_the_main_levels_host_is_listed_when_no_team_runs_there_and_said_not_asked(self):
        """wldn's main level runs on mac-studio, where none of its teams runs, so the board did not ask it."""
        hosts = {h["host"]: h for h in of(fleet(), "wldn")["hosts"]}
        assert list(hosts) == ["chuck-herdr-alpha", "mac-studio"]
        assert (hosts["mac-studio"]["answered"], hosts["mac-studio"]["said"]) == (None, "not asked: no team of it runs there")
        assert [(s["session"], s["agents"]) for s in hosts["mac-studio"]["sessions"]] == [("wldn", ["wldn-design", "wldn-planner", "wldn-ops", "wldn-operator"])]
        assert [(s["session"], s["agents"]) for s in hosts["chuck-herdr-alpha"]["sessions"]] == [("wldn-1", ["swb-1", "wldn-dispatch-chuck-herdr-alpha"])]


class TestKits:
    def kits(self):
        return {k["kit"]: k for k in of(fleet(), "swancloud")["kits"]}

    def test_each_kit_once_in_the_boards_order_with_the_teams_building_it(self):
        assert [(k, v["teams"]) for k, v in self.kits().items()] == [("crew", ["crw-6", "crw-7"]), ("swancloud", ["crw-7"])]

    def test_a_kits_last_landing_is_its_newest_in_the_window_a_refused_one_and_another_kits_passed_over(self):
        """fleet-page "A kit with a landing and a bolt waiting"."""
        crew = self.kits()["crew"]
        assert crew["landing"] == {"bolt": "a", "head": "3f2c1d0" + "0" * 33, "at": "2026-10-21T09:00:00Z", "by": "swancloud-ops"}
        assert crew["said"][0] == "last landed a at 3f2c1d0, 2026-10-21 09:00Z by swancloud-ops"

    def test_a_kit_with_no_landing_in_the_window_says_so(self):
        """fleet-page "A kit with no landing in the window": never a blank."""
        k = self.kits()["swancloud"]
        assert (k["landing"], k["said"][0]) == (None, "no landing since 2026-10-16")

    def test_what_is_queued_for_a_main_waits_to_land_in_construction_planned_and_queued_each_under_its_kit(self):
        crew, sc = self.kits()["crew"], self.kits()["swancloud"]
        assert crew["waits"] == [{"bolt": "w", "card": {"by": "swancloud-ops", "host": "deneb", "at": SINCE}}]
        assert (crew["building"], crew["planned"], crew["queued"]) == ([{"bolt": "b", "state": "active"}], 1, 1)
        assert crew["said"][1] == "w waits to land, its card open; b in construction; 1 bolt planned; 1 unit queued"
        assert sc["said"][1] == "c in construction; 1 bolt planned; 2 units queued"

    def test_a_bolt_waiting_with_no_card_open_and_a_kit_with_nothing_queued_say_so(self):
        b = dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True}, construction=[ledger("s", "switchboard-kit", "swb-1", "waits", [unit("s1", "merged")])])])
        k, = of(fleet(b), "wldn")["kits"]
        assert k["said"] == ["no landing since 2026-10-16", "s waits to land, no card open"]
        assert of(fleet(dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True})])), "wldn")["kits"][0]["said"][1] == "nothing queued"


class TestTeams:
    def test_a_team_at_work_shows_its_bolt_each_slot_and_how_many_are_at_work(self):
        """fleet-page "A team at work": unit-1 at work on code of x, unit-2 holding y with no stage running, a fix's
        slot at work, a slot whose start was refused free, 2 of 4 at work, and the conductor waiting on the stages."""
        crw6 = team_of(of(fleet(), "swancloud"), "crw-6")
        assert (crw6["host"], crw6["session"], crw6["account"], crw6["kits"]) == ("deneb", "swancloud-2", "madswan-2", ["crew"])
        b, = crw6["bolts"]
        assert (b["pips"], b["merged"], b["said"]) == ("●◑◕", "1 of 3 merged", "●◑◕ b · 1 of 3 merged")
        assert [s["said"] for s in crw6["slots"]] == ["unit-1 at work: code of x", "unit-2 holding y (verify), no stage running",
                                                     "unit-3 at work: code of fix/b/edge", "unit-4 free"]
        assert [(s["state"], s.get("kind"), s.get("since")) for s in crw6["slots"]] == [
            ("work", "unit", "2026-10-23T10:00:00Z"), ("held", "unit", None), ("work", "fix", "2026-10-23T11:00:00Z"), ("free", None, None)]
        assert (crw6["at_work"], crw6["at_work_said"]) == (2, "2 of 4 slots at work")
        assert crw6["waits"] == {"on": "stages", "stages": ["code of x", "code of fix/b/edge"], "said": "waits on 2 stages: code of x, code of fix/b/edge"}

    def test_a_slot_whose_stage_ended_holds_its_chore_and_a_merge_of_a_fix_is_its_merge(self):
        crw7 = team_of(of(fleet(), "swancloud"), "crw-7")
        assert [s["said"] for s in crw7["slots"]] == ["unit-1 holding chore m (verify), no stage running", "unit-2 free"]
        logs = {"swancloud": LOGS["swancloud"] + [entry("fix.merge", ["fix/b/edge", "bolt/b", "agent/crw-7-unit-2"], "2026-10-23T11:30:00Z")]}
        crw7 = team_of(of(fleet(logs=logs), "swancloud"), "crw-7")
        assert crw7["slots"][1]["said"] == "unit-2 at work: merge of fix/b/edge" and crw7["waits"]["said"] == "waits on 1 stage: merge of fix/b/edge"

    def test_a_stage_started_before_the_window_is_not_seen(self):
        logs = {"swancloud": [entry("stage.start", ["stage/m/code", "chore/m", "agent/crw-7-unit-2"], "2026-10-10T08:00:00Z")]}
        assert team_of(of(fleet(logs=logs), "swancloud"), "crw-7")["slots"][1]["state"] == "free"

    def test_a_team_whose_bolt_waits_to_land_waits_on_the_landing_on_the_users_word(self):
        """fleet-page "A team whose bolt waits to land"."""
        b = dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True},
                                         construction=[ledger("s", "switchboard-kit", "swb-1", "waits", [unit("s1", "merged"), unit("s2", "merged")], card=True)])])
        swb = team_of(of(fleet(b), "wldn"), "swb-1")
        assert swb["bolts"][0]["said"] == "●● s · 2 of 2 merged · waits to land"
        assert swb["waits"] == {"on": "landing", "bolt": "s", "card": {"by": "swancloud-ops", "host": "deneb", "at": SINCE},
                                "said": "waits on the landing, on the user's word, its card open"}

    def test_a_team_with_no_bolt_holds_none_its_slots_free_and_its_conductor_waits_on_nothing(self):
        """fleet-page "A team with no bolt"."""
        mad = team_of(of(fleet(), "madswan"), "mad-1")
        assert (mad["bolts"], mad["holds"], mad["at_work_said"], mad["waits"]) == ([], "holds no bolt", "0 of 4 slots at work",
                                                                                  {"on": "nothing", "said": "waits on nothing"})
        assert {s["said"] for s in mad["slots"]} == {"unit-1 free", "unit-2 free", "unit-3 free", "unit-4 free"}


class TestAttention:
    def test_attention_in_the_boards_words_and_the_cards_open_counted(self):
        """fleet-page "A bolt still in the plan once landed": the board's own attention line for it."""
        sc = of(fleet(), "swancloud")
        assert sc["attention"] == ["mac-studio did not answer (its kits: ssh: timed out)",
                                   "bolt old: every unit has landed on main, and the bolt is still in the plan"]
        assert (sc["cards"], sc["cards_said"]) == (2, "2 cards open")

    def test_nothing_needing_attention_says_so(self):
        w = of(fleet(), "wldn")
        assert (w["attention"], w["attention_said"], w["cards_said"]) == ([], ["nothing needs attention"], "0 cards open")


class TestLinks:
    LABELS = ["madswan", "swancloud", "wldn"]

    def test_served_as_index_html_each_partition_is_its_label_html_and_each_team_its_dock_there(self):
        """fleet-page "Served beside the partitions' pages": wldn's name links to wldn.html, crw-6 to swancloud's page
        with crw-6's dock open."""
        links = page.fleet_links(PurePath("/srv/board/index.html"), self.LABELS)
        assert links == {"madswan": "madswan.html", "swancloud": "swancloud.html", "wldn": "wldn.html"}
        d = fleet()
        page.linked(d, links)
        assert of(d, "wldn")["link"] == "wldn.html" and team_of(of(d, "swancloud"), "crw-6")["link"] == "swancloud.html#dock=team:crw-6"

    def test_written_as_page_html_each_partition_is_its_folders_page(self):
        """fleet-page "Crew's own layout": wldn's name links to wldn/page.html."""
        assert page.fleet_links(PurePath("/h/.local/state/crew/page.html"), self.LABELS)["wldn"] == "wldn/page.html"

    def test_a_name_that_says_no_layout_links_no_partition_and_no_team(self):
        """fleet-page "A name that says no layout": crew cannot tell where the pages are (read.1)."""
        assert page.fleet_links(PurePath("/srv/fleet.html"), self.LABELS) is None
        d = fleet()
        page.linked(d, None)
        assert {p["link"] for p in d["partitions"]} == {None} and {t["link"] for p in d["partitions"] for t in p["teams"]} == {None}


# Decision 1's file: deneb's readings of madswan, made, and of credits, not made.
WINDOW_AT = "2026-10-27T09:00:00Z"


def made(account, at, **w):
    return {"account": account, "at": at, **w}


MADSWAN = made("madswan", "2026-10-23T11:58:04Z",
               five_hour={"utilization": 34.0, "resets_at": "2026-10-23T14:00:00Z"},
               seven_day={"utilization": 61.0, "resets_at": WINDOW_AT},
               seven_day_opus=None,
               seven_day_sonnet={"utilization": 20.0, "resets_at": WINDOW_AT},
               model_scoped=[{"display_name": "Fable", "utilization": 40.0, "resets_at": WINDOW_AT}])
CREDITS = {"account": "credits", "at": "2026-10-23T11:58:06Z", "unread": "the usage endpoint answered 401"}


def published(host, *readings):
    return {"file": f"/u/{host}.json", "data": {"host": host, "readings": list(readings)}}


class TestPublishedUse:
    def test_a_file_of_two_readings_one_made_and_one_not(self):
        readings, unread = page.usage_checked({"deneb": published("deneb", MADSWAN, CREDITS)})
        assert unread == []
        assert [(r["host"], r["account"], r["at"], r["unread"]) for r in readings] == [
            ("deneb", "madswan", "2026-10-23T11:58:04Z", None), ("deneb", "credits", "2026-10-23T11:58:06Z", "the usage endpoint answered 401")]
        assert readings[0]["windows"] == {"five_hour": MADSWAN["five_hour"], "seven_day": MADSWAN["seven_day"], "seven_day_opus": None,
                                          "seven_day_sonnet": MADSWAN["seven_day_sonnet"], "model_scoped": MADSWAN["model_scoped"]}
        assert readings[1]["windows"] == dict.fromkeys(("five_hour", "seven_day", "seven_day_opus", "seven_day_sonnet", "model_scoped"))

    def test_each_file_not_of_the_shape_is_named_with_what_is_wrong_and_the_good_files_readings_kept(self):
        """fleet-page "A file that is not of the shape": each bad file unread as a whole (read.2), the rest read (read.3)."""
        files = {"box": dict(published("deneb", MADSWAN), file="/u/box.json"),
                 "capital": published("capital", made("Madswan", "2026-10-23T11:58:04Z")),
                 "deneb": published("deneb", MADSWAN),
                 "string": published("string", MADSWAN, made("ia", "2026-10-23T11:00:00Z", five_hour={"utilization": "34", "resets_at": None})),
                 "scoped": published("scoped", made("ia", "2026-10-23T11:00:00Z", model_scoped={"display_name": "Fable"})),
                 "nojson": {"file": "/u/nojson.json", "why": "it is not JSON: Expecting value: line 1 column 1 (char 0)"}}
        readings, unread = page.usage_checked(files)
        assert [(r["host"], r["account"]) for r in readings] == [("deneb", "madswan")]
        assert unread == [
            {"host": "box", "file": "/u/box.json", "why": 'its host is "deneb", not box, the file\'s name'},
            {"host": "capital", "file": "/u/capital.json", "why": 'reading 1: its account is not a name crew takes: "Madswan"'},
            {"host": "string", "file": "/u/string.json", "why": 'reading 2: its five_hour has a utilization that is not a number: "34"'},
            {"host": "scoped", "file": "/u/scoped.json", "why": 'reading 1: its model_scoped is not a list: {"display_name": "Fable"}'},
            {"host": "nojson", "file": "/u/nojson.json", "why": "it is not JSON: Expecting value: line 1 column 1 (char 0)"}]

    def test_a_reading_is_checked_for_its_at_its_unread_and_each_window(self):
        def why(r):
            return page.usage_checked({"deneb": published("deneb", r)})[1][0]["why"]
        assert why(made("ia", "yesterday")) == 'reading 1: its at is not an ISO time: "yesterday"'
        assert why(made("ia", "2026-10-23")) == 'reading 1: its at is not an ISO time: "2026-10-23"'
        assert why(made("ia", "2026-10-23T11:00:00Z", unread=401)) == "reading 1: its unread is not the host's words: 401"
        assert why(made("ia", "2026-10-23T11:00:00Z", seven_day=[61])) == "reading 1: its seven_day is not a window: [61]"
        assert why(made("ia", "2026-10-23T11:00:00Z", seven_day_opus={"utilization": True})) == (
            "reading 1: its seven_day_opus has a utilization that is not a number: true")
        assert why(made("ia", "2026-10-23T11:00:00Z", five_hour={"utilization": 1, "resets_at": "soon"})) == (
            'reading 1: its five_hour has a resets_at that is not an ISO time: "soon"')
        assert why(made("ia", "2026-10-23T11:00:00Z", model_scoped=[{"utilization": 1}])) == (
            'reading 1: its model_scoped holds a window with no display_name: {"utilization": 1}')
        assert why(made("ia", "2026-10-23T11:00:00Z", model_scoped=[{"display_name": "Fable", "utilization": "x"}])) == (
            'reading 1: its model_scoped window Fable has a utilization that is not a number: "x"')
        assert page.usage_checked({"deneb": {"file": "/u/deneb.json", "data": [1]}})[1][0]["why"] == "it is not an object: [1]"
        assert page.usage_checked({"deneb": {"file": "/u/deneb.json", "data": {"host": "deneb"}}})[1][0]["why"] == "its readings are not a list: null"

    def test_a_window_may_be_absent_null_or_without_a_figure(self):
        r = made("ia", "2026-10-23T11:00:00+02:00", five_hour={"resets_at": None}, seven_day={"utilization": None, "resets_at": WINDOW_AT},
                 model_scoped=[{"display_name": "Fable", "utilization": None, "resets_at": None}], seven_day_oauth_apps={"x": 1})
        readings, unread = page.usage_checked({"deneb": published("deneb", r)})
        assert unread == [] and readings[0]["at"] == "2026-10-23T09:00:00Z" and "seven_day_oauth_apps" not in readings[0]["windows"]

    def test_the_folder_is_read_one_file_per_host_a_file_not_json_named_and_a_missing_folder_holding_none(self, tmp_path):
        assert page.usage_files(tmp_path / "usage") == {}
        (tmp_path / "deneb.json").write_text(json.dumps({"host": "deneb", "readings": [MADSWAN]}))
        (tmp_path / "mac-studio.json").write_text("not json")
        (tmp_path / "notes.txt").write_text("not a host's")
        files = page.usage_files(tmp_path)
        assert list(files) == ["deneb", "mac-studio"]
        assert files["deneb"] == {"file": str(tmp_path / "deneb.json"), "data": {"host": "deneb", "readings": [MADSWAN]}}
        assert files["mac-studio"] == {"file": str(tmp_path / "mac-studio.json"), "why": "it is not JSON: Expecting value: line 1 column 1 (char 0)"}
        readings, unread = page.usage_checked(files)
        assert [r["account"] for r in readings] == ["madswan"] and [u["host"] for u in unread] == ["mac-studio"]


def subs(*readings, now=NOW):
    rs, _ = page.usage_checked({h: published(h, *[r for x, r in readings if x == h]) for h in dict.fromkeys(x for x, _ in readings)})
    teams = {t["team"]: t for p in fleet()["partitions"] for t in p["teams"]}
    return {s["account"]: s for s in page.subscriptions(FLEET, rs, teams, now)}


def ago(m):
    return (NOW - datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")


class TestSubscriptions:
    def test_every_account_of_the_sessions_and_of_the_readings_by_name(self):
        """fleet-page "Accounts from sessions and from readings": fable-test is published for and no session names it."""
        assert list(subs(("deneb", MADSWAN), ("deneb", made("fable-test", ago(3))))) == ["fable-test", "ia", "madswan", "madswan-2", "willdan-alex"]

    def test_the_madswan_reading_as_published_with_a_model_the_server_names_and_no_opus_line(self):
        """fleet-page "Use with a model the server names"."""
        m = subs(("deneb", MADSWAN))["madswan"]
        assert (m["state"], m["host"], m["at"], m["said"]) == ("read", "deneb", "2026-10-23T11:58:04Z", "read by deneb 1 min ago")
        assert [w["said"] for w in m["windows"]] == ["five-hour 34%, resets 14:00Z", "seven-day 61%, resets 2026-10-27 09:00Z"]
        assert [w["said"] for w in m["models"]] == ["Sonnet 20%, resets 2026-10-27 09:00Z", "Fable 40%, resets 2026-10-27 09:00Z"]
        assert [(w["window"], w["name"], w["utilization"], w["pct"], w["resets_at"]) for w in m["windows"] + m["models"]] == [
            ("five_hour", "five-hour", 34.0, 34.0, "2026-10-23T14:00:00Z"), ("seven_day", "seven-day", 61.0, 61.0, WINDOW_AT),
            ("seven_day_sonnet", "Sonnet", 20.0, 20.0, WINDOW_AT), ("model_scoped", "Fable", 40.0, 40.0, WINDOW_AT)]

    def test_a_window_with_no_figure_is_said_not_given_and_one_left_out_too(self):
        """fleet-page "A window with no figure": never a blank or 0%."""
        r = made("ia", ago(5), five_hour={"utilization": None, "resets_at": "2026-10-23T14:00:00Z"}, seven_day_opus={"utilization": 12.5},
                 model_scoped=[{"display_name": "Fable", "utilization": None, "resets_at": None}])
        ia = subs(("deneb", r))["ia"]
        assert [w["said"] for w in ia["windows"]] == ["five-hour not given", "seven-day not given"]
        assert [w["said"] for w in ia["models"]] == ["Opus 13%", "Fable not given"]
        assert [w["pct"] for w in ia["windows"] + ia["models"]] == [None, None, 12.5, None]

    def test_a_figure_past_a_hundred_is_said_as_published_and_clamped_for_the_bar_alone(self):
        w = subs(("deneb", made("ia", ago(5), five_hour={"utilization": 104, "resets_at": None})))["ia"]["windows"][0]
        assert (w["said"], w["utilization"], w["pct"]) == ("five-hour 104%", 104, 100)

    def test_read_on_two_hosts_the_newest_is_shown_and_the_other_listed_with_its_age(self):
        """fleet-page "Read on two hosts"."""
        m = subs(("mac-studio", made("madswan", ago(9), seven_day={"utilization": 50})),
                 ("deneb", made("madswan", ago(2), seven_day={"utilization": 61})))["madswan"]
        assert (m["host"], m["said"], m["windows"][1]["said"]) == ("deneb", "read by deneb 2 min ago", "seven-day 61%")
        assert m["others"] == [{"host": "mac-studio", "at": ago(9), "unread": None, "said": "mac-studio read 9 min ago"}]

    def test_a_newer_reading_not_made_lists_its_failure_and_the_made_ones_figures_are_shown(self):
        m = subs(("deneb", made("madswan", ago(65), five_hour={"utilization": 10})),
                 ("mac-studio", made("madswan", ago(4), unread="the token had expired")))["madswan"]
        assert (m["state"], m["said"], m["windows"][0]["said"]) == ("read", "read by deneb 1 h 5 min ago", "five-hour 10%")
        assert [o["said"] for o in m["others"]] == ["mac-studio could not read 4 min ago: the token had expired"]

    def test_only_a_failed_reading_shows_no_figures_and_names_the_host_with_its_words_and_when_it_tried(self):
        """fleet-page "Only a failed reading"."""
        c = subs(("deneb", dict(CREDITS, at=ago(4))))["credits"]
        assert (c["state"], c["said"], c["host"], c["at"], c["windows"], c["models"]) == ("unread", "its use could not be read", None, None, [], [])
        assert c["others"] == [{"host": "deneb", "at": ago(4), "unread": "the usage endpoint answered 401",
                                "said": "deneb could not read 4 min ago: the usage endpoint answered 401"}]

    def test_a_subscription_no_host_published_for_says_so(self):
        """fleet-page "Nothing published"."""
        ia = subs(("deneb", MADSWAN))["ia"]
        assert (ia["state"], ia["said"], ia["windows"], ia["others"]) == ("none", "no host has published its use", [], [])

    def test_ages_in_whole_minutes_and_hours_past_sixty(self):
        assert [page.age_said(ago(m), NOW) for m in (0, 0.9, 2, 59, 60, 65, -3)] == [
            "under a minute ago", "under a minute ago", "2 min ago", "59 min ago", "1 h ago", "1 h 5 min ago", "under a minute ago"]


def tokens(text):
    """The colour tokens' blocks of a page's style, light, dark as preferred and dark as chosen, each as written; a
    block setting no colour, as the phone's layout tokens, is not one."""
    return [b for b in re.findall(r'(:root\{.*?\}|:root:not\(\[data-theme="light"\]\)\{.*?\}|:root\[data-theme="dark"\]\{.*?\})', text, re.S) if "--bg:" in b]


class TestFile:
    def rendered(self, d=None):
        out = page.render_fleet(d or fleet())
        block, = re.findall(r'<script type="application/json" id="data">(.*?)</script>', out, re.S)
        return out, block, out.replace(block, "")

    def test_one_file_holding_its_data_once_that_loads_nothing_and_holds_no_control_but_links(self):
        """fleet-page "Offline": every block draws from the file alone, and the browser makes no request."""
        assert page.FLEET.read_text().count(page.DATA) == 1
        out, block, rest = self.rendered()
        assert [p["label"] for p in json.loads(block)["partitions"]] == ["madswan", "swancloud", "wldn"]
        for no in ("<script src", "<link", "@import", "http://", "https://", "src=", "url(", "{{DATA}}", "innerHTML", "outerHTML",
                   "insertAdjacentHTML", "document.write", "fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "<button", "<input",
                   "<select", "<textarea", "<form", "onclick", "addEventListener"):
            assert no not in rest, no
        assert "textContent" in rest and 'setAttribute("href"' in rest

    def test_its_colour_tokens_are_the_partition_pages_light_and_dark(self):
        """The two templates share their tokens by copy, so a case holds them equal (design, Risks)."""
        fleet_tokens, page_tokens = tokens(page.FLEET.read_text()), tokens(page.TEMPLATE.read_text())
        assert len(fleet_tokens) == 3 and fleet_tokens == page_tokens

    def test_its_partitions_sit_side_by_side_and_stack_under_760_px(self):
        rest = self.rendered()[2]
        assert "grid-template-columns:repeat(auto-fit,minmax(380px,1fr))" in rest
        assert re.search(r"@media \(max-width:759px\)\{.*?\.fleet\{grid-template-columns:1fr", rest, re.S)

    def test_typed_words_are_kept_as_text_and_cannot_end_the_data_block(self):
        """fleet-page "Typed words": an attention item holding </script><b>here</b>, a host's error as it was read."""
        said = "mac-studio did not answer (its kits: </script><b>here</b> & more)"
        b = dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True},
                                         attention=[{"what": "host", "name": "mac-studio", "why": "its kits: </script><b>here</b> & more"}])])
        out, block, rest = self.rendered(fleet(b))
        assert "<b>here</b>" not in block and of(json.loads(block), "wldn")["attention"] == [said]
        assert out.count("</script>") == 2

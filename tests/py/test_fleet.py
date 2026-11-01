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


def main(label, partition, machine, session, sessions=None):
    roles = dict.fromkeys(("design", "planner", "ops", "operator", "reviewer"), session)
    return {"label": label, "partition": partition, "machine": machine, "session": session, "sessions": dict(roles, **(sessions or {}))}


# madswan, swancloud and wldn, in the teams file's order, each a main level, the one kind of agent crew starts
# (the-team-machinery-leaves). swancloud's main level runs on deneb in its session swancloud, its operator in
# swancloud-3, a session the hosts file names no account for; deneb's swancloud-2, on another account, and agentplot-2,
# on madswan, hold no agent of any partition; chuck-herdr-alpha, where wldn's runner takes its work, holds none either.
FLEET = {
    "hosts": {"deneb": {"sessions": {"madswan": sess("business"), "swancloud": sess("personal"), "swancloud-2": sess("personal", "madswan-2"),
                                     "swancloud-3": sess("personal", None), "agentplot-2": sess("agentplot")}},
              "mac-studio": {"sessions": {"wldn": sess("clients/willdan", "willdan-alex")}},
              "chuck-herdr-alpha": {"sessions": {"wldn-1": sess("clients/willdan", "ia")}}},
    "partitions": {"madswan": main("madswan", "business", "deneb", "madswan"),
                   "swancloud": main("swancloud", "personal", "deneb", "swancloud", {"operator": "swancloud-3"}),
                   "wldn": main("wldn", "clients/willdan", "mac-studio", "wldn")},
}


def unit(name, stage, kind="unit"):
    return {"unit": name, "kind": kind, "stage": stage, "tasks": None, "worktree": None, "url": None}


def ledger(bolt, repo, state, units, fixes=(), card=False):
    ms = [{"group": "land", "key": f"land/{repo}", "glyph": "✓", "card": {"by": "swancloud-ops", "host": "deneb", "at": SINCE} if card else None,
           "refused": None}] if state == "waits" else []
    return {"bolt": bolt, "repo": repo, "goal": None, "host": None, "stream": None, "state": state, "url": None, "markers": ms,
            "units": list(units), "fixes": list(fixes)}


def part(label, hosts, kits=(), construction=(), planned=(), queue=(), attention=(), cards=0, plan="c" * 40):
    return {"label": label, "plan": plan, "hosts": hosts, "kits": list(kits), "cards": [{"key": f"k{i}"} for i in range(cards)],
            "construction": list(construction), "attention": list(attention),
            "bolt_plan": {"proposals": [], "planned": [{"bolt": b, "repo": r} for b, r in planned], "queue": [{"unit": u, "repo": r} for u, r in queue]}}


N = iter(range(1, 1000))


def entry(act, on, at, **f):
    return dict(Id=f"{at}-deneb-1-{next(N)}", At=at, Act=act, On=list(on), From=[], **f)


# crew's main last took bolt a, the newer of its two landings in the window, a refused one after it passed over and a
# switchboard-kit landing beside it; a landing of crew's eight days ago is outside the window.
LOGS = {"swancloud": [
    entry("bolt.land", ["bolt/old"], "2026-10-15T09:00:00Z", Repo="crew", Head="0" * 40, By="swancloud-ops"),
    entry("bolt.land", ["bolt/z", "unit/q"], "2026-10-20T09:00:00Z", Repo="crew", Head="1" * 40, By="swancloud-ops"),
    entry("bolt.land", ["bolt/a", "unit/p"], "2026-10-21T09:00:00Z", Repo="crew", Head="3f2c1d0" + "0" * 33, By="swancloud-ops"),
    entry("bolt.land", ["bolt/s"], "2026-10-21T10:00:00Z", Repo="switchboard-kit", Head="5" * 40, By="wldn-ops"),
    entry("bolt.land", ["bolt/r"], "2026-10-22T09:00:00Z", Repo="crew", Head="9" * 40, By="swancloud-ops", Refused="the bolt holds a unit not merged")]}

BOARD = {"read_at": "2026-10-23T12:00:00Z", "from": "deneb", "unread": {"the plan of madswan": "fetch failed: timed out"},
         "partitions": [
             part("madswan", {"deneb": True}, plan=None,
                  attention=[{"what": "plan", "name": "the plan of madswan", "why": "fetch failed: timed out"}]),
             part("swancloud", {"deneb": True, "mac-studio": "its kits: ssh: timed out"}, kits=["crew", "swancloud"],
                  construction=[ledger("b", "crew", "active", [unit("p", "merged"), unit("x", "code"), unit("y", "verify")],
                                       [{"fix": "fix/b/edge", "merged": False, "worktree": None, "url": None}]),
                                ledger("w", "crew", "waits", [unit("w1", "merged")], card=True),
                                ledger("c", "swancloud", "active", [unit("m", "verify", "chore")])],
                  planned=[("d", "crew"), ("e", "swancloud")], queue=[("q1", "crew"), ("q2", "swancloud"), ("q3", "swancloud")],
                  attention=[{"what": "host", "name": "mac-studio", "why": "its kits: ssh: timed out"},
                             {"what": "landed", "name": "old", "why": "every unit has landed on main, and the bolt is still in the plan"}], cards=2),
             part("wldn", {"chuck-herdr-alpha": True}, kits=["switchboard-kit"])]}


def fleet(board=BOARD, logs=LOGS, usage=None):
    return page.fleet_data(FLEET, board, logs, usage or {}, NOW)


def of(d, label):
    return next(p for p in d["partitions"] if p["label"] == label)


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
        assert hosts["mac-studio"]["sessions"] == [] and hosts["deneb"]["sessions"]  # a runner's host holds no agent of crew's

    def test_each_session_names_its_agents_and_its_account_and_one_no_agent_runs_in_is_left_out(self):
        """fleet-page "Two sessions on two accounts": deneb's swancloud holds the main level but its operator, account
        madswan; swancloud-2, the partition's, holds none of its agents."""
        deneb = next(h for h in of(fleet(), "swancloud")["hosts"] if h["host"] == "deneb")
        assert [(s["session"], s["agents"], s["account"]) for s in deneb["sessions"]] == [
            ("swancloud", ["swancloud-design", "swancloud-planner", "swancloud-ops", "swancloud-reviewer"], "madswan"),
            ("swancloud-3", ["swancloud-operator"], None)]
        assert deneb["sessions"][0]["account_said"] == "account madswan"

    def test_a_session_the_hosts_file_names_no_account_for_says_so(self):
        """fleet-page "No account named": never blank (read.2); swancloud's operator's session names none."""
        deneb = next(h for h in of(fleet(), "swancloud")["hosts"] if h["host"] == "deneb")
        assert [(s["session"], s["account"], s["account_said"]) for s in deneb["sessions"] if s["session"] == "swancloud-3"] == [
            ("swancloud-3", None, "no account named in herdr-hosts")]

    def test_the_main_levels_host_is_listed_when_the_board_did_not_ask_it_and_said_not_asked(self):
        """wldn's main level runs on mac-studio, which the board did not ask; chuck-herdr-alpha, where its runner takes
        its work, holds none of its agents."""
        hosts = {h["host"]: h for h in of(fleet(), "wldn")["hosts"]}
        assert list(hosts) == ["chuck-herdr-alpha", "mac-studio"]
        assert (hosts["mac-studio"]["answered"], hosts["mac-studio"]["said"]) == (None, "not asked")
        assert [(s["session"], s["agents"]) for s in hosts["mac-studio"]["sessions"]] == [("wldn", ["wldn-design", "wldn-planner", "wldn-ops", "wldn-operator", "wldn-reviewer"])]
        assert hosts["chuck-herdr-alpha"]["sessions"] == []


class TestKits:
    def kits(self):
        return {k["kit"]: k for k in of(fleet(), "swancloud")["kits"]}

    def test_each_kit_once_in_the_boards_order_naming_no_team(self):
        """The partition's kits, the repositories its plan and its landings name (plan.partition_kits), as the board read them."""
        assert list(self.kits()) == ["crew", "swancloud"] and not any("teams" in k for k in self.kits().values())

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
        b = dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True}, kits=["switchboard-kit"],
                                         construction=[ledger("s", "switchboard-kit", "waits", [unit("s1", "merged")])])])
        k, = of(fleet(b), "wldn")["kits"]
        assert k["said"] == ["no landing since 2026-10-16", "s waits to land, no card open"]
        assert of(fleet(dict(BOARD, partitions=[part("wldn", {"chuck-herdr-alpha": True}, kits=["switchboard-kit"])])), "wldn")["kits"][0]["said"][1] == "nothing queued"


class TestNoTeams:
    def test_a_partitions_block_names_no_team_slot_or_conductor(self):
        """fleet-page, the removed "Each partition shows its teams and how busy each is" and "Each team shows what each of
        its slots is doing" (Decision 11 of the-team-machinery-leaves)."""
        d = fleet()
        words = json.dumps(d)
        assert not any("teams" in p for p in d["partitions"])
        assert '"slot' not in words and "conductor" not in words and "team" not in words.replace("teams file", "")


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

    def test_served_as_index_html_each_partition_is_its_label_html_and_a_subscriptions_its_dock_there(self):
        """fleet-page "Served beside the partitions' pages": wldn's name links to wldn.html, and swancloud on the
        madswan subscription to swancloud's page with madswan's dock open."""
        links = page.fleet_links(PurePath("/srv/board/index.html"), self.LABELS)
        assert links == {"madswan": "madswan.html", "swancloud": "swancloud.html", "wldn": "wldn.html"}
        d = fleet()
        page.linked(d, links)
        m = next(s for s in d["subscriptions"]["items"] if s["account"] == "madswan")
        assert of(d, "wldn")["link"] == "wldn.html" and {"label": "swancloud", "link": "swancloud.html#dock=subscription:madswan"} in m["partitions"]

    def test_written_as_page_html_each_partition_is_its_folders_page(self):
        """fleet-page "Crew's own layout": wldn's name links to wldn/page.html."""
        assert page.fleet_links(PurePath("/h/.local/state/crew/page.html"), self.LABELS)["wldn"] == "wldn/page.html"

    def test_a_name_that_says_no_layout_links_no_partition_and_no_subscriptions_dock(self):
        """fleet-page "A name that says no layout": crew cannot tell where the pages are (read.1)."""
        assert page.fleet_links(PurePath("/srv/fleet.html"), self.LABELS) is None
        d = fleet()
        page.linked(d, None)
        assert {p["link"] for p in d["partitions"]} == {None}
        assert {p["link"] for s in d["subscriptions"]["items"] for p in s["partitions"]} == {None}


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


def subs(*readings, now=NOW, logs=LOGS):
    rs, _ = page.usage_checked({h: published(h, *[r for x, r in readings if x == h]) for h in dict.fromkeys(x for x, _ in readings)})
    return {s["account"]: s for s in page.subscriptions(FLEET, rs, now)}


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


class TestOnASubscription:
    def test_two_partitions_on_one_subscription_each_session_with_its_agents(self):
        """fleet-page "Two partitions on one subscription" and "A session crew runs nothing in": madswan's main level in
        deneb's madswan, swancloud's but its operator in its swancloud, and agentplot-2 running none."""
        m = subs()["madswan"]
        assert [(s["host"], s["session"], s["agents"], s["said"]) for s in m["sessions"]] == [
            ("deneb", "madswan", ["madswan-design", "madswan-planner", "madswan-ops", "madswan-operator", "madswan-reviewer"],
             "madswan-design, madswan-planner, madswan-ops, madswan-operator, madswan-reviewer"),
            ("deneb", "swancloud", ["swancloud-design", "swancloud-planner", "swancloud-ops", "swancloud-reviewer"],
             "swancloud-design, swancloud-planner, swancloud-ops, swancloud-reviewer"),
            ("deneb", "agentplot-2", [], "runs no crew agent")]
        assert not any("teams" in s for s in m["sessions"])
        assert (m["partitions"], m["sessions_said"], m["partitions_said"]) == ([{"label": "madswan", "link": None}, {"label": "swancloud", "link": None}], None, None)

    def test_a_session_no_agent_runs_in_and_one_with_no_account_on_no_subscription(self):
        s = subs()
        assert [(x["host"], x["session"], x["said"]) for x in s["madswan-2"]["sessions"]] == [("deneb", "swancloud-2", "runs no crew agent")]
        assert (s["madswan-2"]["partitions"], s["madswan-2"]["partitions_said"]) == ([], "no partition's agents run on it")
        assert [(x["host"], x["session"], x["agents"]) for x in s["ia"]["sessions"]] == [("chuck-herdr-alpha", "wldn-1", [])]
        assert [(x["host"], x["session"]) for x in s["willdan-alex"]["sessions"]] == [("mac-studio", "wldn")]
        assert all(x["session"] != "swancloud-3" for v in s.values() for x in v["sessions"])

    def test_a_subscription_no_session_runs_on_says_so(self):
        f = subs(("deneb", made("fable-test", ago(3))))["fable-test"]
        assert (f["sessions"], f["sessions_said"], f["partitions"], f["partitions_said"]) == (
            [], "no session of herdr-hosts is on it", [], "no partition's agents run on it")

    def test_where_a_partition_runs_reads_the_same_placement(self):
        assert page.agents_in(FLEET, "swancloud") == {
            ("deneb", "swancloud"): ["swancloud-design", "swancloud-planner", "swancloud-ops", "swancloud-reviewer"],
            ("deneb", "swancloud-3"): ["swancloud-operator"]}


class TestTheSection:
    USAGE = {"deneb": published("deneb", MADSWAN, CREDITS),
             "mac-studio": {"file": "/u/mac-studio.json", "why": "it is not JSON: Expecting value: line 1 column 1 (char 0)"}}

    def test_the_fleets_data_holds_the_subscriptions_beside_the_partitions_and_each_unreadable_file(self):
        """fleet-page "A file that is not of the shape": deneb's readings shown, mac-studio's file named."""
        d = fleet(usage=self.USAGE)
        assert list(d) == ["made", "subscriptions", "unread_usage", "partitions"]
        assert d["subscriptions"]["said"] == "as published by deneb"
        assert [(s["account"], s["state"]) for s in d["subscriptions"]["items"]] == [
            ("credits", "unread"), ("ia", "none"), ("madswan", "read"), ("madswan-2", "none"), ("willdan-alex", "none")]
        assert d["unread_usage"] == [{"host": "mac-studio", "file": "/u/mac-studio.json", "why": "it is not JSON: Expecting value: line 1 column 1 (char 0)"}]

    def test_with_nothing_published_each_subscription_says_no_host_published_its_use(self):
        """fleet-page "No use published"."""
        d = fleet()
        assert (d["subscriptions"]["said"], d["unread_usage"]) == ("no host has published any use", [])
        assert {s["state"] for s in d["subscriptions"]["items"]} == {"none"}
        assert fleet(usage={"deneb": self.USAGE["mac-studio"]})["subscriptions"]["said"] == "no published use could be read"

    def test_a_subscriptions_partitions_link_to_their_pages_at_its_dock(self):
        d = fleet()
        page.linked(d, page.fleet_links(PurePath("/srv/board/index.html"), ["madswan", "swancloud", "wldn"]))
        m = next(s for s in d["subscriptions"]["items"] if s["account"] == "madswan")
        assert m["partitions"] == [{"label": "madswan", "link": "madswan.html#dock=subscription:madswan"},
                                   {"label": "swancloud", "link": "swancloud.html#dock=subscription:madswan"}]
        page.linked(d, None)
        assert {p["link"] for s in d["subscriptions"]["items"] for p in s["partitions"]} == {None}

    def test_the_section_stands_above_the_partitions_sets_every_text_as_text_and_loads_nothing(self):
        """fleet-page "Offline", with the subscriptions drawn: a bar's width a number, never markup."""
        out, block, rest = TestFile().rendered(fleet(usage=self.USAGE))
        assert rest.index('<section class="subs"') < rest.index('<main class="fleet"')
        assert json.loads(block)["subscriptions"]["items"][2]["windows"][0]["said"] == "five-hour 34%, resets 14:00Z"
        for no in ("innerHTML", "outerHTML", "innerText", "insertAdjacentHTML", "document.write", "fetch(", "XMLHttpRequest", "WebSocket",
                   "EventSource", "src=", "<link", "url(", "cssText", "setAttribute(\"style\""):
            assert no not in rest, no
        script = rest[rest.index("// The subscriptions:"):rest.index('var fleet = document.getElementById("fleet")')]
        assert "textContent" in script and re.findall(r"\.style\.\w+ = [^;]*", script) == ['.style.width = Number(w.pct) + "%"']

    def test_an_unread_reason_is_kept_as_text_and_cannot_end_the_data_block(self):
        why = "</script><b>here</b> & more"
        usage = {"deneb": published("deneb", dict(CREDITS, unread=why)), "box": {"file": "/u/box.json", "why": why}}
        out, block, rest = TestFile().rendered(fleet(usage=usage))
        data = json.loads(block)
        assert "<b>here</b>" not in block and out.count("</script>") == 2
        assert data["unread_usage"][0]["why"] == why and data["subscriptions"]["items"][0]["others"][0]["unread"] == why

    def test_the_subscriptions_sit_side_by_side_and_stack_under_760_px(self):
        rest = TestFile().rendered()[2]
        assert "grid-template-columns:repeat(auto-fit,minmax(300px,1fr))" in rest
        assert re.search(r"@media \(max-width:759px\)\{[^@]*?\.subs-grid\{grid-template-columns:1fr", rest, re.S)

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

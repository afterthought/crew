"""The run record (record.1 to record.4, the run-record spec): record.emit appending an entry to the host's file of the
day, record.carry making the branch's copy the union by Id, record.parse and line reading and printing entries, the
events crew events shows, the history crew trace walks, the hosts a partition runs on, and the act and objects each
plan command's entry names. That a write's commit names its entry and carries the host's record, that crew events
reads the branch then each host, that a carried file failing recfix refuses its write, and that --follow tails every
host are the state journey's (t-journey-state). A file written is no process, so these are logic cases."""
import json

import pytest

from facts import FLEET, FactsWrite, known, plan_text

import crew
import plan
import record

KIT = "switchboard-kit"
TE = "tenant-environments"
BOX = "chuck-herdr-alpha"


@pytest.fixture
def here(tmp_path, monkeypatch):
    """This host, mac-studio, its run record under tmp_path, and no session unless a case sets one."""
    monkeypatch.setattr(record, "ROOT", tmp_path / "crew")
    monkeypatch.setattr(record, "_session", ...)
    monkeypatch.setattr(crew, "this_host", lambda: "mac-studio")
    monkeypatch.setenv("CREW_SESSION", "")
    monkeypatch.delenv("CREW_AGENT", raising=False)
    return tmp_path / "crew" / "wldn" / "runs" / "mac-studio"


def entry(eid, at, act, on=(), frm=(), **f):
    return dict(dict(Id=eid, At=at, Act=act, On=list(on), From=list(frm), Commit=[]), **f)


class TestEmit:
    def test_an_entry_goes_in_the_hosts_file_of_the_day_after_the_descriptor_naming_who_asked(self, here, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "wldn-planner")
        monkeypatch.setenv("CREW_SESSION", "chuck-herdr-alpha:sid-1")
        eid = record.emit("wldn", "unit.add", ["unit/a", "queue/switchboard-kit"], frm=["signals/x/01-y"], commit=["r@abc"], why="plan(queue): add a")
        f, = here.glob("*.rec")
        text = f.read_text()
        assert text.startswith(record.DESCRIPTOR) and f.name == f"{eid[:4]}-{eid[4:6]}-{eid[6:8]}.rec" and "-mac-studio-" in eid
        e, = record.parse(text)
        assert (e["By"], e["Session"], e["Host"], e["Act"], e["On"], e["From"], e["Commit"], e["Why"]) == (
            "wldn-planner", "chuck-herdr-alpha:sid-1", "mac-studio", "unit.add", ["unit/a", "queue/switchboard-kit"], ["signals/x/01-y"], ["r@abc"],
            "plan(queue): add a")

    def test_the_users_entry_names_them_at_this_host_with_no_session(self, here):
        import getpass
        record.emit("wldn", "test.user")
        e, = record.parse(next(here.glob("*.rec")).read_text())
        assert e["By"] == f"{getpass.getuser()}@mac-studio" and "Session" not in e

    def test_a_record_that_cannot_be_written_is_said_once_and_changes_nothing_else(self, here, tmp_path, capsys):
        (tmp_path / "crew").mkdir()
        (tmp_path / "crew").chmod(0o555)
        try:
            assert record.emit("wldn", "state.init", ["plan/wldn"]) is None
        finally:
            (tmp_path / "crew").chmod(0o755)
        err = capsys.readouterr().err.strip().splitlines()
        assert len(err) == 1 and err[0].startswith(f"crew: the run record at {tmp_path}/crew/wldn/runs/mac-studio/") and "could not be written" in err[0]

    def test_a_commits_subject_is_its_entrys_why_without_the_agent(self):
        assert record.subject("plan(b): add x (chuck@mac-studio)\n\nbody") == "plan(b): add x"


class TestCarry:
    def write(self, here, day, *ids):
        here.mkdir(parents=True, exist_ok=True)
        (here / f"{day}.rec").write_text(record.DESCRIPTOR + "".join(f"\nId: {i}\nAt: {day}T10:00:00Z\nAct: x\n" for i in ids))

    def test_the_branchs_copy_of_a_day_is_the_union_by_id_in_id_order(self, here):
        self.write(here, "2026-10-12", "20261012T100000Z-mac-studio-1-2", "20261012T100000Z-mac-studio-1-3")
        branch = record.DESCRIPTOR + "\nId: 20261012T100000Z-mac-studio-1-1\nAt: 2026-10-12T10:00:00Z\nAct: x\n"
        out, newest = record.carry("wldn", lambda path: branch)
        text, = out.values()
        assert list(out) == ["runs/mac-studio/2026-10-12.rec"] and newest == "20261012T100000Z-mac-studio-1-3"
        assert [e["Id"][-1] for e in record.parse(text)] == ["1", "2", "3"]

    def test_a_day_the_branch_already_holds_whole_is_left_out(self, here):
        self.write(here, "2026-10-12", "20261012T100000Z-mac-studio-1-1")
        assert record.carry("wldn", lambda path: (here / "2026-10-12.rec").read_text())[0] == {}

    def test_days_before_the_newest_carried_are_not_looked_at(self, here):
        self.write(here, "2026-10-10", "20261010T100000Z-mac-studio-1-1")
        self.write(here, "2026-10-12", "20261012T100000Z-mac-studio-1-1")
        record.mark_carried("wldn", "20261011T000000Z-mac-studio-9-9")
        assert list(record.carry("wldn", lambda path: None)[0]) == ["runs/mac-studio/2026-10-12.rec"]

    def test_a_host_that_lost_its_record_keeps_the_branchs_entries_beside_its_new_ones(self, here):
        branch = record.DESCRIPTOR + "".join(f"\nId: 20261012T09000{i}Z-mac-studio-1-1\nAt: 2026-10-12T09:00:00Z\nAct: x\n" for i in range(3))
        self.write(here, "2026-10-12", "20261012T100000Z-mac-studio-2-1")
        text, = record.carry("wldn", lambda path: branch)[0].values()
        assert len(record.parse(text)) == 4


E = [entry("20261005T100000Z-box-1-1", "2026-10-05T10:00:00Z", "capture", ["signals/s/01-c"], Session="chuck-herdr-alpha:sid-c2",
           Commit=["WilldanGroup/willdan-blueprints@aaaaaaaa11"], By="swb-2-conductor", Host=BOX),
     entry("20261005T100500Z-box-1-2", "2026-10-05T10:05:00Z", "capture", ["signals/s/02-other"]),
     entry("20261005T103000Z-mac-1-1", "2026-10-05T10:30:00Z", "unit.add", ["unit/u", "queue/switchboard-kit"], ["signals/s/01-c"]),
     entry("20261005T103001Z-mac-1-2", "2026-10-05T10:30:01Z", "signal.move", ["signals/s/01-c", "unit/u"]),
     entry("20261005T104000Z-mac-2-1", "2026-10-05T10:40:00Z", "unit.move", ["unit/u", "bolt/b1"], ["queue/switchboard-kit"]),
     entry("20261005T104100Z-mac-3-1", "2026-10-05T10:41:00Z", "unit.add", ["unit/other", "bolt/b1"]),
     entry("20261005T104200Z-mac-4-1", "2026-10-05T10:42:00Z", "bolt.give", ["bolt/b1", "team/swb-1"]),
     entry("20261005T110000Z-box-2-1", "2026-10-05T11:00:00Z", "stage.start", ["stage/u/construct", "unit/u", "agent/swb-1-unit-1"],
           Session="chuck-herdr-alpha:sid-9", By="swb-1-conductor", Host=BOX),
     entry("20261005T113000Z-box-3-1", "2026-10-05T11:30:00Z", "stage.end", ["stage/u/construct", "unit/u", "agent/swb-1-unit-1"], Result="review", Head="bbbbbbb"),
     entry("20261005T123000Z-box-6-1", "2026-10-05T12:30:00Z", "stage.start", ["stage/other/construct", "unit/other", "agent/swb-1-unit-2"])]


class TestTrace:
    def test_a_signals_trace_and_its_units_are_one_chain_and_nothing_else_comes_in(self):
        acts = lambda start: [e["Act"] for e in record.lineage(E, start)]
        assert acts("signals/s/01-c") == ["capture", "unit.add", "signal.move", "unit.move", "stage.start", "stage.end"]
        assert record.lineage(E, "unit/u") == record.lineage(E, "signals/s/01-c")

    def test_a_bare_name_is_tried_as_a_unit_then_a_chore_then_a_bolt_then_a_signal(self):
        assert record.trace_start(E, "u") == ("unit/u", ["unit/u", "chore/u", "bolt/u", "signals/u"])
        assert record.trace_start(E, "b1")[0] == "bolt/b1"
        assert record.trace_start(E, "agenda/8") == (None, ["agenda/8"])
        chore = [entry("20261005T120000Z-mac-5-1", "2026-10-05T12:00:00Z", "chore.add", ["chore/bump", "bolt/b1"])]
        assert record.trace_start(E + chore, "bump")[0] == "chore/bump"

    def test_where_a_chore_moved_from_is_not_what_it_came_from(self):
        moved = [entry("20261005T120000Z-mac-5-1", "2026-10-05T12:00:00Z", "chore.add", ["chore/bump", "queue/switchboard-kit"]),
                 entry("20261005T120100Z-mac-5-2", "2026-10-05T12:01:00Z", "chore.move", ["chore/bump", "bolt/b1"], ["queue/switchboard-kit"])]
        assert [e["Act"] for e in record.lineage(E + moved, "chore/bump")] == ["chore.add", "chore.move"]

    def test_a_line_names_its_time_act_who_host_commit_objects_and_session_to_open(self):
        assert record.line(E[0], zoe=True) == ("10-05 10:00:00  capture       swb-2-conductor      chuck-herdr-alpha  aaaaaaa  signals/s/01-c"
                                              "  zoe sid-c2 on chuck-herdr-alpha")
        assert record.line(E[2]).endswith("unit/u queue/switchboard-kit ← signals/s/01-c")
        assert record.line(E[8]).endswith(" → review at bbbbbbb")
        assert record.line(entry("x", "2026-10-05T10:00:00Z", "tell", ["agent/wldn-planner"], Chars="12")).endswith("(12 characters)")
        assert record.line(entry("x", "2026-10-05T10:00:00Z", "unit.drop", ["unit/a"], Refused="no unit a")).endswith("  refused: no unit a")
        assert record.line(entry("x", "2026-10-05T10:00:00Z", "bolt.land", ["bolt/b", "unit/a"], Repo="switchboard-kit", Head="c" * 40)).endswith(
            "bolt/b unit/a → switchboard-kit main at ccccccc")


class TestEvents:
    def test_events_are_shown_from_a_time_narrowed_to_one_object_and_each_silent_host_named(self):
        out = record.events_text(E, {BOX: "ssh: timed out"}, "2026-10-05T10:40:00Z", "unit/u").splitlines()
        assert [l.split()[2] for l in out[:-1]] == ["unit.move", "stage.start", "stage.end"]
        assert out[-1] == f"{BOX} did not answer: ssh: timed out"

    def test_as_json_the_entries_and_what_did_not_answer(self):
        got = json.loads(record.events_text(E, {}, "0000", None, as_json=True))
        assert [e["Act"] for e in got["entries"]][:2] == ["capture", "capture"] and got["unreachable"] == {}

    def test_a_partition_runs_on_its_teams_hosts_and_its_main_levels(self):
        fleet = {"partitions": {"wldn": dict(FLEET["partitions"]["wldn"], teams=["swb-1", "swb-2"], partition="willdan")},
                 "teams": FLEET["teams"], "hosts": {"laptop": {"sessions": {"wldn": {"partition": "willdan"}}}}}
        assert record.hosts_of(fleet, "wldn") == [BOX, "laptop", "mac-studio"]


class TestPlanEntries:
    W = plan_text(bolts=[(TE, KIT, None), ("apex-zones", KIT, None)], units=[("a", KIT, TE, []), ("b", KIT, TE, []), ("q", KIT, None, [])])

    def op(self, do):
        w = FactsWrite(self.W)
        a = plan.do_args("wldn", do)
        op = plan.OPS[(a.cmd, a.sub)](known(w), a)
        op.change(w)
        return op.act, op.on + w.on, op.frm + w.frm, op.subject

    @pytest.mark.parametrize("do, act, on, frm", [
        (f'bolt new consoles "Consoles." --repo {KIT}', "bolt.new", ["bolt/consoles"], []),
        ("bolt order apex-zones --first", "bolt.order", ["bolt/apex-zones"], []),
        ('bolt drop apex-zones "Not now."', "bolt.drop", ["bolt/apex-zones"], []),
        (f'unit add c "Unit c." --bolt {TE}', "unit.add", ["unit/c", f"bolt/{TE}"], []),
        (f'unit add r "Queued." --repo {KIT}', "unit.add", ["unit/r", f"queue/{KIT}"], []),
        ('unit split q "Narrowed." --into q2 "The rest."', "unit.split", ["unit/q", "unit/q2"], ["unit/q"]),
        ("unit order b --first", "unit.order", ["unit/b", f"bolt/{TE}"], []),
        ("unit after a b", "unit.after", ["unit/a", f"bolt/{TE}"], []),
        (f"unit move q {TE}", "unit.move", ["unit/q", f"bolt/{TE}"], [f"queue/{KIT}"]),
        ('unit drop b "No longer wanted."', "unit.drop", ["unit/b", f"bolt/{TE}"], []),
    ], ids=lambda x: x if isinstance(x, str) and " " not in x else None)
    def test_each_plan_write_is_one_entry_naming_its_act_and_objects_and_none_of_its_typed_text(self, do, act, on, frm):
        got_act, got_on, got_frm, subject = self.op(do)
        assert (got_act, got_on, got_frm) == (act, on, frm)
        for typed in ("Consoles.", "Not now.", "Unit c.", "Queued.", "Narrowed.", "The rest.", "No longer wanted."):
            assert typed not in subject

    def test_a_bolts_add_and_drop_say_so_in_their_why(self):
        assert self.op(f'bolt new consoles "Consoles." --repo {KIT}')[3] == "plan(consoles): add the bolt"
        assert self.op('bolt drop apex-zones "Not now."')[3] == "plan(apex-zones): drop the bolt"

    def test_a_refused_command_names_what_its_command_line_names(self):
        assert plan.named(plan.parser().parse_args(["unit", "drop", "a", "Gone."])) == ["unit/a"]
        assert plan.named(plan.parser().parse_args(["bolt", "give", "swb-1", TE])) == [f"bolt/{TE}", "team/swb-1"]
        assert plan.named(plan.parser().parse_args(["state", "init", "wldn"])) == ["plan/wldn"]


class TestStateInit:
    def plan_of(self, *recs):
        return plan.Plan(plan_text(bolts=[r for r in recs if len(r) == 3], units=[r for r in recs if len(r) == 4]))

    def test_two_plans_sharing_a_name_refuse_the_init_before_anything_is_pushed(self):
        a = self.plan_of(("site-refresh", "swancloud", None), ("the-home-page-loads-fast", "swancloud", "site-refresh", []))
        b = self.plan_of(("flywheel-loop", "flywheel-next", None), ("the-home-page-loads-fast", "flywheel-next", None, []))
        assert plan.shared_name("madswan", [("afterthought/blueprints", a), ("agentplot/blueprints", b)]) == (
            "plan/madswan of afterthought/blueprints and plan/madswan of agentplot/blueprints both hold unit the-home-page-loads-fast: "
            "rename one in its plan first; nothing was written")
        assert plan.shared_name("madswan", [("afterthought/blueprints", a)]) is None

    def test_a_joined_plans_records_follow_the_branchs_their_sources_naming_where_they_came_from(self):
        have = plan.Plan(plan_text(bolts=[("site-refresh", "swancloud", None)]))
        other = plan.Plan(plan_text(bolts=[("flywheel-loop", "flywheel-next", None)], units=[("the-loop-turns", "flywheel-next", None, [])])
                          .replace("Goal of flywheel-loop.\n", "Goal of flywheel-loop.\nSource: design/loop.md\nSource: x/y:z.md\n"))
        plan.joined_into(have, other, "agentplot/blueprints", "madswan/main of afterthought/crew-state", "madswan")
        assert [b.name() for b in have.bolts()] == ["site-refresh", "flywheel-loop"] and have.unit("the-loop-turns")
        assert have.bolt("flywheel-loop").all("Source") == ["agentplot/blueprints:design/loop.md", "x/y:z.md"]
        with pytest.raises(plan.Refusal, match="^madswan/main of afterthought/crew-state already holds bolt flywheel-loop, which plan/madswan of agentplot"):
            plan.joined_into(have, other, "agentplot/blueprints", "madswan/main of afterthought/crew-state", "madswan")

    def test_a_new_moves_file_starts_with_crews_descriptor_and_the_moves_it_adopts(self):
        m = plan.Rec("Move", [("Signal", "2026-10-01-standup/01-noise"), ("Move", "drop"), ("Reason", "a greeting"), ("Date", "2026-10-01"), ("By", "d")])
        text = plan.moves_file([m])
        assert text.startswith(plan.MOVES) and [r.get("Signal") for r in plan.Plan(text).recs("Move")] == ["2026-10-01-standup/01-noise"]
        assert plan.moves_file([]) == plan.MOVES

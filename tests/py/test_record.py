"""The run record (record.1 to record.4, the run-record spec): record.emit appending an entry to the host's file of the
day and asking for its push, record.reach saying a push that is refused, record.unpushed giving the entries the branch
lacks with each day's file as the union by Id and record.entry_message each one's commit, record.parse and line reading
and printing entries, the events crew events shows, read from the branch alone, the history crew trace walks, and
the act and objects each plan command's entry names. That a write's entry follows its commit, that a refused push goes
with the host's next, that crew events and crew trace read the branch and ask no host, and that --follow follows the
branch are the state journey's (t-journey-state). A file written is no process, so these are logic cases."""
import json

import pytest

from facts import FLEET, FactsWrite, known, plan_text

import crew
import plan
import record

KIT = "switchboard-kit"
TE = "tenant-environments"
BOX = "chuck-herdr-alpha"
REACH = record.reach  # the push itself, which conftest stands in for in every case


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

    def test_an_entry_is_pushed_to_its_branch_before_emit_returns(self, here, pushed):
        assert record.emit("wldn", "tell", ["agent/wldn-planner"], Chars="5") and pushed == ["wldn"]
        assert record.emit(None, "tell") is None and pushed == ["wldn"]

    def test_a_push_that_is_refused_is_said_once_and_emit_still_returns_its_id(self, here, monkeypatch, capsys):
        monkeypatch.setattr(record, "reach", REACH)
        monkeypatch.setattr(crew, "load", lambda: FLEET)
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("WilldanGroup/crew-state", f"{label}/main"))

        def unreachable(repo, ref, fresh=False):
            raise crew.Refusal(f"could not fetch {ref} of {repo} over https: fatal: unable to access\n'https://github.com/': timed out")
        monkeypatch.setattr(plan, "fetch", unreachable)
        eid = record.emit("wldn", "stage.start", ["stage/a/construct"])
        assert eid and [e["Id"] for e in record.parse(next(here.glob("*.rec")).read_text())] == [eid]
        assert capsys.readouterr().err.splitlines() == [
            f"crew: entry {eid} did not reach wldn/main of WilldanGroup/crew-state: could not fetch wldn/main of WilldanGroup/crew-state "
            "over https: fatal: unable to access 'https://github.com/': timed out; mac-studio keeps it and pushes it with its next entry"]

    def test_a_push_by_hand_that_is_refused_is_the_commands_refusal(self, here, monkeypatch):
        monkeypatch.setattr(record, "reach", REACH)

        def missing():
            raise crew.Refusal("/x/teams.json is missing; the machine's configuration writes it")
        monkeypatch.setattr(crew, "load", missing)
        with pytest.raises(crew.Refusal, match="^nothing reached wldn/main: /x/teams.json is missing"):
            record.reach("wldn")

    def test_a_fetch_that_lost_the_caches_ref_to_another_command_on_this_host_is_made_again(self, monkeypatch):
        """Every act pushes its entry, so two commands on one host fetch the branch into crew's cache side by side, and
        git refuses the one whose ref the other moved meanwhile: it fetches again, and refuses only what is no race."""
        import types
        calls = []

        def git(repo, *args, input=None, env=None, check=True):
            calls.append(args[0])
            if args[0] == "rev-parse":
                return "c" * 40
            lost = calls.count("fetch") < 3
            return types.SimpleNamespace(returncode=1 if lost else 0, stdout="", stderr=(
                "error: cannot lock ref 'refs/crew/wldn/main': is at aaaa but expected bbbb" if lost else ""))
        monkeypatch.setattr(plan, "git", git)
        monkeypatch.setattr(plan, "READ", plan.Reading())
        monkeypatch.setattr(plan.time, "sleep", lambda s: None)
        assert plan.fetch("WilldanGroup/crew-state", "wldn/main") == "c" * 40 and calls == ["fetch", "fetch", "fetch", "rev-parse"]

        def refused(repo, *args, input=None, env=None, check=True):
            calls.append(args[0])
            return types.SimpleNamespace(returncode=128, stdout="", stderr="fatal: unable to access 'https://github.com/': timed out")
        calls.clear()
        monkeypatch.setattr(plan, "git", refused)
        with pytest.raises(crew.Refusal, match="^could not fetch wldn/main of WilldanGroup/crew-state over https: fatal: unable"):
            plan.fetch("WilldanGroup/crew-state", "wldn/main", fresh=True)
        assert calls == ["fetch"]

    def test_the_entries_of_one_second_sort_as_they_were_made_whichever_process_made_each(self):
        import datetime
        t = datetime.datetime(2026, 10, 19, 1, 49, 46, 120000, tzinfo=datetime.timezone.utc)
        post = entry(record.entry_id(t, BOX, 99891, 1), "2026-10-19T01:49:46Z", "card.post", Card="req_1", Key="batch/2", By="wldn-planner")
        close = entry(record.entry_id(t + datetime.timedelta(milliseconds=400), BOX, 352, 1), "2026-10-19T01:49:46Z", "card.close",
                      Card="req_1", Key="batch/2", By="wldn-planner")
        assert post["Id"].startswith("20261019T014946Z-120000-")
        assert [e["Act"] for e in sorted([close, post], key=lambda e: (e["At"], e["Id"]))] == ["card.post", "card.close"]

    def test_a_commits_subject_is_its_entrys_why_without_the_agent(self):
        assert record.subject("plan(b): add x (chuck@mac-studio)\n\nbody") == "plan(b): add x"


class TestUnpushed:
    A, B, C = "20261012T100000Z-mac-studio-1-1", "20261012T100000Z-mac-studio-1-2", "20261012T100000Z-mac-studio-1-3"

    def write(self, here, day, *ids):
        here.mkdir(parents=True, exist_ok=True)
        (here / f"{day}.rec").write_text(record.DESCRIPTOR + "".join(f"\nId: {i}\nAt: {day}T10:00:00Z\nAct: x\n" for i in ids))

    def test_the_entries_the_branch_lacks_come_oldest_first_each_file_holding_those_before_it(self, here):
        self.write(here, "2026-10-12", self.C, self.A, self.B)
        branch = record.DESCRIPTOR + f"\nId: {self.A}\nAt: 2026-10-12T10:00:00Z\nAct: x\n"
        chain, newest = record.unpushed("wldn", lambda path: branch if path == "runs/mac-studio/2026-10-12.rec" else None)
        assert [(eid, path) for eid, _, path, _ in chain] == [(self.B, "runs/mac-studio/2026-10-12.rec"), (self.C, "runs/mac-studio/2026-10-12.rec")]
        assert newest == self.C and chain[0][1].startswith(f"Id: {self.B}\n")
        assert [[e["Id"] for e in record.parse(text)] for *_, text in chain] == [[self.A, self.B], [self.A, self.B, self.C]]
        assert all(text.startswith(record.DESCRIPTOR) for *_, text in chain)

    def test_nothing_is_left_when_the_branch_holds_every_entry(self, here):
        self.write(here, "2026-10-12", self.A, self.B)
        assert record.unpushed("wldn", lambda path: (here / "2026-10-12.rec").read_text())[0] == []

    def test_days_before_the_newest_pushed_are_not_looked_at(self, here):
        self.write(here, "2026-10-10", "20261010T100000Z-mac-studio-1-1")
        self.write(here, "2026-10-12", self.A)
        record.mark_carried("wldn", "20261011T000000Z-mac-studio-9-9")
        assert [eid for eid, *_ in record.unpushed("wldn", lambda path: None)[0]] == [self.A]

    def test_a_host_that_lost_its_record_keeps_the_branchs_entries_beside_its_new_ones(self, here):
        branch = record.DESCRIPTOR + "".join(f"\nId: 20261012T09000{i}Z-mac-studio-1-1\nAt: 2026-10-12T09:00:00Z\nAct: x\n" for i in range(3))
        self.write(here, "2026-10-12", "20261012T100000Z-mac-studio-2-1")
        (_, _, _, text), = record.unpushed("wldn", lambda path: branch)[0]
        assert len(record.parse(text)) == 4

    def test_an_entrys_own_commit_names_it_its_act_and_what_it_acted_on(self):
        text = f"Id: {self.A}\nAt: 2026-10-12T10:00:00Z\nHost: mac-studio\nBy: wldn-planner\nAct: tell\nOn: agent/wldn-planner\nOn: unit/a\nChars: 5\n"
        assert record.entry_message(text, "wldn-planner") == f"runs(mac-studio): tell agent/wldn-planner (wldn-planner)\n\nCrew-Entry: {self.A}\n"
        assert plan.message("runs(mac-studio): tell agent/wldn-planner (wldn-planner)", "", self.A) == record.entry_message(text, "wldn-planner")

    def test_an_entry_with_no_object_and_a_refusal_say_so_in_their_subject(self):
        bare = f"Id: {self.A}\nAt: 2026-10-12T10:00:00Z\nHost: mac-studio\nBy: chuck@mac-studio\nAct: state.init\n"
        assert record.entry_message(bare, "chuck@mac-studio").split("\n")[0] == "runs(mac-studio): state.init (chuck@mac-studio)"
        refused = bare.replace("Act: state.init\n", "Act: unit.drop\nOn: unit/a\nRefused: no unit a in the plans of wldn\n")
        assert record.entry_message(refused, "x").split("\n")[0] == "runs(mac-studio): unit.drop unit/a refused (x)"


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

    def test_a_signals_short_id_is_the_signal_it_numbers_for_a_trace_and_for_events(self):
        assert record.trace_start(E, "signals/s/01") == ("signals/s/01-c", ["signals/s/01"])
        assert record.trace_start(E, "s/02")[0] == "signals/s/02-other"
        assert record.trace_start(E, "signals/s/03") == (None, ["signals/s/03"])
        assert [l.split()[2] for l in record.events_text(E, {}, "0000", "signals/s/01").splitlines()] == ["capture", "unit.add", "signal.move"]
        two = E + [entry("20261005T120000Z-mac-5-1", "2026-10-05T12:00:00Z", "capture", ["signals/s/01-d"])]
        with pytest.raises(crew.Refusal, match=r"^signals/s/01 names 2 signals: signals/s/01-c, signals/s/01-d; give the full id of one$"):
            record.trace_start(two, "signals/s/01")

    def test_trace_and_events_say_in_their_usage_that_a_signal_is_named_by_its_short_id_too(self, capsys):
        for cmd in ("trace", "events"):
            with pytest.raises(SystemExit):
                record.parser().parse_args([cmd, "--help"])
            assert "<capture>/<NN>-<slug>, or its short one, <capture>/<NN>" in " ".join(capsys.readouterr().out.split())

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
    def test_events_are_shown_from_a_time_narrowed_to_one_object_and_a_branch_not_read_named(self):
        out = record.events_text(E, {"wldn/main": "could not fetch wldn/main"}, "2026-10-05T10:40:00Z", "unit/u").splitlines()
        assert [l.split()[2] for l in out[:-1]] == ["unit.move", "stage.start", "stage.end"]
        assert out[-1] == "wldn/main did not answer: could not fetch wldn/main"

    def test_a_follow_prints_what_it_has_not_printed_in_time_order(self):
        assert [e["Id"] for e in record.fresh({E[0]["Id"], E[2]["Id"]}, [E[3], E[2], E[1], E[0]])] == [E[1]["Id"], E[3]["Id"]]
        assert record.fresh({e["Id"] for e in E}, E) == []

    @pytest.mark.parametrize("label, follower, last, now, fetches", [
        ("wldn", "job", None, 0.0, False), ("wldn", "tab", 0.0, 600.0, False), ("wldn", "unknown", 0.0, 600.0, False),
        ("wldn", "none", 0.0, 59.0, False), ("wldn", "none", 0.0, 60.0, True), ("wldn", "none", None, 1.0, True),
        ("madswan", "job", 0.0, 60.0, True), ("madswan", "job", 0.0, 30.0, False), ("madswan", "job", None, 30.0, True)])
    def test_a_follow_fetches_once_a_minute_only_where_the_hosts_follower_does_not_and_at_once_when_told(self, label, follower, last, now, fetches):
        """The run-record spec, Entries can be followed as they are written: the host's follower follows wldn here; last
        None is a follow told to tick (SIGUSR1)."""
        assert record.follow_fetches(label, {"wldn", "swancloud"}, follower, last, now) is fetches

    def test_a_follow_reads_again_only_the_days_files_whose_blob_changed_since_it_began(self):
        was = {"runs/mac-studio/2026-10-27.rec": "a", "runs/mac-studio/2026-10-28.rec": "b", "runs/box/2026-10-28.rec": "c"}
        now = dict(was, **{"runs/mac-studio/2026-10-28.rec": "b2", "runs/box/2026-10-27.rec": "d", "runs/box/2026-10-29.rec": "e",
                           "runs/box/2026-10-28.rec": "c", "runs/README": "f"})
        assert record.changed_files(was, now, "2026-10-28") == ["runs/box/2026-10-29.rec", "runs/mac-studio/2026-10-28.rec"]
        assert record.changed_files(now, now, "2026-10-28") == []
        assert record.changed_files({}, now, "2026-10-28") == ["runs/box/2026-10-28.rec", "runs/box/2026-10-29.rec", "runs/mac-studio/2026-10-28.rec"]

    def test_as_json_the_entries_and_what_did_not_answer(self):
        got = json.loads(record.events_text(E, {}, "0000", None, as_json=True))
        assert [e["Act"] for e in got["entries"]][:2] == ["capture", "capture"] and got["unreachable"] == {}

    def test_the_record_is_read_from_the_branch_alone_and_no_host_is_asked(self, monkeypatch):
        def asked(*a, **k):
            raise AssertionError(f"a host was asked for the run record: {a}")
        monkeypatch.setattr(crew, "on_machine", asked)
        tips = {}

        def branch(fleet, label, since_day, tips=None):
            tips[label] = "c" * 40
            return [E[3], E[0], dict(E[0])]
        monkeypatch.setattr(record, "on_branch", branch)
        found, missing = record.gather(FLEET, ["wldn"], "2026-10-05", tips)
        assert [e["Id"] for e in found] == [E[0]["Id"], E[3]["Id"]] and missing == {} and tips == {"wldn": "c" * 40}

    def test_a_branch_that_cannot_be_fetched_is_the_one_thing_named(self, monkeypatch):
        def refused(fleet, label, since_day, tips=None):
            raise crew.Refusal(f"could not fetch {label}/main of WilldanGroup/crew-state over https: timed out")
        monkeypatch.setattr(record, "on_branch", refused)
        assert record.gather(FLEET, ["wldn"], "2026-10-05") == (
            [], {"wldn/main": "could not fetch wldn/main of WilldanGroup/crew-state over https: timed out"})


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

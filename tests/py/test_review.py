"""A batch's review and a tell (briefs.12, teams.7, teams.11): plan.review_prompt and reading_command for what the
reviewer is sent, plan.batch_due_said for what the planner is told, and crew.tell_refusal for a tell that types
nothing. Which changes are due, and when a batch is, are test_batches'; starting the reviewer, recording the batch and
the tells themselves, the review journey's (t-journey-review). crew.agent_reading for the session a tell reads an
agent's question mark of, herdr's or the one crew recorded in its pane, on herdr's answer and questions.py's as plain
facts."""
import pytest

import crew
import plan

BOX = "chuck-herdr-alpha"
FLEET = {"partitions": {"wldn": {"label": "wldn", "machine": BOX}},
         "teams": {"swb-1": {"name": "swb-1", "machine": BOX, "ssh": BOX, "kit": {"name": "switchboard-kit", "main": "/kit/main"}},
                   "atl-1": {"name": "atl-1", "machine": "mac-studio", "ssh": "mac-studio", "kit": {"name": "atlas-kit", "main": "/atlas/main"}}}}


def test_the_reviewer_is_sent_each_change_due_and_how_to_read_it_at_its_commit_from_the_main_levels_host():
    said = plan.review_prompt(FLEET, "wldn", 1, "/h/reports/batch-wldn-1.md", [("x1", "swb-1", "abc1234", None), ("z1", "atl-1", "def5678", None)])
    assert said.startswith("Review batch 1 of wldn, 2 changes, and write its summary to /h/reports/batch-wldn-1.md. ")
    assert ("x1 (swb-1, switchboard-kit on chuck-herdr-alpha, at abc1234): list its files with `git -C /kit/main ls-tree -r --name-only "
            "abc1234 openspec/changes/x1/` and read each with `git -C /kit/main show abc1234:<path>`.") in said
    assert "z1 (atl-1, atlas-kit on mac-studio, at def5678): list its files with `ssh -o BatchMode=yes mac-studio git -C /atlas/main ls-tree" in said
    assert "[crew]" not in said


def test_the_planner_is_told_which_changes_are_due_and_why():
    assert plan.batch_due_said("wldn", [("x1", "swb-1", "a", None), ("y1", "swb-2", "b", None)], ["2 changes are due, and a batch is every 2"]) == (
        "A batch of wldn's changes is due: x1 (swb-1), y1 (swb-2); 2 changes are due, and a batch is every 2. Start its reviewer with crew "
        "review wldn, and wait for the summary with crew review wldn --wait, which raises the batch's card and its reading "
        "session in your name.")


class TestTell:
    WAIT = "swb-1-conductor is waiting on a question in its pane: nothing was sent; tell it again once the question is answered"

    @pytest.mark.parametrize("status, asking, unread, said", [
        ("blocked", True, None, WAIT), ("idle", True, None, WAIT),
        (None, False, None, f"could not tell swb-1-conductor on {BOX}: it is not up"),
        ("idle", False, f"no host {BOX}",
         f"could not tell swb-1-conductor on {BOX}: no host {BOX}, so crew can't tell whether it is waiting on a question; nothing was sent"),
        ("idle", False, None, None)])
    def test_a_tell_reaches_its_agent_as_a_prompt_or_not_at_all(self, status, asking, unread, said):
        assert crew.tell_refusal("swb-1-conductor", BOX, status, asking, unread) == said

    def read(self, monkeypatch, item, answers):
        """agent_reading of wldn-planner, in wldn-2, on herdr's item and questions.py's answers by their arguments,
        with the arguments it asked."""
        asked = []
        monkeypatch.setattr(crew, "read_agent", lambda fleet, name: (item, None))
        monkeypatch.setattr(crew, "piped", lambda fleet, host, script, what, *args: asked.append(args) or answers[args])
        monkeypatch.setattr(crew, "place_of_agent", lambda fleet, name: (BOX, "wldn-2"))
        return crew.agent_reading({}, "wldn-planner"), asked

    PANE = ("--pane", "wldn-2", "w1:p2", "wldn-planner")

    def test_an_agent_herdr_names_no_session_for_is_read_by_the_session_crew_recorded_in_its_pane(self, monkeypatch):
        got, asked = self.read(monkeypatch, {"agent_status": "idle", "pane_id": "w1:p2"},
                               {self.PANE: {"session": "sid-1", "question": "open", "id": "toolu_01"}})
        assert (got, asked) == (("idle", True, "sid-1", None), [self.PANE])
        got, _ = self.read(monkeypatch, {"agent_status": "idle", "pane_id": "w1:p2"},
                           {self.PANE: {"session": "sid-1", "question": "answered", "id": "toolu_01"}})
        assert got == ("idle", False, "sid-1", None)

    def test_a_session_herdr_names_is_read_as_it_was_and_crews_record_is_not_asked(self, monkeypatch):
        got, asked = self.read(monkeypatch, {"agent_status": "idle", "pane_id": "w1:p2", "agent_session": {"value": "sid-9"}},
                               {("sid-9",): {"question": None}})
        assert (got, asked) == (("idle", False, "sid-9", None), [("sid-9",)])

    @pytest.mark.parametrize("item", [{"agent_status": "idle", "pane_id": "w1:p2"}, {"agent_status": "idle"}])
    def test_an_idle_agent_neither_herdr_nor_crew_names_a_session_for_is_told(self, monkeypatch, item):
        got, _ = self.read(monkeypatch, item, {self.PANE: {"session": None, "question": None}})
        assert got == ("idle", False, None, None)
        monkeypatch.setattr(crew, "agent_reading", lambda fleet, name: got)
        assert crew.tell_refusal("wldn-planner", BOX, *crew.waits_on_question({}, "wldn-planner")) is None

    @pytest.mark.parametrize("answer, unread", [
        (f"crew's reading of its questions on {BOX} failed (boom)", f"crew's reading of its questions on {BOX} failed (boom)"),
        ({"session": 7, "question": None}, f"crew's reading of its questions on {BOX} gave no answer crew reads"),
        ({"session": "sid-1", "question": "maybe"}, f"crew's reading of its questions on {BOX} gave no answer crew reads")])
    def test_a_record_crew_cannot_read_refuses_the_tell_naming_what(self, monkeypatch, answer, unread):
        got, _ = self.read(monkeypatch, {"agent_status": "idle", "pane_id": "w1:p2"}, {self.PANE: answer})
        assert got[1:] in ((False, None, unread), (False, "sid-1", unread))
        assert crew.tell_refusal("wldn-planner", BOX, got[0], got[1], got[3]).startswith(f"could not tell wldn-planner on {BOX}: {unread}")


def test_a_tell_herdr_refused_to_type_says_why_in_crews_words():
    blocked = '{"error": {"code": "agent_blocked", "message": "blocked"}}'
    assert crew.typed_refusal("swb-1-conductor", BOX, blocked) == TestTell.WAIT
    assert crew.typed_refusal("swb-1-conductor", BOX, "") == f"could not tell swb-1-conductor on {BOX}: it is not up"


def test_an_agent_crew_starts_none_by_that_name_is_refused():
    fleet = {"teams": {}, "partitions": {"wldn": {"label": "wldn", "machine": BOX, "session": "wldn-3"}}}
    assert crew.place_of_agent(fleet, "wldn-planner") == (BOX, "wldn-3")
    with pytest.raises(crew.Refusal, match="no agent somebody: crew starts none by that name"):
        crew.place_of_agent(fleet, "somebody")


class TestAReviewerThatRunsAsItsKind:
    """A partition that runs its reviewer as its kind is asked a batch by crew review and handed it back by crew review
    delivered (design Decision 11; review-batches "The planner starts the partition's reviewer" and "A reviewer's run
    hands its batch back"): the batch ask's words, the --wait refusal, the batches a turn took, whether a summary is
    written, and what the delivery records, raises and asks. That the command does it on the stubs is
    t-journey-review's."""
    START = {"Act": "review.start", "Batch": "21", "At": "2026-10-31T10:00:00Z", "Units": "x1:swb-1@abc1234"}

    def fleet(self, **flume):
        return {"partitions": {"wldn": {"label": "wldn", "machine": BOX, "blueprints": ["WilldanGroup/willdan-blueprints"], "roles": {},
                                        "flume": dict(dict.fromkeys(crew.KIND_ROLES, False), **flume)}},
                "teams": FLEET["teams"], "hosts": {}}

    def test_the_batches_a_turn_took_are_its_batch_asks_in_the_order_taken(self):
        held = [{"Id": "1", "Role": "reviewer", "What": "batch", "Names": "batch/21"}, {"Id": "2", "Role": "reviewer", "What": "tell"},
                {"Id": "3", "Role": "reviewer", "What": "batch", "Names": "batch/22"}, {"Id": "4", "Role": "reviewer", "What": "batch", "Names": "x"}]
        turn = {"Took": ["ask/3", "ask/2", "ask/1", "ask/4", "place/7@5", "ask/9"]}
        assert plan.batches_taken(turn, held) == [22, 21]

    def test_a_summary_is_written_once_its_file_is_as_new_as_its_start(self):
        t = plan.utc(self.START["At"]).timestamp()
        assert plan.batch_written(self.START, t) and plan.batch_written(self.START, t + 60)
        assert not plan.batch_written(self.START, t - 1) and not plan.batch_written(self.START, None) and not plan.batch_written(None, t)

    @pytest.fixture
    def asked(self, monkeypatch):
        got = {"asks": [], "emitted": []}
        monkeypatch.setattr(plan, "arrived", lambda fleet, machine: None)
        monkeypatch.setattr(plan, "review_start", lambda fleet, a: dict(N=21, FILE="/h/reports/batch-wldn-21.md", UNITS="x1:swb-1@abc1234",
                                                                        NAMES="x1", PROMPT="Review batch 21 of wldn, 1 change, ..."))
        monkeypatch.setattr(plan, "ask_write", lambda fleet, label, role, what, frm, names=None, key=None, words=None:
                            got["asks"].append((label, role, what, frm, names, key, words)))
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on=(), **f: got["emitted"].append((act, list(on), f.get("Batch"))))
        monkeypatch.setattr(plan, "agent", lambda: "wldn-planner")
        monkeypatch.setattr(plan.crew, "main_holding", lambda *a: pytest.fail("a reviewer that runs as its kind is given no tab"))
        return got

    def test_crew_review_asks_the_reviewer_the_batch_and_opens_no_tab(self, asked, capsys):
        """review-batches, A reviewer that runs as its kind: the ask holds the batch's changes, how to read each and the
        file to write, no tab is opened and no reviewer started by crew."""
        import argparse
        plan.review_cmd(self.fleet(reviewer="wldn-main"), argparse.Namespace(label="wldn", wait=False, timeout=0))
        assert asked["asks"] == [("wldn", "reviewer", "batch", "wldn-planner", "batch/21", "batch/21", "Review batch 21 of wldn, 1 change, ...")]
        assert asked["emitted"] == [("review.start", ["batch/21", "agent/wldn-reviewer", "unit/x1"], 21)]
        assert "wldn-reviewer is asked batch 21 of wldn, into /h/reports/batch-wldn-21.md" in capsys.readouterr().out

    def test_waiting_on_a_reviewer_that_runs_as_its_kind_is_refused(self, asked):
        """review-batches, Waiting on a reviewer that runs as its kind."""
        import argparse
        with pytest.raises(crew.Refusal, match="wldn runs its reviewer as its kind, so crew review --wait waits on nothing: the batch's "
                                               "delivery reaches wldn-planner as an ask"):
            plan.review_cmd(self.fleet(reviewer="wldn-main"), argparse.Namespace(label="wldn", wait=True, timeout=0))
        assert asked["asks"] == [] and asked["emitted"] == []

    ASKS = ("%rec: Ask\n%key: Id\n\nId: 1\nRole: reviewer\nFrom: wldn-planner\nWhat: batch\nNames: batch/21\nKey: batch/21\nAt: 2026-10-31T10:00:00Z\n\n"
            "Id: 2\nRole: reviewer\nFrom: wldn-planner\nWhat: batch\nNames: batch/22\nKey: batch/22\nAt: 2026-10-31T10:00:00Z\n\n"
            "%rec: Turn\n%key: Turn\n\nTurn: 1\nRole: reviewer\nRun: wldn-reviewer\nPlace: crew-reviewer--wldn\nHost: " + BOX +
            "\nTook: ask/1\nTook: ask/2\nBegan: 2026-10-31T10:01:00Z\n")

    @pytest.fixture
    def run(self, monkeypatch, tmp_path):
        """wldn's reviewer's run on its main level's host, its turn having taken batches 21 and 22, each started; the
        delivery's acts kept."""
        import os
        got = {"asks": [], "emitted": [], "raised": [], "told": []}
        monkeypatch.setenv("FLUME_PLACE", "/flume/places/crew-reviewer--wldn")
        monkeypatch.setattr(plan.crew, "this_host", lambda: BOX)
        monkeypatch.setattr(plan, "state_of", lambda fleet, label: ("o/state", f"{label}/main"))
        monkeypatch.setattr(plan, "fetch", lambda repo, ref, fresh=False: "tip")
        monkeypatch.setattr(plan, "show", lambda repo, tip, path: self.ASKS if path == "asks.rec" else None)
        monkeypatch.setattr(plan, "local_entries", lambda label, days=30: [self.START, dict(self.START, Batch="22")])
        monkeypatch.setattr(plan, "batch_file", lambda label, n: tmp_path / f"batch-{label}-{n}.md")
        monkeypatch.setattr(plan.cards, "host_entries", lambda record, label, host: [])
        monkeypatch.setattr(plan.crew, "tell", lambda fleet, name, text, **k: got["told"].append((name, text)) or True)

        def raised(fleet, row, acts=None, note=None):  # as card_heard tells the owner the line that adopts the card
            got["raised"].append(row["key"])
            acts.tell("wldn-planner", f"Your card {row['key']} is up for the user: call get_request (requestId req_1, name wldn-planner), "
                                      "to hear their answer.")
            return "req_1"
        monkeypatch.setattr(plan, "raise_batch", raised)
        monkeypatch.setattr(plan, "ask_write", lambda fleet, label, role, what, frm, names=None, key=None, words=None:
                            got["asks"].append((role, what, frm, names, key, words)))
        monkeypatch.setattr(plan.record, "emit", lambda label, act, on=(), **f: got["emitted"].append((act, list(on), f.get("Batch"))))
        written = tmp_path / "batch-wldn-21.md"
        written.write_text("# Batch 21\n")
        os.utime(written, (plan.utc(self.START["At"]).timestamp() + 60,) * 2)
        return got

    def delivered(self, fleet, label=None):
        import argparse
        plan.review_delivered(fleet, argparse.Namespace(label=label))

    def test_a_batch_delivered_is_recorded_its_card_raised_and_the_planner_asked_and_one_not_written_refused(self, run, tmp_path, capsys):
        """review-batches, A batch delivered and A summary not written."""
        with pytest.raises(crew.Refusal, match=rf"batch 22's summary {tmp_path}/batch-wldn-22.md is not written since its start, so it is not delivered"):
            self.delivered(self.fleet(reviewer="wldn-main", planner="wldn-main"))
        assert run["emitted"] == [("review.batch", ["batch/21", "unit/x1"], 21)]
        assert run["raised"] == ["batch/21"] and run["told"] == []
        (ask,) = run["asks"]
        assert ask[:5] == ("planner", "delivered", "wldn-reviewer", "batch/21", "delivered/21")
        assert ask[5] == (f"Batch 21 of wldn is reviewed, its summary {tmp_path}/batch-wldn-21.md. Your card batch/21 is up for the user: "
                          "call get_request (requestId req_1, name wldn-planner), to hear their answer.")
        assert f"batch 21 of wldn is delivered: {tmp_path}/batch-wldn-21.md" in capsys.readouterr().out

    def test_a_planner_that_stands_is_told_the_card_as_today_and_asked_nothing(self, run, tmp_path):
        (tmp_path / "batch-wldn-22.md").write_text("# Batch 22\n")
        self.delivered(self.fleet(reviewer="wldn-main"))
        assert run["raised"] == ["batch/21", "batch/22"] and run["asks"] == []
        assert [n for n, _ in run["told"]] == ["wldn-planner", "wldn-planner"]

    def test_it_is_refused_anywhere_but_the_reviewers_run(self, run, monkeypatch):
        monkeypatch.setenv("FLUME_PLACE", "/flume/places/crew-planner--wldn")
        with pytest.raises(crew.Refusal, match="crew review delivered runs in a run of a partition's reviewer"):
            self.delivered(self.fleet(reviewer="wldn-main", planner="wldn-main"))
        monkeypatch.delenv("FLUME_PLACE")
        with pytest.raises(crew.Refusal, match="crew review delivered runs in a run of a partition's reviewer"):
            self.delivered(self.fleet(reviewer="wldn-main"))
        assert run["emitted"] == [] and run["asks"] == []

    def test_a_run_with_no_open_turn_has_nothing_to_hand_back(self, run, monkeypatch):
        monkeypatch.setattr(plan, "show", lambda repo, tip, path: self.ASKS.replace("Began:", "Ended: 2026-10-31T10:30:00Z\nSaid: done\nBegan:"))
        with pytest.raises(crew.Refusal, match="wldn-reviewer has no open turn: crew role start takes the batches asked of it first"):
            self.delivered(self.fleet(reviewer="wldn-main"))

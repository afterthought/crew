"""What a stage's run recorded as made reaches its batch's card (rail-cards "A batch's card carries what each unit's
stages recorded as made", "A batch's card changes in place as lines are added"; bolt-teams "A stage's made things are
read from its place", "The conductor's wait keeps a copy of what each stage made"; record 0043): a made line read as
written (cards.made_line) and said under its unit (cards.made_said); the conductor's wait reading the place's
made.jsonl at each look, keeping each new line once under the stage first seen (plan.made_new, made_keep, made_look);
the copies read back by crew _made, and removed when the unit's bolt lands or is dropped (made_drop); and a line kept
for a unit in a batch whose card waits on the user changing that card in place, one kept after the user answered
leaving it as it is."""
import argparse
import json

import pytest

from facts import FLEET, owed, reviewed, card_closed

import cards
import crew
import plan

PAGE = '{"name": "spike", "kind": "page", "address": "https://example.test/spike"}'
DEMO = '{"name": "demo", "kind": "preview", "branch": "bolt/y", "revision": "abc1234"}'
NOTES = '{"name": "notes", "kind": "page", "address": "https://example.test/notes"}'


@pytest.fixture(autouse=True)
def kept(monkeypatch, tmp_path):
    """crew's copies of what stages made, in a scratch folder rather than the host's."""
    monkeypatch.setattr(plan, "MADE", tmp_path / "made")
    monkeypatch.setattr(plan, "PREVIEWS", tmp_path / "previews")
    return tmp_path / "made"


class TestALine:
    """A made line is read as written: a durable thing by its address, a thing that must run by its branch and
    revision, and a line crew can't read carried as its text (design, Decision 2)."""

    def test_a_page_is_its_name_kind_and_address_as_written(self):
        assert cards.made_line(PAGE) == {"name": "spike", "kind": "page", "address": "https://example.test/spike"}

    def test_a_thing_that_must_run_is_its_branch_and_revision(self):
        assert cards.made_line(DEMO) == {"name": "demo", "kind": "preview", "branch": "bolt/y", "revision": "abc1234"}

    def test_a_line_holding_both_keeps_both(self):
        both = '{"name": "site", "kind": "page", "address": "http://s", "branch": "bolt/y", "revision": "abc1234"}'
        assert cards.made_line(both) == {"name": "site", "kind": "page", "address": "http://s", "branch": "bolt/y", "revision": "abc1234"}

    @pytest.mark.parametrize("line", ["spike at https://example.test/spike", "[1, 2]", "7", '{"name": "spike", "address": "http://s"}',
                                      '{"name": 7, "kind": "page"}', '{"name": "s", "kind": "page", "address": 7}'])
    def test_a_line_that_is_no_made_thing_is_carried_as_its_text(self, line):
        """rail-cards "A line crew cannot read as a made thing": no object, or one missing its kind."""
        assert cards.made_line(line) == {"text": line, "unread": True}

    def test_an_empty_address_is_shown_empty_and_a_null_field_left_out(self):
        """read.2: an absent field never becomes text."""
        assert cards.made_line('{"name": "s", "kind": "page", "address": ""}') == {"name": "s", "kind": "page", "address": ""}
        assert cards.made_line('{"name": "s", "kind": "page", "address": null}') == {"name": "s", "kind": "page"}
        said = cards.made_said("a", [("code", ['{"name": "s", "kind": "page", "address": ""}', '{"name": "t", "kind": "page", "address": null}'])])
        assert said == ["- `code`: s, page, at ", "- `code`: t, page"] and not any("None" in s for s in said)

    def test_each_line_is_said_under_its_unit_by_the_stage_that_recorded_it(self):
        """rail-cards "A spike recorded by a code stage" and "A thing that must run"."""
        assert cards.made_said("a", [("code", [PAGE, DEMO]), ("verify", ["not json"])]) == [
            "- `code`: spike, page, at https://example.test/spike",
            "- `code`: demo, preview, brought up from bolt/y at abc1234; write on this card naming a/demo to bring it up",
            "- `verify`: crew could not read this line as a made thing: not json"]

    def test_a_thing_brought_up_lists_its_addresses_and_one_that_could_not_be_says_why(self):
        up = {"head": "abc1234", "name": "preview/0", "state": "up", "addresses": {"web": "http://w"}}
        assert cards.made_said("a", [("code", [DEMO])], {"demo": up}) == [
            "- `code`: demo, preview, brought up from bolt/y at abc1234; up at web http://w; it lands nothing"]
        why = {"head": "abc1234", "why": "no [branches] table in .config/sluice.toml on unit/a names it"}
        assert cards.made_said("a", [("code", [DEMO])], {"demo": why}) == [
            "- `code`: demo, preview, brought up from bolt/y at abc1234; it could not be brought up: no [branches] table in "
            ".config/sluice.toml on unit/a names it"]

    def test_a_durable_thing_with_a_branch_shows_its_address_and_its_branch_beside_it(self):
        both = '{"name": "site", "kind": "page", "address": "http://s", "branch": "bolt/y", "revision": "abc1234"}'
        assert cards.made_said("a", [("code", [both])]) == ["- `code`: site, page, at http://s (from bolt/y at abc1234)"]

    def test_nothing_recorded_says_nothing(self):
        """rail-cards "Nothing recorded"."""
        assert cards.made_said("b", []) == [] and cards.made_said("b", [("code", [])]) == []


class TestTheWait:
    """The conductor's wait reads made.jsonl in the place's git directory at each look and at the stage's end, and keeps
    each new line once, as written, under the stage first seen, on the team's host (design, Decisions 1 and 3)."""
    T = dict(FLEET["teams"]["swb-1"], kit={"name": "switchboard-kit", "main": "/kit/main"})

    def test_a_place_that_recorded_two_things_is_read_in_order_byte_for_byte(self, tmp_path):
        """bolt-teams "A place that recorded two things"."""
        (tmp_path / "made.jsonl").write_text(f"{PAGE}\n\n{DEMO} \n")
        assert plan.made_file(tmp_path / "made.jsonl") == [PAGE, f"{DEMO} "]

    def test_a_place_that_recorded_nothing_reads_nothing(self, tmp_path):
        """bolt-teams "A place that recorded nothing"."""
        assert plan.made_file(tmp_path / "made.jsonl") == []

    def test_a_wait_asks_git_for_the_places_git_directory_once(self, monkeypatch, tmp_path):
        """Decision 1: made.jsonl is in the place's own git directory, which git names once for the wait."""
        asked = []
        monkeypatch.setattr(plan, "kit_git", lambda fleet, t, where, *args: asked.append((where, args)) or (0, str(tmp_path)))
        (tmp_path / "made.jsonl").write_text(f"{PAGE}\n")
        dirs = {}
        assert plan.made_read(FLEET, self.T, "/kit/places/a", dirs=dirs) == [PAGE]
        assert plan.made_read(FLEET, self.T, "/kit/places/a", dirs=dirs) == [PAGE]
        assert asked == [("/kit/places/a", ("rev-parse", "--absolute-git-dir"))]

    def test_a_file_that_cant_be_read_is_refused_naming_it(self, tmp_path):
        (tmp_path / "made.jsonl").write_bytes(b"\xff\xfe not text")
        with pytest.raises(plan.Refusal, match=f"{tmp_path / 'made.jsonl'} can't be read"):
            plan.made_file(tmp_path / "made.jsonl")

    def test_each_line_is_kept_once_however_many_looks_see_it(self):
        """bolt-teams "A line written while the code stage runs"."""
        assert plan.made_new([], [PAGE]) == [PAGE]
        plan.made_keep("wldn", "a", "code", [PAGE])
        assert plan.made_new(plan.made_kept("wldn", "a"), [PAGE]) == []
        assert plan.made_new(plan.made_kept("wldn", "a"), [PAGE, DEMO, DEMO]) == [DEMO]

    def test_a_line_first_seen_at_a_later_stage_is_kept_under_it_and_never_again(self):
        """bolt-teams "A line seen at a later stage"."""
        plan.made_keep("wldn", "a", "verify", plan.made_new(plan.made_kept("wldn", "a"), [PAGE]))
        plan.made_keep("wldn", "a", "code", [DEMO])
        assert plan.made_new(plan.made_kept("wldn", "a"), [PAGE, DEMO]) == []
        assert plan.made_kept("wldn", "a") == [("code", [DEMO]), ("verify", [PAGE])]

    def look(self, monkeypatch, read, entries=(), stage="code"):
        handed = []
        monkeypatch.setattr(plan, "made_read", read)
        monkeypatch.setattr(plan, "partition_entries", lambda fleet, label: list(entries))
        monkeypatch.setattr(plan, "batch_hand", lambda fleet, label, n, note: handed.append((n, note)))
        said = set()
        plan.made_look(FLEET, self.T, owed(stage), "/kit/places/a", said)
        return handed, said

    def test_a_look_keeps_what_the_place_holds_under_the_stage_running(self, monkeypatch):
        handed, _ = self.look(monkeypatch, lambda fleet, t, place, dirs=None: [PAGE, DEMO])
        assert plan.made_kept("wldn", "a") == [("code", [PAGE, DEMO])] and handed == []
        self.look(monkeypatch, lambda fleet, t, place, dirs=None: [PAGE, DEMO, NOTES], stage="verify")
        assert plan.made_kept("wldn", "a") == [("code", [PAGE, DEMO]), ("verify", [NOTES])]

    def test_a_place_with_none_keeps_nothing(self, monkeypatch, kept):
        handed, _ = self.look(monkeypatch, lambda fleet, t, place, dirs=None: [])
        assert not kept.exists() and handed == []

    def test_a_file_that_cant_be_read_is_said_once_and_the_copy_kept(self, monkeypatch, capsys):
        """bolt-teams "The file can't be read"."""
        plan.made_keep("wldn", "a", "code", [PAGE])

        def refused(fleet, t, place, dirs=None):
            plan.fail("/kit/.git/worktrees/a/made.jsonl can't be read: Permission denied")
        said = set()
        monkeypatch.setattr(plan, "made_read", refused)
        for _ in range(3):
            plan.made_look(FLEET, self.T, owed("code"), "/kit/places/a", said)
        assert capsys.readouterr().err == ("what a's code made is not kept yet: /kit/.git/worktrees/a/made.jsonl can't be read: "
                                           "Permission denied\n")
        assert plan.made_kept("wldn", "a") == [("code", [PAGE])]

    def test_a_line_kept_for_a_unit_in_a_batch_whose_card_is_open_hands_the_card_its_note(self, monkeypatch):
        """rail-cards "A line added while the card waits": the card's raise handed to the main machine."""
        handed, _ = self.look(monkeypatch, lambda fleet, t, place, dirs=None: [NOTES], [reviewed(7, [("a", "swb-1", "aaa1"), ("b", "swb-1", "bbb1")])])
        assert handed == [(7, "a recorded notes")]

    def test_a_batch_whose_card_closed_or_that_holds_no_such_unit_is_handed_nothing(self, monkeypatch):
        b7 = reviewed(7, [("a", "swb-1", "aaa1")])
        assert self.look(monkeypatch, lambda fleet, t, place, dirs=None: [NOTES], [b7, card_closed("batch/7", "req_b7")])[0] == []
        plan.made_drop("wldn", ["a"])
        assert self.look(monkeypatch, lambda fleet, t, place, dirs=None: [NOTES], [reviewed(7, [("b", "swb-1", "bbb1")])])[0] == []

    def test_the_newest_batch_holding_the_unit_is_the_one_whose_card_changes(self):
        entries = [reviewed(6, [("a", "swb-1", "aaa1")]), reviewed(7, [("a", "swb-1", "aaa2")])]
        assert plan.batch_open(entries, "a") == 7 and plan.batch_open(entries, "z") is None
        assert plan.batch_open(entries + [card_closed("batch/7", "req_b7")], "a") is None


class TestTheCopies:
    """The copies are read back on their host by crew _made, and go when the unit's bolt lands or is dropped (design,
    Decision 3)."""

    def test_crew_made_prints_each_units_lines_by_stage(self, capsys):
        plan.made_keep("wldn", "a", "code", [PAGE, DEMO])
        plan.made_cmd(FLEET, argparse.Namespace(label="wldn", unit=["a", "b"], card=None, json=True))
        assert json.loads(capsys.readouterr().out) == {"made": {"a": [["code", [PAGE, DEMO]]], "b": []}, "previews": {}}

    def test_another_hosts_answer_is_read_only_in_its_shape(self):
        got = {"made": {"a": [["code", [PAGE]]]}, "previews": {"a/demo": {"head": "abc1234", "why": "x"}}}
        assert plan.made_listed(json.dumps(got)) == got
        for bad in ("", "[]", '{"made": {"a": [["code", [7]]]}, "previews": {}}', '{"made": {}}'):
            with pytest.raises(plan.Refusal, match="crew _made printed nothing crew reads"):
                plan.made_listed(bad)

    def test_the_copies_go_when_the_bolt_lands_or_is_dropped_and_another_units_stay(self, kept):
        """bolt-teams "The place is tidied" and "The bolt lands"."""
        plan.made_keep("wldn", "a", "code", [PAGE])
        plan.made_keep("wldn", "c", "code", [DEMO])
        assert plan.made_kept("wldn", "a") == [("code", [PAGE])]  # the place gone, the copy stands
        assert plan.made_drop("wldn", ["a", "b", "../c"]) == "removed what a recorded as made, kept for its batch's card"
        assert plan.made_kept("wldn", "a") == [] and plan.made_kept("wldn", "c") == [("code", [DEMO])]
        assert plan.made_drop("wldn", ["a"]) is None


class Acts:
    """A stand-in for the act's reach as a batch's raise uses it: the batch's entries on the main level's host, its
    reading's link, what each unit made on its team's host, and Pending You's get_request answered with the card's
    status (status), every other call answered."""
    LINK = "http://mac-studio.ts.swancloud.net:19432"

    def __init__(self, entries, status, made):
        self.held, self.status, self.made_by = list(entries), status, made
        self.calls, self.emitted = [], []

    def session(self, label, key, facts):
        return self.LINK

    def made(self, label, host, units, key):
        return self.made_by

    def bridge(self, name, later, held=None):
        acts = self

        class Py:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

            def answer(self, tool, args):
                acts.calls.append((tool, args))
                if tool == "get_request":
                    return {"status": acts.status, "turn": "you", "version": 2}, None
                return {"ok": True, "version": 3}, None

            def call(self, tool, args):
                return self.answer(tool, args)[0]
        return Py()

    def emit(self, label, act, on, **fields):
        self.emitted.append(dict(fields, Act=act))

    def entries(self, label):
        return self.held

    def put(self, url, data, kind):
        return None

    def host(self):
        return "mac-studio"

    def kits(self, label):
        return ("switchboard-kit",)


class TestTheCardChanges:
    """A line kept for a unit in a batch whose card waits on the user changes that card in place, and one kept after
    the user answered leaves it as it is (design, Decision 4; row_card_change's own rule)."""
    HELD = [reviewed(7, [("a", "swb-1", "aaa1")]),
            {"Act": "card.post", "Key": "batch/7", "By": "wldn-planner", "Card": "req_b7", "On": ["batch/7"]}]

    def raise_(self, monkeypatch, tmp_path, status):
        (tmp_path / "batch-wldn-7.md").write_text("## a (swb-1)\n\na gives each tenant its own zone.\n")
        monkeypatch.setattr(plan, "batch_file", lambda label, n: tmp_path / f"batch-{label}-{n}.md")
        monkeypatch.setattr(plan, "plan_of", lambda fleet, label: None)
        kit = {"name": "switchboard-kit", "repo": "WilldanGroup/switchboard-kit", "main": "/kit/main", "dir": "/kit"}
        fleet = dict(FLEET, teams={t: dict(v, kit=kit) for t, v in FLEET["teams"].items()})
        acts = Acts(self.HELD, status, {"made": {"a": [["code", [NOTES]]]}, "previews": {}})
        plan.raise_batch(fleet, {"label": "wldn", "key": "batch/7"}, acts, note="a recorded notes")
        return acts

    def test_a_card_that_waits_is_changed_in_place_carrying_the_line(self, monkeypatch, tmp_path):
        """rail-cards "A line added while the card waits"."""
        acts = self.raise_(monkeypatch, tmp_path, "pending")
        change = next(a for t, a in acts.calls if t == "update_request")
        assert change["changeNote"] == "a recorded notes" and change["requestId"] == "req_b7"
        face = next(x for x in change["artifacts"] if x.get("lang") == "markdown")
        assert "- `code`: notes, page, at https://example.test/notes" in face["lines"]

    def test_a_card_the_user_answered_is_left_as_it_is(self, monkeypatch, tmp_path, capsys):
        """rail-cards "A line added after the user answered"."""
        acts = self.raise_(monkeypatch, tmp_path, "answered")
        assert [t for t, _ in acts.calls] == ["get_request"]
        assert "card batch/7: req_b7 is left as it is: the user has answered it" in capsys.readouterr().out

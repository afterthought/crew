"""What a stage's run recorded as made reaches its batch's card (rail-cards "A batch's card carries what each unit's
stages recorded as made", "A batch's card changes in place as lines are added"; record 0043): a made line read as
written (cards.made_line) and said under its unit (cards.made_said); and a line kept for a unit in a batch whose card
waits on the user changing that card in place, one kept after the user answered leaving it as it is."""
import pytest

from facts import FLEET, reviewed

import cards
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

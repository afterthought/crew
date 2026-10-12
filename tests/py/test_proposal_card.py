"""A proposal's Pending You card (plan-proposals spec, briefs.9): plan.card_model on the plan at the tip and the plan its
commands leave, and picture.draw for its picture. The logic tier starts no process, so drawing it here proves crew
needs nothing installed to draw it. Posting the card, and where crew writes its picture, are the proposals journey's
(t-journey-plan)."""
import json
import struct
import zlib

import pytest

from facts import FLEET, FactsWrite, apply, plan_text

import picture
import plan

KIT = "switchboard-kit"
LONG = "a-long-unit-name-that-runs-past-the-width-of-a-phone-line"


def fresh():
    return FactsWrite(plan_text(bolts=[("deploys", KIT, None), ("pages", KIT, None)],
                                units=[(u, KIT, "deploys", []) for u in ("a-first", "b-second", "c-third", "d-fourth")]
                                + [("m-move", KIT, "pages", [])]))


def card(n, case, *dos, state=None):
    pl = plan.Plan(plan.PROPOSALS)
    for k in range(1, n + 1):
        plan.open_proposal(pl, k, case, list(dos), "wldn-planner", "2026-10-12")
    p = plan.proposal(pl, n, "wldn")
    if state:
        plan.close(p, state, "2026-10-12", "not now")
    return plan.card_model(FLEET, "wldn", fresh(), p, after=apply(fresh(), *dos).plan)


def png(data):
    """A PNG's width and height, and whether its pixels hold the dropped and the new colours."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    w, h, depth, kind = struct.unpack(">IIBB", data[16:26])
    raw, i = b"", 8
    while i < len(data):
        n, t = struct.unpack(">I4s", data[i:i + 8])
        raw += data[i + 8:i + 8 + n] if t == b"IDAT" else b""
        i += 12 + n
    raw = zlib.decompress(raw)
    rows = [raw[y * (3 * w + 1) + 1:(y + 1) * (3 * w + 1)] for y in range(h)]
    has = lambda c: any(bytes.fromhex(c) in r for r in rows)
    return w, h, (depth, kind), has("e07b4f"), has("8fb9ae")


class TestDropAmendAdd:
    M = None

    @classmethod
    def setup_class(cls):
        cls.M = card(1, "The third unit is not needed. The second needs more. Two units finish the bolt.",
                     'unit drop c-third "Not needed now."', 'unit amend b-second "The second thing, done better."',
                     'unit add e-fifth "The fifth thing is built." --bolt deploys',
                     f'unit add {LONG} "A unit whose name is longer than a phone\'s line." --bolt deploys --before a-first')

    def test_its_title_counts_and_its_summary_says_the_count_before_and_after_and_the_goal(self):
        c = self.M["card"]
        assert c["title"] == "Approve the change to deploys: 1 dropped, 1 amended, 2 new?"
        assert c["summary"] == "Proposal 1, by wldn-planner\n4 units → 5 once approved: 1 dropped, 1 amended, 2 new.\nGoal: Goal of deploys."
        assert c["context"]["background"].startswith("The third unit is not needed. The second needs more. Two units finish the bolt."
                                                     "\n\nChanges:\nDrop unit c-third\nAmend unit b-second in bolt deploys")
        assert [len(c["context"][k]) for k in ("trace", "filesTouched", "tried", "links")] == [0, 0, 0, 0]
        assert (c["intent"], self.M["session"]) == ("approve", False)

    def test_its_text_is_lines_of_at_most_forty_with_a_block_per_change_and_the_order_once_approved(self):
        art = next(a for a in self.M["card"]["artifacts"] if a["kind"] == "code")
        assert (art["lang"], art["title"], art["ref"]) == ("text", "The change, in text", "proposal-1.txt")
        assert max(len(l) for l in art["lines"]) <= 40
        text = "\n".join(art["lines"])
        assert text.startswith("deploys\n4 units → 5")
        for block in ["DROP   c-third\n       Not needed now.", "AMEND  b-second\n       The second thing, done better.",
                      "ADD    e-fifth\n       The fifth thing is built.", "ADD    a-long-unit-name-that-runs-past-\n       the-width-of-a-phone-line\n",
                      "ONCE APPROVED\n 1 + a-long-unit-name-that-runs-past-\n     the-width-of-a-phone-line\n 2   a-first\n 3 ~ b-second\n 4   d-fourth\n 5 + e-fifth"]:
            assert block in text

    def test_it_asks_the_approval_and_one_question_holding_both_new_units_each_recommended(self):
        q = self.M["card"]["questions"]
        assert [f"{x['id']}:{x['kind']}" for x in q] == ["plan:approve", "units-1:multi"]
        assert q[0]["title"] == "Approve the change to deploys?"
        assert q[0]["detail"] == "• The third unit is not needed.\n• The second needs more.\n• Two units finish the bolt."
        assert q[0]["rationale"] == ("To keep the dropped unit or change the amendment, don't approve: say why in a note from ⋯, "
                                     "and the planner writes the proposal again. A note beside an approval changes nothing applied.")
        assert q[0]["approve"] == {"action": "Apply proposal 1, with the new units you keep", "risk": "low", "reversible": True}
        assert q[1]["title"] == "Which new units go in? Clear one to leave it out."
        assert [o["id"] for o in q[1]["options"]] == q[1]["recommendedIds"] == ["e-fifth", LONG]
        assert (q[1]["options"][0]["detail"], q[1]["options"][0]["consequence"]) == ("The fifth thing is built.", "Cleared: not added; the rest still applies")
        assert q[1]["multi"] == {"min": 0, "max": 2}
        assert self.M["card"]["about"] == {"kind": "other", "title": "Proposal 1: deploys"}
        assert "kind" not in self.M["card"] and "approve" not in self.M["card"]

    def test_no_field_holds_a_path_and_the_picture_is_uploaded_by_its_name(self):
        strings = [s for s in json.dumps(self.M["card"]).split('"') if s.startswith(("/", "~")) or "/.local/" in s]
        assert strings == []
        img = next(a for a in self.M["card"]["artifacts"] if a["kind"] == "image")
        assert (img["title"], img["ref"], img["upload"]) == ("The change, once approved", "proposal-1.png", True)

    def test_its_picture_is_a_png_780_wide_with_a_dropped_unit_and_a_new_one_each_in_its_colour(self):
        w, h, form, dropped, new = png(picture.draw(self.M["sections"]))
        assert (w, form, dropped, new) == (780, (8, 2), True, True)


def test_a_proposal_that_makes_no_unit_new_is_a_plain_approval():
    m = card(2, "The first unit changes, and the last goes first.", 'unit amend a-first "The first thing, done again."',
             "unit order d-fourth --first")
    c = m["card"]
    assert c["title"] == "Approve the change to deploys: 1 amended, 1 moved?"
    assert (c["kind"], c.get("questions"), c["recommendedIds"]) == ("approve", None, ["approve"])
    assert c["approve"] == {"action": "Apply proposal 2", "risk": "low", "reversible": True}
    assert "ONCE APPROVED\n 1 ↕ d-fourth\n 2 ~ a-first" in "\n".join(c["artifacts"][1]["lines"])


def test_one_new_unit_is_a_choice_between_keeping_it_and_leaving_it_out():
    q = card(3, "One more unit, queued.", 'unit add g-one "One unit for later." --repo switchboard-kit')["card"]
    assert q["title"] == "Approve the change to the switchboard-kit queue: 1 new?"
    qs = q["questions"]
    assert [f"{x['id']}:{x['kind']}" for x in qs] == ["plan:approve", "units-1:choice"]
    assert qs[1]["title"] == "Does g-one go in?"
    assert [f"{o['id']}={o['label']}" for o in qs[1]["options"]] == ["g-one=Add it", "leave-out=Leave it out"]
    assert qs[1]["options"][1]["consequence"] == "Cleared: not added; the rest still applies"
    assert qs[1]["recommendedIds"] == ["g-one"]
    assert qs[0]["rationale"] == "To change it, don't approve: say how in a note from ⋯. A note beside an approval changes nothing applied."


def adds(prefix, k):
    return [f'unit add {prefix}-{i} "Unit {i}." --repo switchboard-kit' for i in range(1, k + 1)]


def test_seven_new_units_are_two_questions_every_unit_recommended_and_a_taller_picture():
    m = card(4, "Seven units for the queue.", *adds("s", 7))
    qs = m["card"]["questions"]
    assert [f"{x['id']}:{x['kind']}:{len(x.get('options', []))}" for x in qs] == ["plan:approve:0", "units-1:multi:4", "units-2:multi:3"]
    assert qs[2]["title"] == "Which new units go in? Clear one to leave it out. (2 of 2)"
    assert (qs[1]["recommendedIds"], qs[2]["recommendedIds"]) == (["s-1", "s-2", "s-3", "s-4"], ["s-5", "s-6", "s-7"])
    assert not [x for x in qs if x["kind"] == "text"]
    one = card(3, "One more unit, queued.", 'unit add g-one "One unit for later." --repo switchboard-kit')
    assert png(picture.draw(m["sections"]))[1] > png(picture.draw(one["sections"]))[1]


def test_sixteen_new_units_are_a_plain_approval_that_links_its_session():
    m = card(5, "Sixteen units for the queue.", *adds("x", 16))
    assert (m["card"]["kind"], m["card"].get("questions"), m["session"]) == ("approve", None, True)
    assert len(m["card"]["summary"]) <= 300


def test_a_move_between_bolts_draws_each_counting_it_new_and_moved():
    c = card(6, "The moving page belongs with the deploys.", "unit move m-move deploys")["card"]
    assert c["title"] == "Approve proposal 6 to pages and deploys: 1 new, 1 moved?"
    assert c["questions"][1]["options"][0]["label"] == "Move it in"
    assert c["questions"][1]["options"][1]["consequence"] == "Cleared: stays in bolt pages; the rest still applies"
    text = "\n".join(c["artifacts"][1]["lines"])
    assert "MOVE   m-move\n       from pages to deploys" in text and "pages\n1 unit → 0" in text


def test_a_proposal_that_drops_and_adds_names_only_the_drops_in_its_rationale():
    c = card(7, "Two units are not needed, and one more is.", 'unit drop c-third "Not needed now."',
             'unit drop d-fourth "Not needed either."', 'unit add h-one "One more thing is built." --bolt deploys')["card"]
    assert c["questions"][0]["rationale"] == ("To keep the dropped units, don't approve: say why in a note from ⋯, and the planner "
                                              "writes the proposal again. A note beside an approval changes nothing applied.")


def test_a_closed_proposal_has_no_card():
    with pytest.raises(plan.Refusal, match="proposal 2 is dropped: it is closed, so it has no card"):
        card(2, "x", "unit order d-fourth --first", state="dropped")

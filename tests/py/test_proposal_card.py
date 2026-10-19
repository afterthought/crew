"""A proposal's Pending You card (plan-proposals spec, briefs.9, record 0031): cards.proposal_card, as crew raises it,
on the plan at the tip and the plan its commands leave, with its picture. The logic tier starts no process, so drawing
it here proves crew needs nothing installed to draw it. Raising the card is the proposals journey's (t-journey-plan)."""
import struct
import zlib

import pytest

from facts import FactsWrite, apply, plan_text

import cards
import plan

KIT = "switchboard-kit"
LONG = "a-long-unit-name-that-runs-past-the-width-of-a-phone-line"


def fresh():
    return FactsWrite(plan_text(bolts=[("deploys", KIT, None), ("pages", KIT, None)],
                                units=[(u, KIT, "deploys", []) for u in ("a-first", "b-second", "c-third", "d-fourth")]
                                + [("m-move", KIT, "pages", [])]))


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


# cards.proposal_card on the facts crew raises a proposal's card from: the plan at the tip, the plan the commands
# leave, and the proposal's case and commands, parsed. One checkbox list, every row of the change a box set as proposed.
def adds(prefix, k):
    return [f'unit add {prefix}-{i} "Unit {i}." --repo switchboard-kit' for i in range(1, k + 1)]


def built(n, case, *dos, waiting=(), session=None, state="open"):
    argvs = [plan.do_args("wldn", d) for d in dos]
    return cards.proposal_card(dict(n=n, state=state, case=case, before=fresh().plan, after=apply(fresh(), *dos).plan,
                                    argvs=argvs, waiting=list(waiting), session=session))


DOS = ('unit drop c-third "Not needed now."', 'unit amend b-second "The second thing, done better."',
       'unit add e-fifth "The fifth thing is built." --bolt deploys',
       f'unit add {LONG} "A unit whose name is longer than a phone\'s line." --bolt deploys --before a-first')


class TestBuiltDropAmendAdd:
    B = None

    @classmethod
    def setup_class(cls):
        cls.B = built(1, "The third unit is not needed. The second needs more. Two units finish the bolt.", *DOS, waiting=["swb-2"])

    def test_its_title_is_the_kind_and_the_thing_with_its_counts_and_no_number_or_question(self):
        c = self.B["card"]
        assert self.B["key"] == "proposal/1"
        assert c["title"] == "Plan change to deploys: 1 dropped, 1 amended, 2 new"
        assert c["summary"] == ("The third unit is not needed. Each row below is set as proposed; flip any and send. "
                                "It waits on swb-2-conductor to agree.")
        assert c["context"]["background"] == ("The third unit is not needed. The second needs more. Two units finish the bolt."
                                              "\n\nWaiting on swb-2-conductor to agree.")

    def test_it_is_one_checkbox_list_every_row_a_box_set_as_proposed_and_nothing_else_to_tap(self):
        c = self.B["card"]
        assert (c["kind"], c["intent"]) == ("multi", "decide") and "approve" not in c and "questions" not in c
        assert [(o["id"], o["label"]) for o in c["options"]] == [
            ("keep:c-third", "Keep c-third"), ("old:b-second", "Keep b-second's old intent"), ("add:e-fifth", "Add e-fifth"),
            (f"add:{LONG}", f"Add {LONG}")]
        assert c["recommendedIds"] == ["add:e-fifth", f"add:{LONG}"] and c["multi"] == {"min": 0, "max": 4}
        assert c["options"][0]["detail"] == "Proposed: drop. Why: Not needed now."
        assert c["options"][1]["detail"] == "Unit b-second."
        assert [b["ticked"] for b in self.B["boxes"]] == [False, False, True, True]
        assert [(b["unit"], b["is"]) for b in self.B["boxes"]][:2] == [("c-third", "dropped"), ("b-second", "amended")]

    def test_its_face_holds_a_paragraph_for_each_new_unit_and_the_dropped_one_with_its_direction(self):
        md = self.B["card"]["artifacts"][0]
        assert (md["kind"], md["lang"], md["title"]) == ("code", "markdown", "The new and dropped units")
        text = "\n".join(md["lines"])
        assert "**Drop c-third**\n\nUnit c-third.\n\nWhy: Not needed now." in text
        assert "**Add e-fifth**\n\nThe fifth thing is built.\n\nDirection: into deploys." in text
        assert f"**Add {LONG}**\n\nA unit whose name is longer than a phone's line.\n\nDirection: into deploys, before a-first." in text
        assert "b-second" not in text

    def test_its_picture_is_crews_own_png_1560_wide_uploaded_by_its_name_and_its_change_as_text(self):
        img, text = self.B["card"]["artifacts"][1:]
        assert (img["kind"], img["ref"], img["upload"]) == ("image", "proposal-1.png", True)
        w, h, form, dropped, new = png(self.B["picture"])
        assert (w, form, dropped, new) == (1560, (8, 2), True, True)
        assert (text["lang"], text["title"]) == ("text", "The change, in text") and max(len(l) for l in text["lines"]) <= 40

    def test_it_asks_nothing_in_words(self):
        c = self.B["card"]
        assert "text" not in c and not [q for q in c.get("questions") or [] if q["kind"] == "text"]


def test_the_text_of_a_proposal_that_drops_and_adds():
    text = "\n".join(built(2, "One goes, one comes.", 'unit drop a-first "Superseded."',
                           'unit add c-new "The new thing." --bolt deploys')["card"]["artifacts"][-1]["lines"])
    assert "DROP   a-first\n       Superseded." in text and "ADD    c-new\n       The new thing." in text
    assert "ONCE APPROVED\n" in text and " + c-new" in text.split("ONCE APPROVED")[1]


def test_a_proposal_with_no_unit_rows_is_a_hold_to_approve_of_low_risk():
    c = built(3, "The last goes first.", "unit order d-fourth --first")["card"]
    assert c["title"] == "Plan change to deploys: 1 moved"
    assert (c["kind"], c["approve"], c["recommendedIds"]) == ("approve", {"action": "Apply the plan change to deploys", "risk": "low",
                                                                         "reversible": True}, ["approve"])
    assert [a["kind"] for a in c["artifacts"]] == ["image", "code"]


def test_a_lone_row_is_the_choice_of_its_two_sides_since_a_list_holds_two_at_least():
    b = built(4, "One more unit, queued.", 'unit add g-one "One unit for later." --repo switchboard-kit')
    c = b["card"]
    assert c["title"] == "Plan change to the switchboard-kit queue: 1 new"
    assert (c["kind"], [o["id"] for o in c["options"]], c["recommendedIds"]) == ("choice", ["add:g-one", "unticked"], ["add:g-one"])
    assert c["options"][1]["label"] == "Leave g-one out"
    dropped = built(5, "x.", 'unit drop c-third "Not needed now."')["card"]
    assert ([o["label"] for o in dropped["options"]], dropped["recommendedIds"]) == (["Keep c-third", "Drop c-third"], ["unticked"])


def test_seven_new_units_are_two_lists_of_four_and_three_on_one_card():
    c = built(6, "Seven units for the queue.", *adds("s", 7))["card"]
    assert "kind" not in c and c["about"] == {"kind": "other", "title": "Plan change to the switchboard-kit queue"}
    assert [(q["id"], q["kind"], len(q["options"])) for q in c["questions"]] == [("rows-1", "multi", 4), ("rows-2", "multi", 3)]
    assert c["questions"][1]["title"] == "The change, part 2 of 2: each row as proposed"
    assert c["questions"][1]["recommendedIds"] == ["add:s-5", "add:s-6", "add:s-7"]


def test_sixteen_new_units_are_a_hold_to_approve_that_links_its_reading_session_first():
    b = built(7, "Sixteen units for the queue.", *adds("x", 16), session="http://mac-studio:19500")
    c = b["card"]
    assert (c["kind"], b["session"]) == ("approve", True)
    assert c["summary"].startswith("Read it all in one session: http://mac-studio:19500\n\nSixteen units for the queue.")
    assert c["context"]["links"] == [{"label": "Read proposal 7", "url": "http://mac-studio:19500"}]


@pytest.mark.parametrize("dos, form", [
    (("unit order a-first --first",), "approve"), (adds("p", 1), "choice"), (adds("p", 5), "multi"), (adds("p", 6), "lists"),
    (adds("p", 16), "approve"), (('unit drop c-third "Not needed."', 'unit amend b-second "Better."'), "multi")])
def test_a_proposals_card_form_is_read_from_its_commands_alone_as_its_card_is_built(dos, form):
    """cards.proposal_form, which a rewrite compares with the replaced proposal's, agrees with the card proposal_card
    builds: a hold-to-approve, a choice, one list or lists of questions."""
    assert cards.proposal_form([plan.do_args("wldn", d) for d in dos]) == form
    c = built(3, "Case.", *dos)["card"]
    assert {"approve": c.get("kind") == "approve", "choice": c.get("kind") == "choice", "multi": c.get("kind") == "multi",
            "lists": "questions" in c and "kind" not in c}[form]


def test_a_move_into_a_bolt_is_a_box_to_move_it_in():
    c = built(8, "The moving page belongs with the deploys.", "unit move m-move deploys")["card"]
    assert c["title"] == "Plan change to pages and deploys: 1 new, 1 moved"
    assert c["options"][0]["label"] == "Move m-move in"
    assert c["options"][0]["consequence"] == "Cleared: stays in bolt pages; the rest still applies"


def test_a_closed_proposal_has_no_card_drawn_again():
    with pytest.raises(plan.Refusal, match="proposal 9 is dropped: it is closed, so it has no card"):
        built(9, "x", "unit order d-fourth --first", state="dropped")

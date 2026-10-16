"""A finding recorded through crew signal, its moves and its show (signals.1 to signals.5), and a program's capture
landed through crew signal land (signals.6): the capture a signal goes in, named and quoted by its excerpt's verdict;
the number it takes in its capture; its file; what crew says; where its agent was working; a curation move's record and
refusals; a route's; crew signal show's text; and what a program's capture must hold to land and what its landing
writes. That a capture and its signal are one commit on the flywheel's branch, the raw record banked on the host, a
route and its unit one commit, any host answers show from the branches alone, and a program's capture lands in one
commit and once, is the signal journey's (t-journey-signals)."""
import datetime
import re

import pytest

from facts import FLEET, plan_text

import crew
import plan
import transcript
from crew import Refusal

NOW = datetime.datetime(2026, 10, 12, 14, 30, 5, tzinfo=datetime.timezone.utc)
CAP = "2026-10-12-swb-2-conductor-9f2c1a7e"


def verdict(grade, asserted_by="user", uuid="9f2c1a7e-5b6d-4c3e-8f00-112233445566", at="2026-10-12T14:29:01.123Z", n=1, raw=b'{"x": 1}', reason=None):
    value = {"uuid": uuid, "timestamp": at} if uuid or at else {}
    return transcript.Verdict(grade, reason, raw, n, value, asserted_by)


def named(v, excerpt="a security check", name="swb-2-conductor", kind=None):
    return plan.capture_named(name, v, "s-1", excerpt, NOW, kind)


class TestCaptureNamed:
    def test_a_received_record_names_its_capture_by_its_uuid_dated_and_quoted_at_its_time(self):
        assert named(verdict("verified")) == ("session/s-1/9f2c1a7e-5b6d-4c3e-8f00-112233445566", CAP, "2026-10-12", "user", "14:29:01Z", "constraint")

    def test_a_line_crew_cannot_classify_names_it_by_the_lines_hash_and_quotes_its_number(self):
        v = verdict("found", asserted_by="unknown", uuid=None, at=None, n=3)
        h = v.line_hash()[:16]
        assert named(v, kind="ask") == (f"session/s-1/line-{h}", f"2026-10-12-swb-2-conductor-{h[:8]}", "2026-10-12", "swb-2-conductor", "line 3", "ask")

    def test_an_unchecked_excerpt_names_it_by_the_excerpts_own_hash_dated_today(self):
        h = plan.sha16("drift detected on stack edge")
        got = named(transcript.unverified("no transcript for session s-gone"), "drift detected on stack edge")
        assert got == (f"unverified/swb-2-conductor/{h}", f"2026-10-12-swb-2-conductor-{h[:8]}", "2026-10-12", "swb-2-conductor", "unverified", "constraint")

    def test_who_asserted_it_is_the_user_crew_the_agent_a_tell_named_or_the_agent_itself_for_a_tool(self):
        assert [named(verdict("verified", asserted_by=a))[3] for a in ("user", "crew", "agent:swb-1-conductor", "tool")] == \
            ["user", "crew", "swb-1-conductor", "swb-2-conductor"]

    def test_the_users_note_at_a_shell_is_its_own_excerpt_kind_ask(self):
        h = plan.sha16("Templates should be checked for public buckets")
        got = plan.capture_named(None, None, None, "Templates should be checked for public buckets", NOW, None, "chuck", "mac-studio", "chuck@mac-studio")
        assert got == (f"operator/chuck@mac-studio/{h}", f"2026-10-12-chuck-mac-studio-{h[:8]}", "2026-10-12", "user", "14:30:05Z", "ask")


class TestNumber:
    HAVE = "---\ncapture: x\nkey: session/s-1/u-1\n---\n"
    QUOTE = plan.quoted("beside cfn-lint's validity check", "14:29:01Z")

    def number(self, have, names=(), texts=None, slug="beside-cfn-lint", key="session/s-1/u-1"):
        return plan.signal_number(have, key, CAP, "wldn", list(names), slug, self.QUOTE, lambda n: (texts or {}).get(n))

    def test_a_new_capture_takes_its_first_signal(self):
        assert self.number(None) == (1, 1)

    def test_a_second_signal_from_the_same_record_joins_its_capture(self):
        assert self.number(self.HAVE, ["capture.md", "01-cfn-nag-templates.md"]) == (2, 2)

    def test_the_same_signal_again_is_recorded_already(self):
        with pytest.raises(plan.Already, match=f"^{CAP}/02-beside-cfn-lint$"):
            self.number(self.HAVE, ["01-cfn-nag-templates.md", "02-beside-cfn-lint.md"], {"02-beside-cfn-lint.md": f"---\n---\n\nIt.\n\n{self.QUOTE}\n"})

    def test_the_same_slug_with_other_words_is_another_signal(self):
        assert self.number(self.HAVE, ["01-beside-cfn-lint.md"], {"01-beside-cfn-lint.md": "other words"}) == (2, 2)

    def test_a_capture_of_another_record_under_the_name_is_refused(self):
        with pytest.raises(Refusal, match=f"signals/{CAP} on wldn/main is another capture \\(session/s-1/u-1\\), not session/s-1/u-2"):
            self.number(self.HAVE, key="session/s-1/u-2")


class TestFiles:
    def test_a_signal_file_holds_its_frontmatter_what_it_asserts_and_its_quote(self):
        q = plan.quoted("a security check on the CloudFormation templates", "14:29:01Z")
        assert plan.signal_md(f"{CAP}/01-cfn-nag-templates", "ask", "user", "cloudformation, security,", "The user wants a check.\n", q) == (
            f"---\nsignal: {CAP}/01-cfn-nag-templates\nkind: ask\nwho: user\nsubject: [cloudformation, security]\n---\n\n"
            "The user wants a check.\n\n> \"a security check on the CloudFormation templates\" — 14:29:01Z\n")

    def test_a_quote_over_lines_keeps_each_line_quoted(self):
        assert plan.quoted("one\n\ntwo", "line 2") == '> "one\n>\n> two" — line 2'

    def test_crew_says_the_signal_and_its_grade_who_asserted_a_verified_one_and_why_one_is_unverified(self):
        assert plan.signal_said("x/01-a", verdict("verified", asserted_by="tool")) == "signal x/01-a: excerpt verified, asserted by tool"
        assert plan.signal_said("x/01-a", transcript.unverified("herdr names no session")) == "signal x/01-a: excerpt unverified (herdr names no session)"
        assert plan.signal_said("x/01-a", verdict("found")) == "signal x/01-a: excerpt found"
        assert plan.signal_said("x/01-a", None) == "signal x/01-a: excerpt own"

    @pytest.mark.parametrize("slug, asserts, said", [("Bad_Slug", "x", "a signal's slug is lowercase words with dashes, not Bad_Slug"),
                                                     ("show", "x", "a signal's slug can't be 'show'"),
                                                     ("land", "x", "a signal's slug can't be 'land'"),
                                                     ("says-nothing", " ", "a signal says what it asserts, in a sentence"),
                                                     ("fine", "It holds.", None)])
    def test_a_slug_that_is_no_name_or_a_subcommand_and_an_empty_assertion_are_refused(self, slug, asserts, said):
        assert plan.signal_refusal(slug, asserts) == said


class TestCaptureText:
    PLAN = plan.Plan(plan_text(bolts=[("smoke-2", "switchboard-kit", "swb-2")]))

    def text(self, v, name="swb-2-conductor", raw="chuck-herdr-alpha:~/.local/state/crew/wldn/raw/x.jsonl"):
        key, cap, date, *_ = named(v, name=name)
        return plan.capture_text(FLEET, name, "chuck-herdr-alpha", v, "s-1", key, cap, date, NOW, raw, self.PLAN)

    def test_a_verified_capture_says_where_its_excerpt_came_from_and_how_well_it_was_checked(self):
        c = self.text(verdict("verified"))
        for want in (f"capture: {CAP}", "source: crew-session", "key: session/s-1/9f2c1a7e-5b6d-4c3e-8f00-112233445566", "captured_by: swb-2-conductor",
                     "host: chuck-herdr-alpha", "session: s-1", "record: 9f2c1a7e-5b6d-4c3e-8f00-112233445566", "at: 2026-10-12T14:29:01Z",
                     "excerpt: verified", "asserted_by: user", "where: team swb-2, bolt smoke-2", "raw: chuck-herdr-alpha:~/.local/state/crew/wldn/raw/x.jsonl",
                     "event_date: 2026-10-12", "status: read", "signals: 1", "# swb-2-conductor, 2026-10-12 14:29Z"):
            assert want in c

    def test_an_unverified_capture_says_why_and_holds_no_record_time_or_raw(self):
        c = self.text(transcript.unverified("no transcript for session s-gone"), raw=None)
        assert "excerpt: unverified" in c and "unverified: no transcript for session s-gone" in c and "asserted_by: unknown" in c
        assert not any(f"\n{k}:" in c for k in ("record", "at", "raw"))

    def test_the_users_note_has_no_session_record_raw_or_where(self):
        c = plan.capture_text(FLEET, None, "mac-studio", None, None, "operator/chuck@mac-studio/abc", "2026-10-12-chuck-mac-studio-abc", "2026-10-12", NOW, None, self.PLAN, "chuck@mac-studio")
        assert "source: operator" in c and "captured_by: chuck@mac-studio" in c and "# chuck@mac-studio, 2026-10-12" in c and "excerpt: own" in c and "asserted_by: user" in c
        assert not any(f"\n{k}:" in c for k in ("session", "record", "raw", "where"))


class TestWhere:
    PLAN = plan.Plan(plan_text(bolts=[("smoke-2", "switchboard-kit", "swb-2")]))

    def test_a_conductor_is_at_its_team_and_the_bolt_it_holds_a_planner_at_the_main_level(self):
        assert plan.where_of(FLEET, "swb-2-conductor", self.PLAN) == "team swb-2, bolt smoke-2"
        assert plan.where_of(FLEET, "swb-1-ops", self.PLAN) == "team swb-1"
        assert plan.where_of(FLEET, "wldn-planner", self.PLAN) == "main level"
        assert plan.where_of(FLEET, "wldn-operator-chuck", self.PLAN) == "operator session"
        assert plan.where_of(FLEET, "stranger", self.PLAN) is None

    def test_a_slot_agent_is_also_at_the_unit_or_fix_its_slot_holds(self, monkeypatch):
        held = {"unit-1": {"kind": "unit", "name": "cfn-lint-treefmt"}, "unit-2": {"kind": "fix", "name": "fix/smoke-2/edge"}}
        monkeypatch.setattr(crew, "slot_of", lambda t, slot: held[slot])
        assert plan.where_of(FLEET, "swb-2-unit-1", self.PLAN) == "team swb-2, bolt smoke-2, unit cfn-lint-treefmt"
        assert plan.where_of(FLEET, "swb-2-unit-2", self.PLAN) == "team swb-2, bolt smoke-2, fix edge"

    def test_a_slot_agents_own_stage_prompts_are_its_conductors_and_no_one_elses_are(self):
        assert plan.stage_by(FLEET, "swb-2-unit-1") == "swb-2-conductor"
        assert [plan.stage_by(FLEET, n) for n in ("swb-2-ops", "swb-2-conductor", "wldn-planner")] == [None, None, None]

    def test_a_session_on_another_host_is_not_read_here(self):
        assert plan.session_here("chuck-herdr-alpha:s-1", "chuck-herdr-alpha") == ("s-1", None)
        assert plan.session_here("mac-studio:s-1", "chuck-herdr-alpha") == ("s-1", "session s-1 is on mac-studio, not chuck-herdr-alpha")
        assert plan.session_here(None, "chuck-herdr-alpha") == (None, None)


class TestMoves:
    def test_a_curation_move_records_its_target_or_reason_and_names_a_pointer_target_in_its_entry(self):
        rec, on = plan.curation_move("x/01-a", "answered", "books/atlas-kit/src/tiles.md", None, "2026-10-12", "wldn-design")
        assert rec.lines() == ["Signal: x/01-a", "Move: answered", "Target: books/atlas-kit/src/tiles.md", "Date: 2026-10-12", "By: wldn-design"]
        assert on == ["signals/x/01-a", "books/atlas-kit/src/tiles.md"]
        assert plan.curation_move("x/01-a", "attach", "the intent it lands on", None, "2026-10-12", "d")[1] == ["signals/x/01-a"]
        rec, _ = plan.curation_move("x/01-a", "drop", None, "a duplicate", "2026-10-12", "d")
        assert "Reason: a duplicate" in rec.lines()

    @pytest.mark.parametrize("kind, said", [("attach", "a attach move names its target (--target): the intent, claim or record it lands on"),
                                            ("challenge", "a challenge move names its target (--target): the intent, claim or record it argues with"),
                                            ("answered", "a answered move names its target"), ("drop", "a drop gives its reason (--reason)")])
    def test_a_move_without_its_target_or_reason_is_refused(self, kind, said):
        with pytest.raises(Refusal, match="^" + re.escape(said)):
            plan.curation_move("x/01-a", kind, None, None, "2026-10-12", "d")

    def test_a_signal_with_its_move_is_refused_another(self):
        moves = "%rec: Move\n\nSignal: x/01-a\nMove: answered\n"
        with pytest.raises(Refusal, match="^signal x/01-a already has its move: answered$"):
            plan.unmoved(moves, "x/01-a")
        plan.unmoved(moves, "x/02-b")

    def test_a_route_names_its_unit(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "wldn-planner")
        assert plan.route_move("x/01-a", "the-waf-blocks").lines()[:3] == ["Signal: x/01-a", "Move: route", "Target: unit/the-waf-blocks"]


class TestShow:
    MOVE = plan.Rec("Move", [("Signal", "s/01-a"), ("Move", "drop"), ("Reason", "fixed by the tile cache"), ("Date", "2026-10-12"), ("By", "wldn-design")])

    def test_a_signal_on_the_branch_with_its_captures_fields_and_no_move_yet(self):
        cap = "---\ncaptured_by: swb-2-conductor\nexcerpt: verified\n---\n\n# x\n"
        out = plan.shown_signal("s/01-a", "wldn/main", "WilldanGroup/crew-state", "---\nkind: ask\n---\n\nIt.\n", cap, [("wldn", None)])
        assert out == ("signals/s/01-a, on wldn/main of WilldanGroup/crew-state\n\n---\nkind: ask\n---\n\nIt.\n\nIts capture, signals/s/capture.md:\n"
                       "  captured_by: swb-2-conductor\n  excerpt: verified\n\nNo move yet in wldn.")

    def test_a_meetings_signal_reads_as_it_stands_with_its_move_and_one_with_no_capture_says_so(self):
        out = plan.shown_signal("s/01-a", "main", "WilldanGroup/willdan-blueprints", "Tiles load slowly.", None, [("wldn", self.MOVE)])
        assert "No capture.md beside it in WilldanGroup/willdan-blueprints." in out
        assert out.endswith("Its move in wldn: drop, by wldn-design on 2026-10-12: fixed by the tile cache")
        route = plan.Rec("Move", [("Signal", "s/01-a"), ("Move", "route"), ("Target", "unit/u"), ("Date", "2026-10-12"), ("By", "chuck@laptop")])
        assert plan.shown_signal("s/01-a", "main", "r", "t", None, [("wldn", route)]).endswith("Its move in wldn: route unit/u, by chuck@laptop on 2026-10-12")


class TestRefused:
    FLEET = {"partitions": {"wldn": {"label": "wldn", "blueprints": ["WilldanGroup/willdan-blueprints"], "state": "WilldanGroup/crew-state"}},
             "teams": {}, "hosts": {}}

    def test_a_signal_in_neither_home_is_refused_naming_both(self):
        with pytest.raises(Refusal, match="^no signal x/01-y on wldn/main of WilldanGroup/crew-state or on main of WilldanGroup/willdan-blueprints"):
            plan.no_signal(self.FLEET, "wldn", "x/01-y")

    def test_a_route_is_no_curation_move_it_is_written_only_with_its_unit(self, capsys):
        with pytest.raises(SystemExit):
            plan.parser().parse_args(["signal-move", "x/01-y", "route"])
        assert "invalid choice: 'route'" in capsys.readouterr().err


DEP = "2026-10-12-deploy-mac-studio-abc1234-103000"
CAPTURE = f"""---
capture: {DEP}
source: swancloud-deployer
key: deploy/mac-studio/abc1234def56/20261012T103000Z
event_date: 2026-10-12
captured_by: swancloud-deployer
host: mac-studio
at: 2026-10-12T10:31:00Z
raw: mac-studio:~/.local/state/swancloud/deployer/logs/20261012T103000Z-mac-studio-abc1234def56-machine.log
imported: 2026-10-12
status: read
signals: 1
---

# mac-studio's deploy of abc1234def56

mac-studio's deploy of abc1234def56 failed at the machine, captured by the fleet's deployer on mac-studio.
"""
FAILED = f"""---
signal: {DEP}/01-failed
kind: constraint
who: swancloud-deployer
subject: [deploy, mac-studio]
---

mac-studio's deploy of abc1234def56 (feat: x) failed at the machine.

> error: builder for '/nix/store/x.drv' failed
>
> last line

— mac-studio:~/.local/state/swancloud/deployer/logs/x.log, 2026-10-12T10:31:00Z
"""


def folder(**changed):
    """A deployer's failed deploy as its capture's folder holds it, with any file changed."""
    return dict({"capture.md": CAPTURE, "01-failed.md": FAILED}, **changed)


def refusal(files=None, cap=DEP, here="mac-studio", banked=True):
    return plan.capture_refusal(cap, folder() if files is None else files, here, banked)


class TestLand:
    def test_a_deployers_capture_with_its_one_signal_and_its_raw_record_banked_here_lands(self):
        assert refusal() is None

    @pytest.mark.parametrize("files, cap, said", [
        (None, "2026-10-02-release-mise-2026.10.0", "2026-10-02-release-mise-2026.10.0 is no capture's name crew takes: lowercase words, digits and dashes (code.4)"),
        ({"01-failed.md": FAILED}, DEP, f"{DEP} has no capture.md"),
        (folder(**{"machine.log": "x"}), DEP, f"{DEP}/machine.log is no signal's file, NN-<slug>.md: a capture's raw material stays on its host, outside git (signals.3)"),
        (folder(**{"capture.md": CAPTURE.replace("source: swancloud-deployer\n", "")}), DEP, f"{DEP}/capture.md names no source, the program that recorded it"),
        (folder(**{"capture.md": CAPTURE.replace("captured_by: swancloud-deployer\n", "")}), DEP, f"{DEP}/capture.md names no captured_by, who recorded it"),
        ({"capture.md": CAPTURE.replace("status: read\nsignals: 1", "status: unread\nsignals: 0")}, DEP,
         f"{DEP} lands read, with its signals: a program's capture is its own excerpt, and its one signal is made with it (signals.6)"),
        (folder(**{"capture.md": CAPTURE.replace("signals: 1", "signals: 2")}), DEP, f"{DEP}/capture.md counts 2 signals, and {DEP} holds 1"),
        (folder(**{"01-failed.md": FAILED.replace("kind: constraint", "kind: complaint")}), DEP,
         f"{DEP}/01-failed.md: kind is one of constraint, ask, question, commitment, reaction, not complaint"),
        (folder(**{"01-failed.md": FAILED.replace(f"signal: {DEP}/01-failed", f"signal: {DEP}/01-other")}), DEP,
         f"{DEP}/01-failed.md names the signal {DEP}/01-other, not {DEP}/01-failed"),
        (folder(**{"01-failed.md": FAILED.replace("> ", "").replace(">\n", "")}), DEP, f"{DEP}/01-failed.md quotes no excerpt"),
        (folder(**{"01-failed.md": FAILED + "> " + "x" * 8192 + "\n"}), DEP,
         f"{DEP}/01-failed.md is larger than 8 KiB, so it copies its source: cut its excerpt and keep the whole in the raw record")])
    def test_a_capture_that_is_not_a_programs_whole_capture_is_refused_naming_the_file(self, files, cap, said):
        assert refusal(files, cap) == said

    def test_its_raw_record_is_banked_on_the_host_that_lands_it(self):
        assert refusal(here="chuck-herdr-alpha") == (f"{DEP}/capture.md's raw record is on mac-studio, and a program's capture lands from the host "
                                                     "that banked it, not chuck-herdr-alpha")
        assert refusal(banked=False) == (f"{DEP}/capture.md's raw record, ~/.local/state/swancloud/deployer/logs/"
                                         "20261012T103000Z-mac-studio-abc1234def56-machine.log, is not on mac-studio")
        assert refusal(folder(**{"capture.md": CAPTURE.replace("raw: ", "rawest: ")})).startswith(f"{DEP}/capture.md names no raw record")

    def test_its_landing_writes_what_the_branch_lacks_and_passes_over_what_it_holds_the_same(self):
        assert plan.capture_landing(DEP, folder(), {}, "swancloud") == {f"signals/{DEP}/01-failed.md": FAILED, f"signals/{DEP}/capture.md": CAPTURE}
        assert plan.capture_landing(DEP, folder(), {"capture.md": CAPTURE}, "swancloud") == {f"signals/{DEP}/01-failed.md": FAILED}

    def test_the_same_capture_again_is_already_landed_and_a_changed_one_is_refused(self):
        with pytest.raises(plan.Already):
            plan.capture_landing(DEP, folder(), {"capture.md": CAPTURE, "01-failed.md": FAILED}, "swancloud")
        with pytest.raises(Refusal, match=f"signals/{DEP}/01-failed.md on swancloud/main is not the one landed now, and a capture or signal is never changed"):
            plan.capture_landing(DEP, folder(), {"capture.md": CAPTURE, "01-failed.md": FAILED.replace("machine", "suite")}, "swancloud")

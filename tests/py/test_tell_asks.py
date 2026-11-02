"""A tell or a send to a role that runs as its kind is an ask (role-runs "A tell, a notice or a send to a role that runs
as its kind is an ask", "A tell finds a standing agent of the role first" and "A role that stands is asked nothing";
main-level "Any agent crew starts is reached by name"; design Decision 5): crew.asks_instead decides from what crew read
of the agent, and crew.tell writes the ask through plan.ask_write in place of typing, from the sender or crew. That the
ask lands on the branch is test_asks.py's; that the command does, t-journey-roles'."""
import pytest

import crew
import record

FALSE = dict.fromkeys(crew.KIND_ROLES, False)
FLEET = {"partitions": {"madswan": {"label": "madswan", "machine": "deneb", "roles": {}, "flume": dict(FALSE, planner="madswan-main", operator="madswan-main")},
                        "wldn": {"label": "wldn", "machine": "chuck-herdr-alpha", "roles": {}, "flume": FALSE}},
         "teams": {"swc-3": {"name": "swc-3", "label": "madswan", "machine": "deneb", "session": "madswan-2"}}, "hosts": {}}


class TestAsksInstead:
    """Whether a tell is an ask: a role that runs as its kind, read with no standing agent up; never on a guess."""

    def test_a_role_that_runs_as_its_kind_with_no_standing_agent_up_is_asked(self):
        assert crew.asks_instead(("madswan", "planner"), None, None) is True

    def test_a_standing_agent_still_up_is_told(self):
        """role-runs, The standing agent not yet stopped."""
        assert crew.asks_instead(("madswan", "planner"), "idle", None) is False

    def test_a_standing_agent_crew_could_not_read_is_neither_told_nor_asked(self):
        assert crew.asks_instead(("madswan", "planner"), None, "deneb did not answer") is False

    def test_a_role_that_stands_is_never_asked(self):
        """role-runs, A role still standing."""
        assert crew.asks_instead(None, None, None) is False


@pytest.fixture
def herdr(monkeypatch):
    """What crew reads of each agent, {name: (status, asking, unread)}, a name it lists none of read as not up; every
    prompt typed and every ask written, kept."""
    read, typed, asked, emitted = {}, [], [], []
    monkeypatch.setattr(crew, "place_of_agent", lambda fleet, name: ("deneb", "madswan-1"))
    monkeypatch.setattr(crew, "waits_on_question", lambda fleet, name: read.get(name, (None, False, None)))
    monkeypatch.setattr(crew, "on_machine", lambda fleet, host, argv: typed.append(argv) or type("R", (), {"returncode": 0, "stderr": ""})())
    monkeypatch.setattr(record, "emit", lambda label, act, on=(), **f: emitted.append((label, act, list(on))))
    import plan
    monkeypatch.setattr(plan, "ask_write", lambda fleet, label, role, what, frm, names=None, key=None, words=None:
                        asked.append((label, role, what, frm, words)) or "c" * 40)
    return read, typed, asked, emitted


class TestTell:
    def test_a_tell_to_the_planner_is_an_ask_from_its_sender_and_types_nothing(self, herdr, capsys):
        """role-runs and main-level, A tell to the planner: an ask from madswan-design, nothing typed, the command says it
        asked madswan-planner; the ask's own entry is the record, with no tell entry beside it."""
        _, typed, asked, emitted = herdr
        assert crew.tell(FLEET, "madswan-planner", "record 0053 is accepted", sender="madswan-design") is True
        assert asked == [("madswan", "planner", "tell", "madswan-design", "record 0053 is accepted")]
        assert typed == [] and emitted == []
        assert capsys.readouterr().out == "asked madswan-planner\n"

    def test_crews_own_notice_is_an_ask_from_crew(self, herdr):
        """role-runs, crew's own notice: a notice carries no sender, and its ask is crew's."""
        _, typed, asked, _ = herdr
        assert crew.tell(FLEET, "madswan-planner", "Proposal 12 was approved.") is True
        assert asked == [("madswan", "planner", "tell", "crew", "Proposal 12 was approved.")] and typed == []

    def test_a_notice_sent_to_be_taken_is_an_ask_all_the_same(self, herdr):
        _, typed, asked, _ = herdr
        assert crew.tell(FLEET, "madswan-planner", "notice", taken=True, what="the notice of its restart") is True
        assert [a[2:4] for a in asked] == [("tell", "crew")] and typed == []

    def test_a_standing_agent_still_up_is_typed_into_and_asked_nothing(self, herdr):
        """role-runs, The standing agent not yet stopped."""
        read, typed, asked, emitted = herdr
        read["madswan-planner"] = ("idle", False, None)
        assert crew.tell(FLEET, "madswan-planner", "hello", sender="madswan-design") is True
        assert asked == [] and typed[0][-2:] == ["madswan-planner", "[crew tell from madswan-design] hello"]
        assert [e[1] for e in emitted] == ["tell"]

    def test_a_standing_agent_waiting_on_a_question_is_refused_as_today(self, herdr, capsys):
        read, typed, asked, _ = herdr
        read["madswan-planner"] = ("blocked", True, None)
        assert crew.tell(FLEET, "madswan-planner", "hello") is False
        assert asked == [] and typed == [] and "waiting on a question" in capsys.readouterr().err

    def test_herdr_unread_refuses_naming_it_and_asks_nothing(self, herdr, capsys):
        """role-runs, A tell finds a standing agent of the role first: crew can't read whether one is up (read.1)."""
        read, typed, asked, _ = herdr
        read["madswan-planner"] = (None, False, "deneb did not answer (ssh exited 255)")
        assert crew.tell(FLEET, "madswan-planner", "hello") is False
        assert asked == [] and typed == []
        assert capsys.readouterr().err == ("could not tell madswan-planner on deneb: deneb did not answer (ssh exited 255), so crew can't "
                                           "tell whether a standing agent of it is up or its role is to be asked; nothing was sent or asked\n")

    def test_a_role_that_stands_is_refused_when_not_up_and_never_asked(self, herdr, capsys):
        """role-runs, A role still standing: wldn's planner stands, so a tell to it is today's."""
        _, typed, asked, _ = herdr
        assert crew.tell(FLEET, "wldn-planner", "hello") is False
        assert asked == [] and typed == [] and "it is not up" in capsys.readouterr().err

    def test_an_ask_crew_could_not_write_fails_the_tell_saying_so(self, herdr, monkeypatch, capsys):
        import plan
        monkeypatch.setattr(plan, "ask_write", lambda *a, **k: crew.fail("could not fetch madswan/main"))
        assert crew.tell(FLEET, "madswan-planner", "hello") is False
        assert capsys.readouterr().err == "could not ask madswan-planner: could not fetch madswan/main; nothing was sent\n"


class TestSend:
    @pytest.fixture
    def sender(self, monkeypatch):
        monkeypatch.setenv("CREW_AGENT", "swancloud-planner")

    @pytest.mark.usefixtures("sender")
    def test_a_send_to_an_operator_that_runs_as_its_kind_is_a_send_ask_carrying_whom_it_was_for(self, herdr, capsys):
        """operator-agent, An operator that runs as its kind: the ask holds `(sent to madswan)` and the text; nothing
        is typed, and the ask's entry is the send's one record."""
        _, typed, asked, emitted = herdr
        assert crew.send(FLEET, "madswan", "the zone check fails") is True
        assert asked == [("madswan", "operator", "send", "swancloud-planner", "(sent to madswan) the zone check fails")]
        assert typed == [] and emitted == []
        assert capsys.readouterr().out == "asked madswan-operator\n"

    @pytest.mark.usefixtures("sender")
    def test_a_send_to_a_team_of_that_partition_names_the_team(self, herdr):
        _, _, asked, _ = herdr
        assert crew.send(FLEET, "swc-3", "hello") is True
        assert asked[0][2:] == ("send", "swancloud-planner", "(sent to swc-3) hello")

    @pytest.mark.usefixtures("sender")
    def test_a_standing_operator_still_up_is_typed_into_with_its_send_entry(self, herdr):
        read, typed, asked, emitted = herdr
        read["madswan-operator"] = ("idle", False, None)
        assert crew.send(FLEET, "madswan", "hello") is True
        assert asked == [] and typed[0][-1] == "[crew tell from swancloud-planner] (sent to madswan) hello"
        assert [(e[1], e[2]) for e in emitted] == [("send", ["agent/madswan-operator", None])]

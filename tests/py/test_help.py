"""A help flag shows a command's usage and acts on nothing (code.11): crew.usage_asked for which parser's usage a
command's arguments ask for, and each Python entry point answering it first, before it checks for recutils, reads the
teams file or does anything else. A bash command's own lines and every command's wiring are the end-to-end tier's
(t-help)."""
import pytest

import board
import crew
import hold
import ops
import page
import plan
import record
import sites


def asked(ap, argv):
    p = crew.usage_asked(ap, argv)
    return p.prog if p is not None else None


class TestAsked:
    @pytest.mark.parametrize("argv, prog", [
        (["bolt", "start", "tenant-environments", "--help"], "crew bolt start"),
        (["bolt", "--help"], "crew bolt"),
        (["bolts", "-h"], "crew bolts"),
        (["fix", "tenant-environments", "tidy", "--help"], "crew fix"),
        (["answer", "tenant-environments--tidy", "--help"], "crew answer"),
        (["signal-move", "x", "attach", "--help"], "crew signal move"),
        (["review-delivered", "--help"], "crew review delivered"),
        (["kit", "rename", "a", "b", "-h"], "crew kit rename"),
        (["_sweep", "wldn", "switchboard-kit", "--dir", "/k", "--help"], "crew _sweep"),
    ], ids=lambda v: " ".join(v) if isinstance(v, list) else v)
    def test_the_flag_asks_for_the_usage_of_the_deepest_command_its_words_name(self, argv, prog):
        assert asked(plan.parser(), argv) == prog

    def test_a_run_that_builds_only_its_command_asks_the_same(self):
        assert asked(plan.parser(only="bolt"), ["bolt", "start", "tenant-environments", "--help"]) == "crew bolt start"

    @pytest.mark.parametrize("argv, prog", [
        (["plan", "approve", "three", "--help"], "crew plan approve"),
        (["role", "open", "nobody", "-h"], "crew role open"),
        (["card", "answer", "batch/1", "--excerpt", "--help"], "crew card answer"),
    ], ids=lambda v: " ".join(v) if isinstance(v, list) else v)
    def test_a_word_the_parser_would_refuse_before_the_flag_does_not_answer_in_its_place(self, argv, prog):
        assert asked(plan.parser(), argv) == prog

    @pytest.mark.parametrize("argv", [
        ["fix", "tenant-environments", "tidy", "--help with which table holds tenants"],
        ["answer", "tenant-environments--tidy", "--helpful"],
        ["answer", "tenant-environments--tidy", "-hx"],
        ["bolt", "start", "help"],
        ["bolts"],
    ], ids=" ".join)
    def test_a_word_that_is_not_exactly_the_flag_is_a_word(self, argv):
        assert asked(plan.parser(), argv) is None

    def test_the_other_modules_parsers(self):
        assert asked(record.parser(), ["events", "--label", "wldn", "--help"]) == "crew events"
        assert asked(hold.parser(), ["_hold", "set", "--help"]) == "crew _hold set"
        assert asked(ops.parser(), ["offer", "dev", "-h"]) == "crew ops offer"


class TestAnswered:
    """Each Python entry point answers the flag first: with no recutils on PATH and a teams file that refuses to be read,
    it still prints its usage and exits 0."""

    @pytest.fixture(autouse=True)
    def nothing_readable(self, monkeypatch):
        monkeypatch.setenv("PATH", "")
        monkeypatch.setattr(crew, "load", lambda *a, **k: pytest.fail("the teams file was read for a usage"))

    @pytest.mark.parametrize("main, argv, prog", [
        (plan.main, ["fix", "tenant-environments", "tidy", "--help"], "crew fix"),
        (plan.main, ["bolt", "start", "tenant-environments", "--help"], "crew bolt start"),
        (plan.main, ["signal", "move", "x", "attach", "-h"], "crew signal move"),
        (plan.main, ["review", "delivered", "--help"], "crew review delivered"),
        (board.main, ["board", "--help"], "crew board"),
        (board.main, ["_follow", "--help"], "crew _follow"),
        (board.main, ["_views", "wldn", "-h"], "crew _views"),
        (hold.main, ["_go", "--help"], "crew _go"),
        (ops.main, ["offer", "dev", "--help"], "crew ops offer"),
        (record.main, ["trace", "unit/a", "--help"], "crew trace"),
        (page.main, ["page", "wldn", "--help"], "crew page"),
        (sites.main, ["--help"], "crew sites"),
    ], ids=lambda v: " ".join(v) if isinstance(v, list) else getattr(v, "__module__", v))
    def test_the_usage_is_printed_and_nothing_else_is_done(self, main, argv, prog, capsys):
        with pytest.raises(SystemExit) as e:
            main(argv)
        assert e.value.code == 0
        assert capsys.readouterr().out.startswith(f"usage: {prog} ")

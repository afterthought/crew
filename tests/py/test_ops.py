"""The operations on a partition's environments, a deploy being one kind (plan.14): ops.state on the run record's ops
entries, the rail rows ops.rows makes of them, the approval's refusal and the arguments crew ops refuses. That each act
is an entry of the run record on the partition's main level's host, that crew ops word and steps read them back, that
quiet reads the host's agents and test slots, and that a command run elsewhere runs there are the ops journey's
(t-journey-ops)."""
import pytest

from facts import FLEET

import ops

S1, S2 = "a" * 40, "b" * 40
N = iter(range(1, 1000))


def e(act, env="mac-studio", minutes=0, **f):
    return dict(Id=f"20261012T10{minutes:02d}00Z-mac-studio-1-{next(N)}", At=f"2026-10-12T10:{minutes:02d}:00Z", Act=act, On=[f"env/{env}"], From=[],
                Commit=[], **f)


OFFER = e("ops.offer", minutes=1, Head=S1, Base="none")


class TestState:
    def test_an_offer_is_open_until_approved_and_the_word_holds_until_that_deploy_ends(self):
        approve = e("ops.approve", minutes=2, Head=S1)
        offers, words, _ = ops.state([OFFER])
        assert offers == {"mac-studio": OFFER} and words == {}
        offers, words, _ = ops.state([OFFER, approve])
        assert offers == {} and words == {"mac-studio": approve}
        _, words, _ = ops.state([OFFER, approve, e("ops.deploy", minutes=3, Head=S1, Phase="start"), e("ops.deploy", minutes=4, Head=S1, Phase="step")])
        assert words == {"mac-studio": approve}
        assert ops.state([OFFER, approve, e("ops.deploy", minutes=5, Head=S1, Phase="end")])[1] == {}

    def test_a_newer_offer_replaces_the_open_one_and_waits_beside_an_approved_one(self):
        newer = e("ops.offer", minutes=3, Head=S2, Base="none")
        offers, words, _ = ops.state([OFFER, e("ops.approve", minutes=2, Head=S1), newer, e("ops.deploy", minutes=4, Head=S1, Phase="end")])
        assert offers == {"mac-studio": newer} and words == {}
        assert ops.state([OFFER, newer])[0] == {"mac-studio": newer}

    def test_a_refused_approval_is_no_word(self):
        assert ops.state([OFFER, e("ops.approve", minutes=2, Head=S2, Refused="the deploy of mac-studio offered is to aaaaaaa, not bbbbbbb")])[1] == {}

    def test_each_steps_latest_entry_is_its_state(self):
        steps = [e("ops.step", minutes=1, Head=S1, Key="restart-herdr/1", State="waiting", Doer="user"),
                 e("ops.step", minutes=2, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher"),
                 e("ops.step", minutes=3, Head=S1, Key="restart-herdr/1", State="done", Note="restarted at 10:02")]
        got = [(key, x["State"]) for (env, to, key), x in ops.ordered(ops.state(steps)[2])]
        assert got == [("restart-teams/1", "handed"), ("restart-herdr/1", "done")]


class TestRows:
    def test_an_open_offer_is_a_deploy_row_whose_card_is_main_level_opss(self):
        row, = ops.rows(None, "swancloud", [OFFER])
        assert row["key"] == "deploy/mac-studio/aaaaaaa" and row["group"] == "operations"
        assert row["what"] == ["deploy mac-studio (swancloud) to aaaaaaa, from nothing deployed: swancloud-ops posts its card, and holding it is the word to deploy"]
        assert row["cmds"] == [("answer", f"crew ops approve mac-studio --to {S1} --label swancloud")]

    def test_a_step_the_user_is_to_take_that_waits_is_a_row_until_marked_counted_among_its_environments_steps(self):
        steps = [e("ops.step", minutes=1, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher"),
                 e("ops.step", minutes=2, Head=S1, Key="restart-herdr/1", State="waiting", Doer="user", Text="Restart the herdr server\nonce the teams are quiet."),
                 e("ops.step", minutes=3, Key="rotate-tailnet-key", State="waiting", Doer="user", Note="due this week")]
        rows = ops.rows(None, "swancloud", steps)
        assert [r["key"] for r in rows] == ["op/mac-studio/2", "op/mac-studio/3"]
        assert rows[0]["what"] == [f"an operation after the deploy of mac-studio to aaaaaaa (swancloud), yours to do: Restart the herdr server\nonce the teams are quiet."]
        assert rows[0]["cmds"][0] == ("done", f"crew ops step mac-studio --to {S1} --key restart-herdr/1 --state done --label swancloud")
        assert rows[1]["what"] == ["an operation on mac-studio (swancloud), yours to do: rotate-tailnet-key"]
        assert rows[1]["cmds"] == [("done", "crew ops step mac-studio --key rotate-tailnet-key --state done --label swancloud"),
                                   ("decline", "crew ops step mac-studio --key rotate-tailnet-key --state declined --label swancloud")]
        assert ops.rows(None, "swancloud", steps + [e("ops.step", minutes=4, Key="rotate-tailnet-key", State="declined", Doer="user")])[1:] == []

    def test_a_waiting_steps_row_keeps_its_key_when_an_earlier_steps_state_changes(self):
        steps = [e("ops.step", minutes=1, Key="restart-herdr", State="waiting", Doer="user"),
                 e("ops.step", minutes=2, Key="rotate-tailnet-key", State="waiting", Doer="user")]
        assert [r["key"] for r in ops.rows(None, "swancloud", steps)] == ["op/mac-studio/1", "op/mac-studio/2"]
        done = steps + [e("ops.step", minutes=3, Key="restart-herdr", State="done", Doer="user")]
        assert [r["key"] for r in ops.rows(None, "swancloud", done)] == ["op/mac-studio/2"]


class TestRefusals:
    def test_an_approval_answers_only_the_offer_open_now(self):
        offers = {"mac-studio": OFFER}
        assert ops.approve_refusal(offers, "mac-studio", S1) is None
        assert ops.approve_refusal(offers, "mac-studio", S2) == "the deploy of mac-studio offered is to aaaaaaa, not bbbbbbb"
        assert ops.approve_refusal(offers, "macbook-pro", S1) == "no deploy of macbook-pro is offered"

    @pytest.mark.parametrize("argv, said", [
        (["offer", "mac-studio", "--label", "wldn", "--from", "none", "--to", "nothex"], "--to nothex is no commit: a sha in hex"),
        (["offer", "Bad_Env", "--label", "wldn", "--from", "none", "--to", S1], "Bad_Env is no environment's name: lowercase words and dashes"),
        (["word", "mac-studio", "--label", "nolabel"], "no partition nolabel in the teams file. partitions: wldn"),
        (["step", "mac-studio", "--label", "wldn", "--key", "has space", "--state", "done"], "--key has space is no step key crew takes"),
        (["offer", "mac-studio", "--label", "wldn", "--from", "none", "--to", S1], None)])
    def test_a_commit_an_environment_a_partition_or_a_key_crew_cant_take_is_refused(self, argv, said):
        assert ops.args_refusal(FLEET, ops.parser().parse_args(argv)) == said

    def test_crew_ops_answers_help_as_the_deployers_probe_reads_it(self, capsys):
        with pytest.raises(SystemExit) as x:
            ops.parser().parse_args(["--help"])
        assert x.value.code == 0 and "usage: crew ops" in capsys.readouterr().out

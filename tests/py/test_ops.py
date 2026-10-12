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


S3 = "c" * 40


def landed(bolt, head, repo="swancloud", minutes=0, units=()):
    """A landing as crew bolt land records it: the bolt and its units, the kit and the commit its main holds after."""
    return dict(Id=f"20261012T10{minutes:02d}00Z-mac-studio-1-{next(N)}", At=f"2026-10-12T10:{minutes:02d}:00Z", Act="bolt.land",
                On=[f"bolt/{bolt}"] + [f"unit/{u}" for u in units], From=[], Commit=[], Repo=repo, Head=head)


class TestEnvironments:
    def test_a_deploy_offered_approved_and_run_shows_its_word_steps_checks_outcome_and_the_bolts_it_carried(self):
        es = [landed("crew-thing", "d" * 40, repo="crew", minutes=0), landed("apex-zones", S1, minutes=0, units=["zone-one"]),
              landed("tenant-envs", S2, minutes=1), OFFER | {"Base": "none"}, e("ops.approve", minutes=2, Head=S1, By="swancloud-ops"),
              e("ops.deploy", minutes=3, Head=S1, Base="none", Phase="start"),
              e("ops.deploy", minutes=4, Head=S1, Phase="step", Step="machine", Outcome="ok"),
              e("ops.deploy", minutes=5, Head=S1, Phase="step", Step="suite", Outcome="ok",
                Rows='[{"name":"deployer","state":"ok","detail":"","before":"warn","verdict":"better"}]'),
              e("ops.deploy", minutes=6, Head=S1, Phase="end", Outcome="done"),
              e("ops.step", minutes=7, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher", Agent="swancloud-dispatch-mac-studio")]
        d, = ops.environments(es)["mac-studio"]["deploys"]
        assert (d["to"], d["from"], d["answer"], d["word"], d["outcome"], d["row"]) == (S1, "none", "approved",
                                                                                      {"at": "2026-10-12T10:02:00Z", "by": "swancloud-ops"}, "done", None)
        assert [(x["step"], x["outcome"]) for x in d["steps"]] == [("machine", "ok"), ("suite", "ok")]
        assert d["checks"] == [{"name": "deployer", "state": "ok", "detail": "", "before": "warn", "verdict": "better"}]
        assert (d["bolts"], d["bolts_why"]) == (["apex-zones"], None)
        assert [(a["key"], a["state"], a["doer"]) for a in d["after"]] == [("restart-teams/1", "handed", "dispatcher")]

    def test_an_offer_waits_on_the_word_with_its_row_and_a_newer_one_replaces_it_unanswered(self):
        newer = e("ops.offer", minutes=3, Head=S2, Base=S1)
        deploys = ops.environments([OFFER, newer])["mac-studio"]["deploys"]
        assert [(d["to"], d["answer"], d["row"]) for d in deploys] == [(S2, "waiting", "deploy/mac-studio/bbbbbbb"), (S1, "replaced", None)]

    def test_a_newer_offer_waits_beside_an_approved_one_and_a_deploy_with_no_offer_is_unasked(self):
        es = [OFFER, e("ops.approve", minutes=2, Head=S1), e("ops.offer", minutes=3, Head=S2, Base="none"),
              e("ops.deploy", env="swancloud-srv", minutes=4, Head=S3, Base=S1, Phase="start")]
        envs = ops.environments(es)
        assert [(d["to"], d["answer"]) for d in envs["mac-studio"]["deploys"]] == [(S2, "waiting"), (S1, "approved")]
        d, = envs["swancloud-srv"]["deploys"]
        assert (d["answer"], d["from"], d["started"], d["ended"]) == ("unasked", S1, "2026-10-12T10:04:00Z", None)

    def test_the_same_commit_offered_again_after_its_deploy_failed_is_a_new_deploy(self):
        es = [OFFER, e("ops.approve", minutes=2, Head=S1), e("ops.deploy", minutes=3, Head=S1, Phase="start"),
              e("ops.deploy", minutes=4, Head=S1, Phase="end", Outcome="failed"), e("ops.offer", minutes=5, Head=S1, Base="none")]
        assert [(d["answer"], d["outcome"]) for d in ops.environments(es)["mac-studio"]["deploys"]] == [("waiting", None), ("approved", "failed")]

    def test_since_leaves_out_a_deploy_that_last_moved_before_it_unless_still_open(self):
        es = [OFFER, e("ops.approve", minutes=2, Head=S1), e("ops.deploy", minutes=3, Head=S1, Phase="end", Outcome="done"),
              e("ops.offer", env="swancloud-srv", minutes=4, Head=S2, Base="none")]
        envs = ops.environments(es, since="2026-10-12T10:30:00Z")
        assert envs["mac-studio"]["deploys"] == [] and [d["to"] for d in envs["swancloud-srv"]["deploys"]] == [S2]

    def test_the_operations_waiting_are_those_waiting_handed_or_failed_the_users_with_its_row(self):
        es = [e("ops.step", minutes=1, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher"),
              e("ops.step", minutes=2, Key="rotate-tailnet-key", State="waiting", Doer="user", Text="Rotate the key.\nBefore Friday."),
              e("ops.step", minutes=3, Key="check-backups", State="done", Doer="main-ops"),
              e("ops.step", minutes=4, Key="restart-herdr", State="failed", Doer="dispatcher", Note="herdr would not stop")]
        waiting = ops.environments(es)["mac-studio"]["waiting"]
        assert [(w["key"], w["state"], w["row"], w["text"]) for w in waiting] == [
            ("restart-teams/1", "handed", None, None), ("rotate-tailnet-key", "waiting", "op/mac-studio/2", "Rotate the key."),
            ("restart-herdr", "failed", None, None)]
        assert ops.environments(es)["mac-studio"]["deploys"] == []


class TestCarried:
    LANDS = [dict(bolt="one", repo="swancloud", head=S1), dict(bolt="crew-one", repo="crew", head="d" * 40),
             dict(bolt="two", repo="swancloud", head=S2), dict(bolt="three", repo="swancloud", head=S3)]

    def test_a_deploy_carries_its_kits_landings_after_its_from_up_to_its_to(self):
        assert ops.carried(S3, S1, self.LANDS) == (["two", "three"], None)
        assert ops.carried(S2, "none", self.LANDS) == (["one", "two"], None)

    def test_a_commit_no_landing_left_main_at_is_said_rather_than_guessed(self):
        assert ops.carried("e" * 40, S1, self.LANDS) == (None, "eeeeeee is no landing's commit in the record")
        assert ops.carried(S3, "f" * 40, self.LANDS) == (None, "fffffff is no landing's commit in the record")


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

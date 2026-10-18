"""The operations on a partition's environments, a deploy being one kind (plan.14): ops.state on the run record's ops
entries, the rail rows ops.rows makes of them, the approval's refusal and the arguments crew ops refuses; and the
deploy's and the step's cards crew raises (record 0031): the steps and notes an offer is handed, the deploy card's
facts, whether its card is posted or changed, what it closes with, a step's card's facts from its text, and which
step's card is raised, one at a time. That each act is an entry of the run record on the partition's main level's
host, that crew ops word and steps read them back, that quiet reads the host's agents and test slots, that each card
is posted, changed and closed, and that a command run elsewhere runs there are the ops journey's (t-journey-ops)."""
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
    def test_an_open_offer_is_a_deploy_row_keyed_by_its_environment_whose_card_crew_raises_in_main_level_opss_name(self):
        row, = ops.rows(None, "swancloud", [OFFER])
        assert row["key"] == "deploy/mac-studio" and row["group"] == "operations"
        assert row["what"] == ["deploy mac-studio (swancloud) to aaaaaaa, from nothing deployed: crew raises its card in swancloud-ops's name, "
                               "and holding it is the word to deploy"]
        newer, = ops.rows(None, "swancloud", [OFFER, e("ops.offer", minutes=2, Head=S2, Base="none")])
        assert newer["key"] == "deploy/mac-studio" and newer["cmds"] == [("answer", f"crew ops approve mac-studio --to {S2} --label swancloud")]
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

    def test_an_agents_step_held_for_the_users_word_is_a_row_until_marked_and_one_it_runs_on_its_own_is_none(self):
        steps = [e("ops.step", minutes=1, Head=S1, Key="restart-teams/1", State="waiting", Doer="main-ops", Agent="swancloud-ops",
                   When="quiet held", Text="Restart crew's teams."),
                 e("ops.step", minutes=2, Head=S1, Key="restart-herdr/1", State="waiting", Doer="dispatcher", When="quiet")]
        row, = ops.rows(None, "swancloud", steps)
        assert row["key"] == "op/mac-studio/1"
        assert row["what"] == ["an operation after the deploy of mac-studio to aaaaaaa (swancloud), swancloud-ops's, held for your word: Restart crew's teams."]
        assert row["cmds"][1] == ("decline", f"crew ops step mac-studio --to {S1} --key restart-teams/1 --state declined --label swancloud")
        assert ops.rows(None, "swancloud", steps + [e("ops.step", minutes=3, Head=S1, Key="restart-teams/1", State="done")]) == []
        assert (ops.held(steps[0]), ops.held(steps[1])) == (True, False)


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
        assert [(d["to"], d["answer"], d["row"]) for d in deploys] == [(S2, "waiting", "deploy/mac-studio"), (S1, "replaced", None)]

    def test_a_newer_offer_waits_beside_an_approved_one_and_a_deploy_with_no_offer_is_unasked(self):
        es = [OFFER, e("ops.approve", minutes=2, Head=S1), e("ops.offer", minutes=3, Head=S2, Base="none"),
              e("ops.deploy", env="swancloud-srv", minutes=4, Head=S3, Base=S1, Phase="start")]
        envs = ops.environments(es)
        assert [(d["to"], d["answer"]) for d in envs["mac-studio"]["deploys"]] == [(S2, "waiting"), (S1, "approved")]
        d, = envs["swancloud-srv"]["deploys"]
        assert (d["answer"], d["from"], d["started"], d["ended"]) == ("unasked", S1, "2026-10-12T10:04:00Z", None)

    def test_an_approved_deploy_not_started_is_replaced_once_the_word_goes_to_a_newer_offer_as_state_reads_the_word(self):
        """mac-studio, 2026-10-15: 45eecf3 approved while the host already ran it, so the deployer never deployed it;
        291a4e6 offered from it, approved and deployed. ops.state dropped 45eecf3's word at 291a4e6's approval, and the
        board kept 45eecf3 approved, not yet deployed, above main-level ops's prompt for days."""
        es = [OFFER, e("ops.approve", minutes=2, Head=S1, By="swancloud-ops"), e("ops.offer", minutes=3, Head=S2, Base=S1),
              e("ops.approve", minutes=4, Head=S2), e("ops.deploy", minutes=5, Head=S2, Base=S1, Phase="start"),
              e("ops.deploy", minutes=6, Head=S2, Phase="end", Outcome="done")]
        new, old = ops.environments(es)["mac-studio"]["deploys"]
        assert (new["to"], new["answer"], new["outcome"]) == (S2, "approved", "done")
        assert (old["to"], old["answer"], old["word"], old["ended"], old["at"]) == (
            S1, "replaced", {"at": "2026-10-12T10:02:00Z", "by": "swancloud-ops"}, None, "2026-10-12T10:04:00Z")
        for n in range(1, len(es) + 1):  # at every point, the deploy approved and not ended is the word ops.state reads
            word = ops.state(es[:n])[1].get("mac-studio", {}).get("Head")
            assert [d["to"] for d in ops.environments(es[:n])["mac-studio"]["deploys"]
                    if d["answer"] == "approved" and not d["ended"]] == ([word] if word else [])

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
              e("ops.step", minutes=4, Key="restart-herdr", State="failed", Doer="dispatcher", Note="herdr would not stop"),
              e("ops.step", minutes=5, Key="restart-teams/2", State="waiting", Doer="main-ops", When="held")]
        waiting = ops.environments(es)["mac-studio"]["waiting"]
        assert [(w["key"], w["state"], w["row"], w["text"], w["held"]) for w in waiting] == [
            ("restart-teams/1", "handed", None, None, False), ("rotate-tailnet-key", "waiting", "op/mac-studio/2", "Rotate the key.", False),
            ("restart-herdr", "failed", None, None, False), ("restart-teams/2", "waiting", "op/mac-studio/5", None, True)]
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
        (["step", "mac-studio", "--label", "wldn", "--key", "k", "--state", "waiting", "--doer", "user", "--held"],
         "--held marks an agent's step held for the user's word: give its --doer, dispatcher or main-ops"),
        (["step", "mac-studio", "--label", "wldn", "--key", "k", "--state", "waiting", "--doer", "main-ops", "--when", "quiet", "--held"], None),
        (["offer", "mac-studio", "--label", "wldn", "--from", "none", "--to", S1, "--notes", "n.md", "--steps", "s.txt"], None),
        (["offer", "mac-studio", "--label", "wldn", "--from", "none", "--to", S1], None)])
    def test_a_commit_an_environment_a_partition_or_a_key_crew_cant_take_is_refused(self, argv, said):
        assert ops.args_refusal(FLEET, ops.parser().parse_args(argv)) == said

    def test_crew_ops_answers_help_as_the_deployers_probe_reads_it(self, capsys):
        with pytest.raises(SystemExit) as x:
            ops.parser().parse_args(["--help"])
        assert x.value.code == 0 and "usage: crew ops" in capsys.readouterr().out


# ------------------------------------------------------------------------- the deploy's and the step's cards (record 0031)
import cards  # noqa: E402

STEPS = ("step\t1\tuser\t\tswancloud-srv\tOnly you hold the vault.\trotate the kanidm admin password\n"
         "step\t2\tmain-ops\tquiet held\t\tIt ends a stage mid-unit.\trestart crew's teams\n"
         "step\t1\tdispatcher\tdeployed\tmac-studio\tNo check sees it.\trestart the box's herdr\n")
NOTES = "## swancloud-srv-v0.3.0 (2026-10-15)\n### Fixes\n- deployer: crew reaches the boxes with the peer key (e5b8322)"


class TestOfferHanded:
    def test_the_steps_handed_are_those_for_the_environment_or_every_one_each_with_its_doer_as_a_card_names_it(self):
        steps, why = ops.handed_steps(STEPS, "swancloud-srv", "swancloud")
        assert why is None and steps == [dict(n="1", text="rotate the kanidm admin password", doer="user", held=False),
                                         dict(n="2", text="restart crew's teams", doer="swancloud-ops", held=True)]
        assert [(x["n"], x["doer"]) for x in ops.handed_steps(STEPS, "mac-studio", "swancloud")[0]] == [
            ("2", "swancloud-ops"), ("1", "swancloud-dispatch-mac-studio")]
        assert ops.handed_steps(None, "mac-studio", "swancloud") == ([], None)

    def test_a_steps_file_crew_cant_read_is_named_by_its_line(self):
        assert ops.handed_steps("step\t1\tuser\t\t\twhy\trotate it\nfault\t2\tno why\tx\n", "srv", "swancloud") == (
            None, "line 2 is no step crew reads: step <n> <doer> <when> <environments> <why> <text>, tab-separated, "
                  "the doer dispatcher, main-ops or user")
        assert ops.handed_steps("step\t1\tthe-user\t\t\twhy\trotate it\n", "srv", "swancloud")[0] is None

    def test_the_notes_release_is_the_one_git_cliff_heads_them_with(self):
        assert ops.release_of(NOTES) == "swancloud-srv-v0.3.0"
        assert ops.release_of("## [0.4.0] - 2026-10-16\n### Features\n- x") == "0.4.0"
        assert ops.release_of(NOTES + "\n\n## swancloud-srv-v0.2.9 (2026-10-14)\n- y") is None and ops.release_of(None) is None


DEPLOYED = [landed("deployer-holds", S1, minutes=0), e("ops.offer", minutes=1, Head=S1, Base="none"), e("ops.approve", minutes=2, Head=S1),
            e("ops.deploy", minutes=3, Head=S1, Phase="start", Base="none"), e("ops.deploy", minutes=4, Head=S1, Phase="step", Step="machine", Outcome="ok"),
            e("ops.deploy", minutes=5, Head=S1, Phase="step", Step="suite", Outcome="ok"), e("ops.deploy", minutes=6, Head=S1, Phase="end", Outcome="ok"),
            e("ops.deploy", env="box", minutes=7, Head=S2, Phase="end", Outcome="ok"),
            landed("doctor-names-step", S2, minutes=8), landed("retry-offered", S3, minutes=9)]


class TestDeployCard:
    def test_the_notes_and_steps_handed_are_on_its_face_with_the_landings_since_the_environments_last_deploy_in_its_details(self):
        offer = e("ops.offer", minutes=10, Head=S3, Base=S1)
        steps = ops.handed_steps(STEPS, "mac-studio", "swancloud")[0]
        f = ops.deploy_facts("mac-studio", offer, DEPLOYED + [offer], NOTES, steps)
        assert (f["head"], f["base"], f["landings"], f["landings_why"]) == (S3, S1, [{"pr": None, "subject": "doctor-names-step"},
                                                                                       {"pr": None, "subject": "retry-offered"}], None)
        assert (f["release"], f["before"], f["after"]) == ("swancloud-srv-v0.3.0", [], [])
        c = cards.deploy_card(f)["card"]
        assert c["summary"] == "2 landings since mac-studio's last deploy (aaaaaaa). After the deploy: 2 steps, 0 yours."
        notes, listed = c["artifacts"]
        assert (notes["lang"], notes["title"], notes["lines"]) == ("markdown", "What's in it: swancloud-srv-v0.3.0", NOTES.split("\n"))
        assert listed["lines"] == ["2  restart crew's teams", "   swancloud-ops, held for your word", "1  restart the box's herdr",
                                   "   swancloud-dispatch-mac-studio"]
        assert c["context"]["background"] == "Landings since mac-studio's last deploy:\ndoctor-names-step\nretry-offered"

    def test_an_offer_handed_neither_gives_the_landings_subjects_and_says_the_kit_handed_no_release_notes(self):
        offer = e("ops.offer", minutes=10, Head=S2, Base=S1)
        c = cards.deploy_card(ops.deploy_facts("mac-studio", offer, DEPLOYED + [offer]))["card"]
        assert c["summary"] == "1 landing since mac-studio's last deploy (aaaaaaa). The kit handed no release notes. It comes after box."
        assert [(a["lang"], a["title"], a["lines"]) for a in c["artifacts"]] == [("text", "What's in it: 1 landing", ["doctor-names-step"])]

    def test_landings_crew_cant_read_are_said_rather_than_counted(self):
        offer = e("ops.offer", minutes=10, Head="d" * 40, Base=S1)
        f = ops.deploy_facts("mac-studio", offer, DEPLOYED + [offer], unread={"chuck-herdr-alpha": "no answer"})
        assert f["landings"] == [] and f["landings_why"] == "ddddddd is no landing's commit in the record; chuck-herdr-alpha did not answer"
        c = cards.deploy_card(f)["card"]
        assert c["summary"].startswith("Which landings it carries since mac-studio's last deploy (aaaaaaa) can't be read: ddddddd is no")
        assert [(a["title"], a["lines"]) for a in c["artifacts"]] == [("What's in it", ["ddddddd is no landing's commit in the",
                                                                                          "  record; chuck-herdr-alpha did not", "  answer"])]

    def test_a_newer_offer_changes_the_card_of_one_unanswered_and_waits_on_an_approved_ones_deploy(self):
        newer = e("ops.offer", minutes=3, Head=S2, Base="none")
        assert ops.deploy_move([OFFER], "mac-studio", None) == ("post", None)
        assert ops.deploy_move([OFFER, newer], "mac-studio", "req_1") == ("change", "Now offering bbbbbbb, which includes aaaaaaa")
        approved = [OFFER, e("ops.approve", minutes=2, Head=S1), newer]
        assert ops.deploy_move(approved, "mac-studio", "req_1") == (
            None, "its card asks for the deploy of aaaaaaa, approved, and the offer of bbbbbbb is raised once that deploy ends")
        assert ops.deploy_move(approved, "mac-studio", None) == ("post", None)
        assert ops.deploy_move([OFFER, e("ops.approve", minutes=2, Head=S1)], "mac-studio", "req_1") == (None, "no deploy of mac-studio is offered")

    def test_its_card_closes_with_each_steps_outcome_or_the_step_that_failed_and_its_log(self):
        assert ops.deploy_outcome(DEPLOYED, "mac-studio", S1, "ok") == "Deployed aaaaaaa to mac-studio: machine ok, suite ok."
        failed = DEPLOYED + [e("ops.deploy", minutes=11, Head=S1, Phase="start"),
                             e("ops.deploy", minutes=12, Head=S1, Phase="step", Step="guests", Outcome="failed", Log="/var/log/deployer/guests.log")]
        assert ops.deploy_outcome(failed, "mac-studio", S1, "failed") == "The deploy of aaaaaaa to mac-studio failed at guests; its log: /var/log/deployer/guests.log."
        assert ops.deploy_outcome([], "srv", S2, "failed", "/tmp/run.log") == "The deploy of bbbbbbb to srv failed; its log: /tmp/run.log."


ROTATE = """rotate the kanidm admin password
in its vault
- why: Only you hold the vault, and no check can tell it was done.
- where: a terminal on mac-studio
- command: clan vars generate swancloud-srv --generator kanidm-admin
    --regenerate
- command: clan machines update swancloud-srv
- done: kanidm's login page takes the new password.
"""


class TestStepCard:
    def test_the_users_step_is_a_do_with_its_words_where_each_command_whole_and_when_it_is_done(self):
        f = ops.step_facts("srv", 1, e("ops.step", env="srv", Key="rotate/1", State="waiting", Doer="user", Text=ROTATE), "swancloud")
        assert (f["text"], f["doer"], f["held"], f["where"]) == ("rotate the kanidm admin password in its vault", "user", False, "a terminal on mac-studio")
        assert f["commands"] == ["clan vars generate swancloud-srv --generator kanidm-admin --regenerate", "clan machines update swancloud-srv"]
        c = cards.step_card(f)["card"]
        assert (c["kind"], c["intent"], c["summary"]) == ("action", "do", "Only you hold the vault, and no check can tell it was done.")
        assert c["action"]["steps"][0]["command"] == "clan vars generate swancloud-srv --generator kanidm-admin --regenerate"
        assert c["action"]["done"] == "kanidm's login page takes the new password."
        assert ops.step_words(" ".join(ROTATE.split())) == ops.step_words(ROTATE)

    def test_a_held_steps_card_is_a_choice_of_when_saying_what_now_cuts(self):
        step = e("ops.step", Key="restart-teams/1", State="waiting", Doer="main-ops", When="quiet held", Text="restart crew's teams\n- why: It ends a stage.")
        f = ops.step_facts("mac-studio", 2, step, "swancloud", ["atl-1-unit-2"])
        assert (f["doer"], f["held"], f["consequences"]) == ("swancloud-ops", True, {"now": "It runs at once, cutting the stage of atl-1-unit-2"})
        c = cards.step_card(f)["card"]
        assert (c["kind"], c["recommendedIds"]) == ("choice", ["quiet"])
        assert [(o["id"], o["consequence"]) for o in c["options"]] == [("quiet", "No stage is cut; it could be hours"),
                                                                       ("now", "It runs at once, cutting the stage of atl-1-unit-2"), ("skip", "It is not done")]
        assert ops.step_facts("mac-studio", 2, step, "swancloud", [])["consequences"]["now"] == "It runs at once; no stage is working on mac-studio now"
        assert ops.step_facts("mac-studio", 2, step, "swancloud", "herdr did not answer")["consequences"]["now"] == (
            "It runs at once, whatever is working on mac-studio: crew could not tell what is (herdr did not answer)")
        assert ops.step_facts("mac-studio", 2, dict(step, Text=None), "swancloud")["text"] == "restart-teams/1"


def card(act, key, card_id, minutes, **f):
    return dict(Act=act, Key=key, Card=card_id, At=f"2026-10-12T11:{minutes:02d}:00Z", **f)


class TestOneStepCardAtATime:
    STEPS = [e("ops.step", minutes=1, Head=S1, Key="restart-teams/1", State="handed", Doer="dispatcher"),
             e("ops.step", minutes=2, Head=S1, Key="rotate/1", State="waiting", Doer="user"),
             e("ops.step", minutes=3, Head=S1, Key="restart-herdr/1", State="waiting", Doer="main-ops", When="held")]
    DEPLOY = [card("card.post", "deploy/mac-studio", "req_d", 1)]

    def test_the_first_step_that_waits_on_the_user_is_raised_and_the_next_only_once_its_card_closes(self):
        due, open_ = ops.step_due(self.STEPS, self.DEPLOY, "mac-studio")
        assert (due[0], due[1], open_) == (2, ("mac-studio", S1, "rotate/1"), None)
        posted = self.DEPLOY + [card("card.post", "op/mac-studio/2", "req_s2", 2)]
        assert ops.step_due(self.STEPS, posted, "mac-studio") == (None, "op/mac-studio/2")
        done = self.STEPS + [e("ops.step", minutes=4, Head=S1, Key="rotate/1", State="done")]
        closed = posted + [card("card.close", "op/mac-studio/2", "req_s2", 3, State="closed")]
        due, open_ = ops.step_due(done, closed, "mac-studio")
        assert (due[0], due[1][2], open_) == (3, "restart-herdr/1", None)
        follows = cards.follows_of("step", {"env": "mac-studio", "key": "op/mac-studio/3"}, closed)
        assert follows == "req_s2" and cards.follows_of("step", {"env": "mac-studio", "key": "op/mac-studio/2"}, self.DEPLOY) == "req_d"

    def test_a_step_whose_card_was_raised_is_not_raised_again_and_another_environments_card_holds_none(self):
        had = self.DEPLOY + [card("card.post", "op/mac-studio/2", "req_s2", 2), card("card.close", "op/mac-studio/2", "req_s2", 3),
                             card("card.post", "op/mac-studio/3", "req_s3", 4), card("card.close", "op/mac-studio/3", "req_s3", 5),
                             card("card.post", "op/box/1", "req_b1", 6)]
        assert ops.step_due(self.STEPS, had, "mac-studio") == (None, None)
        assert ops.step_due(self.STEPS, self.DEPLOY + had[-1:], "mac-studio")[0][0] == 2

    def test_a_rows_point_has_come_when_it_is_next_due_or_its_card_is_the_one_open_as_the_rails_sweep_asks(self):
        assert ops.step_point(self.STEPS, self.DEPLOY, "op/mac-studio/2")[0][0] == 2
        assert ops.step_point(self.STEPS, self.DEPLOY, "op/mac-studio/3") == (None, "its step waits on no one, or another's card comes first")
        posted = self.DEPLOY + [card("card.post", "op/mac-studio/2", "req_s2", 2)]
        assert ops.step_point(self.STEPS, posted, "op/mac-studio/2")[0][1] == ("mac-studio", S1, "rotate/1")
        assert ops.step_point(self.STEPS, posted, "op/mac-studio/3") == (None, "card op/mac-studio/2 is open: this step's card is raised when it closes")
        done = self.STEPS + [e("ops.step", minutes=4, Head=S1, Key="rotate/1", State="done")]
        assert ops.step_point(done, posted, "op/mac-studio/2") == (None, "its step no longer waits on the user")

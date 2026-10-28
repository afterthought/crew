"""A held bolt's age and who held its time (plan.20, record 0044; crew-board "Each minute of a bolt's life goes to one
holder" and "A held bolt's head line shows its age and who held its time"): the split, plan.bolt_time, a decision of
facts alone, each case a scenario of the crew-board delta; and what it is split from, plan.bolt_facts, read from the
run record and sluice's submissions."""
import datetime

from facts import START, at, plan_text

import plan

GIVE = datetime.datetime(2026, 10, 27, 11, 0, tzinfo=datetime.timezone.utc)


def t(minutes):
    """A time, minutes after the bolt's give."""
    return GIVE + datetime.timedelta(minutes=minutes)


def split(end, stages=(), submissions=(), cards=(), holds=()):
    return plan.bolt_time(GIVE, t(end), list(stages), list(submissions), list(cards), list(holds))


def shares(**minutes):
    return dict(dict.fromkeys(plan.HOLDERS, 0), **minutes)


# ------------------------------------------------------------------------------------------------ one holder a minute

def test_a_team_at_work():
    """Given three hours ago, a code stage ran two hours, a batch card holding its unit was open forty minutes with
    nothing running, and nothing held it twenty minutes."""
    got = split(180, stages=[{"start": t(0), "end": t(120), "merge": False, "what": "code on a"}],
                cards=[{"at": t(120), "until": t(160), "key": "batch/12"}])
    assert got["age"] == 180 and got["shares"] == shares(team=120, user=40, nobody=20)
    assert got["now"] == {"holder": "nobody", "what": None, "since": t(160)} and got["stalled"]


def test_a_merge_under_test():
    """a's merge #41 stood queued five minutes and under test twelve, while a's merge stage ran throughout."""
    merge = {"start": t(0), "end": None, "merge": True, "what": "merge on a"}
    queued = {"submitted": t(0), "started": None, "decided": None, "state": "queued", "what": "#41"}
    assert split(5, stages=[merge], submissions=[queued])["now"]["holder"] == "team"
    testing = dict(queued, started=t(5), state="testing")
    got = split(17, stages=[merge], submissions=[testing])
    assert got["shares"] == shares(team=5, kit=12)
    assert got["now"] == {"holder": "kit", "what": "#41", "since": t(5)}


def test_a_stage_beside_a_merge_under_test_is_the_teams():
    """c's code stage runs while a's merge #41 is under test."""
    got = split(30, stages=[{"start": t(10), "end": None, "merge": False, "what": "code on c"}],
                submissions=[{"submitted": t(0), "started": t(0), "decided": None, "state": "testing", "what": "#41"}])
    assert got["shares"] == shares(kit=10, team=20)
    assert got["now"] == {"holder": "team", "what": "code on c", "since": t(10)}


def test_a_decided_merge_whose_checks_start_is_not_kept_is_the_kits_whole_stay():
    """sluice's record of #41, landed, gives when it was submitted and decided but not when its checks began."""
    got = split(30, stages=[{"start": t(0), "end": t(25), "merge": True, "what": "merge on a"}],
                submissions=[{"submitted": t(3), "started": None, "decided": t(20), "state": "landed", "what": "#41"}])
    assert got["shares"] == shares(team=8, kit=17, nobody=5)


def test_a_card_counts_only_while_nothing_moves_and_a_hold_only_while_no_one_else_holds():
    got = split(60, stages=[{"start": t(0), "end": t(20), "merge": False}],
                cards=[{"at": t(10), "until": t(40), "key": "land/crew"}],
                holds=[{"at": t(30), "until": None, "what": "its host deneb is held by chuck"}])
    assert got["shares"] == shares(team=20, user=20, hold=20)
    assert got["now"] == {"holder": "hold", "what": "its host deneb is held by chuck", "since": t(40)}


# ---------------------------------------------------------------------------------------------- stalled, or a moment

def test_stalled_once_nobody_has_held_it_five_minutes():
    """Nothing of b has run, stood in sluice, had a card open or been held for seven minutes."""
    got = split(27, stages=[{"start": t(0), "end": t(20), "merge": False}])
    assert got["shares"] == shares(team=20, nobody=7)
    assert got["now"] == {"holder": "nobody", "what": None, "since": t(20)} and got["stalled"]


def test_nobody_for_a_moment_is_not_stalled():
    """A stage of b ended two minutes ago and nothing has started since."""
    got = split(22, stages=[{"start": t(0), "end": t(20), "merge": False}])
    assert got["now"]["holder"] == "nobody" and got["now"]["since"] == t(20) and not got["stalled"]


# ------------------------------------------------------------------------------------------------------- the edges

def test_the_shares_sum_to_the_age():
    """Pieces that are not whole minutes still give whole minutes that add up."""
    sec = datetime.timedelta(seconds=1)
    got = plan.bolt_time(GIVE, t(10) + 50 * sec, [{"start": t(0) + 20 * sec, "end": t(3) + 40 * sec, "merge": False}],
                         [{"submitted": t(4), "started": None, "decided": t(6) + 30 * sec, "state": "landed"}],
                         [{"at": t(7), "until": None, "key": "land/b"}], [])
    assert got["age"] == 10 and sum(got["shares"].values()) == 10


def test_a_stage_with_no_end_runs_to_the_end():
    got = split(45, stages=[{"start": t(15), "end": None, "merge": False, "what": "verify on a"}])
    assert got["shares"] == shares(nobody=15, team=30) and got["now"]["what"] == "verify on a"


def test_a_card_closed_before_the_give_is_left_out_and_one_open_across_it_counts_from_the_give():
    got = split(30, cards=[{"at": t(-60), "until": t(-10), "key": "batch/3"}, {"at": t(-5), "until": t(10), "key": "batch/4"}])
    assert got["shares"] == shares(user=10, nobody=20)


def test_a_standing_submission_testing_with_no_start_of_checks_counts_from_its_submit():
    got = split(20, submissions=[{"submitted": t(5), "started": None, "decided": None, "state": "testing", "what": "#9"}])
    assert got["shares"] == shares(nobody=5, kit=15) and got["now"] == {"holder": "kit", "what": "#9", "since": t(5)}


def test_a_submission_standing_not_under_test_is_the_teams():
    got = split(20, submissions=[{"submitted": t(5), "started": None, "decided": None, "state": "passed", "what": "#9"}])
    assert got["shares"] == shares(nobody=5, team=15)


def test_a_bolt_given_this_minute_is_nobodys_and_not_stalled():
    got = split(0)
    assert got == {"age": 0, "shares": shares(), "now": {"holder": "nobody", "what": None, "since": GIVE}, "stalled": False}


# ------------------------------------------------------------------------------------- each holder from what crew keeps


PLAN = plan.Plan(plan_text(bolts=[("b", "switchboard-kit", "swb-1"), ("o", "switchboard-kit", "swb-2")],
                           units=[("a", "switchboard-kit", "b", []), ("c", "switchboard-kit", "b", [], "chore"),
                                  ("x", "switchboard-kit", "o", [])]))


def e(act, minutes, *on, **fields):
    """A run-record entry, minutes after START, as record.parse reads one."""
    return dict({"Act": act, "At": at(minutes), "On": list(on)}, **fields)


def given(minutes=0):
    return e("bolt.give", minutes, "bolt/b", "team/swb-1")


def facts_of(entries, standing=(), history=(), unread=None):
    return plan.bolt_facts(entries, PLAN, "b", "swb-1", "chuck-herdr-alpha", "switchboard-kit", (list(standing), None),
                           (list(history), None), unread)


def mins(m):
    return START + datetime.timedelta(minutes=m)


def test_the_give_is_the_newest_and_its_stages_pair_with_their_ends():
    entries = [given(-500), e("bolt.give", -100, "bolt/b", "team/swb-1", Refused="its team is down"), given(0),
               e("stage.start", 5, "stage/a/code", "unit/a", "agent/swb-1-unit-1"),
               e("stage.start", 6, "stage/c/code", "chore/c", "agent/swb-1-unit-2"),
               e("stage.end", 30, "stage/a/code", "unit/a", "agent/swb-1-unit-1"),
               e("stage.start", 40, "stage/x/code", "unit/x", "agent/swb-2-unit-1"),
               e("fix.start", 50, "fix/b/take-main", "bolt/b", "agent/swb-1-unit-3"),
               e("stage.end", 55, "fix/b/take-main", "agent/swb-1-unit-3"),
               e("fix.merge", 56, "fix/b/take-main", "bolt/b", "agent/swb-1-unit-3"),
               e("stage.start", 57, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("stage.end", 70, "stage/a/merge", "unit/a", "agent/swb-1-unit-1")]
    got = facts_of(entries)
    assert got["start"] == mins(0)
    assert got["stages"] == [
        {"start": mins(5), "end": mins(30), "merge": False, "what": "code on a"},
        {"start": mins(6), "end": None, "merge": False, "what": "code on chore c"},
        {"start": mins(50), "end": mins(55), "merge": False, "what": "fix fix/b/take-main"},
        {"start": mins(56), "end": None, "merge": True, "what": "merge of fix/b/take-main"},
        {"start": mins(57), "end": mins(70), "merge": True, "what": "merge on a"}]


def test_the_users_card():
    """Every unit of b has merged, nothing runs, and its kit's landings card has been open for an hour."""
    entries = [given(0), e("stage.start", 0, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("stage.end", 60, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("card.post", 30, "bolt/o", Card="req_1", Key="land/switchboard-kit", By="wldn-ops"),
               e("card.close", 30, Card="req_1", Key="land/switchboard-kit", State="closed"),
               e("card.post", 60, Card="req_2", Key="land/switchboard-kit", By="wldn-ops")]
    got = plan.time_at(facts_of(entries), mins(120))
    assert got["shares"]["user"] == 60 and got["shares"]["team"] == 60
    assert got["now"] == {"holder": "user", "what": "land/switchboard-kit", "since": mins(60)}


def test_a_question_from_the_team_while_it_holds_the_bolt_is_the_users():
    """swb-1's unit stopped short and swb-1-conductor's question is open, with nothing of its bolt running."""
    entries = [e("card.post", -20, Card="req_9", Key=None, By="swb-1-conductor"), given(0),
               e("card.post", 10, Card="req_3", Key=None, By="swb-1-conductor"),
               e("card.post", 12, Card="req_4", Key="ask/swb-2", By="swb-2-conductor"),
               e("card.post", 14, Card="req_5", Key=None, By="swb-1-unit-2")]
    got = facts_of(entries)
    assert [c["key"] for c in got["cards"]] == [None, None]
    assert [c["at"] for c in got["cards"]] == [mins(10), mins(14)]


def test_a_held_host():
    """Nothing of b runs and no card of it is open, while its team's host was held at 14:02 and not let go."""
    entries = [given(0), e("host.hold", 10, "host/chuck-herdr-alpha", By="chuck"), e("host.go", 20, "host/chuck-herdr-alpha", By="chuck"),
               e("host.hold", 30, "host/mac-studio", By="chuck"), e("host.hold", 40, "host/chuck-herdr-alpha", By="chuck")]
    got = plan.time_at(facts_of(entries), mins(50))
    assert got["shares"]["hold"] == 20 and got["shares"]["nobody"] == 30
    assert got["now"] == {"holder": "hold", "what": "its host chuck-herdr-alpha is held by chuck", "since": mins(40)}


def test_a_batch_card_a_proposal_card_and_a_card_whose_post_names_the_work_are_the_bolts():
    entries = [given(0), e("review.batch", 1, Batch="12", Units="a:swb-1@abc1234 x:swb-2@def5678"),
               e("review.batch", 1, Batch="13", Units="x:swb-2@def5678"),
               e("card.post", 2, "batch/12", Card="req_b12", Key="batch/12", By="wldn-planner"),
               e("card.post", 2, "batch/13", Card="req_b13", Key="batch/13", By="wldn-planner"),
               e("plan.propose", 3, "proposal/7", "unit/a", "bolt/b"), e("plan.propose", 4, "proposal/8", "unit/x"),
               e("plan.propose", 5, "proposal/9", "unit/x", "proposal/8"), e("plan.propose", 5, "proposal/10", "unit/y", "proposal/7"),
               e("card.post", 6, "proposal/7", Card="req_p7", Key="proposal/7", By="wldn-planner"),
               e("card.post", 6, "proposal/8", Card="req_p8", Key="proposal/8", By="wldn-planner"),
               e("card.post", 7, "unit/a", Card="req_r", Key="record/switchboard-kit/0012", By="wldn-design")]
    assert sorted(c["key"] for c in facts_of(entries)["cards"]) == ["batch/12", "proposal/7", "record/switchboard-kit/0012"]


def test_a_card_lost_to_its_owner_and_posted_again_counts_as_one_open_card():
    entries = [given(0), e("card.post", 10, Card="req_1", Key="land/b", By="swb-1-conductor"),
               e("card.close", 20, Card="req_1", Key="land/b", State="lost"),
               e("card.post", 25, Card="req_2", Key="land/b", By="swb-1-conductor"),
               e("card.close", 40, Card="req_2", Key="land/b", State="closed")]
    assert [(c["at"], c["until"]) for c in facts_of(entries)["cards"]] == [(mins(10), mins(40))]


def test_the_kits_landings_card_counts_from_the_bolts_last_merge():
    entries = [given(0), e("card.post", 5, Card="req_1", Key="land/switchboard-kit", By="wldn-ops"),
               e("stage.start", 10, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("stage.end", 30, "stage/a/merge", "unit/a", "agent/swb-1-unit-1")]
    assert [c["at"] for c in facts_of(entries)["cards"]] == [mins(30)]
    assert facts_of(entries[:2])["cards"] == []


def test_the_bolts_submissions_standing_over_its_record_and_none_of_another_bolts():
    hist = [{"id": 41, "branch": "bolt/b", "state": "landed", "submitted": at(5), "told": at(20), "worktree": "unit/a", "pull_head": None},
            {"id": 42, "branch": "bolt/b", "state": "queued", "submitted": at(21), "told": None, "worktree": "chore/c", "pull_head": None},
            {"id": 43, "branch": "bolt/o", "state": "landed", "submitted": at(5), "told": at(9), "worktree": "unit/x", "pull_head": None},
            {"id": 44, "branch": "main", "state": "withdrawn", "submitted": at(30), "told": at(31), "worktree": "pull/9", "pull_head": "bolt/b"},
            {"id": 45, "branch": "bolt/b", "state": "landed", "submitted": at(5), "told": at(6), "worktree": "unit/stray", "pull_head": None}]
    standing = [{"id": 42, "branch": "bolt/b", "state": "testing", "submitted": at(21), "started": at(25), "worktree": "chore/c", "pull_head": None},
                {"id": 46, "branch": "main", "state": "queued", "submitted": at(40), "started": None, "worktree": "bolt/b", "pull_head": None}]
    got = facts_of([given(0)], standing, hist)["submissions"]
    assert got == [{"submitted": mins(5), "started": None, "decided": mins(20), "state": "landed", "what": "#41"},
                   {"submitted": mins(21), "started": mins(25), "decided": None, "state": "testing", "what": "#42"},
                   {"submitted": mins(30), "started": None, "decided": mins(31), "state": "withdrawn", "what": "#44"},
                   {"submitted": mins(40), "started": None, "decided": None, "state": "queued", "what": "#46"}]


def test_a_give_that_cant_be_read_is_said_and_shows_no_share():
    """The run record holds no give of b in the days the board reads."""
    got = plan.time_at(facts_of([e("bolt.give", 0, "bolt/o", "team/swb-2")]), mins(10))
    assert got == {"unknown": "its age can't be told: the run record of the last 60 days holds no give of it"}


def test_a_record_that_cant_be_read_is_said():
    got = facts_of([given(0)], unread={"wldn/main of WilldanGroup/crew-state": "fetch failed"})
    assert got == {"unknown": "its age can't be told: wldn/main of WilldanGroup/crew-state could not be read (fetch failed)"}


def test_submissions_that_cant_be_read_keep_the_age_and_tell_no_share():
    got = plan.bolt_facts([given(0)], PLAN, "b", "swb-1", "chuck-herdr-alpha", "switchboard-kit", ([], None),
                          (None, "sluice status bolt/b exited 1: no such branch"))
    assert plan.time_at(got, mins(65)) == {
        "unknown": "who held its time can't be told: its submissions can't be read: sluice status bolt/b exited 1: no such branch", "age": 65}


def test_a_decided_submission_with_no_time_it_was_decided_is_said():
    hist = [{"id": 41, "branch": "bolt/b", "state": "landed", "submitted": at(5), "told": None, "worktree": "unit/a", "pull_head": None}]
    assert facts_of([given(0)], history=hist)["unknown"] == "who held its time can't be told: sluice's record of #41 gives no time it was decided"

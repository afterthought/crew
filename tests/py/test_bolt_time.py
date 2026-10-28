"""A held bolt's age and who held its time (plan.20, record 0044; crew-board "Each minute of a bolt's life goes to one
holder" and "A held bolt's head line shows its age and who held its time"): the split, plan.bolt_time, a decision of
facts alone, each case a scenario of the crew-board delta."""
import datetime

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

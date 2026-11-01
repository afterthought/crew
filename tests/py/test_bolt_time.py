"""A started bolt's age and who held its time (plan.20, record 0044; crew-board "Each minute of a bolt's life goes to
one holder" and "A held bolt's head line shows its age and who held its time"): the split, plan.bolt_time, a decision
of facts alone, each case a scenario of the crew-board delta; and what it is split from, plan.bolt_facts, read from the
run record and sluice's submissions as its overview gave them and the follower kept them, from the run record's entry
that made the bolt's branch (Decision 11 of the-team-machinery-leaves)."""
import datetime

from facts import START, at, plan_text

import plan

STARTED = datetime.datetime(2026, 10, 27, 11, 0, tzinfo=datetime.timezone.utc)


def t(minutes):
    """A time, minutes after the bolt's start."""
    return STARTED + datetime.timedelta(minutes=minutes)


def split(end, stages=(), submissions=(), cards=(), holds=()):
    return plan.bolt_time(STARTED, t(end), list(stages), list(submissions), list(cards), list(holds))


def shares(**minutes):
    return dict(dict.fromkeys(plan.HOLDERS, 0), **minutes)


# ------------------------------------------------------------------------------------------------ one holder a minute

def test_a_team_at_work():
    """Started three hours ago, a code stage ran two hours, a batch card holding its unit was open forty minutes with
    nothing running, and nothing held it twenty minutes."""
    got = split(180, stages=[{"start": t(0), "end": t(120), "merge": False, "what": "code on a"}],
                cards=[{"at": t(120), "until": t(160), "key": "batch/12"}])
    assert got["age"] == 180 and got["shares"] == shares(team=120, user=40, nobody=20)
    assert got["now"] == {"holder": "nobody", "what": None, "since": t(160)}


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


MERGE = {"start": t(0), "end": t(25), "merge": True, "what": "merge on a", "work": "unit/a"}


def test_a_decided_merge_with_its_checks_start():
    """#41, landed, was submitted at 14:00, its checks began at 14:05 as the follower saw while it stood, and it was
    decided at 14:17: 14:00 to 14:05 the team's, 14:05 to 14:17 the kit's, and no minute of it team-or-kit."""
    got = split(30, stages=[dict(MERGE, end=t(20))],
                submissions=[{"submitted": t(0), "started": t(5), "decided": t(17), "state": "landed", "what": "#41", "worktree": "unit/a"}])
    assert got["shares"] == shares(team=8, kit=12, nobody=10)


def test_a_decided_merge_whose_checks_start_is_not_kept_is_team_or_kit_though_its_merge_stage_ran():
    """#41, landed, submitted at 14:00 and decided at 14:17, its checks' start kept nowhere: 14:00 to 14:17 are
    team-or-kit, though a's merge stage ran throughout, and none of them the team's or the kit's."""
    got = split(30, stages=[MERGE], submissions=[{"submitted": t(3), "started": None, "decided": t(20), "state": "landed", "what": "#41",
                                                  "worktree": "unit/a"}])
    assert got["shares"] == shares(team=8, team_or_kit=17, nobody=5)


def test_a_merge_that_ended_before_the_follower_saw_it_is_team_or_kit_for_its_whole_run():
    """The follower started after a's merge stage of 13:50 to 14:20 and its submission were over: 13:50 to 14:20 are
    team-or-kit; a decision alone, the merge's own seen in the recent events, places no minute."""
    alone = {"submitted": None, "started": None, "decided": t(28), "state": None, "what": "#41", "worktree": "unit/a"}
    got = split(40, stages=[dict(MERGE, end=t(30))], submissions=[alone])
    assert got["shares"] == shares(team_or_kit=30, nobody=10)
    other = {"submitted": t(10), "started": t(12), "decided": t(15), "state": "landed", "what": "#40", "worktree": "unit/c"}
    assert split(40, stages=[dict(MERGE, end=t(30))], submissions=[other])["shares"] == shares(team_or_kit=27, kit=3, nobody=10), \
        "another unit's submission was taken for the merge's own"


def test_a_merge_stage_running_with_no_submission_held_is_the_teams():
    got = split(12, stages=[dict(MERGE, end=None)])
    assert got["shares"] == shares(team=12) and got["now"] == {"holder": "team", "what": "merge on a", "since": t(0)}


def test_a_standing_submission_testing_with_no_start_of_checks_is_team_or_kit_from_its_submit():
    got = split(20, submissions=[{"submitted": t(5), "started": None, "decided": None, "state": "testing", "what": "#9"}])
    assert got["shares"] == shares(nobody=5, team_or_kit=15) and got["now"] == {"holder": "team_or_kit", "what": "#9", "since": t(5)}


def test_minutes_that_cant_be_split_are_said_as_team_or_kit_with_why_once():
    """crew-board "Minutes that can't be split": twelve minutes of b's age were a decided merge's stay in sluice whose
    checks' start crew does not hold."""
    now = t(30)
    got = split(30, stages=[{"start": t(0), "end": t(10), "merge": False, "what": "code on a"}],
                submissions=[{"submitted": t(12), "started": None, "decided": t(24), "state": "landed", "what": "#41", "worktree": "unit/a"},
                             {"submitted": t(25), "started": None, "decided": None, "state": "testing", "what": "#42", "worktree": "unit/c"}])
    assert got["shares"] == shares(team=10, team_or_kit=17, nobody=3)
    since = f"{t(25).astimezone():%H:%M}"
    assert plan.time_said(got, now) == f"30m: team 10m, team or kit 17m, nobody 3m; team or kit since {since}, #42; team or kit: sluice keeps no start of its checks"
    assert plan.time_said(split(30, stages=[{"start": t(0), "end": t(10), "merge": False, "what": "code on a"}]), now).count("team or kit") == 0


def test_a_card_counts_only_while_nothing_moves_and_a_hold_only_while_no_one_else_holds():
    got = split(60, stages=[{"start": t(0), "end": t(20), "merge": False}],
                cards=[{"at": t(10), "until": t(40), "key": "land/crew"}],
                holds=[{"at": t(30), "until": None, "what": "its host deneb is held by chuck"}])
    assert got["shares"] == shares(team=20, user=20, hold=20)
    assert got["now"] == {"holder": "hold", "what": "its host deneb is held by chuck", "since": t(40)}


# ------------------------------------------------------------------------------------------------------------- nobody

def test_nobody_however_long_is_said_as_nobody_and_never_stalled():
    """Nothing of b has run, stood in sluice, had a card open or been held for seven minutes, then two: nobody holds it
    since the stage ended, and no word of a stall is said (teams.23 retires with the-team-machinery-leaves)."""
    for end in (27, 22):
        got = split(end, stages=[{"start": t(0), "end": t(20), "merge": False}])
        assert got["shares"] == shares(team=20, nobody=end - 20)
        assert got["now"] == {"holder": "nobody", "what": None, "since": t(20)} and "stalled" not in got
        assert plan.time_said(got, t(end)).endswith(f"; nobody since {t(20).astimezone():%H:%M}")


# ------------------------------------------------------------------------------------------------------- the edges

def test_the_shares_sum_to_the_age():
    """Pieces that are not whole minutes still give whole minutes that add up."""
    sec = datetime.timedelta(seconds=1)
    got = plan.bolt_time(STARTED, t(10) + 50 * sec, [{"start": t(0) + 20 * sec, "end": t(3) + 40 * sec, "merge": False}],
                         [{"submitted": t(4), "started": None, "decided": t(6) + 30 * sec, "state": "landed"},
                          {"submitted": t(6) + 40 * sec, "started": t(6) + 50 * sec, "decided": t(7) + 10 * sec, "state": "landed"}],
                         [{"at": t(7) + 20 * sec, "until": None, "key": "land/b"}], [])
    assert got["age"] == 10 and sum(got["shares"].values()) == 10 and got["shares"]["team_or_kit"] == 2


def test_a_stage_with_no_end_runs_to_the_end():
    got = split(45, stages=[{"start": t(15), "end": None, "merge": False, "what": "verify on a"}])
    assert got["shares"] == shares(nobody=15, team=30) and got["now"]["what"] == "verify on a"


def test_a_card_closed_before_the_start_is_left_out_and_one_open_across_it_counts_from_the_start():
    got = split(30, cards=[{"at": t(-60), "until": t(-10), "key": "batch/3"}, {"at": t(-5), "until": t(10), "key": "batch/4"}])
    assert got["shares"] == shares(user=10, nobody=20)


def test_a_submission_standing_not_under_test_is_the_teams():
    got = split(20, submissions=[{"submitted": t(5), "started": None, "decided": None, "state": "passed", "what": "#9"}])
    assert got["shares"] == shares(nobody=5, team=15)


def test_a_bolt_started_this_minute_is_nobodys():
    got = split(0)
    assert got == {"age": 0, "shares": shares(), "now": {"holder": "nobody", "what": None, "since": STARTED}}


# ------------------------------------------------------------------------------------- each holder from what crew keeps


PLAN = plan.Plan(plan_text(bolts=[("b", "switchboard-kit", True), ("o", "switchboard-kit", True)],
                           units=[("a", "switchboard-kit", "b", []), ("c", "switchboard-kit", "b", [], "chore"),
                                  ("x", "switchboard-kit", "o", [])]))


def e(act, minutes, *on, **fields):
    """A run-record entry, minutes after START, as record.parse reads one."""
    return dict({"Act": act, "At": at(minutes), "On": list(on)}, **fields)


def given(minutes=0):
    """The bolt's start, minutes after START."""
    return e("bolt.start", minutes, "bolt/b")


def facts_of(entries, standing=(), decided=(), unread=None):
    return plan.bolt_facts(entries, PLAN, "b", "wldn", "chuck-herdr-alpha", "switchboard-kit", (list(standing), None),
                           (list(decided), None), unread)


def mins(m):
    return START + datetime.timedelta(minutes=m)


def test_the_start_is_the_newest_and_its_stages_pair_with_their_ends():
    """An older crew's give of b, a start of it refused, and its start."""
    entries = [e("bolt.give", -500, "bolt/b", "team/swb-1"), e("bolt.start", -100, "bolt/b", Refused="its host is held"), given(0),
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
        {"start": mins(5), "end": mins(30), "merge": False, "what": "code on a", "work": "unit/a"},
        {"start": mins(6), "end": None, "merge": False, "what": "code on chore c", "work": "chore/c"},
        {"start": mins(50), "end": mins(55), "merge": False, "what": "fix fix/b/take-main", "work": "fix/b/take-main"},
        {"start": mins(56), "end": None, "merge": True, "what": "merge of fix/b/take-main", "work": "fix/b/take-main"},
        {"start": mins(57), "end": mins(70), "merge": True, "what": "merge on a", "work": "unit/a"}]


def test_the_users_card():
    """Every unit of b has merged, nothing runs, and its kit's landings card has been open for an hour."""
    entries = [given(0), e("stage.start", 0, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("stage.end", 60, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("card.post", 30, "bolt/o", Card="req_1", Key="land/switchboard-kit", By="wldn-ops"),
               e("card.close", 30, Card="req_1", Key="land/switchboard-kit", State="closed"),
               e("card.post", 60, Card="req_2", Key="land/switchboard-kit", By="wldn-ops")]
    got = plan.time_at(facts_of(entries), mins(120))
    assert got["shares"]["user"] == 60 and got["shares"]["team_or_kit"] == 60, "a merge with no submit held was counted the team's"
    assert got["now"] == {"holder": "user", "what": "land/switchboard-kit", "since": mins(60)}


def test_a_question_a_main_level_role_asked_since_the_start_is_the_users():
    """a's place stopped short and the planner's question to the user is open, with nothing of b running: a question of
    the partition's planner, main-level ops or design agent since b's start is b's; one asked before it, one of another
    partition's planner and an old conductor's are not."""
    entries = [e("card.post", -20, Card="req_9", Key=None, By="wldn-planner"), given(0),
               e("card.post", 10, Card="req_3", Key=None, By="wldn-planner"),
               e("card.post", 12, Card="req_4", Key="ask/madswan", By="madswan-planner"),
               e("card.post", 13, Card="req_6", Key=None, By="swb-1-conductor"),
               e("card.post", 14, Card="req_5", Key=None, By="wldn-ops"),
               e("card.post", 15, Card="req_7", Key=None, By="wldn-design")]
    got = facts_of(entries)
    assert [c["key"] for c in got["cards"]] == [None, None, None]
    assert [c["at"] for c in got["cards"]] == [mins(10), mins(14), mins(15)]


def test_a_held_host():
    """Nothing of b runs and no card of it is open, while the host its work runs on was held at 14:02 and not let go."""
    entries = [given(0), e("host.hold", 10, "host/chuck-herdr-alpha", By="chuck"), e("host.go", 20, "host/chuck-herdr-alpha", By="chuck"),
               e("host.hold", 30, "host/mac-studio", By="chuck"), e("host.hold", 40, "host/chuck-herdr-alpha", By="chuck")]
    got = plan.time_at(facts_of(entries), mins(50))
    assert got["shares"]["hold"] == 20 and got["shares"]["nobody"] == 30
    assert got["now"] == {"holder": "hold", "what": "its host chuck-herdr-alpha is held by chuck", "since": mins(40)}


def test_a_batch_card_a_proposal_card_and_a_card_whose_post_names_the_work_are_the_bolts():
    entries = [given(0), e("review.batch", 1, Batch="12", Units="a:b@abc1234 x:o@def5678"),
               e("review.batch", 1, Batch="13", Units="x:o@def5678"),
               e("card.post", 2, "batch/12", Card="req_b12", Key="batch/12", By="wldn-planner"),
               e("card.post", 2, "batch/13", Card="req_b13", Key="batch/13", By="wldn-planner"),
               e("plan.propose", 3, "proposal/7", "unit/a", "bolt/b"), e("plan.propose", 4, "proposal/8", "unit/x"),
               e("plan.propose", 5, "proposal/9", "unit/x", "proposal/8"), e("plan.propose", 5, "proposal/10", "unit/y", "proposal/7"),
               e("card.post", 6, "proposal/7", Card="req_p7", Key="proposal/7", By="wldn-planner"),
               e("card.post", 6, "proposal/8", Card="req_p8", Key="proposal/8", By="wldn-planner"),
               e("card.post", 7, "unit/a", Card="req_r", Key="record/switchboard-kit/0012", By="wldn-design")]
    assert sorted(c["key"] for c in facts_of(entries)["cards"]) == ["batch/12", "proposal/7", "record/switchboard-kit/0012"]


def test_a_card_lost_to_its_owner_and_posted_again_counts_as_one_open_card():
    entries = [given(0), e("card.post", 10, Card="req_1", Key="land/b", By="wldn-ops"),
               e("card.close", 20, Card="req_1", Key="land/b", State="lost"),
               e("card.post", 25, Card="req_2", Key="land/b", By="wldn-ops"),
               e("card.close", 40, Card="req_2", Key="land/b", State="closed")]
    assert [(c["at"], c["until"]) for c in facts_of(entries)["cards"]] == [(mins(10), mins(40))]


def test_the_kits_landings_card_counts_from_the_bolts_last_merge():
    entries = [given(0), e("card.post", 5, Card="req_1", Key="land/switchboard-kit", By="wldn-ops"),
               e("stage.start", 10, "stage/a/merge", "unit/a", "agent/swb-1-unit-1"),
               e("stage.end", 30, "stage/a/merge", "unit/a", "agent/swb-1-unit-1")]
    assert [c["at"] for c in facts_of(entries)["cards"]] == [mins(30)]
    assert facts_of(entries[:2])["cards"] == []


def test_the_bolts_submissions_standing_over_the_decided_and_none_of_another_bolts():
    """What the follower kept decided and what stands in the overview's queue, of b's work and its landing alone."""
    def kept(n, branch, worktree, submitted, decided, pull_head=None, started=None, event="landed"):
        return {"id": n, "bolt": "b", "branch": branch, "worktree": worktree, "pull_head": pull_head, "submitted": submitted,
                "started": started, "decided": decided, "event": event}
    decided = [kept(41, "bolt/b", "unit/a", at(5), at(20), started=at(8)), kept(43, "bolt/o", "unit/x", at(5), at(9)),
               kept(44, "main", "pull/9", at(30), at(31), pull_head="bolt/b", event="gone"), kept(45, "bolt/b", "unit/stray", at(5), at(6)),
               kept(47, "bolt/b", "chore/c", None, at(4), event="blamed")]
    standing = [{"id": 42, "branch": "bolt/b", "state": "testing", "submitted": at(21), "started": at(25), "worktree": "chore/c", "pull_head": None},
                {"id": 46, "branch": "main", "state": "queued", "submitted": at(40), "started": None, "worktree": "bolt/b", "pull_head": None}]
    got = facts_of([given(0)], standing, decided)["submissions"]
    assert got == [{"submitted": mins(5), "started": mins(8), "decided": mins(20), "state": "landed", "what": "#41", "worktree": "unit/a"},
                   {"submitted": mins(30), "started": None, "decided": mins(31), "state": "gone", "what": "#44", "worktree": "pull/9"},
                   {"submitted": mins(21), "started": mins(25), "decided": None, "state": "testing", "what": "#42", "worktree": "chore/c"},
                   {"submitted": mins(40), "started": None, "decided": None, "state": "queued", "what": "#46", "worktree": "bolt/b"}]


def test_a_flume_places_submissions_are_the_bolts():
    """A started bolt's work submits from its Flume place's branch, change/<u>, chore/<c> or fix/<bolt>--<f>."""
    standing = [{"id": n, "branch": "bolt/b", "state": "queued", "submitted": at(n), "started": None, "worktree": w, "pull_head": None}
                for n, w in ((61, "change/a"), (62, "chore/c"), (63, "fix/b--gap"), (64, "change/x"), (65, "fix/o--gap"))]
    assert [x["what"] for x in facts_of([given(0)], standing)["submissions"]] == ["#61", "#62", "#63"]


def test_a_landing_by_pull_request_is_the_bolts_by_the_number_its_queued_submit_names():
    """crew-board "A landing by pull request": main's recent events name #52, from pull/9, landed, and the run record's
    queued bolt.submit of b names #52."""
    decided = [{"id": 52, "bolt": None, "branch": "main", "worktree": "pull/9", "pull_head": None, "submitted": at(30), "started": None,
                "decided": at(45), "event": "landed"},
               {"id": 53, "bolt": None, "branch": "main", "worktree": "pull/10", "pull_head": None, "submitted": at(31), "started": None,
                "decided": at(46), "event": "landed"}]
    submit = e("bolt.submit", 30, "bolt/b", Outcome="queued", Submission="52")
    other = e("bolt.submit", 31, "bolt/o", Outcome="queued", Submission="53")
    assert [x["what"] for x in facts_of([given(0), submit, other], decided=decided)["submissions"]] == ["#52"]
    assert facts_of([given(0)], decided=decided)["submissions"] == [], "a landing by pull request was taken with no submit naming it"


def test_an_older_crews_give_is_the_start_where_the_record_holds_no_start():
    assert facts_of([e("bolt.give", 0, "bolt/b", "team/swb-1")])["start"] == mins(0)


def test_a_start_that_cant_be_read_is_said_and_shows_no_share():
    """The run record holds no start of b, nor an older crew's give of it, in the days the board reads."""
    got = plan.time_at(facts_of([e("bolt.start", 0, "bolt/o"), e("bolt.give", 0, "bolt/o", "team/swb-2")]), mins(10))
    assert got == {"unknown": "its age can't be told: the run record of the last 60 days holds no start of it"}


def test_a_record_that_cant_be_read_is_said():
    got = facts_of([given(0)], unread={"wldn/main of WilldanGroup/crew-state": "fetch failed"})
    assert got == {"unknown": "its age can't be told: wldn/main of WilldanGroup/crew-state could not be read (fetch failed)"}


def test_submissions_that_cant_be_read_keep_the_age_and_tell_no_share():
    got = plan.bolt_facts([given(0)], PLAN, "b", "wldn", "chuck-herdr-alpha", "switchboard-kit", ([], None),
                          (None, "its overview watch ended (sluice overview --watch exited 1)"))
    assert plan.time_at(got, mins(65)) == {
        "unknown": "who held its time can't be told: its submissions can't be read: its overview watch ended (sluice overview --watch exited 1)",
        "age": 65}


def test_a_decided_submission_with_no_time_it_was_decided_is_said():
    decided = [{"id": 41, "branch": "bolt/b", "event": "landed", "submitted": at(5), "decided": None, "worktree": "unit/a", "pull_head": None}]
    assert facts_of([given(0)], decided=decided)["unknown"] == "who held its time can't be told: sluice's record of #41 gives no time it was decided"

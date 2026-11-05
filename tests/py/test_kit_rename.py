"""A kit renamed on its host is renamed across the plan in one act (Decision 2 of
a-kit-renamed-on-its-host-is-renamed-across-the-plan; bolt-plan "A kit renamed on its host is renamed across the plan
in one act"): crew kit rename <old> <new> sets the Repo of every Bolt and Unit record naming the old name to the new,
and nothing else, refused with nothing written unless the partition's main-level host's spaces keep the new name and
not the old (plan.op_kit_rename, plan.rename_refusal). And a plan command given a kit's former name writes its name now
and says so (Decision 4; plan.kit_given), a proposal approved after the rename among them. The rename's one commit and
its entry under a real recfix are the contract tier's (tests/contract/test_recfix.py). And madswan's started bolt
you-sign-in-to-staging, renamed, lands under its kit's name now in the folder the runner reports keeping it in (Decision
7; runner.where)."""
import argparse
import json

import pytest

import plan
import runner

from facts import FLUME, STANDING, FactsWrite, apply, crew_read, keeping, known, plan_text

# madswan's plan as afterthought/crew-state held it on 2026-11-05 (design's Context): 21 records in tailrace, three bolts
# and eighteen units, one of them queued; the started bolt you-sign-in-to-staging and its merged unit in flywheel-cloud;
# and crew's own.
TAILRACE = [f"trc-{n}" for n in (1, 2, 3)]
STAGING, SEAM = "you-sign-in-to-staging", "one-seam-turns-every-credential-into-a-principal"
UNITS = [(f"tailrace-work-{b}-{n}", "tailrace", b, []) for b in TAILRACE for n in range(1, 7)][:17] + [("trc-queued", "tailrace", None, [])]


def madswan(extra_units=()):
    return plan_text(bolts=[(b, "tailrace", False) for b in TAILRACE] + [(STAGING, "flywheel-cloud", True), ("crew-bolt", "crew", False)],
                     units=UNITS + [(SEAM, "flywheel-cloud", STAGING, []), ("crew-unit", "crew", "crew-bolt", [])] + list(extra_units))


def fleet(*repos):
    """madswan's fleet, its main level on deneb, whose spaces keep repos (owner/name)."""
    return {"partitions": {"madswan": {"label": "madswan", "machine": "deneb", "flume": STANDING}},
            "hosts": {"deneb": keeping("/d/agentplot", *repos)}}


# deneb's spaces after the user's rename of 2026-11-05: the new names, and neither old one.
RENAMED = fleet("agentplot/boomdrive", "agentplot/boomdrive-cloud", "agentplot/boomdrive-web", "agentplot/flywheel",
                "agentplot/flywheel-next", "agentplot/timber", "afterthought/crew")

# Request 1, the launch of one-seam in flywheel-cloud, as madswan's requests.rec holds it.
REQUESTS = runner.REQUESTS + "\n" + "\n".join(plan.Rec("Request", runner.request_fields(1, "launch", f"unit/{SEAM}", dict(
    Repo="flywheel-cloud", Kind="change", Name=SEAM, Base=f"bolt/{STAGING}", Priority=1, Intent=f"madswan/{STAGING}",
    Recipient="madswan/planner", Brief=f"Build {SEAM}."), "2026-11-04T23:00:00Z", "chuck@deneb")).lines()) + "\n"


def landed(repo, n=1):
    """A bolt.land entry under repo, as record.parse gives it."""
    return {"Id": f"20261030T100000Z-{n}-deneb-1-1", "At": f"2026-10-30T10:00:0{n}Z", "Act": "bolt.land", "On": [f"bolt/old-{n}"],
            "From": [], "Commit": [], "Repo": repo, "Head": "a" * 40}


def renamed(old, new):
    """The kit.rename entry crew kit rename <old> <new> left, as record.parse gives it."""
    return {"Id": "20261105T120000Z-1-deneb-1-1", "At": "2026-11-05T12:00:00Z", "Act": "kit.rename", "On": [f"kit/{new}"],
            "From": [f"kit/{old}"], "Commit": [], "Repo": new, "Count": "21"}


def written(text=None, entries=()):
    return FactsWrite(text or madswan(), files={"requests.rec": REQUESTS}, label="madswan", entries=entries)


def rename(w, old, new, f=RENAMED):
    """crew kit rename <old> <new> as a proposal holds it, built and applied to the write: the op, its entry's fields
    filled at the tip it was applied to."""
    a = plan.do_args("madswan", f"kit rename {old} {new}")
    op = plan.OPS[("kit", "rename")](known(w, fleet=f, n=1), a)
    op.change(w)
    plan.check(w.plan)
    return op


def fields(p):
    """Every record of the plan, field by field, by its kind and name."""
    return {(r.kind, r.name()): list(r.fields) for r in p.bolts() + p.work()}


class TestTheRename:
    def test_every_tailrace_record_names_timber_and_nothing_else_changed(self):
        w = written()
        before = fields(w.plan)
        op = rename(w, "tailrace", "timber")
        after = fields(w.plan)
        for k, was in before.items():
            assert after[k] == ([(f, "timber" if f == "Repo" and v == "tailrace" else v) for f, v in was]), k
        assert sum(1 for r in w.plan.bolts() + w.plan.work() if r.get("Repo") == "timber") == 21
        assert [r.name() for r in w.plan.bolts() + w.plan.work() if r.get("Repo") == "flywheel-cloud"] == [STAGING, SEAM]
        assert [k for k in after] == [k for k in before]
        assert (op.act, op.subject, op.on, op.frm, op.fields) == (
            "kit.rename", "plan(kit): rename tailrace timber", ["kit/timber"], ["kit/tailrace"], {"Repo": "timber", "Count": "21"})

    def test_a_record_naming_its_forge_address_is_renamed(self):
        w = written(madswan([("trc-by-address", "agentplot/tailrace", None, [])]))
        op = rename(w, "tailrace", "timber")
        assert w.plan.unit("trc-by-address").get("Repo") == "timber" and op.fields["Count"] == "22"

    def test_a_kit_only_the_landings_name_renames_no_record_and_still_writes_its_entry(self):
        w = written(plan_text(bolts=[("crew-bolt", "crew", False)]), entries=[landed("tailrace")])
        text = w.plan.text()
        op = rename(w, "tailrace", "timber")
        assert w.plan.text() == text and op.fields == {"Repo": "timber", "Count": "0"}
        assert w.renames()[-1] == ("tailrace", "timber") and w.kits() == ["crew", "timber"]

    def test_the_new_name_is_written_as_given(self):
        w = written()
        rename(w, "flywheel-cloud", "agentplot/boomdrive-cloud")
        assert w.plan.bolt(STAGING).get("Repo") == w.plan.unit(SEAM).get("Repo") == "agentplot/boomdrive-cloud"


class TestRefused:
    """Each refusal leaves the plan as it was and names what it should."""

    @pytest.mark.parametrize("old, new, f, said", [
        ("rocs-kit", "timber", RENAMED, "madswan's plan names no kit rocs-kit: neither its plan nor its landings name it"),
        ("tailrace", "timber", fleet("agentplot/tailrace", "agentplot/timber"),
         "deneb's spaces still keep agentplot/tailrace, so it is not renamed there"),
        ("tailrace", "timber", fleet("agentplot/boomdrive-cloud", "afterthought/crew"),
         "deneb's spaces keep no timber, so it is not renamed there: they keep agentplot/boomdrive-cloud, afterthought/crew"),
        ("tailrace", "crew-bolt", fleet("agentplot/crew-bolt"),
         "crew-bolt is the name of bolt crew-bolt of madswan, so land/crew-bolt would name the bolt and not the kit"),
        ("tailrace", "agentplot/tailrace", RENAMED, "tailrace and agentplot/tailrace name one kit: a rename gives it another name"),
        ("tailrace", "timber", {"partitions": RENAMED["partitions"], "hosts": {}}, "lists no deneb, madswan's main level's host, "
                                                                                   "so crew can't read whether its spaces keep timber"),
        ("tailrace", "timber", fleet("agentplot/timber", "afterthought/timber"),
         "deneb's spaces keep agentplot/timber and afterthought/timber by the name timber, so crew can't tell which is meant")])
    def test_a_refusal_writes_nothing(self, old, new, f, said):
        w = written()
        text = w.plan.text()
        with pytest.raises(plan.Refusal, match=said):
            rename(w, old, new, f)
        assert w.plan.text() == text and w.renamed == []

    def test_a_name_a_rename_already_renamed_is_renamed_by_its_name_now(self):
        w = written(entries=[renamed("tailrace", "timber")])
        with pytest.raises(plan.Refusal, match="^tailrace is timber since its rename: crew kit rename timber trc renames it again$"):
            rename(w, "tailrace", "trc")


class TestTheStartedBolt:
    def test_its_kit_renamed_leaves_its_path_its_units_and_its_requests_as_they_were(self):
        """bolt-plan, A started bolt's kit: you-sign-in-to-staging keeps Path: flume and one-seam, and no request is
        appended."""
        w = written()
        unit = list(w.plan.unit(SEAM).fields)
        op = rename(w, "flywheel-cloud", "boomdrive-cloud")
        assert (w.plan.bolt(STAGING).get("Path"), w.plan.bolt(STAGING).get("Repo")) == ("flume", "boomdrive-cloud")
        assert [u.name() for u in w.plan.work_of(STAGING)] == [SEAM]
        assert w.plan.unit(SEAM).fields == [(f, "boomdrive-cloud" if f == "Repo" else v) for f, v in unit]
        assert w.files == {"requests.rec": REQUESTS} and op.fields["Count"] == "2"


class TestAFormerName:
    """Decision 4: a plan command given a kit's former name writes its name now and says so."""

    def test_a_new_bolt_under_a_former_name_is_written_under_the_name_now(self, capsys):
        w = written(entries=[renamed("tailrace", "timber")])
        a = plan.do_args("madswan", 'bolt new y "Y is built." --repo tailrace')
        op = plan.OPS[("bolt", "new")](known(w, fleet=RENAMED, n=1), a)
        op.change(w)
        op.after("afterthought/crew-state", "0" * 40)
        assert w.plan.bolt("y").get("Repo") == "timber"
        assert capsys.readouterr().out == "tailrace is timber since its rename; written as timber\n"

    def test_a_proposal_approved_after_the_rename_queues_its_unit_under_the_name_now_its_do_unchanged(self, capsys):
        """bolt-plan, A proposal approved after the rename: proposal 400's unit add x --repo tailrace, approved once
        tailrace is timber, queues x in timber and says so, its Do still reading --repo tailrace (plan.4)."""
        do = 'unit add x "X is built." --repo tailrace'
        w = written(entries=[renamed("tailrace", "timber")])
        a = plan.do_args("madswan", do)
        op = plan.OPS[("unit", "add")](known(w, fleet=RENAMED, n=400), a)
        op.change(w)
        op.after("afterthought/crew-state", "0" * 40)
        assert (w.plan.unit("x").get("Repo"), w.plan.unit("x").get("Bolt")) == ("timber", None) and a.do == do
        assert capsys.readouterr().out == "tailrace is timber since its rename; written as timber\n"

    def test_a_chore_into_a_renamed_kits_bolt_given_its_former_name_goes_in(self):
        was = written()
        rename(was, "tailrace", "timber")
        w = written(was.plan.text(), entries=[renamed("tailrace", "timber")])
        apply(w, 'chore add bump "Bump it." --bolt trc-1 --repo tailrace', ctx=known(w, fleet=RENAMED, n=1))
        assert (w.plan.item("bump").get("Repo"), w.plan.item("bump").get("Kind")) == ("timber", "chore")

    def test_a_command_after_a_rename_in_one_proposal_writes_the_name_now(self):
        w = written()
        rename(w, "tailrace", "timber")
        apply(w, 'unit add x "X is built." --repo tailrace', ctx=known(w, fleet=RENAMED, n=1))
        assert w.plan.unit("x").get("Repo") == "timber"

    def test_a_former_name_kept_again_is_refused_naming_the_rename(self):
        w = written(entries=[renamed("tailrace", "timber")])
        text = w.plan.text()
        again = fleet("agentplot/timber", "agentplot/tailrace")
        with pytest.raises(plan.Refusal, match="^tailrace is timber since its rename, and deneb's spaces keep agentplot/tailrace again: "
                                               "crew can't tell its records from timber's, so that repository needs another name in crew$"):
            apply(w, 'bolt new y "Y is built." --repo tailrace', ctx=known(w, fleet=again, n=1))
        assert w.plan.text() == text

    def test_a_name_no_rename_renamed_is_written_as_given_and_says_nothing(self, capsys):
        w = written(entries=[renamed("tailrace", "timber")])
        op = plan.OPS[("bolt", "new")](known(w, fleet=RENAMED, n=1), argparse.Namespace(
            bolt="y", goal="Y.", repo="crew", source=[], before=None))
        op.change(w)
        op.after("afterthought/crew-state", "0" * 40)
        assert w.plan.bolt("y").get("Repo") == "crew" and capsys.readouterr().out == ""


# Where deneb's runner keeps flywheel-cloud's clone, which Flume's status of one-seam's place still names, and the
# folder the clone was renamed to (design's Context; runbook 3.5, step 3).
OLD = "/Users/chuck/.local/share/flywheel/repositories/agentplot/flywheel-cloud"
NEW = "/Users/chuck/.local/share/flywheel/repositories/agentplot/boomdrive-cloud"
PLACE = f"/Users/chuck/.local/share/flume/places/5d2c7e914b0a/change--{SEAM}"
COMMIT = "84393d4" + "0" * 33  # one-seam's landing on bolt/you-sign-in-to-staging, its first seven as read


def deneb(kept=(("agentplot/boomdrive-cloud", NEW), ("agentplot/timber", "/Users/chuck/.local/share/flywheel/repositories/agentplot/timber"))):
    """deneb's runner of madswan as crew reads it (runner.host_read): request 1 answered launched, its place carried once
    Flume tidied it, landed at COMMIT, a flume 0.3.6 status (tests/py/flume-0.3.6/landed.json) naming the old clone's
    folder; and repositories.rec naming each repository it keeps (kept) by its forge address with its folder, as the
    runner reports them once it keeps the renamed clone (R2)."""
    status = json.loads((FLUME / "landed.json").read_text())
    p = status["status"]["places"][0]
    p.update(place=f"{PLACE}@1793474400", repository=OLD, name=SEAM, branch=f"change/{SEAM}", base=f"bolt/{STAGING}",
             stream={"name": "madswan", "from": "intent"})
    p["phase"]["tidied"]["over"]["landed"]["commit"] = COMMIT
    files = {"runner.rec": plan.Plan(runner.RUNNER + "\nHost: deneb\nVersion: 0.1.0\nSince: 2026-11-04T22:00:00Z\n"),
             "answers.rec": plan.Plan(runner.ANSWERS + f"\nRequest: 1\nOutcome: launched\nPlace: {PLACE}\nAt: 2026-11-04T23:01:00Z\n"),
             "places.rec": plan.Plan(runner.PLACES + f"\nRequest: 1\nPlace: {PLACE}\nAt: 2026-11-05T00:23:12Z\nStatus: {json.dumps(status)}\n"),
             "repositories.rec": plan.Plan(runner.REPOSITORIES + "".join(f"\nRepository: {a}\nFolder: {f}\n" for a, f in kept))}
    return {"deneb": runner.host_read("madswan", "deneb", "4a3524e5" + "0" * 32, files, {})}


class TestTheStartedBoltLands:
    """Decision 7: once madswan's plan renames flywheel-cloud boomdrive-cloud and deneb's runner reports the renamed clone,
    you-sign-in-to-staging is read and landed there under its kit's name now, with nothing launched again."""

    @pytest.fixture(autouse=True)
    def here(self, monkeypatch):
        monkeypatch.setattr(plan.crew, "this_host", lambda: "deneb")

    def rows(self, w, run):
        """The rail's land rows (plan.rail_rows) of madswan's plan as the write leaves it, the bolt's head green, read by
        deneb in the renamed clone's folder: a survey of any other folder does not hold the kit."""
        k = crew_read(bolts={STAGING: {"verdict": "passed (4 run)", "head_at": "2026-11-05T00:30:00Z"}})["deneb"]["kits"]["/crew/main"]
        sv = {"deneb": {"ok": True, "kits": {NEW: k}}}
        return [r for r in plan.rail_rows(RENAMED, [("madswan", "afterthought/crew-state", "tip", w.plan)], sv, [], {}, None,
                                          {"madswan": run}) if r["group"] == "land"]

    def test_one_seam_reads_merged_and_the_bolt_lands_in_the_renamed_clone_on_land_boomdrive_cloud(self):
        """request 1, launched under flywheel-cloud, is read as boomdrive-cloud's (plan.launches_now), one-seam reads
        merged at 84393d4 from deneb's place, the bolt is read and landed in the folder deneb's runner reports for
        agentplot/boomdrive-cloud over the place's stale one, and it is a row of land/boomdrive-cloud; requests.rec is
        as it was."""
        w = written()
        rename(w, "flywheel-cloud", "boomdrive-cloud")
        assert w.files == {"requests.rec": REQUESTS}
        requests = plan.launches_now(plan.Plan(REQUESTS).recs("Request"), w.renames())
        run = (requests, deneb())
        s = runner.piece_stage(requests, run[1], runner.launch_of(requests, f"unit/{SEAM}"))
        assert (s["stage"], s["commit"]) == ("merged", COMMIT)
        at = plan.bolt_at(RENAMED, "madswan", w.plan.bolt(STAGING), run)
        assert (at["machine"], at["stream"], at["kit"]) == ("deneb", "madswan", {"name": "boomdrive-cloud", "repo": "boomdrive-cloud",
                                                                                 "main": NEW, "dir": NEW})
        rows = self.rows(w, run)
        assert [(r["key"], r["bolts"]) for r in rows] == [("land/boomdrive-cloud", [{"bolt": STAGING, "host": "deneb", "can": True}])]
        assert rows[0]["what"][1] == f"{STAGING}, on deneb, in Flume stream madswan: can land"

    def test_before_the_rename_the_bolt_is_refused_naming_it_and_nothing_lands(self):
        """Decision 7's last step: with the plan still naming flywheel-cloud, deneb's runner reports no repository by it, so
        the bolt is refused naming deneb, what it keeps and crew kit rename, and no row offers it to land."""
        w = written()
        run = (plan.Plan(REQUESTS).recs("Request"), deneb())
        with pytest.raises(plan.Refusal, match=f"^the runner on deneb took bolt {STAGING}'s work and keeps no flywheel-cloud: it keeps "
                                               "agentplot/boomdrive-cloud, agentplot/timber, so crew can't tell where flywheel-cloud is "
                                               "there; if flywheel-cloud was renamed on its host, crew kit rename flywheel-cloud <new>"):
            plan.bolt_at(RENAMED, "madswan", w.plan.bolt(STAGING), run)
        assert self.rows(w, run) == []

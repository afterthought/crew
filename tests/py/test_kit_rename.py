"""A kit renamed on its host is renamed across the plan in one act (Decision 2 of
a-kit-renamed-on-its-host-is-renamed-across-the-plan; bolt-plan "A kit renamed on its host is renamed across the plan
in one act"): crew kit rename <old> <new> sets the Repo of every Bolt and Unit record naming the old name to the new,
and nothing else, refused with nothing written unless the partition's main-level host's spaces keep the new name and
not the old (plan.op_kit_rename, plan.rename_refusal). And a plan command given a kit's former name writes its name now
and says so (Decision 4; plan.kit_given), a proposal approved after the rename among them. The rename's one commit and
its entry under a real recfix are the contract tier's (tests/contract/test_recfix.py)."""
import argparse

import pytest

import plan
import runner

from facts import STANDING, FactsWrite, apply, keeping, known, plan_text

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

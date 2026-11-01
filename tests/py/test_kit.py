"""A kit's declaration of its toolchain and tests, and the steps that make a worktree ready from it (kit-toolchain
spec; plan.17; record 0023)."""
import base64
import pathlib

import pytest

import kit
from crew import Refusal

FULL = '[tests]\ntoolchain = ["devenv", "print-dev-env"]\nrunner = "moon"\n'
SCRIPT = "/kit.git/worktrees/a/crew/toolchain.sh"


class TestDeclared:
    def test_a_kit_that_declares_both(self):
        assert kit.declared(FULL) == {"toolchain": ["devenv", "print-dev-env"], "runner": "moon", "command": None}

    def test_a_kit_with_no_file_declares_nothing(self):
        assert kit.declared(None) is None

    def test_a_file_with_no_tests_table_declares_nothing(self):
        assert kit.declared('[branches."bolt/*"]\nrequired = ["#check-fast"]\n') == {"toolchain": None, "runner": None, "command": None}

    def test_a_command_runner_with_its_command(self):
        assert kit.declared('[tests]\nrunner = "command"\ncommand = "make check"\n')["command"] == "make check"

    @pytest.mark.parametrize("text, key", [
        ("[tests\n", "is not TOML"),
        ('[tests]\ntoolchain = "devenv print-dev-env"\n', "toolchain is a list of strings"),
        ("[tests]\ntoolchain = []\n", "toolchain is a list of strings"),
        ('[tests]\ntoolchain = ["devenv", 1]\n', "toolchain is a list of strings"),
        ('[tests]\nrunner = "cargo"\n', 'runner is "moon" or "command"'),
        ('[tests]\nrunner = "command"\n', "names no command"),
        ("[tests]\ncommand = 3\n", "command is a string"),
        ("tests = 1\n", "[tests] is a table"),
    ])
    def test_a_declaration_crew_cannot_read_is_refused_naming_the_file_and_key(self, text, key):
        with pytest.raises(Refusal) as e:
            kit.declared(text, "places/a/.config/sluice.toml")
        assert "places/a/.config/sluice.toml" in str(e.value) and key in str(e.value)


class TestReadying:
    def test_a_kit_on_moon_runs_its_toolchain_then_moon_inside_it(self):
        steps = kit.readying(kit.declared(FULL), SCRIPT)
        assert [what for what, _, _ in steps] == ["the toolchain", "moon --version", "moon setup"]
        assert steps[0] == ("the toolchain", ["devenv", "print-dev-env"], SCRIPT)
        assert steps[2] == ("moon setup", kit.in_toolchain(SCRIPT, ["moon", "setup"]), None)

    def test_a_command_runner_needs_no_setup(self):
        decl = kit.declared('[tests]\ntoolchain = ["sh", "print"]\nrunner = "command"\ncommand = "make check"\n')
        assert [what for what, _, _ in kit.readying(decl, SCRIPT)] == ["the toolchain"]

    def test_moon_with_no_toolchain_runs_on_the_hosts_path(self):
        steps = kit.readying(kit.declared('[tests]\nrunner = "moon"\n'), SCRIPT)
        assert steps == [("moon --version", ["moon", "--version"], None), ("moon setup", ["moon", "setup"], None)]

    def test_a_kit_that_declares_nothing_has_no_steps(self):
        assert kit.readying(None, SCRIPT) == []
        assert kit.readying(kit.declared("[tests]\n"), SCRIPT) == []


def test_a_command_inside_the_toolchain_is_sourced_by_the_bash_on_path():
    assert kit.in_toolchain(SCRIPT, ["moon", "setup"]) == ["bash", "-c", 'source "$0" >&2; exec "$@"', SCRIPT, "moon", "setup"]
    assert kit.in_toolchain(None, ["moon", "setup"]) == ["moon", "setup"]


@pytest.mark.parametrize("version, refused", [
    ("moon 2.6.1\n", None), ("moon 3.0.2", None), ("moon 2.5.3\n", None), ("moon 1.41.7", None),
    ("", "no version crew can read: nothing"),
    ("bash: moon: command not found\n", "no version crew can read: bash: moon: command not found"),
])
def test_any_moon_the_kit_runs_is_set_up_and_only_one_whose_version_cant_be_read_is_refused(version, refused):
    """plan.17: crew enforces no moon floor; readying refuses a moon only when it can't read its version (read.1).
    sluice's moon runner keeps its own floor, 2.6, at its run."""
    why = kit.moon_said(version)
    assert why is None if refused is None else refused in why


class TestPlaceSaid:
    def test_a_worktree_with_a_declaration(self):
        out = f"GITDIR=/kit.git/worktrees/a\nDECLARATION={base64.b64encode(FULL.encode()).decode()}\n"
        assert kit.place_said(out) == ("/kit.git/worktrees/a", FULL)

    def test_a_worktree_without_one(self):
        assert kit.place_said("GITDIR=/kit.git/worktrees/a\nDECLARATION=-\n") == ("/kit.git/worktrees/a", None)

    def test_output_that_is_not_places_is_refused(self):
        with pytest.raises(Refusal):
            kit.place_said("fatal: not a git repository\n")


def test_a_failed_step_names_the_place_the_step_and_its_last_lines():
    out = "\n".join(f"line {n}" for n in range(40))
    why = kit.step_failed("/kit/places/a", "moon setup", 1, out)
    assert why.startswith("/kit/places/a is made but not ready: moon setup exited 1")
    assert "line 39" in why and "line 24" not in why and why.endswith("Running the command again sets it up.")


class TestPreviewed:
    """Whether a kit's policy at the bolt's head declares a preview, as sluice reads it from the previewed revision
    (rail-cards, "A landing's card lists the addresses of a preview of its head")."""

    def test_a_policy_with_a_preview_table_declares_one(self):
        assert kit.previewed('[preview]\ncommand = ["devenv", "up"]\n\n[preview.addresses]\nweb = "http://{name.web}"\n')

    def test_a_policy_with_no_preview_table_declares_none(self):
        assert kit.previewed(FULL) is False

    def test_a_kit_with_no_policy_declares_none(self):
        assert kit.previewed(None) is False

    @pytest.mark.parametrize("text, said", [
        ("[preview\n", "is not TOML"),
        ('preview = "x"\n', "[preview] is a table, not str"),
    ])
    def test_a_policy_crew_cannot_read_is_refused_naming_the_file_at_the_head(self, text, said):
        with pytest.raises(Refusal) as e:
            kit.previewed(text, ".config/sluice.toml at abc1234")
        assert ".config/sluice.toml at abc1234" in str(e.value) and said in str(e.value)


POLICY = '[tests]\nrunner = "moon"\n\n[branches."bolt/*"]\nrequired = ["#check-full"]\n\n[branches.main]\nrequired = ["#check-full"]\n'


class TestBoltChecks:
    """A kit merges and lands only through sluice, so crew gives a bolt only in a kit whose policy names the checks its
    bolt branches must pass (teams.5, record 0026)."""

    def test_the_bolt_branches_required_checks(self):
        assert kit.bolt_checks(POLICY, "switchboard-kit") == ["#check-full"]

    def test_the_most_specific_pattern_wins(self):
        text = '[branches."*"]\nrequired = ["#check-fast"]\n[branches."bolt/*"]\nrequired = ["#check-full"]\n'
        assert kit.bolt_checks(text, "k") == ["#check-full"]

    @pytest.mark.parametrize("text, said", [
        (None, "has no .config/sluice.toml on main"),
        ("[tests]\nrunner = \"moon\"\n", "names no checks for its bolt branches"),
        ('[branches.main]\nrequired = ["#check-full"]\n', "names no checks for its bolt branches"),
        ('[branches."bolt/*"]\nrequired = []\n', "names no checks for its bolt branches"),
        ("[branches\n", "is not TOML"),
    ])
    def test_a_kit_whose_policy_gates_no_bolt_is_given_none_naming_the_file(self, text, said):
        with pytest.raises(Refusal) as e:
            kit.bolt_checks(text, "switchboard-kit")
        assert "switchboard-kit" in str(e.value) and said in str(e.value)

    def test_the_policy_is_read_by_ref_at_main_now_and_a_refusal_names_the_ref(self):
        """plan.18: the policy is the one at main now, GitHub's for a kit with an origin and the kit's own for one with
        none, as POLICY read both, and a kit given no bolt is told which ref lacks it."""
        b64 = base64.b64encode(POLICY.encode()).decode()
        assert kit.policy_said(mains("yes", at_github=b64), "switchboard-kit", "h") == (POLICY, "origin/main", GITHUB)
        assert kit.policy_said(mains("no", github="-", at_own=b64), "switchboard-kit", "h") == (POLICY, "main", OWN)
        assert kit.policy_said(mains("no", github="-"), "switchboard-kit", "h") == (None, "main", OWN)
        with pytest.raises(Refusal) as e:
            kit.bolt_checks(None, "switchboard-kit", "/k/main/.config/sluice.toml", ref="origin/main")
        assert "has no /k/main/.config/sluice.toml on origin/main" in str(e.value)

    @pytest.mark.parametrize("out", ["fatal: bad\n", "AT_OWN=-\n", f"ORIGIN=no\nGITHUB=-\nOWN={'b' * 40}\n"])
    def test_what_is_not_policys_words_is_refused(self, out):
        with pytest.raises(Refusal):
            kit.policy_said(out, "k", "h")


ON_GITHUB = POLICY.replace('required = ["#check-full"]\n', 'required = ["#check-full"]\nremote = "origin"\n')


class TestBoltRemote:
    """Where sluice keeps a branch, as the policy routes it (plan.19, sluice's core.15): the `remote` of the table that
    matches the branch, which a give needs for a bolt's branch, since crew gives bolts only on GitHub."""

    def test_the_bolt_branches_remote(self):
        assert kit.bolt_remote(ON_GITHUB, "bolt/b") == "origin"

    def test_the_most_specific_pattern_wins(self):
        text = '[branches."*"]\nremote = "origin"\n[branches."bolt/*"]\nrequired = ["#check-full"]\n'
        assert kit.bolt_remote(text, "bolt/b") is None
        assert kit.bolt_remote(text, "feature/x") == "origin"

    @pytest.mark.parametrize("text", [None, "", POLICY, '[branches."bolt/*"]\nremote = ""\n', '[branches."bolt/*"]\nremote = 1\n'])
    def test_no_remote_keeps_the_branch_in_the_hosts_own_refs(self, text):
        assert kit.bolt_remote(text, "bolt/b") is None

    def test_a_policy_crew_cannot_read_is_refused_naming_the_file(self):
        with pytest.raises(Refusal, match=r"^\.config/sluice\.toml at bolt/b is not TOML"):
            kit.bolt_remote("[branches\n", "bolt/b", ".config/sluice.toml at bolt/b")

    def test_a_give_takes_the_remote_the_policy_at_main_now_names(self):
        assert kit.give_remote(ON_GITHUB, "switchboard-kit", "/k/main/.config/sluice.toml", "bolt/b") == "origin"

    def test_a_give_in_a_kit_whose_bolts_have_no_remote_is_refused_naming_the_file_and_the_key(self):
        """bolt-plan "A kit whose bolts have no remote"."""
        with pytest.raises(Refusal) as e:
            kit.give_remote(POLICY, "switchboard-kit", "/k/main/.config/sluice.toml", "bolt/b", ref="origin/main")
        assert str(e.value) == (
            "switchboard-kit gives bolts only on GitHub, and its /k/main/.config/sluice.toml on origin/main names no remote "
            "for its bolt branches: its [branches.\"bolt/*\"] needs `remote = \"origin\"`, which is the kit's own change "
            "(plan.17), then give the bolt again")


def b64(text):
    return base64.b64encode(text.encode()).decode()


def at(local="-", tracked="-", at_local="-", at_tracked="-", main=None):
    """What BOLT_AT prints, and BOLT_HOME's AT_MAIN after it when given."""
    return (f"LOCAL={local}\nTRACKED={tracked}\nAT_LOCAL={at_local}\nAT_TRACKED={at_tracked}\n"
            + (f"AT_MAIN={main}\n" if main is not None else ""))


class TestWhereABoltLives:
    """Where a bolt's branch lives, read as sluice routes it (plan.19, design Decision 1): by the policy at the host's
    own branch, or at origin's tracking ref of it when the host has none."""
    SHA = "c" * 40

    def test_by_the_policy_at_the_hosts_own_branch(self):
        assert kit.bolt_lives(at(self.SHA, self.SHA, b64(ON_GITHUB), b64(POLICY)), "b") == "origin"
        assert kit.bolt_lives(at(self.SHA, self.SHA, b64(POLICY), b64(ON_GITHUB)), "b") is None
        assert kit.bolt_lives(at(self.SHA, at_local="-"), "b") is None

    def test_by_origins_when_the_host_has_none(self):
        assert kit.bolt_lives(at(tracked=self.SHA, at_tracked=b64(ON_GITHUB)), "b") == "origin"

    def test_a_place_is_cut_where_it_lives(self):
        assert kit.place_base(at(self.SHA, at_local=b64(ON_GITHUB)), "b") == "origin/bolt/b"
        assert kit.place_base(at(self.SHA, at_local=b64(POLICY)), "b") == "bolt/b"

    @pytest.mark.parametrize("said, why", [
        (at(), "crew can't tell where bolt/b lives: this host has neither bolt/b nor origin/bolt/b"),
        ("fatal: bad\n", "crew can't read where bolt/b lives from: fatal: bad"),
        (at("c" * 40, at_local="%%%"), "crew can't read bolt/b's .config/sluice.toml as it was sent"),
    ])
    def test_a_bolt_crew_cannot_place_is_refused(self, said, why):
        with pytest.raises(Refusal) as e:
            kit.bolt_lives(said, "b")
        assert str(e.value).startswith(why)

    def test_a_bolts_home_and_the_remote_main_names_for_bolts(self):
        assert kit.bolt_home(at(self.SHA, at_local=b64(POLICY), main=b64(ON_GITHUB)), "b") == (None, "origin")
        assert kit.bolt_home(at(self.SHA, at_local=b64(ON_GITHUB), main=b64(ON_GITHUB)), "b") == ("origin", "origin")
        assert kit.bolt_home(at(self.SHA, at_local=b64(POLICY), main="-"), "b") == (None, None)
        with pytest.raises(Refusal, match="crew can't read the policy at main"):
            kit.bolt_home(at(self.SHA, at_local=b64(POLICY)), "b")


def copies(own, there, at_there, held, ahead, lacks, beyond):
    """What LAND_COPIES prints once it has fetched the bolt from origin."""
    return (f"OWN={own}\nTHERE={there}\nAT_THERE={at_there}\nHELD={held}\nAHEAD={ahead}\nLACKS={lacks}\n"
            f"BEYOND={beyond}\n")


class TestALandingsCopies:
    """What a landing reads of a bolt's two copies after one fetch from origin (plan.19, design Decision 1): the
    host's own bolt/<bolt> and GitHub's, the policy at GitHub's, and which holds the other."""
    OWN, THERE = "1" * 40, "2" * 40

    def facts(self, **kw):
        return dict(dict(own=self.OWN, there=self.THERE, remote="origin", held="yes", ahead="no", lacks=0, beyond=2,
                         read=None), **kw)

    def test_a_kit_with_no_origin_or_an_origin_with_no_bolt_reads_no_copy_there(self):
        assert kit.land_copies("THERE=-\n", "b") == dict(own=None, there="-", remote=None, held=None, ahead=None,
                                                          lacks=None, beyond=None, read=None)

    def test_a_copy_git_could_not_read_is_read_with_gits_words(self):
        said = "READ=fatal: '/gone.git' does not appear to be a git repository fatal: Could not read from remote repository. \n"
        assert kit.land_copies(said, "b")["read"] == ("fatal: '/gone.git' does not appear to be a git repository fatal: "
                                                      "Could not read from remote repository.")
        assert kit.land_copies("READ=\n", "b")["read"] == "git said nothing"

    def test_a_host_copy_behind_githubs(self):
        said = copies(self.OWN, self.THERE, b64(ON_GITHUB), "yes", "no", 0, 2)
        assert kit.land_copies(said, "b") == self.facts()

    def test_a_host_copy_level_with_githubs(self):
        said = copies(self.THERE, self.THERE, b64(ON_GITHUB), "yes", "yes", 0, 0)
        assert kit.land_copies(said, "b") == self.facts(own=self.THERE, ahead="yes", beyond=0)

    def test_a_host_copy_ahead_of_githubs(self):
        said = copies(self.OWN, self.THERE, b64(ON_GITHUB), "no", "yes", 1, 0)
        assert kit.land_copies(said, "b") == self.facts(held="no", ahead="yes", lacks=1, beyond=0)

    def test_two_copies_that_have_diverged(self):
        said = copies(self.OWN, self.THERE, b64(ON_GITHUB), "no", "no", 1, 2)
        assert kit.land_copies(said, "b") == self.facts(held="no", lacks=1)

    def test_a_host_with_no_copy(self):
        said = copies("-", self.THERE, b64(ON_GITHUB), "yes", "-", "-", "-")
        assert kit.land_copies(said, "b") == self.facts(own="-", ahead=None, lacks=None, beyond=None)

    def test_a_copy_there_whose_policy_names_no_remote_or_holds_none(self):
        assert kit.land_copies(copies(self.OWN, self.THERE, b64(POLICY), "yes", "no", 0, 2), "b")["remote"] is None
        assert kit.land_copies(copies(self.OWN, self.THERE, "-", "yes", "no", 0, 2), "b")["remote"] is None

    def test_a_policy_there_that_is_not_toml_is_refused_naming_it(self):
        with pytest.raises(Refusal, match=r"^\.config/sluice\.toml at origin/bolt/b is not TOML"):
            kit.land_copies(copies(self.OWN, self.THERE, b64("[branches\n"), "yes", "no", 0, 2), "b")

    @pytest.mark.parametrize("said", [
        "",
        "fatal: bad\n",
        copies(OWN, "", b64(ON_GITHUB), "yes", "no", 0, 2),
        copies("", THERE, b64(ON_GITHUB), "yes", "no", 0, 2),
        copies(OWN, THERE, "", "yes", "no", 0, 2),
        copies(OWN, THERE, b64(ON_GITHUB), "maybe", "no", 0, 2),
        copies(OWN, THERE, b64(ON_GITHUB), "yes", "", 0, 2),
        copies(OWN, THERE, b64(ON_GITHUB), "yes", "no", "", 2),
        copies(OWN, THERE, b64(ON_GITHUB), "yes", "no", 0, "-"),
        copies("-", THERE, b64(ON_GITHUB), "no", "-", "-", "-"),
        copies("-", THERE, b64(ON_GITHUB), "yes", "no", 0, 2),
        f"OWN={OWN}\nTHERE={THERE}\nAT_THERE={b64(ON_GITHUB)}\nHELD=yes\n",
    ])
    def test_an_output_that_is_none_of_these_is_refused_naming_it(self, said):
        with pytest.raises(Refusal, match=r"^crew can't read bolt/b's copies for its landing from: "):
            kit.land_copies(said, "b")

    def test_a_policy_sent_badly_is_refused(self):
        with pytest.raises(Refusal, match=r"^crew can't read origin/bolt/b's \.config/sluice\.toml as it was sent"):
            kit.land_copies(copies(self.OWN, self.THERE, "%%%", "yes", "no", 0, 2), "b")


GITHUB, OWN = "a" * 40, "b" * 40


def mains(origin, fetched="ok", github=GITHUB, own=OWN, at_github="-", at_own="-"):
    """What MAINS, and POLICY after it, print."""
    return (f"ORIGIN={origin}\n" + (f"FETCHED={fetched}\n" if origin == "yes" else "")
            + f"GITHUB={github}\nOWN={own}\nAT_GITHUB={at_github}\nAT_OWN={at_own}\n")


class TestMainNow:
    """Which main is a kit's main now (plan.18): GitHub's, after the command's one fetch, for a kit with an origin
    remote, however far the host's own main lags it; its own main for a kit with none, which has no GitHub to lag."""

    def test_a_kit_with_an_origin_reads_githubs_main_however_far_its_own_lags(self):
        assert kit.main_now(mains("yes"), "switchboard-kit", "h") == ("origin/main", GITHUB, None)

    def test_a_kit_with_no_origin_reads_its_own_main(self):
        assert kit.main_now(mains("no", github="-"), "switchboard-kit", "h") == ("main", OWN, None)

    def test_every_kit_read_takes_the_same_ref_from_the_same_fact(self):
        """gather.now_ref, which gather.kit and the tidy read a kit's landed changes at, as this host last fetched it."""
        import gather
        assert (gather.now_ref(True), gather.now_ref(False)) == ("refs/remotes/origin/main", "refs/heads/main")

    @pytest.mark.parametrize("out, why", [
        (mains("yes", fetched="fatal: unable to access"), "cannot fetch switchboard-kit from GitHub on h, so cannot read its main now: fatal: unable to access"),
        (mains("yes", github="-"), "switchboard-kit's GitHub has no main, fetched on h"),
        (mains("no", github="-", own="-"), "switchboard-kit's main checkout on h has no branch main and no origin"),
        ("fatal: not a git repository\n", "crew can't read what switchboard-kit's main on h holds: fatal: not a git repository")])
    def test_a_fetch_that_failed_or_a_main_that_is_not_there_refuses_and_nothing_falls_back(self, out, why):
        assert kit.main_now(out, "switchboard-kit", "h") == (None, None, why)


class TestVerification:
    """A bolt's verification is sluice's verdict on its last landing, read from its head's trailer (tests.5)."""

    def test_a_head_sluice_landed_is_green(self):
        assert kit.verification("d5f8aa4" + "0" * 33, "passed (9 run, 0 replayed)") == (
            "green", "sluice's verdict on its last landing, d5f8aa4: passed (9 run, 0 replayed)")

    def test_a_head_that_is_no_landing_has_no_verdict(self):
        assert kit.verification("abc1234" + "0" * 33, "") == ("none", "its head abc1234 is no landing of sluice's, so it has no verdict")

    def test_nothing_else_reads_green(self):
        assert kit.verification(None, "passed (1 run, 0 replayed)")[0] == "unknown"
        assert kit.verification("abc1234", "failed (1 run, 0 replayed)")[0] == "unknown"


RECORDED = pathlib.Path(__file__).parent / "sluice-0.36.4"


def recorded(name):
    """A document sluice 0.36.4 printed, and the exit it printed it with, as its README lists them."""
    codes = dict(l.split("\t")[:2] for l in (RECORDED / "README").read_text().splitlines() if "\texit " in l)
    return (RECORDED / name).read_text(), int(codes[name].split()[1])


class TestSluiceVersion:
    """A give needs sluice's `branch create`, first in sluice 0.20.0 (plan.19, sluice ADR 0026)."""

    def test_the_version_sluice_prints(self):
        assert kit.sluice_version(recorded("version.txt")[0]) == (0, 36, 4)

    @pytest.mark.parametrize("out", ["sluice 0.36.4\n", "sluice 0.20.0", "sluice 1.0.0\n"])
    def test_a_sluice_with_branch_create_gives(self, out):
        assert kit.sluice_refusal(out, "chuck-herdr-alpha") is None

    @pytest.mark.parametrize("out, said", [
        ("sluice 0.19.9\n", "sluice 0.19.9"),
        ("sluice 0.3.1", "sluice 0.3.1"),
        ("bash: line 1: sluice: command not found\n", "bash: line 1: sluice: command not found"),
        ("", "nothing"),
        ("sluice version unknown", "sluice version unknown"),
    ])
    def test_an_older_sluice_or_one_crew_cannot_read_is_refused_naming_the_version_needed_and_the_hosts_words(self, out, said):
        """bolt-plan "A host whose sluice cannot make a branch" (read.1)."""
        assert kit.sluice_refusal(out, "chuck-herdr-alpha") == (
            "a bolt is given through sluice 0.20.0 or later, which has `branch create`, and sluice --version on "
            f"chuck-herdr-alpha said: {said}")


class TestBranchSaid:
    """What sluice's `branch create` and `branch delete` said with --json, read by facts recorded from sluice 0.36.4
    (read.2)."""

    def test_a_branch_made_is_its_commit(self):
        assert kit.branch_said(*recorded("create.json")) == ("c0da39bae0a5d89da0febc3f46f58607c2ad08a7", None)

    def test_a_branch_removed_is_the_commit_it_was_at(self):
        assert kit.branch_said(*recorded("delete.json")) == ("22eef8585855b2ef8feb0e08177e34d15f131182", None)

    @pytest.mark.parametrize("name, message", [
        ("create-present.json", "bolt/b is already there, at c0da39bae0a5d89da0febc3f46f58607c2ad08a7"),
        ("create-from-absent.json", "no branch nope"),
        ("delete-queued.json", "#1 still queued on bolt/b; wait for them to land, or withdraw them"),
        ("delete-not-landed.json", "bolt/b at 22eef8585855b2ef8feb0e08177e34d15f131182 has not landed into main; submit it there first"),
        ("delete-not-found.json", "no branch bolt/b"),
    ])
    def test_a_refusal_is_sluices_message(self, name, message):
        assert kit.branch_said(*recorded(name)) == (None, message)

    @pytest.mark.parametrize("out, code", [
        ("", 0), ("error: unexpected argument '--json' found\n", 2), ('{"branch": "bolt/b"}', 0),
        ('{"branch": "bolt/b", "created": "not-a-sha"}', 0), (recorded("create.json")[0], 2),
        ('{"error": {"kind": "refused", "message": ""}}', 2), (recorded("create-present.json")[0], 0),
    ])
    def test_anything_else_is_refused_naming_what_sluice_said(self, out, code):
        with pytest.raises(Refusal, match=f"crew can't read what sluice's branch command said \\(exit {code}\\)"):
            kit.branch_said(out, code)


CREWS = (pathlib.Path(__file__).parents[2] / ".config" / "sluice.toml").read_text()


class TestTakesPulls:
    """Whether a kit's main takes pull requests (bolt-teams "A kit that takes no pull requests is asked nothing of
    GitHub"): crew reads and marks a landing's pull request only where the policy at main has a pull_requests table."""

    def test_crews_own_policy_takes_pull_requests_into_main(self):
        assert kit.takes_pulls(CREWS) is True

    def test_a_policy_with_no_table_or_none_at_all_takes_none(self):
        assert kit.takes_pulls(POLICY) is False
        assert kit.takes_pulls(ON_GITHUB) is False
        assert kit.takes_pulls(None) is False

    def test_the_table_of_the_pattern_that_matches_main_is_read(self):
        assert kit.takes_pulls('[branches."*"]\nrequired = ["#check-full"]\n\n[branches."*".pull_requests]\nreviews = 0\n')
        assert not kit.takes_pulls('[branches."bolt/*"]\nrequired = ["#check-full"]\n\n[branches."bolt/*".pull_requests]\nreviews = 0\n')

    @pytest.mark.parametrize("text, said", [
        ("[branches\n", "is not TOML, so crew can't read whether its main takes pull requests"),
        ('[branches.main]\npull_requests = "yes"\n', "[branches.main.pull_requests] is a table, not str"),
    ])
    def test_a_policy_crew_cannot_read_is_refused_naming_the_file(self, text, said):
        with pytest.raises(Refusal) as e:
            kit.takes_pulls(text, ".config/sluice.toml on origin/main")
        assert ".config/sluice.toml on origin/main" in str(e.value) and said in str(e.value)


HEAD = "8079db303f0f815b256e10747aa8a3269f156cc1"


def listed(*pulls):
    """What `gh pr list --json number,isDraft,headRefOid,url` prints, as gh 2.102.0 printed it for afterthought/crew
    on 2026-10-22: a JSON list on one line, each pull request's keys in order."""
    import json
    return json.dumps([{"headRefOid": HEAD, "isDraft": d, "number": n, "url": f"https://github.com/o/k/pull/{n}"}
                       for n, d in pulls], separators=(",", ":")) + "\n"


class TestPullSaid:
    """What gh said of a bolt's open pull request into main (bolt-teams "A landing's pull request is a draft whenever
    the user's word does not stand"), refused where crew can't read it (read.1, read.2)."""

    def test_none_open(self):
        assert kit.pull_said(0, "[]\n", "", "o/k", "b") is None

    def test_one_draft_and_one_ready(self):
        assert kit.pull_said(0, listed((99, True)), "", "o/k", "b") == dict(
            number=99, draft=True, head=HEAD, url="https://github.com/o/k/pull/99")
        assert kit.pull_said(0, listed((100, False)), "", "o/k", "b")["draft"] is False

    def test_two_open_from_the_branch_are_refused_naming_both(self):
        with pytest.raises(Refusal) as e:
            kit.pull_said(0, listed((99, True), (100, False)), "", "o/k", "b")
        assert str(e.value) == ("crew can't tell o/k's open pull request from bolt/b into main: gh lists 2, "
                                "https://github.com/o/k/pull/99 and https://github.com/o/k/pull/100")

    @pytest.mark.parametrize("out", [
        "not json\n", "{}\n", "[1]\n",
        listed((99, True)).replace('"isDraft":true,', ""),
        listed((99, True)).replace('"number":99', '"number":"99"'),
        listed((99, True)).replace('"number":99', '"number":true'),
        listed((99, True)).replace(HEAD, "not-a-sha"),
    ])
    def test_what_is_not_a_list_of_pull_requests_is_refused(self, out):
        with pytest.raises(Refusal, match="crew can't read o/k's open pull request from bolt/b into main from what gh printed: "):
            kit.pull_said(0, out, "", "o/k", "b")

    def test_a_gh_that_failed_is_refused_in_its_words(self):
        with pytest.raises(Refusal) as e:
            kit.pull_said(1, "", "GraphQL: Could not resolve to a Repository with the name 'o/k'. (repository)\n", "o/k", "b")
        assert str(e.value) == ("crew can't read o/k's open pull request from bolt/b into main: gh exited 1: GraphQL: Could "
                                "not resolve to a Repository with the name 'o/k'. (repository)")
        with pytest.raises(Refusal, match="gh exited 127: bash: line 2: gh: command not found$"):
            kit.pull_said(127, "", "bash: line 2: gh: command not found\n", "o/k", "b")


class TestPullMarked:
    """What PULL_MARK said of `gh pr ready`: gh's exit and last line, or the host's words when it did not run there."""

    def test_gh_marked_it(self):
        out = f"RC=0\nSAID={b64('✓ Pull request o/k#99 is converted to \"draft\"')}\n"
        assert kit.pull_marked(0, out, "") == (0, '✓ Pull request o/k#99 is converted to "draft"')

    def test_gh_refused_it(self):
        assert kit.pull_marked(0, f"RC=1\nSAID={b64('HTTP 403: Resource not accessible by integration')}\n", "") == (
            1, "HTTP 403: Resource not accessible by integration")

    def test_a_host_that_did_not_answer_or_words_crew_cannot_read_are_no_mark(self):
        assert kit.pull_marked(255, "", "ssh: connect to host box port 22: timed out\n") == (
            255, "ssh: connect to host box port 22: timed out")
        assert kit.pull_marked(0, "RC=0\n", "")[0] != 0
        assert kit.pull_marked(0, "RC=0\nSAID=%%%\n", "")[0] != 0

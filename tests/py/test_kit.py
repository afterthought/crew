"""A kit's declaration of its toolchain and tests, and the steps that make a worktree ready from it (kit-toolchain
spec; plan.17; record 0023)."""
import base64

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
    ("moon 2.6.1\n", None), ("moon 2.6.0", None), ("moon 3.0.2", None),
    ("moon 2.5.3\n", "moon 2.5.3, below the moon runner's floor, 2.6"),
    ("moon 1.41.7", "below the moon runner's floor"),
    ("", "no version crew can read"),
])
def test_the_moon_runner_needs_moon_2_6(version, refused):
    why = kit.moon_floor(version)
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
        (None, "has no .config/sluice.toml on its main"),
        ("[tests]\nrunner = \"moon\"\n", "names no checks for its bolt branches"),
        ('[branches.main]\nrequired = ["#check-full"]\n', "names no checks for its bolt branches"),
        ('[branches."bolt/*"]\nrequired = []\n', "names no checks for its bolt branches"),
        ("[branches\n", "is not TOML"),
    ])
    def test_a_kit_whose_policy_gates_no_bolt_is_given_none_naming_the_file(self, text, said):
        with pytest.raises(Refusal) as e:
            kit.bolt_checks(text, "switchboard-kit")
        assert "switchboard-kit" in str(e.value) and said in str(e.value)

    def test_policy_said(self):
        assert kit.policy_said(f"POLICY={base64.b64encode(POLICY.encode()).decode()}\n") == POLICY
        assert kit.policy_said("POLICY=-\n") is None
        with pytest.raises(Refusal):
            kit.policy_said("fatal: bad\n")


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

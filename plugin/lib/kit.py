"""A kit's declaration of its toolchain and tests, and what crew's adapters run from it (record 0023, plan.17).

A kit says how its tools are set up and its checks run once, in sluice's words: the [tests] table of the policy file
DECLARATION, read from the worktree in hand. crew reads three keys of it and nothing else: `toolchain`, a command, as
a list, whose output is shell code that sets the kit's tools up (`["devenv", "print-dev-env"]`); `runner`, "moon" or
"command"; and `command`, what a command runner runs. crew assumes neither moon nor devenv: a kit that declares
nothing has nothing run. sluice stands on its own, and flywheel will use sluice's SDK for these same steps; the file
becomes flywheel.toml then, and DECLARATION is the one name that changes.

These are the decisions, each a function of plain facts (code.7); plan.py runs their steps on the team's host. The
steps are sluice's, in sluice's order (its check profile, crates/sluice/src/profiles/checks.rs): the toolchain run in
the worktree with a cleaned environment, its output kept outside the tree; then, for the moon runner, moon's version
and `moon setup`, each with that output sourced by the bash on PATH, since a toolchain may print bash 4 (devenv's
does) and macOS's /bin/bash is 3.2."""
import base64
import binascii
import re
import tomllib

import crew

DECLARATION = ".config/sluice.toml"
RUNNERS = ("moon", "command")
# What of the host's environment a step sees, with every LC_* variable: sluice's list (35). Nothing of a session's,
# another checkout's shell, git's, moon's or crew's own reaches a kit's toolchain.
KEEP = ("PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "TERM", "PROTO_HOME", "MOON_HOME")
# The oldest moon the moon runner sets up: sluice's moon profile's floor.
MOON_FLOOR = (2, 6)


def declared(text, where=DECLARATION):
    """A kit's declaration from the text of its DECLARATION, or None when there is no file: {"toolchain": [argv] or
    None, "runner": "moon" | "command" | None, "command": str or None}. A file with no [tests] declares nothing. Refused,
    naming the file and the key, when it is not TOML or a key is not what sluice's policy takes (read.1)."""
    if text is None:
        return None
    try:
        tests = tomllib.loads(text).get("tests", {})
    except tomllib.TOMLDecodeError as e:
        crew.fail(f"{where} is not TOML, so crew can't read what the kit declares of its toolchain and tests: {e}")
    if not isinstance(tests, dict):
        crew.fail(f"{where}: [tests] is a table, not {type(tests).__name__}")
    toolchain, runner, command = tests.get("toolchain"), tests.get("runner"), tests.get("command")
    if toolchain is not None and not (isinstance(toolchain, list) and toolchain and all(isinstance(a, str) and a for a in toolchain)):
        crew.fail(f"{where}: [tests] toolchain is a list of strings, the command first, not {toolchain!r}")
    if runner is not None and runner not in RUNNERS:
        crew.fail(f"{where}: [tests] runner is " + " or ".join(f'"{r}"' for r in RUNNERS) + f", not {runner!r}")
    if command is not None and not (isinstance(command, str) and command):
        crew.fail(f"{where}: [tests] command is a string, not {command!r}")
    if runner == "command" and command is None:
        crew.fail(f'{where}: [tests] runner = "command" names no command')
    return {"toolchain": toolchain, "runner": runner, "command": command}


def in_toolchain(script, argv):
    """argv run inside the kept toolchain: sourced by the bash on PATH, anything it prints sent to stderr, so a
    command's stdout is its own. With no toolchain, argv as it is."""
    return ["bash", "-c", 'source "$0" >&2; exec "$@"', script, *argv] if script else list(argv)


def readying(decl, script):
    """The steps that make a worktree ready through its kit's declaration (plan.17), in order, each (what, argv, out):
    the declared toolchain, its output kept in script (out); then, for the moon runner, moon's version, which
    moon_floor judges, and `moon setup`, inside that toolchain. A command runner needs no setup, and a kit that
    declares nothing has no steps."""
    if not decl:
        return []
    steps, tool = [], None
    if decl["toolchain"]:
        steps.append(("the toolchain", list(decl["toolchain"]), script))
        tool = script
    if decl["runner"] == "moon":
        steps.append(("moon --version", in_toolchain(tool, ["moon", "--version"]), None))
        steps.append(("moon setup", in_toolchain(tool, ["moon", "setup"]), None))
    return steps


def moon_floor(version):
    """Why `moon --version`'s output is not a moon the moon runner sets up, or None: a version below MOON_FLOOR, or
    output that names none."""
    m = re.search(r"\bmoon (\d+)\.(\d+)\.(\d+)", version or "")
    if not m:
        return f"moon --version printed no version crew can read: {(version or '').strip()[:80] or 'nothing'}"
    have = (int(m.group(1)), int(m.group(2)))
    if have < MOON_FLOOR:
        return f"the kit's toolchain runs moon {'.'.join(m.groups())}, below the moon runner's floor, {'.'.join(map(str, MOON_FLOOR))}"
    return None


def place_said(out):
    """What PLACE printed of a worktree it made or found: its absolute git directory and its DECLARATION's text, or None
    when it has none. Refused when the output is not what PLACE prints."""
    said = dict(line.split("=", 1) for line in (out or "").splitlines() if "=" in line)
    gitdir, decl = said.get("GITDIR"), said.get("DECLARATION")
    if not gitdir or decl is None:
        crew.fail(f"crew can't read where the worktree's git directory is and what its kit declares from: {(out or '').strip()[:200] or 'nothing'}")
    if decl == "-":
        return gitdir, None
    try:
        return gitdir, base64.b64decode(decl).decode()
    except (binascii.Error, UnicodeDecodeError) as e:
        crew.fail(f"crew can't read the worktree's {DECLARATION} as PLACE sent it: {e}")


def step_failed(place, what, code, output, lines=15):
    """crew's words for a step that failed in a worktree: the place, the step, its exit and its last lines, and that
    running the command again sets the worktree up."""
    tail = "\n".join((output or "").strip().splitlines()[-lines:])
    return (f"{place} is made but not ready: {what} exited {code}" + (f":\n{tail}\n" if tail else "; ")
            + "Running the command again sets it up.")

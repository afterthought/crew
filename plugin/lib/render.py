#!/usr/bin/env python3
"""render.py <team> <role>: print the role's brief for the team.

{{NAME}} takes the setting NAME (the team's team.sh, its machine, and what crew derives from them);
{{name}} takes the whole file <team folder>/name.md, which is filled the same way.
A token left unfilled is an error, never blank text."""
import os, pathlib, re, subprocess, sys

team, role = sys.argv[1], sys.argv[2]
lib = pathlib.Path(__file__).resolve().parent
env = subprocess.run(
    ["bash", "-c", f"team='{team}'; set -a; . '{lib}/team-env.sh'; echo \"__DIR__=$team_dir\"; env -0"],
    check=True, capture_output=True).stdout.decode()
head, _, rest = env.partition("\n")
team_dir = pathlib.Path(head.split("=", 1)[1])
vars_ = dict(kv.split("=", 1) for kv in rest.split("\0") if "=" in kv)
TOKEN = re.compile(r"\{\{([A-Za-z_]+)\}\}")

def fill(m, src=role):
    key = m.group(1)
    if key.isupper():
        if key not in vars_:
            sys.exit(f"{src} needs {{{{{key}}}}} and the team's settings do not give it")
        return vars_[key]
    part = team_dir / f"{key}.md"
    if not part.is_file():
        sys.exit(f"{src} needs {{{{{key}}}}} and {part} does not exist")
    return TOKEN.sub(lambda n: fill(n, part.name), part.read_text().rstrip("\n"))

sys.stdout.write(TOKEN.sub(fill, (lib.parent / "roles" / f"{role}.md").read_text()))

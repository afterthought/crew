"""Where sluice keeps a branch, for crew's stub sluice and stub wt-submit, as sluice 0.36.4 routes it (its rule core.15,
crates/sluice-core/src/branches.rs): by the policy, .config/sluice.toml, at the branch's own revision in this
repository, or at origin's tracking ref of it when there is no local branch; the `remote` of the [branches."<pattern>"]
table that matches the branch, the most specific first, names where it lives, and no remote means local refs. Run as
`python3 route.py <branch>` in a checkout, it prints the remote, or nothing for local refs. Not executable, so no
command of the stubs' PATH."""
import fnmatch
import subprocess
import sys
import tomllib


def rev(ref):
    """The commit a ref is at in this repository, or None."""
    r = subprocess.run(["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], capture_output=True, text=True)
    return r.stdout.strip() or None


def table(at, branch):
    """The table of the policy at a revision that matches the branch, as sluice matches it; {} when none does."""
    r = subprocess.run(["git", "show", f"{at}:.config/sluice.toml"], capture_output=True, text=True)
    branches = tomllib.loads(r.stdout).get("branches", {}) if r.returncode == 0 else {}
    matching = sorted((p for p in branches if fnmatch.fnmatchcase(branch, p)), key=lambda p: (p.count("*"), -len(p)))
    return branches[matching[0]] if matching else {}


def remote(branch):
    """The remote sluice keeps the branch on, or None: by the policy at its own revision, or at origin's tracking ref
    of it when there is no local branch; None too when there is neither."""
    at = rev(f"refs/heads/{branch}") or rev(f"refs/remotes/origin/{branch}")
    return table(at, branch).get("remote") or None if at else None


if __name__ == "__main__":
    print(remote(sys.argv[1]) or "")

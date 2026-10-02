#!/usr/bin/env python3
"""plan.py: the bolt plan, one recutils plan.rec per partition and blueprints repo, on its plan/<label> branch."""
import shutil, sys


def need_recutils():
    """Every plan command checks for recutils before anything else."""
    for c in ("recsel", "recfix"):
        if not shutil.which(c):
            sys.exit(f"crew's plan needs recutils, and {c} is not on PATH: install the recutils package "
                     "(crew's devenv.nix declares it; on a host, swancloud's packages)")


def main(argv):
    need_recutils()
    sys.exit(f"crew {' '.join(argv)}: not a plan command")


if __name__ == "__main__":
    main(sys.argv[1:])

#!/bin/sh
# Prints the verification of a bolt's head, as bolt-verify.sh recorded it, and writes nothing:
#
#   sh .config/hooks/bolt-status.sh [<bolt>]
#
# run in a worktree of crew; the bolt is the current branch's when none is named. It prints the record of the
# bolt's current revision from <git common dir>/bolt-verify/<bolt>/, a run recorded as running whose process is
# gone shown as interrupted, the file left as it is. It exits 0 only when that run is green; 1 when it is red,
# interrupted or still running, or when the head has no recorded run; 2 when the record can't be read or no bolt
# is named. It uses only sh, git, sed and grep, so it runs with or without devenv, and over ssh.
set -u

refuse() { echo "bolt-status: $*" >&2; exit 2; }
# field <name> <record>: the value of each field of that name in the record
field() { sed -n "s/^$1: //p" "$2"; }
# state <record> <rev>: the run's state, interrupted for a running one whose process is gone; or, failing, why the
# record is not one bolt-verify.sh wrote for that revision
state() {
  [ -r "$1" ] || { echo "it cannot be read"; return 1; }
  s=$(field State "$1")
  case $s in running | green | red) ;; *) echo "it holds no one State bolt-verify.sh writes"; return 1 ;; esac
  [ "$(field Rev "$1")" = "$2" ] || { echo "its Rev is not $2"; return 1; }
  if [ "$s" = running ]; then
    p=$(field Pid "$1")
    case $p in '' | *[!0-9]*) echo "its Pid is not a process"; return 1 ;; esac
    kill -0 "$p" 2>/dev/null || s=interrupted
  fi
  echo "$s"
}

if [ $# -gt 0 ]; then
  bolt=$1
else
  branch=$(git symbolic-ref --short -q HEAD)
  case $branch in
    bolt/*) bolt=${branch#bolt/} ;;
    *) refuse "${branch:-a detached HEAD} is not a bolt's branch: name the bolt, or run this in its worktree" ;;
  esac
fi
printf '%s\n' "$bolt" | grep -Eqx '[a-z0-9][a-z0-9-]*' || refuse "$bolt is not a bolt name crew accepts"
rev=$(git rev-parse --verify -q "refs/heads/bolt/$bolt^{commit}") || refuse "there is no branch bolt/$bolt"
common=$(git rev-parse --path-format=absolute --git-common-dir) || refuse "cannot find the repository's git directory"
dir=$common/bolt-verify/$bolt
rec=$dir/$rev.rec

if [ ! -e "$rec" ]; then
  echo "not verified: $rev"
  echo "bolt/$bolt's head has no recorded run."
  newest=$(ls -t "$dir"/*.rec 2>/dev/null | head -1)
  if [ -n "$newest" ]; then
    o=$(basename "$newest" .rec)
    if s=$(state "$newest" "$o"); then echo "The newest recorded run, of $o, reads $s."; else echo "The newest recorded run, of $o, can't be read: $s."; fi
  fi
  exit 1
fi

s=$(state "$rec" "$rev") || refuse "cannot read $rec: $s"
sed "s/^State: .*/State: $s/" "$rec"
[ "$s" = green ]

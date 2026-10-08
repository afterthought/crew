#!/bin/sh
# The bolt's verification. worktrunk runs it as the [post-merge] hook (.config/wt.toml) in the target's worktree
# after each merge, with the target's branch; ops runs it by hand from the bolt's worktree, with none, to verify
# the bolt's head again when a run was cut off or a machine was fixed and nothing has merged since:
#
#   devenv shell -- sh .config/hooks/bolt-verify.sh
#
# It runs crew's whole suite, tests/run without the live test, on a copy of the revision the bolt holds when it is
# started, exported with git archive into a scratch directory, so a later merge into the bolt never changes the
# files under a run in progress; two merges in a row run side by side, each on its own revision. Each run records
# its outcome in <git common dir>/bolt-verify/<bolt>/, where every worktree on the host reads it:
#
#   <rev>.rec   one recutils record: State (running | green | red), Rev, Subject, Started, Ended, Pid,
#               Failed (one field per failing test), Log
#   <rev>.log   the run's output
#
# bolt-status.sh prints the record of the bolt's head. A run cut off leaves its record `running` with its process
# gone, which bolt-status.sh reads as interrupted. A branch that isn't a bolt's, main's among them, is not verified.
set -u

refuse() { echo "bolt-verify: $*" >&2; exit 1; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
# field <name> <record>: the value of each field of that name in the record
field() { sed -n "s/^$1: //p" "$2"; }
# readable <record> <rev>: the record is one this script wrote for that revision; $why says why when it is not
readable() {
  [ -r "$1" ] || { why="it cannot be read"; return 1; }
  case $(field State "$1") in running | green | red) ;; *) why="it holds no one State this script writes"; return 1 ;; esac
  [ "$(field Rev "$1")" = "$2" ] || { why="its Rev is not $2"; return 1; }
}
# alive <record>: the record says running, and its run's process still answers
alive() {
  [ "$(field State "$1")" = running ] || return 1
  pid=$(field Pid "$1")
  case $pid in '' | *[!0-9]*) return 1 ;; esac
  kill -0 "$pid" 2>/dev/null
}

branch=${1:-$(git symbolic-ref --short -q HEAD)}
case $branch in
  bolt/*) bolt=${branch#bolt/} ;;
  *) echo "bolt-verify: not verifying ${branch:-a detached HEAD}: only a bolt's branch is verified"; exit 0 ;;
esac
printf '%s\n' "$bolt" | grep -Eqx '[a-z0-9][a-z0-9-]*' || refuse "$branch does not name a bolt crew accepts"
common=$(git rev-parse --path-format=absolute --git-common-dir) || refuse "cannot find the repository's git directory"
dir=$common/bolt-verify/$bolt

# Started by a merge or by hand: read the bolt's revision once, refuse while a run of it is alive, and detach the
# run under worktrunk's tether, so it is not cut off when worktrunk's own process ends and is ended when the bolt's
# worktree is removed. Without the tether, nohup alone still detaches it.
if [ -z "${BOLT_VERIFY_REV:-}" ]; then
  rev=$(git rev-parse --verify -q "refs/heads/$branch^{commit}") || refuse "cannot read $branch"
  short=$(git rev-parse --short "$rev")
  if [ -e "$dir/$rev.rec" ]; then
    readable "$dir/$rev.rec" "$rev" || refuse "cannot read $dir/$rev.rec: $why; it is left as it is, and removing it lets $short be verified again"
    alive "$dir/$rev.rec" && refuse "a run of $branch at $short is in progress (process $pid); sh .config/hooks/bolt-status.sh prints it"
  fi
  mkdir -p "$dir" || refuse "cannot make $dir"
  self=$(cd "$(dirname "$0")" && pwd -P)/$(basename "$0")
  tether=
  wt step tether --help >/dev/null 2>&1 && tether="wt step tether --"
  # shellcheck disable=SC2086 # $tether is the tether's words, or none
  BOLT_VERIFY_REV=$rev nohup $tether sh "$self" "$branch" </dev/null >/dev/null 2>&1 &
  echo "bolt-verify: verifying $branch at $short in the background; sh .config/hooks/bolt-status.sh prints its outcome"
  exit 0
fi

# The run itself, detached. BOLT_VERIFY_REV goes once read: a suite that inherited it would have any test that
# merges into a bolt of its own verify this run's revision there instead of that bolt's.
rev=$BOLT_VERIFY_REV
unset BOLT_VERIFY_REV
rec=$dir/$rev.rec
log=$dir/$rev.log
# A run of this revision claimed meanwhile, or a record that can't be read, is left alone.
if [ -e "$rec" ]; then readable "$rec" "$rev" || exit 1; alive "$rec" && exit 1; fi
subject=$(git log -1 --format=%s "$rev")
started=$(now)

# record <state> [<failed test>...]: the run's record, written whole and renamed into place
record() {
  state=$1; shift
  {
    printf 'State: %s\nRev: %s\nSubject: %s\nStarted: %s\n' "$state" "$rev" "$subject" "$started"
    [ "$state" = running ] || printf 'Ended: %s\n' "$(now)"
    printf 'Pid: %s\n' "$$"
    for t in "$@"; do printf 'Failed: %s\n' "$t"; done
    printf 'Log: %s\n' "$log"
  } >"$rec.$$" && mv "$rec.$$" "$rec"
}

record running
: >"$log"

# The bolt's other revisions whose runs have ended go: the directory holds the newest outcome of each run in flight.
for other in "$dir"/*.rec; do
  [ -f "$other" ] && [ "$other" != "$rec" ] || continue
  o=$(basename "$other" .rec)
  if readable "$other" "$o" && ! alive "$other"; then rm -f "$other" "$dir/$o.log"; fi
done

# The scratch copy is made by mktemp under the temp dir, and only such a directory is ever removed.
tmp=$(cd "${TMPDIR:-/tmp}" && pwd -P) || { echo "cannot read the temp dir ${TMPDIR:-/tmp}" >>"$log"; record red; exit 1; }
copy=$(mktemp -d "$tmp/crew-verify.XXXXXX") && copy=$(cd "$copy" && pwd -P) || { echo "cannot make a scratch directory under $tmp" >>"$log"; record red; exit 1; }
unscratch() { case $copy in "$tmp"/crew-verify.??????) rm -rf -- "$copy" ;; *) echo "not removing $copy" >>"$log" ;; esac; }
case $copy in "$tmp"/crew-verify.??????) ;; *) echo "mktemp gave $copy, not a crew-verify directory under $tmp" >>"$log"; record red; exit 1 ;; esac

# Cut off, the run removes its copy and leaves its record running, which bolt-status.sh reads as interrupted.
child=
stop() { [ -n "$child" ] && kill "$child" 2>/dev/null; unscratch; exit "$1"; }
trap 'stop 129' HUP
trap 'stop 130' INT
trap 'stop 143' TERM

if ! { git archive -o "$copy/.rev.tar" "$rev" && tar -x -f "$copy/.rev.tar" -C "$copy" && rm -f "$copy/.rev.tar"; } >>"$log" 2>&1; then
  echo "cannot export $rev into $copy" >>"$log"; unscratch; record red; exit 1
fi
# Waited for in the background, so a signal reaches the trap at once rather than once the suite ends.
(cd "$copy" && exec env CREW_TEST_LIVE= ./tests/run) </dev/null >>"$log" 2>&1 &
child=$!
wait "$child"; status=$?
child=
unscratch

set -f
# shellcheck disable=SC2046 # one failing test's name per word
if [ "$status" -eq 0 ]; then record green; else record red $(sed -n 's/^FAIL  \([^ ]*\).*/\1/p' "$log"); fi

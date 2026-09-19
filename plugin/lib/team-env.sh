# Sourced with $team set to a team's short name (switchboard) or org/name (willdan/switchboard).
# Leaves: team_dir, every setting of the team and of its machine, and what crew derives from them.
crew_home=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
case $team in
  */*) team_dir=$crew_home/teams/$team ;;
  *)   team_dir=$(ls -d "$crew_home"/teams/*/"$team" 2>/dev/null | head -1) ;;
esac
[[ -n ${team_dir:-} && -f $team_dir/team.sh ]] || { echo "no team '$team'. teams: $(cd "$crew_home/teams" && ls -d */* | tr '\n' ' ')" >&2; exit 2; }
CODERS=1
. "$team_dir/team.sh"
[[ -f $crew_home/machines/$MACHINE.sh ]] || { echo "team $TEAM runs on $MACHINE, and machines/$MACHINE.sh does not exist" >&2; exit 2; }
. "$crew_home/machines/$MACHINE.sh"
org_root_var=ORG_ROOT_$ORG; ORG_ROOT=${!org_root_var:?machines/$MACHINE.sh sets no $org_root_var}
KIT=$ORG_ROOT/$KIT_REPO
DESIGN=$ORG_ROOT/$DESIGN_REPO
TEAM_CMD=$CREW_HOME/plugin/bin/crew
state=$HOME/.local/state/$TEAM-team
# Agent names are unique across a herdr session, so every one carries its team.
CONDUCTOR=$TEAM-conductor FABLE=$TEAM-fable EXPLORER=$TEAM-explorer OPS=$TEAM-ops
coder_roles=(); CODER_NAMES=
for n in $(seq "$CODERS"); do coder_roles+=("coder-$n"); CODER_NAMES+="${CODER_NAMES:+, }\`$TEAM-coder-$n\`"; done
SELF=${CREW_SELF:-}
export TEAM ORG MACHINE SESSION KIT DESIGN TEAM_CMD ORG_ROOT CREW_HOME CODERS CODER_NAMES CONDUCTOR FABLE EXPLORER OPS SELF

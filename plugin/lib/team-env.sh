# Sourced with $team set to a team's short name (switchboard) or org/name (willdan/switchboard).
# Leaves: team_dir, TEAM and every setting of the team, its machine's settings, KIT, DESIGN and state.
crew_home=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
case $team in
  */*) team_dir=$crew_home/teams/$team ;;
  *)   team_dir=$(ls -d "$crew_home"/teams/*/"$team" 2>/dev/null | head -1) ;;
esac
[[ -n ${team_dir:-} && -f $team_dir/team.sh ]] || { echo "no team '$team'. teams: $(cd "$crew_home/teams" && ls -d */* | tr '\n' ' ')" >&2; exit 2; }
. "$team_dir/team.sh"
[[ -f $crew_home/machines/$MACHINE.sh ]] || { echo "team $TEAM runs on $MACHINE, and machines/$MACHINE.sh does not exist" >&2; exit 2; }
. "$crew_home/machines/$MACHINE.sh"
org_root_var=ORG_ROOT_$ORG; ORG_ROOT=${!org_root_var:?machines/$MACHINE.sh sets no $org_root_var}
KIT=$ORG_ROOT/$KIT_REPO
DESIGN=$ORG_ROOT/$DESIGN_REPO
TEAM_CMD=$CREW_HOME/plugin/bin/crew
state=$HOME/.local/state/$TEAM-team
export TEAM ORG MACHINE SESSION KIT DESIGN TEAM_CMD ORG_ROOT CREW_HOME

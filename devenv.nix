{ pkgs, ... }:
{
  # What crew's own scripts call. herdr, wt and openspec come from the machine and from each team's repository.
  packages = [ pkgs.jq pkgs.yq-go pkgs.python3 ];
}

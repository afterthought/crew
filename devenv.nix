{ pkgs, ... }:
{
  # What crew's own scripts call. herdr, wt and openspec come from the machine and from each team's repository.
  # recutils (recsel, recfix) reads and checks the bolt plan.
  packages = [ pkgs.jq pkgs.python3 pkgs.recutils ];
}

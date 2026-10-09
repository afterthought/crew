{ pkgs, config, ... }:
{
  # What crew's own scripts call. herdr, wt and openspec come from the machine and from each team's repository.
  # recutils (recsel, recfix) reads and checks the bolt plan. moon runs crew's suite as one task per test file, in
  # parallel, and replays a test whose inputs already passed (tests/suite, .moon/workspace.yml; record 0008).
  packages = [ pkgs.jq pkgs.moon pkgs.python3 pkgs.recutils ];

  # moon's task archives (.moon/cache/outputs) are a link into the git common dir, so every worktree of crew on a
  # host and its main checkout share them: a test the coder passed replays at the merge's gate, and one the gate
  # passed replays in the bolt's verification. The rest of .moon/cache stays the checkout's own, since it records
  # the checkout's absolute paths. moon reads no setting for where its cache lives, hence the link. A checkout that
  # is no git repository gets no link. moon runs the shell's own tools, never proto's from the home directory.
  enterShell = ''
    if _moon_common="$(git -C ${config.devenv.root} rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
      _moon_cache=${config.devenv.root}/.moon/cache
      [ -L "$_moon_cache" ] && rm -f "$_moon_cache"
      mkdir -p "$_moon_common/moon-outputs" "$_moon_cache"
      if [ ! -L "$_moon_cache/outputs" ]; then
        rm -rf "$_moon_cache/outputs"
        ln -s "$_moon_common/moon-outputs" "$_moon_cache/outputs"
      fi
    fi
    unset _moon_common _moon_cache
    export MOON_TOOLCHAIN_FORCE_GLOBALS=true
  '';
}

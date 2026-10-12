{ pkgs, config, ... }:
let
  # moon from moonrepo's own release build, at the version sluice pins: nixpkgs trails moon by a minor version or
  # more, and sluice's moon profile needs 2.6. Linux takes the static musl build, so no loader needs patching.
  moon =
    let
      version = "2.6.1";
      target = {
        aarch64-darwin = "aarch64-apple-darwin";
        x86_64-darwin = "x86_64-apple-darwin";
        aarch64-linux = "aarch64-unknown-linux-musl";
        x86_64-linux = "x86_64-unknown-linux-musl";
      }.${pkgs.stdenv.hostPlatform.system} or (throw "moon ${version}: no release build for ${pkgs.stdenv.hostPlatform.system}");
      hashes = {
        aarch64-apple-darwin = "2922ce70277cc6f3750106fa9ebd1e25ed890ec8cdba4570148ff8701a5bea53";
        x86_64-apple-darwin = "ef715c5fa43985de841049c319c52e9307a233a8634c08b6729e7b224592dc8e";
        aarch64-unknown-linux-musl = "b1fb67933231c9c565ea4375b54f0f9645112d76ede767a6040c5142bf7c0310";
        x86_64-unknown-linux-musl = "200314608ee89d1deecc7cd0bbd523d4dffa64ffbb365989f003f3a8d91c9080";
      };
    in
    pkgs.stdenvNoCC.mkDerivation {
      pname = "moon";
      inherit version;
      src = pkgs.fetchurl {
        url = "https://github.com/moonrepo/moon/releases/download/v${version}/moon_cli-${target}.tar.xz";
        sha256 = hashes.${target};
      };
      sourceRoot = "moon_cli-${target}";
      installPhase = ''
        runHook preInstall
        install -Dm755 -t $out/bin moon moonx
        runHook postInstall
      '';
    };
in
{
  # What crew's own scripts call. herdr, wt and openspec come from the machine and from each team's repository.
  # recutils (recsel, recfix) reads and checks the bolt plan. moon runs crew's suite as tasks in parallel, and
  # replays a task whose inputs already passed (tests/suite, .moon/workspace.yml; record 0008). pytest runs the
  # logic and contract tiers (record 0022); crew's own Python imports nothing but the standard library (code.1).
  packages = [ pkgs.jq moon (pkgs.python3.withPackages (ps: [ ps.pytest ])) pkgs.recutils ];

  # moon's task archives (.moon/cache/outputs) are a link into the git common dir, so every worktree of crew on a
  # host and its main checkout share them: a test the coder passed replays at the merge's gate, and one the gate
  # passed replays in the bolt's verification. The rest of .moon/cache stays the checkout's own, since it records
  # the checkout's absolute paths. moon reads no setting for where its cache lives, hence the link. A checkout that
  # is no git repository gets no link. moon runs the shell's own tools, never proto's from the home directory.
  enterShell = ''
    if _moon_common="$(git -C "${config.devenv.root}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
      _moon_cache="${config.devenv.root}/.moon/cache"
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

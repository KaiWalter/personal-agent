{
  description = "nix-python-uv-environment";

  inputs = {
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs-unstable, nixpkgs }:
    {
      devShell.x86_64-linux = (
        let
          system = "x86_64-linux";

          nixpkgsSystem = import nixpkgs { inherit system; config.allowUnfree = true; };
          nixpkgsSystemUnstable = import nixpkgs-unstable { inherit system; config.allowUnfree = true; };

          lib = nixpkgsSystem.lib;
          lib-unstable = nixpkgsSystemUnstable.lib;

          pkgs = nixpkgsSystem.pkgs;
          pkgs-unstable = nixpkgsSystemUnstable.pkgs;
        in
        pkgs.mkShell
          {
            nativeBuildInputs = (
              with pkgs; [
                pkgs-unstable.uv
              ]
            );
          }
      );
    };
}

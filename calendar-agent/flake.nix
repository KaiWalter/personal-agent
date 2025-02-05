{
  description = "nix-python-uv-environment";

  inputs = {
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs =
    {
      self,
      nixpkgs-unstable,
      nixpkgs,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);

      pkgsFor = system: import nixpkgs { inherit system; };
      pkgsUnstableFor = system: import nixpkgs-unstable { inherit system; };
    in
    {
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.alejandra);
      devShell = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
          pkgs-unstable = pkgsUnstableFor system;
        in
        pkgs.mkShell {
          nativeBuildInputs = ([
            pkgs.zsh
            pkgs-unstable.uv
          ]);

          shellHook = ''
              exec ${pkgs.zsh}/bin/zsh
            export GEMINI_API_KEY=$(op item get 2pjcnxuutw7tmg7pzsvac65nqq --reveal --fields password)
            export ANTHROPIC_API_KEY=$(op item get il25qguduuefr7pjzzxn5nuf4q --reveal --fields password)
            export MISTRAL_API_KEY=$(op item get i4akc4bf7fgnk2gf5zuddwyfjy --reveal --fields password)
            export OPENAI_API_KEY=$(op item get lw56uuvvq6b77ln6rrnwavvity --reveal --fields nvim)
          '';
        }
      );
    };
}

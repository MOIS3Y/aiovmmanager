{
  description = ''
    Async lib based on aiohttp for working with the VMmanager6 API
  '';

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs"; 
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        packages.default = mkPoetryApplication {
          python = pkgs.python3;
          projectDir = self;
        };

        devShells.default = pkgs.mkShellNoCC {
          shellHook = ''
            echo
            echo "█░█░█ █▀▀ █░░ █▀▀ █▀█ █▀▄▀█ █▀▀"
            echo "▀▄▀▄▀ ██▄ █▄▄ █▄▄ █▄█ █░▀░█ ██▄"
            echo "-- -- -- -- -- -- -- -- -- -- -"
            echo
          '';
          inputsFrom = [ self.packages.${system}.default ];
          packages = [ pkgs.poetry ];
        };
      });
}

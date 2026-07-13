{
  description = "ttyp";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };
  };

  outputs = inputs@{
    self,
    nixpkgs,
    pyproject-nix,
    uv2nix,
    pyproject-build-systems,
    ...
  }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      perSystem = system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
          python = lib.head (pyproject-nix.lib.util.filterPythonInterpreters {
            inherit (workspace) requires-python;
            inherit (pkgs) pythonInterpreters;
          });
          overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
          pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope (lib.composeManyExtensions [
            pyproject-build-systems.overlays.wheel
            overlay
          ]);
          virtualenv = pythonSet.mkVirtualEnv "ttyp-env" workspace.deps.default;
          editablePythonSet = pythonSet.overrideScope (workspace.mkEditablePyprojectOverlay {
            root = "$REPO_ROOT";
          });
        in
        {
          packages.default = virtualenv;

          devShells.default = pkgs.mkShell {
            packages = [
              (editablePythonSet.mkVirtualEnv "ttyp-dev-env" workspace.deps.all)
              pkgs.uv
            ];

            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = editablePythonSet.python.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
            '';
          };
        };
    in
    {
      packages = forAllSystems (system: (perSystem system).packages);
      devShells = forAllSystems (system: (perSystem system).devShells);

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/ttyp";
        };
      });
    };
}

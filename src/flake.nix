{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (system: {
        #martor = pkgs.fetchPypi
      });

      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (let 
              martor = python39.pkgs.buildPythonPackage rec {
                pname = "martor";
                version = "1.6.26";
                
                src = python39.pkgs.fetchPypi {
                  inherit pname version;
                  hash = "";
                };
                
                doCheck = false;
                
                meta = {
                  homepage = "https://github.com/agusmakmun/django-markdown-editor";
                  description = "Markdown editor for Django";
                };
              };

			in python3.withPackages(p: [ p.django p.gunicorn martor ]))
          ];
        };
      });
    };
}

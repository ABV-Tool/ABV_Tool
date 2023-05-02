{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems =
        [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in rec {
      packages = forAllSystems (system: {
        martor = pkgs.${system}.python39.pkgs.buildPythonPackage rec {
          pname = "martor";
          version = "1.6.26";

          src = pkgs.${system}.python39.pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-9ErxF2lbW2LAAuHGenJ7Ruzp2WYnONVR3tAYYRuL/IY=";
          };

          propagatedBuildInputs = [
            pkgs.${system}.python39.pkgs.django
            pkgs.${system}.python39.pkgs.requests
            pkgs.${system}.python39.pkgs.bleach
            self.packages.${system}.python-markdown
          ];

          doCheck = false;

          meta = {
            homepage = "https://github.com/agusmakmun/django-markdown-editor";
            description = "Markdown editor for Django";
          };
        };
        python-markdown = pkgs.${system}.python39.pkgs.buildPythonPackage rec {
          pname = "Markdown";
          version = "3.3.4";

          src = pkgs.${system}.python39.pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-MbW0kYaNzIfWwkt+PRmg1zDVnT5G9O6mQwoyG+04ekk=";
          };

          propagatedBuildInputs = [
          ];

          doCheck = false;

          meta = {
            homepage = "https://python-markdown.github.io/";
            description = "Pythojn markdown implementation";
          };
        };
        djmoney = pkgs.${system}.python39.pkgs.buildPythonPackage rec {
          pname = "django-money";
          version = "3.1.0";

          src = pkgs.${system}.python39.pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-Bqklf6eEV29aCIXpsXkGXj1NpHl4dvoKTzEN4Gttxls=";
          };

          propagatedBuildInputs = [
            self.packages.${system}.py-moneyed
            pkgs.${system}.python39.pkgs.django
          ];

          doCheck = false;

          meta = {
            homepage = "https://github.com/django-money/django-money";
            description = "Support for money fields in models and forms";
          };
        };
        py-moneyed = pkgs.${system}.python39.pkgs.buildPythonPackage rec {
          pname = "py-moneyed";
          version = "2.0";

          src = pkgs.${system}.python39.pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-pW4Zh96ssuDqxZBFUmmaXT+iUQQuUovy/3SnI1n15bM=";
          };

          propagatedBuildInputs = [
            pkgs.${system}.python39.pkgs.typing-extensions
            pkgs.${system}.python39.pkgs.babel
          ];

          doCheck = false;

          meta = {
            homepage = "https://github.com/py-moneyed/py-moneyed";
            description = "Classes for handling money in python";
          };
        };
      });

      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python39.withPackages (p: [
              p.django 
              p.gunicorn 
              p.psycopg2 
              packages.${system}.martor 
              packages.${system}.djmoney 
              packages.${system}.python-markdown 
            ]))
          ];
        };
      });
    };
}

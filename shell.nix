{
  pkgs ? import <nixpkgs> {
    config = {
      allowUnfree = true;
    };
  },
}:

let
  # Native shared libraries needed at runtime (Slint, OpenGL, CUDA, etc.)
  # Centralizing this list means LD_LIBRARY_PATH and NIX_LD_LIBRARY_PATH
  # always stay in sync automatically.
  runtimeLibs = with pkgs; [
    zlib
    libGL
    stdenv.cc.cc.lib

    # Slint native dependencies
    glib # glib provides libgobject, libglib and libgio .
    glibc
    expat
    fontconfig.lib # .lib output is required to get the actual .so files

    # Graphics / input
    mesa
    libinput

    wayland
    libxkbcommon
  ];

  runtimeLibPath = pkgs.lib.makeLibraryPath runtimeLibs;

  # Extra non-store paths (driver libs injected by the host / nixGL etc.)
  extraLibPaths = [
    "/run/opengl-driver/lib"
  ];

  fullLibPath = pkgs.lib.concatStringsSep ":" (extraLibPaths ++ [ runtimeLibPath ]);
in
pkgs.mkShell {
  name = "LicenseWise";

  buildInputs =
    with pkgs;
    [
      (python313.withPackages (
        ps: with ps; [
          #-> Basics for IDEs
          uv
          ruff # linter and code formatter
          debugpy # Debugger
          basedpyright # LSP server

          #-> Basics for package installation / bundeling
          uv # Package Manager & virtual environment manager (replaces pip while being better at everything)
          setuptools # Utilities to facilitate the installation of Python packages
          python-dotenv # Add .env support to your apps
          pyinstaller # Tool to bundle a python application with dependencies into a single package
          pyinstaller-versionfile # Create a windows version-file from a simple YAML file that can be used by PyInstaller

          #-> testing
          pytest
          pytest-cov
          pytest-aio
        ]
      ))

      gcc
      ninja
      glibc.bin
    ]
    ++ runtimeLibs;

  shellHook = ''
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  uv        : $(uv --version)"
    echo "  Python    : $(python --version)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Native runtime libraries (Slint, OpenGL, CUDA, etc.)
    export LD_LIBRARY_PATH="${fullLibPath}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    export NIX_LD_LIBRARY_PATH="${fullLibPath}''${NIX_LD_LIBRARY_PATH:+:$NIX_LD_LIBRARY_PATH}"

    # Create / activate venv
    if [ ! -d ".venv" ]; then
      echo "→ Creating venv with uv..."
      uv venv .venv --python python3.13
    fi
    source .venv/bin/activate
  '';
}

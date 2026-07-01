{
  pkgs ? import <nixpkgs> {
    config = {
      allowUnfree = true;
      cudaSupport = true;
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
    glib          # <-- add this, provides libgobject-2.0.so.0, libglib-2.0.so.0, libgio-2.0.so.0, etc.
    glibc
    expat
    fontconfig.lib   # .lib output is required to get the actual .so files

    # Graphics / input (needed off NixOS, where these fall back to /usr paths)
    mesa
    libinput

    # CUDA
    cudaPackages.cudatoolkit.lib

    wayland
    libxkbcommon
  ];

  runtimeLibPath = pkgs.lib.makeLibraryPath runtimeLibs;

  # Extra non-store paths (driver libs injected by the host / nixGL etc.)
  extraLibPaths = [
    "/run/opengl-driver/lib"
  ];

  fullLibPath = pkgs.lib.concatStringsSep ":" (
    extraLibPaths ++ [ runtimeLibPath ]
  );
in
pkgs.mkShell {
  name = "LicenseWise";

  buildInputs = with pkgs; [
    uv
    python313
    python313Packages.pip

    cudaPackages.cudatoolkit

    gcc
    ninja
    glibc.bin
  ] ++ runtimeLibs;

  shellHook = ''
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  uv        : $(uv --version)"
    echo "  Python    : $(python --version)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # CUDA
    export CUDA_HOME="${pkgs.cudaPackages.cudatoolkit}"
    export PATH="$CUDA_HOME/bin:$PATH"

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

{
  pkgs ? import <nixpkgs> {
    config = {
      allowUnfree = true;
      cudaSupport = true;
    };
  },
}:

pkgs.mkShell {
  name = "LicenseWise";

  buildInputs = with pkgs; [
    uv
    python313
    python313Packages.pip

    cudaPackages.cudatoolkit

    gcc
    ninja

    zlib
    libGL
    glibc.bin
    stdenv.cc.cc.lib
  ];

  shellHook = ''
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  uv        : $(uv --version)"
    echo "  Python    : $(python --version)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


    # Nix
    export NIX_LD_LIBRARY_PATH="/run/opengl-driver/lib''${NIX_LD_LIBRARY_PATH:+:$NIX_LD_LIBRARY_PATH}"
    export NIX_LD_LIBRARY_PATH="$CUDA_HOME/lib:${pkgs.cudaPackages.cudatoolkit.lib}/lib:$NIX_LD_LIBRARY_PATH"
    export NIX_SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt
    export TRITON_LIBCUDA_PATH=/run/opengl-driver/lib/

    #LD
    export LD_LIBRARY_PATH="/run/opengl-driver/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    export LD_LIBRARY_PATH="$CUDA_HOME/lib:${pkgs.cudaPackages.cudatoolkit.lib}/lib:$LD_LIBRARY_PATH"

    # CUDA
    export CUDA_HOME="${pkgs.cudaPackages.cudatoolkit}"
    export PATH="$CUDA_HOME/bin:$PATH"


    # Create / activate venv
    if [ ! -d ".venv" ]; then
      echo "→ Creating venv with uv..."
      uv venv .venv --python python3.13
    fi
    source .venv/bin/activate
  '';
}

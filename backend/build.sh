#!/usr/bin/env bash
# Render build script — CPU-only PyTorch + pinned ML stack (no CUDA wheels).
set -euo pipefail

python -m pip install --upgrade pip

# Install CPU torch first so pip does not pull multi-GB NVIDIA CUDA packages.
python -m pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

python -m pip install -r requirements.txt

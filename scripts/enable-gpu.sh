#!/bin/bash
# Detect and enable GPU acceleration
if command -v nvcc &> /dev/null; then
    echo "🟢 NVIDIA GPU detected - compiling with CUDA"
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp && make clean && make LLAMA_CUDA=1 -j
elif [[ $(uname) == "Darwin" ]]; then
    echo "🟠 Apple Metal detected - enabling GPU acceleration"
    export LLAMA_METAL=1
else
    echo "🔴 No GPU detected - using CPU-only mode"
fi

# Rebuild with acceleration
pip uninstall -y llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir

echo "✅ GPU optimizations applied"

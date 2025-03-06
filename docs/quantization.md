# Model Quantization Guide

Reduce model size and increase inference speed by converting models to lower precision.

## Requirements
- `llama.cpp` compiled with CUDA/OpenBLAS
- Original model in Hugging Face format

## Steps

1. **Install llama.cpp**:
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

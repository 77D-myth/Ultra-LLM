# ⚡ Ultra LLM

A standalone AI assistant with real-time web search capabilities, running entirely locally.

![Demo](docs/demo.gif)

## Features
- 🚀 300+ tokens/sec inference (TinyLlama 1.1B)
- 🌐 Integrated web search
- 📱 Single-file architecture
- 🐳 Docker support

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# 3. Run (with your search API)
SEARCH_API="https://your.search/api" python app.py
```

## Configuration

| Environment Variable | Description                          |
|----------------------|--------------------------------------|
| `MODEL_PATH`         | Path to GGUF model file              |
| `SEARCH_API`         | Your search engine endpoint          |
| `LLM_THREADS`        | CPU threads for inference (default: all) |

## Performance Tips
1. Use `llama.cpp` compiled with BLAS support
2. Quantize model to lower precision (Q2_K)
3. Enable GPU acceleration ([CUDA instructions](docs/cuda.md))

## License
MIT
## Advanced Tuning

### Hardware Acceleration
```bash
./scripts/enable-gpu.sh

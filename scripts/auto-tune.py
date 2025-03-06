import platform
import psutil
import os

def optimize():
    system = platform.system()
    mem_gb = psutil.virtual_memory().total // (1024**3)
    cpu_cores = os.cpu_count()

    # Memory-based model selection
    model_map = {
        (0, 4): "tinyllama-1.1b-Q2_K.gguf",
        (4, 8): "llama-2-7b-Q4_K_M.gguf",
        (8, float('inf')): "mixtral-8x7b-Q4_K_M.gguf"
    }

    selected_model = next(
        v for (lo, hi), v in model_map.items()
        if lo <= mem_gb < hi
    )

    # Write optimized config
    with open("config.json", "w") as f:
        json.dump({
            "model": selected_model,
            "threads": max(1, cpu_cores - 2),
            "gpu_layers": 35 if system == "Darwin" else 0
        }, f)

if __name__ == "__main__":
    optimize()
    print("⚙️ Auto-configured for your hardware")

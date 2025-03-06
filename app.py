# ultra_llm.py
import asyncio
import os
import sys
import time
import subprocess
import logging
from functools import wraps
from typing import Callable, Any
from aiohttp import web
from llama_cpp import Llama
import aiohttp
import json

# ======== Configuration ========
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LLM_THREADS = 8
SEARCH_API = os.getenv("SEARCH_API", "https://your-searx-instance.com/search?q={query}&format=json")
SEARCH_TIMEOUT = 2

# ======== Error Handling Setup ========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoResolver:
    def __init__(self):
        self.error_history = []
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.model_url = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

    def error_handler(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                self.error_history.append({
                    "timestamp": time.time(),
                    "function": func.__name__,
                    "error": str(e)
                })
                return await self.attempt_recovery(e, func, args, kwargs)
        return wrapper

    async def attempt_recovery(self, error: Exception, func: Callable, args: tuple, kwargs: dict) -> Any:
        error_type = type(error).__name__
        recovery_strategies = {
            "FileNotFoundError": self.handle_missing_model,
            "ConnectionError": self.handle_connection_issues,
            "TimeoutError": self.handle_timeout,
            "RuntimeError": self.handle_runtime_error
        }

        if self.recovery_attempts < self.max_recovery_attempts:
            handler = recovery_strategies.get(error_type, self.generic_recovery)
            if await handler(error):
                self.recovery_attempts += 1
                return await func(*args, **kwargs)
        
        logger.critical("Automatic recovery failed. Entering failsafe mode.")
        return await self.failsafe_response(error)

    async def handle_missing_model(self, error: Exception) -> bool:
        logger.info("Attempting model recovery...")
        try:
            model_dir = os.path.dirname(MODEL_PATH)
            if model_dir and not os.path.exists(model_dir):
                os.makedirs(model_dir)
            
            subprocess.run(
                ["wget", self.model_url, "-O", MODEL_PATH],
                check=True,
                capture_output=True
            )
            logger.info("Model downloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Model recovery failed: {str(e)}")
            return False

    async def handle_connection_issues(self, error: Exception) -> bool:
        logger.info("Attempting network recovery...")
        try:
            subprocess.run(["ping", "-c", "1", "8.8.8.8"], check=True)
            return True
        except Exception as e:
            logger.error(f"Network recovery failed: {str(e)}")
            return False

    async def handle_timeout(self, error: Exception) -> bool:
        global SEARCH_TIMEOUT
        SEARCH_TIMEOUT += 2
        logger.info(f"Adjusted search timeout to {SEARCH_TIMEOUT}s")
        return True

    async def handle_runtime_error(self, error: Exception) -> bool:
        global LLM_THREADS
        LLM_THREADS = max(1, LLM_THREADS - 1)
        logger.info(f"Optimized CPU threads to {LLM_THREADS}")
        return True

    async def generic_recovery(self, error: Exception) -> bool:
        logger.info("Attempting generic recovery...")
        time.sleep(2 ** self.recovery_attempts)
        return True

    async def failsafe_response(self, error: Exception) -> dict:
        return {
            "status": "error",
            "message": "Critical system failure",
            "error": str(error),
            "recovery_attempts": self.recovery_attempts,
            "suggested_action": "Check system logs and restart service"
        }

resolver = AutoResolver()

# ======== Model Initialization ========
try:
    if "--test" in sys.argv:
        print("🚨 Running in test mode")
        llm = Llama(model_path=MODEL_PATH, n_ctx=128, n_threads=2)
        print("✅ Model loaded successfully")
        sys.exit(0)
    else:
        llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=LLM_THREADS)
except FileNotFoundError as e:
    logger.critical("Critical startup error: Model file missing!")
    sys.exit(1)

# ======== Web Application ========
@resolver.error_handler
async def generate(request):
    data = await request.json()
    prompt = data.get('prompt', '')
    
    llm_task = asyncio.create_task(
        llm.create_chat_completion([{"role": "user", "content": prompt}], max_tokens=150)
    )
    search_task = asyncio.create_task(search_web(prompt))
    
    llm_response, search_results = await asyncio.gather(llm_task, search_task)
    
    return web.json_response({
        "answer": llm_response['choices'][0]['message']['content'],
        "sources": search_results[:3]
    })

@resolver.error_handler
async def search_web(query):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_API.format(query=query), timeout=SEARCH_TIMEOUT) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return [{"title": r.get('title',''), "url": r.get('url','')} for r in results.get('results', [])[:3]]
                return []
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return []

async def health_check(request):
    return web.json_response({
        "status": "healthy" if resolver.recovery_attempts == 0 else "degraded",
        "error_count": len(resolver.error_history),
        "active_threads": LLM_THREADS,
        "last_errors": resolver.error_history[-3:]
    })

HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Ultra LLM</title>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 20px; font-family: system-ui; }
        .container { max-width: 800px; margin: 0 auto; }
        input { width: 100%; padding: 12px; font-size: 16px; margin-bottom: 10px; }
        #output { margin-top: 20px; white-space: pre-wrap; }
        .source { color: #666; font-size: 0.9em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <input type="text" id="input" placeholder="Ask anything..." autofocus>
        <div id="output"></div>
    </div>
    <script>
        const input = document.getElementById('input');
        const output = document.getElementById('output');
        
        input.addEventListener('input', async (e) => {
            const prompt = e.target.value;
            if(prompt.length < 3) return;
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt})
                });
                
                const data = await response.json();
                output.innerHTML = `
                    <strong>Answer:</strong> ${data.answer}
                    ${data.sources.map(s => 
                        `<div class="source">
                            <a href="${s.url}" target="_blank">${s.title}</a>
                        </div>`
                    ).join('')}
                `;
            } catch (e) {
                output.textContent = "Error: " + e.message;
            }
        });
    </script>
</body>
</html>"""

app = web.Application()
app.router.add_get('/', lambda r: web.Response(text=HTML, content_type='text/html'))
app.router.add_post('/generate', generate)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    web.run_app(app, port=8080)

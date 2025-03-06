# ultra_llm.py
import asyncio
from aiohttp import web
from llama_cpp import Llama
import aiohttp
import json

# ======== Configuration ========
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"  # <1GB model
LLM_THREADS = 8  # Use all CPU cores
SEARCH_API = "https://searxng.example.com/search?q={query}&format=json"  # Self-hosted search engine

# ======== Initialize LLM ========
llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=LLM_THREADS)

# ======== Async Web Server ========
async def handle(request):
    return web.Response(text=HTML, content_type='text/html')

async def generate(request):
    data = await request.json()
    prompt = data.get('prompt', '')
    
    # Parallel processing
    llm_task = asyncio.create_task(
        llm.create_chat_completion([{"role": "user", "content": prompt}], max_tokens=150)
    )
    search_task = asyncio.create_task(search_web(prompt))
    
    llm_response, search_results = await asyncio.gather(llm_task, search_task)
    
    return web.json_response({
        "answer": llm_response['choices'][0]['message']['content'],
        "sources": search_results[:3]
    })

async def search_web(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_API.format(query=query)) as resp:
            results = await resp.json()
            return [{"title": r.get('title',''), "url": r.get('url','')} for r in results.get('results', [])]

# ======== Single-File HTML/JS ========
HTML = """
<!DOCTYPE html>
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
</html>
"""

# ======== Start Server ========
app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/generate', generate)

if __name__ == '__main__':
    web.run_app(app, port=8080)
  # ... [previous code] ...

SEARCH_API = os.getenv("SEARCH_API", "https://your-searx-instance.com/search?q={query}&format=json")

async def search_web(query):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_API.format(query=query), timeout=2) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return [{"title": r.get('title',''), "url": r.get('url','')} for r in results.get('results', [])[:3]]
                return []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []
# Add to imports
import sys

# Add test mode handling
if "--test" in sys.argv:
    print("🚨 Running in test mode")
    MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    try:
        llm = Llama(model_path=MODEL_PATH, n_ctx=128, n_threads=2)
        print("✅ Model loaded successfully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)
else:
    # Original initialization
    llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=LLM_THREADS)

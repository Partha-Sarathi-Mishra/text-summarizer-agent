from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from agents.summarizer import TextSummarizerAgent
import uvicorn

app = FastAPI(
    title="Text Summarizer Agent API",
    description="A simple API that uses a Gemini AI agent to summarize text.",
    version="1.0.0"
)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Text Summarizer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg-color: #0f172a;
            --surface-color: rgba(30, 41, 59, 0.7);
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.1);
        }
        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(-45deg, #0f172a, #1e1b4b, #0f172a, #312e81);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            width: 100%;
            max-width: 800px;
            padding: 2rem;
            margin: 2rem;
            background: var(--surface-color);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            animation: slideUp 0.8s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-align: center;
        }
        p.subtitle {
            text-align: center;
            color: var(--text-muted);
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 1.5rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 16px;
            color: white;
            font-size: 1rem;
            line-height: 1.6;
            resize: vertical;
            transition: all 0.3s ease;
            box-sizing: border-box;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
            background: rgba(15, 23, 42, 0.8);
        }
        .btn-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }
        button {
            background: linear-gradient(135deg, var(--primary), #818cf8);
            color: white;
            border: none;
            padding: 1rem 3rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.5);
            background: linear-gradient(135deg, var(--primary-hover), #6366f1);
        }
        button:active {
            transform: translateY(1px);
        }
        button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .result-container {
            display: none;
            margin-top: 1rem;
            padding: 2rem;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            color: var(--text-color);
            line-height: 1.8;
            font-size: 1.1rem;
            animation: fadeIn 0.5s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .error {
            color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.2);
        }
        .result-label {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ AI Text Summarizer</h1>
        <p class="subtitle">Powered by Google Gemini 2.5 Flash</p>
        
        <textarea id="textInput" placeholder="Paste your long article, document, or email here..."></textarea>
        
        <div class="btn-container">
            <button id="summarizeBtn" onclick="summarize()">
                <span id="btnText">Summarize Now</span>
                <div id="spinner" class="spinner"></div>
            </button>
        </div>
        
        <div id="resultContainer" class="result-container">
            <div class="result-label">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                Summary
            </div>
            <div id="resultText"></div>
        </div>
    </div>

    <script>
        async function summarize() {
            const input = document.getElementById('textInput').value;
            if (!input.trim()) return;
            
            const btn = document.getElementById('summarizeBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            const resultContainer = document.getElementById('resultContainer');
            const resultText = document.getElementById('resultText');
            
            // Loading state
            btn.disabled = true;
            btnText.textContent = "Processing...";
            spinner.style.display = "block";
            resultContainer.style.display = "none";
            resultContainer.classList.remove('error');
            
            try {
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: input })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultText.innerHTML = data.summary.replace(/\\n/g, '<br>');
                } else {
                    resultText.textContent = "Error: " + (data.detail || "An unexpected error occurred.");
                    resultContainer.classList.add('error');
                }
            } catch (error) {
                resultText.textContent = "Error: Failed to connect to the server.";
                resultContainer.classList.add('error');
            } finally {
                // Reset state
                btn.disabled = false;
                btnText.textContent = "Summarize Now";
                spinner.style.display = "none";
                resultContainer.style.display = "block";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTML_CONTENT

# Initialize the ADK-based agent
summarizer_agent = TextSummarizerAgent()

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="The text to be summarized")

class SummarizeResponse(BaseModel):
    summary: str

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(req: SummarizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    try:
        summary_result = summarizer_agent.summarize(req.text)
        return SummarizeResponse(summary=summary_result.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

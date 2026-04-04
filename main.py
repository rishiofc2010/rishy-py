from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import fitz
import requests
import os

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Please upload a PDF file"}

    text_content = ""
    pdf = fitz.open(stream=await file.read(), filetype="pdf")
    for page in pdf:
        text_content += page.get_text() + "\n"
    pdf.close()

    return {"content": text_content}


@app.post("/chat-openrouter")
async def chat_openrouter(req: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return {"error": "OPENROUTER_API_KEY not set"}

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/auto",
            "messages": [{"role": "user", "content": req.prompt}]
        },
        timeout=30
    )

    if response.status_code != 200:
        return {"error": response.text}

    return {
        "response": response.json()["choices"][0]["message"]["content"]
    }


@app.post("/chat-huggingface")
async def chat_hf(req: ChatRequest):
    # Use the environment variable name you have set
    hf_token = os.getenv("HUGGINGFACE_API_KEY") 
    
    # 2026 Standard: Use the V1 Chat Router
    # This is OpenAI-compatible and works for free-tier users
    url = "https://router.huggingface.co/v1/chat/completions"
    
    # Selecting a modern model that supports the Chat format
    model_id = "meta-llama/Llama-3.2-3B-Instruct"

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": req.prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    # Using 'requests' as per your imports
    # Note: In a production async app, 'httpx' is better, 
    # but 'requests' works fine for learning!
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raises error for 4xx or 5xx responses
        
        data = response.json()
        return {"reply": data["choices"][0]["message"]["content"]}
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

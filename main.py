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
            "model": "mistralai/mistral-7b-instruct",
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
    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        return {"error": "HF_TOKEN not set"}

    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers={
            "Authorization": f"Bearer {hf_token}"
        },
        json={
            "inputs": req.prompt,
            "parameters": {"max_new_tokens": 200}
        },
        timeout=30
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    try:
        output = result[0]["generated_text"]
    except:
        output = str(result)

    return {"response": output}

from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
import requests
import os

app = FastAPI()

# Index route
@app.get("/")
def read_root():
    return {"message": "Hello World"} 

# Extract text from uploaded PDF
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


# Chat endpoint
@app.post("/chat-openrouter")
async def chat(prompt: str):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",  # free model
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    reply = result["choices"][0]["message"]["content"]

    return {"response": reply}



@app.post("/chat-huggingface")
async def chat(req: ChatRequest):
    prompt = req.prompt

    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

    headers = {
        "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    # HuggingFace response format handling
    try:
        output = result[0]["generated_text"]
    except:
        output = str(result)

    return {"response": output}

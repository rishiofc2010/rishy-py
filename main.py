from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
import requests

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
@app.post("/chat")
async def chat(prompt: str):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer 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",  # 🔴 Replace this
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

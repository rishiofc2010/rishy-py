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

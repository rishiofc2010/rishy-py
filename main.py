from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF

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

import os, uuid, shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("KIMI_API_KEY")
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "tesseract")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize(text: str) -> str:
    return " ".join(text.split())

def extract_text(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng")
    return sanitize(text)

def generate_feedback(subject: str, question: str, student_answer: str) -> str:
    prompt = f"""
You are a friendly and constructive tuition teacher.
Subject: {subject}
Question: {question}
Student's handwritten answer (OCR text): {student_answer}

Provide concise, human-like feedback in the following structure:
1. Strengths (2-3 bullets)
2. Areas to Improve (2-3 bullets)
3. Sample improved answer (1 short paragraph)
"""
    response = openai.ChatCompletion.create(
        model="kimi",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

@app.post("/evaluate")
async def evaluate(
    subject: str = Form(...),
    question: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        student_text = extract_text(file_path)
        feedback = generate_feedback(subject, question, student_text)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import io
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract

app = FastAPI(root_path="/")  # <- required for Vercel

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text(contents: bytes) -> str:
    return pytesseract.image_to_string(Image.open(io.BytesIO(contents)), lang="eng").strip()

def generate_feedback(subject: str, question: str, student_answer: str) -> str:
    return (
        "1. Strengths\n"
        "   • Handwriting is legible.\n"
        "   • Key terms are present.\n\n"
        "2. Areas to Improve\n"
        "   • Add more depth to definitions.\n"
        "   • Provide a real-world example.\n\n"
        "3. Sample improved answer\n"
        "Newton’s first law: an object stays at rest or in uniform motion unless acted upon by an external force.\n"
        "Example: a hockey puck slides on ice until friction stops it."
    )

@app.post("/evaluate")
async def evaluate(
    subject: str = Form(...),
    question: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        text = extract_text(await image.read())
        return {"feedback": generate_feedback(subject, question, text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

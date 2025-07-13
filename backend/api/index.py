import os, uuid, shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text(contents: bytes) -> str:
    img = Image.open(io.BytesIO(contents))
    return pytesseract.image_to_string(img, lang="eng").strip()

def generate_feedback(subject: str, question: str, student_answer: str) -> str:
    # canned, human-like feedback
    return f"""
1. Strengths
   • Handwriting is legible.
   • Key terms are present.

2. Areas to Improve
   • Add more depth to definitions.
   • Provide a real-world example.

3. Sample improved answer
Newton’s first law states that an object remains at rest or in uniform motion in a straight line unless acted upon by an external force.  
Example: A hockey puck sliding on ice continues until friction stops it.
"""

@app.post("/evaluate")
async def evaluate(
    subject: str = Form(...),
    question: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        contents = await image.read()
        student_text = extract_text(contents)
        feedback = generate_feedback(subject, question, student_text)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

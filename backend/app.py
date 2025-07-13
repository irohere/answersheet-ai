import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract

app = FastAPI()

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
    return f"""
1. Strengths
   • Handwriting is legible.
   • Key terms are present.

2. Areas to Improve
   • Add more depth to definitions.
   • Provide a real-world example.

3. Sample improved answer
Newton’s first law: an object stays at rest or in uniform motion unless acted upon by an external force.
Example: a hockey puck slides on ice until friction stops it.
"""

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

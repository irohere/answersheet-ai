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
    return f"""
1. Strengths
   • Clear handwriting
   • Good use of keywords

2. Areas to Improve
   • Add more detail to the definition
   • Include an example

3. Sample improved answer
A body continues in its state of rest or uniform motion in a straight line unless acted upon by an external force.  
For example, a hockey puck sliding on ice keeps moving until friction slows it down.
"""
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

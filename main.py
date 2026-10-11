import os
import markdown
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Initialize FastAPI and Templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def generate_excuse(issue: str) -> str:
    """Sends the issue to Gemini and returns the excuse as raw markdown."""
    try:
        response = model.generate_content(issue)
        return response.text
    except Exception as e:
        return f"**Critical System Failure:** An error occurred while generating the RCA: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"excuse_html": None, "issue": ""})

@app.post("/", response_class=HTMLResponse)
async def create_excuse(request: Request, issue: str = Form(...)):
    if not issue.strip():
        return templates.TemplateResponse(request, "index.html", {"excuse_html": None, "issue": ""})
        
    raw_markdown = generate_excuse(issue)
    # Convert markdown to HTML for safe rendering in template
    excuse_html = markdown.markdown(raw_markdown)
    
    return templates.TemplateResponse(request, "index.html", {
        "excuse_html": excuse_html, 
        "issue": issue
    })

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import json

# =========================================
# 1️⃣ Initialize FastAPI FIRST
# =========================================
app = FastAPI(title="AI Code Review & Rewrite Agent - Enterprise")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# 2️⃣ Load Environment Variables
# =========================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# =========================================
# 3️⃣ Initialize Groq Client
# =========================================
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_TOKENS = 2000

# =========================================
# 4️⃣ Serve Frontend
# =========================================
@app.get("/app", response_class=HTMLResponse)
async def serve_app():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "frontend", "index.html")

        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception:
        return HTMLResponse("<h1>Frontend not found</h1>")

# =========================================
# 5️⃣ Request Model
# =========================================
class CodeRequest(BaseModel):
    code: str

# =========================================
# 6️⃣ Review Endpoint
# =========================================
@app.post("/api/review")
async def review_code(request: CodeRequest):

    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    prompt = f"""
You are a senior software engineer with 15+ years of experience.

Step 1:
Identify the programming language of the provided code.

Step 2:
Perform a professional code review.

Analyze strictly for:
- Bugs
- Security vulnerabilities
- Performance issues
- Best practice violations

Return ONLY valid JSON.
Do NOT return markdown.
Do NOT include explanations.
Do NOT include extra text.
Do NOT wrap in backticks.

JSON format MUST be exactly:

{{
  "language": "DetectedLanguage",
  "critical": ["issue1", "issue2"],
  "high": ["issue1"],
  "medium": [],
  "low": []
}}

If no issues exist in a category, return an empty array.

Code:
{request.code}
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return strictly valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=MAX_TOKENS,
            top_p=0.9
        )

        response_text = completion.choices[0].message.content.strip()
        parsed = json.loads(response_text)

        return {
            "language": parsed.get("language", "Unknown"),
            "review": {
                "critical": parsed.get("critical", []),
                "high": parsed.get("high", []),
                "medium": parsed.get("medium", []),
                "low": parsed.get("low", [])
            },
            "critical": len(parsed.get("critical", [])),
            "high": len(parsed.get("high", [])),
            "medium": len(parsed.get("medium", [])),
            "low": len(parsed.get("low", []))
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model did not return valid JSON."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================
# 7️⃣ Rewrite Endpoint
# =========================================
@app.post("/api/rewrite")
async def rewrite_code(request: CodeRequest):

    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    rewrite_prompt = f"""
You are a senior software engineer.

Step 1:
Identify the programming language.

Step 2:
Rewrite the code by:
- Fixing bugs
- Improving performance
- Improving security
- Applying industry best practices
- Adding documentation where necessary

Return ONLY the rewritten valid code.
Do NOT return markdown.
Do NOT include explanations.
Do NOT include extra text.
Do NOT wrap in backticks.

Code:
{request.code}
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return only valid code without explanation."},
                {"role": "user", "content": rewrite_prompt}
            ],
            temperature=0.05,
            max_tokens=MAX_TOKENS,
            top_p=0.9
        )

        rewritten_code = completion.choices[0].message.content.strip()

        return {
            "rewritten_code": rewritten_code
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================
# 8️⃣ Health Check
# =========================================
@app.get("/")
async def root():
    return {"message": "AI Code Review Agent Running (Enterprise Mode)"}
# AI-CODE-REVIEW-AGENT
AI Code Review &amp; Rewrite Agent is an LLM-powered developer assistant that automatically detects programming language, analyzes code for bugs, security risks, and performance issues, classifies findings by severity, and generates optimized rewritten code with a clear diff view. Built with FastAPI and a modern UI.

# Follow instructions to execute:
### 1. Create .env file and add groq API key
Go to backend directory
```
cd backend
```
```
GROQ_API_KEY = Your api key
``` 
### 2. Install Requirements
#### Run
```
pip install -r requirements.txt
```

### 3. Run Backend
In backend Directory Run:
```
uvicorn main:app --reload
```
And open port for backend:
```
http://127.0.0.1:8000
```
For frontend UI open :
```
http://127.0.0.1:8000/app
```

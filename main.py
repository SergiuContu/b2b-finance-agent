import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles          
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import boto3

# Security Imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

# Initialize the Rate Limiter (tracks requests by the user's IP address)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="B2B Retail Finance AI Agent",
    description="GDPR-compliant RAG agent for retail finance policies.",
)

# Attach the rate limiter to the FastAPI app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["https://faithwayai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")

bedrock_agent_client = boto3.client(
    "bedrock-agent-runtime", 
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Defense Layer 1: Input Validation
# Restricts input to 500 characters. Rejects massive payloads before they reach AWS.
class QueryRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=5, 
        max_length=500, 
        description="The user query, strictly bounded to prevent token stuffing attacks."
    )

@app.get("/")
async def serve_frontend():
    """Serves the frontend UI."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Simple endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running securely."}

# Defense Layer 2: API Rate Limiting
# Restricts each IP to 5 requests per minute.
@app.post("/ask")
@limiter.limit("5/minute")
async def ask_knowledge_base(request: Request, payload: QueryRequest):
    """Queries the Bedrock Knowledge Base and generates an answer."""

    KNOWLEDGE_BASE_ID = "GSED6MYF2K"
    MODEL_ARN = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

    try:
        response = bedrock_agent_client.retrieve_and_generate(
            input={"text": payload.question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        return {
            "answer": response["output"]["text"],
            "citations_returned": len(response.get("citations", [])) > 0,
        }

    except Exception as e:
        print(f"Internal AWS Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while processing the request.",
        )
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import boto3

# Load the environment variables from the .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="B2B Retail Finance AI Agent",
    description="GDPR-compliant RAG agent for retail finance policies.",
)

# Mount the static directory so FastAPI can serve the CSS and frontend assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enterprise CORS Policy
origins = ["https://faithwayai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Explicitly pull the keys from the loaded .env file
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")

# Initialize the AWS SDK client for Bedrock Knowledge Bases using explicit credentials
bedrock_agent_client = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
async def serve_frontend():
    """Serves the frontend UI."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """Simple endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running securely."}


@app.post("/ask")
async def ask_knowledge_base(request: QueryRequest):
    """Queries the Bedrock Knowledge Base and generates an answer."""

    # Your actual Knowledge Base ID from the AWS Console
    KNOWLEDGE_BASE_ID = "GSED6MYF2K"

    # Targeting Claude Haiku 4.5 using EU Cross-Region Inference Profile
    MODEL_ARN = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

    try:
        # retrieve_and_generate handles embedding the query, searching Pinecone, and prompting Claude
        response = bedrock_agent_client.retrieve_and_generate(
            input={"text": request.question},
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
        # Security: Log the real error internally, but return a generic error to the client
        print(f"Internal AWS Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while processing the request.",
        )

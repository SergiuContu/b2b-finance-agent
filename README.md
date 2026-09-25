# Enterprise B2B Retail Finance Compliance Agent

An enterprise-grade, GDPR-compliant Retrieval-Augmented Generation (RAG) agent engineered for B2B retail finance policies. Built with **Python 3.11**, **FastAPI**, **Amazon Bedrock Knowledge Bases**, and **Claude Haiku 4.5**, backed by a serverless vector store to achieve a **zero-fixed-cost (£0.00/month idle)** operational architecture.

---

## Architecture Overview

```text
[ User UI / Client ]
         │  (HTTPS / Strict CORS)
         ▼
[ FastAPI Backend ] ──(boto3)──► [ Amazon Bedrock Knowledge Base ]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     [ Pinecone Serverless ]                         [ AWS S3 Policy Store ]
      (Titan Text v2 Embeddings)                      (GDPR & MCA Policy Docs)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                      [ Claude Haiku 4.5 ]
                   (EU Cross-Region Inference)
                                          │
                                          ▼
                                [ Grounded Response ]
```

### Key Technical Decisions & Compliance Safeguards

- **Zero-Fixed-Cost Architecture:** Replaced traditional, high-burn vector clusters (e.g., OpenSearch Serverless at ~$175+/mo) with **Pinecone Serverless Free Tier** and pay-per-token model inference, bringing idle infrastructure costs to £0.00/month.
- **UK GDPR & Data Sovereignty:** API traffic is routed through **AWS EU Cross-Region Inference Profiles** (`eu.anthropic.claude-haiku-4-5-20251001-v1:0`), guaranteeing that token processing and retrieval remain strictly within European data boundaries.
- **Deterministic Anti-Hallucination:** Configured Bedrock Knowledge Base retrieval with grounded context boundaries. Queries with missing or out-of-scope policies trigger explicit compliance fallbacks rather than speculative model generation.
- **Defense-in-Depth API Security:** Locked down FastAPI via explicit `CORSMiddleware` restricted to verified origins (`https://faithwayai.com`), explicit environment variable injection via `python-dotenv`, and internal exception masking to prevent cloud stack trace leakage.

---

## Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic
- **Cloud & AI:** AWS Bedrock (Knowledge Bases, Guardrails), Anthropic Claude Haiku 4.5, Amazon Titan Text Embeddings v2, AWS S3
- **Vector Database:** Pinecone Serverless
- **Frontend:** Lightweight responsive chat UI using Tailwind CSS & Vanilla JavaScript
- **SDKs & Tooling:** Boto3, Python-Dotenv
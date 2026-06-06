# FleetFix AI

An AI-powered operations platform for a heavy-vehicle (truck & trailer) repair and 24/7
roadside-assistance company. It does three things:

1. **Work order → invoice.** Turns messy, bilingual (EN/FR) mechanic notes into clean,
   translated, customer-ready invoices using an LLM with structured output.
2. **Supplier PDF → database.** Extracts structured data from supplier-invoice PDFs and stores it
   in SQL Server.
3. **Cost prediction.** Estimates repair cost from work-order features with a scikit-learn model.

Workflows are orchestrated with **n8n**, the backend is **FastAPI**, data lives in **SQL Server**,
and a **TypeScript/Node** dashboard provides human review and approval.

## Tech stack

| Layer | Technology |
|---|---|
| Backend / API | Python, FastAPI, SQLAlchemy |
| AI / LLM | OpenAI API (structured outputs) — Azure OpenAI ready |
| ML | scikit-learn (Pipeline + RandomForest) |
| Document extraction | pdfplumber (OCR-ready) |
| Database | SQL Server 2022 |
| Automation | n8n |
| Frontend | TypeScript, Node.js, Express |
| Infra | Docker, Docker Compose, GitHub Actions, PowerShell |

## Architecture

```
Work orders ───────┐
                   ├─► n8n ─► FastAPI ─► SQL Server ─┬─► Dashboard (TS/Node, review + approve)
Supplier PDFs ─────┘            │ LLM service        └─► Customer invoices
                                │ PDF extraction
                                │ Cost predictor
```

## Prerequisites

- Docker Desktop (WSL2 backend on Windows)
- Python 3.11+, Node.js 20+
- Microsoft ODBC Driver 18 for SQL Server
- An OpenAI API key

## Setup

```bash
# 1. Environment variables
cp .env.example .env        # then set MSSQL_SA_PASSWORD and OPENAI_API_KEY

# 2. Infrastructure (SQL Server + n8n)
docker compose up -d

# 3. Database schema + seed (run in VS Code with the MSSQL extension,
#    connected to localhost,1433 / sa, Trust Server Certificate ON)
#    Execute sql/schema.sql then sql/seed.sql

# 4. Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload       # http://localhost:8000/docs

# 5. Train the cost model (from the project root)
python ml/train.py                  # writes ml/cost_model.joblib

# 6. Dashboard
cd frontend
npm install
npm run dev                         # http://localhost:3000

# 7. n8n
# Open http://localhost:5678, import the workflow from n8n/, activate it.
```

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/work-orders` | Create a work order |
| GET | `/work-orders` | List (optional `?status=`) |
| POST | `/work-orders/{id}/invoice` | LLM: clean + translate → invoice |
| GET | `/work-orders/{id}/invoice` | Fetch generated invoice + lines |
| POST | `/work-orders/{id}/approve` | Human approval |
| POST | `/invoices/upload` | Extract a supplier-invoice PDF |
| POST | `/predictions/cost` | Predict repair cost |

## Project structure

```
fleetfix-ai/
├── backend/      FastAPI app, services (llm, pdf_extract), routers
├── ml/           training script + dataset + saved model
├── frontend/     TypeScript/Node review dashboard
├── n8n/          exported automation workflows
├── scripts/      PowerShell automation
├── sql/          schema, seed, reset
└── docker-compose.yml
```

## Notes

- The ML model is trained on **synthetic data** for demonstration; production would require real
  historical orders and re-validation.
- The LLM is intentionally constrained: it does not invent prices. Prices come from the source
  documents (supplier invoices) or, for customer invoices, would come from a parts/labour catalog.
- Every customer invoice is **human-approved** before it's final — a guardrail against LLM error.
- LLM token usage, cost, and latency are logged to the `llm_logs` table for observability.
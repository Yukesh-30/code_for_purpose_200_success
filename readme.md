# FlowSight AI — Natural Language Financial Intelligence

### NatWest Group | Code for Purpose – India Hackathon

## Overview

- FlowSight AI is a conversational AI system that allows MSME business owners, banking relationship managers, and financial analysts to query structured financial data using plain English — no SQL knowledge required.
- Users type questions like "What were my top expenses last month?" and the system translates them into SQL queries, executes them against a financial database, and returns human-readable insights with confidence scores and suggested visualizations.

### Problem it solves

- Small business owners and non-technical banking staff cannot access or interpret raw financial data without developer support.
- This system eliminates that barrier entirely through a natural language interface.

### Intended users

- MSME business users
- Banking relationship managers
- Financial analysts

## Features

- Natural language query input — users type questions in plain English; no SQL required
- Automatic table selection — the system identifies which database tables are relevant before generating SQL, reducing hallucinations
- SQL generation from natural language — converts refined queries into executable SQL using schema-aware prompting
- Business-level data isolation — all queries are filtered by business_id to enforce multi-tenant data security
- Insight generation — raw query results are converted into a summary, key insight, and confidence score
- Suggested chart type — each response includes a recommended visualization type (bar, line, pie, etc.)
- Chat memory — the system maintains conversation history so users can ask follow-up questions like "Why did it drop?"
- Conversational fallback — non-data queries (greetings, general questions) are handled gracefully without crashing the pipeline
- Insight storage — past queries, generated SQL, and result summaries are stored for reuse and auditability

# FlowSight AI Platform - Run Guide

This guide details the setup and execution process for the FlowSight AI Platform, comprising a React/Vite frontend and a Python/Flask backend.

## Live Demo
You can try out the deployed version of the application here:
**URL:** [https://code-for-purpose-200-success.vercel.app/](https://code-for-purpose-200-success.vercel.app/)

**Demo Credentials:**
- **Username:** `ramcharan2310608@ssn.edu.in`
- **Password:** `Ram@2006`

## Prerequisites
- Node.js (LTS) & package manager (`bun` or `npm`)
- Python 3.11+
- PostgreSQL Server
- Docker Desktop (Optional - for containerized backend execution)

---

## Part 1: Backend Setup & Execution

### Option A: Local Python Environment
1. **Virtual Environment Setup**
   Navigate to the backend directory and establish an isolated virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   
   # Activate on Mac/Linux:
   source .venv/bin/activate
   # Activate on Windows:
   .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Duplicate `backend/.env.example` as `backend/.env` and configure your credentials:
   ```env
   DATABASE_URL='postgresql://username:password@hostname:port/dbname?sslmode=require'
   JWT_SECRET_KEY='your_secure_random_hash'
   FLASK_APP=main.py
   FLASK_ENV=development
   ```

4. **Initialize and Run**
   The application initializes the SQLAlchemy models automatically upon startup (via `db.create_all()`).
   Start the API server:
   ```bash
   python main.py
   ```
   *The Flask API should now be running on `http://127.0.0.1:5000/`. Keep this terminal running.*

   > **Note:** Directory `backend/scripts/` contains optional generators (like `generate_bank_transactions.py` and `generate_invoices.py`) if you need to seed your database with sample analytical data.

### Option B: Docker Container
For isolated execution without local Python dependencies, leverage the provided Dockerfile.
1. **Navigate and Build**
   ```bash
   cd backend
   docker build -t flowsight-backend .
   ```
2. **Execute Container**
   Ensure your `.env` string is correctly populated as described in Option A, then run:
   ```bash
   docker run -p 5000:5000 --env-file .env flowsight-backend
   ```

---

## Part 2: Frontend Setup & Execution

With the backend active, run the React frontend in a new terminal window.

1. **Install Dependencies**
   It is recommended to use `bun` as the package manager if available on your system, although `npm` works equivalently.
   ```bash
   cd frontend
   bun install
   ```

2. **Configure Local Environment**
   Update the `frontend/.env` variables to route requests to your local backend server instead of the production API:
   ```env
   VITE_API_URL=http://localhost:5000
   ```

3. **Start the Development Server**
   ```bash
   bun run dev
   ```
   *The Vite process will serve the development portal on `http://localhost:5173/`. Navigate here in your browser to access the FlowSight platform.*

---

## Quick Reference / Stop & Start
For subsequent startups, the execution sequence is simplified:

**Terminal 1 (Backend API):**
```bash
cd backend
source .venv/bin/activate  # (Or .venv\Scripts\activate on Windows)
python main.py
```
*(Or use `docker run -p 5000:5000 --env-file .env flowsight-backend` if using Docker)*

**Terminal 2 (Frontend Client):**
```bash
cd frontend
bun run dev
```


## Tech Stack

| Layer | Technology |
|--------|-------------|
| Backend language | Python 3.11+ |
| Backend framework | Flask |
| Frontend language | JavaScript (ES2020+) |
| Frontend framework | React |
| Database | PostgreSQL |
|Vector Database | ChromaDB|
| ORM / Query layer | SQLAlchemy |
| LLM / AI | groq (via API) |
| Embeddings / Semantic search | OpenAI `text-embedding-ada-002` |
| Chat memory | In-memory store / PostgreSQL session table |
| Package manager (backend) | pip / requirements.txt |
| Package manager (frontend) | npm / package.json |
| Environment config | python-dotenv |
| Containerization | Docker |
| Frontend deployment | Vercel |
| Backend deployment | Railway |

## Folder Structure

```text
.
├── .gitignore
├── backend/
│   ├── .dockerignore
│   ├── .env.example
│   ├── datasets/
│   │   ├── bank_transactions.csv
│   │   ├── bank_transactions_10k.csv
│   │   ├── expenses.csv
│   │   ├── expenses_3k.csv
│   │   ├── invoices.csv
│   │   ├── invoices_10k.csv
│   │   ├── loans.csv
│   │   ├── loans_2k.csv
│   │   ├── payroll.csv
│   │   ├── payroll_2k.csv
│   │   ├── recommendations.csv
│   │   ├── recommendations_2k.csv
│   │   ├── risk_scores.csv
│   │   ├── risk_scores_3k.csv
│   │   ├── vendor_payments.csv
│   │   └── vendor_payments_3k.csv
│   │
│   ├── instance/
│   │   └── test.db
│   │
│   ├── ml_models/
│   │   ├── forecast_model.pkl
│   │   ├── invoice_delay_model.pkl
│   │   ├── recommendation_model.pkl
│   │   ├── risk_score_model.pkl
│   │   └── scaler.pkl
│   │
│   ├── routes/
│   │   ├── alert_routes.py
│   │   ├── auth_routes.py
│   │   ├── business_routes.py
│   │   ├── chatbot_routes.py
│   │   ├── chat_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── forecasting_routes.py
│   │   ├── recommendation_routes.py
│   │   ├── relationship_manager_routes.py
│   │   ├── risk_routes.py
│   │   ├── team_routes.py
│   │   ├── upload_routes.py
│   │   └── __pycache__/
│   │       └── auth_routes.cpython-311.pyc
│   │
│   ├── sample_data/
│   │   ├── bank_transactions.csv
│   │   ├── expenses.csv
│   │   └── invoices.csv
│   │
│   ├── schema/
│   │   └── db_schema.py
│   │
│   ├── services/
│   │   ├── alert_service.py
│   │   ├── auth_service.py
│   │   ├── chatbot_service.py
│   │   ├── explainability_service.py
│   │   ├── forecast_service.py
│   │   ├── invoice_prediction_service.py
│   │   ├── nl_to_sql_service.py
│   │   ├── recommendation_service.py
│   │   ├── report_service.py
│   │   ├── risk_score_service.py
│   │   ├── transaction_service.py
│   │   ├── upload_service.py
│   │   └── __pycache__/
│   │       └── auth_service.cpython-311.pyc
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_forecast.py
│   │   ├── test_integration.py
│   │   ├── test_invoice_prediction.py
│   │   └── test_risk_score.py
│   │
│   ├── utils/
│   │   ├── csv_parser.py
│   │   ├── date_utils.py
│   │   ├── model_loader.py
│   │   ├── prompt_builder.py
│   │   ├── response_formatter.py
│   │   └── validators.py
│   │
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── package-lock.json
│   ├── readme.md
│   └── requirements.txt
│
├── frontend/
│   ├── .env.example
│   ├── .gitignore
│   ├── bun.lock
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   │
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── Badge.jsx
│   │   │       ├── Button.jsx
│   │   │       ├── Card.jsx
│   │   │       ├── Input.jsx
│   │   │       └── ThemeToggle.jsx
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   │
│   │   ├── layouts/
│   │   │   ├── DashboardLayout.jsx
│   │   │   └── LandingLayout.jsx
│   │   │
│   │   ├── lib/
│   │   │   └── utils.js
│   │   │
│   │   ├── pages/
│   │   │   ├── bank/
│   │   │   │   ├── AlertsCenter.jsx
│   │   │   │   ├── BankPortfolio.jsx
│   │   │   │   ├── CustomerDetail.jsx
│   │   │   │   ├── Explainability.jsx
│   │   │   │   ├── HighRiskList.jsx
│   │   │   │   ├── LendingOpportunities.jsx
│   │   │   │   ├── RiskDefaultPrediction.jsx
│   │   │   │   └── SystemAdmin.jsx
│   │   │   │
│   │   │   ├── BankingRecommendation.jsx
│   │   │   ├── CompleteProfile.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DataUpload.jsx
│   │   │   ├── Forecasting.jsx
│   │   │   ├── InvoiceRisk.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── SignupPage.jsx
│   │   │   ├── TalkToData.jsx
│   │   │   ├── TeamWorkspace.jsx
│   │   │   └── WorkingCapital.jsx
│   │   │
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── README.md
│   ├── SKILL.md
│   ├── skills-lock.json
│   ├── vercel.json
│   └── vite.config.js
│
└── readme.md

```

## Usage Examples
Login with demo credential and go to talk to data by clicking it in the sidebar.
### Example Natural Language Queries

- "What was my total revenue last month?"
- "Show me my top 5 expense categories this quarter"
- "How does my cash flow compare between January and February?"
- "Which transactions are above ₹50,000?"
- "Why did my expenses spike in March?" ← follow-up using chat memory


### Screenshots

Talk to data:

<img width="1600" height="822" alt="image" src="https://github.com/user-attachments/assets/7ade3bda-0874-4c5d-837f-074733cf4af3" />

chat

<img width="1600" height="817" alt="image" src="https://github.com/user-attachments/assets/9ada9f00-270b-42ac-85a7-223e9cce8d23" />

MSME Dashboard

<img width="1600" height="874" alt="image" src="https://github.com/user-attachments/assets/bd0595a8-e2cc-4952-a05f-cf57140ac8b1" />

Generated Report

<img width="563" height="304" alt="image" src="https://github.com/user-attachments/assets/04a10e7d-0a06-4e38-a526-32393e4dd670" />





## Architecture

The system follows a modular, multi-stage pipeline:

```text
User Query
    │
    ▼
[1] NLP Layer
    → Resolves intent, incorporates chat history
    │
    ▼
[2] Table Selector
    → Picks relevant DB tables from semantic schema
    │
    ▼
[3] SQL Generator
    → Converts refined query to SQL (business_id enforced)
    │
    ▼
[4] SQL Executor
    → Runs query safely against PostgreSQL
    │
    ▼
[5] Insight Generator
    → Converts rows into summary + confidence + chart type
    │
    ▼
[6] Response Delivery
    → Returns structured JSON to frontend
    │
    ▼
[7] Storage
    → Saves interaction to chat memory + insight store
```


### Key Design Decisions

- Table selection before SQL generation prevents hallucination by limiting schema exposure
- Business ID enforcement at the SQL generation layer ensures multi-tenant data isolation
- The conversational fallback layer handles non-data queries gracefully without pipeline errors
- Chat memory enables context-aware follow-up questions across a session

## Future Improvements

- Persistent cross-session chat memory stored in PostgreSQL
- Semantic insight retrieval to avoid recomputing answers to repeated questions
- Support for multi-language queries (Tamil, Hindi)
- Role-based access control at the API level
- Automated test suite covering SQL generation accuracy across edge cases
- Voice input support for mobile users

## Limitations

- The system has been tested on a sample financial dataset; accuracy on production-scale data has not been evaluated


### Current Implementation Status

**Fully Implemented (Frontend & Backend with Database Integration)**
* **Authentication & Onboarding:** Complete signup and login flow using JWT authentication, complete with automatic creation of business profiles and default bank accounts for new users.
* **Talk to Data (Conversational AI):** The core NLP pipeline is fully functional. It integrates with the Groq API (`llama-3.3-70b-versatile`) to resolve query intent, generate schema-aware Postgres SQL, safely execute queries, and generate business insights with persistent chat memory.
* **Data Ingestion (Uploads):** Fully functional CSV upload pipelines using Pandas. The system successfully validates, parses, and inserts records into the database for Bank Transactions, Invoices, and Expenses.
* **Team Management:** Complete functionality to fetch team members, invite new users with role assignments, and remove members from a business profile.

**Partially Implemented (Frontend Integrated with Stubbed/Mocked Backend)**
* **Dashboard & Reporting:** The frontend successfully communicates with backend endpoints to retrieve metrics and export CSV reports, but the backend currently returns static, mocked financial data.
* **Forecasting:** UI components trigger backend routes (`/optimize`, `/mitigations`), but the backend currently returns static success messages rather than connecting to live ML prediction models.
* **Risk & Invoice Delay Management:** Actions like applying for invoice factoring or sending automated reminders have backend endpoints that return simulated responses.
* **Banking Recommendations:** The recommendation engine (`/apply`, `/simulate`) is stubbed in the backend to return static simulated impacts.

**Frontend-Only Modules**
* **Bank-Side Portals:** Advanced bank-facing dashboards (e.g., `BankPortfolio`, `AlertsCenter`, `CustomerDetail`, `SystemAdmin`) have been built in the frontend React application for demonstration purposes but do not yet have corresponding backend database routing.


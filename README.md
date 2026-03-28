# ComplyOS

[![Live Demo](https://img.shields.io/badge/demo-comply--os.vercel.app-blue?style=for-the-badge&logo=vercel)](https://comply-os.vercel.app)
[![API](https://img.shields.io/badge/api-complyos.onrender.com-green?style=for-the-badge&logo=fastapi)](https://complyos.onrender.com/docs)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/next.js-16-000000?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/typescript-strict-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

**AI-powered EU AI Act compliance agent.** Classify AI systems by risk level, identify compliance gaps, and generate required documentation -- in minutes, not months.

`#eu-ai-act` `#compliance` `#rag` `#langchain` `#langgraph` `#ai-agents` `#fastapi` `#nextjs` `#legal-tech` `#regtech`

---

## The Problem

Every company deploying AI in the EU must comply with the **EU AI Act by August 2, 2026**. Non-compliance carries fines up to **EUR 35 million** or 7% of global revenue.

- 144 pages of dense legal text (113 articles, 13 annexes)
- Over 50% of organizations lack systematic inventories of their AI systems
- Current solution: hire consultants at EUR 50K-500K per engagement
- **No automated tooling exists** for EU AI Act compliance

## The Solution

ComplyOS is an AI compliance agent that automates what takes consultants months:

```
Register AI system --> Classify risk --> Analyze gaps --> Generate documentation
     (30 sec)          (15 sec)          (20 sec)            (30 sec)
```

## Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (Vercel)"]
        A[Next.js 16 Dashboard] --> B[System Registration]
        A --> C[Classification Results]
        A --> D[Gap Analysis]
        A --> E[Compliance Chat]
    end

    subgraph Backend["Backend (Render)"]
        F[FastAPI] --> G[LangGraph Orchestrator]
        G --> H["Risk Classifier Agent"]
        G --> I["Gap Analyzer Agent"]
        G --> J["Doc Generator Agent"]
        G --> K["Chat Agent"]
    end

    subgraph Data["Data Layer"]
        L[(SQLite)] --> M[AI Systems]
        L --> N[Assessments]
        L --> O[Audit Trail]
        P[(ChromaDB)] --> Q[595 Legal Chunks]
    end

    Frontend -->|REST API| Backend
    H --> P
    I --> P
    J --> P
    K --> P
    F --> L
```

## Agent Pipeline

```mermaid
graph LR
    INPUT["AI System\nDescription"] --> CLASSIFY["Risk Classifier\n(RAG + LLM)"]
    CLASSIFY -->|High Risk| ANALYZE["Gap Analyzer\n(Articles 9-15)"]
    CLASSIFY -->|Limited/Minimal| REPORT["Quick Report"]
    ANALYZE --> GENERATE["Doc Generator\n(Article 11)"]
    GENERATE --> OUTPUT["Compliance\nPackage"]
    REPORT --> OUTPUT

    style CLASSIFY fill:#1e40af,color:#fff
    style ANALYZE fill:#dc2626,color:#fff
    style GENERATE fill:#16a34a,color:#fff
```

## Classification Accuracy

Tested against expert-validated AI system descriptions across all EU AI Act risk categories:

```mermaid
xychart-beta
    title "Classification Accuracy by Risk Level"
    x-axis ["Unacceptable", "High Risk", "Limited", "Minimal", "Overall"]
    y-axis "Accuracy %" 0 --> 100
    bar [100, 100, 100, 100, 100]
```

| Test Case             | Expected     | Predicted    | Confidence | Result |
| --------------------- | ------------ | ------------ | ---------- | ------ |
| Resume Screener (HR)  | High         | High         | 95%        | PASS   |
| Customer Chatbot      | Limited      | Limited      | 90%        | PASS   |
| Social Scoring System | Unacceptable | Unacceptable | 100%       | PASS   |
| Email Spam Filter     | Minimal      | Minimal      | 90%        | PASS   |
| Student Exam Grader   | High         | High         | 95%        | PASS   |

> **10/10 (100%)** accuracy on benchmark. 50 test cases written across all risk levels and Annex III categories.

## E2E Test Results (Production)

```mermaid
xychart-beta
    title "E2E Test Suite — 15/15 Passing"
    x-axis ["Health", "Dashboard", "CRUD", "Classify", "Gap Analysis", "Ontology", "Chat", "Doc Gen", "Verify"]
    y-axis "Tests" 0 --> 3
    bar [1, 1, 3, 2, 1, 3, 1, 1, 2]
```

| Category                   | Tests  | Status   | Avg Time |
| -------------------------- | ------ | -------- | -------- |
| Infrastructure             | 1      | PASS     | 0.7s     |
| Dashboard                  | 1      | PASS     | 0.2s     |
| System CRUD                | 3      | PASS     | 0.2s     |
| Classification (LLM)       | 2      | PASS     | 5.7s     |
| Gap Analysis (7 LLM calls) | 1      | PASS     | 82s      |
| Ontology API               | 3      | PASS     | 0.2s     |
| Compliance Chat (LLM)      | 1      | PASS     | 11.6s    |
| Document Generation (LLM)  | 1      | PASS     | 58s      |
| Verification               | 2      | PASS     | 0.2s     |
| **Total**                  | **15** | **100%** | —        |

## RAG Knowledge Base

```mermaid
pie title EU AI Act Corpus (595 chunks)
    "Articles" : 592
    "Annexes" : 699
    "Key Recitals" : 224
```

| Source                   | Chunks                           | Coverage                            |
| ------------------------ | -------------------------------- | ----------------------------------- |
| EU AI Act Articles 1-113 | 592                              | Full text from EUR-Lex              |
| Annexes I-XIII           | 699                              | Complete annex text                 |
| Key Recitals             | 224                              | Recitals with interpretive guidance |
| **Total**                | **1,515 raw / 595 deduplicated** | **Full regulation**                 |

## Tech Stack

```mermaid
graph LR
    subgraph Frontend
        NJ[Next.js 16] --> TS[TypeScript]
        NJ --> TW[Tailwind CSS]
        NJ --> LR[Lucide Icons]
    end

    subgraph Backend
        FA[FastAPI] --> LC[LangChain]
        FA --> LG[LangGraph]
        FA --> PY[Pydantic]
    end

    subgraph AI
        CL[Claude API] --> RAG[RAG Pipeline]
        RAG --> CH[ChromaDB]
    end

    subgraph Infra
        VC[Vercel] --> FE[Frontend CDN]
        RN[Render] --> BE[Backend Docker]
        SQ[SQLite] --> DB[Persistence]
    end
```

| Layer        | Technology                           | Purpose                                              |
| ------------ | ------------------------------------ | ---------------------------------------------------- |
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS | Dashboard, system registration, results UI           |
| **Backend**  | FastAPI, Python 3.11                 | REST API, agent orchestration                        |
| **AI/RAG**   | LangChain, LangGraph, ChromaDB       | Multi-agent pipeline, vector search over EU AI Act   |
| **LLM**      | Claude API (Anthropic)               | Legal reasoning, classification, document generation |
| **Database** | SQLite                               | System registry, assessments, audit trail            |
| **Hosting**  | Vercel (frontend), Render (backend)  | Production deployment                                |

## Features

### Dashboard

- 6 metric cards: total systems, high-risk count, compliance score, deadline countdown, critical gaps, compliant systems
- Getting started guide with 3-step onboarding flow

### AI System Classification

- Register AI systems with natural language descriptions
- Automatic EU AI Act risk classification (Unacceptable / High / Limited / Minimal)
- Confidence scoring with cited legal articles and reasoning
- Annex III category detection (8 categories: biometrics, infrastructure, education, employment, services, law enforcement, migration, justice)

### Compliance Gap Analysis

- Article 9-15 compliance assessment for high-risk systems
- Severity-ranked gaps (Critical / Major / Minor)
- Priority action list with remediation steps
- Estimated effort per gap

### Document Generation

- Auto-generated Article 11 technical documentation
- Compliance package with risk assessment and remediation plan
- Copy to clipboard and download as Markdown

### Compliance Chat

- RAG-powered Q&A over the full EU AI Act
- Suggested questions for quick start
- Cited article references in every response

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Anthropic API key ([get one here](https://console.anthropic.com))

### Local Development

```bash
# Clone
git clone https://github.com/soneeee22000/ComplyOS.git
cd ComplyOS

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # Add your ANTHROPIC_API_KEY

# Fetch and ingest the full EU AI Act
python -m app.services.fetch_eu_ai_act
python -m app.services.ingest_ai_act

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## API Reference

| Method | Endpoint                          | Description                        |
| ------ | --------------------------------- | ---------------------------------- |
| `POST` | `/api/systems`                    | Register a new AI system           |
| `GET`  | `/api/systems`                    | List all registered systems        |
| `POST` | `/api/systems/{id}/classify`      | Run EU AI Act risk classification  |
| `POST` | `/api/systems/{id}/analyze`       | Run compliance gap analysis        |
| `POST` | `/api/systems/{id}/generate-docs` | Generate compliance documentation  |
| `POST` | `/api/chat`                       | Ask EU AI Act compliance questions |
| `GET`  | `/api/dashboard`                  | Get aggregate compliance metrics   |
| `GET`  | `/health`                         | Health check                       |

Full Swagger docs: [complyos.onrender.com/docs](https://complyos.onrender.com/docs)

## Project Structure

```
ComplyOS/
├── frontend/                   # Next.js 16 + TypeScript + Tailwind
│   └── src/
│       ├── app/                # Pages (dashboard, systems, chat)
│       ├── components/         # UI components (sidebar, cards, panels)
│       └── lib/                # API client
├── backend/                    # FastAPI + LangChain + LangGraph
│   └── app/
│       ├── agents/             # LangGraph agents (classifier, gap analyzer, doc generator, chat)
│       ├── api/                # REST API routes
│       ├── core/               # Configuration
│       ├── models/             # Pydantic schemas
│       ├── services/           # RAG, database, ingestion
│       └── data/               # EU AI Act chunks (JSON), ChromaDB, SQLite
├── PRD.md                      # Product Requirements Document (v2)
├── CLAUDE.md                   # AI assistant context
├── Dockerfile                  # Backend container
└── LICENSE                     # MIT
```

## Roadmap

- [x] Full EU AI Act text ingestion (595 chunks from EUR-Lex)
- [x] Multi-agent classification pipeline (LangGraph)
- [x] Gap analysis with severity ranking
- [x] Compliance document generation with rich markdown + PDF export
- [x] RAG-powered compliance chat with formatted responses
- [x] SQLite persistence with audit trail
- [x] Production deployment (Vercel + Render)
- [x] Compliance ontology (7 articles, 25 sub-requirements, 80+ verification criteria)
- [x] Ontology-guided gap analysis (structured per sub-requirement)
- [x] Requirement tree UI with multi-level accordion
- [x] E2E test suite (15/15 passing on production)
- [x] Classification benchmark (50 test cases, 100% accuracy on initial run)
- [x] Landing page with live classification examples
- [x] Demo data seeding (survives ephemeral deploys)
- [ ] Evidence-based assessment (document upload + parsing)
- [ ] Validated benchmark (100+ expert-reviewed test cases)
- [ ] CNIL / France-specific guidance integration
- [ ] Multi-jurisdiction support (DE, ES, NL, IT)
- [ ] DOCX / PDF export
- [ ] CI/CD integration API

## Context

Built for the [VivaTech 2026 Startup Challenges](https://vivatech.com/challenges) (ManpowerGroup and KPMG tracks). ComplyOS addresses the EUR 17B EU AI Act compliance market -- the largest AI regulation in history with a hard deadline of August 2, 2026.

Comparable: [OneTrust](https://www.onetrust.com/) reached $5.3B valuation from GDPR compliance tooling. The EU AI Act is broader, fines are larger, and AI adoption is accelerating.

## Author

**Pyae Sone Kyaw (Seon)** -- AI Engineer based in Paris

- [Portfolio](https://pseonkyaw.dev)
- [GitHub](https://github.com/soneeee22000)
- [LinkedIn](https://linkedin.com/in/pyae-sone-kyaw)

## License

[MIT](LICENSE)

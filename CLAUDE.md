# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComplyOS is an EU AI Act compliance platform that automates risk classification, gap analysis, and technical documentation generation for AI systems. Target users are CTOs, DPOs, and compliance teams deploying AI in the EU.

## Architecture

**Monorepo with two main applications:**

| Layer    | Technology                               | Hosting  |
| -------- | ---------------------------------------- | -------- |
| Frontend | Next.js 15 + TypeScript + Tailwind       | Vercel   |
| Backend  | FastAPI (Python)                         | Railway  |
| Database | Supabase (PostgreSQL + Auth + RLS)       | Supabase |
| AI/RAG   | LangChain + LangGraph + ChromaDB         | Railway  |
| LLM      | Claude API (primary), Mistral (fallback) | —        |

**Multi-agent pipeline (LangGraph):**

- **Risk Classifier Agent** — RAG over EU AI Act Articles 5, 6, Annex I/III to classify systems as Unacceptable/High/Limited/Minimal risk
- **Gap Analyzer Agent** — checks Article 9-15 compliance requirements, outputs severity-ranked gaps with remediation steps
- **Doc Generator Agent** — produces Article 11 technical documentation, risk management plans, conformity declarations (Markdown + PDF)

## Key Data Models

- **AISystem** — registered AI system with risk_level, annex_category, classification_reasoning, confidence_score
- **ComplianceAssessment** — per-system compliance status across Articles 9-15, gaps (JSONB), remediation_plan (JSONB), overall_score (0-100)
- **GeneratedDocument** — doc_type (technical_doc | risk_assessment | conformity_declaration), content, pdf_url

## API Endpoints

All endpoints require auth. Key routes:

- `POST /api/systems` — register AI system
- `POST /api/systems/{id}/classify` — run risk classification
- `POST /api/systems/{id}/analyze` — run gap analysis
- `POST /api/systems/{id}/generate-docs` — generate compliance docs
- `GET /api/dashboard` — aggregate compliance metrics
- `POST /api/chat` — compliance Q&A

## Domain Context

- EU AI Act compliance deadline: **August 2, 2026**
- 8 Annex III high-risk categories: biometrics, infrastructure, education, employment, services, law_enforcement, migration, justice
- RAG knowledge base covers all 113 articles + 13 annexes of the EU AI Act
- Every AI classification must include confidence scores and cited legal reasoning (no black-box outputs)
- No PII in the vector database — only regulatory text

## Testing Approach

- Unit tests: risk classification logic, gap analysis scoring, document templates, API validation
- Integration tests: full classification/analysis/docgen pipelines, Supabase CRUD
- E2E tests: register → classify → analyze → generate docs → download
- Do NOT test: Supabase Auth internals, LLM output word-for-word, PDF pixel-perfect rendering
- Test LLM outputs by validating structure and required fields only

## Build Commands

```bash
# Frontend
cd frontend && npm run dev        # Dev server on :3000
cd frontend && npm run build      # Production build
cd frontend && npm run lint       # ESLint

# Backend
cd backend && pip install -r requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000
cd backend && python -m app.services.ingest_ai_act   # Ingest EU AI Act
cd backend && pytest tests/
```

## Build Order (from PRD)

1. **Foundation** — scaffolding, EU AI Act ingestion into ChromaDB, Supabase schema, auth, CI
2. **Classification** — Risk Classifier agent, system registration UI, classification results UI, dashboard
3. **Gap Analysis + Doc Gen** — Gap Analyzer agent, compliance questionnaire, Doc Generator agent, PDF export
4. **Polish** — landing page, demo mode, mobile responsiveness, E2E tests, deploy

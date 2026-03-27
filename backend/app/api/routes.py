from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import verify_api_key

from app.models.schemas import (
    AISystemCreate,
    AISystemResponse,
    ChatMessage,
    ChatResponse,
    ClassificationResult,
    DashboardMetrics,
    DocumentGenerationRequest,
    GapAnalysisResult,
    GeneratedDocument,
)
from app.agents.classifier import classify_ai_system
from app.agents.gap_analyzer import analyze_gaps
from app.agents.doc_generator import generate_document
from app.agents.chat_agent import answer_compliance_question
from app.services.database import (
    create_system,
    list_systems,
    get_system,
    update_system,
    save_assessment,
    get_assessment,
    save_document,
    log_audit,
    get_dashboard_stats,
)

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _row_to_response(row: dict) -> AISystemResponse:
    """Convert a database row to an AISystemResponse."""
    return AISystemResponse(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        department=row["department"] or "",
        use_case=row["use_case"] or "",
        risk_level=row.get("risk_level"),
        annex_category=row.get("annex_category"),
        classification_reasoning=row.get("classification_reasoning"),
        confidence_score=row.get("confidence_score"),
        overall_compliance_score=row.get("overall_compliance_score"),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


@router.post("/systems", response_model=AISystemResponse)
async def register_system(system: AISystemCreate) -> AISystemResponse:
    """Register a new AI system for compliance assessment."""
    row = create_system(
        name=system.name,
        description=system.description,
        department=system.department,
        use_case=system.use_case,
    )
    log_audit(row["id"], "system_registered", f"Registered: {system.name}")
    return _row_to_response(row)


@router.get("/systems", response_model=list[AISystemResponse])
async def get_systems() -> list[AISystemResponse]:
    """List all registered AI systems."""
    return [_row_to_response(r) for r in list_systems()]


@router.get("/systems/{system_id}", response_model=AISystemResponse)
async def get_system_by_id(system_id: str) -> AISystemResponse:
    """Get a specific AI system by ID."""
    row = get_system(system_id)
    if not row:
        raise HTTPException(status_code=404, detail="System not found")
    return _row_to_response(row)


@router.post("/systems/{system_id}/classify", response_model=ClassificationResult)
async def classify_system(system_id: str) -> ClassificationResult:
    """Run EU AI Act risk classification on an AI system."""
    row = get_system(system_id)
    if not row:
        raise HTTPException(status_code=404, detail="System not found")

    result = await classify_ai_system(
        name=row["name"],
        description=row["description"],
        use_case=row["use_case"] or "",
    )

    update_system(
        system_id,
        risk_level=result.risk_level.value,
        annex_category=result.annex_category.value,
        classification_reasoning=result.reasoning,
        confidence_score=result.confidence_score,
    )

    log_audit(
        system_id,
        "system_classified",
        f"Risk: {result.risk_level.value}, Category: {result.annex_category.value}, Confidence: {result.confidence_score}",
    )

    return result


@router.post("/systems/{system_id}/analyze", response_model=GapAnalysisResult)
async def analyze_system(system_id: str) -> GapAnalysisResult:
    """Run compliance gap analysis on a classified AI system."""
    row = get_system(system_id)
    if not row:
        raise HTTPException(status_code=404, detail="System not found")

    if not row.get("risk_level"):
        raise HTTPException(
            status_code=400, detail="System must be classified before gap analysis"
        )

    result = await analyze_gaps(
        system_id=system_id,
        name=row["name"],
        description=row["description"],
        risk_level=row["risk_level"],
        annex_category=row["annex_category"] or "",
    )

    update_system(system_id, overall_compliance_score=result.overall_score)
    save_assessment(
        system_id=system_id,
        overall_score=result.overall_score,
        gaps=[g.model_dump() for g in result.gaps],
        summary=result.summary,
        priority_actions=result.priority_actions,
    )
    log_audit(system_id, "gap_analysis_completed", f"Score: {result.overall_score}%")

    return result


@router.post("/systems/{system_id}/generate-docs", response_model=GeneratedDocument)
async def generate_docs(
    system_id: str, request: DocumentGenerationRequest
) -> GeneratedDocument:
    """Generate compliance documentation for an AI system."""
    row = get_system(system_id)
    if not row:
        raise HTTPException(status_code=404, detail="System not found")

    assessment = get_assessment(system_id)
    if not assessment:
        raise HTTPException(
            status_code=400,
            detail="System must be analyzed before document generation",
        )

    content = await generate_document(
        system=row,
        assessment=assessment,
        doc_type=request.doc_type,
    )

    doc = save_document(system_id=system_id, doc_type=request.doc_type, content=content)
    log_audit(system_id, "document_generated", f"Type: {request.doc_type}")

    return GeneratedDocument(
        id=doc["id"],
        system_id=system_id,
        doc_type=request.doc_type,
        content=content,
        generated_at=datetime.fromisoformat(doc["generated_at"]),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage) -> ChatResponse:
    """Chat with the AI about EU AI Act compliance questions."""
    context = None
    if message.system_id:
        context = get_system(message.system_id)

    return await answer_compliance_question(
        question=message.message, system_context=context
    )


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard() -> DashboardMetrics:
    """Get aggregate compliance dashboard metrics."""
    deadline = date(2026, 8, 2)
    days_remaining = (deadline - date.today()).days

    stats = get_dashboard_stats()

    return DashboardMetrics(
        total_systems=stats["total_systems"],
        high_risk_count=stats["high_risk_count"],
        limited_risk_count=stats["limited_risk_count"],
        minimal_risk_count=stats["minimal_risk_count"],
        unclassified_count=stats["unclassified_count"],
        average_compliance_score=stats["average_compliance_score"],
        days_until_deadline=max(days_remaining, 0),
        critical_gaps_count=stats["critical_gaps_count"],
    )

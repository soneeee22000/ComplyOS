from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """EU AI Act risk classification levels."""

    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"


class AnnexCategory(str, Enum):
    """EU AI Act Annex III high-risk categories."""

    BIOMETRICS = "biometrics"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION = "migration"
    JUSTICE = "justice"
    NONE = "none"


class ComplianceStatus(str, Enum):
    """Status of a compliance requirement."""

    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"


class AISystemCreate(BaseModel):
    """Request body for registering a new AI system."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    department: str = Field(default="", max_length=200)
    use_case: str = Field(default="", max_length=500)


class AISystemResponse(BaseModel):
    """Response body for an AI system."""

    id: str
    name: str
    description: str
    department: str
    use_case: str
    risk_level: RiskLevel | None = None
    annex_category: AnnexCategory | None = None
    classification_reasoning: str | None = None
    confidence_score: float | None = None
    overall_compliance_score: int | None = None
    created_at: datetime
    updated_at: datetime


class ClassificationResult(BaseModel):
    """Result of AI system risk classification."""

    risk_level: RiskLevel
    annex_category: AnnexCategory
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    cited_articles: list[str]
    requires_compliance: bool


class ComplianceGap(BaseModel):
    """A single compliance gap identified during assessment."""

    requirement: str = ""
    article: str = ""
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    severity: str = "major"
    description: str = ""
    remediation: str = ""
    estimated_effort: str = ""


class GapAnalysisResult(BaseModel):
    """Result of compliance gap analysis."""

    system_id: str
    overall_score: int = Field(..., ge=0, le=100)
    gaps: list[ComplianceGap]
    summary: str
    priority_actions: list[str]


class DocumentGenerationRequest(BaseModel):
    """Request to generate compliance documentation."""

    system_id: str
    doc_type: str = Field(
        default="technical_documentation",
        pattern="^(technical_documentation|risk_assessment|conformity_declaration)$",
    )


class GeneratedDocument(BaseModel):
    """Generated compliance document."""

    id: str
    system_id: str
    doc_type: str
    content: str
    generated_at: datetime


class ChatMessage(BaseModel):
    """Chat message for compliance Q&A."""

    message: str = Field(..., min_length=1, max_length=2000)
    system_id: str | None = None


class ChatResponse(BaseModel):
    """Response from compliance chat."""

    answer: str
    cited_articles: list[str]
    confidence: float


class DashboardMetrics(BaseModel):
    """Aggregate dashboard metrics."""

    total_systems: int
    high_risk_count: int
    limited_risk_count: int
    minimal_risk_count: int
    unclassified_count: int
    average_compliance_score: float
    days_until_deadline: int
    critical_gaps_count: int

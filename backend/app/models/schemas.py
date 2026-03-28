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


# --- Enhanced Ontology-Aware Schemas ---


class SubRequirementStatus(BaseModel):
    """Status of a single sub-requirement from the ontology."""

    sub_requirement_id: str
    paragraph: str
    title: str
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    severity: str = "major"
    finding: str = ""
    remediation: str = ""
    estimated_effort: str = ""
    evidence_required: list[str] = Field(default_factory=list)


class ArticleStatus(BaseModel):
    """Compliance status of an entire article, aggregated from sub-requirements."""

    article_id: str
    article_title: str
    article_status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    sub_requirement_statuses: list[SubRequirementStatus] = Field(default_factory=list)


class CrossReferenceFinding(BaseModel):
    """A finding related to cross-references between articles."""

    source_article: str
    target_article: str
    relationship: str
    finding: str


class EnhancedGapAnalysisResult(BaseModel):
    """Ontology-aware gap analysis result with sub-requirement-level detail."""

    system_id: str
    overall_score: int = Field(..., ge=0, le=100)
    summary: str
    priority_actions: list[str]
    requirement_statuses: list[ArticleStatus]
    cross_reference_findings: list[CrossReferenceFinding] = Field(default_factory=list)


class RequirementTreeResponse(BaseModel):
    """Full requirement tree from the ontology for a given risk level."""

    risk_level: str
    annex_category: str | None = None
    total_articles: int
    total_sub_requirements: int
    articles: list[dict]

"""Gap Analyzer Agent — ontology-guided compliance assessment.

v2: Uses the compliance ontology to structure the analysis. Instead of asking
the LLM to invent the compliance framework, we provide the exact sub-requirements
and verification criteria from the ontology. The LLM only fills in the assessment.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings
from app.models.schemas import (
    ArticleStatus,
    ComplianceStatus,
    CrossReferenceFinding,
    EnhancedGapAnalysisResult,
    GapAnalysisResult,
    ComplianceGap,
    SubRequirementStatus,
)
from app.ontology import Article
from app.ontology.eu_ai_act import EU_AI_ACT_ONTOLOGY
from app.services.rag import query_ai_act

ARTICLE_ASSESSMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert EU AI Act compliance auditor. You are assessing a specific
article's requirements against an AI system description.

For EACH sub-requirement listed below, provide a status assessment based ONLY on
what can be determined from the system description. If the organization has not
provided evidence of compliance, assume non-compliance.

Regulatory context:
{regulatory_context}

Respond in JSON with this exact structure:
{{
  "sub_requirements": [
    {{
      "sub_requirement_id": "the id provided",
      "status": "compliant" | "partial" | "non_compliant" | "not_assessed",
      "severity": "critical" | "major" | "minor",
      "finding": "specific finding about this sub-requirement",
      "remediation": "concrete steps to achieve compliance",
      "estimated_effort": "days" | "weeks" | "months"
    }}
  ]
}}""",
        ),
        (
            "human",
            """Assess this AI system against {article_title} ({article_ref}):

System Name: {name}
System Description: {description}
Risk Level: {risk_level}
Annex Category: {annex_category}

Sub-requirements to assess:
{sub_requirements_text}

Provide your assessment as JSON.""",
        ),
    ]
)

SEVERITY_WEIGHTS = {"critical": 0, "major": 0.3, "minor": 0.7}
STATUS_SCORES = {"compliant": 1.0, "partial": 0.5, "non_compliant": 0.0, "not_assessed": 0.0}


def _format_sub_requirements(article: Article) -> str:
    """Format an article's sub-requirements for the LLM prompt."""
    lines = []
    for sr in article.sub_requirements:
        lines.append(f"\n{sr.paragraph} — {sr.title}")
        lines.append(f"  ID: {sr.id}")
        lines.append(f"  Description: {sr.description}")
        if sr.verification_criteria:
            lines.append(f"  Evidence needed:")
            for vc in sr.verification_criteria:
                lines.append(f"    - {vc}")
        if sr.cross_references:
            for xr in sr.cross_references:
                lines.append(f"  Note: Cross-references {xr.target_article} ({xr.description})")
    return "\n".join(lines)


def _derive_article_status(sub_statuses: list[SubRequirementStatus]) -> ComplianceStatus:
    """Derive the overall article status from its sub-requirement statuses (worst wins)."""
    priority = [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL, ComplianceStatus.NOT_ASSESSED, ComplianceStatus.COMPLIANT]
    for status in priority:
        if any(s.status == status for s in sub_statuses):
            return status
    return ComplianceStatus.NOT_ASSESSED


def _compute_overall_score(article_statuses: list[ArticleStatus]) -> int:
    """Compute overall compliance score from article statuses (0-100)."""
    total_weight = 0.0
    total_score = 0.0

    for art_status in article_statuses:
        for sub in art_status.sub_requirement_statuses:
            weight = 1.0 - SEVERITY_WEIGHTS.get(sub.severity, 0.3)
            score = STATUS_SCORES.get(sub.status.value if hasattr(sub.status, "value") else sub.status, 0.0)
            total_weight += weight
            total_score += weight * score

    if total_weight == 0:
        return 0
    return int((total_score / total_weight) * 100)


def _derive_priority_actions(article_statuses: list[ArticleStatus]) -> list[str]:
    """Extract top priority actions from critical and major findings."""
    actions = []
    for art_status in article_statuses:
        for sub in art_status.sub_requirement_statuses:
            if sub.severity == "critical" and sub.status != ComplianceStatus.COMPLIANT:
                actions.append(f"[{sub.paragraph}] {sub.remediation}")
    for art_status in article_statuses:
        for sub in art_status.sub_requirement_statuses:
            if sub.severity == "major" and sub.status != ComplianceStatus.COMPLIANT:
                actions.append(f"[{sub.paragraph}] {sub.remediation}")
    return actions[:5]


async def _assess_article(
    article: Article,
    name: str,
    description: str,
    risk_level: str,
    annex_category: str,
) -> ArticleStatus:
    """Assess a single article's sub-requirements against an AI system.

    One LLM call per article, structured by the ontology.
    """
    regulatory_context = await query_ai_act(
        f"EU AI Act {article.title} Article {article.number} requirements obligations"
    )

    sub_req_text = _format_sub_requirements(article)

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=settings.anthropic_api_key,
        temperature=0.0,
        max_tokens=3000,
    )

    chain = ARTICLE_ASSESSMENT_PROMPT | llm | JsonOutputParser()

    try:
        result = await chain.ainvoke({
            "article_title": article.title,
            "article_ref": f"Article {article.number}",
            "name": name,
            "description": description,
            "risk_level": risk_level,
            "annex_category": annex_category,
            "sub_requirements_text": sub_req_text,
            "regulatory_context": regulatory_context,
        })
    except Exception:
        return _default_article_status(article)

    sub_statuses = []
    result_subs = result.get("sub_requirements", [])
    result_map = {s.get("sub_requirement_id", ""): s for s in result_subs}

    for sr in article.sub_requirements:
        llm_sub = result_map.get(sr.id, {})
        status_str = llm_sub.get("status", "not_assessed")
        try:
            status = ComplianceStatus(status_str)
        except ValueError:
            status = ComplianceStatus.NOT_ASSESSED

        sub_statuses.append(SubRequirementStatus(
            sub_requirement_id=sr.id,
            paragraph=sr.paragraph,
            title=sr.title,
            status=status,
            severity=llm_sub.get("severity", "major"),
            finding=llm_sub.get("finding", ""),
            remediation=llm_sub.get("remediation", ""),
            estimated_effort=llm_sub.get("estimated_effort", ""),
            evidence_required=sr.verification_criteria,
        ))

    return ArticleStatus(
        article_id=article.id,
        article_title=article.title,
        article_status=_derive_article_status(sub_statuses),
        sub_requirement_statuses=sub_statuses,
    )


def _default_article_status(article: Article) -> ArticleStatus:
    """Return a default NOT_ASSESSED status for an article (fallback on LLM error)."""
    return ArticleStatus(
        article_id=article.id,
        article_title=article.title,
        article_status=ComplianceStatus.NOT_ASSESSED,
        sub_requirement_statuses=[
            SubRequirementStatus(
                sub_requirement_id=sr.id,
                paragraph=sr.paragraph,
                title=sr.title,
                status=ComplianceStatus.NOT_ASSESSED,
                severity="major",
                finding="Assessment could not be completed",
                evidence_required=sr.verification_criteria,
            )
            for sr in article.sub_requirements
        ],
    )


async def analyze_gaps(
    system_id: str,
    name: str,
    description: str,
    risk_level: str,
    annex_category: str,
) -> EnhancedGapAnalysisResult:
    """Analyze compliance gaps using ontology-guided structured prompting.

    One LLM call per applicable article (7 for high-risk), each structured
    by the ontology's sub-requirements and verification criteria.
    """
    applicable_articles = EU_AI_ACT_ONTOLOGY.get_requirements_for_risk_level(risk_level)

    article_statuses = []
    for article in applicable_articles:
        status = await _assess_article(article, name, description, risk_level, annex_category)
        article_statuses.append(status)

    overall_score = _compute_overall_score(article_statuses)
    priority_actions = _derive_priority_actions(article_statuses)

    non_compliant_count = sum(
        1 for a in article_statuses
        for s in a.sub_requirement_statuses
        if s.status == ComplianceStatus.NON_COMPLIANT
    )
    total_count = sum(len(a.sub_requirement_statuses) for a in article_statuses)

    summary = (
        f"Assessed {total_count} sub-requirements across {len(applicable_articles)} articles. "
        f"{non_compliant_count} non-compliant findings. "
        f"Overall compliance score: {overall_score}%."
    )

    return EnhancedGapAnalysisResult(
        system_id=system_id,
        overall_score=overall_score,
        summary=summary,
        priority_actions=priority_actions,
        requirement_statuses=article_statuses,
        cross_reference_findings=[],
    )

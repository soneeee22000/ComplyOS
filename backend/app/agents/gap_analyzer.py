"""Gap Analyzer Agent — identifies compliance gaps for high-risk AI systems."""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings
from app.models.schemas import GapAnalysisResult, ComplianceGap
from app.services.rag import query_ai_act

GAP_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert EU AI Act compliance auditor. Analyze an AI system's
compliance status against all required obligations.

For HIGH-RISK AI systems, assess these requirements:
1. Risk Management System (Article 9)
2. Data and Data Governance (Article 10)
3. Technical Documentation (Article 11)
4. Record-Keeping / Logging (Article 12)
5. Transparency and Information to Deployers (Article 13)
6. Human Oversight (Article 14)
7. Accuracy, Robustness and Cybersecurity (Article 15)

For each requirement, assess:
- status: "compliant", "partial", "non_compliant", or "not_assessed"
- severity: "critical" (blocks compliance), "major" (significant gap), "minor" (improvement needed)
- description: what specifically is missing or inadequate
- remediation: concrete steps to achieve compliance
- estimated_effort: "days", "weeks", or "months"

Use the following regulatory context:
{regulatory_context}

Respond in JSON with:
- system_id: the provided system ID
- overall_score: 0-100 compliance score
- gaps: array of gap objects
- summary: brief overall assessment
- priority_actions: top 3-5 most urgent actions""",
        ),
        (
            "human",
            """Analyze compliance for this AI system:

System ID: {system_id}
Name: {name}
Description: {description}
Risk Level: {risk_level}
Annex Category: {annex_category}

Based on the description alone (no additional documentation has been provided),
identify what compliance gaps likely exist. Assume the organization has NOT yet
begun formal EU AI Act compliance work.

Provide your analysis as JSON.""",
        ),
    ]
)


async def analyze_gaps(
    system_id: str,
    name: str,
    description: str,
    risk_level: str,
    annex_category: str,
) -> GapAnalysisResult:
    """Analyze compliance gaps for an AI system.

    Args:
        system_id: Unique identifier for the system.
        name: Name of the AI system.
        description: Description of what the system does.
        risk_level: EU AI Act risk classification.
        annex_category: Applicable Annex III category.

    Returns:
        GapAnalysisResult with identified gaps and remediation plan.
    """
    regulatory_context = await query_ai_act(
        f"EU AI Act requirements obligations high-risk AI system "
        f"{annex_category} Article 9 10 11 12 13 14 15"
    )

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=settings.anthropic_api_key,
        temperature=0.0,
        max_tokens=4000,
    )

    parser = JsonOutputParser(pydantic_object=GapAnalysisResult)
    chain = GAP_ANALYSIS_PROMPT | llm | parser

    result = await chain.ainvoke(
        {
            "system_id": system_id,
            "name": name,
            "description": description,
            "risk_level": risk_level,
            "annex_category": annex_category,
            "regulatory_context": regulatory_context,
        }
    )

    gaps = [ComplianceGap(**g) for g in result.get("gaps", [])]

    return GapAnalysisResult(
        system_id=system_id,
        overall_score=result.get("overall_score", 0),
        gaps=gaps,
        summary=result.get("summary", ""),
        priority_actions=result.get("priority_actions", []),
    )

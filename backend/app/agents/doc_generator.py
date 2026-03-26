"""Document Generator Agent — generates EU AI Act compliance documentation."""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.services.rag import query_ai_act

DOC_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert EU AI Act compliance documentation specialist.
Generate professional compliance documentation following EU AI Act Article 11
and Annex IV requirements.

The documentation must include:
1. General description of the AI system
2. Detailed description of elements and development process
3. Information about monitoring, functioning and control
4. Description of the risk management system
5. Data governance measures
6. Human oversight measures
7. Accuracy and robustness specifications
8. Description of any changes made during lifecycle

Use the following regulatory context for accurate requirements:
{regulatory_context}

Generate the document in professional Markdown format suitable for regulatory submission.
Include section headers, clear structure, and placeholder notes where the organization
needs to fill in specific technical details.""",
        ),
        (
            "human",
            """Generate a {doc_type} document for this AI system:

System Name: {name}
Description: {description}
Risk Level: {risk_level}
Annex Category: {annex_category}
Compliance Score: {compliance_score}

Gap Analysis Summary: {gap_summary}

Identified Gaps:
{gaps_text}

Generate a complete, professional {doc_type} document in Markdown format.""",
        ),
    ]
)


async def generate_document(
    system: dict, assessment: dict, doc_type: str
) -> str:
    """Generate compliance documentation for an AI system.

    Args:
        system: AI system record.
        assessment: Gap analysis assessment.
        doc_type: Type of document to generate.

    Returns:
        Generated document content as Markdown string.
    """
    regulatory_context = await query_ai_act(
        f"EU AI Act Article 11 Annex IV technical documentation requirements "
        f"{doc_type} high-risk AI system"
    )

    gaps_text = "\n".join(
        f"- [{g.get('severity', 'unknown').upper()}] {g.get('requirement', '')}: "
        f"{g.get('description', '')}"
        for g in assessment.get("gaps", [])
    )

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=settings.anthropic_api_key,
        temperature=0.1,
        max_tokens=8000,
    )

    chain = DOC_GENERATION_PROMPT | llm

    result = await chain.ainvoke(
        {
            "doc_type": doc_type.replace("_", " ").title(),
            "name": system.get("name", ""),
            "description": system.get("description", ""),
            "risk_level": system.get("risk_level", ""),
            "annex_category": system.get("annex_category", ""),
            "compliance_score": assessment.get("overall_score", 0),
            "gap_summary": assessment.get("summary", ""),
            "gaps_text": gaps_text or "No gaps identified.",
            "regulatory_context": regulatory_context,
        }
    )

    return result.content

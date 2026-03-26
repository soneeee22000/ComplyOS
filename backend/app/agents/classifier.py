"""Risk Classifier Agent — classifies AI systems per EU AI Act."""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings
from app.models.schemas import ClassificationResult, RiskLevel, AnnexCategory
from app.services.rag import query_ai_act

CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert EU AI Act compliance classifier. Your job is to classify
AI systems according to the EU AI Act risk framework.

Risk levels:
- UNACCEPTABLE (Article 5): Social scoring, real-time biometric surveillance, manipulation
- HIGH (Article 6 + Annex III): Biometrics, critical infrastructure, education, employment,
  essential services, law enforcement, migration, justice
- LIMITED (Article 50): Systems with transparency obligations (chatbots, deepfakes, emotion recognition)
- MINIMAL: All other AI systems with no specific obligations

Annex III High-Risk Categories:
1. biometrics - Biometric identification and categorisation
2. critical_infrastructure - Management and operation of critical infrastructure
3. education - Education and vocational training
4. employment - Employment, workers management, access to self-employment
5. essential_services - Access to essential private/public services and benefits
6. law_enforcement - Law enforcement
7. migration - Migration, asylum and border control management
8. justice - Administration of justice and democratic processes

Use the following regulatory context to inform your classification:
{regulatory_context}

Respond in JSON with exactly these fields:
- risk_level: one of "unacceptable", "high", "limited", "minimal"
- annex_category: one of the categories above, or "none" if not high-risk
- confidence_score: float between 0.0 and 1.0
- reasoning: detailed explanation of why this classification applies
- cited_articles: list of specific EU AI Act articles that support this classification
- requires_compliance: boolean, true if high-risk or above""",
        ),
        (
            "human",
            """Classify this AI system:

Name: {name}
Description: {description}
Use Case: {use_case}

Provide your classification as JSON.""",
        ),
    ]
)


async def classify_ai_system(
    name: str, description: str, use_case: str
) -> ClassificationResult:
    """Classify an AI system according to EU AI Act risk levels.

    Args:
        name: Name of the AI system.
        description: Description of what the system does.
        use_case: How the system is used.

    Returns:
        ClassificationResult with risk level, category, and reasoning.
    """
    regulatory_context = await query_ai_act(
        f"AI system classification risk level: {description} {use_case}"
    )

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=settings.anthropic_api_key,
        temperature=0.0,
        max_tokens=2000,
    )

    parser = JsonOutputParser(pydantic_object=ClassificationResult)

    chain = CLASSIFICATION_PROMPT | llm | parser

    result = await chain.ainvoke(
        {
            "name": name,
            "description": description,
            "use_case": use_case,
            "regulatory_context": regulatory_context,
        }
    )

    return ClassificationResult(
        risk_level=RiskLevel(result["risk_level"]),
        annex_category=AnnexCategory(result["annex_category"]),
        confidence_score=result["confidence_score"],
        reasoning=result["reasoning"],
        cited_articles=result["cited_articles"],
        requires_compliance=result["requires_compliance"],
    )

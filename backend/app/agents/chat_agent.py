"""Chat Agent — answers EU AI Act compliance questions using RAG."""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.models.schemas import ChatResponse
from app.services.rag import query_ai_act

CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are ComplyOS, an expert AI assistant for EU AI Act compliance.
Answer questions accurately based on the EU AI Act regulatory text.

Always:
- Cite specific articles and annexes
- Be precise about obligations, deadlines, and penalties
- Distinguish between what is required vs recommended
- Note when something is ambiguous or subject to interpretation

Regulatory context from the EU AI Act:
{regulatory_context}

{system_context}""",
        ),
        ("human", "{question}"),
    ]
)


async def answer_compliance_question(
    question: str, system_context: dict | None = None
) -> ChatResponse:
    """Answer a compliance question using RAG over the EU AI Act.

    Args:
        question: The user's compliance question.
        system_context: Optional context about a specific AI system.

    Returns:
        ChatResponse with answer, cited articles, and confidence.
    """
    regulatory_context = await query_ai_act(question)

    context_str = ""
    if system_context:
        context_str = (
            f"\nThe user is asking about this specific AI system:\n"
            f"Name: {system_context.get('name', '')}\n"
            f"Description: {system_context.get('description', '')}\n"
            f"Risk Level: {system_context.get('risk_level', 'Not classified')}\n"
        )

    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=settings.anthropic_api_key,
        temperature=0.1,
        max_tokens=2000,
    )

    chain = CHAT_PROMPT | llm

    result = await chain.ainvoke(
        {
            "question": question,
            "regulatory_context": regulatory_context,
            "system_context": context_str,
        }
    )

    content = result.content
    cited = []
    for word in content.split():
        if word.startswith("Article") or word.startswith("Annex"):
            cited.append(word.rstrip(".,;:)"))

    return ChatResponse(
        answer=content,
        cited_articles=list(set(cited))[:10],
        confidence=0.85,
    )

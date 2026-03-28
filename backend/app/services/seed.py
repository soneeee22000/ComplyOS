"""Seed demo data — runs on app startup if database is empty.

Pre-classified demo systems so the dashboard always has data,
even after Render ephemeral filesystem wipes.
"""

from app.services.database import create_system, list_systems, update_system

DEMO_SYSTEMS = [
    {
        "name": "AI Resume Screener",
        "description": "Machine learning system that automatically screens job applications, parses resumes using NLP, ranks candidates based on skills matching algorithms, and filters out applicants who do not meet minimum qualifications for open positions.",
        "department": "Human Resources",
        "use_case": "Candidate screening and ranking for recruitment",
        "risk_level": "high",
        "annex_category": "employment",
        "classification_reasoning": "This AI system falls under Annex III, category 4 (Employment, workers management and access to self-employment). It is specifically designed for recruitment, selection, screening, filtering, and evaluation of candidates — all explicitly listed as high-risk use cases under the EU AI Act.",
        "confidence_score": 0.95,
    },
    {
        "name": "Customer Support Chatbot",
        "description": "AI-powered conversational chatbot deployed on company website that answers customer questions about products, services, and billing. Uses natural language understanding to route complex queries to human agents.",
        "department": "Customer Success",
        "use_case": "Automated customer support and FAQ handling",
        "risk_level": "limited",
        "annex_category": "none",
        "classification_reasoning": "This system falls under limited risk (Article 50) as it is an AI system intended to interact directly with natural persons. It requires transparency obligations — users must be informed they are interacting with an AI system.",
        "confidence_score": 0.90,
    },
    {
        "name": "Credit Scoring Model",
        "description": "AI system that evaluates loan applications and determines creditworthiness of individuals based on financial history, income data, employment records, and behavioral patterns to automate lending decisions.",
        "department": "Risk & Compliance",
        "use_case": "Automated credit assessment and lending decisions",
        "risk_level": "high",
        "annex_category": "essential_services",
        "classification_reasoning": "This system is classified as high-risk under Annex III, category 5 (Access to essential private services and benefits). AI systems used for creditworthiness assessment and risk evaluation for insurance are explicitly listed as high-risk.",
        "confidence_score": 0.95,
    },
    {
        "name": "Email Spam Filter",
        "description": "AI-based email filtering system that classifies incoming emails as spam or legitimate using pattern recognition and content analysis. Operates on email metadata and body text.",
        "department": "IT Infrastructure",
        "use_case": "Automated email spam detection",
        "risk_level": "minimal",
        "annex_category": "none",
        "classification_reasoning": "This system has minimal risk with no specific obligations under the EU AI Act. Email spam filtering does not fall under any prohibited, high-risk, or limited-risk categories.",
        "confidence_score": 0.90,
    },
    {
        "name": "Student Performance Predictor",
        "description": "AI system used by universities to predict student academic performance, identify at-risk students, and determine eligibility for academic programs based on historical grades, attendance, and engagement data.",
        "department": "Academic Affairs",
        "use_case": "Student assessment and academic program admission",
        "risk_level": "high",
        "annex_category": "education",
        "classification_reasoning": "This system is classified as high-risk under Annex III, category 3 (Education and vocational training). AI systems intended to determine access or admission to educational institutions and to assess students are explicitly high-risk.",
        "confidence_score": 0.95,
    },
]


def seed_demo_data() -> int:
    """Seed demo systems if the database is empty.

    Returns the number of systems seeded (0 if data already exists).
    """
    existing = list_systems()
    if existing:
        return 0

    count = 0
    for demo in DEMO_SYSTEMS:
        system = create_system(
            name=demo["name"],
            description=demo["description"],
            department=demo["department"],
            use_case=demo["use_case"],
        )
        update_system(
            system["id"],
            risk_level=demo["risk_level"],
            annex_category=demo["annex_category"],
            classification_reasoning=demo["classification_reasoning"],
            confidence_score=demo["confidence_score"],
        )
        count += 1

    return count

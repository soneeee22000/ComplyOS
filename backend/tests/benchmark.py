"""Classification accuracy benchmark — 50+ test cases across all EU AI Act risk levels.

Run: python -m tests.benchmark
      python -m tests.benchmark --quick    (first 10 only)
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass

from app.agents.classifier import classify_ai_system

@dataclass
class TestCase:
    """A single benchmark test case."""

    name: str
    description: str
    use_case: str
    expected_risk: str
    expected_category: str


BENCHMARK_CASES: list[TestCase] = [
    # === UNACCEPTABLE (Article 5) ===
    TestCase("Social Credit Scoring", "Government AI system that assigns citizens a trustworthiness score based on social behavior, online activity, and financial records to determine access to public services.", "Citizen social scoring", "unacceptable", "none"),
    TestCase("Subliminal Manipulation Engine", "AI system that deploys subliminal visual and audio techniques in advertising to manipulate consumer purchasing decisions without their awareness.", "Subliminal consumer manipulation", "unacceptable", "none"),
    TestCase("Real-Time Biometric Surveillance", "City-wide facial recognition system deployed in public spaces for real-time remote biometric identification of all pedestrians for law enforcement monitoring.", "Mass public surveillance", "unacceptable", "none"),
    TestCase("Vulnerability Exploitation Tool", "AI system designed to exploit psychological vulnerabilities of elderly people to influence their financial decisions and direct them toward specific products.", "Elderly financial manipulation", "unacceptable", "none"),

    # === HIGH RISK — Employment (Annex III, Category 4) ===
    TestCase("AI Resume Screener", "Machine learning system that automatically screens job applications, parses resumes using NLP, ranks candidates based on skills matching, and filters out applicants.", "Candidate screening and ranking", "high", "employment"),
    TestCase("Employee Performance Monitor", "AI system that continuously monitors employee productivity, tracks keystrokes, screen activity, and communication patterns to evaluate work performance.", "Employee performance evaluation", "high", "employment"),
    TestCase("AI Interview Analyzer", "System that analyzes video interviews using facial expression recognition, voice tone analysis, and NLP to score candidate suitability.", "Automated interview assessment", "high", "employment"),
    TestCase("Workforce Allocation AI", "AI system that assigns shifts, tasks, and workloads to employees based on behavioral patterns, past performance metrics, and predicted productivity.", "Task allocation based on behavior", "high", "employment"),
    TestCase("Promotion Decision Engine", "AI that recommends which employees should be promoted based on performance data, peer reviews, and predicted future contributions.", "Promotion and advancement decisions", "high", "employment"),
    TestCase("Layoff Risk Predictor", "AI system that identifies employees most likely to be laid off based on role redundancy analysis, performance trends, and cost optimization models.", "Workforce reduction decisions", "high", "employment"),

    # === HIGH RISK — Education (Annex III, Category 3) ===
    TestCase("Student Exam Grader", "AI system that grades student essays and exams, determining pass/fail outcomes and final grades for university courses.", "Automated student assessment", "high", "education"),
    TestCase("University Admissions AI", "System that evaluates and ranks university applications, determining which students are admitted based on grades, essays, and extracurriculars.", "Admission decision making", "high", "education"),
    TestCase("Learning Disability Detector", "AI system used in schools to identify students with potential learning disabilities and recommend placement in special education programs.", "Student classification and placement", "high", "education"),
    TestCase("Scholarship Allocation AI", "AI system that determines which students receive scholarships based on academic performance, financial need assessment, and predicted future success.", "Scholarship eligibility decisions", "high", "education"),

    # === HIGH RISK — Essential Services (Annex III, Category 5) ===
    TestCase("Credit Scoring Model", "AI system that evaluates loan applications and determines creditworthiness based on financial history, income data, and behavioral patterns.", "Automated credit assessment", "high", "essential_services"),
    TestCase("Insurance Risk Calculator", "AI that assesses insurance applications, calculating premiums and determining coverage eligibility based on health data and risk profiling.", "Insurance risk assessment", "high", "essential_services"),
    TestCase("Emergency Dispatch Prioritizer", "AI system that prioritizes emergency calls and dispatches first responders based on assessed severity, location data, and available resources.", "Emergency services dispatching", "high", "essential_services"),
    TestCase("Benefits Eligibility Checker", "Government AI system that evaluates citizen applications for social welfare benefits, determining eligibility and benefit amounts.", "Public benefits assessment", "high", "essential_services"),
    TestCase("Mortgage Approval AI", "AI system that makes automated decisions on mortgage applications, assessing property values, borrower risk, and loan terms.", "Automated mortgage decisions", "high", "essential_services"),

    # === HIGH RISK — Biometrics (Annex III, Category 1) ===
    TestCase("Airport Facial Recognition", "Biometric identification system at airport security checkpoints that verifies passenger identity by matching faces against passport databases.", "Passenger identity verification", "high", "biometrics"),
    TestCase("Emotion Detection in Workplace", "AI system that analyzes employee facial expressions during meetings to detect stress, engagement, and satisfaction levels.", "Workplace emotion recognition", "high", "biometrics"),
    TestCase("Biometric Access Control", "AI-powered system that uses fingerprint and iris scanning to control access to secure government facilities.", "Biometric facility access", "high", "biometrics"),

    # === HIGH RISK — Critical Infrastructure (Annex III, Category 2) ===
    TestCase("Power Grid Load Balancer", "AI system that manages electricity distribution across the national grid, making real-time decisions about power routing and load balancing.", "Critical infrastructure management", "high", "critical_infrastructure"),
    TestCase("Water Treatment Controller", "AI that controls water treatment plant operations, adjusting chemical dosing and filtration parameters in real-time.", "Water supply safety component", "high", "critical_infrastructure"),
    TestCase("Traffic Management AI", "AI system controlling city traffic signals, managing road traffic flow, and making real-time routing decisions for the entire transportation network.", "Road traffic management", "high", "critical_infrastructure"),

    # === HIGH RISK — Law Enforcement (Annex III, Category 6) ===
    TestCase("Predictive Policing System", "AI system that predicts crime hotspots and identifies individuals likely to commit offenses based on historical crime data and behavioral patterns.", "Crime prediction and risk profiling", "high", "law_enforcement"),
    TestCase("Evidence Analysis AI", "AI system used by prosecutors to analyze digital evidence, identify patterns in communications, and assess the reliability of witness statements.", "Criminal evidence evaluation", "high", "law_enforcement"),
    TestCase("Recidivism Risk Scorer", "AI that assesses the likelihood of convicted individuals reoffending, used by parole boards to inform release decisions.", "Criminal risk assessment", "high", "law_enforcement"),

    # === HIGH RISK — Migration (Annex III, Category 7) ===
    TestCase("Visa Application Screener", "AI system that evaluates visa and asylum applications, assessing risk profiles of applicants and recommending approval or rejection.", "Immigration risk assessment", "high", "migration"),
    TestCase("Border Document Verifier", "AI system at border crossings that analyzes travel documents for authenticity, detecting forged or altered passports and visas.", "Travel document fraud detection", "high", "migration"),

    # === HIGH RISK — Justice (Annex III, Category 8) ===
    TestCase("Legal Case Outcome Predictor", "AI system used by courts to predict case outcomes and recommend sentencing ranges based on case facts, precedents, and defendant profiles.", "Judicial decision support", "high", "justice"),
    TestCase("Dispute Resolution AI", "AI system that analyzes legal disputes and recommends settlements or rulings, used by arbitration panels for commercial cases.", "Automated legal reasoning", "high", "justice"),

    # === LIMITED RISK (Article 50) ===
    TestCase("Customer Service Chatbot", "AI chatbot on a company website that answers customer questions about products and services. Interacts directly with users via text.", "Customer support automation", "limited", "none"),
    TestCase("AI Content Generator", "System that generates marketing copy, blog posts, and social media content using large language models.", "Synthetic text generation", "limited", "none"),
    TestCase("Deepfake Detection Tool", "AI system that generates synthetic video content for entertainment, creating realistic but artificial video of fictional characters.", "Synthetic video generation", "limited", "none"),
    TestCase("Voice Assistant", "AI-powered voice assistant integrated into smart home devices that responds to voice commands and controls home appliances.", "Voice-based AI interaction", "limited", "none"),
    TestCase("AI Translation Service", "Real-time language translation service that translates spoken conversations between two people in different languages.", "AI-mediated communication", "limited", "none"),

    # === MINIMAL RISK ===
    TestCase("Email Spam Filter", "AI email spam filter that classifies incoming emails as spam or legitimate based on content analysis and sender reputation.", "Email classification", "minimal", "none"),
    TestCase("Product Recommendation Engine", "AI system on e-commerce site that suggests products based on browsing history and purchase patterns.", "Personalized shopping recommendations", "minimal", "none"),
    TestCase("Music Playlist Generator", "AI that creates personalized music playlists based on listening history and mood preferences.", "Entertainment personalization", "minimal", "none"),
    TestCase("Inventory Forecasting", "AI system that predicts product demand and optimizes warehouse inventory levels based on historical sales data.", "Supply chain optimization", "minimal", "none"),
    TestCase("Autocomplete Search", "AI-powered search autocomplete that suggests search queries as users type in a search box.", "Search suggestion", "minimal", "none"),
    TestCase("Photo Enhancement AI", "AI that automatically enhances photo quality, adjusting brightness, contrast, and sharpness for uploaded images.", "Image quality improvement", "minimal", "none"),
    TestCase("Code Completion Tool", "AI-powered IDE extension that suggests code completions and generates code snippets based on developer context.", "Developer productivity tool", "minimal", "none"),
    TestCase("Weather Prediction Model", "AI system that predicts weather patterns and generates forecasts based on atmospheric data and satellite imagery.", "Weather forecasting", "minimal", "none"),
    TestCase("Document OCR System", "AI that extracts text from scanned documents and images using optical character recognition.", "Document digitization", "minimal", "none"),
    TestCase("Fitness Tracker AI", "Wearable AI that tracks exercise routines, counts steps, and provides personalized fitness recommendations.", "Personal health tracking", "minimal", "none"),
    TestCase("Price Optimization AI", "AI system for an online retailer that dynamically adjusts product prices based on demand, competitor pricing, and inventory levels.", "Dynamic pricing optimization", "minimal", "none"),
    TestCase("Meeting Transcription AI", "AI that transcribes and summarizes meeting recordings, identifying action items and key decisions from audio.", "Meeting productivity tool", "minimal", "none"),
    TestCase("Fraud Detection System", "AI system used by banks to flag potentially fraudulent credit card transactions in real-time based on spending pattern anomalies.", "Financial fraud detection", "minimal", "none"),
]


async def run_benchmark(quick: bool = False) -> dict:
    """Run the classification benchmark and return results."""
    cases = BENCHMARK_CASES[:10] if quick else BENCHMARK_CASES
    results = {"total": len(cases), "correct_risk": 0, "correct_category": 0, "errors": 0, "details": []}

    print(f"\n{'='*70}")
    print(f"ComplyOS Classification Benchmark — {len(cases)} test cases")
    print(f"{'='*70}\n")

    start = time.time()

    for i, tc in enumerate(cases):
        try:
            result = await classify_ai_system(
                name=tc.name,
                description=tc.description,
                use_case=tc.use_case,
            )
            risk_match = result.risk_level.value == tc.expected_risk
            cat_match = result.annex_category.value == tc.expected_category or (
                tc.expected_category == "none" and result.annex_category.value == "none"
            )

            if risk_match:
                results["correct_risk"] += 1
            if cat_match:
                results["correct_category"] += 1

            status = "PASS" if risk_match else "FAIL"
            print(f"  [{i+1:2d}/{len(cases)}] {status} | {tc.name[:35]:35s} | expected={tc.expected_risk:13s} got={result.risk_level.value:13s} ({result.confidence_score:.0%})")

            results["details"].append({
                "name": tc.name,
                "expected_risk": tc.expected_risk,
                "predicted_risk": result.risk_level.value,
                "expected_category": tc.expected_category,
                "predicted_category": result.annex_category.value,
                "confidence": result.confidence_score,
                "risk_correct": risk_match,
                "category_correct": cat_match,
            })

        except Exception as e:
            results["errors"] += 1
            print(f"  [{i+1:2d}/{len(cases)}] ERROR | {tc.name[:35]:35s} | {e}")
            results["details"].append({
                "name": tc.name,
                "expected_risk": tc.expected_risk,
                "predicted_risk": "error",
                "error": str(e),
                "risk_correct": False,
                "category_correct": False,
            })

    elapsed = time.time() - start

    risk_acc = results["correct_risk"] / results["total"] * 100 if results["total"] else 0
    cat_acc = results["correct_category"] / results["total"] * 100 if results["total"] else 0

    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"  Risk Level Accuracy:  {results['correct_risk']}/{results['total']} ({risk_acc:.1f}%)")
    print(f"  Category Accuracy:    {results['correct_category']}/{results['total']} ({cat_acc:.1f}%)")
    print(f"  Errors:               {results['errors']}")
    print(f"  Time:                 {elapsed:.1f}s ({elapsed/len(cases):.1f}s per case)")
    print(f"{'='*70}\n")

    # Breakdown by risk level
    for level in ["unacceptable", "high", "limited", "minimal"]:
        level_cases = [d for d in results["details"] if d["expected_risk"] == level]
        if level_cases:
            correct = sum(1 for d in level_cases if d["risk_correct"])
            print(f"  {level:13s}: {correct}/{len(level_cases)} ({correct/len(level_cases)*100:.0f}%)")

    results["risk_accuracy"] = risk_acc
    results["category_accuracy"] = cat_acc
    results["elapsed_seconds"] = elapsed

    return results


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    results = asyncio.run(run_benchmark(quick=quick))

    with open("tests/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to tests/benchmark_results.json")

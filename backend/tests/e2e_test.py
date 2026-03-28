"""End-to-end tests for ComplyOS API.

Tests the full pipeline: health -> register -> classify -> analyze -> generate docs -> chat
Runs against either local or production backend.

Usage:
    python -m tests.e2e_test                          # local (localhost:8000)
    python -m tests.e2e_test --prod                   # production (complyos.onrender.com)
    python -m tests.e2e_test --base-url https://...   # custom URL
"""

import json
import sys
import time

import httpx

DEFAULT_LOCAL = "http://localhost:8000"
DEFAULT_PROD = "https://complyos.onrender.com"


def get_base_url() -> str:
    """Determine base URL from CLI args."""
    if "--prod" in sys.argv:
        return DEFAULT_PROD
    for arg in sys.argv:
        if arg.startswith("--base-url="):
            return arg.split("=", 1)[1]
    return DEFAULT_LOCAL


class E2ETestRunner:
    """Run end-to-end tests against ComplyOS API."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=120.0)
        self.passed = 0
        self.failed = 0
        self.results: list[dict] = []

    def test(self, name: str, method: str, path: str, expected_status: int = 200, body: dict | None = None, checks: list | None = None) -> dict | None:
        """Run a single test case."""
        start = time.time()
        try:
            if method == "GET":
                r = self.client.get(path)
            elif method == "POST":
                r = self.client.post(path, json=body or {})
            else:
                raise ValueError(f"Unknown method: {method}")

            elapsed = time.time() - start
            status_ok = r.status_code == expected_status

            data = None
            try:
                data = r.json()
            except Exception:
                pass

            check_results = []
            if checks and data:
                for check_name, check_fn in checks:
                    try:
                        passed = check_fn(data)
                        check_results.append((check_name, passed))
                    except Exception as e:
                        check_results.append((check_name, False))

            all_checks_pass = all(ok for _, ok in check_results) if check_results else True
            test_passed = status_ok and all_checks_pass

            if test_passed:
                self.passed += 1
                icon = "PASS"
            else:
                self.failed += 1
                icon = "FAIL"

            print(f"  [{icon}] {name} ({elapsed:.1f}s) — {r.status_code}")
            for check_name, ok in check_results:
                print(f"         {'ok' if ok else 'FAIL'}: {check_name}")

            self.results.append({
                "name": name,
                "passed": test_passed,
                "status_code": r.status_code,
                "elapsed": round(elapsed, 2),
                "checks": {cn: ok for cn, ok in check_results},
            })

            return data

        except Exception as e:
            elapsed = time.time() - start
            self.failed += 1
            print(f"  [FAIL] {name} ({elapsed:.1f}s) — ERROR: {e}")
            self.results.append({
                "name": name,
                "passed": False,
                "error": str(e),
                "elapsed": round(elapsed, 2),
            })
            return None

    def summary(self) -> dict:
        """Print and return summary."""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"E2E Results: {self.passed}/{total} passed ({self.passed/total*100:.0f}%)")
        print(f"{'='*60}")
        return {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round(self.passed / total * 100, 1) if total else 0,
            "details": self.results,
        }


def run_e2e(base_url: str) -> dict:
    """Run the full e2e test suite."""
    runner = E2ETestRunner(base_url)
    print(f"\nComplyOS E2E Tests — {base_url}")
    print(f"{'='*60}\n")

    # --- 1. Health Check ---
    print("1. Health & Infrastructure")
    runner.test(
        "Health check",
        "GET", "/health",
        checks=[("status is healthy", lambda d: d.get("status") == "healthy")],
    )

    # --- 2. Dashboard ---
    print("\n2. Dashboard")
    dashboard = runner.test(
        "Dashboard metrics",
        "GET", "/api/dashboard",
        checks=[
            ("has total_systems", lambda d: "total_systems" in d),
            ("has days_until_deadline", lambda d: d.get("days_until_deadline", 0) > 0),
            ("seeded data exists", lambda d: d.get("total_systems", 0) >= 5),
        ],
    )

    # --- 3. List Systems ---
    print("\n3. System Registry")
    systems = runner.test(
        "List systems",
        "GET", "/api/systems",
        checks=[
            ("returns list", lambda d: isinstance(d, list)),
            ("has seeded systems", lambda d: len(d) >= 5),
        ],
    )

    # --- 4. Register New System ---
    new_system = runner.test(
        "Register new system",
        "POST", "/api/systems",
        body={
            "name": "E2E Test Chatbot",
            "description": "An AI chatbot that interacts with customers on an e-commerce website, answering product questions and processing returns.",
            "department": "Support",
            "use_case": "Customer service automation",
        },
        checks=[
            ("has id", lambda d: "id" in d),
            ("name matches", lambda d: d.get("name") == "E2E Test Chatbot"),
            ("not classified yet", lambda d: d.get("risk_level") is None),
        ],
    )

    system_id = new_system.get("id") if new_system else None

    # --- 5. Get Single System ---
    if system_id:
        runner.test(
            "Get system by ID",
            "GET", f"/api/systems/{system_id}",
            checks=[
                ("correct id", lambda d: d.get("id") == system_id),
                ("has description", lambda d: len(d.get("description", "")) > 10),
            ],
        )

    # --- 6. Classify System ---
    print("\n4. Classification Pipeline")
    if system_id:
        classification = runner.test(
            "Classify system (LLM call)",
            "POST", f"/api/systems/{system_id}/classify",
            checks=[
                ("has risk_level", lambda d: d.get("risk_level") in ["unacceptable", "high", "limited", "minimal"]),
                ("has confidence", lambda d: 0 <= d.get("confidence_score", -1) <= 1),
                ("has reasoning", lambda d: len(d.get("reasoning", "")) > 20),
                ("has cited_articles", lambda d: isinstance(d.get("cited_articles"), list)),
                ("chatbot is limited risk", lambda d: d.get("risk_level") == "limited"),
            ],
        )

    # --- 7. Register + Classify High-Risk System ---
    hr_system = runner.test(
        "Register high-risk system",
        "POST", "/api/systems",
        body={
            "name": "E2E Resume Screener",
            "description": "AI system that automatically screens job applications and resumes, ranks candidates based on skills matching, and filters applicants for recruitment.",
            "department": "HR",
            "use_case": "Candidate screening",
        },
        checks=[("has id", lambda d: "id" in d)],
    )
    hr_id = hr_system.get("id") if hr_system else None

    if hr_id:
        hr_class = runner.test(
            "Classify as high-risk (employment)",
            "POST", f"/api/systems/{hr_id}/classify",
            checks=[
                ("is high risk", lambda d: d.get("risk_level") == "high"),
                ("employment category", lambda d: d.get("annex_category") == "employment"),
                ("confidence >= 90%", lambda d: d.get("confidence_score", 0) >= 0.9),
            ],
        )

    # --- 8. Gap Analysis ---
    print("\n5. Gap Analysis Pipeline")
    if hr_id:
        gap_result = runner.test(
            "Run ontology-guided gap analysis (7 LLM calls)",
            "POST", f"/api/systems/{hr_id}/analyze",
            checks=[
                ("has overall_score", lambda d: 0 <= d.get("overall_score", -1) <= 100),
                ("has requirement_statuses", lambda d: isinstance(d.get("requirement_statuses"), list)),
                ("7 articles assessed", lambda d: len(d.get("requirement_statuses", [])) == 7),
                ("has priority_actions", lambda d: len(d.get("priority_actions", [])) > 0),
                ("has summary", lambda d: len(d.get("summary", "")) > 10),
            ],
        )

    # --- 9. Ontology Endpoints ---
    print("\n6. Ontology Endpoints")
    runner.test(
        "Get requirement tree (no LLM)",
        "GET", "/api/ontology/requirements?risk_level=high",
        checks=[
            ("7 articles", lambda d: d.get("total_articles") == 7),
            ("25 sub-requirements", lambda d: d.get("total_sub_requirements") == 25),
            ("has articles array", lambda d: isinstance(d.get("articles"), list)),
        ],
    )

    runner.test(
        "Get cross-references for Article 9",
        "GET", "/api/ontology/cross-references/article_9",
        checks=[
            ("returns list", lambda d: isinstance(d, list)),
            ("has cross-references", lambda d: len(d) > 0),
            ("targets article_72", lambda d: any(x.get("target_article") == "article_72" for x in d)),
        ],
    )

    runner.test(
        "Invalid article returns 404",
        "GET", "/api/ontology/cross-references/article_999",
        expected_status=404,
    )

    # --- 10. Chat ---
    print("\n7. Compliance Chat")
    runner.test(
        "Chat about AI Act (LLM call)",
        "POST", "/api/chat",
        body={"message": "What are the penalties for non-compliance with the EU AI Act?"},
        checks=[
            ("has answer", lambda d: len(d.get("answer", "")) > 50),
            ("has cited_articles", lambda d: isinstance(d.get("cited_articles"), list)),
        ],
    )

    # --- 11. Document Generation ---
    print("\n8. Document Generation")
    if hr_id:
        runner.test(
            "Generate compliance documentation (LLM call)",
            "POST", f"/api/systems/{hr_id}/generate-docs",
            body={"system_id": hr_id, "doc_type": "technical_documentation"},
            checks=[
                ("has content", lambda d: len(d.get("content", "")) > 100),
                ("has id", lambda d: "id" in d),
                ("markdown format", lambda d: "#" in d.get("content", "")),
            ],
        )

    # --- 12. Dashboard Updated ---
    print("\n9. Verification")
    runner.test(
        "Dashboard reflects new data",
        "GET", "/api/dashboard",
        checks=[
            ("more systems than before", lambda d: d.get("total_systems", 0) >= 7),
            ("has high risk systems", lambda d: d.get("high_risk_count", 0) >= 1),
        ],
    )

    return runner.summary()


if __name__ == "__main__":
    base_url = get_base_url()
    results = run_e2e(base_url)

    with open("tests/e2e_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to tests/e2e_results.json")

    sys.exit(0 if results["failed"] == 0 else 1)

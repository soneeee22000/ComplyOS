"""EU AI Act Compliance Ontology — structured legal knowledge as typed Python."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ApplicableRiskLevel(str, Enum):
    """Risk levels an article/requirement applies to."""

    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    ALL = "all"


@dataclass(frozen=True)
class CrossReference:
    """A reference from one article/requirement to another."""

    target_article: str
    relationship: str
    description: str


@dataclass(frozen=True)
class SubRequirement:
    """A specific sub-obligation within an article."""

    id: str
    article_id: str
    paragraph: str
    title: str
    description: str
    verification_criteria: list[str] = field(default_factory=list)
    cross_references: list[CrossReference] = field(default_factory=list)


@dataclass(frozen=True)
class Article:
    """A top-level article of the EU AI Act with its sub-requirements."""

    id: str
    number: int
    title: str
    chapter: str
    summary: str
    sub_requirements: list[SubRequirement] = field(default_factory=list)
    cross_references: list[CrossReference] = field(default_factory=list)
    applies_to: list[ApplicableRiskLevel] = field(
        default_factory=lambda: [ApplicableRiskLevel.HIGH]
    )


@dataclass
class Ontology:
    """The complete EU AI Act compliance ontology."""

    version: str
    articles: dict[str, Article]

    def get_requirements_for_risk_level(self, risk_level: str) -> list[Article]:
        """Return all articles applicable to a given risk level."""
        results = []
        for article in self.articles.values():
            applicable = [a.value for a in article.applies_to]
            if risk_level in applicable or "all" in applicable:
                results.append(article)
        return sorted(results, key=lambda a: a.number)

    def get_article(self, article_id: str) -> Article | None:
        """Return a single article by ID."""
        return self.articles.get(article_id)

    def get_full_requirement_tree(
        self, risk_level: str, annex_category: str | None = None
    ) -> dict:
        """Return the full requirement tree as a serializable dict."""
        articles = self.get_requirements_for_risk_level(risk_level)
        total_sub_reqs = sum(len(a.sub_requirements) for a in articles)

        return {
            "risk_level": risk_level,
            "annex_category": annex_category,
            "total_articles": len(articles),
            "total_sub_requirements": total_sub_reqs,
            "articles": [_serialize_article(a) for a in articles],
        }

    def resolve_cross_references(self, article_id: str) -> list[dict]:
        """Resolve cross-references from an article, including target metadata."""
        article = self.get_article(article_id)
        if not article:
            return []

        results = []
        for xref in article.cross_references:
            target = self.get_article(xref.target_article)
            results.append({
                "source_article": article_id,
                "target_article": xref.target_article,
                "target_title": target.title if target else "Unknown",
                "relationship": xref.relationship,
                "description": xref.description,
            })
        return results


def _serialize_article(article: Article) -> dict:
    """Serialize an Article to a JSON-compatible dict."""
    return {
        "id": article.id,
        "number": article.number,
        "title": article.title,
        "chapter": article.chapter,
        "summary": article.summary,
        "applies_to": [a.value for a in article.applies_to],
        "sub_requirements": [
            {
                "id": sr.id,
                "paragraph": sr.paragraph,
                "title": sr.title,
                "description": sr.description,
                "verification_criteria": sr.verification_criteria,
                "cross_references": [
                    {
                        "target_article": xr.target_article,
                        "relationship": xr.relationship,
                        "description": xr.description,
                    }
                    for xr in sr.cross_references
                ],
            }
            for sr in article.sub_requirements
        ],
        "cross_references": [
            {
                "target_article": xr.target_article,
                "relationship": xr.relationship,
                "description": xr.description,
            }
            for xr in article.cross_references
        ],
    }

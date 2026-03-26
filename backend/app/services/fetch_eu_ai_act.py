"""Fetch and chunk the full EU AI Act from EUR-Lex.

Downloads the complete HTML version of Regulation (EU) 2024/1689,
parses it into article-level chunks with metadata, and saves as JSON
for ingestion into ChromaDB.

Run: python -m app.services.fetch_eu_ai_act
"""

import json
import os
import re
import sys

import httpx


EUR_LEX_URL = (
    "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/"
    "?uri=OJ:L_202401689"
)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eu_ai_act_chunks.json")


def fetch_html() -> str:
    """Fetch the full HTML of the EU AI Act from EUR-Lex."""
    print(f"Fetching EU AI Act from EUR-Lex...")
    response = httpx.get(
        EUR_LEX_URL,
        follow_redirects=True,
        timeout=60.0,
        headers={
            "User-Agent": "ComplyOS/1.0 (EU AI Act compliance tool; research purposes)",
            "Accept": "text/html",
        },
    )
    response.raise_for_status()
    print(f"Fetched {len(response.text):,} characters")
    return response.text


def strip_html_tags(html: str) -> str:
    """Remove HTML tags and clean up whitespace."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#\d+;", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_by_articles(html: str) -> list[dict]:
    """Parse the EU AI Act HTML and chunk by article/annex.

    Returns a list of dicts with keys: id, source, chapter, text
    """
    chunks = []

    # Split by Article markers
    # EUR-Lex uses patterns like "Article 1" or "Article 5"
    article_pattern = re.compile(
        r"(Article\s+(\d+))(.*?)(?=Article\s+\d+|ANNEX\s+[IVX]+|$)",
        re.DOTALL | re.IGNORECASE,
    )

    matches = article_pattern.findall(html)
    print(f"Found {len(matches)} article matches in HTML")

    for match in matches:
        article_header = match[0]
        article_num = match[1]
        article_body = match[2]

        text = strip_html_tags(article_body)

        # Extract the article title (first line after article number)
        title_match = re.match(r"\s*([A-Z][^.!?]*?)(?:\s{2,}|\.\s|\n)", text)
        title = title_match.group(1).strip() if title_match else ""

        if len(text) < 20:
            continue

        # Split long articles into sub-chunks of ~1500 chars
        if len(text) > 2000:
            paragraphs = re.split(r"(\d+\.\s)", text)
            current_chunk = ""
            chunk_idx = 0

            for para in paragraphs:
                if len(current_chunk) + len(para) > 1500 and current_chunk:
                    chunks.append({
                        "id": f"article-{article_num}-{chunk_idx}",
                        "source": f"Article {article_num}: {title}" if title else f"Article {article_num}",
                        "chapter": f"Article {article_num}",
                        "text": current_chunk.strip(),
                    })
                    chunk_idx += 1
                    current_chunk = para
                else:
                    current_chunk += para

            if current_chunk.strip():
                chunks.append({
                    "id": f"article-{article_num}-{chunk_idx}",
                    "source": f"Article {article_num}: {title}" if title else f"Article {article_num}",
                    "chapter": f"Article {article_num}",
                    "text": current_chunk.strip(),
                })
        else:
            chunks.append({
                "id": f"article-{article_num}",
                "source": f"Article {article_num}: {title}" if title else f"Article {article_num}",
                "chapter": f"Article {article_num}",
                "text": text,
            })

    # Extract Annexes
    annex_pattern = re.compile(
        r"(ANNEX\s+([IVX]+))(.*?)(?=ANNEX\s+[IVX]+|$)",
        re.DOTALL | re.IGNORECASE,
    )

    annex_matches = annex_pattern.findall(html)
    print(f"Found {len(annex_matches)} annex matches")

    for match in annex_matches:
        annex_header = match[0]
        annex_num = match[1]
        annex_body = match[2]

        text = strip_html_tags(annex_body)

        if len(text) < 20:
            continue

        # Split long annexes
        if len(text) > 2000:
            sections = re.split(r"(?=\d+\.\s+[A-Z])", text)
            for idx, section in enumerate(sections):
                section = section.strip()
                if len(section) > 30:
                    chunks.append({
                        "id": f"annex-{annex_num.lower()}-{idx}",
                        "source": f"Annex {annex_num}",
                        "chapter": f"Annex {annex_num}",
                        "text": section[:2000],
                    })
        else:
            chunks.append({
                "id": f"annex-{annex_num.lower()}",
                "source": f"Annex {annex_num}",
                "chapter": f"Annex {annex_num}",
                "text": text,
            })

    return chunks


def add_recitals(html: str, chunks: list[dict]) -> list[dict]:
    """Extract key recitals that provide interpretive guidance."""
    recital_pattern = re.compile(
        r"\((\d+)\)\s+(.*?)(?=\(\d+\)\s|$)",
        re.DOTALL,
    )

    text = strip_html_tags(html)
    matches = recital_pattern.findall(text)

    # Only include recitals that are substantial (>200 chars)
    # and relate to key topics
    key_topics = [
        "high-risk", "prohibited", "transparency", "biometric",
        "employment", "education", "critical infrastructure",
        "general-purpose", "foundation model", "fine",
        "penalty", "sandbox", "conformity", "risk management",
        "human oversight", "data governance",
    ]

    recital_count = 0
    for num, body in matches:
        body = body.strip()
        if len(body) < 100:
            continue

        body_lower = body.lower()
        if any(topic in body_lower for topic in key_topics):
            chunks.append({
                "id": f"recital-{num}",
                "source": f"Recital {num}",
                "chapter": "Preamble",
                "text": body[:2000],
            })
            recital_count += 1

    print(f"Added {recital_count} key recitals")
    return chunks


def save_chunks(chunks: list[dict]) -> None:
    """Save chunks to JSON file."""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(chunks)} chunks to {OUTPUT_PATH}")


def main() -> None:
    """Fetch, parse, and save EU AI Act chunks."""
    html = fetch_html()
    chunks = chunk_by_articles(html)
    chunks = add_recitals(html, chunks)

    # Print stats
    total_chars = sum(len(c["text"]) for c in chunks)
    articles = [c for c in chunks if c["chapter"].startswith("Article")]
    annexes = [c for c in chunks if c["chapter"].startswith("Annex")]
    recitals = [c for c in chunks if c["chapter"] == "Preamble"]

    print(f"\n--- EU AI Act Ingestion Stats ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"  Articles: {len(articles)} chunks")
    print(f"  Annexes: {len(annexes)} chunks")
    print(f"  Recitals: {len(recitals)} chunks")
    print(f"Total characters: {total_chars:,}")
    print(f"Avg chunk size: {total_chars // max(len(chunks), 1):,} chars")

    save_chunks(chunks)


if __name__ == "__main__":
    main()

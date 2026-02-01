from ddgs import DDGS


def score_result(title: str, link: str, snippet: str) -> int:
    """
    Generic credibility scoring (not hardcoded to specific sites).
    Higher score = more reliable for policy/regulation queries.
    """

    score = 0
    text = f"{title} {snippet}".lower()
    link = link.lower()

    # Boost official / credible domains
    if ".gov" in link:
        score += 3
    if ".org" in link:
        score += 2

    # Boost regulation/policy keywords
    keywords = ["policy", "guideline", "act", "regulation", "ministry", "government", "law"]
    if any(k in text for k in keywords):
        score += 3

    # Penalize noisy aggregators
    noisy = ["latest", "breaking", "top stories", "entertainment", "sports"]
    if any(n in text for n in noisy):
        score -= 3

    return score


def web_search(query: str, max_results: int = 6):
    """
    Web search with:
    - Query expansion
    - Deduplication
    - Credibility scoring (generic, scalable)
    """

    expanded_queries = [
        query,
        query + " policy guideline"
    ]

    collected = []

    with DDGS() as ddgs:
        for q in expanded_queries:
            for r in ddgs.text(q, max_results=max_results):
                collected.append(r)

    # Deduplicate
    unique = {}
    for r in collected:
        unique[r["href"]] = r

    results = []

    # Score + format
    for r in unique.values():
        title = r.get("title") or ""
        snippet = r.get("body") or ""
        link = r.get("href") or ""

        results.append({
            "title": title,
            "snippet": snippet,
            "link": link,
            "score": score_result(title, link, snippet)
        })

    # Sort by best score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # Return top results
    return results[:max_results]

from __future__ import annotations

from pathlib import Path


class LocalKnowledgeBase:
    """Very small file-based retrieval layer for playbooks and notes."""

    def __init__(self, directory: str) -> None:
        self.directory = Path(directory)

    def search(self, query: str, limit: int = 3) -> list[str]:
        if not self.directory.exists():
            return []

        terms = [token.lower() for token in query.split() if len(token) > 3]
        if not terms:
            return []

        scored: list[tuple[int, str]] = []
        for doc in self.directory.glob("*.md"):
            text = doc.read_text(encoding="utf-8", errors="ignore")
            lowered = text.lower()
            score = sum(lowered.count(term) for term in terms)
            if score > 0:
                first_line = text.strip().splitlines()[0] if text.strip() else doc.name
                scored.append((score, f"{doc.name}: {first_line}"))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [snippet for _, snippet in scored[:limit]]

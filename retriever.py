"""Stdlib TF-IDF + cosine similarity retriever (same concepts as the labs)."""
import math
import re
from collections import Counter

from policies import POLICIES

_STOP = {"the", "a", "an", "of", "on", "in", "to", "is", "and", "or", "for", "at", "it", "with", "off", "any"}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP]


class TfidfRetriever:
    def __init__(self, policies=POLICIES):
        self.docs = policies
        tokenized = [tokenize(f"{p['id']} {p['title']} {p['source_text']}") for p in policies]
        n = len(tokenized)
        df = Counter(t for toks in tokenized for t in set(toks))
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.vecs = [self._vectorize(toks) for toks in tokenized]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(t for t in tokens if t in self.idf)
        vec = {t: c * self.idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        return {t: v / norm for t, v in vec.items()} if norm else {}

    def search(self, query: str, k: int = 3, min_score: float = 0.05) -> list[dict]:
        """Return up to k policies with cosine score >= min_score (empty list = no evidence)."""
        q = self._vectorize(tokenize(query))
        if not q:
            return []
        scored = []
        for doc, vec in zip(self.docs, self.vecs):
            score = sum(w * vec.get(t, 0.0) for t, w in q.items())
            if score >= min_score:
                scored.append({"id": doc["id"], "title": doc["title"],
                               "source_text": doc["source_text"], "score": round(score, 4)})
        return sorted(scored, key=lambda d: d["score"], reverse=True)[:k]

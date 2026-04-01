from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from agentic_runtime.utils.time_utils import utc_now_iso


# ---------------------------------------------------------------------------
# Tipos de datos
# ---------------------------------------------------------------------------

@dataclass
class VectorEntry:
    key: str           # identificador único (p.ej. "proj:last_request")
    text: str          # texto original indexado
    metadata: dict     # scope, session_id, etc.
    stored_at: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "text": self.text,
            "metadata": self.metadata,
            "stored_at": self.stored_at,
        }


@dataclass
class SearchResult:
    entry: VectorEntry
    score: float       # 0.0 – 1.0


# ---------------------------------------------------------------------------
# Protocolo — permite sustituir por FAISS/Chroma sin cambiar interfaces
# ---------------------------------------------------------------------------

@runtime_checkable
class VectorBackend(Protocol):
    def store(self, entry: VectorEntry) -> None: ...
    def search(self, query: str, top_k: int) -> list[SearchResult]: ...
    def delete(self, key: str) -> bool: ...
    def count(self) -> int: ...


# ---------------------------------------------------------------------------
# Backend por defecto: TF-IDF simplificado en memoria
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúñüA-Z0-9]+", text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = max(len(tokens), 1)
    return {t: c / total for t, c in counts.items()}


def _idf(term: str, docs: list[list[str]]) -> float:
    n_docs = len(docs)
    n_containing = sum(1 for d in docs if term in d)
    return math.log((1 + n_docs) / (1 + n_containing)) + 1.0


def _cosine(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values())) or 1.0
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values())) or 1.0
    return dot / (norm_a * norm_b)


class KeywordVectorBackend:
    """Backend TF-IDF en memoria, sin dependencias externas.

    Para producción, sustituir por FAISSBackend o ChromaBackend
    implementando el protocolo VectorBackend.
    """

    def __init__(self) -> None:
        self._entries: dict[str, VectorEntry] = {}
        self._token_cache: dict[str, list[str]] = {}  # key -> tokens

    def store(self, entry: VectorEntry) -> None:
        self._entries[entry.key] = entry
        self._token_cache[entry.key] = _tokenize(entry.text)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not self._entries:
            return []
        q_tokens = _tokenize(query)
        all_token_lists = list(self._token_cache.values())
        q_tf = _tf(q_tokens)
        q_tfidf = {
            t: q_tf[t] * _idf(t, all_token_lists)
            for t in q_tf
        }
        results: list[SearchResult] = []
        for key, entry in self._entries.items():
            d_tokens = self._token_cache[key]
            d_tf = _tf(d_tokens)
            d_tfidf = {
                t: d_tf[t] * _idf(t, all_token_lists)
                for t in d_tf
            }
            score = _cosine(q_tfidf, d_tfidf)
            if score > 0:
                results.append(SearchResult(entry=entry, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            del self._token_cache[key]
            return True
        return False

    def count(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Fachada pública: VectorDB
# ---------------------------------------------------------------------------

class VectorDB:
    """Memoria semántica del runtime.

    Por defecto usa KeywordVectorBackend (TF-IDF, sin deps).
    Para FAISS: ``VectorDB(backend=FAISSBackend(...))``
    Para Chroma: ``VectorDB(backend=ChromaBackend(...))``

    Integración con MemoryStore:
        Cada vez que MemoryStore.put() se llama, también indexa
        el valor en VectorDB para búsqueda semántica posterior.
    """

    def __init__(self, backend: VectorBackend | None = None) -> None:
        self._backend: VectorBackend = backend or KeywordVectorBackend()

    def store(self, key: str, text: str, metadata: dict | None = None) -> VectorEntry:
        entry = VectorEntry(
            key=key,
            text=text,
            metadata=metadata or {},
            stored_at=utc_now_iso(),
        )
        self._backend.store(entry)
        return entry

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Busca entradas similares por contenido semántico."""
        return self._backend.search(query, top_k=top_k)

    def search_as_context(self, query: str, top_k: int = 5) -> str:
        """Retorna resultados formateados como contexto para el LLM."""
        results = self.search(query, top_k=top_k)
        if not results:
            return ""
        lines = ["[VECTOR MEMORY — resultados semánticos]"]
        for r in results:
            lines.append(
                f"  [{r.score:.2f}] ({r.entry.metadata.get('scope', '?')}) "
                f"{r.entry.key}: {r.entry.text[:200]}"
            )
        return "\n".join(lines)

    def delete(self, key: str) -> bool:
        return self._backend.delete(key)

    def count(self) -> int:
        return self._backend.count()

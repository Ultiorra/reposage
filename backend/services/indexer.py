import uuid

import numpy as np
from sentence_transformers import SentenceTransformer

from core.config import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _chunk(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


class RepoIndex:
    def __init__(self, files: dict[str, str]):
        self.files = files
        self.chunk_texts: list[str] = []
        self.chunk_paths: list[str] = []
        model = _get_model()
        for path, content in files.items():
            for piece in _chunk(content, settings.chunk_size, settings.chunk_overlap):
                self.chunk_texts.append(piece)
                self.chunk_paths.append(path)
        self.embeddings = model.encode(
            self.chunk_texts, convert_to_numpy=True, normalize_embeddings=True
        )

    def search(self, query: str, k: int) -> list[dict]:
        model = _get_model()
        q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        scores = self.embeddings @ q
        top = np.argsort(scores)[::-1][:k]
        return [
            {
                "path": self.chunk_paths[i],
                "snippet": self.chunk_texts[i],
                "score": float(scores[i]),
            }
            for i in top
        ]

    def read_file(self, path: str) -> str:
        return self.files.get(path, "")

    def list_files(self) -> list[str]:
        return sorted(self.files.keys())


_indexes: dict[str, RepoIndex] = {}


def create_index(files: dict[str, str]) -> str:
    index_id = uuid.uuid4().hex
    _indexes[index_id] = RepoIndex(files)
    return index_id


def get_index(index_id: str) -> RepoIndex | None:
    return _indexes.get(index_id)

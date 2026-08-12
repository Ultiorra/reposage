import uuid

import numpy as np
import voyageai

from core.config import settings

_client: voyageai.Client | None = None


def _get_client() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=settings.voyage_api_key)
    return _client


def _chunk(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def _embed(texts: list[str], input_type: str) -> np.ndarray:
    client = _get_client()
    vectors: list[list[float]] = []
    batch = settings.embed_batch_size
    for i in range(0, len(texts), batch):
        result = client.embed(
            texts[i:i + batch],
            model=settings.embedding_model,
            input_type=input_type,
        )
        vectors.extend(result.embeddings)
    return np.array(vectors, dtype="float32")


class RepoIndex:
    def __init__(self, files: dict[str, str]):
        self.files = files
        self.chunk_texts: list[str] = []
        self.chunk_paths: list[str] = []
        for path, content in files.items():
            for piece in _chunk(content, settings.chunk_size, settings.chunk_overlap):
                self.chunk_texts.append(piece)
                self.chunk_paths.append(path)
        self.embeddings = _embed(self.chunk_texts, "document")

    def search(self, query: str, k: int) -> list[dict]:
        q = _embed([query], "query")[0]
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

import json
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "knowledge_base" / "troubleshooting.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class KnowledgeRetriever:
    """Small local RAG index over curated troubleshooting entries."""
    def __init__(self):
        with open(KB_PATH, "r", encoding="utf-8") as f:
            self.entries = json.load(f)
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        texts = [self._search_text(entry) for entry in self.entries]
        vectors = self.encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        vectors = np.asarray(vectors, dtype="float32")
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    @staticmethod
    def _search_text(entry):
        return " ".join([entry.get("title", ""), entry.get("symptoms", ""), entry.get("cause", ""), entry.get("fix", ""), entry.get("tags", "")])

    def search(self, query: str, top_k: int = 4):
        vector = self.encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        k = min(max(1, int(top_k)), len(self.entries))
        scores, ids = self.index.search(vector, k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            item = dict(self.entries[int(idx)])
            item["score"] = float(score)
            results.append(item)
        return results

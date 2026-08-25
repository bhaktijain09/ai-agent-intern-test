from src.retrieval.document_loader import load_documents
from src.retrieval.chunker import chunk_documents
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_store import VectorStore
from src.config import (
    KNOWLEDGE_BASE_DIR,
    TOP_K,
    SIMILARITY_THRESHOLD
)


class Retriever:

    def __init__(self):

        documents = load_documents(
            KNOWLEDGE_BASE_DIR
        )

        self.chunks = chunk_documents(documents)

        self.embedding_model = EmbeddingModel()

        embeddings = self.embedding_model.encode(
            [chunk.text for chunk in self.chunks]
        )

        self.vector_store = VectorStore(
            embeddings
        )

    def retrieve(self, query, k=None):

        k = k or TOP_K

        query_embedding = self.embedding_model.encode(
            [query]
        )

        scores, indices = self.vector_store.search(
            query_embedding,
            k
        )

        results = []

        for score, index in zip(scores, indices):

            if index < 0:
                continue

            chunk = self.chunks[index]

            results.append({
                "text": chunk.text,
                "filename": chunk.filename,
                "heading": chunk.heading,
                "metadata": chunk.metadata,
                "score": float(score),
                "authority": self.classify_authority(
                    chunk.filename,
                    chunk.metadata
                )
            })

        results = self.apply_authority_rules(results)

        return {
            "results": results,
            "conflict": self.detect_conflict(results)
        }

    def classify_authority(self, filename, metadata=None):
        """
        Authority is determined primarily from document metadata.
        Filename is used only as a fallback.
        """

        metadata = metadata or {}

        status = metadata.get(
            "status",
            ""
        ).strip().lower()

        if status == "internal":
            return "internal"

        if status in {
            "legacy",
            "deprecated",
            "superseded"
        }:
            return "legacy"

        if status in {
            "current",
            "active"
        }:
            return "current"

        # Fallback to filename
        if "internal" in filename:
            return "internal"

        if "legacy" in filename:
            return "legacy"

        if "current" in filename:
            return "current"

        return "unclassified"

    def apply_authority_rules(self, results):

        def priority(result):

            authority = result["authority"]

            # Internal documents should never
            # become authoritative.
            if authority == "internal":
                return -100

            # Legacy documents have lower priority
            # than current documents.
            if authority == "legacy":
                return -50

            # Current documents get highest priority.
            if authority == "current":
                return 100

            return 10

        results.sort(
            key=lambda x: (
                priority(x),
                x["score"]
            ),
            reverse=True
        )

        return results

    def detect_conflict(self, results):

        current_results = [
            r
            for r in results
            if r["authority"] == "current"
            and r["score"] >= SIMILARITY_THRESHOLD
        ]

        # Multiple current documents do NOT automatically
        # mean that there is a conflict.
        #
        # We only flag a possible conflict when multiple
        # current documents have the same topic/heading.

        topic_sources = {}

        for result in current_results:

            heading = result["heading"].strip().lower()

            topic_sources.setdefault(
                heading,
                set()
            ).add(result["filename"])

        conflicting_sources = set()

        for sources in topic_sources.values():

            if len(sources) > 1:
                conflicting_sources.update(sources)

        return {
            "possible_conflict": len(conflicting_sources) > 1,
            "sources": list(conflicting_sources)
        }
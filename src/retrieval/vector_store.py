import faiss
import numpy as np


class VectorStore:

    def __init__(self, embeddings):
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(
            np.asarray(
                embeddings,
                dtype="float32"
            )
        )

    def search(self, query_embedding, k=5):

        k = min(k, self.index.ntotal)

        scores, indices = self.index.search(
            np.asarray(
                query_embedding,
                dtype="float32"
            ),
            k
        )

        return scores[0], indices[0]

import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.vectors = []
        self.texts = []
        self.metadata = []
        self.dim = dim

    def add(self, vectors, texts, metadata_list):
        self.vectors.extend(vectors)
        self.texts.extend(texts)
        self.metadata.extend(metadata_list)

    def search(self, query_vector, k=5):
        vectors_np = np.array(self.vectors)
        sims = np.dot(vectors_np, query_vector)
        top_k = np.argsort(sims)[-k:][::-1]
        return [(self.texts[i], self.metadata[i]) for i in top_k]

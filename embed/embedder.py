from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks):
    return np.array(model.encode(chunks, show_progress_bar=True))

def get_embedder():
    return model

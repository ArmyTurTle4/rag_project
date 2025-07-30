import os
import pickle
import re
from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from ingest.preprocess_pipeline import build_index

VECTOR_DB_PATH = "./vector_index/index.pkl"

# Keywords to boost (can adjust for topic_indexer later)
KEYWORDS = {"abstract", "introduction", "motivation", "problem", "approach", "transformer", "attention"}
EMAIL_REGEX = re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b")
AFFILIATION_KEYWORDS = {"google", "research", "university", ".edu", "institute", "school"}


def load_vectorstore():
    if not os.path.exists(VECTOR_DB_PATH):
        print("\u26a0\ufe0f Vector index missing. Rebuilding it now...")
        build_index()

    if not os.path.exists(VECTOR_DB_PATH):
        raise FileNotFoundError(f"[Missing index] {VECTOR_DB_PATH} not found even after rebuild. Check data and pipeline.")

    with open(VECTOR_DB_PATH, "rb") as f:
        return pickle.load(f)


def cosine_similarity(a, b):
    a = a.reshape(1, -1)
    b = b.reshape(1, -1)
    return cos_sim(a, b)[0][0]


def get_top_k_chunks(query_vec, vectorstore, k=30):
    results = []
    for i, (vec, text, meta) in enumerate(zip(vectorstore.vectors, vectorstore.texts, vectorstore.metadata)):
        sim = cosine_similarity(query_vec, vec)

        # Lowercase version of text for pattern checks
        text_lc = text.lower()

        # Heuristic to demote author/affiliation chunks
        is_author_chunk = EMAIL_REGEX.search(text) or any(kw in text_lc for kw in AFFILIATION_KEYWORDS)
        if is_author_chunk and len(text.split()) < 25:
            sim = 0  # Nullify short author-type chunks

        # Penalize citations
        if meta.get("type") == "citation" or meta.get("section", "").lower() == "references":
            sim *= 0.4

        # Boost useful sections
        section = meta.get("section", "").lower()
        if any(keyword in section for keyword in KEYWORDS):
            sim *= 1.4

        results.append((sim, text, meta))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:k]


def search(query_vec, vectorstore, k=10):
    return get_top_k_chunks(query_vec, vectorstore, k)


# Initialize vectorstore on import
retriever = load_vectorstore()




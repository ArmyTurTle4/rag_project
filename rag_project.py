from Utility.DocSaver import save_to_downloads
from embed.embedder import get_embedder
#from generate.answerer import answer_query   # import the correct function
from retrieval.retriever import load_vectorstore
import os

embedder = get_embedder()
retriever = load_vectorstore()

def query_rag_system(question, save_sections=False, filename=None):
    query_vec = embedder.encode([question])[0]
    docs = retriever.search(query_vec, k=5)
    context = "\n\n".join([text for text, meta in docs])
    if not docs:
        return "No relevant context found."
    if save_sections and filename:
        # Build annotated text with metadata
        output_lines = []
        for i, (text, metadata) in enumerate(docs, start=1):
            output_lines.append(f"--- Section {i} ---")
            for key, value in metadata.items():
                output_lines.append(f"{key.capitalize()}: {value}")
            output_lines.append("")
            output_lines.append(text)
            output_lines.append("")

        full_content = "\n".join(output_lines)
        save_to_downloads("retrieved_context.txt", full_content)

    return docs

    #if save_sections and output_path:
        #with open(output_path, "w", encoding="utf-8") as f:
            #for text, metadata in docs:
                #f.write(f"Source: {metadata.get('source', 'Unknown')}\n")
                #f.write(f"Page: {metadata.get('page', '?')}\n")
                #f.write(f"Content:\n{text}\n")
                #f.write("="*40 + "\n\n")
        #save_to_downloads("retrieved_context.txt", context)
        #print(f"[Saved] Retrieved context saved to: {output_path}")
    #return docs


    #context = "\n\n".join([text for text, meta in docs])

    #prompt = f"""Use the context below to answer the question:

    #Context:
    #{context}

    #Question: {question}
    #"""
    # Call answer_query with both query and context
    #response = answer_query(question, context)

    #return response
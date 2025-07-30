# app.py
from ingest.preprocess_pipeline import build_index
from rag_project import query_rag_system

#print("Running build_index()")

def main():
    print("Choose output mode:")
    print("1. Display results")
    print("2. Save results to file (Downloads folder)")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in {"1", "2"}:
            break
        print("Invalid choice. Please enter 1 or 2.")

    save_to_file = (choice == "2")
    filename = "retrieved_context.txt"

    while True:
        try:
            q = input("\nAsk a question (or type 'exit'): ").strip()
            if q.lower() in {"exit", "quit"}:
                break

            result = query_rag_system(
                question=q,
                save_sections=save_to_file,
                filename = filename
            )

            if not save_to_file:
                if not result:
                    print("No relevant context found.")
                else:
                    print("\nTop Retrieved Chunks:\n")
                    for i, (text, meta) in enumerate(result, start=1):
                        print(f"[{i}] From: {meta.get('source', 'Unknown')} Page: {meta.get('page', '?')}")
                        print(text)
                        print("-" * 80)
        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    # Uncomment to rebuild index
    build_index()
    main()

#from rag_project import query_rag_system

#if __name__ == "__main__":

    #while True:
        #try:
            #q = input("Ask a question (or type 'exit'): ")
            #if q.lower() in {"exit", "quit"}:
                #break
            #results = query_rag_system(q)
            #print("\nTop Retrieved Chunks:\n")
            #for i, (text, metadata) in enumerate(results, 1):
                #print(f"[{i}] From: {metadata.get('source', 'Unknown')} Page: {metadata.get('page', '?')}")
                #print(text)
                #print("-" * 80)
        #xcept KeyboardInterrupt:
            #break

        #answer = query_rag_system(q)
        #print("\nAnswer:\n", answer)

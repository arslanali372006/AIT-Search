# src/main.py
from search import single_word_search, multi_word_search, semantic_search, autocomplete_words
from semantic import load_all_embeddings, load_glove


def main():

    print("Loading all embeddings into memory (this may take a while)...")
    embeddings = load_all_embeddings()

    glove = load_glove()

    while True:
        print("\n==== Search Engine CLI ====")
        print("1. Single-word Search")
        print("2. Multi-word Search")
        print("3. Autocomplete")
        print("4. Semantic Search")
        print("5. Exit")
        choice = input("Enter choice (1-5): ")

        if choice == "1":
            word = input("Enter search term: ").strip().lower()
            results = single_word_search(word)
            if not results:
                print("No results found.")
            else:
                print("Top results:")
                for doc_id, score in results[:10]:
                    print(f"{doc_id} | Score: {score}")

        elif choice == "2":
            query = input("Enter multi-word query: ").strip().lower()
            results = multi_word_search(query)
            if not results:
                print("No results found.")
            else:
                print("Top results:")
                for doc_id, score in results[:10]:
                    print(f"{doc_id} | Score: {score}")

        elif choice == "3":
            prefix = input("Enter prefix: ").strip().lower()
            suggestions = autocomplete_words(prefix)
            print("Autocomplete suggestions:")
            for s in suggestions:
                print(s)

        elif choice == "4":
            query = input("Enter semantic search query: ").strip().lower()
            results = semantic_search(query, glove=glove, embeddings=embeddings, top_k=10)
            if not results:
                print("No results found.")
            else:
                print("Top results:")
                for doc_id, score in results[:10]:
                    print(f"{doc_id} | Score: {score}")

        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
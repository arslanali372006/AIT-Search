# src/autocomplete.py
from lexicon import lexicon

def get_autocomplete_suggestions(prefix, top_n=10):
    """
    Returns a list of autocomplete suggestions from the lexicon.
    """
    prefix = prefix.lower()
    matches = []

    # Use lexicon.word_to_id keys
    for word in lexicon.word_to_id.keys():
        if word.startswith(prefix):
            # Rank by wordID (higher IDs first) or frequency if available
            matches.append((word, lexicon.get_id(word)))

    # Sort by ID descending
    matches.sort(key=lambda x: x[1], reverse=True)

    # Return top_n words
    return [word for word, _ in matches[:top_n]]


# Example usage
if __name__ == "__main__":
    prefix = input("Enter prefix: ")
    suggestions = get_autocomplete_suggestions(prefix)
    print("Suggestions:", suggestions)

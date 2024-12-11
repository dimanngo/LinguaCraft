import os

def load_known_words(language):
    """
    Loads known words from the language-specific known_words.txt file.
    Args:
        language (str): The language code for the known words file.
    Returns:
        tuple: A tuple containing the set of known words and the file name.
    """
    known_words = set()
    file = f"known_words_{language}.txt"
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    known_words.add(word)
    return (known_words, file)

def add_known_word(word, language):
    """
    Adds a new known word to the known_words.txt file.
    Args:
        word (str): The word to add as known.
    """
    # Ensure the word is added to the file only if it is not already present
    (known_words, file) = load_known_words(language)
    if word not in known_words:
        with open(file, "a", encoding="utf-8") as f:
            f.write(f"{word}\n")

def update_known_words(new_words, language):
    """
    Updates the known_words.txt file with a list of new words.
    Args:
        new_words (list): List of words to add as known.
    """
    (known_words, file) = load_known_words(language)
    with open(file, "a", encoding="utf-8") as f:
        for word in new_words:
            if word not in known_words:
                f.write(f"{word}\n")

def save_known_words(known_words, filename):
    """
    Saves the entire set of known words to the known_words.txt file, 
    overwriting any existing data.
    Args:
        known_words (set): Set of known words to save.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for word in known_words:
            f.write(f"{word}\n")
import os

# Define the path to the known words file
KNOWN_WORDS_FILE = "known_words.txt"

def load_known_words():
    """
    Loads known words from the known_words.txt file.
    Returns:
        set: A set of known words.
    """
    known_words = set()
    if os.path.exists(KNOWN_WORDS_FILE):
        with open(KNOWN_WORDS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                word = line.strip()
                if word:
                    known_words.add(word)
    return known_words

def add_known_word(word):
    """
    Adds a new known word to the known_words.txt file.
    Args:
        word (str): The word to add as known.
    """
    # Ensure the word is added to the file only if it is not already present
    known_words = load_known_words()
    if word not in known_words:
        with open(KNOWN_WORDS_FILE, "a", encoding="utf-8") as file:
            file.write(f"{word}\n")

def update_known_words(new_words):
    """
    Updates the known_words.txt file with a list of new words.
    Args:
        new_words (list): List of words to add as known.
    """
    known_words = load_known_words()
    with open(KNOWN_WORDS_FILE, "a", encoding="utf-8") as file:
        for word in new_words:
            if word not in known_words:
                file.write(f"{word}\n")

def save_known_words(known_words):
    """
    Saves the entire set of known words to the known_words.txt file, 
    overwriting any existing data.
    Args:
        known_words (set): Set of known words to save.
    """
    with open(KNOWN_WORDS_FILE, "w", encoding="utf-8") as file:
        for word in known_words:
            file.write(f"{word}\n")
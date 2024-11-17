# PREREQUISITE: python -m spacy download en_core_web_sm

import re
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load the spaCy model for lemmatization
nlp = spacy.load("en_core_web_sm")

import ssl
from urllib import request
# Ignore SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Ensure NLTK stopwords are downloaded
import nltk
nltk.download("punkt")
nltk.download('punkt_tab')
nltk.download("stopwords")

# Define stop words to ignore common words (optional, based on your use case)
STOP_WORDS = set(stopwords.words("english"))

def read_text_file(file_path):
    """
    Reads a text file and returns the content as a single string.
    Args:
        file_path (str): The path to the text file.
    Returns:
        str: The content of the file as a single string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return ""

def tokenize_text(text):
    """
    Tokenizes text into individual words and removes punctuation.
    Args:
        text (str): The input text.
    Returns:
        list: A list of words (tokens).
    """
    # Use regex to replace non-alphabetic characters with space, then tokenize
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return word_tokenize(text.lower()) # Ensure all tokens are lowercase

def normalize_words(tokens):
    """
    Normalizes words by lemmatizing and filtering out stopwords.
    Args:
        tokens (list): List of words (tokens) to normalize.
    Returns:
        list: A list of normalized words.
    """
    # Remove stopwords and apply lemmatization
    lemmatized_words = []
    for word in tokens:
        if word not in STOP_WORDS:  # Optional stopword filtering
            doc = nlp(word)
            for token in doc:
                lemma = token.lemma_
                # Add 'to' only if the token is identified as a verb in infinitive form
                if token.pos_ == "VERB":
                    lemma = f"to {lemma}"
                lemmatized_words.append(lemma)
    return lemmatized_words

def deduplicate_words(words):
    """
    Deduplicates a list of words.
    Args:
        words (list): List of words to deduplicate.
    Returns:
        list: A list of unique words.
    """
    return list(set(words))

def filter_known_words(words, known_words):
    """
    Filters out known words from the list of normalized words.
    Args:
        words (list): List of normalized, deduplicated words.
        known_words (set): Set of known words to exclude.
    Returns:
        list: A list of words that are not in the known words list.
    """
    # Convert known words to lowercase to ensure case-insensitive comparison
    known_words_lower = {word.lower() for word in known_words}
    return [word for word in words if word.lower() not in known_words_lower]

def process_text(file_path, known_words):
    """
    Processes text from a file, normalizes and deduplicates it, then filters out known words.
    Args:
        file_path (str): Path to the text file to process.
        known_words (set): Set of known words to exclude.
    Returns:
        list: List of unknown words after processing.
    """
    # Step 1: Read text from file
    text = read_text_file(file_path)
    if not text:
        return []  # Return empty list if file read fails

    # Step 2: Tokenize the text
    tokens = tokenize_text(text)

    # Step 3: Normalize (lemmatize) the tokens
    normalized_words = normalize_words(tokens)

    # Step 4: Deduplicate the list of words
    unique_words = deduplicate_words(normalized_words)

    # Step 5: Filter out known words
    unknown_words = filter_known_words(unique_words, known_words)

    return unknown_words
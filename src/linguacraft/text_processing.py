# PREREQUISITE: python -m spacy download en_core_web_sm

import re
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from spacy.cli import download
from langdetect import detect

# Ignore SSL certificate verification
import ssl
from urllib import request
ssl._create_default_https_context = ssl._create_unverified_context

# Ensure NLTK stopwords are downloaded
import nltk
nltk.download("punkt")
nltk.download('punkt_tab')
nltk.download("stopwords")

# Load SpaCy models for supported languages
SPACY_MODELS = {
    "en": "en_core_web_sm",
    "uk": "uk_core_news_sm",
    # Add more languages as needed
}

# Predefined dictionary mapping language codes to NLTK stopwords languages
LANGUAGE_MAP = {
    "en": "english",
    "ar": "arabic",
    "da": "danish",
    "nl": "dutch",
    "fi": "finnish",
    "fr": "french",
    "de": "german",
    "hu": "hungarian",
    "it": "italian",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "es": "spanish",
    "sv": "swedish",
    # Add more mappings as needed if supported by NLTK
}

def detect_language(text):
    """Detects the language of the given text."""
    try:
        return detect(text)
    except Exception as e:
        print(f"Language detection failed: {e}")
        return ""  # Default to empty string

# Load the spaCy model for lemmaization
def ensure_spacy_model(language):
    """Ensure the required spaCy model is downloaded."""
    model_name = SPACY_MODELS.get(language, SPACY_MODELS["en"])
    try:
        return spacy.load(model_name)
    except Exception as e:
        print(f"Downloading SpaCy model '{model_name}'...")
        download(model_name)
        return spacy.load(model_name)

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

def tokenize_text(text, language_code="en"):
    """
    Tokenizes text into individual words using SpaCy based on the language.
    Args:
        text (str): The input text.
        language_code (str): The language code of the text.
    Returns:
        list: A list of words (tokens).
    """
    nlp = ensure_spacy_model(language=language_code)
    doc = nlp(text)
    # Tokenize the text and filter out non-alphabetic tokens
    tokens = [token.text.lower() for token in doc if token.is_alpha]
    return tokens

def get_stop_words(language_code="en"):
    """Retrieve stopwords set based on language code."""
    language = LANGUAGE_MAP.get(language_code.lower(), language_code.lower())
    
    try:
        return set(stopwords.words(language))
    except LookupError:
        print(f"Stopwords for language code '{language_code}' not found. Using an empty set.")
        return set()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return set()
    
def normalize_words(tokens, language_code):
    """
    Normalizes words by lemmatizing and filtering out stopwords.
    Args:
        tokens (list): List of words (tokens) to normalize.
        language_code (str): The language code of the text.
    Returns:
        list: A list of normalized words.
    """
    STOP_WORDS = get_stop_words(language_code)
    lemmatized_words = []
    nlp = ensure_spacy_model(language=language_code)
    for word in tokens:
        if word not in STOP_WORDS:
            doc = nlp(word)
            for token in doc:
                lemma = token.lemma_
                # Add 'to' only if the token is identified as a verb in infinitive form
                if language_code == "en" and token.pos_ == "VERB":
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

def process_text(file_path, known_words, input_language):
    """
    Processes text from a file, normalizes and deduplicates it, then filters out known words.
    Args:
        file_path (str): Path to the text file to process.
        known_words (set): Set of known words to exclude.
        input_language (str): The language code of the input text.
    Returns:
        list: List of unknown words in the text.
    """
    # Read text from file
    text = read_text_file(file_path)
    if not text:
        return []  # Return empty word list if file is empty or not found
    
    # Tokenize the text
    tokens = tokenize_text(text, input_language)

    # Normalize (lemmatize) the tokens
    normalized_words = normalize_words(tokens, input_language)

    # Deduplicate the list of words
    unique_words = deduplicate_words(normalized_words)

    # Filter out known words
    unknown_words = filter_known_words(unique_words, known_words)

    return unknown_words
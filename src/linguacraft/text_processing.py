import logging
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
    "af": "af_core_news_sm",
    "bg": "bg_core_news_sm",
    "bn": "bn_core_news_sm",
    "ca": "ca_core_news_sm",
    "cs": "cs_core_news_sm",
    "da": "da_core_news_sm",
    "de": "de_core_news_sm",
    "el": "el_core_news_sm",
    "es": "es_core_news_sm",
    "et": "et_core_news_sm",
    "fa": "fa_core_news_sm",
    "fi": "fi_core_news_sm",
    "fr": "fr_core_news_sm",
    "ga": "ga_core_news_sm",
    "he": "he_core_news_sm",
    "hi": "hi_core_news_sm",
    "hr": "hr_core_news_sm",
    "hu": "hu_core_news_sm",
    "id": "id_core_news_sm",
    "it": "it_core_news_sm",
    "ja": "ja_core_news_sm",
    "ko": "ko_core_news_sm",
    "lt": "lt_core_news_sm",
    "lv": "lv_core_news_sm",
    "mk": "mk_core_news_sm",
    "nb": "nb_core_news_sm",
    "nl": "nl_core_news_sm",
    "pl": "pl_core_news_sm",
    "pt": "pt_core_news_sm",
    "ro": "ro_core_news_sm",
    "ru": "ru_core_news_sm",
    "sk": "sk_core_news_sm",
    "sl": "sl_core_news_sm",
    "sv": "sv_core_news_sm",
    "ta": "ta_core_news_sm",
    "th": "th_core_news_sm",
    "tl": "tl_core_news_sm",
    "tr": "tr_core_news_sm",
    "uk": "uk_core_news_sm",
    "ur": "ur_core_news_sm",
    "vi": "vi_core_news_sm",
    "zh": "zh_core_news_sm",
    }

# Predefined dictionary mapping language codes to NLTK stopwords languages
LANGUAGE_MAP = {
    "ar": "arabic",
    "az": "azerbaijani",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "fi": "finnish",
    "fr": "french",
    "hu": "hungarian",
    "id": "indonesian",
    "it": "italian",
    "kk": "kazakh",
    "ne": "nepali",
    "nl": "dutch",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sl": "slovene",
    "sv": "swedish",
    "tg": "tajik",
    "tr": "turkish",
}

def detect_language(text):
    """Detects the language of the given text."""
    try:
        return detect(text)
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return ""  # Default to empty string

# Load the spaCy model for lemmaization
def ensure_spacy_model(language):
    """Ensure the required spaCy model is downloaded."""
    model_name = SPACY_MODELS.get(language)
    try:
        return spacy.load(model_name)
    except Exception as e:
        logging.error(f"Downloading SpaCy model '{model_name}'...")
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
        logging.error(f"Error: The file at {file_path} was not found.")
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
    language = LANGUAGE_MAP.get(language_code.lower())

    try:
        return set(stopwords.words(language))
    except LookupError:
        logging.error(f"Stopwords for language code '{language_code}' not found. Using an empty set.")
        return set()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
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
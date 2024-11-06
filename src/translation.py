import openai
import requests
import os

# Set up API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

def get_definition(word):
    """
    Fetches the definition of a word using the OpenAI API.
    Args:
        word (str): The word to define.
    Returns:
        str: The definition of the word.
    """
    prompt = f"Provide a clear, concise dictionary definition for the word '{word}'."
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error fetching definition for '{word}': {e}")
        return "Definition not available"

def translate_word(word, target_language):
    """
    Translates a word into the target language using the Google Translate API.
    Args:
        word (str): The word to translate.
        target_language (str): The language code for the target language (e.g., 'es' for Spanish).
    Returns:
        str: The translated word.
    """
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": word,
        "target": target_language,
        "key": GOOGLE_TRANSLATE_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        response_data = response.json()
        return response_data["data"]["translations"][0]["translatedText"]
    except Exception as e:
        print(f"Error translating word '{word}': {e}")
        return "Translation not available"

def fetch_translation(unknown_words, target_language="ua"):
    """
    Fetches definitions and translations for a list of unknown words.
    Args:
        unknown_words (list): List of words to translate and define.
        target_language (str): The language code for the target language (default is 'ua').
    Returns:
        dict: A dictionary where each word maps to its definition and translation.
    """
    translations = {}
    for word in unknown_words:
        definition = get_definition(word)
        translation = translate_word(word, target_language)
        translations[word] = {
            "definition": definition,
            "translation": translation,
        }
        print(f"Processed '{word}': Definition - '{definition}', Translation - '{translation}'")
    save_translations_to_file(translations)
    return translations

def save_translations_to_file(translations, filename="output.txt"):
    """
    Saves translations and definitions to a file.
    Args:
        translations (dict): Dictionary with words, their definitions, and translations.
        filename (str): The file name for saving the output.
    """
    with open(filename, "w", encoding="utf-8") as file:
        for word, info in translations.items():
            file.write(f"Word: {word}\n")
            file.write(f"Definition: {info['definition']}\n")
            file.write(f"Translation: {info['translation']}\n\n")
    print(f"Translations saved to {filename}")
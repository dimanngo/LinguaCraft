import logging
from openai import OpenAI
from deep_translator import GoogleTranslator
import requests
import os

# Set up API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
MICROSOFT_TRANSLATOR_API_KEY = os.getenv("MICROSOFT_TRANSLATOR_API_KEY")
MICROSOFT_TRANSLATOR_ENDPOINT = os.getenv("MICROSOFT_TRANSLATOR_ENDPOINT")

# Configure OpenAI API
OpenAI.api_key = OPENAI_API_KEY

def get_definition(word):
    """
    Fetches the definition of a word using the OpenAI API.
    """
    prompt = f"Provide a clear, concise dictionary definition for the word '{word}'."
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error fetching definition for '{word}': {e}")
        return "Definition not available"


def translate_word_google(word, target_language):
    """
    Translates a word into the target language using the Google Translate API.
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
        logging.error(f"Error translating word '{word}' using Google Translate: {e}")
        return "Translation not available"


def translate_word_microsoft(word, target_language):
    """
    Translates a word into the target language using the Microsoft Translator API.
    """
    url = f"{MICROSOFT_TRANSLATOR_ENDPOINT}/translate"
    headers = {
        "Ocp-Apim-Subscription-Key": MICROSOFT_TRANSLATOR_API_KEY,
        "Ocp-Apim-Subscription-Region": "global",
        "Content-Type": "application/json",
    }
    body = [{"Text": word}]
    params = {"to": target_language}
    try:
        response = requests.post(url, headers=headers, json=body, params=params)
        response_data = response.json()
        return response_data[0]["translations"][0]["text"]
    except Exception as e:
        logging.error(f"Error translating word '{word}' using Microsoft Translator: {e}")
        return "Translation not available"


def translate_word_deep(word, target_language):
    """
    Translates a word into the target language using Deep Translator.
    Supported providers: 'google', 'microsoft'.
    """
    try:
        return GoogleTranslator(target=target_language).translate(word)
    except Exception as e:
        logging.error(f"Error translating word '{word}' using Deep Translator (Google): {e}")
        return "Translation not available"


def translate_word(word, target_language, provider="deep-google"):
    """
    Translates a word into the target language using the specified provider.
    """
    if provider == "google":
        return translate_word_google(word, target_language)
    elif provider == "microsoft":
        return translate_word_microsoft(word, target_language)
    elif provider == "deep-google":
        return translate_word_deep(word, target_language)
    else:
        raise ValueError("Unsupported translation provider. Use 'google', 'microsoft', or 'deep-google'.")


def fetch_translation(unknown_words, target_language, provider="deep-google"):
    """
    Fetches definitions and translations for a list of unknown words.
    """
    translations = {}
    for word in unknown_words:
        definition = get_definition(word)
        translation = translate_word(word, target_language, provider=provider)
        translations[word] = {
            "definition": definition,
            "translation": translation,
        }
        logging.info(f"Processed '{word}': Definition - '{definition}', Translation - '{translation}'")
    save_translations_to_file(translations)
    return translations


def save_translations_to_file(translations, filename="output.txt"):
    """
    Saves translations and definitions to a file.
    """
    content = []
    for word, info in translations.items():
        content.append(f"Word: {word}")
        content.append(f"Definition: {info['definition']}")
        content.append(f"Translation: {info['translation']}\n")
    content_str = "\n".join(content)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content_str)
    logging.info(f"Translations saved to {filename}")
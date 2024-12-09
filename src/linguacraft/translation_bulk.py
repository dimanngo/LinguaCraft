import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
import pathlib

# Explicitly load .env file from current directory
env_path = pathlib.Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure OpenAI API
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def fetch_definitions_bulk(unknown_words, input_language, target_language):
    """
    Fetches definitions and translations for a list of unknown words.
    Args:
        unknown_words (list): List of words to translate and define.
        target_language (str): The language code for the target language (default is 'ua').
    """
    definitions = get_definition_bulk(unknown_words, input_language, target_language)
    save_output_file(definitions)

def get_definition_bulk(words, input_language, target_language):
    """
    Fetches definitions and translations for a list of unknown words.
    Args:
        words (list): List of words to define.
    Returns:
        llm_response (str): The response from the OpenAI API, formatted as a list of words and their definitions.
    """
    
    prompt = f"Provide clear and concise dictionary definitions in '{input_language}', and translations from '{input_language}' into '{target_language}' for the following words:\n"
    prompt += "\n".join(words)
    prompt += "\n\nFormat the response as 'word:\tdefinition; translation'. For example:\n'car:\ta vehicle with four wheels; машина'."

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
        llm_response = completion.choices[0].message.content.strip()
        return llm_response
    except Exception as e:
        logging.error(f"Error fetching definitions and translations: {e}")
        return(f"Error fetching definitions and translations: {e}")

def save_output_file(definitions, filename="output.txt"):
    """
    Saves definitions to a file.
    Args:
        definitions (str): Dictionary with words and their definitions.
        filename (str): The file name for saving the output.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(definitions)
    logging.info(f"Definitions saved to {filename}")
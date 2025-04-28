# c:\Users\1134931\chat_bot\app\config.py
import json
import os
import logging

# Get a logger specific to this module
logger = logging.getLogger(__name__)
# Basic configuration if no root logger is set yet (won't override if already configured by run.py)
# This basicConfig might be removed if run.py handles it definitively.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Use a known valid model name
GEMINI_MODEL_NAME = "gemini-2.5-pro-exp-03-25"

# --- Load API Key ---
API_KEY = None
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE_PATH = os.path.join(CONFIG_DIR, "keys.json")

try:
    logger.info(f"Attempting to load API key from: {KEYS_FILE_PATH}")
    if os.path.exists(KEYS_FILE_PATH):
        with open(KEYS_FILE_PATH, 'r') as f:
            keys = json.load(f)
            API_KEY = keys.get("gemini_api_key")
            if API_KEY:
                logger.info("API key loaded successfully from keys.json.")
            else:
                logger.warning(f"Found {KEYS_FILE_PATH}, but 'gemini_api_key' key is missing or empty.")
    else:
        logger.info(f"{KEYS_FILE_PATH} not found. Checking environment variable GEMINI_API_KEY.")
        API_KEY = os.environ.get("GEMINI_API_KEY")
        if API_KEY:
            logger.info("API key loaded successfully from environment variable.")

    if not API_KEY:
        error_message = f"Gemini API key not found. Please create '{KEYS_FILE_PATH}' with format {{ \"gemini_api_key\": \"YOUR_API_KEY\" }} or set the environment variable GEMINI_API_KEY."
        logger.error(error_message)
        # Consider if raising an error here is desired, or if the app should proceed
        # and let gemini_client handle the None key. Raising it stops the app earlier.
        raise ValueError(error_message)

except (FileNotFoundError, json.JSONDecodeError, ValueError, Exception) as e:
    logger.error(f"Error loading configuration: {e}", exc_info=True)
    API_KEY = None # Ensure API_KEY is None if loading fails

# --- Prompt Template ---
PROMPT_TEMPLATE = """
You are a mean chatbot responding to a user.
You have been given some background information about this user.

USER BACKSTORY:
{backstory}

Based on this backstory, respond to the user's following request.
Your response should directly answer the request, while ostentatiously (or sometimes cheekily, depending on the context) weave in weaknesses, elements or the overall tone suggested by their backstory.

USER REQUEST:
{user_prompt}

YOUR RESPONSE:
"""

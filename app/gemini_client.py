import google.generativeai as genai
from .config import API_KEY, GEMINI_MODEL_NAME, PROMPT_TEMPLATE
import logging # Added for better error reporting

# Get logger instance - configuration should happen in the main entry point (run.py or main.py)
logger = logging.getLogger(__name__)

# Configure the Gemini client
model = None # Initialize model to None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        logger.info(f"Gemini client configured successfully for model: {GEMINI_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to configure Gemini client: {e}", exc_info=True) # Log traceback
        model = None # Ensure model is None if configuration fails
else:
    # This log might be redundant if config.py already logged/raised an error
    logger.error("Gemini API Key was not available during client initialization.")
    model = None

def generate_response(backstory: str, user_prompt: str) -> str:
    """
    Generates a response from Gemini using the user's backstory and prompt.

    Args:
        backstory: The predefined backstory of the user.
        user_prompt: The user's current request or question.

    Returns:
        The generated response string from Gemini, or an error message.
    """
    if not model:
        logger.error("generate_response called but Gemini client is not initialized.")
        return "Error: Gemini client is not initialized. Please check API key and configuration logs."
    if not backstory:
        logger.warning("generate_response called without backstory.")
        return "Error: Please provide a user backstory."
    if not user_prompt:
        logger.warning("generate_response called without user_prompt.")
        return "Error: Please provide a user prompt."

    try:
        # Construct the full prompt using the template
        full_prompt = PROMPT_TEMPLATE.format(backstory=backstory, user_prompt=user_prompt)

        logger.info("Sending prompt to Gemini...")
        # print(f"--- DEBUG: Sending Prompt ---\n{full_prompt}\n--------------------------") # Uncomment for debugging

        response = model.generate_content(full_prompt)

        # Handle potential safety blocks or empty responses
        # Check for prompt_feedback existence before accessing block_reason
        prompt_feedback = getattr(response, 'prompt_feedback', None)
        if not response.parts:
             if prompt_feedback and prompt_feedback.block_reason:
                 block_reason = prompt_feedback.block_reason
                 logger.warning(f"Gemini response blocked. Reason: {block_reason}")
                 # Provide a more user-friendly message if possible
                 return f"My response was blocked due to safety settings ({block_reason}). Please try phrasing your request differently."
             else:
                 # If not blocked, it's likely just an empty response
                 logger.warning("Gemini returned an empty response with no blocking reason.")
                 return "Sorry, I couldn't generate a response for that. Please try again or rephrase your request."

        # Accessing response.text is simpler if parts exist
        generated_text = response.text
        logger.info("Received response from Gemini.")
        # print(f"--- DEBUG: Received Response ---\n{generated_text}\n--------------------------") # Uncomment for debugging
        return generated_text.strip()

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}", exc_info=True) # Log traceback
        # Consider more specific error handling based on potential API errors
        return f"An error occurred while contacting the AI model. Please check the logs for details."

# Example usage (optional, for testing this module directly)
# Note: Running this directly will fail because of the relative import '.config'
if __name__ == "__main__":
    print("Attempting direct execution (will likely fail due to relative imports)...")
    # This block will raise ImportError: attempted relative import with no known parent package
    # To test this module, you might need to temporarily change imports or use a test runner
    # that understands package structures.
    # test_backstory = "A recently divorced man in his late 30s, trying to learn basic life skills he previously relied on his partner for. He's feeling a bit lost but determined."
    # test_prompt = "Can you give me a simple recipe for baked salmon?"
    # print(f"Testing Gemini Client:\nBackstory: {test_backstory}\nPrompt: {test_prompt}\n")
    # response = generate_response(test_backstory, test_prompt)
    # print(f"Generated Response:\n{response}")

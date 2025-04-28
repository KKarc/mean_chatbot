# c:\Users\1134931\chat_bot\app\gradio_interface.py
import gradio as gr
import json
import os
import logging
# Assuming gemini_client.py handles text generation based on backstory
from .gemini_client import generate_response
# We are not using imagen_client anymore for this approach
# from .imagen_client import generate_image_from_text

# Get logger instance
logger = logging.getLogger(__name__)

# --- Configuration ---
# Define the base path for relative image paths in backstories.json
# Assuming 'images' folder is at the root of the chat_bot project
IMAGE_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))
logger.info(f"Image base path set to: {IMAGE_BASE_PATH}")


# --- Load Backstories ---
BACKSTORIES_FILE_PATH = os.path.join(os.path.dirname(__file__), "backstories.json")
# backstories_data will store the full object: {"backstory": "...", "image": "..."}
backstories_data = {}
persona_names = []
default_persona_info = None # Store the info for the default persona

try:
    if os.path.exists(BACKSTORIES_FILE_PATH):
        with open(BACKSTORIES_FILE_PATH, 'r', encoding='utf-8') as f:
            loaded_json = json.load(f)
            if isinstance(loaded_json, dict):
                # Validate structure slightly - ensure values are dicts with 'backstory'
                valid_data = {}
                for name, data in loaded_json.items():
                    if isinstance(data, dict) and "backstory" in data:
                        valid_data[name] = data # Store the whole dict {backstory, image?}
                    else:
                         logger.warning(f"Skipping persona '{name}': Invalid format or missing 'backstory' key in backstories.json.")

                backstories_data = valid_data
                persona_names = list(backstories_data.keys())

                # Get info for the default persona (first valid one)
                if persona_names:
                    default_persona_info = backstories_data.get(persona_names[0])

                if not persona_names:
                    logger.warning(f"{BACKSTORIES_FILE_PATH} is empty or has no valid personas.")
                else:
                    logger.info(f"Successfully loaded {len(persona_names)} personas from {BACKSTORIES_FILE_PATH}.")
            else:
                 logger.error(f"Invalid format in {BACKSTORIES_FILE_PATH}. Expected a JSON object (dictionary).")
                 persona_names = ["Error: Invalid JSON format"]

    else:
        logger.error(f"Backstories file not found at: {BACKSTORIES_FILE_PATH}")
        persona_names = ["Error: backstories.json not found"]
except json.JSONDecodeError:
    logger.error(f"Error decoding JSON from {BACKSTORIES_FILE_PATH}.", exc_info=True)
    persona_names = ["Error: Invalid JSON in backstories.json"]
except Exception as e:
    logger.error(f"An unexpected error occurred loading backstories: {e}", exc_info=True)
    persona_names = ["Error: Could not load backstories"]
# --- End Load Backstories ---


def handle_submission(selected_persona_name: str, user_prompt: str) -> str:
    """
    Wrapper function to get the backstory text based on the selected name
    and then call the actual generation function.
    """
    if not selected_persona_name or "Error:" in selected_persona_name:
        logger.warning("Submission attempt with invalid persona selection.")
        return "Error: Please select a valid persona from the dropdown."
    if not user_prompt:
        logger.warning("Submission attempt with empty prompt.")
        # Let generate_response handle the specific error message
        return generate_response("", user_prompt) # Pass empty backstory

    # Get the persona data object
    persona_info = backstories_data.get(selected_persona_name)

    if not isinstance(persona_info, dict) or "backstory" not in persona_info:
        logger.error(f"Incomplete or invalid data for persona '{selected_persona_name}'.")
        return f"Error: Internal mismatch. Could not find backstory details for '{selected_persona_name}'."

    backstory_text = persona_info["backstory"]

    logger.info(f"Generating response for persona '{selected_persona_name}'.")
    return generate_response(backstory_text, user_prompt)

# --- Function to update the image display ---
def update_local_image(selected_persona_name: str) -> tuple[str | None, gr.update]:
    """
    Gets the local image path for the selected persona, if available and valid.
    Returns the image path (or None) and a Gradio update object for visibility.
    """
    image_path_to_load = None
    is_visible = False

    if selected_persona_name and "Error:" not in selected_persona_name:
        persona_info = backstories_data.get(selected_persona_name)
        if isinstance(persona_info, dict):
            relative_image_path = persona_info.get("image") # Get the path like "images/bartek.jpg"
            if relative_image_path:
                # Construct full path relative to the defined base path
                full_image_path = os.path.join(IMAGE_BASE_PATH, os.path.normpath(relative_image_path))
                logger.debug(f"Checking for image at: {full_image_path}")
                if os.path.exists(full_image_path):
                    image_path_to_load = full_image_path
                    is_visible = True
                    logger.info(f"Found local image for '{selected_persona_name}': {full_image_path}")
                else:
                    logger.warning(f"Image path specified for '{selected_persona_name}' but file not found: {full_image_path}")
            else:
                 logger.debug(f"No 'image' key found for persona '{selected_persona_name}'.")
        else:
             logger.warning(f"Could not find persona data for '{selected_persona_name}' when updating image.")

    # Return the path (or None) and the visibility update
    return image_path_to_load, gr.update(visible=is_visible)
# --- End image update function ---


def create_chatbot_interface():
    """Creates the Gradio interface for the chatbot."""

    custom_css = """
    /* ... (your existing CSS rules) ... */

    /* Style the local image component */
    #persona-local-image img { /* Target the img element */
        max-height: 200px; /* Adjust size as needed */
        max-width: 100%; /* Ensure it fits column width */
        object-fit: contain;
        display: block;
        margin-top: 10px; /* Space above image */
        border-radius: 8px;
        /* box-shadow: 0 1px 3px rgba(0,0,0,0.1); */ /* Optional shadow */
    }
    #persona-local-image { /* Target the component container */
       min-height: 50px; /* Prevent layout jump when hidden */
       margin-top: 15px; /* Add some space below the prompt input */
    }
    """

    # --- Determine initial image state ---
    initial_image_path, initial_visibility = None, gr.update(visible=False)
    if default_persona_info:
        # Use the update function to get initial state based on default selection
        initial_image_path, initial_visibility = update_local_image(persona_names[0])
    # --- End initial image state ---


    with gr.Blocks(theme=gr.themes.Soft(), title="Persona Chatbot", css=custom_css) as interface:
        gr.Markdown("# Persona Chatbot")
        gr.Markdown(
            "Select a persona and enter a prompt. The chatbot will respond, "
            "incorporating the persona's hidden backstory into its answer."
        )

        with gr.Row():
            # --- Left Column ---
            with gr.Column(scale=1):
                persona_selector = gr.Dropdown(
                    label="Select Persona",
                    choices=persona_names,
                    value=persona_names[0] if persona_names and "Error:" not in persona_names[0] else None,
                    info="Choose the user persona.",
                    elem_id="persona-dropdown"
                )
                prompt_input = gr.Textbox(
                    label="User Prompt",
                    placeholder="e.g., Give me a simple recipe for salmon.",
                    lines=5,
                    info="What does the user want to ask or know?"
                )

                # --- Add the Image component for local files ---
                # Place it here, below the prompt in the left column
                persona_local_image = gr.Image(
                    label="Persona Image",
                    value=initial_image_path, # Set initial image
                    visible=initial_visibility['visible'], # Set initial visibility
                    elem_id="persona-local-image",
                    show_label=False, # Hide label if desired
                    interactive=False,
                    type="filepath" # Expecting a file path
                )
                # --- End Image component ---

            # --- Right Column ---
            with gr.Column(scale=2):
                output_response = gr.Textbox(
                    label="Chatbot Response",
                    lines=15, # Adjusted lines slightly
                    interactive=False
                )

        # --- Event Listeners ---
        # Update image when dropdown selection changes
        persona_selector.change(
            fn=update_local_image,
            inputs=persona_selector,
            # Output path to the image value, and visibility update to the image component itself
            outputs=[persona_local_image, persona_local_image]
        )

        # Handle text generation on button click
        submit_button = gr.Button("Get Response", variant="primary") # Moved button definition here for clarity
        submit_button.click(
            fn=handle_submission,
            inputs=[persona_selector, prompt_input],
            outputs=output_response,
            show_progress="minimal"
        )
        # --- End Event Listeners ---

    return interface

# Main block remains the same
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("Launching Gradio interface directly for testing...")
    # Make sure the 'images' directory exists relative to the project root if needed
    if not os.path.exists(IMAGE_BASE_PATH):
         logger.warning(f"Image base path directory does not exist: {IMAGE_BASE_PATH}")
         # os.makedirs(IMAGE_BASE_PATH) # Optionally create it

    try:
        app = create_chatbot_interface()
        app.launch()
    except ImportError as e:
        print(f"ImportError: {e}. Running this file directly might fail.")
        print("Try running using 'python run.py' from the 'chat_bot' parent directory.")
    except Exception as e:
        print(f"An error occurred during launch: {e}")
        logger.error("Error during Gradio launch", exc_info=True)


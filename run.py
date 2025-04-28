# c:\Users\1134931\chat_bot\run.py
import logging
import gradio as gr
# Import directly from the gradio_interface module
from app.gradio_interface import create_chatbot_interface

# --- Configure logging centrally ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # Optional: Add a file handler
    # handlers=[
    #     logging.FileHandler("chatbot.log"),
    #     logging.StreamHandler() # Keep console output
    # ]
)

if __name__ == "__main__":
    logging.info("Creating Gradio interface...")
    try:
        # Create the Gradio interface instance
        chatbot_interface = create_chatbot_interface()

        logging.info("Launching Gradio interface...")
        # Launch the Gradio app using its built-in server
        # Set share=False for local development unless you need a public link
        # Set server_name="0.0.0.0" to make it accessible on your local network
        chatbot_interface.launch(server_name="0.0.0.0", server_port=7860, share=False)

    except ImportError as e:
        logging.error(f"Import error: {e}. Please ensure all dependencies are installed and relative imports are correct.", exc_info=True)
    except Exception as e:
        logging.exception("An error occurred while creating or launching the Gradio interface.")


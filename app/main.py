# c:\Users\1134931\chat_bot\app\main.py
from flask import Flask
import gradio as gr
from .gradio_interface import create_chatbot_interface
import logging

# Configure logging (ensure it's configured only once, e.g., here or in run.py)
# If run.py also configures it, you might remove this line to avoid potential conflicts.
# However, having it here ensures main.py can log even if run differently.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create the Flask app instance
flask_app = Flask(__name__) # Use a different variable name initially to avoid confusion

# Create the Gradio interface
logging.info("Creating Gradio interface...")
gradio_interface = create_chatbot_interface()
logging.info("Gradio interface created.")

# Mount the Gradio interface onto the Flask app at the root path '/'
# Call the function without reassigning the flask_app variable
logging.info("Mounting Gradio interface onto Flask app...")
gr.mount_gradio_app(flask_app, gradio_interface, path="/")
logging.info("Gradio interface mounted successfully at path '/'")

# You can add other Flask routes here if needed, using flask_app
@flask_app.route("/health")
def health_check():
    """A simple health check endpoint."""
    logging.info("Health check endpoint accessed.")
    return "OK", 200

# Rename the final variable back to 'app' so run.py can import it
app = flask_app
logging.info("Flask app setup complete.")

# Note: We don't run app.run() here; that's handled by run.py or a WSGI server.

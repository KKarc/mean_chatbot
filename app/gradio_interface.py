import gradio as gr
from .gemini_client import generate_response # Import the function that calls Gemini

def create_chatbot_interface():
    """Creates the Gradio interface for the chatbot."""

    with gr.Blocks(theme=gr.themes.Soft(), title="Persona Chatbot") as interface:
        gr.Markdown("# Persona Chatbot")
        gr.Markdown(
            "Enter a user backstory and a prompt, and the chatbot will respond, "
            "incorporating the backstory into its answer."
        )

        with gr.Row():
            with gr.Column(scale=1):
                backstory_input = gr.Textbox(
                    label="User Backstory",
                    placeholder="e.g., A recently divorced man trying to learn cooking...",
                    lines=5,
                    info="Describe the user's background context."
                )
                prompt_input = gr.Textbox(
                    label="User Prompt",
                    placeholder="e.g., Give me a simple recipe for salmon.",
                    lines=3,
                    info="What does the user want to ask or know?"
                )
                submit_button = gr.Button("Get Response", variant="primary")

            with gr.Column(scale=2):
                output_response = gr.Textbox(
                    label="Chatbot Response",
                    lines=10,
                    interactive=False # Output is not editable by user
                )

        # Define the action when the button is clicked
        submit_button.click(
            fn=generate_response, # The function to call
            inputs=[backstory_input, prompt_input], # Map inputs to function arguments
            outputs=output_response # Map function output to the output component
        )

        # Add some examples for users to try
        gr.Examples(
            examples=[
                ["A recently divorced man in his late 30s, trying to learn basic life skills he previously relied on his partner for.", "Can you give me a simple recipe for baked salmon?"],
                ["A stressed college student juggling exams and a part-time job. They love fantasy novels and need quick, cheap meal ideas.", "What's a super fast dinner I can make after work?"],
                ["An aspiring musician who just moved to a new city and feels lonely.", "Suggest some ways to meet new people."],
                ["A retiree who loves gardening but has mobility issues.", "What are some easy-to-maintain plants for containers?"]
            ],
            inputs=[backstory_input, prompt_input],
            outputs=output_response,
            fn=generate_response, # The function needs to be specified for examples too
            cache_examples=False # Disable caching if API calls are involved or change frequently
        )

    return interface

# To test the Gradio interface directly (optional)
if __name__ == "__main__":
    print("Launching Gradio interface directly for testing...")
    app = create_chatbot_interface()
    app.launch()

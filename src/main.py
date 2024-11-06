from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Label
from textual.reactive import reactive
from textual.containers import Container, Horizontal
from text_processing import process_text  # Custom file with text processing functions
from known_words import load_known_words  # Manages known words persistence
from translation import fetch_translation  # Manages API calls for translations

class LinguaLearnApp(App):
    async def on_mount(self):
        """Set up the main UI components."""
        # Add header and footer
        await self.mount(Header())
        await self.mount(Footer())

        # Set up input fields and button
        self.file_input = Input(placeholder="Enter file path here", id="file_input")
        self.lang_input = Input(placeholder="Default is 'en'", id="lang_input")
        self.run_button = Button(label="Run Analysis", id="run_button")

        # Create containers for layout
        input_container = Container(
            Label("Select a file with text to process:"),
            self.file_input,
            Label("Enter your native language (e.g., 'en', 'es'):"),
            self.lang_input,
        )

        button_container = Container(self.run_button)
        self.output_widget = Static("", id="output_message")

        output_container = Container(self.output_widget)

        # Mount all containers in the main app
        await self.mount(Horizontal(input_container, button_container, output_container))

    async def on_button_pressed(self, event):
        """Handle button click events."""
        # Ensure the button ID matches our Run Analysis button
        if event.button.id == "run_button":
            await self.run_analysis()

    async def run_analysis(self):
        """Initial processing step to load and display potential unknown words."""
        # Get the values from the input fields directly
        selected_file = self.file_input.value.strip()
        native_language = self.lang_input.value.strip() or "en"

        # Output message to show progress
        self.output_widget.update("Analysis in progress...")

        # Load known words
        known_words = load_known_words()
        if not selected_file:
            self.output_widget.update("Please enter a valid file path.")
            return

        # Process text and get unknown words
        unknown_words = process_text(selected_file, known_words)
        
        # Fetch translations and definitions
        fetch_translation(unknown_words, native_language)
        
        # Update the output message
        self.output_widget.update("Analysis complete! Check output.txt for results.")

if __name__ == "__main__":
    LinguaLearnApp().run()
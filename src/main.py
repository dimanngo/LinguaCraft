from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Label, ListView, ListItem
from textual.reactive import reactive
from textual.containers import Container, Horizontal
from textual.events import Key

from text_processing import process_text  # Custom file with text processing functions
from known_words import load_known_words, update_known_words  # Manages known words persistence
from translation import fetch_translation  # Manages API calls for translations

class WordItem(ListItem):
    """Custom list item to represent a word with its known/unknown status."""
    def __init__(self, word):
        super().__init__()
        self.word = word
        self.is_known = False  # Default status is unknown
        self.label = Static(f"{self.word} (Unknown)")

    async def on_mount(self):
        """Mount the label after WordItem itself is mounted."""
        await self.mount(self.label)

    def toggle_status(self):
        """Toggle the word's known/unknown status and update display."""
        self.is_known = not self.is_known
        self.label.update(f"{self.word} ({'Known' if self.is_known else 'Unknown'})")

class LinguaLearnApp(App):
    selected_file = reactive("")
    native_language = reactive("en")
    word_items = reactive([])  # List of WordItem objects
    selected_index = reactive(0)  # Index of the currently selected word item
    new_known_words = reactive([])  # Track newly marked known words

    async def on_mount(self):
        """Set up the main UI components."""
        # Add header and footer
        await self.mount(Header())
        await self.mount(Footer())

        # Input fields for file path and language
        self.file_input = Input(placeholder="Enter file path here", id="file_input")
        self.lang_input = Input(placeholder="Default is 'en'", id="lang_input")
        self.run_button = Button(label="Run Analysis", id="run_button")

        # Set up input containers and add to layout
        input_container = Container(
            Label("Select a file with text to process:"),
            self.file_input,
            Label("Enter your native language (e.g., 'en', 'es'):"),
            self.lang_input,
            self.run_button,
        )

        
        # button_container = Container(self.run_button)
        
        self.output_widget = Static("", id="output_message")
        output_container = Container(self.output_widget)

        # Mount all containers in the main app
        await self.mount(Horizontal(input_container, output_container))

    async def on_button_pressed(self, event):
        """Handle button click events."""
        # Ensure the button ID matches our Run Analysis button and check the flag
        if event.button.id == "run_button" and not event.button.disabled:
            await self.run_analysis()

    async def run_analysis(self):
        """Process text, generate word items list, and display interactive classification."""
        # Disable the button to prevent multiple executions
        self.run_button.disabled = True

        selected_file = self.file_input.value.strip()
        native_language = self.lang_input.value.strip() or "en"

        # Output message to show progress
        self.output_widget.update("Loading words for classification...")

        # Load known words and process input text
        known_words = load_known_words()
        if not selected_file:
            self.output_widget.update("Please enter a valid file path.")
            self.run_button.disabled = False  # Re-enable the button on error
            return

        # Process text and get unknown words
        unknown_words = process_text(selected_file, known_words)

        # Generate WordItem objects for each unknown word
        self.word_items = [WordItem(word) for word in unknown_words]
        
        # Display the word list for classification
        self.word_list_view = ListView(*self.word_items)
        await self.mount(self.word_list_view)
        self.set_focus(self.word_list_view)  # Set focus to the word list view initially
        self.output_widget.update("Navigate the list with up/down arrow keys.\nUse K and U keys to toggle known/unknown status.\nPress <ENTER> when you finish.")

    async def on_key(self, event: Key):
        """Handle key presses for marking words and finalizing the list."""
        # Ensure key handling only occurs if word_list_view exists and is focused
        if hasattr(self, "word_list_view") and self.focused is self.word_list_view:
            # Navigate the list with up/down arrow keys
            if event.key == "up":
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == "down":
                self.selected_index = min(len(self.word_items) - 1, self.selected_index + 1)

            # Get the currently selected word item
            current_item = self.word_items[self.selected_index]

            # Handle 'K' and 'U' keys to toggle known/unknown status
            if event.key == "k":
                current_item.is_known = True
                current_item.label.update(f"{current_item.word} (Known)")
                if current_item.word not in self.new_known_words:
                    self.new_known_words.append(current_item.word)

            elif event.key == "u":
                current_item.is_known = False
                current_item.label.update(f"{current_item.word} (Unknown)")
                if current_item.word in self.new_known_words:
                    self.new_known_words.remove(current_item.word)

            # Finalize list and process on Enter key
            elif event.key == "enter":
                # Update known words file once with the accumulated known words
                if self.new_known_words:
                    update_known_words(self.new_known_words)
                await self.finalize_and_translate()

    async def finalize_and_translate(self):
        """Finalize word classification and proceed with translation."""
        unknown_words = [item.word for item in self.word_items if not item.is_known]

        # Fetch translations and definitions for unknown words
        self.output_widget.update("Fetching translations and definitions...")
        fetch_translation(unknown_words, self.native_language)

        # Display completion message
        self.output_widget.update("Analysis complete! Check output.txt for results.")
        
        # Remove the word list view after finalizing
        await self.word_list_view.remove()

        # Re-enable the button after the analysis is complete
        self.run_button.disabled = False

if __name__ == "__main__":
    LinguaLearnApp().run()
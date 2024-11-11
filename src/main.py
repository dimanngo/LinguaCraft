# Import necessary modules from Textual library
from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Label, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import Reactive
from textual.events import Key

# Import necessary modules from Textual library for screen management
from textual import on, work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label

class QuestionScreen(Screen[bool]):
    """Screen with a parameter."""

    def __init__(self, question: str) -> None:
        self.question = question
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.question)
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no")

    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)  

    @on(Button.Pressed, "#no")
    def handle_no(self) -> None:
        self.dismiss(False)

# Import custom modules for text processing, known words management, and translation
from text_processing import process_text  # Custom file with text processing functions
from known_words import load_known_words, update_known_words # Manages known words persistence
# from translation import fetch_translation  # Manages API calls for translations
from translation_bulk import fetch_definitions  # Manages Open API calls for definitions and translations 

class WordItem(ListItem):
    """Custom list item to represent a word with its known/unknown status."""
    def __init__(self, word):
        super().__init__()
        self.word = word
        self.is_known = False  # Default status is unknown
        self.label = Static(f"{self.word} (Unknown)")
        self.label.styles.color = "red"  # Set initial color for "Unknown" status

    async def on_mount(self):
        """Mount the label after WordItem itself is mounted."""
        await self.mount(self.label)

    def toggle_status(self):
        """Toggle the word's known/unknown status and update display."""
        self.is_known = not self.is_known
        status = "Known" if self.is_known else "Unknown"
        color = "grey" if self.is_known else "red"
        self.label.update(f"{self.word} ({status})")
        self.label.styles.color = color  # Change color based on status

class LinguaLearnApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    InputWithLabel {
        width: 80%;
        margin: 1;
    }
    """

    word_items = Reactive([])  # List of WordItem objects
    selected_index = Reactive(0)  # Index of the currently selected word item
    new_known_words = Reactive([])  # Track newly marked known words

    async def on_mount(self):
        """Set up the main UI components."""
        # Add header and footer
        await self.mount(Header())
        await self.mount(Footer())

        # Input fields for file path and language with labels
        file_input_label = Label("File path:")
        self.file_input = Input(placeholder="Enter file path here", id="file_input")
        
        lang_input_label = Label("Native language code:")
        self.lang_input = Input(placeholder="Default is 'en'", id="lang_input")
        
        # Run Analysis button
        self.run_button = Button(label="Run Analysis", id="run_button")

        # Group inputs and button vertically with clear labels
        input_container = Vertical(
            Horizontal(file_input_label, self.file_input),
            Horizontal(lang_input_label, self.lang_input),
            self.run_button,
            classes="input-container",
        )

        # Output status widget
        self.output_widget = Static("", classes="output-widget")
        output_container = Container(self.output_widget)

        # Layout containers for organization
        layout = Vertical(
            input_container,
            Label("Analysis Output", classes="section-label"),
            output_container,
            classes="main-layout",
        )

        await self.mount(layout)

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
        
        # Display the word list for classification with clear labels
        self.word_list_view = ListView(*self.word_items, classes="word-list-view")
        await self.mount(Vertical(Label("Classify Words"), self.word_list_view))
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

            # Call `toggle_status` based on the key pressed
            if event.key == "k":
                if not current_item.is_known:
                    current_item.toggle_status()

            elif event.key == "u":
                if current_item.is_known:
                    current_item.toggle_status()

            # Finalize list and process on Enter key
            elif event.key == "enter":
                # Collect known words to update
                known_words_to_update = [item.word for item in self.word_items if item.is_known]
                if known_words_to_update:
                    update_known_words(known_words_to_update)
                
                self.finalize_and_translate()
    
    @work
    async def finalize_and_translate(self):
        """Finalize word classification and proceed with translation."""

        native_language = self.lang_input.value.strip() or "en"
        unknown_words = [item.word for item in self.word_items if not item.is_known]

        # Fetch translations and definitions for unknown words
        self.notify("Fetching translations and definitions...")
        self.output_widget.update("Fetching translations and definitions...")
        ############ fetch_definitions(unknown_words, native_language)

        # Display completion message
        self.notify("Analysis complete! Check output.txt for results.")
        self.output_widget.update("Analysis complete! Check output.txt for results.")

        # Show modal window with question: "Would you like to add all the unknown words to the known words list?"
        # If yes, add all unknown words to known words list file and save it (call update_known_words(unknown_words))
        # If no, do nothing
        if await self.push_screen_wait(  
            QuestionScreen("Would you like to add all the unknown words to the known words list?"),
        ):
            update_known_words(unknown_words)
            self.notify("All unknown words added to known words list.", severity="information")
        else:
            self.notify("Unknown words not added to known words list.", severity="warning")
        
        # Remove the word list view after finalizing
        await self.word_list_view.remove()

        # Re-enable the button after the analysis is complete
        self.run_button.disabled = False

if __name__ == "__main__":
    LinguaLearnApp().run()
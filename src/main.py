# Import necessary modules from Textual library
from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Label, ListView, ListItem
from textual.widget import Widget
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.reactive import reactive
from textual.events import Key

# Import necessary modules for Welcome Screen
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets._button import Button
from textual.widgets._static import Static

# Import necessary modules from Textual library for screen management
from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Label

# Screen 1: Welcome Screen
class WelcomeScreen(Screen):
    WELCOME_MD = """\
# Welcome!

Textual is a TUI, or *Text User Interface*, framework for Python inspired by modern web development. **We hope you enjoy using Textual!**

## Dune quote

> "I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."
"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Static(Markdown(self.WELCOME_MD), id="text"), id="md")
        yield Button("Next", id="next_button", variant="primary")
        yield Footer()

    async def on_button_pressed(self, event):
        if event.button.id == "next_button":
            await self.app.push_screen(InputScreen())

# Screen 2: Input Screen
class InputScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()

        # Input fields and labels
        yield Container(
            InputWithLabel("File path:", "Enter file path here", "file_input"),
            InputWithLabel("Native language code:", "Default is 'ua'", "lang_input")
        )

        yield Button("Run Analysis", id="run_analysis_button", variant="primary")
        
        yield Footer()

    async def on_button_pressed(self, event):
        if event.button.id == "run_analysis_button":
            await self.app.run_analysis()

# Screen 3: Word List Screen
class WordListScreen(Screen):
    selected_index = reactive(0)

    def __init__(self, word_items):
        super().__init__()
        self.word_items = word_items

    def compose(self):
        yield Header()
        yield Label("Unknown Words for Classification:")
        self.word_list_view = ListView(*self.word_items)
        yield self.word_list_view
        yield Footer()

    # @on(Key, "up")
    # def handle_up(self) -> None:
    #     pass

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

            # Toggle status for known and unknown words
            if event.key == "k":
                if not current_item.is_known:
                    current_item.toggle_status()
            elif event.key == "u":
                if current_item.is_known:
                    current_item.toggle_status()

            # Finalize list and process on Enter key
            elif event.key == "enter":
                known_words_to_update = [item.word for item in self.word_items if item.is_known]
                if known_words_to_update:
                    update_known_words(known_words_to_update)
                await self.app.finalize_and_translate()

class InputWithLabel(Widget):
    """An input with a label."""

    def __init__(self, input_label: str, input_placeholder: str, input_id: str) -> None:
        self.input_label = input_label
        self.input_placeholder = input_placeholder
        self.input_id = input_id
        super().__init__()

    def compose(self) -> ComposeResult:  
        yield Label(self.input_label)
        yield Input(placeholder=self.input_placeholder, id=self.input_id)

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
    CSS_PATH = "styles.tcss"  # Path to custom CSS file
    TITLE = "A Lingua Learn App"
    SUB_TITLE = "knows what you don't know"

    word_items = reactive([])

    async def on_mount(self):
        await self.push_screen(WelcomeScreen())  # Start with WelcomeScreen

    def on_key(self, event: Key):
        self.title = event.key
        self.sub_title = f"You just pressed {event.key}!"

    async def run_analysis(self):
        """Run the analysis and proceed to WordListScreen."""
        # Retrieve input values using query_one
        file_input = self.query_one("#file_input", Input)
        lang_input = self.query_one("#lang_input", Input)
        selected_file = file_input.value.strip()
        native_language = lang_input.value.strip() or "ua"

        # Load known words and process input text
        known_words = load_known_words()
        if not selected_file:
            print("Please enter a valid file path.")
            return

        unknown_words = process_text(selected_file, known_words)
        
        # Generate WordItem objects for each unknown word
        self.word_items = [WordItem(word) for word in unknown_words]
        
        # Transition to WordListScreen
        await self.push_screen(WordListScreen(self.word_items))
    
    async def finalize_and_translate(self):
        """Finalize word classification and proceed with translation."""
        unknown_words = [item.word for item in self.word_items if not item.is_known]
        
        # Fetch translations and definitions for unknown words
        ####### fetch_translation(unknown_words, "ua")
        
        # Display completion message
        print("Analysis complete! Check output.txt for results.")
        await self.pop_screen()  # Return to the previous screen after completion

    @work
    async def finalize_and_translate_old(self):
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
        self.run_analysis_button.disabled = False

if __name__ == "__main__":
    LinguaLearnApp().run()
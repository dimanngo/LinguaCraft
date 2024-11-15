# Import necessary modules from Textual library
from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Label, DataTable, TextArea, Digits
from textual.widget import Widget
from textual.containers import Container
from textual.screen import Screen
from textual.reactive import reactive
from textual import on
from textual import work

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

# Import custom modules for text processing, known words management, and translation
from text_processing import process_text  # Custom file with text processing functions
from known_words import load_known_words, update_known_words # Manages known words persistence
from translation import fetch_translation, translate_word  # Manages API calls for translations
from translation_bulk import fetch_definitions_bulk  # Manages Open API calls for definitions and translations

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
            InputWithLabel("Native language code:", "Default is 'ua'", "lang_input"),
            InputWithLabel("Output file path:", "Enter output file path here", "output_file_input")
        )

        yield Button("Run Analysis", id="run_analysis_button", variant="primary")
        
        yield Footer()

    def on_mount(self) -> None:
        self.app.sub_title = "give your text"

    async def on_button_pressed(self, event):
        if event.button.id == "run_analysis_button":
            await self.app.run_analysis()
class WordItem:
    """Represents a word with a known/unknown status."""
    def __init__(self, word):
        self.word = word
        self.is_known = False  # Default status is unknown
        self.translation = "---"  # Translation of the word
        self.definition = "---"  # Definition of the word

    def toggle_status(self, known=None):
        """Toggle or set the known/unknown status of the word."""
        if known is not None:
            self.is_known = known
        else:
            self.is_known = not self.is_known

    def display_status(self):
        """Return the display label based on the known/unknown status."""
        return "Known" if self.is_known else "Unknown"

# Screen 3 (New version with DataTable): Word List Screen
class WordListScreen(Screen):
    BINDINGS = [
        ("k", "mark_known", "Mark as Known"),
        ("u", "mark_unknown", "Mark as Unknown"),
        ('space', 'get_translation', 'Get Translation'),
    ]

    def __init__(self, word_items, translation_language):
        super().__init__()
        # Initialize WordItem instances and DataTable
        self.word_items = [WordItem(word.word) for word in word_items]
        self.translation_language = translation_language

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Unknown Words for Classification:"),
            DataTable(id="word_table")
        )
        # Add the instruction text as a Static widget
        yield Static(
            "Instruction: Please press 'Complete' button when you finish reviewing the words and mark as 'Known' all words you know the translation and definition.",
            id="instruction_text",
            classes="instruction"
        )
        yield Button("Complete", id="complete_button", variant="success")
        yield Footer()


    def on_mount(self) -> None:
        """Set up the DataTable when the screen is mounted."""
        self.app.sub_title = "check the words"

        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.cursor_type = "row"
        # Add columns with header names only (without tuple)
        table.add_columns("ID", "Word", "Status", "Translation")

        # Add rows with explicit row keys based on index
        for index, item in enumerate(self.word_items):
            row_data = (index, item.word, item.display_status(), item.translation)
            table.add_row(*row_data) # Use index as row key

    def action_mark_known(self) -> None:
        """Mark the selected word as known."""
        self._toggle_word_status(known=True)

    def action_mark_unknown(self) -> None:
        """Mark the selected word as unknown."""
        self._toggle_word_status(known=False)

    def action_get_translation(self) -> None:
        """Translate the selected word and update the translation column."""
        table = self.query_one(DataTable)
        
        # Get the current cursor row index
        cursor_row = table.cursor_coordinate[0]  # Row index
        word_item = self.word_items[cursor_row]  # Access WordItem directly by row index

        # Fetch the translation for the selected word
        translation = translate_word(word_item.word, self.translation_language)
        word_item.translation = translation  # Update the WordItem with the translation

        # Move cursor to the "Translation" column to get correct cell keys
        table.move_cursor(column=3)  # Column 3 is "Translation"
        row_key, col_key = table.coordinate_to_cell_key(table.cursor_coordinate)

        # Update the "Translation" cell with the translated word
        table.update_cell(row_key, col_key, word_item.translation, update_width=True)

    async def on_button_pressed(self, event):
        if event.button.id == "complete_button":
            await self.app.run_processing()

    def _toggle_word_status(self, known: bool) -> None:
        """Toggle the known/unknown status of the currently selected word."""
        table = self.query_one(DataTable)

        # Get the current row index from the cursor
        cursor_row = table.cursor_coordinate[0]  # Row index
        word_item = self.word_items[cursor_row]  # Access WordItem directly by row index
        word_item.toggle_status(known=known)

        # Move cursor to the "Status" column to get correct cell keys
        table.move_cursor(column=2)  # Column 2 is "Status"
        row_key, col_key = table.coordinate_to_cell_key(table.cursor_coordinate)
        
        # Update the "Status" cell with the new status label
        table.update_cell(row_key, col_key, word_item.display_status())

class ResultScreen(Screen):
    """Screen to show results of the analysis."""

    # Reactive properties to update results dynamically
    output_content = reactive("")
    new_known_words_count = reactive(0)
    total_known_words_count = reactive(0)

    def __init__(self, output_file, new_known_words_count, total_known_words_count):
        super().__init__()
        self.output_file = output_file
        self.new_known_words_count = new_known_words_count
        self.total_known_words_count = total_known_words_count

    def compose(self) -> ComposeResult:
        """Set up the screen layout."""
        yield Header()
        yield Static("Fetching translations and definitions...", id="fetching_label")
        yield Static("", id="indicator")  # Placeholder for indicator widget
        yield Footer()

    async def on_mount(self):
        """Update the screen when the translation process completes."""
        # TODO: Simulate fetching translations (in reality, this is done in finalize_and_translate)
        await work(self.fetch_results)

    async def fetch_results(self):
        """Fetch results and update the screen."""
        # TODO: Placeholder for any delay or actual work
        await self.sleep(5)  # Simulating translation process
        # await work(self.app.finalize_and_translate())

        # Read the output file content
        try:
            with open(self.output_file, "r", encoding="utf-8") as file:
                self.output_content = file.read()
        except FileNotFoundError:
            self.output_content = "Output file not found."

        # Update the screen
        self.clear_widgets()
        yield Header()
        yield Label("Results", id="result_label")
        yield TextArea(self.output_content, id="output_textarea", height=20)
        yield Label(f"New Known Words: {self.new_known_words_count}", id="new_known_label")
        yield Digits(self.new_known_words_count, id="new_known_digits")
        yield Label(f"Total Known Words: {self.total_known_words_count}", id="total_known_label")
        yield Digits(self.total_known_words_count, id="total_known_digits")
        yield Footer()

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

class LinguaLearnApp(App):
    CSS_PATH = "styles.tcss"  # Path to custom CSS file
    TITLE = "A Lingua Learn App"
    SUB_TITLE = "knows what you don't know"

    # TODO: add reactive property for source type: file or url
    selected_file = reactive("")
    translation_language = reactive("")
    output_file = reactive("")
    word_items = reactive([])
    known_words = reactive([])

    async def on_mount(self):
        await self.push_screen(WelcomeScreen())  # Start with WelcomeScreen

    async def run_analysis(self):
        """Run the analysis and proceed to WordListScreen."""
        # Retrieve input values using query_one
        file_input = self.query_one("#file_input", Input)
        lang_input = self.query_one("#lang_input", Input)
        file_output = self.query_one("#output_file_input", Input)
        self.selected_file = file_input.value.strip() or "input.txt"
        self.translation_language = lang_input.value.strip() or "ua"
        self.output_file = file_output.value.strip() or "output.txt"

        # Load known words and process input text
        self.known_words = load_known_words()
        if not self.selected_file:
            self.notify("Please enter a valid file path.", severity="error")
            return

        unknown_words = process_text(self.selected_file, self.known_words)
        
        # Generate WordItem objects for each unknown word
        self.word_items = [WordItem(word) for word in unknown_words]
        
        # Transition to WordListScreen
        await self.push_screen(WordListScreen(self.word_items, self.translation_language))
    
    async def run_processing(self):
        """Run the obtaining of definition and translation of unknown words."""
        new_known_words_count = len([item for item in self.word_items if item.is_known])
        total_known_words_count = len(self.known_words) + new_known_words_count

        # Transition to ResultScreen
        await self.push_screen(ResultScreen(self.output_file, new_known_words_count, total_known_words_count))

    @work
    async def finalize_and_translate(self):
        """Finalize word classification and proceed with translation."""
        unknown_words = [item.word for item in self.word_items if not item.is_known]

        # Fetch translations and definitions for unknown words
        self.notify("Fetching translations and definitions...")
        fetch_definitions_bulk(unknown_words, self.translation_language)
        
        # Display completion message
        self.notify("Analysis complete! Check output.txt for results.")

        # Show modal window with question: "Would you like to add all the unknown words to the known words list?"
        # If yes, add all unknown words to known words list file and save it.
        # If no, do nothing
        if await self.push_screen_wait(QuestionScreen("Would you like to add all the unknown words to the known words list?")):
            update_known_words(self.unknown_words)
            self.notify("All unknown words added to known words list.", severity="information")
        else:
            self.notify("Unknown words not added to known words list.", severity="warning")

        # await self.pop_screen()  # Return to the previous screen after completion


if __name__ == "__main__":
    LinguaLearnApp().run()
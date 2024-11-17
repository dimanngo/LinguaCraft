# Import necessary modules from Textual library
import asyncio
from rich.markdown import Markdown
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Grid, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Header, Footer, Input, Button, Static, Label, DataTable, TextArea, Digits, LoadingIndicator
from textual.widgets._button import Button
from textual.widgets._static import Static

# Import custom modules for text processing, known words management, and translation
from known_words import load_known_words, update_known_words # Manages known words persistence
from text_processing import process_text  # Custom file with text processing functions
from translation import fetch_translation, translate_word  # Manages API calls for translations
from translation_bulk import fetch_definitions_bulk  # Manages Open API calls for definitions and translations

# constants
DEFAULT_INPUT_FILE = "input.txt"
DEFAULT_LANGUAGE = "ua"
DEFAULT_OUTPUT_FILE = "output.txt"

# Screen 1: Welcome Screen
class WelcomeScreen(Screen):
    WELCOME_MD = """\
# Welcome!

“LinguaCraft: Use it before you read to uncover unfamiliar words effortlessly.”

> "Your personalized companion for mastering foreign languages with confidence! This program helps you analyze texts, identify unfamiliar words, and prepare them for learning. With LinguaCraft, you can:

- Effortlessly process texts (from files or URLs) to detect unknown words.

- Mark words as known or unknown, helping you focus on what truly matters.

- Retrieve translations and definitions for unfamiliar terms in your preferred language.

- Save result and build a growing list of known words for continuous learning.

Whether you’re preparing for exams, translating documents, or simply expanding your vocabulary, LinguaCraft makes language learning efficient, organized, and enjoyable. Dive into the world of words and watch your knowledge grow!"
"""
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Grid(
                Vertical(
                    Static(
                        r"""
                [bold red]
╦  ┬┌┐┌┌─┐┬ ┬┌─┐╔═╗┬─┐┌─┐┌─┐┌┬┐
║  │││││ ┬│ │├─┤║  ├┬┘├─┤├┤  │ 
╩═╝┴┘└┘└─┘└─┘┴ ┴╚═╝┴└─┴ ┴└   ┴ 
                [/bold red]
                        """,
                        id="ascii_art",
                        classes="ascii left-column",
                    ),
                    Static("Copyright 2024 Dmytro Golodiuk"),
                    Static("[bold]Raise an Issue:[/] https://github.com/.../issues"),
                    Static("[bold]Release Notes:[/] https://github.com/.../releases"),
                    Static("[bold magenta]Become a sponsor:[/] https://github.com/sponsors/...")
                ),
                Static(Markdown(self.WELCOME_MD)),
                id="welcome_grid"
            )
        )
        yield Button("Next", id="next_button", variant="primary")
        yield Footer()

    async def on_button_pressed(self, event):
        if event.button.id == "next_button":
            await self.app.push_screen(InputScreen())

# screen 2: input fields
class InputScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()

        # Input fields and labels
        yield Container(
            InputWithLabel("File path:", f"Enter file path here, default value is '{DEFAULT_INPUT_FILE}'", "file_input"),
            InputWithLabel("Native language code:", f"Default is '{DEFAULT_LANGUAGE}'", "lang_input"),
            InputWithLabel("Output file path:", f"Enter output file path here, default value is '{DEFAULT_OUTPUT_FILE}'", "output_file_input")
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

# screen 3: word list
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

# screen 4: results
class ResultScreen(Screen):
    """Screen to show results of the analysis."""
    BINDINGS = [
        ("c", "copy_output", "Copy Output"),
        ("h", "go_home", "Go Home"),
    ]

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
        yield LoadingIndicator(id="loader")
        yield Label("fsdfdsfdsfsd", id="result_label")
        yield TextArea(id="output_textarea", read_only=True)
        yield Horizontal(
            Label(id="new_known_label"),
            Digits(id="new_known_digits"),
            Label(id="total_known_label"),
            Digits(id="total_known_digits"),
            id="known_words_info"
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.call_later(self.fetch_results)

    async def fetch_results(self):
        """Run the obtaining of definition and translation of unknown words. Shows the results."""
        await self.app.finalize_and_translate()

        # Read the output file content asynchronously
        try:
            # Use a thread-safe approach to read the file asynchronously
            with open(self.output_file, "r", encoding="utf-8") as file:
                self.output_content = file.read()
        except FileNotFoundError:
            self.output_content = "Output file not found."

        # Remove the LoadingIndicator
        loader = self.query_one("#loader", LoadingIndicator)
        loader.remove()

        # Update the screen
        self.query_one("#result_label", Label).update("Results")
        self.query_one("#output_textarea", TextArea).text = f"{self.output_file}\n------\n{self.output_content}"
        self.query_one("#new_known_label", Label).update("New Known Words:")
        self.query_one("#new_known_digits", Digits).update(str(self.new_known_words_count))
        self.query_one("#total_known_label", Label).update("Total Known Words:")
        self.query_one("#total_known_digits", Digits).update(str(self.total_known_words_count))

    def action_copy_output(self):
        """Copy the output content to the clipboard."""
        self.app.copy_to_clipboard(self.output_content)
        self.app.notify("Output copied to clipboard.", severity="information")

    async def action_go_home(self):
        """Return to the home screen."""
        await self.app.switch_screen(WelcomeScreen())

"""Custom widgets."""
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

"""Main application class."""
class LinguaLearnApp(App):
    CSS_PATH = "styles.tcss"
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
        self.selected_file = file_input.value.strip() or DEFAULT_INPUT_FILE
        self.translation_language = lang_input.value.strip() or DEFAULT_LANGUAGE
        self.output_file = file_output.value.strip() or DEFAULT_OUTPUT_FILE

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
        self.push_screen(ResultScreen(self.output_file, new_known_words_count, total_known_words_count))

    # @work(thread=True)
    async def finalize_and_translate(self):
        """Finalize word classification and proceed with translation."""
        unknown_words = [item.word for item in self.word_items if not item.is_known]

        # Fetch translations and definitions for unknown words
        fetch_definitions_bulk(unknown_words, self.translation_language)
        
        # Display completion message
        self.notify("Analysis complete! Check output.txt for results.")
        return

        # Show modal window with question: "Would you like to add all the unknown words to the known words list?"
        # If yes, add all unknown words to known words list file and save it.
        # If no, do nothing
        if await self.push_screen_wait(QuestionScreen("Would you like to add all the unknown words to the known words list?")):
            update_known_words(self.unknown_words)
            self.notify("All unknown words added to known words list.", severity="information")
        else:
            self.notify("Unknown words not added to known words list.", severity="warning")

"""Main entry point."""
if __name__ == "__main__":
    LinguaLearnApp().run()
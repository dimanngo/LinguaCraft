```
╦  ┬┌┐┌┌─┐┬ ┬┌─┐╔═╗┬─┐┌─┐┌─┐┌┬┐
║  │││││ ┬│ │├─┤║  ├┬┘├─┤├┤  │ 
╩═╝┴┘└┘└─┘└─┘┴ ┴╚═╝┴└─┴ ┴└   ┴ 
```

> “LinguaCraft: Use it before you read to uncover unfamiliar words effortlessly.”

## About

Your personalized companion for mastering foreign languages with confidence! This program helps you analyze texts, identify unfamiliar words, and prepare them for learning. With LinguaCraft, you can:

- Effortlessly process texts (from files or URLs) to detect unknown words.
- Mark words as known or unknown, helping you focus on what truly matters.
- Retrieve translations and definitions for unfamiliar terms in your preferred language.
- Save result and build a growing list of known words for continuous learning.

Whether you’re preparing for exams, translating documents, or simply expanding your vocabulary, LinguaCraft makes language learning efficient, organized, and enjoyable. Dive into the world of words and watch your knowledge grow!

<img width="2239" alt="01" src="https://github.com/user-attachments/assets/f5467492-ccb8-49a8-b088-812b721d1bf9">
<img width="2239" alt="02" src="https://github.com/user-attachments/assets/c5130b74-ceba-44d2-a81f-6451f4860ceb">
<img width="2200" alt="03" src="https://github.com/user-attachments/assets/bf7cf7cb-3861-465a-b019-35521cff8130">
<img width="2200" alt="04" src="https://github.com/user-attachments/assets/d43d9afe-bc3f-40cd-8baa-947e4a7ea078">


## Getting Started

You can get started quickly like this:

```bash
pip install LinguaCraft

# Select your working directory
cd /to/your/work/dir

# Work with OpenAI GPT
export OPENAI_API_KEY=your-key-goes-here

# Create a text file with input text
touch input.txt

# Run LinguaCraft app
linguacraft 
```

See the [installation instructions](https://github.com/dimanngo/LinguaCraft/wiki/Installing-LinguaCraft) and other [documentation on LLM setup](https://github.com/dimanngo/LinguaCraft/wiki/Connecting-to-LLM) for more details.

## Usage

1. Run the application:
    ```bash
    linguacraft
    ```
2. Follow the on-screen instructions to input your text file.
3. Analyze the text to identify unknown words.
4. Review translations and definitions in the results screen.

## Features

- **Text Analysis:** Process input texts to identify and categorize known and unknown words.
- **Language Detection:** Automatically detect the language of the input text.
- **Translations & Definitions:** Fetch translations and definitions for unknown words using various providers like OpenAI and Google Translator.
- **User-Friendly Terminal Interface (TUI):** Interactive screens for input, word lists, and results.
- **Persistent Storage:** Maintain a list of known words to enhance your learning over time.

## Troubleshooting

If you encounter any issues while using LinguaCraft, refer to the `app.log` file for detailed error messages and logs.

```bash
cat app.log
```

Refer to [Troubleshooting](https://github.com/dimanngo/LinguaCraft/wiki/Troubleshooting) page for details.


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature/YourFeature
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add Your Feature"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/YourFeature
    ```
5. Create a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Contact

For any inquiries or support, please contact [info@golodiuk.com](mailto:info@golodiuk.com).

---
© 2024 Dmytro Golodiuk
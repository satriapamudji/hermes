## Hermes

GM.

With back-to-school szn in full swing next week, I decided to build Hermes — a Telegram bot designed to accelerate the learning process.

Initially, I considered building a web app, but I realized that Telegram would be a more accessible platform for quick interactions. Hermes is still in its early stages (since I actually have to test this out throughtout this new semester), but I hope it will make learning more efficient.

### How Hermes Works

- Audio summarization: Uses Deepgram for transcription, OpenAI for summarization
- Text summarization: Uses OpenAI for summarization
- Research: Utilizes [CrewAI](https://www.crewai.com/) due to the complexity of the task. The configuration for different "agents" is in ```src/crew_utils/crew.py```.

## Getting Started

1. Install Poetry (If you don't have Poetry yet):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```
   git clone https://github.com/satriapamudji/hermes.git
   cd hermes
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Set up your `.env` file with these variables:
   ```
   # Deepgram API (For Transcription)
   DEEPGRAM_API_KEY=

   # OpenAI API (For text-related tasks)
   OPENAI_API_KEY=
   OPENAI_MODEL_NAME=

   # Serper API (For web searches)
   SERPER_API_KEY=

   # Telegram API
   TELEGRAM_API_ID=
   TELEGRAM_API_HASH=
   TELEGRAM_BOT_TOKEN=
   ```

5. Run the project:
   ```
   poetry run python main.py
   ```

## Features and Bugs

### Current Features

| Features                                       | Description                                                              |
| -------------------------------------  | ------------------------------------------------------------- |
| 🎧 **Audio summarization**            | Convert lengthy audio into concise summaries.                  |
| 📄 **Text summarization**              | Digest large volumes of text easily.                          |
| 📜 **Research (Function)**             | Conduct research on a specific topic. An example of the research output can be found [here](https://github.com/satriapamudji/hermes/blob/main/example_research.pdf).                       |

### Planned Features

| Features                                       | Description                                                             |
| -------------------------------------  | ------------------------------------------------------------------------------  |
| 🗃️ **Text to Anki**                   | Turn any given text into an Anki flashcard list.                                 |
| 🙋🏻‍♂️ **Learn (Function)**               | Quickly learn any subject matter. A more mild version of Research.               |
| ❓ **Text to Questions**               | Generate a questionnaire to practice based on a given text.                      |

### Current Known Bugs

- **Text Summarization**: Inability to read some PDFs 
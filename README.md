# Hermes

Hermes is a Telegram bot that can summarize audio, text, and conduct research.

## Features

- Audio summarization
- Text summarization
- Research assistant

## Setup

1. Install Poetry:
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

## How It Works

- Audio summarization: Uses Deepgram + OpenAI
- Text summarization: Powered by OpenAI
- Research: Utilizes CrewAI

## Development

Activate the virtual environment:
```
poetry shell
```

Add new dependencies:
```
poetry add package-name
```

Enjoy using Hermes!
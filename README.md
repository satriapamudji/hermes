GM.

With back-to-school szn in full swing next week, I decided to build Hermes — a Telegram bot designed to accelerate the learning process.

Initially, I considered building a web app, but I realized that Telegram would be a more accessible platform for quick interactions. Hermes is still in its early stages (since I actually have to test this out throughtout this new semester), but I hope it will make learning more efficient.

### How Hermes Works

- Audio summarization: Uses Deepgram for transcription, OpenAI for summarization
- Text summarization: Uses OpenAI for summarization
- Research: Utilizes [CrewAI](https://www.crewai.com/) due to the complexity of the task. The configuration for different "agents" is in `src/crew_utils/crew.py`.

## Getting Started

### 1. Install Poetry

You have two options to install Poetry:

- #### **Option 1**: Official installer (Recommended)

```
curl -sSL https://install.python-poetry.org | python3 -
```

- #### **Option 2**: Alternatively, you can use pip to install Poetry:

```
pip install poetry
```

After installation, you may need to add Poetry to your PATH. The exact command depends on your operating system and shell, but it's typically something like:

```
export PATH="$HOME/.local/bin:$PATH"
```

You may want to add this line to your shell configuration file (e.g., `.bashrc`, `.zshrc`) to make it permanent.

### 2. Install FFMPEG

FFmpeg is required for audio processing. Install it based on your operating system:

- #### **macOS** (using Homebrew):

  ```
  brew install ffmpeg
  ```

- #### **Ubuntu or Debian**:

  ```
  sudo apt update
  sudo apt install ffmpeg
  ```

- #### **Windows**:
  Download from the [official FFmpeg website](https://ffmpeg.org/download.html) and add it to your system PATH.

### 3. Clone the Repository

```
git clone https://github.com/satriapamudji/hermes.git
cd hermes
```

### 4. Install Dependencies

```
poetry install
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

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

# Canvas API

CANVAS_API_URL=
CANVAS_ACCESS_TOKEN=

# Approved Users

APPROVED_USERS=
```

For the `APPROVED_USERS` variable, add the Telegram user IDs of people allowed to use the bot, separated by commas. For example:

```
APPROVED_USERS=123456789,987654321
```

To get your Telegram user ID, you can use the @userinfobot on Telegram.

You can find an example `.env` file [here](https://github.com/satriapamudji/hermes/blob/main/.env_example).

### 6. Navigate to the Source Directory

```bash
cd src/hermes
```

### 7. Run the Project

```bash
poetry run python main.py
```

## Note on APPROVED_USERS

The `APPROVED_USERS` setting is a security feature that restricts access to your bot. Only users whose Telegram IDs are listed in this setting will be able to interact with the bot. This is useful for:

- Preventing unauthorized use of your bot
- Controlling access to sensitive information or functions
- Limiting API usage to avoid exceeding rate limits

Make sure to keep this list updated as you add or remove users who should have access to your bot.

## Features and Bugs

### Current Features

| Features                   | Description                                                                                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🎧 **Audio (Summary)**     | Convert lengthy audio into concise summaries.                                                                                                            |
| 📄 **Text (Summary)**      | Digest large volumes of text easily.                                                                                                                     |
| 📜 **Research (Function)** | Conduct research on a specific topic. Example of the output can be found [here](https://github.com/satriapamudji/hermes/blob/main/example_research.pdf). |
| 📄 **Canvas Support**      | View your Canvas (LMS) classes & download files quickly.                                                                                                 |

### Planned Features

| Features                 | Description                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| 🗃️ **Text to Anki**      | Turn any given text into an Anki flashcard list.                   |
| 🙋🏻‍♂️ **Learn (Function)**  | Quickly learn any subject matter. A more mild version of Research. |
| ❓ **Text to Questions** | Generate a questionnaire to practice based on a given text.        |

### Current Known Bugs

- **Text Summarization**: Inability to read some PDFs
- **Research**: Model does not provide inline citation

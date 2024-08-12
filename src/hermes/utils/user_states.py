from enum import Enum, auto

class BotState(Enum):
    IDLE = auto()
    AWAITING_AUDIO_FILENAME = auto()
    AWAITING_TEXT_FILENAME = auto()
    AWAITING_AUDIO_FILE = auto()
    AWAITING_TEXT_FILES = auto()
    PROCESSING_SUMMARY = auto()
    PROCESSING_RESEARCH = auto()
    TASK_COMPLETED = auto()

class UserStateMachine:

    def __init__(self):
        self.state = BotState.IDLE
        self.filename = None
        self.file = None
        self.text_files = []
        self.research_topic = None

    def set_task_completed(self):
        self.state = BotState.TASK_COMPLETED

    def start_audio_summarize(self):
        if self.state == BotState.IDLE:
            self.state = BotState.AWAITING_AUDIO_FILENAME
            return "Please provide a name for your file (without extension and without '/' at the start)."
        else:
            return self._busy_message()

    def start_text_summarize(self):
        if self.state == BotState.IDLE:
            self.state = BotState.AWAITING_TEXT_FILENAME
            return "Please provide a name for your summary file (without extension and without '/' at the start)."
        else:
            return self._busy_message()

    def start_research(self, topic):
        if self.state == BotState.IDLE:
            self.state = BotState.PROCESSING_RESEARCH
            self.research_topic = topic
            return f"Starting research on the topic: {topic}. This may take a while..."
        else:
            return self._busy_message()

    def set_audio_filename(self, filename):
        if self.state == BotState.AWAITING_AUDIO_FILENAME:
            self.filename = filename
            self.state = BotState.AWAITING_AUDIO_FILE
            return f"Great! I've noted the filename as '{filename}'. Now, please send me the audio file you want to summarize."
        else:
            return "I'm not expecting a filename at this time. Please use the /summarize_audio command to start the process."

    def set_text_filename(self, filename):
        if self.state == BotState.AWAITING_TEXT_FILENAME:
            self.filename = filename
            self.state = BotState.AWAITING_TEXT_FILES
            return f"Great! I've noted the filename as '{filename}'. Now, please send me the text documents (PDF, Word, or TXT) you want to summarize. You can send multiple files. When you're done, send /done."
        else:
            return "I'm not expecting a filename at this time. Please use the /summarize_text command to start the process."

    def set_audio_file(self, file):
        if self.state == BotState.AWAITING_AUDIO_FILE:
            self.file = file
            self.state = BotState.PROCESSING_SUMMARY
            return "File received. Starting the summarization process."
        else:
            return "I'm not expecting a file at this time. Please use the /summarize_audio command to start the process."

    def add_text_file(self, file):
        if self.state == BotState.AWAITING_TEXT_FILES:
            self.text_files.append(file)
            return f"File received. Total files: {len(self.text_files)}. Send more files or /done when finished."
        else:
            return "I'm not expecting text files at this time. Please use the /summarize_text command to start the process."

    def finish_text_files(self):
        if self.state == BotState.AWAITING_TEXT_FILES and self.text_files:
            self.state = BotState.PROCESSING_SUMMARY
            return "Processing your text files for summarization."
        elif self.state == BotState.AWAITING_TEXT_FILES:
            return "You haven't sent any files yet. Please send at least one file before using /done."
        else:
            return "I'm not expecting the /done command at this time."

    def get_state(self):
        return self.state

    def _busy_message(self):
        current_state = self.state.name.lower().replace('_', ' ')
        return f"I'm currently busy with another task ({current_state}). Please wait until it's finished or use /cancel to stop the current process."

    def cancel_current_task(self):
        previous_state = self.state
        self.reset()
        return f"Cancelled the current task. You can start a new task now."

    def reset(self):
        self.state = BotState.IDLE
        self.filename = None
        self.file = None
        self.text_files = []
        self.research_topic = None

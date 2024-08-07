import os
import logging
from telethon import TelegramClient, events

from config.settings import TELEGRAM_BOT_TOKEN, API_HASH, API_ID
from utils.validity_checks import is_valid_audio_file, is_valid_text_file
from utils.user_states import BotState, UserStateMachine
from processors.process_text import process_text_documents
from processors.process_audio import process_audio
from processors.run_research import run_research

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize clients & Dictionary
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)
user_states = {}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    message = (
        "Welcome to Hermes! I can help you with various tasks:\n\n"
        "/research <topic>: Conduct research on a specific topic.\n"
        "/summarize_audio: Summarize an audio file.\n"
        "/summarize_text: Summarize multiple text documents.\n\n"
        "Other functions:\n\n"
        "/status: Check the current status of your task.\n"
        "/cancel: Cancel the current task.\n"
    )
    await event.reply(message)

@client.on(events.NewMessage(pattern='/research'))
async def handle_research(event):
    user_id = event.sender_id
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    user_state = user_states[user_id]
    
    try:
        topic = event.message.text.split('/research ', 1)[1]
        response = user_state.start_research(topic)
        await event.reply(response)
        
        if user_state.get_state() == BotState.PROCESSING_RESEARCH:
            pdf_filename = await run_research(topic)
            await client.send_file(event.chat_id, pdf_filename, caption=f"Here's your research on {topic}")
            os.remove(pdf_filename)
            user_state.set_task_completed()
            await event.reply("Research task completed. What would you like to do next? Use /start to see available commands.")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        await event.reply("An error occurred while processing your request. Please try again later.")
        user_state.reset()

@client.on(events.NewMessage(pattern='/summarize_audio'))
async def summarize_audio_command(event):
    user_id = event.sender_id
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    response = user_states[user_id].start_audio_summarize()
    await event.reply(response)

@client.on(events.NewMessage(pattern='/summarize_text'))
async def summarize_text_command(event):
    user_id = event.sender_id
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    response = user_states[user_id].start_text_summarize()
    await event.reply(response)

@client.on(events.NewMessage(pattern='/cancel'))
async def cancel_command(event):
    user_id = event.sender_id
    if user_id in user_states:
        user_states[user_id].cancel_current_task()
    else:
        await event.reply("No active task to cancel.")

@client.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    user_id = event.sender_id
    if user_id in user_states:
        state = user_states[user_id].get_state().name.lower().replace('_', ' ')
        await event.reply(f"Current status: {state}")
    else:
        await event.reply("No active task. You can start a new task with /research, /summarize_audio, or /summarize_text.")

@client.on(events.NewMessage(func=lambda e: e.sender_id in user_states))
async def handle_user_input(event):
    user_id = event.sender_id
    user_state = user_states[user_id]
    state = user_state.get_state()

    if state == BotState.TASK_COMPLETED:
        user_state.reset()
        return

    if state in [BotState.AWAITING_AUDIO_FILENAME, BotState.AWAITING_TEXT_FILENAME]:
        filename = event.text.strip()
        if filename.startswith('/'):
            if filename in ['/cancel', '/start', '/status', '/summarize_audio', '/summarize_text', '/research']:
                pass
            else:
                await event.reply("Please provide a valid filename without '/' at the start.")
                return
        else:
            if state == BotState.AWAITING_AUDIO_FILENAME:
                response = user_state.set_audio_filename(filename)
            else:
                response = user_state.set_text_filename(filename)
            await event.reply(response)
            return

    if event.text.startswith('/'):
        if event.text.startswith('/cancel'):
            response = user_state.cancel_current_task()
            await event.reply(response)
        elif event.text == '/done' and state == BotState.AWAITING_TEXT_FILES:
            response = user_state.finish_text_files()
            await event.reply(response)
            if user_state.get_state() == BotState.PROCESSING_SUMMARY:
                await process_text_documents(event, client, user_state)
        elif event.text in ['/start', '/status', '/summarize_audio', '/summarize_text', '/research']:
            return
        else:
            await event.reply("I'm not sure what you want to do. Please use /start to see available commands.")
        return

    elif state == BotState.AWAITING_AUDIO_FILE:
        if event.message.media:
            try:
                if is_valid_audio_file(event.message, logger):
                    response = user_state.set_audio_file(event.message)
                    await event.reply(response)
                    if user_state.get_state() == BotState.PROCESSING_SUMMARY:
                        await process_audio(event, client, user_state)
                else:
                    await event.reply("Please send a valid audio file. Supported formats include MP3, WAV, OGG, M4A, AAC, and FLAC.")
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}", exc_info=True)
                await event.reply(f"An error occurred while processing your file: {str(e)}")
                user_state.reset()
        else:
            await event.reply("Please send an audio file.")
    
    elif state == BotState.AWAITING_TEXT_FILES:
        if event.message.media:
            try:
                if is_valid_text_file(event.message, logger):
                    response = user_state.add_text_file(event.message)
                    await event.reply(response)
                else:
                    await event.reply("Please send a valid text file (PDF, Word, or TXT).")
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}", exc_info=True)
                await event.reply(f"An error occurred while processing your file: {str(e)}")
                user_state.reset()
        else:
            await event.reply("Please send a text file or use /done when you're finished sending files.")

    elif state in [BotState.PROCESSING_SUMMARY, BotState.PROCESSING_RESEARCH]:
        await event.reply("I'm currently processing your previous request. Please wait until it's finished or use /cancel to stop the current process.")

    else:
        await event.reply("I'm not sure what you want to do. Please use /start to see available commands.")

if __name__ == "__main__":
    logger.info("Starting the bot")
    client.run_until_disconnected()
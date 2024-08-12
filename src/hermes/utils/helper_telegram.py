from utils.validity_checks import is_valid_audio_file, is_valid_text_file
from processors.process_text import process_text_documents
from processors.process_audio import process_audio
from utils.user_states import BotState
from logging_config import logger

async def handle_command(event, user_state):
    command = event.text.lower()
    logger.info(f"Received command: {command}")
    
    if command == '/cancel':
        response = user_state.cancel_current_task()
        logger.info("User requested to cancel the current task.")
        await event.reply(response)
    elif command == '/done' and user_state.get_state() == BotState.AWAITING_TEXT_FILES:
        response = user_state.finish_text_files()
        await event.reply(response)
        if user_state.get_state() == BotState.PROCESSING_SUMMARY:
            logger.info("Processing text documents as user finished sending files.")
            await process_text_documents(event, user_state)
    elif command in ['/start', '/status', '/summarize_audio', '/summarize_text', '/research', '/courses']:
        logger.info(f"Command '{command}' is acknowledged.")
        return
    else:
        logger.warning(f"Unknown command received: {command}")
        await event.reply("I'm not sure what you want to do. Please use /start to see available commands.")

async def handle_state_specific_input(event, user_state, state):
    logger.info(f"Handling input for state: {state.name}")
    
    if state in [BotState.AWAITING_AUDIO_FILENAME, BotState.AWAITING_TEXT_FILENAME]:
        await handle_filename_input(event, user_state, state)
    elif state == BotState.AWAITING_AUDIO_FILE:
        await handle_audio_file_input(event, user_state)
    elif state == BotState.AWAITING_TEXT_FILES:
        await handle_text_file_input(event, user_state)
    elif state in [BotState.PROCESSING_SUMMARY, BotState.PROCESSING_RESEARCH]:
        logger.info("Processing in progress; user requested another task.")
        await event.reply("I'm currently processing your previous request. Please wait until it's finished or use /cancel to stop the current process.")
    else:
        logger.warning(f"Unexpected state encountered: {state.name}")
        await event.reply("I'm not sure what you want to do. Please use /start to see available commands.")

async def handle_filename_input(event, user_state, state):
    filename = event.text.strip()
    logger.info(f"User provided filename: {filename}")
    
    if filename.startswith('/'):
        logger.warning("Filename provided by user starts with '/'. Invalid format.")
        await event.reply("Please provide a valid filename without '/' at the start.")
    else:
        if state == BotState.AWAITING_AUDIO_FILENAME:
            response = user_state.set_audio_filename(filename)
        else:
            response = user_state.set_text_filename(filename)
        logger.info(f"Filename '{filename}' accepted. State updated to {user_state.get_state().name}.")
        await event.reply(response)

async def handle_audio_file_input(event, user_state):
    if event.message.media:
        logger.info("Received media file, checking if it's a valid audio file.")
        try:
            if is_valid_audio_file(event.message):
                response = user_state.set_audio_file(event.message)
                await event.reply(response)
                if user_state.get_state() == BotState.PROCESSING_SUMMARY:
                    logger.info("Valid audio file received. Starting audio processing.")
                    await process_audio(event, user_state)
            else:
                logger.warning("Invalid audio file format received.")
                await event.reply("Please send a valid audio file. Supported formats include MP3, WAV, OGG, M4A, AAC, and FLAC.")
        except Exception as e:
            logger.error(f"Error while processing audio file: {str(e)}", exc_info=True)
            await event.reply(f"An error occurred while processing your file: {str(e)}")
            user_state.reset()
            logger.info("User state reset after error.")
    else:
        logger.warning("No media file received when expected.")
        await event.reply("Please send an audio file.")

async def handle_text_file_input(event, user_state):
    if event.message.media:
        logger.info("Received media file, checking if it's a valid text file.")
        try:
            if is_valid_text_file(event.message):
                response = user_state.add_text_file(event.message)
                await event.reply(response)
                logger.info("Valid text file received and added to the user state.")
            else:
                logger.warning("Invalid text file format received.")
                await event.reply("Please send a valid text file (PDF, Word, or TXT).")
        except Exception as e:
            logger.error(f"Error while processing text file: {str(e)}", exc_info=True)
            await event.reply(f"An error occurred while processing your file: {str(e)}")
            user_state.reset()
            logger.info("User state reset after error.")
    else:
        logger.warning("No media file received when expected.")
        await event.reply("Please send a text file or use /done when you're finished sending files.")

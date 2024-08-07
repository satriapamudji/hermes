from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename

def is_valid_audio_file(message, logger):
    timestamp = message.date
    message_id = message.id
    user_id = message.sender_id

    try:
        is_audio = False

        if message.audio:
            is_audio = True
            logger.info(f"{timestamp} - Message {message_id} from user {user_id} contains audio.")
        elif message.document:
            attributes = message.document.attributes
            is_audio = any(isinstance(attr, DocumentAttributeAudio) for attr in attributes)
            logger.info(f"{timestamp} - Checking document attributes for audio: {attributes}")

            if not is_audio:
                filename_attr = next((attr for attr in attributes if isinstance(attr, DocumentAttributeFilename)), None)
                if filename_attr:
                    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac']
                    is_audio = any(filename_attr.file_name.lower().endswith(ext) for ext in audio_extensions)
                    logger.info(f"{timestamp} - Checking filename for audio extensions: {filename_attr.file_name}")

        if is_audio:
            logger.info(f"{timestamp} - User {user_id} uploaded a valid audio file.")
        else:
            logger.info(f"{timestamp} - Message {message_id} from user {user_id} does not contain valid audio.")

        return is_audio
    except Exception as e:
        logger.error(f"{timestamp} - An error occurred for user {user_id}: {str(e)}", exc_info=True)
        return False

def is_valid_text_file(message, logger):
    timestamp = message.date
    message_id = message.id
    user_id = message.sender_id

    try:
        is_valid = False

        if message.document:
            attributes = message.document.attributes
            filename_attr = next((attr for attr in attributes if isinstance(attr, DocumentAttributeFilename)), None)
            if filename_attr:
                valid_extensions = ['.pdf', '.docx', '.txt', '.pptx']
                is_valid = any(filename_attr.file_name.lower().endswith(ext) for ext in valid_extensions)
                logger.info(f"{timestamp} - Checking filename for valid extensions: {filename_attr.file_name}")

        if is_valid:
            logger.info(f"{timestamp} - User {user_id} uploaded a valid text file.")
        else:
            logger.info(f"{timestamp} - Message {message_id} from user {user_id} does not contain a valid text file.")

        return is_valid
    except Exception as e:
        logger.error(f"{timestamp} - An error occurred for user {user_id}: {str(e)}", exc_info=True)
        return False
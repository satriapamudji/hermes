from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename
from logging_config import logger

def is_valid_audio_file(message):
    """
    Check if the message contains a valid audio file.
    
    :param message: The Telegram message object
    :return: Boolean indicating if the file is a valid audio file
    """
    if message.audio:
        logger.info("Message contains a valid audio file.")
        return True

    if not message.document:
        logger.warning("Message does not contain a document.")
        return False

    audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}

    try:
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                logger.info("Message document is a valid audio file.")
                return True
            if isinstance(attr, DocumentAttributeFilename):
                if any(attr.file_name.lower().endswith(ext) for ext in audio_extensions):
                    logger.info(f"Message document filename {attr.file_name} is a valid audio file.")
                    return True
    except AttributeError as e:
        logger.error("AttributeError encountered while checking audio file validity.", exc_info=True)
    return False

def is_valid_text_file(message):
    """
    Check if the attached document is a valid text file based on its extension.
    
    :param message: The Telegram message object
    :return: Boolean indicating if the file is a valid text file
    """
    if not message.document:
        logger.warning("Message does not contain a document.")
        return False

    valid_extensions = {'.pdf', '.docx', '.txt', '.pptx'}

    try:
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                if any(attr.file_name.lower().endswith(ext) for ext in valid_extensions):
                    logger.info(f"Message document filename {attr.file_name} is a valid text file.")
                    return True
    except AttributeError as e:
        logger.error("AttributeError encountered while checking text file validity.", exc_info=True)
    return False

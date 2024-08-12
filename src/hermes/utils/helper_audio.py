import math
import tempfile
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from pydub import AudioSegment
from config.settings import DEEPGRAM_API_KEY
from logging_config import logger

# Set up Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

async def split_audio(file_path, progress_message, max_size_mb=30):
    logger.info(f"Starting audio splitting for file: {file_path}")
    
    try:
        audio = AudioSegment.from_file(file_path)
        duration_ms = len(audio)
        logger.info(f"Audio duration: {duration_ms} ms, Frame rate: {audio.frame_rate} Hz, Channels: {audio.channels}")
        
        # Calculate chunk size in milliseconds
        sample_rate = audio.frame_rate
        sample_width = audio.sample_width
        channels = audio.channels

        max_size_bytes = max_size_mb * 1024 * 1024
        bytes_per_ms = (sample_rate * sample_width * channels) / 1000
        chunk_size_ms = max_size_bytes / bytes_per_ms

        chunks = []
        total_chunks = math.ceil(duration_ms / chunk_size_ms)
        logger.info(f"Splitting audio into {total_chunks} chunks")

        for chunk_number in range(total_chunks):
            start_ms = chunk_number * chunk_size_ms
            end_ms = min((chunk_number + 1) * chunk_size_ms, duration_ms)
            chunk = audio[start_ms:end_ms]

            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                chunk_path = temp_file.name
                chunk.export(chunk_path, format="ogg")
                chunks.append(chunk_path)
                logger.info(f"Chunk {chunk_number + 1}/{total_chunks} processed and saved as {chunk_path}")
            
            # Update progress message
            await progress_message.edit(f"Splitting audio file... {chunk_number + 1}/{total_chunks} chunks processed.")

        logger.info(f"Audio splitting completed. {total_chunks} chunks created.")
        return chunks, total_chunks

    except Exception as e:
        logger.error(f"Error during audio splitting: {str(e)}", exc_info=True)
        raise

def process_audio_chunk(chunk_path):
    logger.info(f"Processing audio chunk: {chunk_path}")
    
    try:
        with open(chunk_path, "rb") as audio:
            buffer_data = audio.read()
        
        payload: FileSource = {
            "buffer": buffer_data,
        }
        
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            paragraphs=True,
        )
        
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        logger.info(f"Audio chunk processed. Transcript length: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Error during audio chunk processing: {str(e)}", exc_info=True)
        raise

async def download_audio(client, message, file, filename):
    last_percentage = 0
    logger.info(f"Starting download of file: {filename}")

    async def progress_callback(current, total):
        nonlocal last_percentage
        percentage = math.floor((current / total) * 100)
        if percentage - last_percentage >= 10:
            logger.info(f"Download progress: {percentage}% for file: {filename}")
            await message.edit(f"Downloading: {percentage}%")
            last_percentage = percentage

    try:
        await message.edit("Starting download...")
        await client.download_media(file, filename, progress_callback=progress_callback)
        await message.edit("Download complete!")
        logger.info(f"Download complete for file: {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Download failed for file {filename}: {str(e)}", exc_info=True)
        await message.edit(f"Download failed: {str(e)}")
        return False

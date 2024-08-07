import math 
import logging
import tempfile
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from pydub import AudioSegment

from config.settings import DEEPGRAM_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

async def split_audio(file_path, progress_message, max_size_mb=30):
    logger.info("Splitting audio")
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    
    # Correct calculation for chunk size in milliseconds
    sample_rate = audio.frame_rate  # Use actual frame rate of the audio file
    sample_width = audio.sample_width  # bytes per sample
    channels = audio.channels  # number of audio channels

    max_size_bytes = max_size_mb * 1024 * 1024
    bytes_per_ms = (sample_rate * sample_width * channels) / 1000
    chunk_size_ms = max_size_bytes / bytes_per_ms

    chunks = []
    total_chunks = math.ceil(duration_ms / chunk_size_ms)  # Ensure total_chunks is an integer

    for chunk_number in range(total_chunks):
        start_ms = chunk_number * chunk_size_ms
        end_ms = min((chunk_number + 1) * chunk_size_ms, duration_ms)
        chunk = audio[start_ms:end_ms]
        logger.info(f"Working on chunk {chunk_number + 1}/{total_chunks}")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            chunk_path = temp_file.name
            chunk.export(chunk_path, format="ogg")
            chunks.append(chunk_path)
        
        # Update progress message
        await progress_message.edit(f"Splitting audio file... {chunk_number + 1}/{total_chunks} chunks processed.")
    
    return chunks, total_chunks

def process_audio_chunk(chunk_path):
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
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

async def download_file_with_progress(client, message, file, filename):
    async def progress_callback(current, total):
        nonlocal last_percentage
        percentage = math.floor((current / total) * 100)
        if percentage - last_percentage >= 10:
            await message.edit(f"Downloading: {percentage}%")
            last_percentage = percentage

    last_percentage = 0
    await message.edit("Starting download...")
    await client.download_media(file, filename, progress_callback=progress_callback)
    await message.edit("Download complete!")
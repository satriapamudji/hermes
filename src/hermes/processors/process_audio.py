import os
import json
import tempfile
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from config.bot_instance import client
from .pdf_summarizer import generate_summarize_pdf
from utils.helper_text import read_json_file, read_text_file
from utils.helper_audio import download_audio, split_audio, process_audio_chunk
from logging_config import logger

# Set up OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize sample files
sample_summary_json = read_json_file('sample_summary.json')
sample_transcript = read_text_file('sample_transcript.txt')

async def process_audio(event, user_state):
    local_filename = None
    audio_chunks = []
    pdf_filename = None

    try:
        logger.info(f"User {event.sender_id} initiated audio processing.")
        filename = user_state.filename
        file = user_state.file
        progress_message = await event.reply("Starting to process your audio file...")

        # Start the download process
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as temp_file:
            local_filename = temp_file.name

        download_success = await download_audio(client, progress_message, file.media, local_filename)
        logger.info(f"Audio file downloaded to {local_filename} for user {event.sender_id}.")

        if not download_success:
            raise Exception("Download failed. Please try uploading the file again.")

        # Split the audio file if it's too large
        await progress_message.edit("Splitting the audio file...")
        audio_chunks, total_chunks = await split_audio(local_filename, progress_message)
        logger.info(f"Audio file split into {total_chunks} chunks for user {event.sender_id}.")

        full_transcript = ""

        for i, chunk_path in enumerate(audio_chunks):
            await progress_message.edit(f"Transcribing audio chunk {i+1}/{total_chunks}...")
            chunk_transcript = process_audio_chunk(chunk_path)
            full_transcript += chunk_transcript + " "
            logger.info(f"Transcribed chunk {i+1}/{total_chunks} for user {event.sender_id}.")

        await progress_message.edit("Transcription finished. Generating summary...")

        # Summarize using OpenAI
        messages = [
            {
                "role": "system",
                "content": (
                    "## Language and Tone\n"
                    "- Use EXPERT terminology for the given context\n"
                    "- AVOID: superfluous prose, self-references, expert advice disclaimers, and apologies\n\n"
                    "## Content Depth and Breadth\n"
                    "- Present a meticulous AND holistic understanding of the topic\n"
                    "- Provide comprehensive and nuanced analysis and guidance\n"
                    "- For complex queries, demonstrate your reasoning process with step-by-step explanations\n\n"
                    "## Objectives\n"
                    "1. You are an expert summarizer.\n"
                    "2. You MUST provide a comprehensive, in-depth and detailed summary of the given transcript, highlighting as many key points and sub-points as necessary to fully capture the content.\n"
                    "3. You must ALWAYS provide a reference of where you get the sub-points from, and mark it as lines\n"
                    "4. With the reference, also provide the RAW LINES for the FIRST and LAST line.\n"
                    "5. With the reference, ensure that the words you give are FULL. (i.e. It should start from the beginning of a sentence, and end at the end of a sentence.)\n"
                    "6. With the reference, ensure that you DO NOT only reference 1 to 2 (one to two) lines. This ensures the user has more context."
                    "7. ENSURE that you have a MINIMUM of 5 key points. There is no maximum limit to the number of key points or sub-points to include.\n\n"
                    "# Your response MUST ALWAYS be in valid JSON format as follows, without any markdown formatting:\n\n"
                    '{\n'
                    '  "summary": "Synopsis of the transcript",\n'
                    '  "key_points": [\n'
                    '    {\n'
                    '      "point": "Key point {}",\n'
                    '      "explanation": "Comprehensive and in-depth explanation of point {}",\n'
                    '      "sub_points": [\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Lines {}-{}"\n'
                    '          "sub_reference_first_line": "Line {}: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Line {}: lorem ipsum"\n'
                    '        },\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Lines {}-{}"\n'
                    '          "sub_reference_first_line": "Line {}: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Line {}: lorem ipsum"\n'
                    '        }\n'
                    '      ]\n'
                    '    },\n'
                    '    {\n'
                    '      "point": "Key point {}",\n'
                    '      "explanation": "Comprehensive and in-depth explanation of point {}",\n'
                    '      "sub_points": [\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Lines {}-{}"\n'
                    '          "sub_reference_first_line": "Line {}: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Line {}: lorem ipsum"\n'
                    '        },\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Lines {}-{}"\n'
                    '          "sub_reference_first_line": "Line {}: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Line {}: lorem ipsum"\n'
                    '        }\n'
                    '      ]\n'
                    '    }\n'
                    '  ]\n'
                    '}\n'
                    "#Note: The above JSON structure is just an example.\n"
                    "##You should include as many key points "
                    "and sub-points as necessary to fully capture the content of the transcript. "
                    "Do not limit yourself to any specific number of points or sub-points."
                )
            },
            {
                "role": "user",
                "content": (
                    "## INSTRUCTIONS\n"
                    "Analyze the following transcript and provide a summary in the specified JSON format, without any markdown formatting.\n"
                    "Include as many key points and sub-points as necessary, and make it comprehensive, in-depth and detailed to fully capture the content.\n"
                    "Follow the SYSTEM MESSAGE and the EXAMPLES regarding your style of writing.\n"
                    "Below '-----' is the transcript.\n\n"
                    "## FORMAT\n"
                    'Provide your response in JSON format only, without any markdown formatting. The format should be as specified in the system message.\n'
                    "ENSURE that you ALWAYS follow this format as specified above.\n\n"
                    "# EXAMPLE\n"
                    "Here is an example of a transcript, and a summary.\n"
                    "1. f'EXAMPLE transcript: {sample_transcript}'\n"
                    "2. f'EXAMPLE summary: {json.dumps(sample_summary_json, indent=2)}'\n"
                    "ALWAYS follow this example for the BREADTH and COMPREHENSIVENESS of the content.\n"
                    "ALWAYS follow this example for the STRUCTURING of the format.\n\n"
                    "-----\n"
                    f"Transcript:\n{full_transcript}"
                )
            }
        ]
        
        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            seed=555,
            messages=messages
        )
        logger.info(f"OpenAI API call successful for user {event.sender_id}.")
        
        content = completion.choices[0].message.content
        json_content = content.strip('`').replace('json\n', '', 1) if content.startswith('```json') else content
        
        try:
            summary_data = json.loads(json_content)
            logger.info(f"Summary successfully parsed into JSON for user {event.sender_id}.")
        except json.JSONDecodeError as json_error:
            logger.error(f"JSONDecodeError while parsing summary for user {event.sender_id}: {str(json_error)}", exc_info=True)
            raise ValueError(f"There was an issue with the summary format: {json_error.msg}. Please try again.")

        await progress_message.edit("Summary generated. Creating PDF...")

        # Generate PDF
        try:
            pdf_filename = generate_summarize_pdf(filename, full_transcript, summary_data, is_audio=True)
            logger.info(f"PDF generated for user {event.sender_id} with filename {pdf_filename}.")
        except Exception as pdf_error:
            logger.error(f"Error during PDF generation for user {event.sender_id}: {str(pdf_error)}", exc_info=True)
            raise RuntimeError(f"An error occurred while creating the PDF summary: {str(pdf_error)}. Please try again.")

        # Send the PDF
        await client.send_file(event.chat_id, pdf_filename, caption=f"Here's the summary of {filename}")
        await progress_message.edit("Processing complete!")
        logger.info(f"Summary PDF sent to user {event.sender_id}.")

    except Exception as e:
        logger.error(f"Unexpected error occurred while processing audio for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.reply(f"I'm sorry, an error occurred while processing your audio.\n\n{str(e)}")

    finally:
        # Clean up
        if local_filename and os.path.exists(local_filename):
            os.remove(local_filename)
            logger.info(f"Temporary audio file {local_filename} deleted after processing for user {event.sender_id}.")
        for chunk in audio_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
                logger.info(f"Temporary audio chunk {chunk} deleted after processing for user {event.sender_id}.")
        if pdf_filename and os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            logger.info(f"Temporary PDF file {pdf_filename} deleted after processing for user {event.sender_id}.")
        user_state.reset()
        logger.info(f"User state reset for user {event.sender_id} after processing.")

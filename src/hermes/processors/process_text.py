import os
import json
import logging
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from .pdf_summarizer import generate_summarize_pdf
from utils.helpers_process_text import extract_text_from_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def process_text_documents(event, client, user_state):
    user_id = event.sender_id
    message_id = event.message.id
    timestamp = event.message.date

    logger.info(f"{timestamp} - Starting text document processing for user {user_id} with message ID {message_id}.")

    try:
        progress_message = await event.reply("Starting to process your text documents...")
        
        # Extract text from all documents
        all_documents = []
        for i, file in enumerate(user_state.text_files, start=1):
            await progress_message.edit(f"Extracting text from file {i}/{len(user_state.text_files)}...")
            logger.info(f"{timestamp} - Extracting text from file {i}/{len(user_state.text_files)} for user {user_id}")
            doc_info = await extract_text_from_file(client, event.message, file, i)
            all_documents.append(doc_info)
            logger.info(f"{timestamp} - Successfully extracted text from file {i} for user {user_id}")

        # Combine all documents into a single string for OpenAI
        all_text = "\n\n".join([f"Document {doc['doc_number']} ({doc['file_name']}):\n\n{doc['text']}" for doc in all_documents])
        logger.info(f"{timestamp} - Combined {len(all_documents)} documents for user {user_id}. Total character count: {len(all_text)}")

        await progress_message.edit("Text extraction complete. Generating summary...")

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
                    "2. You MUST provide a comprehensive, in-depth and detailed summary of the given documents, highlighting as many key points and sub-points as necessary to fully capture the content.\n"
                    "3. You must ALWAYS provide a reference of where you get the sub-points from, and mark it as 'Document X, Lines Y-Z'\n"
                    "4. With the reference, also provide the RAW LINES for the FIRST and LAST line.\n"
                    "5. With the reference, ensure that the words you give are FULL. (i.e. It should start from the beginning of a sentence, and end at the end of a sentence.)\n"
                    "6. With the reference, ensure that you DO NOT only reference 1 to 2 (one to two) lines. This ensures the user has more context."
                    "7. ENSURE that you have a MINIMUM of 5 key points. There is no maximum limit to the number of key points or sub-points to include.\n\n"
                    "# Your response MUST ALWAYS be in valid JSON format as follows, without any markdown formatting:\n\n"
                    '{\n'
                    '  "summary": "Synopsis of the documents",\n'
                    '  "key_points": [\n'
                    '    {\n'
                    '      "point": "Key point {}",\n'
                    '      "explanation": "Comprehensive and in-depth explanation of point {}",\n'
                    '      "sub_points": [\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Document X, Lines Y-Z"\n'
                    '          "sub_reference_first_line": "Document X, Line Y: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Document X, Line Z: lorem ipsum"\n'
                    '        },\n'
                    '        {\n'
                    '          "sub_point": "Sub-point {}.{}",\n'
                    '          "sub_explanation": "Comprehensive, in-depth and detailed explanation of sub-point {}.{}"\n'
                    '          "sub_reference": "Document X, Lines Y-Z"\n'
                    '          "sub_reference_first_line": "Document X, Line Y: lorem ipsum"\n'
                    '          "sub_reference_last_line": "Document X, Line Z: lorem ipsum"\n'
                    '        }\n'
                    '      ]\n'
                    '    }\n'
                    '  ]\n'
                    '}\n'
                    "Ensure your response is a valid JSON object without any markdown formatting."
                )
            },
            {
                "role": "user",
                "content": (
                    "## INSTRUCTIONS\n"
                    "Analyze the following documents and provide a summary in the specified JSON format without any markdown formatting.\n"
                    "Include as many key points and sub-points as necessary, and make it comprehensive, in-depth and detailed to fully capture the content.\n"
                    "Follow the SYSTEM MESSAGE regarding your style of writing.\n"
                    "Below '-----' is the content of the documents.\n\n"
                    "## FORMAT\n"
                    'Provide your response in JSON format only without any markdown formatting. The format should be as specified in the system message.\n'
                    "ENSURE that you ALWAYS follow this format as specified above.\n\n"
                    "-----\n"
                    f"Document content:\n{all_text}"
                )
            }
        ]

        completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            seed=555,
            messages=messages
        )
        logger.info(f"{timestamp} - Received response from OpenAI API for user {user_id}")

        content = completion.choices[0].message.content
        logger.debug(f"{timestamp} - Raw API response for user {user_id}: {content}...")  # Log first 1000 characters

        json_content = content.strip('`').replace('json\n', '', 1) if content.startswith('```json') else content
        
        try:
            summary_data = json.loads(json_content)
            logger.info(f"{timestamp} - Successfully parsed JSON response for user {user_id}")
        except json.JSONDecodeError as json_error:
            logger.error(f"{timestamp} - JSON parsing error for user {user_id}: {str(json_error)}")
            logger.error(f"{timestamp} - Problematic content for user {user_id}: {json_content}...")  # Log first 1000 characters
            raise ValueError("The API response was not in valid JSON format. Please try again.")

        logger.info(f"{timestamp} - Generating PDF for user {user_id}")
        await progress_message.edit("Summary generated. Creating PDF...")

        # Generate PDF
        pdf_filename = generate_summarize_pdf(user_state.filename, all_documents, summary_data, is_audio=False)
        logger.info(f"{timestamp} - PDF generated for user {user_id}: {pdf_filename}")

        # Send the PDF
        await client.send_file(event.chat_id, pdf_filename, caption=f"Here's the summary of {user_state.filename}")
        logger.info(f"{timestamp} - PDF sent to user {user_id}")

        await progress_message.edit("Processing complete!")
        logger.info(f"{timestamp} - Text document processing completed successfully for user {user_id}")

    except ValueError as ve:
        error_message = str(ve)
        logger.error(f"{timestamp} - ValueError for user {user_id}: {error_message}")
        await event.reply(f"I'm sorry, an error occurred: {error_message}")
    except Exception as e:
        logger.error(f"{timestamp} - An unexpected error occurred for user {user_id}: {str(e)}", exc_info=True)
        await event.reply("I'm sorry, an unexpected error occurred while processing your text documents.")

    finally:
        # Clean up
        if 'pdf_filename' in locals() and os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            logger.info(f"{timestamp} - Temporary PDF file removed for user {user_id}")
        user_state.reset()
        logger.info(f"{timestamp} - User state reset to IDLE for user {user_id}")
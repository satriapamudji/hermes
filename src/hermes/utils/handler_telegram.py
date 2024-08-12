import os
import re
import html
from telethon import events
from telethon.tl.custom import Button
from telethon.errors import MessageNotModifiedError

from config.bot_instance import client
from canvas_utils.canvas_api import get_canvas_data, download_canvas_file
from canvas_utils.message_display import display_folders, display_courses
from processors.run_research import run_research
from .user_states import BotState, UserStateMachine
from .handler_decorator import handler_collector
from .helper_telegram import handle_command, handle_state_specific_input
from logging_config import logger  # Import the central logger

user_states = {}

## Command Handlers
@handler_collector.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    logger.info(f"Received /start command from user {event.sender_id}")
    message = (
        "Welcome to Hermes! I can help you with various tasks:\n\n"
        "/research <topic>: Conduct research on a specific topic.\n"
        "/summarize_audio: Summarize an audio file.\n"
        "/summarize_text: Summarize multiple text documents.\n\n"
        "Other functions:\n\n"
        "/courses: Check your Canvas Courses (If you've set it up).\n"
        "/status: Check the current status of your task.\n"
        "/cancel: Cancel the current task.\n"
    )
    await event.reply(message)
    logger.info(f"Sent welcome message to user {event.sender_id}")
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/research'))
async def research_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /research command from user {user_id}")
    
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    user_state = user_states[user_id]
    
    try:
        topic = event.message.text.split('/research ', 1)[1]
        logger.info(f"User {user_id} requested research on topic: {topic}")
        response = user_state.start_research(topic)
        await event.reply(response)
        
        if user_state.get_state() == BotState.PROCESSING_RESEARCH:
            logger.info(f"Starting research process for user {user_id} on topic: {topic}")
            pdf_filename = await run_research(topic)
            await client.send_file(event.chat_id, pdf_filename, caption=f"Here's your research on {topic}")
            os.remove(pdf_filename)
            logger.info(f"Research completed and file sent to user {user_id}. File {pdf_filename} has been removed.")
            user_state.set_task_completed()
            await event.reply("Research task completed.")
        
    except Exception as e:
        logger.error(f"Error occurred during research process for user {user_id}: {str(e)}", exc_info=True)
        await event.reply("An error occurred while processing your request. Please try again later.")
        user_state.reset()
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/summarize_audio'))
async def audio_summary_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /summarize_audio command from user {user_id}")
    
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    user_state = user_states[user_id]
    response = user_state.start_audio_summarize()
    await event.reply(response)
    logger.info(f"User {user_id} initiated audio summarization.")
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/summarize_text'))
async def text_summary_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /summarize_text command from user {user_id}")
    
    if user_id not in user_states:
        user_states[user_id] = UserStateMachine()
    
    user_state = user_states[user_id]
    response = user_state.start_text_summarize()
    await event.reply(response)
    logger.info(f"User {user_id} initiated text summarization.")
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/cancel'))
async def cancel_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /cancel command from user {user_id}")
    
    if user_id in user_states:
        response = user_states[user_id].cancel_current_task()
        logger.info(f"User {user_id} canceled their current task.")
        await event.reply(response)
    else:
        await event.reply("No active task to cancel.")
        logger.info(f"User {user_id} attempted to cancel a task, but no active task was found.")
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /status command from user {user_id}")
    
    if user_id in user_states:
        state = user_states[user_id].get_state().name.lower().replace('_', ' ')
        await event.reply(f"Current status: {state}")
        logger.info(f"User {user_id} checked their task status: {state}")
    else:
        await event.reply("No active task. You can start a new task with /research, /summarize_audio, or /summarize_text.")
        logger.info(f"User {user_id} checked status but no active task was found.")
    raise events.StopPropagation

@handler_collector.on(events.NewMessage(pattern='/courses'))
async def courses_handler(event):
    user_id = event.sender_id
    logger.info(f"Received /courses command from user {user_id}")
    
    try:
        courses = await get_canvas_data('courses?enrollment_state=active&include[]=term&state[]=available')
        if courses:
            await display_courses(event, courses, page=1, edit=False)
            logger.info(f"Displayed courses to user {user_id}.")
        else:
            await event.reply("Failed to retrieve courses. Please try again later or contact support.")
            logger.warning(f"Failed to retrieve courses for user {user_id}.")
    except Exception as e:
        logger.error(f"Error while fetching courses for user {user_id}: {str(e)}", exc_info=True)
        await event.reply("An error occurred while fetching your courses. Please try again later.")
    raise events.StopPropagation

## Other handlers
@handler_collector.on(events.NewMessage(func=lambda e: e.sender_id in user_states))
async def user_input_handler(event):
    user_id = event.sender_id
    logger.info(f"Handling user input from user {user_id}")
    
    user_state = user_states[user_id]
    state = user_state.get_state()

    if state == BotState.TASK_COMPLETED:
        logger.info(f"User {user_id} has completed their task, resetting state.")
        user_state.reset()
        return

    if event.text.startswith('/'):
        await handle_command(event, user_state)
    else:
        await handle_state_specific_input(event, user_state, state)
    raise events.StopPropagation

@handler_collector.on(events.CallbackQuery(pattern=r'course_(\d+)_(.+)'))
async def course_detail_handler(event):
    try:
        course_id, course_code = event.data.decode().split('_')[1:]
        logger.info(f"User {event.sender_id} requested details for course {course_code} (ID: {course_id})")
        
        course_info = await get_canvas_data(f'courses/{course_id}')
        if course_info:
            reply = f"Course: {course_info.get('name', 'Unnamed Course')} ({course_code})\n\nSelect an option:"
            buttons = [
                [Button.inline("Overview", f"overview_{course_id}_{course_code}"),
                 Button.inline("Folders", f"folders_{course_id}_{course_code}")],
                [Button.inline("Back to Courses", "back_to_courses")]
            ]
            await event.edit(reply, buttons=buttons)
            logger.info(f"Displayed course details for {course_code} to user {event.sender_id}")
        else:
            await event.edit("Failed to retrieve course information.", 
                             buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
            logger.warning(f"Failed to retrieve course information for course {course_code} (ID: {course_id}) for user {event.sender_id}")
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Error while handling course details for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    finally:
        await event.answer()

@handler_collector.on(events.CallbackQuery(pattern=r'courses_page_(\d+)'))
async def courses_page_handler(event):
    page = int(event.data.decode().split('_')[-1])
    logger.info(f"User {event.sender_id} requested page {page} of courses.")
    
    try:
        courses = await get_canvas_data('courses?enrollment_state=active&include[]=term&state[]=available')
        if courses:
            await display_courses(event, courses, page)
            logger.info(f"Displayed page {page} of courses to user {event.sender_id}")
        else:
            await event.edit("Failed to retrieve courses. Please try again.",
                             buttons=[[Button.inline("Retry", "back_to_courses")]])
            logger.warning(f"Failed to retrieve courses for user {event.sender_id} on page {page}.")
    except Exception as e:
        logger.error(f"Error while handling course page {page} for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Retry", "back_to_courses")]])
    finally:
        await event.answer()

@handler_collector.on(events.CallbackQuery(pattern=r'overview_(\d+)_(.+)'))
async def overview_handler(event):
    try:
        course_id, course_code = event.data.decode().split('_')[1:]
        logger.info(f"User {event.sender_id} requested overview for course {course_code} (ID: {course_id})")
        
        modules = await get_canvas_data(f'courses/{course_id}/modules?include[]=items')
        if modules:
            module_list = [f"{i+1}. {module['name']}" for i, module in enumerate(modules)]
            reply = f"Course Overview (Modules) for course {course_code}:\n\n" + "\n".join(module_list) + "\n\nSelect a module number to view its content:"
            
            module_buttons = [Button.inline(f"{i+1}", f"module_{course_id}_{module['id']}_{course_code}") for i, module in enumerate(modules)]
            module_buttons = [module_buttons[i:i+5] for i in range(0, len(module_buttons), 5)]
            logger.info(f"Displayed overview for course {course_code} to user {event.sender_id}")
        else:
            reply = "Failed to retrieve modules for this course. The course might not have any modules or there was an error."
            module_buttons = []
            logger.warning(f"Failed to retrieve modules for course {course_code} (ID: {course_id}) for user {event.sender_id}.")
        
        buttons = module_buttons + [
            [Button.inline(f"Back to {course_code}", f"course_{course_id}_{course_code}")],
            [Button.inline("Back to Courses", "back_to_courses")]
        ]
        await event.edit(reply, buttons=buttons)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Error while handling overview for course {course_code} (ID: {course_id}) for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    finally:
        await event.answer()

@handler_collector.on(events.CallbackQuery(pattern=r'module_(\d+)_(\d+)_(.+)'))
async def overview_content_handler(event):
    try:
        course_id, module_id, course_code = event.data.decode().split('_')[1:]
        logger.info(f"User {event.sender_id} requested content for module {module_id} in course {course_code}")
        
        module_items = await get_canvas_data(f'courses/{course_id}/modules/{module_id}/items')
        
        if module_items:
            item_list = []
            item_number = 1
            button_map = {}
            processed_file_ids = set()

            for i, item in enumerate(module_items):
                item_type = item['type']
                if item_type == 'SubHeader':
                    item_list.append(f"\n**{item['title']}**")
                else:
                    item_text = f"{item_number}. {item['title']} ({item_type})"
                    item_list.append(item_text)
                    if item_type == 'File':
                        file_id = item.get('content_id')
                        if file_id not in processed_file_ids:
                            button_map[item_number] = ('download', file_id)
                            processed_file_ids.add(file_id)
                    else:
                        button_map[item_number] = ('view', i)
                    item_number += 1

            reply = "\n".join(item_list) + "\n\nSelect an item number for more details:"
            
            item_buttons = []
            for num, (action, id_or_index) in button_map.items():
                if action == 'download':
                    item_buttons.append(Button.inline(f"{num}", f"download_{course_id}_{id_or_index}"))
                else:
                    item_buttons.append(Button.inline(f"{num}", f"item_{course_id}_{module_id}_{id_or_index}_{course_code}"))
            item_buttons = [item_buttons[i:i+5] for i in range(0, len(item_buttons), 5)]
        else:
            reply = f"Failed to retrieve content for this module or the module is empty."
            item_buttons = []
            logger.warning(f"Failed to retrieve content for module {module_id} in course {course_code} for user {event.sender_id}.")
        
        buttons = item_buttons + [
            [Button.inline("Back to Overview", f"overview_{course_id}_{course_code}")],
            [Button.inline("Back to Courses", "back_to_courses")]
        ]
        
        await event.edit(reply, buttons=buttons)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Error while handling module content for module {module_id} in course {course_code} for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    finally:
        await event.answer()

@handler_collector.on(events.CallbackQuery(pattern=r'item_(\d+)_(\d+)_(\d+)_(.+)'))
async def overview_content_detail_handler(event):
    try:
        course_id, module_id, item_index, course_code = event.data.decode().split('_')[1:]
        logger.info(f"User {event.sender_id} requested details for item {item_index} in module {module_id} for course {course_code}")
        
        item_index = int(item_index)
        module_items = await get_canvas_data(f'courses/{course_id}/modules/{module_id}/items')
        
        if module_items and 0 <= item_index < len(module_items):
            item = module_items[item_index]
            reply = f"Title: {item['title']}\n\n"
            
            buttons = []
            if item['type'] == 'Page':
                page_url = item.get('page_url')
                if page_url:
                    page_data = await get_canvas_data(f'courses/{course_id}/pages/{page_url}')
                    if page_data and 'body' in page_data:
                        body = page_data['body']
                        if body:
                            reply += "Files in this page:\n"
                            
                            file_links = re.findall(r'title="([^"]+)"[^>]*href="[^"]*?/courses/\d+/files/(\d+)[^"]*"', body)
                            
                            processed_file_ids = set()
                            for file_name, file_id in file_links:
                                if file_id not in processed_file_ids:
                                    decoded_file_name = html.unescape(file_name)
                                    reply += f"• {decoded_file_name}\n"
                                    buttons.append([Button.inline(f"Download {decoded_file_name}", f"download_{course_id}_{file_id}")])
                                    processed_file_ids.add(file_id)
                            
                            if not file_links:
                                reply += "No files found in this page.\n"
                        else:
                            reply += "The page is empty.\n"
                    else:
                        reply += "No content found for this page.\n"
                else:
                    reply += "No page URL found for this item.\n"
            elif item['type'] == 'File':
                file_id = item.get('content_id')
                if file_id:
                    buttons.append([Button.inline(f"Download {item['title']}", f"download_{course_id}_{file_id}")])
            elif item['type'] == 'ExternalUrl':
                reply += f"External URL: {item.get('external_url', 'N/A')}\n"
            elif item['type'] in ['Discussion', 'Assignment', 'Quiz']:
                reply += f"This is a {item['type']} item.\n"
            elif item['type'] == 'SubHeader':
                reply += "This is a subheader item (section divider).\n"
            elif item['type'] == 'ExternalTool':
                reply += f"This is an External Tool item.\n"
            
            # Item type link for non-file items
            if item['type'] != 'File' and 'html_url' in item:
                reply += f"\n{item['type']} link: {item['html_url']}\n"
        else:
            reply = "Failed to retrieve item details or invalid item selected."
            buttons = []
            logger.warning(f"Failed to retrieve details for item {item_index} in module {module_id} for course {course_code} for user {event.sender_id}.")
        
        buttons.extend([
            [Button.inline("Back to Module", f"module_{course_id}_{module_id}_{course_code}")],
            [Button.inline("Back to Overview", f"overview_{course_id}_{course_code}")],
            [Button.inline("Back to Courses", "back_to_courses")]
        ])
        
        await event.edit(reply, buttons=buttons)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Error while handling item details for item {item_index} in module {module_id} for course {course_code} for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    finally:
        await event.answer()

@handler_collector.on(events.CallbackQuery(pattern=r'folders_(\d+)_(.+)'))
async def folders_handler(event):
    course_id, course_code = event.data.decode().split('_')[1:]
    logger.info(f"User {event.sender_id} requested folders for course {course_code} (ID: {course_id})")
    await display_folders(event, course_id, course_code)

@handler_collector.on(events.CallbackQuery(pattern=r'folder_(\d+)_(.+)_(\d+)'))
async def folder_content_handler(event):
    course_id, course_code, folder_id = event.data.decode().split('_')[1:]
    logger.info(f"User {event.sender_id} requested content for folder {folder_id} in course {course_code} (ID: {course_id})")
    await display_folders(event, course_id, course_code, folder_id)

@handler_collector.on(events.CallbackQuery(pattern=r'folder_page_(\d+)_(.+)_(\d+)_(\d+)'))
async def folder_page_handler(event):
    try:
        data = event.data.decode().split('_')[1:]
        if len(data) >= 4:
            course_id, course_code, folder_id, page = data[:4]
            folder_id = None if folder_id == 'None' else folder_id
            logger.info(f"User {event.sender_id} requested page {page} of folder {folder_id} in course {course_code}")
            await display_folders(event, course_id, course_code, folder_id, int(page))
        else:
            await event.answer("Invalid folder page data. Please try again.")
            logger.warning(f"Invalid folder page data received from user {event.sender_id}.")
    except ValueError as e:
        logger.error(f"ValueError while processing page number for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.answer("Error processing page number. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error during folder page handling for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.answer("An unexpected error occurred. Please try again later.")

@handler_collector.on(events.CallbackQuery(pattern='back_to_courses'))
async def back_to_courses_handler(event):
    logger.info(f"User {event.sender_id} requested to go back to courses.")
    
    try:
        courses = await get_canvas_data('courses?enrollment_state=active&include[]=term&state[]=available')
        if courses:
            await display_courses(event, courses, page=1, edit=True)
            logger.info(f"Displayed back to courses for user {event.sender_id}.")
        else:
            await event.edit("Failed to retrieve courses. Please try again.",
                             buttons=[[Button.inline("Retry", "back_to_courses")]])
            logger.warning(f"Failed to retrieve courses for user {event.sender_id} on back to courses request.")
    except MessageNotModifiedError:
        pass
    except Exception as e:
        logger.error(f"Error during back to courses request for user {event.sender_id}: {str(e)}", exc_info=True)
        await event.edit("An error occurred. Please try again.",
                         buttons=[[Button.inline("Retry", "back_to_courses")]])
    finally:
        await event.answer()
            
@handler_collector.on(events.CallbackQuery(pattern=r'download_(\d+)(?:_([^_]+))?_(\d+)'))
async def download_file_handler(event):
    parts = event.data.decode().split('_')[1:]
    course_id, file_id = parts[0], parts[-1]
    logger.info(f"User {event.sender_id} requested download for file {file_id} in course {course_id}.")
    
    status_message = await event.reply("Downloading file, please wait...")
    try:
        file_info = await get_canvas_data(f'courses/{course_id}/files/{file_id}')
        if file_info and 'url' in file_info:
            file_name = file_info['filename']
            file_url = file_info['url']
            logger.info(f"Downloading file {file_name} from URL {file_url} for user {event.sender_id}")
            
            downloaded_file = await download_canvas_file(file_url, file_name)
            if downloaded_file:
                await status_message.edit("File downloaded, sending...")
                if os.path.exists(downloaded_file):
                    await event.respond(file=downloaded_file)
                    os.remove(downloaded_file)
                await status_message.edit(f"File sent: {file_name}")
                logger.info(f"File {file_name} sent to user {event.sender_id} and removed from server.")
            else:
                await status_message.edit(f"Failed to download file: {file_name}")
                logger.warning(f"Failed to download file {file_name} for user {event.sender_id}.")
        else:
            await status_message.edit(f"Failed to retrieve file information for file ID: {file_id}")
            logger.warning(f"Failed to retrieve file information for file ID: {file_id} for user {event.sender_id}.")
    except Exception as e:
        logger.error(f"Error during file download for file ID: {file_id} for user {event.sender_id}: {str(e)}", exc_info=True)
        await status_message.edit("An error occurred while processing your request. Please try again.")

from telethon.tl.custom import Button
from aiohttp import ClientResponseError
from telethon.errors import MessageNotModifiedError

from .canvas_api import get_canvas_data

async def display_courses(event, courses, page=1, edit=False):
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    current_courses = courses[start:end]

    if current_courses:
        course_list = [f"Code: {course.get('course_code', 'N/A')}\n"
                       f"Name: {course.get('name', 'Unnamed Course')}"
                       for course in current_courses]
        
        courses_text = "\n\n".join(course_list)
        reply = f"Your active courses (Page {page}):\n\n{courses_text}\n\nSelect a course to view details:"

        course_buttons = [Button.inline(course.get('course_code', f"Course {course['id']}"), 
                                        f"course_{course['id']}_{course['course_code']}") 
                          for course in current_courses]
        course_buttons = [course_buttons[i:i+3] for i in range(0, len(course_buttons), 3)]
        
        nav_buttons = []
        if page > 1:
            nav_buttons.append(Button.inline("◀️ Previous", f"courses_page_{page-1}"))
        if end < len(courses):
            nav_buttons.append(Button.inline("Next ▶️", f"courses_page_{page+1}"))

        buttons = course_buttons + ([nav_buttons] if nav_buttons else [])

        if edit:
            await event.edit(reply, buttons=buttons)
        else:
            await event.reply(reply, buttons=buttons)
    else:
        reply = "No more courses to display."
        buttons = [[Button.inline("Back to first page", "back_to_courses")]]
        if edit:
            await event.edit(reply, buttons=buttons)
        else:
            await event.reply(reply, buttons=buttons)

async def display_folders(event, course_id, course_code, folder_id=None, page=1):
    try:
        per_page = 10
        if folder_id:
            folders = await get_canvas_data(f'folders/{folder_id}/folders')
            files = await get_canvas_data(f'folders/{folder_id}/files?per_page={per_page}&page={page}')
            folder_info = await get_canvas_data(f'folders/{folder_id}')
            current_folder_name = folder_info.get('name', 'Unknown Folder')
            parent_folder_id = folder_info.get('parent_folder_id')
        else:
            root_folders = await get_canvas_data(f'courses/{course_id}/folders')
            course_files_folder = next((f for f in root_folders if f['name'] == 'course files'), None)
            
            if course_files_folder:
                folder_id = course_files_folder['id']
                folders = await get_canvas_data(f'folders/{folder_id}/folders')
                files = await get_canvas_data(f'folders/{folder_id}/files?per_page={per_page}&page={page}')
                current_folder_name = course_code
                parent_folder_id = None
            else:
                folders = root_folders
                files = await get_canvas_data(f'courses/{course_id}/files?per_page={per_page}&page={page}')
                current_folder_name = f"{course_code} (Root)"
                parent_folder_id = None

        total_items = len(folders) + len(files)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        folder_list = [f"📁 {i+1}. {folder['name']}" for i, folder in enumerate(folders[start_index:end_index])]
        remaining_slots = per_page - len(folder_list)
        file_list = [f"📄 {i+1+len(folder_list)}. {file['display_name']}" for i, file in enumerate(files[:remaining_slots])]

        content_text = "Folders:\n" + "\n".join(folder_list) if folder_list else "No folders found."
        content_text += "\n\nFiles:\n" + "\n".join(file_list) if file_list else "\n\nNo files found."

        reply = f"Contents of {current_folder_name} (Page {page}):\n\n{content_text}\n\nSelect a folder to view, or file to download:"

        buttons = []
        for i, folder in enumerate(folders[start_index:end_index]):
            buttons.append(Button.inline(f"📁 {i+1}", f"folder_{course_id}_{course_code}_{folder['id']}"))
        for i, file in enumerate(files[:remaining_slots]):
            buttons.append(Button.inline(f"📄 {i+1+len(folder_list)}", f"download_{course_id}_{course_code}_{file['id']}"))

        buttons = [buttons[i:i+3] for i in range(0, len(buttons), 3)]

        nav_buttons = []
        if page > 1:
            nav_buttons.append(Button.inline("◀️ Previous", f"folder_page_{course_id}_{course_code}_{folder_id}_{page-1}"))
        
        if total_items > end_index:
            nav_buttons.append(Button.inline("Next ▶️", f"folder_page_{course_id}_{course_code}_{folder_id}_{page+1}"))

        if nav_buttons:
            buttons.append(nav_buttons)

        if folder_id and parent_folder_id:
            back_button = Button.inline("⬆️ Up to Parent Folder", f"folder_{course_id}_{course_code}_{parent_folder_id}")
        else:
            back_button = Button.inline(f"Back to {course_code}", f"course_{course_id}_{course_code}")

        buttons.append([back_button])
        buttons.append([Button.inline("Back to Courses", "back_to_courses")])

        await event.edit(reply, buttons=buttons)
    except MessageNotModifiedError:
        await event.answer("You're already viewing this folder.")
    except ClientResponseError as e:
        error_message = "You don't have permission to access this folder." if e.status == 403 else str(e)
        await event.edit(f"Error: {error_message}", buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    except Exception as e:
        await event.edit("An error occurred while displaying folder contents.",
                         buttons=[[Button.inline("Back to Courses", "back_to_courses")]])
    finally:
        await event.answer()
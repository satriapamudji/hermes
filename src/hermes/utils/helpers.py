import os
import json
import tempfile
from telethon.tl.types import DocumentAttributeFilename

def read_json_file(file_name):
    file_path = os.path.join('data', file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def read_text_file(file_name):
    file_path = os.path.join('data', file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

async def download_file(client, message, file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(file)) as temp_file:
        await client.download_media(file, temp_file.name)
        return temp_file.name

def get_file_extension(file):
    for attr in file.document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            return os.path.splitext(attr.file_name)[1]
    return ''

def get_file_name(file):
    for attr in file.document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            return attr.file_name
    return 'Unnamed Document'
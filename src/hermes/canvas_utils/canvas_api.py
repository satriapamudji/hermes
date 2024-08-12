import aiohttp

from config.settings import CANVAS_ACCESS_TOKEN, CANVAS_API_URL

async def get_canvas_data(endpoint):
    headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}
    url = f'{CANVAS_API_URL}/{endpoint}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()

async def download_canvas_file(url, filename):
    headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                with open(filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return filename
            else:
                return None
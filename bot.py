import aiohttp
import tempfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_mp4_format(formats):
    async with aiohttp.ClientSession() as session:
        for fmt in formats:
            if ".mp4" in fmt["url"]:
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
                os.close(tmp_fd)
                async with session.get(fmt["url"]) as resp:
                    if resp.status != 200:
                        continue
                    with open(tmp_path, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
                return tmp_path
    return None

@bot.on_message(filters.command("dl"))
async def handle_download(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Send like: `/dl <url>`")

    url = message.command[1]
    api_url = f"https://ar-api-iauy.onrender.com/aio-dl?url={url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()

    if data.get("status") != 200:
        return await message.reply(f"❌ Failed: {data.get('data')}")

    formats = data["data"].get("formats", [])
    if not formats:
        return await message.reply("No valid formats found.")

    video_path = await download_mp4_format(formats)
    if not video_path:
        return await message.reply("Couldn't download a valid MP4 file.")

    try:
        await message.reply_video(video=video_path, caption=data["data"].get("title", "Downloaded"))
    except Exception as e:
        await message.reply(f"⚠️ Error sending video: {e}")
    finally:
        os.remove(video_path)

bot.run()

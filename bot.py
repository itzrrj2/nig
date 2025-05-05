import os
import aiohttp
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_file(session, url):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    async with session.get(url) as resp:
        if resp.status == 200:
            with open(tmp_file.name, 'wb') as f:
                f.write(await resp.read())
    return tmp_file.name

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply("Send me any media URL (YouTube, Instagram, TikTok, etc.) to download.")

@app.on_message(filters.text & ~filters.command("start"))
async def download_media(client, message: Message):
    url = message.text.strip()
    api = f"https://ar-api-iauy.onrender.com/aio-dl?url={url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            data = await response.json()

            if data.get("successful") != "success":
                await message.reply("❌ Failed to fetch media. Check URL or platform.")
                return

            media = data.get("data", {})
            formats = media.get("formats", [])
            audio = media.get("audio", {})

            # Get best quality (first in formats list)
            video_url = formats[0]["url"] if formats else None

            if not video_url:
                await message.reply("⚠️ No video format found.")
                return

            file_path = await download_file(session, video_url)

            # Send video
            try:
                await message.reply_video(
                    video=file_path,
                    caption=f"🎬 {media.get('title', 'Downloaded Video')}\n⏱ Duration: {media.get('duration')}",
                    supports_streaming=True
                )
            except Exception as e:
                await message.reply(f"❌ Failed to send video: {e}")
            finally:
                os.remove(file_path)

app.run()

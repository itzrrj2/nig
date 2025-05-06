import os
import aiohttp
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity
from pyrogram.enums import MessageEntityType
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("all_in_one_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

YOUTUBE_API = "https://jerrycoder.oggyapi.workers.dev/ytmp4?url="

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "👋 Welcome to All-In-One Downloader Bot!\n\nSend me a YouTube link and I'll fetch the video for you."
    )

@app.on_message(filters.text & filters.private)
async def download_and_send_video(client: Client, message: Message):
    url = message.text.strip()

    if "youtube.com" in url or "youtu.be" in url:
        await message.reply("🔄 Fetching video link...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(YOUTUBE_API + url) as resp:
                    data = await resp.json()

                    if not data.get("status"):
                        return await message.reply("❌ Failed to fetch video.")

                    title = data["data"]["title"]
                    video_url = data["data"]["dl"]

                async with session.get(video_url) as video_resp:
                    if video_resp.status != 200:
                        return await message.reply("❌ Couldn't download the video file.")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                        temp_video.write(await video_resp.read())
                        temp_path = temp_video.name

            await message.reply_video(
                video=temp_path,
                caption=f"🎬 {title}",
                caption_entities=[
                    MessageEntity(
                        type=MessageEntityType.BOLD,
                        offset=2,
                        length=len(title)
                    )
                ]
            )

            os.remove(temp_path)

        except Exception as e:
            await message.reply(f"❌ Error: {e}")

    else:
        await message.reply("⚠️ Please send a valid YouTube URL.")

app.run()

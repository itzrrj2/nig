import os
import aiohttp
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity
from pyrogram.enums import MessageEntityType
from dotenv import load_dotenv
from urllib.parse import quote

# Load credentials from .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

YOUTUBE_API = "https://jerrycoder.oggyapi.workers.dev/ytmp4?url="


@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "👋 Welcome to All-In-One Downloader Bot!\n\nSend me a YouTube link and I'll download the video for you!"
    )


@app.on_message(filters.text & filters.private)
async def download_and_send_video(client: Client, message: Message):
    url = message.text.strip()

    if "youtube.com" in url or "youtu.be" in url:
        await message.reply("🔄 Fetching download link...")

        try:
            async with aiohttp.ClientSession() as session:
                # Encode URL safely
                safe_url = quote(url, safe='')
                full_api_url = YOUTUBE_API + safe_url
                print("Calling API:", full_api_url)

                # Call the API
                async with session.get(full_api_url) as resp:
                    data = await resp.json()
                    print("API response:", data)

                    # Validate response
                    if "status" not in data or not data["status"]:
                        return await message.reply(f"❌ Failed to fetch video.\n\nAPI Response: {data}")

                    if "data" not in data or "dl" not in data["data"] or "title" not in data["data"]:
                        return await message.reply(f"❌ Invalid API structure.\n\nResponse: {data}")

                    title = data["data"]["title"]
                    video_url = data["data"]["dl"]
                    print("Downloading from:", video_url)

                # Download the video
                headers = {"User-Agent": "Mozilla/5.0"}
                async with session.get(video_url, headers=headers) as video_resp:
                    if video_resp.status != 200:
                        return await message.reply("❌ Couldn't download the video.")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                        temp_video.write(await video_resp.read())
                        temp_path = temp_video.name

            # Send the video file
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

            # Cleanup
            os.remove(temp_path)

        except Exception as e:
            await message.reply(f"❌ Error: {e}")

    else:
        await message.reply("⚠️ Please send a valid YouTube URL.")


# Run the bot
app.run()

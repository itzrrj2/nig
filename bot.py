import os
import aiohttp
import aiofiles
import tempfile
from uuid import uuid4
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity
from pyrogram.enums import MessageEntityType
from dotenv import load_dotenv
from urllib.parse import quote

# Load .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# External APIs
YOUTUBE_VIDEO_API = "https://jerrycoder.oggyapi.workers.dev/ytmp4?url="
YOUTUBE_AUDIO_API = "https://oggy-api.vercel.app/ytmp3?url="
INSTAGRAM_API = "https://oggy-api.vercel.app/insta?url="

# Init bot
app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "👋 Welcome to All-In-One Downloader Bot!\n\n"
        "📽 Send a YouTube or Instagram link to download video or image.\n"
        "🎧 Use /audio <YouTube link> to get MP3 audio."
    )

@app.on_message(filters.command("audio") & filters.private)
async def download_audio(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /audio <YouTube URL>")

    url = message.command[1]
    await message.reply("🔄 Fetching audio...")

    try:
        async with aiohttp.ClientSession() as session:
            full_api_url = YOUTUBE_AUDIO_API + quote(url, safe='')
            async with session.get(full_api_url) as resp:
                data = await resp.json()

                if "download" not in data or "title" not in data:
                    return await message.reply("❌ Invalid audio API response.")

                title = data["title"]
                audio_url = data["download"]

            headers = {"User-Agent": "Mozilla/5.0"}
            temp_path = f"/tmp/{uuid4().hex}.mp3"

            async with session.get(audio_url, headers=headers) as audio_resp:
                if audio_resp.status != 200:
                    return await message.reply("❌ Couldn't download the audio.")

                async with aiofiles.open(temp_path, 'wb') as f:
                    async for chunk in audio_resp.content.iter_chunked(1024 * 64):
                        await f.write(chunk)

        await message.reply_audio(
            audio=temp_path,
            title=title,
            caption=f"🎵 {title}",
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

@app.on_message(filters.text & filters.private)
async def auto_download(client: Client, message: Message):
    url = message.text.strip()

    try:
        # YouTube Video
        if "youtube.com" in url or "youtu.be" in url:
            await message.reply("🔄 Fetching YouTube video...")

            async with aiohttp.ClientSession() as session:
                full_api_url = YOUTUBE_VIDEO_API + quote(url, safe='')
                async with session.get(full_api_url) as resp:
                    data = await resp.json()

                    if not data.get("status") or "data" not in data:
                        return await message.reply("❌ Failed to fetch YouTube video.")

                    title = data["data"]["title"]
                    video_url = data["data"]["dl"]

                headers = {"User-Agent": "Mozilla/5.0"}
                temp_path = f"/tmp/{uuid4().hex}.mp4"

                async with session.get(video_url, headers=headers) as video_resp:
                    if video_resp.status != 200:
                        return await message.reply("❌ Couldn't download the YouTube video.")

                    async with aiofiles.open(temp_path, 'wb') as f:
                        async for chunk in video_resp.content.iter_chunked(1024 * 64):
                            await f.write(chunk)

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
            return

        # Instagram Media
        if "instagram.com" in url:
            await message.reply("🔄 Fetching Instagram media...")

            async with aiohttp.ClientSession() as session:
                full_api_url = INSTAGRAM_API + quote(url, safe='')
                async with session.get(full_api_url) as resp:
                    data = await resp.json()

                    if not data.get("status") or "data" not in data:
                        return await message.reply("❌ Failed to fetch Instagram media.")

                    items = data["data"]

                    for i, item in enumerate(items):
                        media_url = item["url"]
                        media_type = item["type"]
                        filename = f"/tmp/{uuid4().hex}"
                        suffix = ".mp4" if media_type == "video" else ".jpg"
                        full_path = filename + suffix

                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with session.get(media_url, headers=headers) as media_resp:
                            if media_resp.status != 200:
                                await message.reply(f"❌ Failed to download media #{i+1}")
                                continue

                            async with aiofiles.open(full_path, 'wb') as f:
                                async for chunk in media_resp.content.iter_chunked(1024 * 64):
                                    await f.write(chunk)

                        if media_type == "video":
                            await message.reply_video(video=full_path)
                        else:
                            await message.reply_photo(photo=full_path)

                        os.remove(full_path)

            return

        # Invalid URL
        await message.reply("⚠️ Please send a valid YouTube or Instagram URL.")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# Run bot
app.run()

import os
import aiohttp
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity
from pyrogram.enums import MessageEntityType
from dotenv import load_dotenv
from urllib.parse import quote

# Load secrets from .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

YOUTUBE_VIDEO_API = "https://jerrycoder.oggyapi.workers.dev/ytmp4?url="
YOUTUBE_AUDIO_API = "https://oggy-api.vercel.app/ytmp3?url="


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "👋 Welcome to All-In-One Downloader Bot!\n\n"
        "📽 Send any YouTube link to download the video.\n"
        "🎧 Use /audio <YouTube URL> to download just the audio (MP3)."
    )


@app.on_message(filters.command("audio") & filters.private)
async def download_audio(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /audio <YouTube URL>")

    url = message.command[1]
    await message.reply("🔄 Fetching audio...")

    try:
        async with aiohttp.ClientSession() as session:
            safe_url = quote(url, safe='')
            full_api_url = YOUTUBE_AUDIO_API + safe_url
            async with session.get(full_api_url) as resp:
                data = await resp.json()

                if "download" not in data or "title" not in data:
                    return await message.reply(f"❌ Invalid audio API response.\n\nResponse: {data}")

                title = data["title"]
                audio_url = data["download"]

            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(audio_url, headers=headers) as audio_resp:
                if audio_resp.status != 200:
                    return await message.reply("❌ Couldn't download the audio.")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(await audio_resp.read())
                    temp_path = temp_audio.name

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
async def auto_download_video(client: Client, message: Message):
    url = message.text.strip()

    if "youtube.com" in url or "youtu.be" in url:
        await message.reply("🔄 Fetching video...")

        try:
            async with aiohttp.ClientSession() as session:
                safe_url = quote(url, safe='')
                full_api_url = YOUTUBE_VIDEO_API + safe_url

                async with session.get(full_api_url) as resp:
                    data = await resp.json()

                    if "status" not in data or not data["status"]:
                        return await message.reply(f"❌ Failed to fetch video.\n\nAPI Response: {data}")

                    if "data" not in data or "dl" not in data["data"] or "title" not in data["data"]:
                        return await message.reply(f"❌ Invalid video API structure.\n\nResponse: {data}")

                    title = data["data"]["title"]
                    video_url = data["data"]["dl"]

                headers = {"User-Agent": "Mozilla/5.0"}
                async with session.get(video_url, headers=headers) as video_resp:
                    if video_resp.status != 200:
                        return await message.reply("❌ Couldn't download the video.")

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
        await message.reply("⚠️ Please send a valid YouTube URL or use /audio <url> to get audio.")


# Run the bot
app.run()

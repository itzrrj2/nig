import os
import aiohttp
import aiofiles
from uuid import uuid4
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API URLs
YOUTUBE_VIDEO_API = "https://jerrycoder.oggyapi.workers.dev/ytmp4?url="
YOUTUBE_AUDIO_API = "https://oggy-api.vercel.app/ytmp3?url="
INSTAGRAM_API = "https://oggy-api.vercel.app/insta?url="
SPOTIFY_API = "https://oggy-api.vercel.app/dspotify?url="
TIKTOK_API = "https://ar-api-iauy.onrender.com/tiktok?url="

# Initialize bot
app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Welcome to All-In-One Downloader Bot!\n\n"
        "📽 Send any YouTube / Instagram / TikTok link to download\n"
        "🎧 Use /audio <YouTube link> to get MP3\n"
        "🎶 Use /spotify <Spotify link> to get audio track"
    )

@app.on_message(filters.command("audio") & filters.private)
async def download_audio(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /audio <YouTube URL>")
    url = message.command[1]
    await message.reply("🎧 Fetching audio...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(YOUTUBE_AUDIO_API + quote(url, safe='')) as resp:
                data = await resp.json()
                title = data["title"]
                audio_url = data["download"]

            path = f"/tmp/{uuid4().hex}.mp3"
            async with session.get(audio_url) as r:
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in r.content.iter_chunked(1024 * 64):
                        await f.write(chunk)

        await message.reply_audio(audio=path, title=title, caption=f"🎵 {title}")
        os.remove(path)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("spotify") & filters.private)
async def download_spotify(client, message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /spotify <Spotify URL>")
    url = message.command[1]
    await message.reply("🎶 Fetching Spotify track...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SPOTIFY_API + quote(url, safe='')) as resp:
                data = await resp.json()
                track = data["data"]
                title = track["title"]
                artist = track.get("artis", "")
                audio_url = track["download"]

            path = f"/tmp/{uuid4().hex}.mp3"
            async with session.get(audio_url) as r:
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in r.content.iter_chunked(1024 * 64):
                        await f.write(chunk)

        await message.reply_audio(audio=path, title=title, performer=artist, caption=f"🎶 {title} - {artist}")
        os.remove(path)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.text & filters.private)
async def auto_download(client, message):
    url = message.text.strip()

    try:
        async with aiohttp.ClientSession() as session:

            # ✅ YouTube Video
            if "youtube.com" in url or "youtu.be" in url:
                await message.reply("🎬 Fetching YouTube video...")
                async with session.get(YOUTUBE_VIDEO_API + quote(url, safe='')) as resp:
                    data = await resp.json()
                    video_url = data["data"]["dl"]
                    title = data["data"]["title"]

                path = f"/tmp/{uuid4().hex}.mp4"
                async with session.get(video_url) as r:
                    async with aiofiles.open(path, "wb") as f:
                        async for chunk in r.content.iter_chunked(1024 * 64):
                            await f.write(chunk)
                await message.reply_video(video=path, caption=f"🎬 {title}")
                os.remove(path)
                return

            # ✅ Instagram Media
            if "instagram.com" in url:
                await message.reply("📸 Fetching Instagram media...")
                async with session.get(INSTAGRAM_API + quote(url, safe='')) as resp:
                    data = await resp.json()
                    for item in data["data"]:
                        media_url = item["url"]
                        ext = ".mp4" if item["type"] == "video" else ".jpg"
                        path = f"/tmp/{uuid4().hex}{ext}"

                        async with session.get(media_url) as r:
                            async with aiofiles.open(path, "wb") as f:
                                async for chunk in r.content.iter_chunked(1024 * 64):
                                    await f.write(chunk)

                        if ext == ".mp4":
                            await message.reply_video(video=path)
                        else:
                            await message.reply_photo(photo=path)
                        os.remove(path)
                return

            # ✅ TikTok Video (Only 720p)
            if "tiktok.com" in url:
                await message.reply("📱 Fetching TikTok video (720p only)...")
                async with session.get(TIKTOK_API + quote(url, safe='')) as resp:
                    data = await resp.json()
                    videos = data.get("video", [])
                    selected = next((v for v in videos if v["resolution"] == "720p"), None)

                    if not selected:
                        return await message.reply("❌ 720p resolution not available.")

                    video_url = selected["link"]
                    path = f"/tmp/{uuid4().hex}.mp4"

                    async with session.get(video_url) as r:
                        async with aiofiles.open(path, "wb") as f:
                            async for chunk in r.content.iter_chunked(1024 * 64):
                                await f.write(chunk)

                await message.reply_video(video=path, caption="🎥 TikTok Video (720p)")
                os.remove(path)
                return

        await message.reply("⚠️ Please send a valid YouTube, Instagram, or TikTok link, or use /audio /spotify.")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# Run bot
app.run()

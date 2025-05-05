import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://ar-api-iauy.onrender.com/aio-dl?url="

app = Client("aio_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_file(url, dest_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(dest_path, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return True
            else:
                return False

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "**👋 Welcome to the Media Downloader Bot!**\n"
        "Send any video or audio URL from YouTube, Instagram, Twitter, TikTok, etc.\n"
        "I'll download and send it back to you 🎁"
    )

@app.on_message(filters.text & ~filters.command("start"))
async def handle_url(client, message: Message):
    url = message.text.strip()
    info = await message.reply("🔍 Fetching download link...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + url) as resp:
                result = await resp.json()

        if result["status"] != 200 or result["successful"] != "success":
            return await info.edit(f"❌ Error: `{result['data']}`")

        data = result["data"]
        title = data.get("title", "Untitled")
        duration = data.get("duration", "N/A")
        formats = data.get("formats", [])
        audio = data.get("audio")

        # Select the first video format or audio if video not available
        media = formats[0] if formats else audio
        if not media:
            return await info.edit("⚠️ No downloadable media found.")

        download_url = media["url"]
        filename = download_url.split("/")[-1].split("?")[0]
        filepath = f"/tmp/{filename}"

        await info.edit("📥 Downloading media...")

        success = await download_file(download_url, filepath)
        if not success:
            return await info.edit("❌ Failed to download the file.")

        caption = f"🎬 **{title}**\n⏱️ Duration: {duration}"

        if formats:
            await message.reply_video(video=filepath, caption=caption)
        else:
            await message.reply_audio(audio=filepath, caption=caption)

        os.remove(filepath)
        await info.delete()

    except Exception as e:
        await info.edit(f"❌ Error: `{str(e)}`")

app.run()

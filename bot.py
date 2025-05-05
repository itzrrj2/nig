import os
import aiohttp
import tempfile
from pyrogram import Client, filters
from dotenv import load_dotenv

# Load API credentials from .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Pyrogram client
app = Client("media_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# API endpoint
API_ENDPOINT = "https://ar-api-iauy.onrender.com/aio-dl?url="

# Function to get mp4 URL from formats
def get_best_mp4_url(formats):
    for fmt in formats:
        if fmt.get("ext") == "mp4" and "url" in fmt:
            return fmt["url"]
    return None

# Download video and send to user
async def download_and_send_video(message, video_url, title):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                if resp.status == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(await resp.read())
                        tmp_path = tmp.name
                    await message.reply_video(video=tmp_path, caption=f"🎬 {title}")
                else:
                    await message.reply("❌ Failed to download video content.")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# Handler for any link
@app.on_message(filters.private & filters.text)
async def handle_url(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        return await message.reply("❌ Please send a valid URL.")

    await message.reply("⏳ Processing your request...")

    async with aiohttp.ClientSession() as session:
        async with session.get(API_ENDPOINT + url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("status") == 200 and data.get("successful") == "success":
                    title = data["data"].get("title", "Downloaded Media")
                    formats = data["data"].get("formats", [])
                    video_url = get_best_mp4_url(formats)
                    if video_url:
                        await download_and_send_video(message, video_url, title)
                    else:
                        await message.reply("❌ Could not find a valid video format to download.")
                else:
                    await message.reply(f"❌ Error: {data.get('data')}")
            else:
                await message.reply("❌ Failed to reach the API. Try again later.")

# Run the bot
app.run()
